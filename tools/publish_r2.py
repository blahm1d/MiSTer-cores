#!/usr/bin/env python3
"""Publish the blahm1d database to a Cloudflare R2 bucket served over HTTPS.

Independent of GitHub: payloads (RBFs, MRAs, NVRAM defaults) upload under
content-addressed keys (files/<sha256>/<name>), source archives under sources/,
and the database + INI last, so a live database never names a missing payload.
Objects already on the mirror are skipped (checked with an HTTP HEAD).

Requires `wrangler login` (or CLOUDFLARE_API_TOKEN) on this machine.

  python tools/publish_r2.py --bucket blahm1d-mister --base-url https://<public host> --dry-run
  python tools/publish_r2.py --bucket blahm1d-mister --base-url https://<public host>
"""
import argparse
import json
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import build_db  # noqa: E402
import build_site  # noqa: E402

IMMUTABLE = 'public, max-age=31536000, immutable'
FRESH = 'no-cache'
TYPES = {'.zip': 'application/zip', '.gif': 'image/gif', '.png': 'image/png', '.json': 'application/json', '.ini': 'text/plain; charset=utf-8', '.md': 'text/plain; charset=utf-8', '.html': 'text/html; charset=utf-8', '.txt': 'text/plain; charset=utf-8', '.xml': 'application/xml',
         '.mra': 'application/xml', '.rbf': 'application/octet-stream', '.nvm': 'application/octet-stream'}


def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()


def exists(url, size):
    # Query string keeps this probe off the real URL's cache entry: a HEAD before upload would
    # otherwise leave a cached 404 at the edge for the very URL users are about to download.
    url = f'{url}?probe={time.time_ns()}'
    req = urllib.request.Request(url, method='HEAD', headers={'User-Agent': 'blahm1d-publish'})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status == 200 and int(r.headers.get('Content-Length', -1)) == size
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False
        raise
    except urllib.error.URLError:
        return False  # host not serving yet (first publish): upload everything


def wrangler_cmd():
    """Run wrangler's JS entry with node directly: on Windows the npm .cmd shim goes through
    cmd.exe, which mangles or crashes on some argument characters."""
    exe = shutil.which('wrangler')
    if exe and sys.platform == 'win32':
        js = Path(exe).parent / 'node_modules' / 'wrangler' / 'bin' / 'wrangler.js'
        node = shutil.which('node')
        if js.is_file() and node:
            return [node, str(js)]
    return [exe] if exe else None


def put(wrangler, bucket, key, path, cache, dry):
    ctype = TYPES.get(path.suffix.lower(), 'application/octet-stream')
    print(f'  put {key}  ({path.stat().st_size:,} bytes)')
    if dry:
        return
    subprocess.run([*wrangler, 'r2', 'object', 'put', f'{bucket}/{key}', '--file', str(path),
                    '--content-type', ctype, '--cache-control', cache, '--remote'],
                   cwd=ROOT, check=True)


def publish_site(wrangler, args, base):
    site = build_site.build(base, ROOT / 'dist' / 'site')
    entry_points = {'index.html', 'sitemap.xml', 'llms.txt'}
    pages = build_site.generated_files(site) + sorted((ROOT / 'site-static').glob('*'))
    for page in sorted(pages, key=lambda p: (p.name in entry_points, p.name)):
        put(wrangler, args.bucket, page.name, page, FRESH, args.dry_run)
    if not args.dry_run:
        subprocess.run([sys.executable, str(ROOT / 'tools' / 'verify_site.py'), base],
                       cwd=ROOT, check=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--bucket', required=True)
    ap.add_argument('--base-url', required=True, help='public HTTPS URL the bucket is served at')
    ap.add_argument('--dry-run', action='store_true', help='build and list uploads without writing')
    ap.add_argument('--payloads-only', action='store_true',
                    help='upload payloads and source archives but not the database (payload keys do not depend on the URL)')
    ap.add_argument('--site-only', action='store_true',
                    help='generate, publish and verify website pages without republishing the core database')
    args = ap.parse_args()
    if args.site_only and args.payloads_only:
        ap.error('--site-only and --payloads-only are mutually exclusive')
    base = args.base_url.rstrip('/')
    if not base.startswith('https://'):
        sys.exit('--base-url must be https://')
    if git('status', '--porcelain', '--', '_Arcade', 'catalog', 'sources'):
        sys.exit('Release files have uncommitted changes; commit first so the database pins a real commit.')
    if not args.dry_run and git('status', '--porcelain', '--', 'tools/build_site.py', 'tools/publish_r2.py', 'tools/verify_site.py', 'site-static'):
        sys.exit('Website sources have uncommitted changes; commit the approved update first.')
    wrangler = wrangler_cmd()
    if not wrangler and not args.dry_run:
        sys.exit('wrangler not found on PATH')
    if args.site_only:
        build_db.validate()
        publish_site(wrangler, args, base)
        print('Dry run: nothing uploaded.' if args.dry_run else 'Website published and verified.')
        return

    revision = git('rev-parse', 'HEAD')
    timestamp = int(git('show', '-s', '--format=%ct', revision))
    out = ROOT / 'dist' / 'r2'
    objects = build_db.build(revision, out, timestamp, base)

    print('Payloads:')
    todo = [(k, ROOT / p) for k, p in sorted(objects.items())]
    todo += [(f'sources/{p.name}', p) for p in sorted((ROOT / 'sources').glob('*.zip'))]
    skipped = 0
    for key, path in todo:
        if exists(f'{base}/{key}', path.stat().st_size):
            skipped += 1
            continue
        put(wrangler, args.bucket, key, path, IMMUTABLE, args.dry_run)
    print(f'  {skipped} already on the mirror')
    if args.payloads_only:
        print('Payloads only: database not uploaded.')
        return

    print('Database:')
    for name in ('db.json.zip', 'db.json', 'downloader_blahm1d.ini', 'downloader_blahm1d.zip'):
        put(wrangler, args.bucket, name, out / name, FRESH, args.dry_run)
    # Human-readable release notes, linked from the README and the release post.
    put(wrangler, args.bucket, 'RELEASES.md', ROOT / 'RELEASES.md', FRESH, args.dry_run)
    # Public website (index, release notes, robots, sitemap, llms.txt), rebuilt from the catalog every publish.
    publish_site(wrangler, args, base)
    (out / 'published.json').write_text(json.dumps(dict(revision=revision, base_url=base), indent=2) + '\n')
    print(('Dry run: nothing uploaded. ' if args.dry_run else 'Published. ') +
          f'Users add to downloader.ini:\n\n[blahm1d]\ndb_url = {base}/db.json.zip\n')


if __name__ == '__main__':
    main()
