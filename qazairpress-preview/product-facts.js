/* QazAirPress: audited product facts from the existing 23 Satu-linked product cards.
   Only catalogued/explicitly indicated figures are reproduced. No unknown specs invented.
   Enhances technical tables and zoom without changing the page's base layout. */
(()=>{'use strict';
const units=[
['abk7-5-8tb','ABK7,5-8TB','7,5','1,2','8'],
['abk15-10tb','ABK15-10TB','15','2,2','10'],
['abk22-8tb','ABK22-8TB','22','3,6','8'],
['abk37-8tb','ABK37-8TB','37','6,0','8'],
['abk55-8tb','ABK55-8TB','55','10,0','8'],
['abk75-8tb','ABK75-8TB','75','13,0','8'],
['abk15-16-laser','ABK15-16','15','1,18','16']
];
const facts={};
for(const [id,model,power,air,bar] of units){
 facts[id]=[
 ['Тип оборудования','Винтовой воздушный компрессор'],
 ['Модель',model],
 ['Мощность двигателя',power+' кВт'],
 ['Производительность',air+' м³/мин ('+Math.round(parseFloat(air.replace(',','.'))*1000).toLocaleString('ru-RU')+' л/мин)'],
 ['Рабочее давление',bar+' атм'],
 ['Режим работы и подключение','Подбираются с инженером по требованиям производства']
 ];
}
facts['abk15-16-laser'].push(['Назначение','Подготовка сжатого воздуха для лазерной резки'],['Состав комплекта по каталогу','Компрессор, ресивер, осушитель и фильтрация']);
for(const [id,size,flow] of [
 ['separator-170-200-230','170/200 × 230 мм','6,5 м³/мин'],
 ['separator-135-170-200','135/170 × 200 мм','4,5 м³/мин'],
 ['separator-220-275-305','220/275 × 305 мм','12 м³/мин'],
 ['separator-300-355-305','300/355 × 305 мм','16 м³/мин']
]){
 facts[id]=[
 ['Тип','Воздушно-масляный сепаратор'],
 ['Типоразмер по обозначению продавца',size],
 ['Заявленная пропускная способность',flow],
 ['Подбор','По посадочным размерам, артикулу и модели компрессора']
 ];
}
facts['separator-lb13145-3']=[['Тип','Воздушно-масляный сепаратор'],['Артикул','LB13145/3'],['Марка по каталогу','Kentek'],['Страна, заявленная в каталоге','Италия'],['Подбор','По артикулу и совместимости с компрессором']];
facts['mol-compressol-r46-al']=[['Вид','Компрессорное масло'],['Наименование','MOL Compressol R 46 AL'],['Тип по каталогу','Минеральное'],['Назначение','Смазка и охлаждение совместимых компрессоров'],['Допуск и объём заправки','Сверить с паспортом компрессора']];
facts['shell-corena-s3-r46']=[['Вид','Компрессорное масло'],['Наименование','Shell Corena S3 R46'],['Класс вязкости по каталогу','ISO VG 46'],['Назначение','Обслуживание совместимых роторных компрессоров'],['Допуск и объём заправки','Сверить с паспортом компрессора']];
for(const [id,volume,pressure] of [['rv-500-10','500 л','10 бар'],['rv-900-10','900 л','10 атм']]){
 facts[id]=[['Тип','Ресивер сжатого воздуха'],['Серия','РВ'],['Объём',volume],['Давление по каталогу',pressure],['Назначение','Запас воздуха и сглаживание колебаний давления'],['Паспорт сосуда, присоединение и габариты','Запросить у поставщика перед заказом']];
}
facts['pressure-sensor-g14']=[['Тип','Датчик давления для компрессора'],['Диапазон измерения','0–16 бар'],['Выходной сигнал','4–20 мА'],['Присоединительная резьба','G1/4'],['Совместимость','Уточнить по контроллеру и модели оборудования']];
facts['temperature-sensor-m12']=[['Тип','Датчик температуры компрессора'],['Посадочная резьба','M12 × 1,5'],['Назначение','Контроль температуры воздушно-масляной смеси'],['Диапазон и тип сигнала','Запросить по артикулу у поставщика']];
facts['air-filter-a569']=[['Тип','Воздушный фильтр компрессора'],['Артикул','A569'],['Марка по каталогу','MFilter'],['Назначение','Очистка всасываемого воздуха от пыли'],['Размеры и совместимость','Сверить с установленным фильтром']];
for(const [id,code] of [['oil-filter-wd13145','WD13145'],['oil-filter-66094172ef','66094172EF'],['oil-filter-66094212ef','66094212EF'],['oil-filter-wd962','WD962']]){
 facts[id]=[['Тип','Масляный фильтр компрессора'],['Маркировка',code],['Марка по каталогу','MANN'],['Назначение','Очистка масла в смазочном контуре'],['Совместимость','Сверить артикул и размер с установленным фильтром']];
}
const slug=(location.pathname.split('/').pop()||'').replace(/\.html$/,'');
const rows=facts[slug];if(!rows)return;
const table=document.querySelector('main table');if(table){
 const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
 table.innerHTML=rows.map(([k,v])=>'<tr><th scope="row">'+esc(k)+'</th><td>'+esc(v)+'</td></tr>').join('');
 table.setAttribute('aria-label','Технические характеристики '+(document.querySelector('h1')?.textContent||''));
}
// Open the primary source image in a no-layout-change, accessible lightbox.
const photo=document.querySelector('main .photo img');
if(photo){
 photo.style.cursor='zoom-in';photo.title='Нажмите для увеличения фотографии';
 photo.setAttribute('tabindex','0');photo.setAttribute('role','button');
 photo.setAttribute('aria-label','Увеличить фото: '+photo.alt);
 const show=()=>{
  const dialog=document.createElement('dialog');
  dialog.setAttribute('aria-label','Фото оборудования крупно');
  dialog.style.cssText='width:min(92vw,980px);max-width:980px;max-height:92vh;padding:15px;border:0;border-radius:16px;background:#f5f8fc;box-shadow:0 30px 100px #0007';
  const img=document.createElement('img');img.src=photo.currentSrc||photo.src;img.alt=photo.alt;img.style.cssText='width:100%;max-height:78vh;object-fit:contain;display:block';
  const close=document.createElement('button');close.textContent='Закрыть ×';close.type='button';close.style.cssText='border:0;background:#0c82f3;color:white;font:700 13px Manrope,Arial,sans-serif;border-radius:9px;padding:10px 17px;cursor:pointer;float:right;margin-bottom:10px';
  close.addEventListener('click',()=>dialog.close());dialog.append(close,img);document.body.append(dialog);
  dialog.addEventListener('close',()=>dialog.remove());
  dialog.addEventListener('click',e=>{if(e.target===dialog)dialog.close();});
  dialog.showModal();close.focus();
 };
 photo.addEventListener('click',show);
 photo.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();show();}});
}
})();