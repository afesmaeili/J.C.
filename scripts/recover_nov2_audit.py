"""One-time source recovery for the independently researched 2 November audit."""
import concurrent.futures, html, json, re, time
from collections import Counter
from datetime import date, datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen
from listing_statistics import CATEGORIES, listing_sentence
ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / '.nov2-recovery-cache'
CACHE.mkdir(exist_ok=True)
CHECKED = datetime.now(timezone.utc).isoformat()
def plain(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]*>', ' ', s))).strip()
def get(url):
    key = re.sub(r'[^a-zA-Z0-9._-]', '_', url)
    p = CACHE / key
    if p.exists(): return p.read_text()
    errors = []
    for attempt in range(2):
        try:
            request = Request(url, headers={'User-Agent':'JournalClubArchiveAudit/1.0 (dated academic bibliography verification)'})
            with urlopen(request, timeout=60) as response:
                data = response.read().decode('utf-8')
            assert len(data) > 100, 'Empty source'
            p.write_text(data)
            return data
        except Exception as exc:
            errors.append(str(exc))
            if not attempt: time.sleep(3)
    raise RuntimeError(url + ': ' + ' | '.join(errors))
def listing(day, category):
    url = f'https://arxiv.org/catchup/{category}/{day}?abs=True'
    raw = get(url)
    p = plain(raw)
    d = date.fromisoformat(day)
    tokens = [d.strftime('%-d %B %Y'), d.strftime('%-d %b %Y')]
    assert any(token in p for token in tokens), 'Listing date mismatch: '+url
    if re.search(r'no (?:updates|submissions|articles)', p, re.I) and not re.search(r'/abs/\d{4}\.\d+', raw):
        return {'date':day, 'category':category, 'count':0, 'ids':[], 'subcategories':{}, 'source':url, 'entries':[]}
    parts = re.split(r'(<h3\b[^>]*>.*?</h3>)', raw, flags=re.S|re.I)
    state = None
    entries = []
    for chunk in parts:
        if re.match(r'<h3\b', chunk, re.I):
            h = plain(chunk).lower()
            state = 'New' if 'new submission' in h else 'Cross' if 'cross' in h else 'Replacement' if 'replacement' in h else None
            continue
        if state is None: continue
        for dt, dd in re.findall(r'<dt\b[^>]*>(.*?)</dt>\s*<dd\b[^>]*>(.*?)</dd>', chunk, re.S|re.I):
            ids = re.findall(r'/abs/(\d{4}\.\d+)', dt)
            if not ids: continue
            primary = re.search(r'class=["\']primary-subject["\'][^>]*>(.*?)</span>', dd, re.S)
            cats = re.findall(r'\(([a-z-]+(?:\.[A-Z-]+)?)\)', plain(primary.group(1) if primary else dd))
            title = re.search(r'class=["\']list-title[^"\']*["\'][^>]*>(.*?)</div>', dd, re.S)
            entries.append({'id':ids[0], 'kind':state, 'primary_category':cats[0] if cats else None, 'title':re.sub(r'^Title:\s*','',plain(title.group(1))) if title else ''})
    assert entries, 'No entries parsed: '+url
    selected = {e['id']:e for e in entries if e['kind']=='New'}
    assert selected or 'new submissions' not in p.lower(), 'New section parse failure: '+url
    subs = Counter(e['primary_category'] for e in selected.values())
    if category == 'astro-ph':
        assert all(k and k.startswith('astro-ph.') for k in subs), 'Astro primary categories missing'
    return {'date':day,'category':category,'count':len(selected),'ids':list(selected),'subcategories':dict(subs),'source':url,'entries':entries}
def split(raw):
    _, front, body = re.split(r'^---[ \t]*$', raw, maxsplit=2, flags=re.M)
    return json.loads(front), body.strip()
def save(p, m, b):
    p.write_text('---\n'+json.dumps(m,ensure_ascii=False,indent=2)+'\n---\n\n'+b.strip()+'\n')
sources = sorted((ROOT/'content').glob('*.md'))
tasks = [(p.stem,c) for p in sources for c in CATEGORIES]
results = {}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    futures = {pool.submit(listing,*t):t for t in tasks}
    for future in concurrent.futures.as_completed(futures):
        t = futures[future]
        results[t] = future.result()
print('Verified category/date listings:',len(results),flush=True)
assert {c:results[('2026-11-02',c)]['count'] for c in CATEGORIES} == {'astro-ph':79,'hep-ph':22,'hep-ex':4,'hep-th':23,'gr-qc':21,'nucl-ex':1,'nucl-th':7}, 'November 2 counts differ from independently checked counts'
for path in sources:
    m,b = split(path.read_text())
    first = re.search(r'^### ', b, re.M)
    assert first, 'No section heading: '+str(path)
    oldintro, rest = b[:first.start()].strip(), b[first.start():]
    stats = {'date':m['date'],'basis':'new_primary_submissions',
        'counts':{c:results[(m['date'],c)]['count'] for c in CATEGORIES},
        'sources':{c:results[(m['date'],c)]['source'] for c in CATEGORIES},
        'verified_at':CHECKED,
        'excluded':'Cross-lists and replacements; each paper counted by primary category only.'}
    if stats['counts']['astro-ph']:
        stats['astro_subcategories'] = results[(m['date'],'astro-ph')]['subcategories']
    audit = m.setdefault('source_audit',{})
    audit.setdefault('original_introduction',oldintro)
    audit.setdefault('original_scope',m.get('scope',''))
    m['listing_statistics'] = stats
    save(path,m,listing_sentence(stats)+'\n\n'+rest)

