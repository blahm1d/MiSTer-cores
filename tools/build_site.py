#!/usr/bin/env python3
"""Build the public website for the feed from the catalog, so it can never drift from what
Update_All installs: index.html (every core and game, install steps, FAQ, JSON-LD),
releases.html (RELEASES.md), robots.txt, sitemap.xml and llms.txt.

  python tools/build_site.py [--out dist/site] [--base-url https://mister.blahm1d.com]
"""
import argparse
import datetime
import html
import json
import re
from pathlib import Path, PurePosixPath
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
AUTHOR = 'blahm1d'
TAG = ' [blahm1d]'

# Board families shown on the page, in order; catalog ids map onto them.
GROUPS = [
    ('V Unit', 'Midway V Unit', ['vunit', 'wargods']),
    ('Wolf Unit', 'Midway Wolf Unit', ['wolfunit']),
    ('T Unit', 'Midway T Unit', ['tunit', 'tunitdcs']),
    ('Y Unit', 'Midway / Williams Y Unit', ['yunit', 'yunitadpcm']),
    ('X Unit', 'Midway X Unit', ['xunit']),
    ('NARC', 'Williams Z Unit', ['narc']),
    ('Exidy 440', 'Exidy 440', ['exidy440']),
    ('Night Slashers', 'Data East', ['nightslashers']),
    ('Gladiator', 'Taito', ['gladiator']),
    ('The Legend of Kage', 'Taito', ['legendofkage']),
]

FAQ = [
    ('How do I install the blahm1d MiSTer cores?',
     'Download downloader_blahm1d.ini from {base}/downloader_blahm1d.ini, put it in the root of your MiSTer SD card '
     '(/media/fat/), and run Update_All. The games appear in the Arcade menu, each name ending in [blahm1d]. Run '
     'Update_All again any time to get new releases.'),
    ('Are ROMs included?',
     'No. Keep Update_All\'s Arcade ROMs option enabled, or supply your own MAME ROM zips. Each game lists the ROM zip '
     'names it needs.'),
    ('Which hardware do the cores run on?',
     'MiSTer FPGA on a Terasic DE10-Nano (Intel Cyclone V). The games run in the FPGA as hardware, not software '
     'emulation.'),
    ('Why does every game name end in [blahm1d]?',
     'So these games never collide with another collection\'s version of the same game (for example jotego or the '
     'Coin-Op Collection). MiSTer names a game\'s save (.nvm) and DIP settings (.dip) after that name.'),
    ('How do I set up War Gods?',
     'War Gods boots from its original hard disk. Extract your own image with chdman extracthd -i <War Gods CHD> -o '
     'wargods.img and put it in games/wargods/ on the SD card; the feed installs config/wargods.s0, which mounts it.'),
    ('Is the source code available?',
     'Yes. Every core is released under the GPL; each core on this page links the source archive for its exact build.'),
]


def mra_facts(path):
    """year, manufacturer and a clean title from the MRA itself."""
    root = ET.fromstring((ROOT / path).read_bytes())
    title = PurePosixPath(path).stem
    title = title[:-len(TAG)] if title.endswith(TAG) else title
    return dict(title=title, year=(root.findtext('year') or '').strip(),
                maker=(root.findtext('manufacturer') or '').strip())


def md_to_html(md):
    """Small Markdown subset used by RELEASES.md: headings, paragraphs, `code`, [links](url)."""
    out = []
    for block in re.split(r'\n\s*\n', md.strip()):
        text = html.escape(block.strip())
        text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
        text = re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)', r'<a href="\2">\1</a>', text)
        m = re.match(r'(#{1,3}) (.*)', text)
        out.append(f'<h{len(m.group(1))}>{m.group(2)}</h{len(m.group(1))}>' if m else f'<p>{text}</p>')
    return '\n'.join(out)


