#!/usr/bin/env python3
"""Upload the large extra downloads and media listed in catalog/extras.json to the R2 mirror.

These files are too big for git (GitHub rejects files over 100 MB), so they live only on the
mirror. Each local file is checked against the catalogued size and SHA-256 before upload; files
already on the mirror at the catalogued size are skipped.

  python tools/publish_extras.py --bucket blahm1d-mister --base-url https://mister.blahm1d.com --dir <folder> [--dry-run]
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from publish_r2 import IMMUTABLE, exists, put, wrangler_cmd  # noqa: E402


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--bucket', required=True)
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--dir', required=True, type=Path, action='append',
                    help='folder holding files named in extras.json (repeatable)')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    base = args.base_url.rstrip('/')
    files = [f for e in json.loads((ROOT / 'catalog/extras.json').read_text(encoding='utf-8'))['extras']
             for f in e['files'] + e.get('media', [])]
    wrangler = wrangler_cmd()
    if not wrangler and not args.dry_run:
        sys.exit('wrangler not found')
    for f in files:
        name = PurePosixPath(f['key']).name
        found = [d / name for d in args.dir if (d / name).is_file()]
        assert found, f'{name} not found in any --dir'
        path = found[0]
        assert path.stat().st_size == f['bytes'], f'{path}: size differs from catalog'
        assert sha256(path) == f['sha256'], f'{path}: SHA-256 differs from catalog'
        if exists(f'{base}/{f["key"]}', f['bytes']):
            print(f'  skip {f["key"]} (already on the mirror)')
            continue
        put(wrangler, args.bucket, f['key'], path, IMMUTABLE, args.dry_run)
    for f in files:
        if not args.dry_run:
            assert exists(f'{base}/{f["key"]}', f['bytes']), f'{f["key"]} not served after upload'
    print('done' + (' (dry run)' if args.dry_run else ''))


if __name__ == '__main__':
    main()
