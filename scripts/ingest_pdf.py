"""Extract chapter clauses from the real PDF; fail if metadata and PDF disagree.
Only the supplied, one-chapter-per-page handbook layout is supported. Scans need OCR.
"""
import hashlib, json, re
from pathlib import Path
import fitz
root = Path(__file__).resolve().parents[1]
pdf = root / 'public/Demo_Company_Policy.pdf'
policies = json.loads((root / 'public/policies.json').read_text())
chunks=[]
with fitz.open(pdf) as doc:
    for p in policies:
        if not p['active']: continue
        raw=doc[p['page']-1].get_text()
        lines=raw.splitlines()
        if re.sub(r'\s+',' ',p['title']).strip() not in re.sub(r'\s+',' ',raw): raise ValueError(f"Missing chapter: {p['id']}")
        lines=lines[lines.index(p['clauses'][0]['heading']):]
        for i,c in enumerate(p['clauses']):
            start=lines.index(c['heading'])+1
            end=lines.index(p['clauses'][i+1]['heading']) if i+1<len(p['clauses']) else len(lines)
            text=' '.join(x.strip() for x in lines[start:end] if x.strip())
            norm=lambda s:re.sub(r'\s+',' ',s).strip()
            if norm(text)!=norm(c['text']): raise ValueError(f"PDF/JSON disagreement: {p['id']} clause {i}")
            chunks.append({'id':f"{p['id']}-{i+1}",'policy_id':p['id'],'title':p['title'],'heading':c['heading'],'text':text,'page':p['page'],'version':p['version'],'active':True})
result={'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'method':'PDF text extraction and verified clause headings','chunks':chunks}
(root/'data/chunks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(f'Extracted and verified {len(chunks)} clause chunks from {len(policies)} PDF chapters.')
