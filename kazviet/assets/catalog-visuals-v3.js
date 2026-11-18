(function(){
'use strict';
/* All product photography is self-hosted in the KAZVIET repository.
   These are category illustrations, not verified photographs of each company. */
const base='/kazviet/assets/';
const profiles=new Set([
'kazcrop','sevesilzerno','maslodel','organicum-bio','altyn-harvest','kazkon','dynasty-agro','grain-consortium',
'simexco-daklak','intimex-group','fpv-vietnam','tt-plywood','hg-plywood','dongstar-wood','tekcom','anh-phuong'
]);
const categories={
furniture:'suppliers/fpv-vietnam.jpg',
components:'suppliers/tt-plywood.jpg',
agri:'suppliers/kazcrop.jpg',
textiles:'categories/textiles.jpg',
packaging:'categories/packaging.jpg',
industrial:'categories/industry.jpg',
electronics:'categories/electronics.jpg',
construction:'suppliers/hg-plywood.jpg'
};
function fallback(id){
 const x=[['#123852','#198fa2'],['#27485e','#6a927d'],['#504034','#ba985b'],['#213e63','#5b83b8']];
 let n=0;for(const c of id)n=(n*31+c.charCodeAt(0))%1024;const c=x[n%4];
 const svg='<svg xmlns="http://www.w3.org/2000/svg" width="960" height="540" viewBox="0 0 960 540"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop stop-color="'+c[0]+'"/><stop offset="1" stop-color="'+c[1]+'"/></linearGradient></defs><rect width="960" height="540" fill="url(#g)"/><circle cx="815" cy="120" r="255" fill="#ffffff" opacity=".06"/><circle cx="840" cy="400" r="200" fill="#ffffff" opacity=".045"/><path d="M0 425C260 330 450 525 960 300V540H0Z" fill="#ffffff" opacity=".09"/><path d="M0 490C260 390 650 575 960 410V540H0Z" fill="#ffffff" opacity=".05"/><text x="70" y="365" font-family="Arial,sans-serif" font-size="64" font-weight="800" fill="#fff" letter-spacing="5">KAZVIET</text><rect x="70" y="393" width="150" height="5" rx="2.5" fill="#73e0dd"/></svg>';
 return 'data:image/svg+xml;charset=utf-8,'+encodeURIComponent(svg);
}
function createImage(path,alt,slug,cls,priority){
 const img=document.createElement('img');
 img.className=cls;img.src=base+path+'?v=20261118b';img.alt=alt;img.width=960;img.height=540;
 img.loading=priority?'eager':'lazy';img.decoding='async';
 if(priority)img.fetchPriority='high';
 img.onerror=function(){img.onerror=null;img.src=fallback(slug)};
 return img;
}
function slugFrom(a){const p=(a.getAttribute('href')||'').split('#')[0].split('/').filter(Boolean);return p[p.length-1]||''}
function lang(){return document.documentElement.lang==='en'?'en':document.documentElement.lang==='kk'?'kk':'ru'}
const txt={
ru:{cta:'Запросить предложение',card:'Товары и запрос цены',countryKz:'Казахстан',countryVn:'Вьетнам'},
en:{cta:'Request a quotation',card:'Products & quotation',countryKz:'Kazakhstan',countryVn:'Vietnam'},
kk:{cta:'Ұсыныс сұрау',card:'Тауарлар мен баға сұрау',countryKz:'Қазақстан',countryVn:'Вьетнам'}
};
function cleanCountry(node){
 const value=node.textContent;
 const isKz=/🇰🇿|\bkz\b|Kazakh|Қазақ|Казах/i.test(value);
 node.textContent=isKz?txt[lang()].countryKz:txt[lang()].countryVn;
 node.classList.add(isKz?'kv-country-kz':'kv-country-vn');
}
function addTags(card){
 if(card.querySelector('.kv-product-tags'))return;
 const desc=card.querySelector('p');if(!desc)return;
 const words=desc.textContent.split(/[,，;]+/).map(s=>s.trim()).filter(Boolean);
 const wrap=document.createElement('div');wrap.className='kv-product-tags';
 words.slice(0,3).forEach(word=>{const chip=document.createElement('span');chip.textContent=word.length>26?word.slice(0,25).trim()+'…':word;wrap.appendChild(chip)});
 if(wrap.children.length)desc.insertAdjacentElement('afterend',wrap);
}
function improveSupplierCard(card,index){
 const slug=slugFrom(card);if(!profiles.has(slug))return;
 card.dataset.kvVisualReady='1';
 const img=createImage('suppliers/'+slug+'.jpg',card.textContent.trim(),slug,'kv-cover',index<4);
 card.prepend(img);card.classList.add('kv-elevated');
 card.querySelectorAll('.kvSFlag').forEach(cleanCountry);
 addTags(card);
 const cta=card.querySelector('.kvSSource');if(cta){cta.textContent=txt[lang()].cta;cta.setAttribute('role','link');cta.setAttribute('aria-label',txt[lang()].cta+' — '+(card.querySelector('strong')?.textContent||''));}
}
function improveDirectoryCard(card,index){
 const slug=slugFrom(card);if(!profiles.has(slug))return;
 card.dataset.kvVisualReady='1';
 card.prepend(createImage('suppliers/'+slug+'.jpg',card.querySelector('h2')?.textContent||'',slug,'kv-cover',index<4));
 card.querySelectorAll('.tag').forEach(cleanCountry);
 const meta=card.querySelector('.meta');if(meta)meta.textContent=txt[lang()].card+' →';
}
function improveCategory(card){
 const slug=card.dataset.cat,path=categories[slug];if(!path)return;
 card.dataset.kvVisualReady='1';card.prepend(createImage(path,card.textContent.trim(),slug,'kv-cat-image',false));
}
function productPhoto(label,defaultSlug){
 const q=(label||'').toLowerCase();
 if(/(?:flour|мук|ұн|bột mì|cám|bran)/.test(q))return 'suppliers/sevesilzerno.jpg';
 if(/(?:linseed|flax|л[её]н|зығыр|hạt lanh)/.test(q))return 'suppliers/dynasty-agro.jpg';
 if(/(?:rapeseed|рапс|cải dầu|canola|sunflower|подсолнечник|күнбағыс)/.test(q))return 'suppliers/altyn-harvest.jpg';
 if(/(?:oil|масло|масл|dầu|май)/.test(q))return 'suppliers/maslodel.jpg';
 if(/(?:beans|pulses|бобов|бұршақ|legumes|lentil|чечевиц|đậu)/.test(q))return 'suppliers/organicum-bio.jpg';
 if(/(?:coffee|кофе|cà phê)/.test(q))return 'suppliers/simexco-daklak.jpg';
 if(/(?:chocolate|кондитер|сладост|bánh kẹo|confection)/.test(q))return 'suppliers/kazkon.jpg';
 if(/(?:furniture|мебел|жиһаз|nội thất)/.test(q))return 'suppliers/fpv-vietnam.jpg';
 if(/(?:packing|packaging|упаков|bao bì)/.test(q))return 'suppliers/tt-plywood.jpg';
 if(/(?:plywood|фанер|ván ép|ағаш тақт)/.test(q))return 'suppliers/hg-plywood.jpg';
 if(/(?:veneer|шпон|ván lạng)/.test(q))return 'suppliers/anh-phuong.jpg';
 if(/(?:grain|cereal|wheat|зерн|пшениц|астық|lúa mì|ngũ cốc)/.test(q))return 'suppliers/kazcrop.jpg';
 return 'suppliers/'+defaultSlug+'.jpg';
}
function improveCompanyPage(p){
 const slug=p.dataset.slug;if(!profiles.has(slug))return;
 const hero=document.querySelector('main .hero');
 if(hero&&!hero.classList.contains('kv-image-hero')){hero.classList.add('kv-image-hero');hero.style.setProperty('--kv-hero-photo','url("'+base+'suppliers/'+slug+'.jpg")')}
 document.querySelectorAll('.kvProduct:not([data-kv-visual-ready])').forEach((v,i)=>{v.dataset.kvVisualReady='1';v.prepend(createImage(productPhoto(v.textContent.trim(),slug),v.textContent.trim(),slug+'-product-'+i,'kv-product-image',i===0))});
}
function run(){
 document.querySelectorAll('a.kvSeedCard:not([data-kv-visual-ready])').forEach((c,i)=>improveSupplierCard(c,i));
 document.querySelectorAll('a.card:not([data-kv-visual-ready])').forEach((c,i)=>improveDirectoryCard(c,i));
 document.querySelectorAll('#categoryList [data-cat]:not([data-kv-visual-ready])').forEach(improveCategory);
 const p=document.querySelector('[data-kv-company]');if(p)improveCompanyPage(p);
}
const styles=`
/* KAZVIET premium responsive catalog — photo-first, stable grids */
#realSuppliersPreview,.kvSeeds,.hero,.kv-directory .hero,#enquiry{scroll-margin-top:96px!important}
.kvSeeds{padding:26px 28px!important}
.kvSeedsHead{align-items:center!important;margin-bottom:20px!important}
.kvSeedsHead h2{font-size:clamp(23px,2.2vw,32px)!important;line-height:1.15!important;letter-spacing:-1px}
.kvSeedsHead p{color:#61798d!important;font-size:13px!important;line-height:1.65!important}
.kvSeedsGrid{display:grid!important;grid-template-columns:repeat(4,minmax(0,1fr))!important;gap:18px!important}
.kvSeedCard{position:relative;display:flex!important;flex-direction:column!important;gap:0!important;padding:0!important;border:1px solid #e2ebf2!important;background:white!important;border-radius:17px!important;min-height:0!important;overflow:hidden;box-shadow:0 6px 22px rgba(17,56,90,.045)!important;transition:transform .2s,box-shadow .2s,border-color .2s!important}
.kvSeedCard:hover{transform:translateY(-4px)!important;box-shadow:0 16px 34px rgba(17,56,90,.12)!important;border-color:#7bc9df!important}
.kvSeedCard .kv-cover,.kv-directory .card .kv-cover{display:block!important;width:100%!important;height:auto!important;aspect-ratio:16/9!important;object-fit:cover!important;margin:0!important;background:#dceaf0;flex-shrink:0}
.kvSeedCard .kvSFlag{margin:16px 17px 0!important;font-size:11px!important;display:inline-flex!important;gap:8px;align-items:center!important;color:#517b91!important;font-weight:750!important}
.kvSeedCard .kvSFlag:before,.kv-directory .card .tag:before{content:'';display:inline-block;background:#24a7c4;width:9px;height:9px;border-radius:50%;box-shadow:0 0 0 3px #e2f5f9}
.kvSeedCard .kvSFlag.kv-country-vn:before,.kv-directory .card .tag.kv-country-vn:before{background:#e55c56;box-shadow:0 0 0 3px #fff0ef}
.kvSeedCard strong{display:block!important;margin:8px 17px 0!important;color:#122a43!important;font-size:16px!important;font-weight:800!important;letter-spacing:-.45px;line-height:1.3}
.kvSeedCard p{margin:9px 17px 8px!important;color:#617c8e!important;font-size:12px!important;line-height:1.55!important;display:-webkit-box!important;-webkit-box-orient:vertical;-webkit-line-clamp:2;overflow:hidden!important;min-height:37px;flex:initial!important}
.kv-product-tags{margin:0 17px 14px;display:flex;flex-wrap:wrap;gap:5px;min-height:26px;align-content:start}
.kv-product-tags span{font-size:10px;color:#4b6d80;padding:5px 8px;border:1px solid #e1eaf0;background:#f5f9fc;border-radius:100px;max-width:100%;text-overflow:ellipsis;overflow:hidden;white-space:nowrap}
.kvSeedCard .kvSSource{display:flex!important;align-items:center!important;justify-content:space-between!important;margin:auto 17px 17px!important;padding:12px 14px!important;min-height:44px;background:linear-gradient(102deg,#08aeb5,#087fb6)!important;color:#fff!important;font-size:12px!important;font-weight:800!important;border-radius:10px!important;text-decoration:none}
.kvSeedCard .kvSSource:after{content:'↗';font-size:18px;line-height:1}
.kvSeedCard:hover .kvSSource{filter:brightness(1.06)}
.kv-directory .cards{gap:18px!important}
.kv-directory .card{display:flex!important;flex-direction:column!important;padding:0!important;overflow:hidden;min-height:0!important;background:white;border-radius:16px!important;border:1px solid #e2ebf2!important;box-shadow:0 5px 20px rgba(17,56,90,.045)}
.kv-directory .card:hover{transform:translateY(-4px);box-shadow:0 16px 34px rgba(17,56,90,.12)!important}
.kv-directory .card .tag{display:inline-flex;align-self:flex-start;align-items:center;gap:8px;margin:14px 16px 0!important;font-size:11px!important}
.kv-directory .card h2{margin:10px 16px 0!important;font-size:17px!important;line-height:1.3;letter-spacing:-.3px}
.kv-directory .card p{margin:9px 16px 12px!important;color:#627b8a;line-height:1.6;min-height:42px;font-size:13px}
.kv-directory .card .meta{margin:auto 16px 16px!important;display:block;padding:11px 12px;background:#eaf8fa;color:#087c9e!important;border-radius:9px;font-size:12px!important;font-weight:800}
.kv-directory .kvProduct{padding:0!important;overflow:hidden;border-radius:14px!important}
.kv-directory .kvProduct img.kv-product-image{display:block;width:100%;height:auto;aspect-ratio:16/9;object-fit:cover}
.kv-directory .kvProduct>.kvDot{display:none}
.kv-directory .kvProduct strong,.kv-directory .kvProduct small{margin-left:15px;margin-right:15px}
.kv-directory .kvProduct small{margin-bottom:15px;display:block}
#categoryList .cat{min-height:62px!important;overflow:hidden}
#categoryList .cat[data-cat]:not([data-cat="all"]){position:relative;padding-left:64px!important}
#categoryList .cat[data-cat]:not([data-cat="all"]) img.kv-cat-image{position:absolute;left:8px;top:50%;transform:translateY(-50%);width:44px;height:44px;object-fit:cover;border-radius:10px}
#categoryList .cat[data-cat]:not([data-cat="all"])>span:first-of-type{display:none}
.kv-directory .hero.kv-image-hero{position:relative;overflow:hidden;padding-right:min(35%,380px);background:linear-gradient(110deg,#eaf8fe,#d9f0f5)!important}
.kv-directory .hero.kv-image-hero:before{content:'';position:absolute;top:0;bottom:0;right:0;width:34%;background:var(--kv-hero-photo) center/cover;opacity:.8}
.kv-directory .hero.kv-image-hero>*{position:relative;z-index:1}
#demoNotice{display:none!important}
@media(max-width:1250px){.kvSeedsGrid{grid-template-columns:repeat(3,minmax(0,1fr))!important}}
@media(max-width:850px){.kvSeedsGrid{grid-template-columns:repeat(2,minmax(0,1fr))!important}.kvSeeds{padding:20px 16px!important}}
@media(max-width:580px){.kvSeedsGrid{grid-template-columns:1fr!important}.kvSeedCard .kv-cover{aspect-ratio:16/8!important}.kvSeedsHead h2{font-size:24px!important}.kv-directory .hero.kv-image-hero{padding:160px 20px 25px}.kv-directory .hero.kv-image-hero:before{width:100%;height:140px;bottom:auto}}
`;
const st=document.createElement('style');st.textContent=styles;document.head.appendChild(st);
document.addEventListener('click',function(e){const target=e.target.closest('.kvSSource');if(!target)return;const a=target.closest('a.kvSeedCard');if(!a)return;e.preventDefault();e.stopPropagation();window.location.href=a.href.split('#')[0]+'#enquiry';},true);
let scheduled=false;
function refresh(){if(scheduled)return;scheduled=true;requestAnimationFrame(()=>{scheduled=false;run()})}
function init(){run();new MutationObserver(refresh).observe(document.body,{subtree:true,childList:true})}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();