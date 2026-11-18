/**
 * KAZVIET RFQ -> Telegram (Cloudflare Worker).
 * Secrets (set using Cloudflare dashboard/ wrangler secret):
 * TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
 * Optional: ALLOWED_ORIGIN defaults to https://modulnydom.github.io
 * Deploy as separate Worker. Never publish tokens to GitHub Pages.
 */
const reply=(body,status=200,origin='https://modulnydom.github.io')=>new Response(JSON.stringify(body),{status,headers:{'content-type':'application/json; charset=utf-8','access-control-allow-origin':origin,'vary':'Origin','cache-control':'no-store','x-content-type-options':'nosniff'}});
const limit=(v,n)=>typeof v==='string'?v.trim().slice(0,n):'';
export default {async fetch(request,env){
 const allowed=env.ALLOWED_ORIGIN||'https://modulnydom.github.io';
 const origin=request.headers.get('Origin')||'';
 if(request.method==='OPTIONS'){
  if(origin!==allowed)return new Response(null,{status:403});
  return new Response(null,{status:204,headers:{'access-control-allow-origin':allowed,'access-control-allow-methods':'POST, OPTIONS','access-control-allow-headers':'Content-Type','access-control-max-age':'600','vary':'Origin'}});
 }
 if(origin!==allowed)return reply({ok:false,error:'origin'},403,allowed);
 if(request.method!=='POST')return reply({ok:false,error:'method'},405,allowed);
 if(Number(request.headers.get('Content-Length')||0)>12000)return reply({ok:false,error:'too_large'},413,allowed);
 let a;try{a=await request.json();}catch{return reply({ok:false,error:'json'},400,allowed);}
 if(!a||typeof a!=='object'||a.consent!==true)return reply({ok:false,error:'consent'},400,allowed);
 if(limit(a.website,500))return reply({ok:true},200,allowed);
 const p={supplier:limit(a.supplier,160),slug:limit(a.supplier_slug,90),lang:limit(a.lang,5),person:limit(a.person,120),company:limit(a.company,160),email:limit(a.email,200),messenger:limit(a.messenger,200),product:limit(a.product,250),quantity:limit(a.quantity,120),destination:limit(a.destination,160),details:limit(a.details,1500),page:limit(a.source_url,350)};
 if(!p.person||!p.supplier||!p.product||!p.destination||(!p.email&&!p.messenger))return reply({ok:false,error:'required'},400,allowed);
 if(p.email&&!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(p.email))return reply({ok:false,error:'email'},400,allowed);
 if(!env.TELEGRAM_BOT_TOKEN||!env.TELEGRAM_CHAT_ID)return reply({ok:false,error:'configuration'},503,allowed);
 const msg=['📩 KAZVIET · НОВЫЙ B2B-ЗАПРОС','🏭 Поставщик: '+p.supplier,'🧩 Профиль: '+p.slug,'📦 Товар: '+p.product,'📊 Объём: '+(p.quantity||'не указан'),'📍 Доставка: '+p.destination,'📝 Детали: '+(p.details||'—'),'','👤 Покупатель: '+p.person,'🏢 Компания: '+(p.company||'—'),'📧 E-mail: '+(p.email||'—'),'💬 Мессенджер: '+(p.messenger||'—'),'🌐 Язык: '+p.lang,'🔗 Страница: '+p.page].join('\n');
 let upstream;try{upstream=await fetch('https://api.telegram.org/bot'+env.TELEGRAM_BOT_TOKEN+'/sendMessage',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({chat_id:env.TELEGRAM_CHAT_ID,text:msg,disable_web_page_preview:true})});}catch{return reply({ok:false,error:'telegram_network'},502,allowed);}
 let result;try{result=await upstream.json();}catch{return reply({ok:false,error:'telegram_response'},502,allowed);}
 if(!upstream.ok||!result.ok)return reply({ok:false,error:'telegram_rejected'},502,allowed);
 return reply({ok:true},200,allowed);
}};
