(()=>{
'use strict';
const PHONE='77761717111';
const WA='https://wa.me/'+PHONE;
const previewRoot='/qazairpress-preview/';
const modal=document.createElement('dialog');modal.className='qa-lead-modal';
modal.innerHTML=`<form class="qa-lead-popup lead-form"><button type="button" aria-label="Закрыть" class="qa-x">×</button><div class="qa-lead-eyebrow">QAZAIRPRESS / ПРЕДПРОСМОТР</div><h2>Подберём оборудование под вашу задачу</h2><p>В демоверсии запрос отправляется через WhatsApp.</p><label>Имя<input name="name" minlength="2" maxlength="90" required placeholder="Ваше имя"></label><label>Телефон<input name="phone" type="tel" minlength="10" maxlength="30" required placeholder="+7 7XX XXX XX XX"></label><label>Компания<input name="company" maxlength="120" placeholder="Необязательно"></label><label>Оборудование и задача<textarea name="task" rows="3" maxlength="950" placeholder="Например: компрессор для цеха, 37 кВт"></textarea></label><label class="qa-consent"><input name="consent" type="checkbox" value="1" required> Согласен(на) передать данные в WhatsApp компании. <a href="${previewRoot}privacy.html">Условия</a></label><button type="submit" class="qa-send">Продолжить в WhatsApp</button><div class="qa-status" role="status" aria-live="polite"></div><small>Или <a href="${WA}" target="_blank" rel="noopener noreferrer">откройте WhatsApp</a> · <a href="tel:+77761717111">+7 776 171 7111</a></small></form>`;
document.body.appendChild(modal);
const trigger=document.createElement('button');trigger.type='button';trigger.className='qa-lead-trigger';trigger.textContent='Запросить КП';trigger.setAttribute('aria-label','Отправить запрос на коммерческое предложение');document.body.appendChild(trigger);
trigger.addEventListener('click',()=>{modal.showModal();modal.querySelector('[name=name]').focus();});
modal.querySelector('.qa-x').addEventListener('click',()=>modal.close());
modal.addEventListener('click',e=>{if(e.target===modal)modal.close();});
document.querySelectorAll('.lead-form').forEach(form=>form.addEventListener('submit',e=>{
 e.preventDefault();
 if(!form.reportValidity())return;
 const data=new FormData(form);const message='Здравствуйте! Интересует оборудование QazAirPress.\\nИмя: '+(data.get('name')||'')+'\\nТелефон: '+(data.get('phone')||'')+'\\nКомпания: '+(data.get('company')||'')+'\\nЗадача: '+(data.get('task')||'')+'\\nИсточник: демо-сайт '+location.pathname;
 const url=WA+'?text='+encodeURIComponent(message);
 const status=form.querySelector('.qa-status');if(status)status.textContent='Открываем WhatsApp — подтвердите отправку сообщения.';
 window.location.href=url;
}));
})();