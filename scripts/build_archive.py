#!/usr/bin/env python3
"""Render dated Markdown reports into a portable, dependency-free HTML archive."""
import html
import json
import os
import re
import zipfile
import sys
from collections import defaultdict
from datetime import date
from hashlib import sha256
from pathlib import Path
from urllib.parse import quote
sys.path.insert(0, str(Path(__file__).resolve().parent / "vendor"))
import markdown as md_renderer
from latex2mathml.converter import convert as render_math

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT
# A fresh icon URL prevents browsers from reusing an older monogram.
FAVICON_VERSION = sha256((ROOT / 'assets/favicon.svg').read_bytes()).hexdigest()[:12]
public_paths = {Path('assets') / name for name in ('site.css', 'site.js', 'favicon.svg')}
entries = []
for source in sorted((ROOT / 'content').glob('*.md'), reverse=True):
    raw = source.read_text()
    _, front, body = re.split(r'^---[ \t]*$', raw, maxsplit=2, flags=re.M)
    e = json.loads(front)
    date.fromisoformat(e['date'])
    assert source.stem == e['date'], 'Use one report file per ISO date'
    e['body'], e['raw'] = body.strip(), raw
    e['path'] = e['date'].replace('-', '/') + '/index.html'
    entries.append(e)
assert entries, 'At least one report is required'
latest = entries[0]
all_topics = ['Neutrinos', 'Cosmic rays', 'Gamma rays', 'Multimessenger', 'Oscillations', 'Dark matter', 'BSM']
esc = lambda x: html.escape(str(x), quote=True)
def longdate(s): return date.fromisoformat(s).strftime('%d %B %Y').lstrip('0')
def shortdate(s): return date.fromisoformat(s).strftime('%d %b %Y').lstrip('0')
def count_label(n, noun): return f'{n} {noun}' + ('' if n == 1 else 's')
def report_count_label(e):
    if not e['papers'] and e.get('news_count'):
        return count_label(e['news_count'], 'news section')
    return count_label(len(e['papers']), 'paper')
def rel(current, target): return os.path.relpath(target, str(Path(current).parent)).replace(os.sep, '/')
def slug(s): return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')
def icon(name):
    paths = {'search':'<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/>', 'moon':'<path d="M20 14A8 8 0 0 1 10 4a8 8 0 1 0 10 10Z"/>', 'book':'<path d="M3 4h6a4 4 0 0 1 3 1.5A4 4 0 0 1 15 4h6v15h-6a4 4 0 0 0-3 1.5A4 4 0 0 0 9 19H3Z"/><path d="M12 6v14"/>', 'archive':'<rect x="3" y="4" width="18" height="4" rx="1"/><path d="M5 8v12h14V8M9 12h6"/>'}
    return f'<svg viewBox="0 0 24 24" aria-hidden="true">{paths[name]}</svg>'
def topic_links(current, topics):
    return '<div class="chips">' + ''.join(f'<a class="chip" href="{rel(current,"search.html")}?topic={quote(t)}">{esc(t)}</a>' for t in topics) + '</div>'
def archive_rail(current):
    groups = defaultdict(lambda: defaultdict(list))
    for e in entries: groups[e['date'][:4]][e['date'][5:7]].append(e)
    parts = []
    for year, months in groups.items():
        parts.append(f'<details class="rail-archive" open><summary>{year}</summary><a href="{rel(current, year+"/index.html")}">Year overview</a>')
        for month, reports in months.items():
            name = date(int(year), int(month), 1).strftime('%B')
            parts.append(f'<a href="{rel(current,year+"/"+month+"/index.html")}">{name} <span aria-label="reports">({len(reports)})</span></a>')
            for e in reports:
                parts.append(f'<a class="day-link" href="{rel(current,e["path"])}">{int(e["date"][8:])} {name}</a>')
        parts.append('</details>')
    return ''.join(parts)