CSS = """
:root{--bg:#0f1115;--fg:#e8e6e3;--mut:#9aa0a6;--card:#171a21;--line:#262b35;--acc:#f0b429;--ok:#3fb950}
@media (prefers-color-scheme:light){:root{--bg:#fafaf8;--fg:#1d1f23;--mut:#5f6368;--card:#fff;--line:#e3e3df;--acc:#b7791f;--ok:#1a7f37}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.55 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
main{max-width:980px;margin:0 auto;padding:32px 16px 64px}h1{font-size:2rem;margin:.2em 0}h2{margin-top:2.2em;border-bottom:1px solid var(--line);padding-bottom:.3em}
h3{margin:.2em 0}a{color:var(--acc)}code{background:var(--card);border:1px solid var(--line);border-radius:4px;padding:0 .3em;font-size:.92em}
.lede{color:var(--mut);font-size:1.1rem}.install{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px 20px}
.install ol{margin:.4em 0 0;padding-left:1.3em}.btn{display:inline-block;background:var(--acc);color:#111;font-weight:600;text-decoration:none;padding:.5em 1em;border-radius:8px;margin:.6em 0}
.core{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px 20px;margin:14px 0}
.meta{color:var(--mut);font-size:.92rem}.badge{display:inline-block;font-size:.78rem;border:1px solid var(--line);border-radius:999px;padding:.05em .6em;margin-left:.4em;color:var(--mut)}
.badge.ok{color:var(--ok);border-color:var(--ok)}table{border-collapse:collapse;width:100%;margin-top:.6em;font-size:.93rem}
th,td{text-align:left;padding:.35em .5em;border-top:1px solid var(--line);vertical-align:top}th{color:var(--mut);font-weight:600}
.wrap{overflow-x:auto}dt{font-weight:600;margin-top:1em}dd{margin:.2em 0 0}footer{margin-top:3em;color:var(--mut);font-size:.9rem}
"""


