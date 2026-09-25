#!/usr/bin/env python3
"""End-to-end check of a published mirror, as MiSTer Downloader sees it: fetch the INI,
follow db_url, then download every file in the database and verify size + MD5.

  python tools/verify_mirror.py https://mister.blahm1d.com/downloader_blahm1d.ini
"""
import hashlib
import io
import json
import re
import sys
import urllib.request
import zipfile
from pathlib import Path


def get(url):
    # MiSTer Downloader's own user agent: the check sees exactly what players' MiSTers get.
    req = urllib.request.Request(url, headers={'User-Agent': 'Downloader/2.X (Linux; theypsilon@gmail.com)'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def main():
    ini = get(sys.argv[1]).decode()
    db_url = re.search(r'^db_url\s*=\s*(\S+)', ini, re.M).group(1)
    raw = get(db_url)
    db = json.loads(zipfile.ZipFile(io.BytesIO(raw)).read('db.json') if db_url.endswith('.zip') else raw)
    print(f'INI -> {db_url}: db_id={db["db_id"]}, {len(db["files"])} files')
    bad = 0
    for path, f in sorted(db['files'].items()):
        try:
            data = get(f['url'])
            ok = len(data) == f['size'] and hashlib.md5(data).hexdigest() == f['hash']
        except Exception as e:  # report every failure, keep going
            ok, data = False, str(e).encode()
        if not ok:
            bad += 1
            print('  FAIL', path, f['url'])
    base = db_url.rsplit('/', 1)[0]
    catalog = Path(__file__).resolve().parents[1] / 'catalog/sources.json'
    for s in json.loads(catalog.read_text(encoding='utf-8'))['sources']:
        try:
            ok = hashlib.sha256(get(f'{base}/{s["archive"]}')).hexdigest() == s['sha256']
        except Exception:
            ok = False
        if not ok:
            bad += 1
            print('  FAIL source', s['archive'])
    print('PASS: every file and source archive downloads and matches' if not bad else f'{bad} FAILED')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
