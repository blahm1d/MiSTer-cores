#!/usr/bin/env python3
"""Stage a new build of an existing core into this feed.

Takes the SD-card style `_Arcade` folder a core build produces and:
  * copies the RBF to `_Arcade/cores/<binding>_<date>.rbf` and removes the old one,
  * copies each matching MRA (matched by <setname>) and points its <rbf> at the binding,
  * rebuilds the core's source archive from the build's project folder,
  * updates catalog/releases.json and catalog/sources.json with the new hashes,
  * runs the same validation the publish workflow runs.

Example (Windows):
  python tools\\stage_release.py --id tunitdcs ^
    --sd-dir "D:\\...\\releases\\TUnitDCS_20260923-SD\\_Arcade" ^
    --version "DCS sound fix" --status "Beta" --notes "..."
"""
import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import build_db  # noqa: E402

SKIP_DIRS = {'output_files', 'db', 'incremental_db', 'greybox_tmp', 'work', 'simulation',
             'build', 'build_syn', 'releases', '__pycache__', '.git'}
NEW_FILE_DIRS = ('rtl/', 'sys/')
NEW_FILE_EXTS = {'.sv', '.v', '.vhd', '.vh', '.svh', '.qip', '.sdc', '.tcl', '.hex', '.mif'}
ZIP_TIME = (2026, 9, 14, 0, 0, 0)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def load_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def save_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def fail(msg):
    sys.exit(f'ERROR: {msg}')


def find_rbf(sd_dir, date):
    rbfs = sorted(p for p in sd_dir.rglob('*') if p.is_file() and p.suffix.lower() == '.rbf')
    if date:
        dated = [p for p in rbfs if date in p.name]
        rbfs = dated or rbfs
    if len(rbfs) != 1:
        fail(f'expected exactly one .rbf under {sd_dir}, found {[str(p) for p in rbfs] or "none"}. '
             'Use --rbf to pick one.')
    return rbfs[0]


def mras_by_setname(sd_dir):
    found = {}
    for p in sorted(sd_dir.rglob('*')):
        if p.is_file() and p.suffix.lower() == '.mra':
            try:
                setname = ET.fromstring(p.read_bytes()).findtext('setname')
            except ET.ParseError as e:
                fail(f'{p} is not valid XML: {e}')
            if setname:
                found.setdefault(setname, []).append(p)
    return found


def retarget_mra(data, binding, path):
    new, count = re.subn(rb'(<rbf>)[^<]*(</rbf>)', rb'\g<1>' + binding.encode() + rb'\g<2>', data)
    if count != 1:
        fail(f'{path} must contain exactly one <rbf> tag, found {count}')
    return new


def default_source_dir(sd_dir):
    for parent in sd_dir.parents:
        if parent.name.lower() == 'releases':
            return parent.parent
    return None


def build_source_archive(core_id, version, rbf_hash, source_dir, old_archive):
    with zipfile.ZipFile(old_archive) as z:
        old_manifest = json.loads(z.read('SOURCE-MANIFEST.json'))
        old_readme = z.read('SOURCE-README.txt').decode('utf-8') if 'SOURCE-README.txt' in z.namelist() else ''
    listed = sorted(old_manifest['files_sha256'])
    missing = [p for p in listed if not (source_dir / p).is_file()]
    if missing:
        fail(f'{len(missing)} source files from the previous archive are missing in {source_dir}, '
             f'for example {missing[:5]}. Check --source-dir.')
    added = []
    for p in sorted(source_dir.rglob('*')):
        rel = p.relative_to(source_dir).as_posix()
        if (p.is_file() and rel.startswith(NEW_FILE_DIRS) and p.suffix.lower() in NEW_FILE_EXTS
                and rel not in old_manifest['files_sha256']
                and not SKIP_DIRS.intersection(p.relative_to(source_dir).parts[:-1])):
            added.append(rel)
    files = {rel: (source_dir / rel).read_bytes() for rel in listed + added}
    manifest = dict(old_manifest, core=core_id, version=version, rbf_sha256=rbf_hash,
                    source_commit=None, snapshot=source_dir.name,
                    files_sha256={rel: sha256(data) for rel, data in sorted(files.items())})
    readme = old_readme
    if readme:
        lines = readme.splitlines()
        if lines:
            lines[0] = re.sub(r' - .*$', f' - {version}', lines[0])
        readme = '\n'.join(lines) + '\n'
        readme = re.sub(r'RBF SHA-256: [0-9a-f]{64}', f'RBF SHA-256: {rbf_hash}', readme)
        readme = re.sub(r'Source identity: .*', f'Source identity: {source_dir.name}', readme)
    files['SOURCE-MANIFEST.json'] = (json.dumps(manifest, indent=1) + '\n').encode()
    if readme:
        files['SOURCE-README.txt'] = readme.encode()
    return files, added


