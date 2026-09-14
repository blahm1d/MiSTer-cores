#!/usr/bin/env python3
"""Build the blahm1d MiSTer database from the explicit release catalog."""
import argparse
import hashlib
import json
import re
import time
import zipfile
from pathlib import Path, PurePosixPath
from urllib.parse import quote
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
REPO = 'blahm1d/MiSTer-cores'
DB_ID = 'blahm1d'

def digest(data, kind='sha256'):
    return hashlib.new(kind, data).hexdigest()

def validate():
    catalog=json.loads((ROOT/'catalog/releases.json').read_text(encoding='utf-8'))
    assert catalog['roms_included'] is False
    expected={}
    bindings=set()
    paths=set()
    for c in catalog['cores']:
        assert c['binding'].startswith('blahm1d_') and c['binding'] not in bindings
        bindings.add(c['binding'])
        assert re.fullmatch(r'\d{8}',c['date'])
        assert c['binary']==f"_Arcade/cores/{c['binding']}_{c['date']}.rbf"
        expected[c['binary']]=(c['sha256'],['arcade','blahm1d',c['id'],'rbf'],[c['binding']],True)
        assert c['games'], c['id']+' has no MRAs'
        for g in c['games']:
            p=g['path']
            assert p.startswith('_Arcade/_blahm1d/') and p.endswith('.mra')
            assert p.casefold() not in paths,p
            paths.add(p.casefold())
            mra=ET.fromstring((ROOT/p).read_bytes())
            assert mra.findtext('rbf')==c['binding'],p
            assert mra.findtext('setname')==g['setname'] and g['setname'],p
            assert mra.findtext('name') and mra.findall('rom'),p
            expected[p]=(g['sha256'],['arcade','blahm1d',c['id'],'mra'],[c['binding']],True)
    actual={p.relative_to(ROOT).as_posix() for p in (ROOT/'_Arcade').rglob('*') if p.is_file()}
    assert actual==set(expected),f'Unlisted/missing arcade files: {actual ^ set(expected)}'
    if (ROOT/'catalog/defaults.json').exists():
        for e in json.loads((ROOT/'catalog/defaults.json').read_text())['files']:
            assert e['path'].startswith('config/nvram/') and e['path'].endswith('.nvm')
            expected[e['path']]=(e['sha256'],['arcade','blahm1d',e['core'],'nvram'],[],False)
    for p,(h,_,_,_) in expected.items():
        assert not PurePosixPath(p).is_absolute() and '..' not in PurePosixPath(p).parts
        data=(ROOT/p).read_bytes()
        assert digest(data)==h,p+' content changed; update the catalog deliberately'
        assert len(data)>0
    sources=json.loads((ROOT/'catalog/sources.json').read_text())['sources']
    assert {s['id'] for s in sources}=={c['id'] for c in catalog['cores']},'Every binary requires its source archive'
    for s in sources:
        assert digest((ROOT/s['archive']).read_bytes())==s['sha256'],s['archive']
        with zipfile.ZipFile(ROOT/s['archive']) as z:
            assert z.testzip() is None,s['archive']
            assert 'SOURCE-MANIFEST.json' in z.namelist()
    return expected,catalog

def make_zip(path, contents):
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in contents.items():
            info=zipfile.ZipInfo(name,(2026,9,14,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,data)

def build(revision,out,timestamp):
    assert re.fullmatch(r'[0-9a-f]{40}',revision),'Artifact URLs must pin a full Git commit'
    expected,catalog=validate()
    files,folders={},{}
    for p,(h,tags,tangle,overwrite) in sorted(expected.items()):
        data=(ROOT/p).read_bytes()
        d=dict(hash=digest(data,'md5'),size=len(data),url=f'https://raw.githubusercontent.com/{REPO}/{revision}/{quote(p,safe="/")}',tags=tags)
        if tangle:d['tangle']=tangle
        if not overwrite:d['overwrite']=False
        files[p]=d
        for parent in PurePosixPath(p).parents:
            if str(parent)=='.':continue
            folders.setdefault(str(parent),{'tags':['arcade','blahm1d']})
    db=dict(v=1,db_id=DB_ID,timestamp=timestamp,files=files,folders=dict(sorted(folders.items())))
    raw=(json.dumps(db,indent=2,ensure_ascii=False)+'\n').encode()
    out.mkdir(parents=True,exist_ok=True)
    (out/'db.json').write_bytes(raw)
    make_zip(out/'db.json.zip',{'db.json':raw})
    ini=(ROOT/'downloader_blahm1d.ini').read_bytes()
    (out/'downloader_blahm1d.ini').write_bytes(ini)
    make_zip(out/'downloader_blahm1d.zip',{'downloader_blahm1d.ini':ini})
    print(f"Validated {len(catalog['cores'])} RBFs, {sum(len(c['games']) for c in catalog['cores'])} MRAs; database has {len(files)} files.")

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--revision')
    p.add_argument('--out',type=Path,default=ROOT/'dist')
    p.add_argument('--timestamp',type=int,default=int(time.time()))
    p.add_argument('--validate-only',action='store_true')
    args=p.parse_args()
    if args.validate_only:
        expected,catalog=validate();print(f'PASS: {len(expected)} downloadable files; complete source archives; all hashes and MRA bindings match.')
    else:
        p.error('--revision is required') if not args.revision else build(args.revision,args.out,args.timestamp)
