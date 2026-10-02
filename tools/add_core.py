#!/usr/bin/env python3
"""Add a NEW core to the feed (stage_release.py updates existing ones).

Copies the RBF to _Arcade/cores/<binding>_<date>.rbf, installs each MRA under
_Arcade/_Blahm1d/ (alternate versions: --alternative-of) with <rbf> pointed at the binding, archives the source
snapshot the RBF was built from (generated Quartus output excluded, GPL COPYING added
if absent), adds catalog/releases.json and catalog/sources.json entries, and runs
the publish validation.

  python tools/add_core.py --id cruisinusa --family "Cruis'n" \
    --rbf build/gm1.rbf --mra "gm1_CruisinUSA.mra=Cruis'n USA (rev L4.4)" \
    --source-dir build/source --date 20260924 --version r26 --status Beta --notes "..."
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import build_db  # noqa: E402
import stage_release as sr  # noqa: E402

GENERATED = {'output_files', 'db', 'incremental_db', 'greybox_tmp', '__pycache__', '.git'}
README = """{title}
RBF SHA-256: {rbf}

This archive contains the selected integration source and build support files.
Use Quartus 17.0 Lite for the DE10-Nano / Cyclone V target. See the project
QSF/QIP files and build scripts for the source list and conversion steps.
Third-party files retain their individual copyright and license notices.
No game ROMs, personal settings, fitted databases or game traces are included.
ROMs are loaded by MiSTer at runtime; ROM-driven simulations need local game data.

Source identity: {snapshot}
The compiled binary's validation status is recorded in the feed catalog.
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--id', required=True)
    ap.add_argument('--family', required=True)
    ap.add_argument('--alternative-of', metavar='GAME', help='install these MRAs under _Blahm1d/_alternatives/_GAME/ (regional/revision variants of a main game)')
    ap.add_argument('--rbf', type=Path, required=True)
    ap.add_argument('--mra', action='append', required=True, metavar='FILE=TITLE',
                    help='package MRA and the file title it is published under (repeatable)')
    ap.add_argument('--source-dir', type=Path, required=True)
    ap.add_argument('--snapshot-name', help='source identity recorded in the archive (default: folder name)')
    ap.add_argument('--date', required=True)
    ap.add_argument('--version', required=True)
    ap.add_argument('--status', required=True)
    ap.add_argument('--notes', required=True)
    ap.add_argument('--cabinet-verified', action='store_true')
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()

    catalog = sr.load_json(ROOT / 'catalog/releases.json')
    sources = sr.load_json(ROOT / 'catalog/sources.json')
    if any(c['id'] == a.id for c in catalog['cores']):
        sr.fail(f'{a.id} already exists; use stage_release.py')
    if not re.fullmatch(r'\d{8}', a.date):
        sr.fail('--date must be YYYYMMDD')
    binding = f'blahm1d_{a.id}'
    rbf = a.rbf.read_bytes()
    binary = f'_Arcade/cores/{binding}_{a.date}.rbf'

    games, mra_writes = [], []
    for spec in a.mra:
        src, _, title = spec.partition('=')
        if not title.endswith(' [blahm1d]'):
            title += ' [blahm1d]'  # feed MRA tag; also names the game's .nvm/.dip files
        src = Path(src)
        original = src.read_bytes()
        data = sr.retarget_mra(original, binding, src)
        text = data.decode('utf-8')
        setname = re.search(r'<setname>([^<]+)', text).group(1).strip()
        mame = (re.search(r'<mameversion>([^<]+)', text) or [None, ''])[1].strip()
        zips = sorted({z for m in re.finditer(r'zip="([^"]+)"', text) for z in m.group(1).split('|')})
        path = f'_Arcade/_Blahm1d/_alternatives/_{a.alternative_of}/{title}.mra' if a.alternative_of else f'_Arcade/_Blahm1d/{title}.mra'
        games.append(dict(name=title, setname=setname, mameversion=mame, path=path, sha256=sr.sha256(data),
                          original_sha256=sr.sha256(original), rom_archives=zips))
        mra_writes.append((path, data))

    src_root = a.source_dir.resolve()
    files = {}
    for p in sorted(src_root.rglob('*')):
        rel = p.relative_to(src_root)
        if p.is_file() and not GENERATED.intersection(rel.parts[:-1]):
            files[rel.as_posix()] = p.read_bytes()
    if 'COPYING' not in files:
        files['COPYING'] = (ROOT / 'COPYING').read_bytes()
    snapshot = a.snapshot_name or src_root.name
    rbf_hash = sr.sha256(rbf)
    manifest = dict(core=a.id, version=a.version, rbf_sha256=rbf_hash, source_commit=None, snapshot=snapshot,
                    files_sha256={k: sr.sha256(v) for k, v in sorted(files.items())})
    files['SOURCE-MANIFEST.json'] = (json.dumps(manifest, indent=1) + '\n').encode()
    files['SOURCE-README.txt'] = README.format(title=f'{a.family} - {a.version}', rbf=rbf_hash,
                                               snapshot=snapshot).encode()
    archive = f'sources/{a.id}-{a.date}.zip'

    print(f'Core    {a.id} ({binding}) -> {binary}  sha256 {rbf_hash}')
    for g in games:
        print(f'MRA     {g["path"]}  setname {g["setname"]}  zips {g["rom_archives"]}')
    print(f'Source  {src_root} -> {archive}  ({len(files)} files)')
    if a.dry_run:
        print('Dry run: nothing written.')
        return

    (ROOT / binary).write_bytes(rbf)
    for path, data in mra_writes:
        (ROOT / path).parent.mkdir(parents=True, exist_ok=True)
        (ROOT / path).write_bytes(data)
    sr.write_zip(ROOT / archive, files)
    zdata = (ROOT / archive).read_bytes()
    catalog['cores'].append(dict(id=a.id, family=a.family, version=a.version, date=a.date, sha256=rbf_hash,
                                 status=a.status, notes=a.notes, binary=binary, binding=binding, games=games,
                                 cabinet_verified=a.cabinet_verified))
    sources['sources'].append(dict(id=a.id, archive=archive, sha256=sr.sha256(zdata), file_count=len(files),
                                   bytes=len(zdata)))
    sr.save_json(ROOT / 'catalog/releases.json', catalog)
    sr.save_json(ROOT / 'catalog/sources.json', sources)
    build_db.validate()
    print('PASS: catalog, hashes, MRA bindings and source archive all validate.')


if __name__ == '__main__':
    main()
