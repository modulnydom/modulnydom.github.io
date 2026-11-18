(function(){'use strict';
const photoSources={
wheat:'https://images.unsplash.com/photo-1692861615331-62bf4dce8987?w=900&h=560&fit=crop&auto=format&q=85',
coffee:'https://images.unsplash.com/photo-1703646619157-eb553d16d402?w=900&h=560&fit=crop&auto=format&q=85',
oil:'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=900&h=560&fit=crop&auto=format&q=85',
sweets:'https://images.unsplash.com/photo-1481391319762-47dff72954d9?w=900&h=560&fit=crop&auto=format&q=85',
flour:'https://images.unsplash.com/photo-1601593768795-7a8c7c00e8f1?w=900&h=560&fit=crop&auto=format&q=85',
furniture:'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=900&h=560&fit=crop&auto=format&q=85',
wood:'https://images.unsplash.com/photo-1523413651479-597eb2da0ad6?w=900&h=560&fit=crop&auto=format&q=85',
textiles:'https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=900&h=560&fit=crop&auto=format&q=85',
packaging:'https://images.unsplash.com/photo-1607082348824-0a96f2a4b9da?w=900&h=560&fit=crop&auto=format&q=85',
industry:'https://images.unsplash.com/photo-1494412519320-aa613dfb7738?w=900&h=560&fit=crop&auto=format&q=85',
electronics:'https://images.unsplash.com/photo-1518770660439-4636190af475?w=900&h=560&fit=crop&auto=format&q=85'
};
const themes={
wheat:['#143e47','#296d5f','#dcb665','🌾'],flour:['#6f4d31','#b58b51','#f5deac','🌾'],
oil:['#3b4c20','#849636','#f5c741','🌻'],sweets:['#482e39','#ac6474','#f2bac4','🍫'],
coffee:['#302d27','#716348','#be9b6f','☕'],furniture:['#234b49','#598b81','#d4a77c','🪑'],
wood:['#354652','#6e8998','#e4b27a','🪵'],textiles:['#363d70','#777eac','#d1b2cf','🧵'],
packaging:['#295a66','#58a2a8','#cce7d8','📦'],industry:['#1c4258','#286f8d','#a1c8d4','⚙️'],
electronics:['#20385e','#3168a0','#9dcde1','🔌']
};
const supplierTypes={
kazcrop:'wheat',sevesilzerno:'flour',maslodel:'oil','organicum-bio':'wheat','altyn-harvest':'wheat',kazkon:'sweets','dynasty-agro':'oil','grain-consortium':'flour',
'simexco-daklak':'coffee','intimex-group':'coffee','fpv-vietnam':'furniture','tt-plywood':'wood','hg-plywood':'wood','dongstar-wood':'wood',tekcom:'wood','anh-phuong':'wood'
};
const categoryTypes={furniture:'furniture',components:'wood',agri:'wheat',textiles:'textiles',packaging:'packaging',industrial:'industry',electronics:'electronics',construction:'wood'};
function svgData(kind,seed){const v=themes[kind]||themes.industry;let circles='';
for(let i=0;i<8;i++){const x=(70+i*113+(seed*17)%80)%950,y=60+((i*59+seed*29)%390),r=24+i%3*15;circles+='<circle cx="'+x+'" cy="'+y+'" r="'+r+'" fill="'+v[2]+'" opacity=".09"/>'}
const label={wheat:'GRAIN & AGRICULTURE',flour:'FLOUR & CEREALS',oil:'EDIBLE OILS',sweets:'CONFECTIONERY',coffee:'COFFEE & AGRICULTURE',furniture:'FURNITURE',wood:'WOOD & PLYWOOD',textiles:'TEXTILES',packaging:'PACKAGING',industry:'INDUSTRIAL',electronics:'ELECTRONICS'}[kind]||'TRADE';
const svg='<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="560" viewBox="0 0 1000 560"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop stop-color="'+v[0]+'"/><stop offset=".66" stop-color="'+v[1]+'"/><stop offset="1" stop-color="'+v[0]+'"/></linearGradient><radialGradient id="gl"><stop stop-color="'+v[2]+'" stop-opacity=".48"/><stop offset="1" stop-color="'+v[2]+'" stop-opacity="0"/></radialGradient></defs><rect width="1000" height="560" fill="url(#g)"/>'+circles+'<circle cx="760" cy="245" r="285" fill="url(#gl)"/><path d="M0 445C265 280 580 560 1000 300V560H0Z" fill="#fff" opacity=".065"/><path d="M0 505C280 345 720 520 1000 390V560H0Z" fill="#fff" opacity=".06"/><rect x="60" y="72" rx="9" width="178" height="42" fill="#fff" opacity=".14"/><text x="82" y="99" fill="#fff" font-family="Arial,sans-serif" font-size="18" letter-spacing="3" font-weight="700">KAZVIET</text><text x="65" y="380" fill="#fff" font-family="Arial,sans-serif" font-size="43" font-weight="700" letter-spacing="4">'+label+'</text><rect x="65" y="410" width="190" height="5" rx="2.5" fill="'+v[2]+'"/><text x="690" y="365" font-size="194">'+v[3]+'</text></svg>';
return 'data:image/svg+xml;charset=utf-8,'+encodeURIComponent(svg);
}
function kindFor(slug,text){if(supplierTypes[slug])return supplierTypes[slug];text=(text||'').toLowerCase();if(/coffee|кофе/.test(text))return 'coffee';if(/кондитер|confection|chocolate/.test(text))return 'sweets';if(/масл|oil|sunflower/.test(text))return 'oil';if(/мебел|furniture/.test(text))return 'furniture';if(/фанер|plywood|wood|gỗ/.test(text))return 'wood';if(/flour|мук|ұн/.test(text))return 'flour';return 'wheat'}
function cover(kind,cls,seed){let image=document.createElement('img');image.className=cls;image.loading='lazy';image.decoding='async';image.alt='Тематическое изображение товара';image.referrerPolicy='no-referrer';image.src=photoSources[kind]||photoSources.industry;const fallback=svgData(kind,seed);image.onerror=function(){if(image.src!==fallback){image.onerror=null;image.src=fallback}};return image;}
const css=`
/* KAZVIET 2026 | editorial product cards */
.kvSeeds{padding:24px 30px!important}.kvSeedsHead{margin-bottom:18px!important}
.kvSeedsHead p{color:#667e90!important;max-width:700px}
.kvSeedsGrid{grid-template-columns:repeat(4,minmax(0,1fr))!important;gap:17px!important}
.kvSeedCard{height:auto!important;min-height:0!important;border:1px solid #e1e9ef!important;border-radius:17px!important;padding:0!important;background:white!important;overflow:hidden;display:flex!important;flex-direction:column!important;gap:0!important;box-shadow:0 6px 24px rgba(24,53,86,.045)!important;transition:transform .2s,box-shadow .2s,border-color .2s!important}
.kvSeedCard:hover{transform:translateY(-4px)!important;box-shadow:0 16px 36px rgba(24,53,86,.13)!important;border-color:#78d1df!important}
.kvSeedCard .kv-cover{display:block!important;object-fit:cover!important;width:100%!important;height:auto!important;aspect-ratio:16/9!important;margin:0!important;background:#e4edf2}
.kvSeedCard .kvSFlag{display:inline-flex!important;align-self:flex-start;margin:15px 16px 0!important;font-size:11px!important;color:#42758a!important;line-height:1.2;font-weight:750}
.kvSeedCard strong{display:block;margin:8px 16px 0!important;font-size:16px!important;letter-spacing:-.4px;color:#152f48!important;line-height:1.35}
.kvSeedCard p{display:-webkit-box!important;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;min-height:39px;margin:8px 16px 12px!important;font-size:12px!important;line-height:1.6!important;color:#667c8b!important;flex:none!important}
.kvSeedCard .kvSSource{display:flex!important;margin:auto 16px 16px!important;padding:11px 13px;border-radius:9px;background:#eaf8fa;color:#087e9b!important;justify-content:space-between;align-items:center;font-size:12px!important;font-weight:800!important}
.kvSeedCard .kvSSource:after{content:'↗';font-size:15px}
.kvSeedFoot{margin-top:20px!important}
.kv-directory .cards{gap:19px!important}
.kv-directory a.card{min-height:0!important;display:flex!important;flex-direction:column!important;padding:0!important;overflow:hidden;border-radius:17px!important;border:1px solid #e0eaf1!important;background:#fff;box-shadow:0 8px 24px rgba(14,53,88,.045)}
.kv-directory a.card .kv-cover{width:100%!important;height:auto!important;aspect-ratio:16/9;object-fit:cover!important;display:block!important;background:#e8eff5}
.kv-directory a.card .tag{align-self:flex-start;margin:14px 16px 0!important}
.kv-directory a.card h2{font-size:17px!important;line-height:1.3;margin:10px 16px 0!important;letter-spacing:-.3px}
.kv-directory a.card p{font-size:13px;line-height:1.6;margin:8px 16px 14px!important;color:#617989;flex:1}
.kv-directory a.card .meta{display:block;margin:auto 16px 16px!important;font-size:12px;color:#087e9b;font-weight:800}
.kv-directory a.card:hover{transform:translateY(-4px);border-color:#8cd6e1!important;box-shadow:0 18px 38px rgba(14,53,88,.13)}
.kv-directory .kvProduct{overflow:hidden;border-radius:14px!important;background:#fff}
.kv-directory .kvProduct img.kv-product-image{display:block;width:100%;height:auto;aspect-ratio:16/9;object-fit:cover}
.kv-directory .kvProduct .kvDot{display:none}
.kv-directory .kvProduct strong,.kv-directory .kvProduct small{margin-left:15px;margin-right:15px}
.kv-directory .kvProduct small{display:block;margin-bottom:15px}
#categoryList .cat{min-height:59px;overflow:hidden}
#categoryList .cat[data-cat]:not([data-cat="all"]){position:relative;padding-left:60px!important}
#categoryList .cat[data-cat]:not([data-cat="all"]) img.kv-cat-image{position:absolute;left:8px;top:50%;transform:translateY(-50%);width:40px;height:40px;object-fit:cover;border-radius:9px}
#categoryList .cat[data-cat]:not([data-cat="all"])>span:first-of-type{display:none}
.kv-directory .hero.kv-visualhero{position:relative;overflow:hidden;background:linear-gradient(110deg,#ecf8ff,#dceff6)!important;padding-right:min(34%,340px)}
.kv-directory .hero.kv-visualhero:before{content:'';position:absolute;inset:0 0 0 auto;width:33%;background:var(--kv-hero-image) center/cover;opacity:.82}
.kv-directory .hero.kv-visualhero>*{position:relative}
#demoNotice{display:none!important}
@media(max-width:1200px){.kvSeedsGrid{grid-template-columns:repeat(3,minmax(0,1fr))!important}}
@media(max-width:800px){.kvSeeds{padding:20px 16px!important}.kvSeedsGrid{grid-template-columns:repeat(2,minmax(0,1fr))!important}.kv-directory .cards{grid-template-columns:repeat(2,minmax(0,1fr))!important}}
@media(max-width:520px){.kvSeedsGrid,.kv-directory .cards{grid-template-columns:1fr!important}.kvSeedCard .kv-cover{aspect-ratio:16/8!important}.kv-directory .hero.kv-visualhero{padding-right:22px;padding-top:160px}.kv-directory .hero.kv-visualhero:before{inset:0 0 auto;width:100%;height:140px}}
`;
const sheet=document.createElement('style');sheet.textContent=css;document.head.appendChild(sheet);
function upgrade(){
 document.querySelectorAll('a.kvSeedCard:not([data-visual-ready])').forEach((a,i)=>{a.dataset.visualReady='1';const parts=(a.getAttribute('href')||'').split('/').filter(Boolean),slug=parts[parts.length-1],k=kindFor(slug,a.textContent);a.prepend(cover(k,'kv-cover',i));const btn=a.querySelector('.kvSSource');if(btn)btn.textContent=/^\/kazviet\/en\//.test(location.pathname)?'Request a quotation': 'Запросить предложение'});
 document.querySelectorAll('a.card:not([data-visual-ready])').forEach((a,i)=>{a.dataset.visualReady='1';const parts=(a.getAttribute('href')||'').split('/').filter(Boolean),slug=parts[parts.length-1],k=kindFor(slug,a.textContent);a.prepend(cover(k,'kv-cover',i));const m=a.querySelector('.meta');if(m)m.textContent=document.documentElement.lang==='en'?'View products and enquire →':document.documentElement.lang==='kk'?'Өнімдер мен сұрау →':'Товары и запрос цены →'});
 const profile=document.querySelector('[data-kv-company]');
 if(profile){const k=kindFor(profile.dataset.slug,profile.dataset.products),hero=document.querySelector('main .hero');if(hero&&!hero.classList.contains('kv-visualhero')){hero.classList.add('kv-visualhero');hero.style.setProperty('--kv-hero-image','url("'+svgData(k,7)+'")')}document.querySelectorAll('.kvProduct:not([data-visual-ready])').forEach((v,i)=>{v.dataset.visualReady='1';v.prepend(cover(k,'kv-product-image',i))})}
 document.querySelectorAll('#categoryList .cat[data-cat]:not([data-cat="all"]):not([data-visual-ready])').forEach((c,i)=>{const k=categoryTypes[c.dataset.cat];if(k){c.dataset.visualReady='1';c.prepend(cover(k,'kv-cat-image',i))}});
}
let active=false;function update(){if(active)return;active=true;requestAnimationFrame(()=>{active=false;upgrade()})}
function start(){upgrade();new MutationObserver(update).observe(document.body,{subtree:true,childList:true})}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start);else start();
})();