class Meta(HTMLParser):
    def __init__(self): super().__init__(); self.values={}
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='meta' and 'name' in a and 'content' in a:
            self.values.setdefault(a['name'],[]).append(a['content'])
studies = json.loads((ROOT/'docs/nov2-additions.json').read_text())
assert len(studies)==23
path=ROOT/'content/2026-11-02.md'
m,b=split(path.read_text())
existing=set(p['arxiv'] for p in m['papers'])
all_entries={e['id']:e for c in CATEGORIES for e in results[('2026-11-02',c)]['entries']}
sections=[]
for n,s in enumerate(studies,3):
    aid=s['arxiv']
    assert aid not in existing and aid in all_entries, 'Duplicate or not in dated listings: '+aid
    assert all_entries[aid]['kind'] in ('New','Cross'), 'Replacement needs separate treatment'
    for other in sources:
        if other==path: continue
        om,_=split(other.read_text())
        assert not any(p['arxiv']==aid for p in om['papers']), 'Already reviewed elsewhere: '+aid
    raw=get('https://arxiv.org/abs/'+aid+'v1')
    meta=Meta();meta.feed(raw)
    title=' '.join(meta.values['citation_title'][0].split())
    authors=', '.join(meta.values['citation_author'])
    assert title and authors
    assert '[v1]' in plain(raw), 'Version record missing'
    if all_entries[aid]['primary_category']:
        assert all_entries[aid]['primary_category']==s['primary_category'], 'Category mismatch'
    anchor='paper-'+aid.replace('.','-')
    paper={'id':anchor,'arxiv':aid,'title':title,'authors':authors,'primary_category':s['primary_category'],
        'tags':s['tags'],'label':'Retrospective addition · '+s['label'],
        'teaser':s['heading'],'review_date':'2026-11-11','listing_date':'2026-11-02','version':'v1','submission_date':s['submission']}
    m['papers'].append(paper)
    existing.add(aid)
    stamp=datetime.fromisoformat(s['submission'].replace('Z','+00:00')).strftime('%-d %B %Y, %H:%M:%S UTC')
    header=f"<!-- paper:{anchor} -->\n#### {n}. {s['heading']}\n\n"
    header+=f"**“{title}” — {authors}.** [arXiv:{aid}v1](https://arxiv.org/abs/{aid}v1) · [full text](https://arxiv.org/html/{aid}v1) · [PDF](https://arxiv.org/pdf/{aid}v1). Submitted **{stamp}**; UTC listing **2 November 2026**; primary category **{s['primary_category']}**. **{s['label']}.** {s['status']} Added retrospectively **11 November 2026**.\n\n"
    sections.append(header+s['text'].strip()+'\n\n##### History\n\n'+s['history'].strip())
note="**Retrospective expansion · 11 November 2026:** this edition now contains **25 paper studies**, including **23 additions** from the 2 November listing. The two original studies and the original news remain below. Sato, Zhang and Murase's [structured-jet/external-Compton paper, 2610.41476](https://afesmaeili.github.io/J.C./2026/11/03/#paper-2610-41476), also belongs to this listing and was already reviewed in the [3 November catch-up](https://afesmaeili.github.io/J.C./2026/11/03/); it is linked here without duplicating its study or counting it among these additions."
b=b.replace('### ArXiv Highlights','### ArXiv Highlights\n\n'+note,1)
assert '\n### Science News' in b
b=b.replace('\n### Science News','\n\n'+'\n\n'.join(sections)+'\n\n### Science News',1)
counts=dict(sorted(Counter(p['primary_category'] for p in m['papers']).items()))
m['description']='25 selected papers, including 23 retrospective additions · 4 science-news stories · 1 Science Radar story.'
m['scope']='2 November UTC listing; expanded 11 November with 23 additional full-text studies. Original news cutoff and coverage retained in source_audit.'
m['topics']=list(dict.fromkeys(m['topics']+[t for s in studies for t in s['tags']]))
m['statistics']={'basis':'selected_papers_by_primary_category','date':'2026-11-02','counts':counts,'selected_papers_by_primary_category':counts,'provenance':'25 unique studies on this page; 23 added retrospectively on 11 November. Separate from full-list totals. The already-reviewed 2610.41476 is linked, not counted twice.'}
m['source_audit']['retrospective_review']={'review_date':'2026-11-11','metadata_rechecked_at':CHECKED,'listing_date':'2026-11-02','added_papers':[s['arxiv'] for s in studies],'coverage':'Dated new and cross-listed titles screened across seven archives, with priority abstracts and replacement titles checked. Selected additions received full-text methods/results/figure and limitations review plus independent historical literature checks. Not every screened paper was read in full. News was preserved, not retrospectively refreshed.'}
save(path,m,b)
audit={'date':'2026-11-02','review_date':'2026-11-11','listing_counts':m['listing_statistics'],'added_papers':[s['arxiv'] for s in studies],'original_papers':['2610.41163','2610.40782'],'already_reviewed_on_2026_11_03':['2610.41476'],'coverage':m['source_audit']['retrospective_review']['coverage'],'screened_entries':all_entries,'history_references':sorted(set(re.findall(r'https://arxiv.org/abs/[^)\s]+','\n'.join(s['history'] for s in studies))))}
(ROOT/'docs/arxiv-audit-2026-11-02.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
(ROOT/'docs/archive-listing-statistics.json').write_text(json.dumps([{k:v for k,v in r.items() if k!='entries'} for _,r in sorted(results.items())],ensure_ascii=False,indent=2)+'\n')
# Remove temporary retrieval cache; it is not repository content.
import shutil
shutil.rmtree(CACHE)
print('Added 23 studies; migrated',len(sources),'daily openings.',flush=True)
