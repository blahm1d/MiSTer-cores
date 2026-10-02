#!/usr/bin/env python3
"""Stage a new build of an existing core into this feed.

Takes the SD-card style `_Arcade` folder a core build produces and:
  * copies the RBF to `_Arcade/cores/<binding>_<date>.rbf` and removes the old one,
  * copies each matching MRA (matched by <setname>) and points its <rbf> at the binding,
  * rebuilds the core's source archive from the build's project folder, adding
    only new files the build itself references (Quartus project, QIPs, sv2v list),
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

# Generated build output; never part of a source archive.
GENERATED_DIRS = {'output_files', 'db', 'incremental_db', 'greybox_tmp', 'build_syn'}
# Plain-text lists of synthesis sources, one project-relative path per line.
SOURCE_LISTS = ('tools/quartus_sv2v_files.txt',)
QUARTUS_FILE_REF = re.compile(
    r'-name\s+\w*FILE\s+(?:\[file\s+join\s+\$::quartus\(qip_path\)\s+"?([^\]"]+?)"?\s*\]|"([^"]+)"|(\S+))')
MEM_INIT_REF = re.compile(r'\$readmem[hb]\s*\(\s*"([^"]+)"')
# Build scripts that name synthesis sources as "$ROOT/<project path>" (e.g. Wolf's quartus/build_sv2v.sh).
SCRIPT_ROOT_REF = re.compile(r'\$\{?ROOT\}?/([\w./-]+\.(?:sv|v|vhd|vh|svh|qip|sdc|hex|mif))')
HDL_EXTS = {'.sv', '.v', '.vhd', '.vh', '.svh'}
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


def build_references(source_dir, seed):
    """Files the build actually uses: the synthesis source lists, everything the
    Quartus project and QIP files name (recursively), and memory-init files the
    HDL loads with $readmemh/$readmemb. Test benches and unrelated cores in the
    same folder are left out because nothing in the build refers to them."""
    root = source_dir.resolve()

    def rel(path):
        try:
            r = path.resolve().relative_to(root)
        except ValueError:
            return None
        if not path.is_file() or GENERATED_DIRS.intersection(r.parts[:-1]):
            return None
        return r.as_posix()

    queue = [p for p in seed if p.endswith(('.qsf', '.qip'))
             or (p.endswith('.sh') and not p.startswith(('sim/', 'tb/', 'test/')))] + list(SOURCE_LISTS)
    queue += [p.relative_to(root).as_posix() for p in root.glob('*.qsf')]
    found, seen = set(), set()
    while queue:
        name = queue.pop()
        if name in seen:
            continue
        seen.add(name)
        path = root / name
        if not path.is_file():
            continue
        found.add(name)
        text = path.read_text(encoding='utf-8', errors='replace')
        refs = []
        if name in SOURCE_LISTS:
            refs = [(root / line.strip()) for line in text.splitlines()
                    if line.strip() and not line.strip().startswith('#')]
        elif name.endswith(('.qsf', '.qip')):
            base = path.parent  # Quartus resolves QSF/QIP paths from the file's own directory
            for line in text.splitlines():
                if line.lstrip().startswith('#'):
                    continue
                m = QUARTUS_FILE_REF.search(line)
                if m:
                    qip_rel, quoted, bare = m.groups()
                    refs.append(path.parent / qip_rel.strip() if qip_rel else base / (quoted or bare))
        elif name.endswith('.sh'):
            refs = [root / m.group(1) for m in SCRIPT_ROOT_REF.finditer(text)
                    if not m.group(1).startswith(('sim/', 'tb/', 'test/'))]
        elif path.suffix.lower() in HDL_EXTS:
            for m in MEM_INIT_REF.finditer(text):
                refs += [path.parent / m.group(1), root / m.group(1)]
        for ref in refs:
            r = rel(ref)
            if r and r not in seen:
                queue.append(r)
    return found


def build_source_archive(core_id, version, rbf_hash, source_dir, old_archive, drop=()):
    with zipfile.ZipFile(old_archive) as z:
        old_manifest = json.loads(z.read('SOURCE-MANIFEST.json'))
        old_readme = z.read('SOURCE-README.txt').decode('utf-8') if 'SOURCE-README.txt' in z.namelist() else ''
    unknown = sorted(set(drop) - set(old_manifest['files_sha256']))
    if unknown:
        fail(f'--drop names files that are not in the previous archive: {unknown}')
    listed = sorted(set(old_manifest['files_sha256']) - set(drop))
    missing = [p for p in listed if not (source_dir / p).is_file()]
    if missing:
        fail(f'{len(missing)} source files from the previous archive are missing in {source_dir}, '
             f'for example {missing[:5]}. Check --source-dir.')
    added = sorted(build_references(source_dir, listed) - set(listed))
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
    ap.add_argument('--drop', action='append', default=[], metavar='PATH',
                    help='deliberately leave this previous-archive file out of the new archive (repeatable)')
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
    src_files, added_src = build_source_archive(a.id, a.version, rbf_hash, source_dir, old_archive, a.drop)

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
    if a.drop:
        print(f'            dropped on request: {sorted(a.drop)}')
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
    print('  Review the diff and stage only the exact intended release paths.')
    print('  Ask the owner for publication approval before committing or pushing.')
    print(f'  git commit -m "{core["family"]}: {a.version} ({date})"')
    print('  git push origin main')


if __name__ == '__main__':
    main()
