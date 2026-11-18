(function(){'use strict';
const IMG={
grain:'https://images.unsplash.com/photo-1501436513145-30f24e19fcc4?w=1000&q=82&auto=format&fit=crop',
coffee:'https://images.unsplash.com/photo-1447933601403-0c6688de566e?w=1000&q=82&auto=format&fit=crop',
wood:'https://images.unsplash.com/photo-1497366754035-f200968a6e72?w=1000&q=82&auto=format&fit=crop',
food:'https://images.unsplash.com/photo-1542838132-92c53300491e?w=1000&q=82&auto=format&fit=crop',
industry:'https://images.unsplash.com/photo-1494412519320-aa613dfb7738?w=1000&q=82&auto=format&fit=crop',
textile:'https://images.unsplash.com/photo-1483985988355-763728e1935b?w=1000&q=82&auto=format&fit=crop',
furniture:'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=1000&q=82&auto=format&fit=crop',
electronic:'https://images.unsplash.com/photo-1518770660439-4636190af475?w=1000&q=82&auto=format&fit=crop',
packaging:'https://images.unsplash.com/photo-1607082348824-0a96f2a4b9da?w=1000&q=82&auto=format&fit=crop'
};
const IMAGE_BY_SLUG={
kazcrop:'grain',sevesilzerno:'grain',maslodel:'food','organicum-bio':'grain','altyn-harvest':'grain',kazkon:'food','dynasty-agro':'grain','grain-consortium':'grain','simexco-daklak':'coffee','intimex-group':'coffee','fpv-vietnam':'furniture','tt-plywood':'wood','hg-plywood':'wood','dongstar-wood':'wood',tekcom:'wood','anh-phuong':'wood'
};
const cats={furniture:'furniture',components:'wood',agri:'grain',textiles:'textile',packaging:'packaging',industrial:'industry',electronics:'electronic',construction:'wood'};
const css=`
/* KAZVIET visual merchandise system */
.kv-directory .hero{position:relative;overflow:hidden;background:linear-gradient(90deg,#eef8ff 0%,#f4faff 49%,rgba(232,246,254,.76) 100%)!important}
.kv-directory .hero.kv-visualhero{padding-right:min(35%,420px)}
.kv-directory .hero.kv-visualhero:after{content:"";position:absolute;right:0;top:0;bottom:0;width:34%;background:linear-gradient(90deg,#f0f9ff,transparent 40%),var(--kv-hero-image) center/cover;opacity:.78;pointer-events:none}
.kv-directory .hero.kv-visualhero>*{position:relative;z-index:1}
.kv-directory .card{overflow:hidden;padding:0!important;transition:transform .2s,box-shadow .2s}
.kv-directory .card>.kv-cover{width:100%;height:125px;object-fit:cover;display:block;background:#ecf4f9}
.kv-directory .card>.tag,.kv-directory .card>h2,.kv-directory .card>p,.kv-directory .card>.meta{margin-left:18px!important;margin-right:18px!important}
.kv-directory .card>.tag{margin-top:14px}.kv-directory .card>.meta{display:block;margin-bottom:17px}
.kv-directory .kvProduct{overflow:hidden;padding:0!important}
.kv-directory .kvProduct>.kv-product-image{display:block;width:100%;height:115px;object-fit:cover}
.kv-directory .kvProduct>.kvDot{display:none}
.kv-directory .kvProduct>strong,.kv-directory .kvProduct>small{margin-left:14px;margin-right:14px}
.kv-directory .kvProduct>small{display:block;margin-bottom:14px}
.kvSeedCard{overflow:hidden;padding-top:0!important}
.kvSeedCard>.kv-cover{width:calc(100% + 28px);height:115px;object-fit:cover;margin:0 -14px 7px;display:block;background:#eff6f9}
#categoryList .cat{min-height:53px;overflow:hidden}
#categoryList .cat[data-cat]:not([data-cat="all"]){position:relative;padding-left:55px!important}
#categoryList .cat[data-cat]:not([data-cat="all"])>.kv-cat-image{position:absolute;left:7px;top:50%;transform:translateY(-50%);width:38px;height:38px;border-radius:9px;object-fit:cover}
#categoryList .cat[data-cat]:not([data-cat="all"])>span:first-of-type{display:none}
@media(max-width:650px){.kv-directory .hero.kv-visualhero{padding-right:23px;padding-top:150px}.kv-directory .hero.kv-visualhero:after{width:100%;height:138px;bottom:auto;background:var(--kv-hero-image) center/cover;opacity:.72}}
`;
const st=document.createElement('style');st.textContent=css;document.head.appendChild(st);
function photo(url,cls,alt){const im=document.createElement('img');im.className=cls;im.src=url;im.alt=alt||'';im.loading='lazy';im.decoding='async';im.onerror=function(){im.remove()};return im}
function type(s){s=(s||'').toLowerCase();if(/coffee|кофе|cà phê/.test(s))return 'coffee';if(/plywood|wood|furniture|фанер|мебел|дерев|ván|gỗ/.test(s))return 'wood';if(/масл|oil|confection|кондитер|fat|bánh/.test(s))return 'food';if(/grain|flour|agro|зерн|мук|пшениц|lentil|rapeseed|астық|ngũ/.test(s))return 'grain';return 'industry'}
function apply(){
 const p=document.querySelector('[data-kv-company]');
 if(p){const k=IMAGE_BY_SLUG[p.dataset.slug]||type(p.dataset.products),img=IMG[k],hero=document.querySelector('main .hero');
 if(hero&&!hero.classList.contains('kv-visualhero')){hero.classList.add('kv-visualhero');hero.style.setProperty('--kv-hero-image','url("'+img+'")')}
 document.querySelectorAll('.kvProduct:not([data-kv-imaged])').forEach((e,i)=>{e.dataset.kvImaged='yes';e.prepend(photo(img,'kv-product-image',''))});
 }
 document.querySelectorAll('a.card:not([data-kv-imaged])').forEach(a=>{const href=a.getAttribute('href')||'',slug=href.split('/').filter(Boolean).pop();let k=IMAGE_BY_SLUG[slug]||type(a.textContent);a.dataset.kvImaged='yes';a.prepend(photo(IMG[k]||IMG.industry,'kv-cover',''))});
 document.querySelectorAll('a.kvSeedCard:not([data-kv-imaged])').forEach(a=>{const href=a.getAttribute('href')||'',slug=href.split('/').filter(Boolean).pop(),k=IMAGE_BY_SLUG[slug]||type(a.textContent);a.dataset.kvImaged='yes';a.prepend(photo(IMG[k]||IMG.industry,'kv-cover',''))});
 document.querySelectorAll('#categoryList .cat[data-cat]:not([data-cat="all"]):not([data-kv-imaged])').forEach(e=>{const k=cats[e.dataset.cat];if(!k)return;e.dataset.kvImaged='yes';e.prepend(photo(IMG[k],'kv-cat-image',''))});
}
let pending=false;function schedule(){if(pending)return;pending=true;requestAnimationFrame(()=>{pending=false;apply()})}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>{apply();new MutationObserver(schedule).observe(document.body,{subtree:true,childList:true})});else{apply();new MutationObserver(schedule).observe(document.body,{subtree:true,childList:true})}
})();