def write_zip(path, files):
    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name in sorted(files):
            info = zipfile.ZipInfo(name, ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, files[name])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--id', required=True, help='core id in catalog/releases.json, e.g. tunitdcs')
    ap.add_argument('--sd-dir', type=Path, required=True, help='the build\'s SD-card _Arcade folder')
    ap.add_argument('--source-dir', type=Path, help='project folder the RBF was built from '
                    '(default: the folder that contains "releases")')
    ap.add_argument('--rbf', type=Path, help='RBF to use if the SD folder holds more than one')
    ap.add_argument('--date', help='YYYYMMDD for the new filename (default: read from the SD folder or RBF name)')
    ap.add_argument('--version', required=True, help='short build name shown in the catalog')
    ap.add_argument('--status', help='catalog status text (default: keep the current one)')
    ap.add_argument('--notes', help='catalog notes text (default: keep the current one)')
    ap.add_argument('--cabinet-verified', action='store_true', help='mark this build as tested on a real cabinet')
    ap.add_argument('--dry-run', action='store_true', help='show what would change without writing anything')
    a = ap.parse_args()

    sd_dir = a.sd_dir.resolve()
    if not sd_dir.is_dir():
        fail(f'{sd_dir} is not a folder')

    releases_path = ROOT / 'catalog/releases.json'
    sources_path = ROOT / 'catalog/sources.json'
    catalog = load_json(releases_path)
    sources = load_json(sources_path)
    core = next((c for c in catalog['cores'] if c['id'] == a.id), None)
    if core is None:
        fail(f'no core "{a.id}" in catalog; known ids: {[c["id"] for c in catalog["cores"]]}')
    src_entry = next((s for s in sources['sources'] if s['id'] == a.id), None)
    if src_entry is None:
        fail(f'no source archive entry for "{a.id}" in catalog/sources.json')

    rbf_src = a.rbf.resolve() if a.rbf else find_rbf(sd_dir, a.date)
    date = a.date
    if not date:
        # Nearest name wins: the RBF itself, then the SD folder and its parents.
        for name in [rbf_src.name, sd_dir.name] + [p.name for p in sd_dir.parents]:
            m = re.search(r'(20\d{6})', name)
            if m:
                date = m.group(1)
                break
    if not date or not re.fullmatch(r'\d{8}', date):
        fail('could not work out the release date; pass --date YYYYMMDD')

    source_dir = (a.source_dir or default_source_dir(sd_dir))
    if source_dir is None or not source_dir.is_dir():
        fail('could not find the project folder; pass --source-dir')
    source_dir = source_dir.resolve()

    binding = core['binding']
    rbf_data = rbf_src.read_bytes()
    rbf_hash = sha256(rbf_data)
    new_binary = f'_Arcade/cores/{binding}_{date}.rbf'
    old_binary = core['binary']

    supplied = mras_by_setname(sd_dir)
    mra_updates = []
    for g in core['games']:
        candidates = supplied.get(g['setname'], [])
        if len(candidates) > 1:
            fail(f'more than one MRA for {g["setname"]}: {[str(p) for p in candidates]}')
        if candidates:
            original = candidates[0].read_bytes()
            mra_updates.append((g, candidates[0], original, retarget_mra(original, binding, candidates[0])))
    unused = sorted(set(supplied) - {g['setname'] for g in core['games']})

    old_archive = ROOT / src_entry['archive']
    new_archive_rel = f'sources/{a.id}-{date}.zip'
    src_files, added_src = build_source_archive(a.id, a.version, rbf_hash, source_dir, old_archive)

    print(f'Core        {a.id} ({binding})')
    print(f'RBF         {rbf_src}')
    print(f'            -> {new_binary}  sha256 {rbf_hash}')
    if old_binary != new_binary:
        print(f'            removes {old_binary}')
    for g, src, _, new in mra_updates:
        print(f'MRA         {src.name} -> {g["path"]}  sha256 {sha256(new)}')
    kept = [g['name'] for g in core['games'] if g not in [u[0] for u in mra_updates]]
    if kept:
        print(f'MRA kept    no new MRA supplied for: {kept}')
    if unused:
        print(f'MRA ignored setnames not in this core\'s catalog entry: {unused}')
    print(f'Source      {source_dir}')
    print(f'            -> {new_archive_rel}  ({len(src_files)} files)')
    if added_src:
        print(f'            new files since the last archive: {added_src}')
    if a.dry_run:
        print('Dry run: nothing written.')
        return

    (ROOT / new_binary).write_bytes(rbf_data)
    if old_binary != new_binary and (ROOT / old_binary).exists():
        (ROOT / old_binary).unlink()
    for g, _, original, new in mra_updates:
        (ROOT / g['path']).write_bytes(new)
        g['sha256'] = sha256(new)
        g['original_sha256'] = sha256(original)
    write_zip(ROOT / new_archive_rel, src_files)
    if new_archive_rel != src_entry['archive'] and old_archive.exists():
        old_archive.unlink()
    archive_bytes = (ROOT / new_archive_rel).read_bytes()

    core.update(version=a.version, date=date, sha256=rbf_hash, binary=new_binary,
                cabinet_verified=bool(a.cabinet_verified))
    if a.status:
        core['status'] = a.status
    if a.notes:
        core['notes'] = a.notes
    src_entry.update(archive=new_archive_rel, sha256=sha256(archive_bytes),
                     file_count=len(src_files), bytes=len(archive_bytes))
    save_json(releases_path, catalog)
    save_json(sources_path, sources)

    build_db.validate()
    print('PASS: catalog, hashes, MRA bindings and source archive all validate.')
    print('\nNext:')
    print('  git add -A _Arcade sources catalog')
    print(f'  git commit -m "{core["family"]}: {a.version} ({date})"')
    print('  git push origin main')


if __name__ == '__main__':
    main()
