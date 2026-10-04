#!/usr/bin/env python3
"""Build the public website for the feed from the catalog, so it can never drift from what
Update_All installs: index.html (every core and game, install steps, FAQ, JSON-LD),
game and core pages, releases.html, robots.txt, sitemap.xml and llms.txt.

  python tools/build_site.py [--out dist/site] [--base-url https://mister.blahm1d.com]
"""
import argparse
import datetime
import html
import json
import re
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
AUTHOR = 'blahm1d'
COFFEE = 'https://buymeacoffee.com/blahm1d'
TAG = ' [blahm1d]'

# Board families shown on the page, in order; catalog ids map onto them.
GROUPS = [
    ('Mortal Kombat 4', 'Midway Zeus 1', ['mk4']),
    ('Invasion: The Abductors', 'Midway Zeus 1', ['invasion']),
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
     '(/media/fat/), and run Update_All. The games appear under Arcade > Blahm1d, each name ending in [blahm1d]. Run '
     'Update_All again any time to get new releases.'),
    ('Are ROMs included?',
     'No. Enable ROM downloads in Update_All, or BYOR (bring your own ROMs). This feed supplies FPGA cores and MRA game '
     'definitions. ROM compatibility has been tested with a MAME 0.289 merged set. Each game lists its compatible '
     'ROM ZIP names. War Gods also requires your own disk image.'),
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


def game_page_name(game):
    title = mra_facts(game['path'])['title']
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
    assert slug, game['path']
    return slug + '.html'


def core_page_name(core):
    return f'core-{core["id"]}.html'


def person(base):
    return {'@type': 'Person', '@id': f'{base}/about.html#blahm1d',
            'name': AUTHOR, 'url': f'{base}/about.html'}


def application(base, core, source, games, url):
    d = core['date']
    return {'@type': 'SoftwareApplication', '@id': url + '#core',
            'name': f'{core["family"]} MiSTer FPGA core', 'url': url,
            'applicationCategory': 'GameApplication', 'operatingSystem': 'MiSTer FPGA (DE10-Nano)',
            'softwareVersion': core['version'], 'datePublished': f'{d[:4]}-{d[4:6]}-{d[6:]}',
            'author': {'@id': person(base)['@id']}, 'publisher': {'@id': person(base)['@id']},
            'isAccessibleForFree': True, 'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'USD'},
            'license': 'https://www.gnu.org/licenses/gpl-3.0.html',
            'downloadUrl': f'{base}/downloader_blahm1d.ini', 'description': core['notes'],
            'subjectOf': {'@type': 'SoftwareSourceCode', 'url': f'{base}/{source}'},
            'about': [{'@type': 'VideoGame', 'name': mra_facts(g['path'])['title']} for g in games]}


def detail_document(base, name, title, description, body, graph):
    url = f'{base}/{name}'
    ld = {'@context': 'https://schema.org', '@graph': [person(base),
          {'@type': 'WebPage', '@id': url, 'url': url, 'name': title,
           'description': description, 'publisher': {'@id': person(base)['@id']}}, *graph]}
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><meta name="description" content="{html.escape(description)}">
<link rel="canonical" href="{url}"><meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(description)}"><meta property="og:url" content="{url}">
<meta property="og:type" content="website"><style>{CSS}</style>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False).replace('</', '<\\/')}</script>
</head><body><main><nav><a href="index.html">All blahm1d MiSTer cores</a> &middot;
<a href="about.html">About blahm1d</a> &middot; <a href="releases.html">Release notes</a></nav>
{body}<footer>FPGA core development and publication: <a href="about.html">blahm1d</a>.
Original arcade games and third-party source retain their original credits and licenses.</footer>
</main></body></html>'''


def install_html(base, title=None):
    launch = (f'<li>Open <strong>{html.escape(title)} [blahm1d]</strong> under Arcade &gt; Blahm1d '
              '(regional and revision alternatives are inside the alternatives folder).</li>') if title else ''
    return f'''<div class="install"><h2>Install with Update_All</h2><ol>
