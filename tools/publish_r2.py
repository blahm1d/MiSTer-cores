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
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import build_db  # noqa: E402

IMMUTABLE = 'public, max-age=31536000, immutable'
FRESH = 'no-cache'
TYPES = {'.zip': 'application/zip', '.json': 'application/json', '.ini': 'text/plain; charset=utf-8',
         '.mra': 'application/xml', '.rbf': 'application/octet-stream', '.nvm': 'application/octet-stream'}


def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()


def exists(url, size):
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


def put(wrangler, bucket, key, path, cache, dry):
    ctype = TYPES.get(path.suffix.lower(), 'application/octet-stream')
    print(f'  put {key}  ({path.stat().st_size:,} bytes)')
    if dry:
        return
    subprocess.run([wrangler, 'r2', 'object', 'put', f'{bucket}/{key}', '--file', str(path),
                    '--content-type', ctype, '--cache-control', cache, '--remote'],
                   cwd=ROOT, check=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--bucket', required=True)
    ap.add_argument('--base-url', required=True, help='public HTTPS URL the bucket is served at')
    ap.add_argument('--dry-run', action='store_true', help='build and list uploads without writing')
    args = ap.parse_args()
    base = args.base_url.rstrip('/')
    if not base.startswith('https://'):
        sys.exit('--base-url must be https://')
    if git('status', '--porcelain', '--', '_Arcade', 'catalog', 'sources'):
        sys.exit('Release files have uncommitted changes; commit first so the database pins a real commit.')
    wrangler = shutil.which('wrangler') or shutil.which('wrangler.cmd')
    if not wrangler and not args.dry_run:
        sys.exit('wrangler not found on PATH')

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

    print('Database:')
    for name in ('db.json.zip', 'db.json', 'downloader_blahm1d.ini', 'downloader_blahm1d.zip'):
        put(wrangler, args.bucket, name, out / name, FRESH, args.dry_run)
    (out / 'published.json').write_text(json.dumps(dict(revision=revision, base_url=base), indent=2) + '\n')
    print(('Dry run: nothing uploaded. ' if args.dry_run else 'Published. ') +
          f'Users add to downloader.ini:\n\n[blahm1d]\ndb_url = {base}/db.json.zip\n')


if __name__ == '__main__':
    main()
