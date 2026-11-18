(function(){
'use strict';
var $=function(s){return document.querySelector(s)};
var $$=function(s){return Array.from(document.querySelectorAll(s))};
var state={category:'all',country:'all',query:'',sort:'default',layout:'grid',supplierCountry:'all'};
var cards=$$('#productGrid .product');
var suppliers=$$('#realSuppliersGrid .kvSeedCard');
function text(el){return(el.textContent||'').toLocaleLowerCase()}
function update(){
  var q=state.query.trim().toLocaleLowerCase();
  cards.forEach(function(el){
    el.hidden=(state.category!=='all'&&el.dataset.category!==state.category)||
    (state.country!=='all'&&el.dataset.country!==state.country)||
    (!!q&&!text(el).includes(q));
  });
  suppliers.forEach(function(el){
    var filter=state.supplierCountry==='all'||el.dataset.country===state.supplierCountry;
    el.hidden=!filter|| (!!q&&!text(el).includes(q));
  });
  $$('#categoryList [data-cat]').forEach(function(el){el.classList.toggle('active',el.dataset.cat===state.category)});
  $$('#realSuppliersPreview [data-seed-country]').forEach(function(el){el.classList.toggle('current',el.dataset.seedCountry===state.supplierCountry)});
  if($('#categoryFilter'))$('#categoryFilter').value=state.category;
  if($('#marketFilter'))$('#marketFilter').value=state.country;
  if($('#catalogEmpty'))$('#catalogEmpty').hidden=cards.some(function(x){return !x.hidden});
  if($('#supplierEmpty'))$('#supplierEmpty').hidden=suppliers.some(function(x){return !x.hidden});
  var sorted=cards.slice();
  if(state.sort==='title')sorted.sort(function(a,b){return a.dataset.sortTitle.localeCompare(b.dataset.sortTitle)});
  if(state.sort==='country')sorted.sort(function(a,b){return a.dataset.country.localeCompare(b.dataset.country)});
  if(state.sort==='default')sorted.sort(function(a,b){return Number(a.dataset.rank)-Number(b.dataset.rank)});
  var grid=$('#productGrid');if(grid)sorted.forEach(function(el){grid.appendChild(el)});
  if(grid)grid.classList.toggle('aslist',state.layout==='list');
  cards.forEach(function(el){el.classList.toggle('list',state.layout==='list')});
}
function toCatalog(){var el=$('#view-catalog');if(el)el.scrollIntoView({behavior:'smooth',block:'start'})}
function toCompanies(){var el=$('#realSuppliersPreview');if(el)el.scrollIntoView({behavior:'smooth',block:'start'})}
$$('[data-cat]').forEach(function(el){el.addEventListener('click',function(){state.category=el.dataset.cat;update();toCatalog()})});
$$('[data-seed-country]').forEach(function(el){el.addEventListener('click',function(){state.supplierCountry=el.dataset.seedCountry;update()})});
$$('[data-market-pick]').forEach(function(el){el.addEventListener('click',function(){state.country=el.dataset.marketPick;state.category='all';update();toCatalog()})});
if($('#marketFilter'))$('#marketFilter').addEventListener('change',function(e){state.country=e.target.value;update()});
if($('#categoryFilter'))$('#categoryFilter').addEventListener('change',function(e){state.category=e.target.value;update()});
if($('#sortSelect'))$('#sortSelect').addEventListener('change',function(e){state.sort=e.target.value;update()});
$$('[data-layout]').forEach(function(el){el.addEventListener('click',function(){state.layout=el.dataset.layout;$$('[data-layout]').forEach(function(x){x.classList.toggle('on',x===el)});update()})});
function doSearch(){state.query=$('#heroSearch')?$('#heroSearch').value:'';update();toCatalog();}
if($('#heroSearchGo'))$('#heroSearchGo').addEventListener('click',doSearch);
if($('#heroSearch'))$('#heroSearch').addEventListener('keydown',function(e){if(e.key==='Enter'){e.preventDefault();doSearch()}});
if($('#heroRequest'))$('#heroRequest').addEventListener('click',function(){toCatalog();if($('#heroSearch'))$('#heroSearch').focus({preventScroll:true})});
['#heroSupplier','#addSupplierCountry'].forEach(function(id){var el=$(id);if(el)el.addEventListener('click',function(){window.location.href='/kazviet/'+document.documentElement.lang+'/request/'})});
if($('#menuToggle'))$('#menuToggle').addEventListener('click',function(){$('#mobileMenu').classList.toggle('hidden')});
$$('#mobileMenu a').forEach(function(el){el.addEventListener('click',function(){if($('#mobileMenu'))$('#mobileMenu').classList.add('hidden')})});
document.addEventListener('click',function(e){
  var source=e.target.closest('.kvSeedCard .kvSSource');
  if(source){
    var card=source.closest('a.kvSeedCard');
    if(card){e.preventDefault();window.location.href=card.href.split('#')[0]+'#enquiry'}
  }
  var fav=e.target.closest('[data-fav]');
  if(fav){e.preventDefault();fav.classList.toggle('on');fav.setAttribute('aria-pressed',String(fav.classList.contains('on')))}
});
update();
})();