<li>Download <a href="{base}/downloader_blahm1d.ini">downloader_blahm1d.ini</a>.</li>
<li>Put it in your MiSTer SD card root (<code>/media/fat/</code>).</li>
<li>Run <strong>Update_All</strong> to install or update the FPGA core and MRA.</li>{launch}</ol>
<p>ROMs are supplied by users through their Update_All settings or BYOR. No game ROMs are included in this feed.</p>
<p>Keep your existing save and DIP filenames. Downloader preserves existing save defaults.</p></div>'''


def extras_html(base, extras, core_id):
    """Extra downloads hosted on the mirror (catalog/extras.json), e.g. a PC build of MAME."""
    out = ''
    for ex in (e for e in extras if e['core'] == core_id):
        buttons = ''.join(f'<a class="btn" href="{base}/{f["key"]}">{html.escape(f["label"])} '
                          f'({f["bytes"] / 1048576:.0f} MB)</a>' for f in ex['files'] if f.get('button'))
        buttons += f'<a class="btn coffee" href="{COFFEE}" rel="noopener">&#9749; Buy me a coffee</a>'
        items = ''
        for f in ex['files']:
            link = '' if f.get('button') else f'<a href="{base}/{f["key"]}">{html.escape(f["label"])}</a> '
            items += (f'<li>{link}<code>{PurePosixPath(f["key"]).name}</code> ({f["bytes"] / 1048576:.0f} MB)<br>'
                      f'SHA-256 <code>{f["sha256"]}</code></li>')
        out += (f'<h2>{html.escape(ex["title"])}</h2><p>{html.escape(ex["description"])}</p>'
                f'<div class="install"><h2>Install</h2><p>{html.escape(ex["install"])}</p>{buttons}</div>'
                f'<h3>Files</h3><ul>{items}</ul>')
        if ex.get('media'):
            imgs = ''.join(f'<figure><img src="{base}/{m["key"]}" alt="{html.escape(m["alt"])}" loading="lazy" '
                           f'style="max-width:100%;height:auto"><figcaption>{html.escape(m["alt"])}</figcaption></figure>'
                           for m in ex['media'])
            out += f'<h3>{html.escape(ex["media_title"])}</h3><p>{html.escape(ex["media_note"])}</p>{imgs}'
    return out


def build_detail_pages(base, cores, srcs, extras=()):
    pages = {}
    for core in cores.values():
        cp = core_page_name(core)
        games = core['games']
        game_links = ''.join(f'<li><a href="{game_page_name(g)}">{html.escape(mra_facts(g["path"])["title"])}</a></li>' for g in games)
        d = core['date']; date = f'{d[:4]}-{d[4:6]}-{d[6:]}'
        release = (f'<h2>Current build and known issues</h2><p><strong>{html.escape(core["version"])}</strong> '
                   f'&middot; {date}</p><p>{html.escape(core["status"])}</p><p>{html.escape(core["notes"])}</p>'
                   '<p>These statements describe the published core build. They do not establish that every supported game has passed every cabinet test.</p>')
        credits = (f'<h2>Source and credits</h2><p>FPGA core development and publication: <a href="about.html">blahm1d</a>. '
                   f'<a href="{base}/{srcs[core["id"]]}">Download the corresponding source archive and license notices</a>. '
                   'Original authors, donor projects and third-party copyright notices are preserved in the source.</p>')
        title = f'{core["family"]} MiSTer FPGA Core | {core["version"]} | blahm1d'
        desc = f'blahm1d develops and publishes this {core["family"]} MiSTer FPGA core for DE10-Nano. Supported games, installation, source and release status.'
        extra = extras_html(base, extras, core['id'])
        body = f'<h1>{html.escape(core["family"])} MiSTer FPGA core</h1><p class="lede">{html.escape(desc)}</p><h2>Supported games</h2><ul>{game_links}</ul>' + release + install_html(base) + extra + credits
        pages[cp] = detail_document(base, cp, title, desc, body, [application(base, core, srcs[core['id']], games, f'{base}/{cp}')])
        for g in games:
            gp = game_page_name(g); assert gp not in pages, f'Duplicate game page: {gp}'
            f = mra_facts(g['path']); name = f['title']
            desc = f'{name} is supported by the {core["family"]} MiSTer FPGA core developed and published by blahm1d. Installation, source and current build status.'
            peers = ''.join(f'<li><a href="{game_page_name(other)}">{html.escape(mra_facts(other["path"])["title"])}</a></li>' for other in games if other is not g)
            about = (f'<h2>About this arcade release</h2><dl><dt>Game</dt><dd>{html.escape(name)}</dd>'
                     f'<dt>Original arcade manufacturer</dt><dd>{html.escape(f["maker"])}</dd>'
                     f'<dt>Original arcade year</dt><dd>{html.escape(f["year"])}</dd>'
                     f'<dt>MiSTer core</dt><dd><a href="{cp}">{html.escape(core["family"])}</a></dd>'
                     f'<dt>Compatible ROM ZIP names</dt><dd><code>{html.escape(", ".join(g["rom_archives"]))}</code></dd></dl>')
            faq = [(f'Is {name} available on MiSTer FPGA?', f'Yes. This game is supported by the {core["family"]} core published by blahm1d. See the current build status and known issues on this page.'),
                   ('Who develops and publishes this MiSTer core?', 'blahm1d develops and publishes this FPGA core. Original arcade creators and third-party source contributors retain their credits.'),
                   ('Where do I download it?', f'Download downloader_blahm1d.ini from {base}/downloader_blahm1d.ini, put it in the MiSTer SD root and run Update_All. Launch the game under Arcade > Blahm1d.'),
                   ('What hardware does it use?', 'MiSTer FPGA on a Terasic DE10-Nano. This is an arcade FPGA core; its current release limitations are listed above.')]
            faqs = '<h2>Questions</h2><dl>' + ''.join(f'<dt>{html.escape(q)}</dt><dd>{html.escape(a)}</dd>' for q,a in faq) + '</dl>'
            body = f'<h1>{html.escape(name)} on MiSTer FPGA</h1><p class="lede">{html.escape(desc)}</p>' + about + release + install_html(base, name) + extra + credits + faqs
            if peers: body += '<h2>Other games and revisions on this core</h2><ul>' + peers + '</ul>'
            pages[gp] = detail_document(base, gp, f'{name} MiSTer FPGA Core | blahm1d', desc, body,
                [application(base, core, srcs[core['id']], [g], f'{base}/{gp}'),
                 {'@type': 'FAQPage', 'mainEntity': [{'@type':'Question','name':q,'acceptedAnswer':{'@type':'Answer','text':a}} for q,a in faq]}])
    pages['about.html'] = detail_document(base, 'about.html', 'blahm1d | MiSTer FPGA arcade core developer',
        'blahm1d develops and publishes MiSTer FPGA arcade cores. Find supported games, current releases, source archives and installation instructions.',
        '<h1>blahm1d MiSTer FPGA arcade cores</h1><p>blahm1d develops and publishes the MiSTer FPGA arcade cores in this collection. '
        'The release site documents supported games, current builds, installation instructions, corresponding source and known issues.</p>'
        '<p>The original arcade games belong to their original creators. Third-party framework, CPU, sound and other source contributors retain their copyright and license notices in each source archive.</p>'
        '<p><a href="index.html">Browse all supported games and cores</a></p>', [])
    return pages


def generated_files(out):
    """Publish exactly this sitemap's pages, excluding obsolete previews or files."""
    sitemap = ET.fromstring((out / 'sitemap.xml').read_bytes())
    names = {'robots.txt', 'sitemap.xml', 'llms.txt'}
    for loc in sitemap.findall('{*}url/{*}loc'):
        path = urlsplit(loc.text).path
        name = path.lstrip('/') or 'index.html'
        assert '/' not in name and name.endswith('.html'), name
        names.add(name)
    files = [out / name for name in sorted(names)]
    assert all(p.is_file() for p in files), 'generated site page missing'
    return files


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
.install ol{margin:.4em 0 0;padding-left:1.3em}.btn{display:inline-block;background:var(--acc);color:#111;font-weight:600;text-decoration:none;padding:.5em 1em;border-radius:8px;margin:.6em .4em .6em 0}
.btn.coffee{background:transparent;color:var(--fg);border:1px solid var(--acc)}
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
    groups = list(GROUPS)
    listed = {i for _, _, ids in groups for i in ids}
    assert listed <= set(cores), 'page groups reference a missing core'
    groups.extend((c['family'], 'MiSTer FPGA', [cid]) for cid, c in cores.items() if cid not in listed)
    today = datetime.date.today().isoformat()
    n_games = sum(len(c['games']) for c in cat['cores'])
    all_titles = []
    extras_path = ROOT / 'catalog/extras.json'
    extras = json.loads(extras_path.read_text(encoding='utf-8'))['extras'] if extras_path.is_file() else []
    assert {e['core'] for e in extras} <= set(cores), 'extras reference a missing core'
    detail_pages = build_detail_pages(base, cores, srcs, extras)
    assert len(detail_pages) == n_games + len(cores) + 1, 'every game and core needs a distinct page'

    sections, apps = [], []
    for name, board, ids in groups:
        cards = []
        for cid in ids:
            c = cores[cid]
            rows = []
            for g in c['games']:
                f = mra_facts(g['path'])
                all_titles.append(f['title'])
                alt = ' <span class="badge">alternative</span>' if '/_alternatives/' in g['path'] else ''
                rows.append(f'<tr><td><a href="{game_page_name(g)}">{html.escape(f["title"])}</a>{alt}</td><td>{html.escape(f["year"])}</td>'
                            f'<td>{html.escape(f["maker"])}</td><td><code>{html.escape(", ".join(g["rom_archives"]))}</code></td></tr>')
            verified = '<span class="badge ok">cabinet verified</span>' if c.get('cabinet_verified') else ''
            d = c['date']
            cards.append(
                f'<div class="core" id="{cid}"><h3><a href="{core_page_name(c)}">{html.escape(c["family"])}</a> {verified}</h3>'
                f'<div class="meta">Build {html.escape(c["version"])} &middot; {d[:4]}-{d[4:6]}-{d[6:]} &middot; '
                f'{html.escape(c["status"])} &middot; <a href="{base}/{srcs[cid]}">source (GPL)</a></div>'
                f'<p>{html.escape(c["notes"])}</p>'
                f'<div class="wrap"><table><tr><th>Game</th><th>Year</th><th>Manufacturer</th><th>ROM zip</th></tr>'
                f'{"".join(rows)}</table></div></div>')
            apps.append(application(base, c, srcs[cid], c['games'], f'{base}/{core_page_name(c)}'))
        sections.append(f'<h2 id="{name.lower().replace(" ", "-")}">{html.escape(name)} '
                        f'<span class="meta">&middot; {html.escape(board)}</span></h2>' + ''.join(cards))

    faq = [(q, a.format(base=base)) for q, a in FAQ]
    ld = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'WebSite', 'name': 'blahm1d MiSTer cores', 'url': f'{base}/'},
        person(base),
        {'@type': 'ItemList', 'name': 'blahm1d MiSTer FPGA arcade cores', 'numberOfItems': len(apps),
         'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'item': a} for i, a in enumerate(apps)]},
        {'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q,
                                             'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faq]}]}

    desc = (f'blahm1d MiSTer FPGA arcade cores: {len(cat["cores"])} cores and {n_games} games, including the Midway '
            f'Zeus 1 (Mortal Kombat 4), V Unit (Cruis\'n USA, Cruis\'n World, Off Road Challenge, War Gods), Wolf Unit, T Unit, Y Unit, X Unit, '
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
<p>FPGA core development and publication: <a href="about.html">blahm1d</a>.
Each game below links to its installation instructions, source, build status and known issues.
Original arcade creators and third-party source contributors retain their credits.</p>
<div class="install"><strong>Install</strong>
<ol><li>Download <a href="{base}/downloader_blahm1d.ini">downloader_blahm1d.ini</a> (right-click, Save link as).</li>
<li>Put it in the root of your MiSTer SD card (<code>/media/fat/</code>).</li>
<li>Run <strong>Update_All</strong>. The games appear under <strong>Arcade &gt; Blahm1d</strong>, each ending in <code>[blahm1d]</code>.</li></ol>
<a class="btn" href="{base}/downloader_blahm1d.ini">Download the INI</a>
<a href="{base}/downloader_blahm1d.zip">INI ZIP (extract first)</a>
<a class="btn coffee" href="{COFFEE}" rel="noopener">&#9749; Buy me a coffee</a>
<div class="meta">Or add these two lines to your <code>downloader.ini</code>:</div>
<pre><code>[blahm1d]
db_url = {base}/db.json.zip</code></pre></div>
<p>These cores rebuild the original arcade boards in the FPGA: CPUs, graphics, sound boards and I/O. Some builds are
beta; each core shows its build, test status and known issues. Full notes: <a href="{base}/releases.html">release notes</a>.
<strong>No ROMs are included.</strong> Enable ROM downloads in <strong>Update_All</strong>,
or <strong>BYOR</strong> (bring your own ROMs).
ROM compatibility has been tested with a MAME 0.289 merged set.
War Gods also requires your own disk image.</p>
{''.join(sections)}
<h2 id="faq">FAQ</h2><dl>{''.join(f'<dt>{html.escape(q)}</dt><dd>{html.escape(a)}</dd>' for q, a in faq)}</dl>
<footer>blahm1d &middot; cores released under the GPL &middot; source code linked from each core
&middot; <a href="{COFFEE}" rel="noopener">&#9749; buy me a coffee</a>
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
                         for p in ('', 'releases.html', *sorted(detail_pages))) + '</urlset>\n')
    llms = [f'# blahm1d MiSTer FPGA arcade cores', '', f'> {desc}', '',
            f'- Install: put {base}/downloader_blahm1d.ini in the MiSTer SD root and run Update_All.',
            f'- Games show under Arcade > Blahm1d with names ending in [blahm1d]. Moving the entries does not rename saves or DIP settings.',
            '- No ROMs are included. Enable ROM downloads in Update_All, or BYOR (bring your own ROMs). '
            'ROM compatibility has been tested with a MAME 0.289 merged set. War Gods also requires your own disk image.',
            f'- Release notes: {base}/releases.html', f'- Source code (GPL): linked per core on {base}/', '', '## Cores', '']
    llms.extend(['- FPGA core developer and publisher: blahm1d. Original arcade and third-party source credits remain with their authors.',
                 f'- Developer profile: {base}/about.html'])
    for name, board, ids in groups:
        for cid in ids:
            c = cores[cid]
            titles = ', '.join(mra_facts(g['path'])['title'] for g in c['games'])
            llms.append(f'- [{c["family"]}]({base}/{core_page_name(c)}) ({board}), build {c["version"]}: {titles}')
            for g in c['games']:
                llms.append(f'  - [{mra_facts(g["path"])["title"]}]({base}/{game_page_name(g)}): FPGA core by blahm1d.')

    out.mkdir(parents=True, exist_ok=True)
    for fname, text in (('index.html', index), ('releases.html', releases), ('robots.txt', robots),
                        ('sitemap.xml', sitemap), ('llms.txt', '\n'.join(llms) + '\n')):
        (out / fname).write_text(text, encoding='utf-8', newline='\n')
    for fname, text in detail_pages.items():
        (out / fname).write_text(text, encoding='utf-8', newline='\n')
    print(f'Site: {len(cat["cores"])} core pages, {n_games} game pages, developer profile -> {out}')
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--out', type=Path, default=ROOT / 'dist' / 'site')
    ap.add_argument('--base-url', default='https://mister.blahm1d.com')
    a = ap.parse_args()
    build(a.base_url.rstrip('/'), a.out)
