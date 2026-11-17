#!/usr/bin/env python3
"""Check static release contracts without fetching third-party resources."""
import argparse
from collections import Counter
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import urlsplit, unquote
import xml.etree.ElementTree as ET

class Document(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.elements=[]; self.ids=[]; self.texts={'title':[], 'h1':[]}; self.current=None
        self.schemas=[]; self.json_text=None
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs); self.elements.append((tag,attrs))
        if attrs.get('id'):self.ids.append(attrs['id'])
        if tag in self.texts:self.current=tag
        if tag=='script' and attrs.get('type')=='application/ld+json':self.json_text=''
    def handle_data(self, text):
        if self.current:self.texts[self.current].append(text)
        if self.json_text is not None:self.json_text+=text
    def handle_endtag(self, tag):
        if tag==self.current:self.current=None
        if tag=='script' and self.json_text is not None:
            self.schemas.append(json.loads(self.json_text));self.json_text=None
    def select(self, tag):return [a for t,a in self.elements if t==tag]

def audit(root, production=False):
    errors=[];pages=sorted(root.rglob('*.html'));docs={p.resolve():Document(p.read_text()) for p in pages}
    assert len(pages)==28, f'Expected 28 HTML pages, got {len(pages)}'
    titles=[];heads=[];descriptions=[];links=0;images=0
    for p in pages:
        d=docs[p.resolve()];rel=p.relative_to(root).as_posix()
        def check(ok, message):
            if not ok:errors.append(f'{rel}: {message}')
        check(len(d.select('h1'))==1,'exactly one H1 required')
        check(len(d.select('main'))==1,'exactly one main landmark required')
        check(len(d.ids)==len(set(d.ids)),'duplicate DOM IDs')
        title=''.join(d.texts['title']);h1=''.join(d.texts['h1'])
        titles.append(title);heads.append(h1)
        metas=d.select('meta');robots=[a.get('content','') for a in metas if a.get('name')=='robots']
        desc=[a.get('content','') for a in metas if a.get('name')=='description'];descriptions+=desc
        check(bool(title) and len(desc)==1,'missing or duplicate title/description')
        canonical=[a.get('href') for a in d.select('link') if a.get('rel')=='canonical']
        expected='https://qazairpres.kz/'+('' if rel=='index.html' else rel.replace('/index.html','/'))
        check(canonical==[expected],'canonical must match the production URL')
        excluded=rel in ['privacy.html','products/air-filter-a569.html']
        check(robots==['index,follow' if production and not excluded else 'noindex,nofollow,noarchive'],'wrong index policy')
        graph=[entry for schema in d.schemas for entry in schema.get('@graph',[])]
        check(any(x.get('@type')=='Organization' for x in graph),'missing Organization schema')
        if rel!='index.html':check(any(x.get('@type')=='BreadcrumbList' for x in graph),'missing BreadcrumbList')
        if rel.startswith('products/'):
            products=[x for x in graph if x.get('@type')=='Product'];check(len(products)==1,'missing Product schema')
            check(bool(products[0].get('additionalProperty')),'missing product properties')
            check('availability' not in products[0].get('offers',{}),'unconfirmed availability')
            check(any(a.get('data-lead')==products[0]['name'] for a in d.select('a')),'missing model-specific CTA')
            check('image' in products[0] or not any(a.get('property')=='og:image' for a in metas),'unrelated OG image on a product without an approved photo')
        for tag,a in d.elements:
            if tag=='img':
                images+=1
                check(bool(a.get('alt')) and a.get('width') and a.get('height'),'image lacks alt or reserved dimensions')
                check(a.get('loading')=='lazy' or a.get('fetchpriority')=='high','unprioritized image')
                check(not a.get('src','').startswith('http'),'hotlinked product image')
            for attr in ['href','src']:
                u=a.get(attr)
                if not u:continue
                parsed=urlsplit(u)
                if parsed.scheme:
                    if parsed.netloc=='wa.me':check(parsed.path=='/77761717111','wrong WhatsApp number')
                    if parsed.scheme=='tel':check(parsed.path=='+77761717111','wrong phone')
                    continue
                links+=1;target=(p.parent/unquote(parsed.path)).resolve() if parsed.path else p.resolve()
                if target.is_dir():target=target/'index.html'
                check(target.exists(),f'broken {attr}: {u}')
                if parsed.fragment and target in docs:check(parsed.fragment in docs[target].ids,f'broken anchor: {u}')
            for candidate in a.get('srcset','').split(','):
                if candidate.strip():check((p.parent/candidate.split()[0]).exists(),'missing srcset image')
    for values,name in [(titles,'title'),(heads,'H1'),(descriptions,'description')]:
        for value,n in Counter(values).items():
            if n>1:errors.append(f'Duplicate {name}: {value}')
    sitemap=ET.parse(root/'sitemap.xml');urls=[x.text for x in sitemap.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
    if production:
        if len(urls)!=26 or any('privacy' in u or 'air-filter-a569' in u for u in urls):errors.append('Production sitemap must contain exactly 26 eligible URLs')
    elif urls:errors.append('Preview sitemap must be empty')
    if not production and (root/'robots.txt').read_text()!='User-agent: *\nDisallow: /\n':errors.append('Preview robots policy')
    result={'mode':'production export' if production else 'preview','pages':len(pages),'local_references_checked':links,'image_elements':images,'unique_titles':len(set(titles)),'unique_descriptions':len(set(descriptions)),'sitemap_urls':len(urls),'errors':errors}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 1 if errors else 0

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);parser.add_argument('--production',action='store_true');args=parser.parse_args()
    raise SystemExit(audit(args.root,args.production))
