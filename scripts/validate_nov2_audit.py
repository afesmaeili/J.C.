"""Validate content preservation and every generated delivery surface."""
import json,re,subprocess,zipfile
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE='4aa88b555b80761fe010d53f985c64c647a662d7'
def split(s):
    _,f,b=re.split(r'^---[ \t]*$',s,maxsplit=2,flags=re.M)
    return json.loads(f),b.strip()
def before(path):
    return subprocess.check_output(['git','show',BASE+':'+str(path)],cwd=ROOT,text=True)
sources=sorted((ROOT/'content').glob('*.md'))
assert len(sources)==51
for p in sources:
    m,b=split(p.read_text())
    om,ob=split(before(p.relative_to(ROOT)))
    first=re.search(r'^### ',ob,re.M)
    oldsections=ob[first.start():].strip()
    firstnew=re.search(r'^### ',b,re.M)
    intro=b[:firstnew.start()].strip()
    assert intro.startswith('**arXiv · ')
    assert '\n\n' not in intro
    assert set(m['listing_statistics']['counts'])=={'astro-ph','hep-ph','hep-ex','hep-th','gr-qc','nucl-ex','nucl-th'}
    if p.stem!='2026-11-02':
        assert b[firstnew.start():].strip()==oldsections, 'Changed scientific body '+p.stem
        assert m['papers']==om['papers']
    else:
        original_arxiv=oldsections.split('### ArXiv Highlights',1)[1].split('### Science News',1)[0].strip()
        assert original_arxiv in b, 'Changed original paper studies'
        assert b.split('### Science News',1)[1]==ob.split('### Science News',1)[1], 'Changed original news'
    page=(ROOT/p.stem.replace('-','/')/'index.html').read_text()
    assert '<div class="notice">'+om.get('scope','')+'</div>' not in page
    assert (ROOT/'editions'/p.name).read_bytes()==p.read_bytes(), 'Markdown differs from source'
m,b=split((ROOT/'content/2026-11-02.md').read_text())
assert len(m['papers'])==25
anchors=re.findall(r'<!-- paper:([a-z0-9-]+) -->',b)
assert Counter(anchors)==Counter(p['id'] for p in m['papers'])
assert len(re.findall(r'^##### History\s*$',b,re.M))==25
for title in ('ArXiv Highlights','Science News','Science Radar'):
    assert b.count('### '+title+'\n')==1
assert b.endswith('END OF JOURNAL CLUB — 2026-11-02')
page=(ROOT/'2026/11/02/index.html').read_text()
search=(ROOT/'assets/search-index.js').read_text()
for p in m['papers']:
    assert 'id="'+p['id']+'"' in page
    assert p['arxiv'] in search
assert '25 paper studies' in page
assert 'How the journal is prepared' in (ROOT/'index.html').read_text()
assert '2026/11/11/index.html' in (ROOT/'index.html').read_text(), 'Latest link changed'
with zipfile.ZipFile(ROOT/'downloads/physics-journal-club.zip') as z:
    assert z.testzip() is None
    assert z.read('editions/2026-11-02.md')==(ROOT/'content/2026-11-02.md').read_bytes()
    zipped=z.read('2026/11/02/index.html').decode()
    for p in m['papers']: assert p['id'] in zipped
for asset in ('assets/site.css','assets/site.js','assets/favicon.svg'):
    assert (ROOT/asset).read_text()==before(Path(asset)), 'Changed design asset'
print('PASS: 51 openings; 23 additions; 25 History sections; prior science/news preserved; anchors, search, latest link, Markdown and offline ZIP verified.',flush=True)
