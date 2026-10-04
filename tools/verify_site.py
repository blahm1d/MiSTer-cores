#!/usr/bin/env python3
"""Verify generated game/core coverage, attribution, links and indexable HTML.

  python tools/verify_site.py https://mister.blahm1d.com
  python tools/verify_site.py --local-dir dist/search-preview
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urlsplit, unquote
import urllib.request
import xml.etree.ElementTree as ET

import build_site

ROOT = Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.canonicals, self.links, self.json_ld, self.visible = [], [], [], []
        self.in_script = False
        self.script_type = None
        self.script = ''
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'link' and a.get('rel') == 'canonical': self.canonicals.append(a['href'])
        if tag == 'a' and a.get('href'): self.links.append(a['href'])
        if tag == 'meta' and a.get('name', '').lower() in ('robots', 'googlebot'):
            assert not re.search(r'noindex|nosnippet', a.get('content', ''), re.I)
        if tag == 'script':
            self.in_script, self.script_type, self.script = True, a.get('type'), ''

    def handle_endtag(self, tag):
        if tag == 'script':
            if self.script_type == 'application/ld+json': self.json_ld.append(json.loads(self.script))
            self.in_script = False

    def handle_data(self, data):
        if self.in_script: self.script += data
        else: self.visible.append(data)


def verify(base, local_dir=None):
    catalog = json.loads((ROOT / 'catalog/releases.json').read_text(encoding='utf-8'))
    sources = json.loads((ROOT / 'catalog/sources.json').read_text())['sources']
    source_paths = {s['archive'] for s in sources}
    extras_path = ROOT / 'catalog/extras.json'
    extra_files = [f for e in json.loads(extras_path.read_text(encoding='utf-8'))['extras']
                   for f in e['files'] + e.get('media', [])] if extras_path.is_file() else []
    source_paths |= {f['key'] for f in extra_files}
    if not local_dir:
        for f in extra_files:  # extra downloads live only on the mirror: check they are there at the catalogued size
            req = urllib.request.Request(f'{base}/{f["key"]}?probe=1', method='HEAD',
                                         headers={'User-Agent': 'Mozilla/5.0 (blahm1d website verification)'})
            with urllib.request.urlopen(req, timeout=30) as r:
                assert r.status == 200 and int(r.headers['Content-Length']) == f['bytes'], f['key']
    cores = catalog['cores']
    names = {'index.html', 'releases.html', 'about.html'}
    names.update(build_site.core_page_name(c) for c in cores)
    names.update(build_site.game_page_name(g) for c in cores for g in c['games'])
    assert len(names) == 3 + len(cores) + sum(len(c['games']) for c in cores)

    def get(name):
        if local_dir: return (local_dir / name).read_text(encoding='utf-8')
        req = urllib.request.Request(f'{base}/{name}', headers={'User-Agent': 'Mozilla/5.0 (blahm1d website verification)'})
        with urllib.request.urlopen(req, timeout=30) as r:
            assert r.status == 200
            assert not re.search(r'noindex|nosnippet', r.headers.get('X-Robots-Tag', ''), re.I)
            return r.read().decode('utf-8')

    with ThreadPoolExecutor(max_workers=4) as pool:
        texts = dict(zip(sorted(names), pool.map(get, sorted(names))))
    pages = {n: Page(t) for n, t in texts.items()}
    for n, page in pages.items():
        assert page.canonicals == [base + ('/' if n == 'index.html' else '/' + n)], n
        for link in page.links:
            u = urlsplit(link)
            if u.scheme and u.netloc != urlsplit(base).netloc: continue
            path = unquote(u.path).lstrip('/')
            assert path in names | source_paths | {'', 'downloader_blahm1d.ini', 'downloader_blahm1d.zip'}, (n, link)
        if n != 'releases.html':
            assert len(page.json_ld) == 1, n
            graph = page.json_ld[0]['@graph']
            people = [x for x in graph if x['@type'] == 'Person']
            assert len(people) == 1 and people[0]['name'] == 'blahm1d', n
    for core in cores:
        for g in core['games']:
            n = build_site.game_page_name(g); p = pages[n]
            visible = ' '.join(p.visible)
            assert build_site.mra_facts(g['path'])['title'] in visible, n
            assert 'developed and published by blahm1d' in visible, n
            assert core['version'] in visible and core['status'] in visible, n
            apps = [x for x in p.json_ld[0]['@graph'] if x['@type'] == 'SoftwareApplication']
            assert len(apps) == 1 and apps[0]['softwareVersion'] == core['version'], n
            assert apps[0]['author']['@id'] == build_site.person(base)['@id'], n
            assert apps[0]['publisher']['@id'] == build_site.person(base)['@id'], n
            assert n in pages['index.html'].links and n in pages[build_site.core_page_name(core)].links, n
    sitemap = ET.fromstring(get('sitemap.xml'))
    urls = {loc.text for loc in sitemap.findall('{*}url/{*}loc')}
    expected_urls = {base + ('/' if n == 'index.html' else '/' + n) for n in names}
    assert urls == expected_urls, 'sitemap does not cover exactly the current pages'
    robots = get('robots.txt'); assert 'Allow: /' in robots and f'Sitemap: {base}/sitemap.xml' in robots
    llms = get('llms.txt')
    assert all(f'{base}/{build_site.game_page_name(g)}' in llms for c in cores for g in c['games'])
    print(f'PASS: {len(cores)} core pages, {sum(len(c["games"]) for c in cores)} game pages; attribution, release status, JSON-LD, internal links and sitemap verified.')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('base', nargs='?', default='https://mister.blahm1d.com')
    ap.add_argument('--local-dir', type=Path)
    args = ap.parse_args()
    verify(args.base.rstrip('/'), args.local_dir)
