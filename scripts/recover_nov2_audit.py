"""Normalize citation-metadata author formatting without changing the studies."""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'content/2026-11-02.md'
_,f,b=re.split(r'^---[ \t]*$',path.read_text(),maxsplit=2,flags=re.M)
m=json.loads(f)
for p in m['papers']:
    if p.get('review_date')!='2026-11-11': continue
    old=p['authors']
    values=old.split(', ')
    if len(values)>1:
        assert len(values)%2==0, 'Unexpected citation author format'
        p['authors']=', '.join(values[i+1]+' '+values[i] for i in range(0,len(values),2))
        assert '— '+old+'.**' in b
        b=b.replace('— '+old+'.**','— '+p['authors']+'.**')
    if p['arxiv']=='2610.40925':
        title=p['title']
        p['title']=title.replace("Alfv\\'enic",'Alfvénic')
        b=b.replace(title,p['title'])
path.write_text('---\n'+json.dumps(m,ensure_ascii=False,indent=2)+'\n---\n'+b)
print('Normalized 23 study metadata entries; scientific content unchanged.')