def build(base, out):
    cat = json.loads((ROOT / 'catalog/releases.json').read_text(encoding='utf-8'))
    cores = {c['id']: c for c in cat['cores']}
    srcs = {s['id']: s['archive'] for s in json.loads((ROOT / 'catalog/sources.json').read_text(encoding='utf-8'))['sources']}
    assert set(cores) == {i for _, _, ids in GROUPS for i in ids}, 'every catalog core needs a page group'
    today = datetime.date.today().isoformat()
    n_games = sum(len(c['games']) for c in cat['cores'])
    all_titles = []

    sections, apps = [], []
    for name, board, ids in GROUPS:
        cards = []
        for cid in ids:
            c = cores[cid]
            rows = []
            for g in c['games']:
                f = mra_facts(g['path'])
                all_titles.append(f['title'])
                alt = ' <span class="badge">alternative</span>' if '/_alternatives/' in g['path'] else ''
                rows.append(f'<tr><td>{html.escape(f["title"])}{alt}</td><td>{html.escape(f["year"])}</td>'
                            f'<td>{html.escape(f["maker"])}</td><td><code>{html.escape(", ".join(g["rom_archives"]))}</code></td></tr>')
            verified = '<span class="badge ok">cabinet verified</span>' if c.get('cabinet_verified') else ''
            d = c['date']
            cards.append(
                f'<div class="core" id="{cid}"><h3>{html.escape(c["family"])} {verified}</h3>'
                f'<div class="meta">Build {html.escape(c["version"])} &middot; {d[:4]}-{d[4:6]}-{d[6:]} &middot; '
                f'{html.escape(c["status"])} &middot; <a href="{base}/{srcs[cid]}">source (GPL)</a></div>'
                f'<p>{html.escape(c["notes"])}</p>'
                f'<div class="wrap"><table><tr><th>Game</th><th>Year</th><th>Manufacturer</th><th>ROM zip</th></tr>'
                f'{"".join(rows)}</table></div></div>')
            apps.append({
                '@type': 'SoftwareApplication', 'name': f'{c["family"]} MiSTer FPGA core',
                'applicationCategory': 'GameApplication', 'operatingSystem': 'MiSTer FPGA (DE10-Nano)',
                'softwareVersion': c['version'], 'datePublished': f'{d[:4]}-{d[4:6]}-{d[6:]}',
                'author': {'@type': 'Person', 'name': AUTHOR}, 'license': 'https://www.gnu.org/licenses/gpl-3.0.html',
                'isAccessibleForFree': True, 'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'USD'},
                'downloadUrl': f'{base}/downloader_blahm1d.ini', 'url': f'{base}/#{cid}',
                'description': c['notes'],
                'about': [{'@type': 'VideoGame', 'name': mra_facts(g['path'])['title']} for g in c['games']]})
        sections.append(f'<h2 id="{name.lower().replace(" ", "-")}">{html.escape(name)} '
                        f'<span class="meta">&middot; {html.escape(board)}</span></h2>' + ''.join(cards))

    faq = [(q, a.format(base=base)) for q, a in FAQ]
    ld = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'WebSite', 'name': 'blahm1d MiSTer cores', 'url': f'{base}/'},
        {'@type': 'Person', 'name': AUTHOR, 'url': f'{base}/'},
        {'@type': 'ItemList', 'name': 'blahm1d MiSTer FPGA arcade cores', 'numberOfItems': len(apps),
         'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'item': a} for i, a in enumerate(apps)]},
        {'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q,
                                             'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faq]}]}

    desc = (f'blahm1d MiSTer FPGA arcade cores: {len(cat["cores"])} cores and {n_games} games, including the Midway '
            f'V Unit (Cruis\'n USA, Cruis\'n World, Off Road Challenge, War Gods), Wolf Unit, T Unit, Y Unit, X Unit, '
            f'NARC, Exidy 440, Night Slashers, Gladiator and The Legend of Kage. Install with one Update_All INI.')
    index = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>blahm1d MiSTer FPGA Arcade Cores</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{base}/">
<meta property="og:title" content="blahm1d MiSTer FPGA Arcade Cores"><meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{base}/"><meta property="og:type" content="website">
<style>{CSS}</style>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script></head><body><main>
<h1>blahm1d MiSTer FPGA arcade cores</h1>
<p class="lede">{html.escape(desc)}</p>
<div class="install"><strong>Install</strong>
<ol><li>Download <a href="{base}/downloader_blahm1d.ini">downloader_blahm1d.ini</a> (right-click, Save link as).</li>
<li>Put it in the root of your MiSTer SD card (<code>/media/fat/</code>).</li>
<li>Run <strong>Update_All</strong>. The games appear in the <strong>Arcade</strong> menu, each ending in <code>[blahm1d]</code>.</li></ol>
<a class="btn" href="{base}/downloader_blahm1d.ini">Download the INI</a>
<div class="meta">Or add these two lines to your <code>downloader.ini</code>: <code>[blahm1d]</code> <code>db_url = {base}/db.json.zip</code></div></div>
<p>These cores rebuild the original arcade boards in the FPGA: CPUs, graphics, sound boards and I/O. Some builds are
beta; each core shows its build, test status and known issues. Full notes: <a href="{base}/releases.html">release notes</a>.
No ROMs are included.</p>
{''.join(sections)}
<h2 id="faq">FAQ</h2><dl>{''.join(f'<dt>{html.escape(q)}</dt><dd>{html.escape(a)}</dd>' for q, a in faq)}</dl>
<footer>blahm1d &middot; cores released under the GPL &middot; source code linked from each core
&middot; updated {today}</footer></main></body></html>
"""
    releases = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>blahm1d MiSTer Cores Release Notes</title>
<meta name="description" content="Release status, fixes and known issues for every blahm1d MiSTer FPGA arcade core.">
<link rel="canonical" href="{base}/releases.html"><style>{CSS}</style></head><body><main>
<p><a href="{base}/">&larr; blahm1d MiSTer cores</a></p>
{md_to_html((ROOT / 'RELEASES.md').read_text(encoding='utf-8'))}
</main></body></html>
"""
    robots = (f'User-agent: *\nAllow: /\n\n# Content use: search results and AI-generated answers may use this site.\n'
              f'Content-Signal: search=yes, ai-input=yes\n\nSitemap: {base}/sitemap.xml\n')
    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
               + ''.join(f'<url><loc>{base}/{p}</loc><lastmod>{today}</lastmod></url>\n'
                         for p in ('', 'releases.html')) + '</urlset>\n')
    llms = [f'# blahm1d MiSTer FPGA arcade cores', '', f'> {desc}', '',
            f'- Install: put {base}/downloader_blahm1d.ini in the MiSTer SD root and run Update_All.',
            f'- Games show in the Arcade menu with names ending in [blahm1d]. No ROMs included.',
            f'- Release notes: {base}/releases.html', f'- Source code (GPL): linked per core on {base}/', '', '## Cores', '']
    for name, board, ids in GROUPS:
        for cid in ids:
            c = cores[cid]
            titles = ', '.join(mra_facts(g['path'])['title'] for g in c['games'])
            llms.append(f'- {c["family"]} ({board}), build {c["version"]}: {titles}')

    out.mkdir(parents=True, exist_ok=True)
    for fname, text in (('index.html', index), ('releases.html', releases), ('robots.txt', robots),
                        ('sitemap.xml', sitemap), ('llms.txt', '\n'.join(llms) + '\n')):
        (out / fname).write_text(text, encoding='utf-8', newline='\n')
    print(f'Site: {len(cat["cores"])} cores, {n_games} games -> {out}')
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--out', type=Path, default=ROOT / 'dist' / 'site')
    ap.add_argument('--base-url', default='https://mister.blahm1d.com')
    a = ap.parse_args()
    build(a.base_url.rstrip('/'), a.out)