def shell(current, title, content, active='latest', description='Astroparticle physics papers and science news.', extra=''):
    url = lambda target: rel(current, target)
    nav = [('latest','Latest report',latest['path'],'book'),('archive','Archive','archive/index.html','archive'),('search','Search papers','search.html','search')]
    rail_links = ''.join(f'<a class="{"active" if active==key else ""}" href="{url(path)}"'+(' aria-current="page"' if active==key else '')+f'>{icon(i)}{label}</a>' for key,label,path,i in nav)
    top_links = ''.join(f'<a href="{url(path)}"'+(' aria-current="page"' if active==key else '')+f'>{label}</a>' for key,label,path in [('latest','Latest',latest['path']),('archive','Archive','archive/index.html'),('search','Search','search.html')])
    text = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} · Daily Physics Journal Club</title><meta name="description" content="{esc(description)}"><meta name="color-scheme" content="light dark"><meta name="theme-color" content="#111f3a"><link rel="icon" type="image/svg+xml" href="{url('assets/favicon.svg')}?v={FAVICON_VERSION}"><script>try{{document.documentElement.dataset.theme=localStorage.getItem('physics-journal-theme')||(matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light')}}catch{{document.documentElement.dataset.theme='light'}}</script><link rel="stylesheet" href="{url('assets/site.css')}"></head>
<body><a class="skip" href="#main">Skip to content</a><header class="masthead"><div class="mast-inner"><a class="brand" href="{url('index.html')}"><span class="monogram" aria-hidden="true">J.C.</span><span><span class="brand-name">Daily Physics Journal Club</span><span class="brand-caption">Astroparticle physics</span></span></a><nav class="topnav" aria-label="Main navigation">{top_links}<button class="theme-toggle" type="button" aria-label="Switch to dark mode" aria-pressed="false">{icon('moon')}<span>Dark</span></button></nav></div></header>
<details class="mobile-archive"><summary>Browse by date</summary><a href="{url('archive/index.html')}">All reports</a><a href="{url(latest['date'][:4]+'/index.html')}">{latest['date'][:4]}</a><a href="{url(latest['date'][:7].replace('-','/')+'/index.html')}">{date.fromisoformat(latest['date']).strftime('%B %Y')}</a></details>
<div class="layout"><aside class="sidebar" aria-label="Archive navigation"><div class="rail-title">Journal Club</div><nav class="rail-links">{rail_links}</nav><div class="rail-title">Browse by date</div>{archive_rail(current)}<div class="rail-bottom">{count_label(len(entries),'report')} · {count_label(sum(len(e['papers']) for e in entries),'paper')}<a href="{url('downloads/physics-journal-club.zip')}" download>Download HTML archive ↓</a></div></aside><main class="main" id="main">{content}<footer class="footer"><span>Daily Physics Journal Club</span><a href="{url('downloads/physics-journal-club.zip')}" download>Offline archive ↓</a></footer></main></div>{extra}<script src="{url('assets/site.js')}" defer></script></body></html>'''
    write(current, text)
def write(path, text):
    p = OUT / path; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(text)
    public_paths.add(Path(path))
def header(current,e,home=False):
    return f'''<div class="dateline"><span class="eyebrow">{esc(e['kind'])}</span></div><div class="report-header"><div><h1><time datetime="{e['date']}">{longdate(e['date'])}</time></h1><p class="deck">{esc(e['description'])}</p>{topic_links(current,e['topics'])}</div></div>'''
def paper_row(current,e,p,i):
    return f'''<article class="paper-row"><span class="num" aria-hidden="true">{i:02d}</span><div><span class="paper-label">{esc(p['label'])}</span><h3><a href="{rel(current,e['path'])}#{p['id']}">{esc(p['title'])}</a></h3><div class="meta">{esc(p['authors'])}</div><p class="teaser">{esc(p['teaser'])}</p></div><div class="paper-side"><span class="chip">{esc(p['tags'][0])}</span><a href="https://arxiv.org/abs/{p['arxiv']}" target="_blank" rel="noopener noreferrer">arXiv:{p['arxiv']} ↗</a><a href="{rel(current,e['path'])}#{p['id']}">Read summary →</a></div></article>'''
def inline(s):
    s = esc(s)
    s = re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',s)
    s = re.sub(r'\[([^\]]+)\]\((https?://[^\s)]+)\)',r'<a href="\2" target="_blank" rel="noopener noreferrer">\1 ↗</a>',s)
    return s
def source_card(p):
    return f'''<div class="source-card" id="{p['id']}"><span class="paper-label">{esc(p['label'])}</span><div class="source-title">{esc(p['title'])}</div><div class="meta">{esc(p['authors'])}</div><div class="meta">First submitted {shortdate(p['published'])} · Revised {shortdate(p['revised'])}</div><a href="https://arxiv.org/abs/{p['arxiv']}" target="_blank" rel="noopener noreferrer">arXiv:{p['arxiv']} ↗</a></div>'''
def markdown(e):
    formulas = []
    def math_replace(match):
        formula = match.group(1) if match.group(1) is not None else match.group(2)
        display = match.group(1) is not None
        output = render_math(formula.strip(), display='block' if display else 'inline')
        tag, cls = ('div', 'math-display') if display else ('span', 'math-inline')
        formulas.append(f'<{tag} class="{cls}">{output}</{tag}>')
        return f'JOURNALMATH{len(formulas)-1}TOKEN'
    body = re.sub(r'\\\[(.*?)\\\]|\\\((.*?)\\\)', math_replace, e['body'], flags=re.S)
    body = re.sub(r'<!-- paper:([a-z0-9-]+) -->', r'<div class="paper-anchor" id="\1"></div>', body)
    body = re.sub(r'^(#{3,4}) ', lambda m: m.group(1)[1:]+' ', body, flags=re.M)
    renderer = md_renderer.Markdown(extensions=['extra', 'sane_lists', 'toc'], extension_configs={'toc': {'toc_depth': '2-2'}})
    result = renderer.convert(body)
    headings = [(h['id'], html.unescape(re.sub('<[^>]+>', '', h['name']))) for h in renderer.toc_tokens]
    for i, formula in enumerate(formulas):
        token=f'JOURNALMATH{i}TOKEN'
        result=result.replace('<p>'+token+'</p>',formula).replace(token,formula)
    assert 'JOURNALMATH' not in result
    return result, headings
def breadcrumbs(current, e):
    y,m,_ = e['date'].split('-')
    return f'<nav class="crumbs" aria-label="Breadcrumb"><a href="{rel(current,"archive/index.html")}">Archive</a><span>/</span><a href="{rel(current,y+"/index.html")}">{y}</a><span>/</span><a href="{rel(current,y+"/"+m+"/index.html")}">{date.fromisoformat(e["date"]).strftime("%B")}</a><span>/</span><span>{int(e["date"][8:])}</span></nav>'

# Home: surface the latest paper selection or the full news-only report.
current = 'index.html'
home = header(current,latest,True)
home += f'<div class="notice">{esc(latest["scope"])}</div><div class="report-actions"><a class="button" href="{latest["path"]}">Read this report <span aria-hidden="true">→</span></a><a class="button secondary" href="archive/index.html">Browse the archive</a></div>'
home += f'<div class="section-line"><h2>In this report</h2><span>{report_count_label(latest)}</span></div>'
if latest['papers']:
    home += ''.join(paper_row(current,latest,p,i) for i,p in enumerate(latest['papers'],1))
else:
    body, _ = markdown(latest)
    home += f'<article class="prose">{body}</article>'
shell(current,'Latest report',home,description=latest['description'])

# A permanent, fully rendered page for every day. No client-side router or network fetch required.
for idx,e in enumerate(entries):
    current = e['path']; body, headings = markdown(e)
    toc = '<aside class="toc" aria-label="In this report"><div class="eyebrow">In this report</div>'+''.join(f'<a href="#{anchor}">{esc(title)}</a>' for anchor,title in headings)+'</aside>'
    content = breadcrumbs(current,e)+header(current,e)
    content += f'<div class="notice">{esc(e["scope"])}</div><div class="report-actions"><button type="button" class="button secondary" data-print>Print / save PDF</button><a class="button secondary" href="{rel(current,"editions/"+e["date"]+".md")}" download>Download Markdown ↓</a></div>'
    if e.get('correction'):
        content += f'<aside class="notice"><strong>Later correction:</strong> {esc(e["correction"])} <a href="{rel(current, "2026/09/14/index.html")}#verified-science-news">Read the 14 September update →</a></aside>'
    content += f'<div class="reading-layout"><article class="prose">{body}</article>{toc}</div>'
    pagination=[]
    if idx+1<len(entries): pagination.append(f'<a href="{rel(current,entries[idx+1]["path"])}">← {longdate(entries[idx+1]["date"])}</a>')
    pagination.append(f'<a href="{rel(current,"archive/index.html")}">All reports</a>')
    if idx>0: pagination.append(f'<a href="{rel(current,entries[idx-1]["path"])}">{longdate(entries[idx-1]["date"])} →</a>')
    content += '<nav class="day-pagination" aria-label="Report navigation">'+''.join(pagination)+'</nav>'
    shell(current,longdate(e['date']),content,active='latest' if idx == 0 else 'archive',description=e['description'])
    write('editions/'+e['date']+'.md', '# Daily Physics Journal Club — '+longdate(e['date'])+'\n\n'+e['description']+'\n\n'+re.sub(r'<!-- paper:[a-z0-9-]+ -->\n\n', '', e['body'])+'\n')

def archive_page(current,title,subset,crumb=''):
    content = crumb+f'<span class="eyebrow">The collection</span><h1 style="margin-top:.7rem">{esc(title)}</h1><p class="archive-intro">{count_label(len(subset),"report")} · Browse the journal by year, month, and day.</p>'
    groups=defaultdict(lambda:defaultdict(list))
    for e in subset: groups[e['date'][:4]][e['date'][5:7]].append(e)
    for year,months in groups.items():
        content += f'<section class="archive-group"><div class="archive-year"><h2><a href="{rel(current,year+"/index.html")}">{year}</a></h2><span>{count_label(sum(map(len,months.values())),"report")}</span></div>'
        for month,reports in months.items():
            name=date(int(year),int(month),1).strftime('%B')
            content+=f'<h3 class="month-heading"><a href="{rel(current,year+"/"+month+"/index.html")}">{name} →</a></h3>'
            for e in reports:
                content+=f'<a class="archive-row" href="{rel(current,e["path"])}"><div class="date-block">{int(e["date"][8:])}<span>{name[:3]}</span></div><div><span class="paper-label">{esc(e["kind"])}</span><h3>{longdate(e["date"])}</h3><p>{report_count_label(e)} · {esc(" / ".join(e["topics"]))}</p></div><span class="arrow" aria-hidden="true">→</span></a>'
        content+='</section>'
    shell(current,title,content,'archive')
archive_page('archive/index.html','The archive',entries)
for year in sorted({e['date'][:4] for e in entries}):
    current=year+'/index.html'
    archive_page(current,year,[e for e in entries if e['date'].startswith(year)],f'<nav class="crumbs" aria-label="Breadcrumb"><a href="{rel(current,"archive/index.html")}">Archive</a><span>/ {year}</span></nav>')
for month in sorted({e['date'][:7] for e in entries}):
    current=month.replace('-','/')+'/index.html'; y=month[:4]
    archive_page(current,date.fromisoformat(month+'-01').strftime('%B %Y'),[e for e in entries if e['date'].startswith(month)],f'<nav class="crumbs" aria-label="Breadcrumb"><a href="{rel(current,"archive/index.html")}">Archive</a><span>/</span><a href="{rel(current,y+"/index.html")}">{y}</a></nav>')

search_index=[]
for e in entries:
    for p in e['papers']:
        section=e['body'].split('<!-- paper:'+p['id']+' -->',1)[1].split('<!-- paper:',1)[0]
        # Stop before the next report section, such as the science-news heading.
        section=re.split(r'^#{1,3} ', section, maxsplit=1, flags=re.M)[0].strip()
        search_index.append({**p,'path':e['path']+'#'+p['id'],'reportDate':longdate(e['date']),'searchText':' '.join([p['title'],p['authors'],p['arxiv'],p['teaser'],e['date'],longdate(e['date']),*p['tags'],section])})
write('assets/search-index.js','window.JOURNAL_INDEX = '+json.dumps(search_index,ensure_ascii=False).replace('</',r'<\/')+';\n')
content='<span class="eyebrow">Across all reports</span><h1 style="margin-top:.7rem">Find a paper.</h1><p class="archive-intro">Search titles, authors, arXiv IDs, dates, and the full reading notes.</p><section class="search-panel" aria-label="Search the archive"><label class="search-label" for="search-input">What are you looking for?</label><div class="searchbox">'+icon('search')+'<input id="search-input" type="search" placeholder="Try IceCube, spectral break, or 2507.22233" autocomplete="off"></div><div class="filters" role="group" aria-label="Filter by topic">'+''.join(f'<button class="filter" type="button" data-topic="{esc(t)}" aria-pressed="{str(t=="All topics").lower()}">{esc(t)}</button>' for t in ['All topics']+all_topics)+'</div></section><p id="search-status" class="search-status" role="status" aria-live="polite"></p><div id="search-results"></div><noscript><p class="noscript">Search needs JavaScript. You can still <a href="archive/index.html">browse every report in the archive</a>.</p></noscript>'
shell('search.html','Search',content,'search',extra='<script src="assets/search-index.js"></script>')
shell('404.html','Page not found','<span class="eyebrow">404</span><h1 style="margin:1rem 0">This page isn’t in the archive.</h1><p class="deck">The address may be incomplete, or this report has not been saved yet.</p><a class="button" href="index.html">Return to the journal</a>','')

# Retired report URLs preserve links to papers and dated news after regrouping.
for current, route in json.loads((ROOT/'scripts/legacy_routes.json').read_text()).items():
    def relative_target(target):
        path, separator, fragment = target.partition('#')
        return rel(current, path) + (separator + fragment if separator else '')
    default = relative_target(route['default'])
    fragments = {key: relative_target(value) for key, value in route['fragments'].items()}
    script = '<script>const destinations='+json.dumps(fragments)+';let fragment=location.hash.slice(1);try{fragment=decodeURIComponent(fragment)}catch{}location.replace(Object.prototype.hasOwnProperty.call(destinations,fragment)?destinations[fragment]:'+json.dumps(default)+');</script>'
    content = '<h1>Report archive updated</h1><p class="deck">The papers are organized by arXiv listing date.</p>'
    content += '<div class="report-actions">'+''.join(
        f'<a class="button secondary" href="{rel(current,d.replace("-","/")+"/index.html")}">{longdate(d)}</a>'
        for d in ('2026-09-10','2026-09-11'))+'</div>'
    shell(current, 'Report archive updated', content, 'archive', extra=script)

# ZIP is an offline copy of the public assets. Its folder layout preserves every relative link.
zip_path=OUT/'downloads/physics-journal-club.zip';zip_path.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
    for relative_path in sorted(public_paths):
        p = OUT / relative_path
        if p.is_file():
            if p.suffix == '.html':
                offline = re.sub(r'<a\b[^>]*href="[^"]*physics-journal-club\.zip"[^>]*>.*?</a>', '<span>Offline copy</span>', p.read_text())
                z.writestr(str(p.relative_to(OUT)), offline)
            else:
                z.write(p,p.relative_to(OUT))
    z.writestr('READ-ME.txt','Open index.html after extracting this ZIP. Pages, search, styles, and equations work offline. External paper links require internet. To refresh this snapshot, download the archive again from the hosted site.\n')
print(f'Rendered {len(entries)} report(s), {len(search_index)} papers, and {sum(p.suffix == ".html" for p in public_paths)} HTML pages.')
