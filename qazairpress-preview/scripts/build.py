#!/usr/bin/env python3
"""Build 28 static pages. Preview by default; production only into a separate directory."""
import argparse
import base64
import html
import json
import re
from pathlib import Path
import shutil
import zlib
from urllib.parse import quote, urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]
P = json.loads((ROOT / 'data/products.json').read_text())
BY = {p['slug']: p for p in P}
CONTACT = json.loads((ROOT / 'data/contacts.json').read_text())
SITE = 'https://qazairpres.kz/'
PHONE = '+7 776 171 7111'
WA = 'https://wa.me/77761717111'
CATS = {'compressors':'Винтовые компрессоры','receivers':'Ресиверы','separators':'Сепараторы','filters':'Фильтры','oils':'Масла','electrics':'Датчики'}
REGIONS = [('Абай','Семей'),('Акмолинская','Кокшетау'),('Актюбинская','Актобе'),('Алматинская','Конаев'),('Атырауская','Атырау'),('Восточно-Казахстанская','Усть-Каменогорск'),('Жамбылская','Тараз'),('Жетісу','Талдыкорган'),('Западно-Казахстанская','Уральск'),('Карагандинская','Караганда'),('Костанайская','Костанай'),('Кызылординская','Кызылорда'),('Мангистауская','Актау'),('Павлодарская','Павлодар'),('Северо-Казахстанская','Петропавловск'),('Туркестанская','Туркестан'),('Ұлытау','Жезказган')]
FAQ = [('Как понять, какой компрессор нужен моему цеху?', 'Нужны расход и давление каждого станка, а также понимание, какие из них работают одновременно. Если этих данных нет, пришлите список оборудования или фото шильдиков. Поможем собрать исходные параметры и подобрать модель.'), ('Достаточно ли выбрать компрессор по мощности в кВт?', 'Нет. При одинаковой мощности модели могут давать разный расход при разном давлении. Начните с потребностей станков, а затем сравните производительность компрессора и условия её измерения.'), ('Что нужно учесть для лазерной резки?', 'Попросите у изготовителя станка требования к давлению, расходу, точке росы, частицам и остаточному маслу. По ним подбираются компрессор и подготовка воздуха. Один только осушитель ещё не гарантирует, что воздух подойдёт лазеру.'), ('Как узнать окончательную цену и срок поставки?', 'Напишите модель, количество и город доставки. Уточним наличие, комплектацию, стоимость оборудования и перевозки. Состав заказа, срок, оплату и гарантийные условия согласуем до покупки.'), ('Как заказать фильтр или сепаратор без ошибки?', 'Пришлите модель компрессора, артикул старого элемента и фото маркировки. Для некоторых позиций понадобятся размеры и данные о подключении. Проверим совместимость до заказа.'), ('Почему давление в карточках указано в атм, а в форме — в бар?', 'В карточках сохранены единицы технической таблицы продавца. Бар и стандартная атмосфера немного различаются: 1 атм = 1,01325 бар. Укажите требования станка в его единицах; перед подбором уточним также, избыточное это давление или абсолютное.'), ('Какая гарантия на оборудование?', 'Условия зависят от модели и исполнения. Перед покупкой согласуем гарантийный срок, начало его отсчёта, состав поставки и требования к обслуживанию. Эти условия должны быть зафиксированы в предложении и договоре.')]

def esc(s): return html.escape(str(s), quote=True)
def j(s): return json.dumps(s, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
def wa(text): return WA + '?text=' + quote(text)
def link(url,text,cls=''): return f'<a class="{cls}" href="{esc(url)}">{text}</a>'

def canonical_local_href(match):
    url=html.unescape(match.group(1));parsed=urlsplit(url)
    if not parsed.scheme and not parsed.netloc and parsed.path.endswith('index.html'):
        url=urlunsplit(('', '', parsed.path[:-10] or './', parsed.query, parsed.fragment))
        return f'href="{esc(url)}"'
    return match.group(0)

def product_title(p):
    title=p['name'].replace('Винтовой компрессор ', 'Компрессор ').replace('Компрессор для лазерного станка ', 'Компрессор для лазера ')
    title=title.replace('Сепаратор воздушно-масляный ', 'Сепаратор ').replace('Воздушно-масляный сепаратор ', 'Сепаратор ')
    return title+' — цена'
def cta(model='', label='Запросить КП', cls='btn primary'):
    return f'<a class="{cls}" data-lead="{esc(model)}" href="{wa("Здравствуйте! Интересует " + (model or "промышленное оборудование") + ". Прошу подготовить коммерческое предложение.")}">{label}<span aria-hidden="true">↗</span></a>'

def brand(base):
    return f'<a class="brand" href="{base}index.html" aria-label="QazAirPress — главная"><b>QazAirPress</b></a>'

def header(base, active):
    entries=[('catalog/index.html','Каталог'),('index.html#applications','Применение'),('dostavka/index.html','Доставка'),('index.html#service','Сервис'),('o-kompanii/index.html','Компания')]
    nav=''.join(f'<a href="{base}{u.replace("index.html","") if active=="index.html" and u.startswith("index.html#") else u}"'+(' aria-current="page"' if active==u else '')+f'>{t}</a>' for u,t in entries)
    return f'''<a class="skip" href="#main">Перейти к содержимому</a>
    <div class="topbar"><div class="container"><span>Промышленное оборудование · Казахстан</span><span>Астана <i aria-hidden="true">/</i> Работаем с предприятиями по всей стране</span></div></div>
    <header class="header"><div class="container nav-row">{brand(base)}<nav id="navigation" aria-label="Основная навигация">{nav}</nav><div class="nav-contact"><a href="tel:+77761717111">{PHONE}</a><small>Подбор и коммерческое предложение</small></div><button class="menu-toggle" aria-expanded="false" aria-controls="navigation" aria-label="Открыть меню"><span></span><span></span></button></div></header>'''

def footer(base):
    return f'''<footer id="contacts"><div class="container"><div class="footer-top"><div>{brand(base)}<p>Компрессоры и комплектующие<br>для работы вашего производства.</p></div><div><p class="footer-heading">Оборудование</p>{''.join(link(base+'catalog/index.html?category='+k,v) for k,v in CATS.items())}</div><div><p class="footer-heading">QazAirPress</p>{link(base+'o-kompanii/index.html','О компании')}{link(base+'dostavka/index.html','Доставка по Казахстану')}{link(base+'index.html#service','Сервис и расходники')}{link(base+'index.html#faq','Вопросы и ответы')}</div><div><p class="footer-heading">Обсудим вашу задачу</p><a class="footer-phone" href="tel:+77761717111">{PHONE}</a><a href="{WA}">Написать в WhatsApp ↗</a><address class="footer-address"><a href="{base}#visit">{esc(CONTACT["addressLocality"])},<br>{esc(CONTACT["streetAddress"])}</a></address><p>Пн–Пт · 10:00–18:00</p></div></div><div class="footer-bottom"><span>© 2026 QazAirPress</span>{link(base+'privacy.html','Обработка данных')}<span>Цена, состав заказа и срок поставки согласуются до покупки.</span></div></div></footer>
    <div class="mobile-actions"><a href="tel:+77761717111">Позвонить</a>{cta(label='Подобрать оборудование')}</div>'''

def crumbs(base, parts):
    return '<nav class="breadcrumbs" aria-label="Хлебные крошки">'+link(base+'index.html','Главная')+''.join('<span aria-hidden="true">/</span>'+(link(base+u,esc(t)) if u else f'<span aria-current="page">{esc(t)}</span>') for t,u in parts)+'</nav>'

def map_widget_url():
    # Same public data format as the official 2GIS map constructor.
    encoded=lambda value:base64.b64encode(value.encode('utf-8')).decode('ascii')
    marker={'type':'Feature','geometry':{'type':'Point','coordinates':[CONTACT['longitude'],CONTACT['latitude']]},'properties':{'title':encoded(CONTACT['name']),'description':encoded(CONTACT['addressLocality']+', '+CONTACT['streetAddress']),'color':'#0873c6','zIndex':0}}
    data={'orderedGeometries':[marker],'mapPosition':{'lat':CONTACT['latitude'],'lon':CONTACT['longitude'],'zoom':17},'scrollWheelZoom':False}
    packed=base64.urlsafe_b64encode(zlib.compress(json.dumps(data,ensure_ascii=False,separators=(',',':')).encode('utf-8'))).decode('ascii').rstrip('=')
    return 'https://makemap.2gis.ru/widget?data='+packed

def location_section():
    return f'''<section class="location-section" id="visit" aria-labelledby="location-title"><div class="container location-grid"><div class="location-copy"><span class="eyebrow">Контакты / {esc(CONTACT['addressLocality'])}</span><h2 id="location-title">Адрес и карта<br>проезда</h2><address class="location-address">{esc(CONTACT['addressLocality'])},<br><strong>{esc(CONTACT['streetAddress'])}</strong></address><p>Обсудим подбор, комплектацию и поставку оборудования. Постройте маршрут или позвоните нам.</p><a class="btn primary" href="{esc(CONTACT['routeUrl'])}" target="_blank" rel="noopener noreferrer">Построить маршрут в 2ГИС <span aria-hidden="true">↗</span></a><div class="location-contact-links"><a href="tel:+77761717111">{PHONE}</a><a href="{WA}">Написать в WhatsApp ↗</a></div></div><div class="location-map"><iframe src="{esc(map_widget_url())}" title="Карта 2ГИС: QazAirPress — Астана, переулок Кызылкол, 16" width="800" height="440" loading="lazy" referrerpolicy="strict-origin-when-cross-origin" sandbox="allow-modals allow-forms allow-scripts allow-same-origin allow-popups allow-top-navigation-by-user-activation"></iframe><div class="location-map-caption"><span>Карта 2ГИС</span><a href="{esc(CONTACT['mapUrl'])}" target="_blank" rel="noopener noreferrer">Открыть адрес в 2ГИС ↗</a></div></div></div></section>'''

METRIKA='''<!-- Yandex.Metrika counter -->
<script type="text/javascript">
    (function(m,e,t,r,i,k,a){
        m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};
        m[i].l=1*new Date();
        for (var j = 0; j < document.scripts.length; j++) {if (document.scripts[j].src === r) { return; }}
        k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)
    })(window, document,'script','https://mc.yandex.ru/metrika/tag.js?id=114694318', 'ym');

    ym(114694318, 'init', {ssr:true, webvisor:true, clickmap:true, ecommerce:"dataLayer", referrer: document.referrer, url: location.href, accurateTrackBounce:true, trackLinks:true});
</script>
<noscript><div><img src="https://mc.yandex.ru/watch/114694318" style="position:absolute; left:-9999px;" alt="" /></div></noscript>
<!-- /Yandex.Metrika counter -->'''

def page(rel,title,description,body,parts=None,schema=None,hero=None):
    base='../' if '/' in rel else ''
    canonical=SITE+('' if rel=='index.html' else rel.replace('/index.html','/'))
    org={'@type':'Organization','@id':SITE+'#organization','name':'QazAirPress','url':SITE,'telephone':'+77761717111','areaServed':{'@type':'Country','name':'Казахстан'},'sameAs':['https://qazairpress.satu.kz/about_us','https://2gis.kz/astana/firm/70000001081683917']}
    postal={'@type':'PostalAddress','streetAddress':CONTACT['streetAddress'],'addressLocality':CONTACT['addressLocality'],'addressCountry':CONTACT['addressCountry']}
    org['address']=postal
    org['location']={'@type':'Place','name':CONTACT['name'],'address':postal,'geo':{'@type':'GeoCoordinates','latitude':CONTACT['latitude'],'longitude':CONTACT['longitude']},'hasMap':CONTACT['mapUrl']}
    graph=[org]
    if parts:
        entries=[{'@type':'ListItem','position':1,'name':'Главная','item':SITE}]
        for i,(name,url) in enumerate(parts,2):entries.append({'@type':'ListItem','position':i,'name':name,'item':SITE+url.replace('/index.html','/') if url else canonical})
        graph.append({'@type':'BreadcrumbList','itemListElement':entries})
    graph+=schema or []
    preload=f'<link rel="preload" as="image" href="{base}assets/products/{hero}.webp" imagesrcset="{base}assets/products/{hero}-440.webp 440w, {base}assets/products/{hero}.webp 1000w" imagesizes="(max-width: 700px) calc(100vw - 40px), 45vw">' if hero else ''
    is_home=rel=='index.html'
    home_css='<link rel="preload" href="assets/fonts/manrope-variable.woff2" as="font" type="font/woff2" crossorigin><link rel="stylesheet" href="assets/home.css?v=seo-20261118">' if is_home else ''
    home_script='<script src="assets/home.js" defer></script>' if is_home else ''
    body_attrs=' class="home-page"' if is_home else ''
    if is_home:preload='<link rel="preload" as="image" href="assets/hero/abk15-10tb-768.webp" imagesrcset="assets/hero/abk15-10tb-384.webp 384w, assets/hero/abk15-10tb-768.webp 768w" imagesizes="(max-width: 850px) calc(100vw - 56px), 50vw">'
    image=SITE+'assets/products/'+(hero or 'abk37-8tb')+'.webp'
    og_image='' if rel.startswith('products/') and not hero else f'<meta property="og:image" content="{image}">'
    return f'''<!doctype html>
<html lang="ru-KZ"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} | QazAirPress</title><meta name="description" content="{esc(description)}"><meta name="robots" content="noindex,nofollow,noarchive"><meta name="theme-color" content="#0b2235"><meta name="author" content="QazAirPress"><meta name="publisher" content="QazAirPress"><link rel="canonical" href="{canonical}"><meta property="og:title" content="{esc(title)} | QazAirPress"><meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{canonical}"><meta property="og:type" content="website"><meta property="og:locale" content="ru_KZ">{og_image}<link rel="icon" href="{base}assets/favicon.svg" type="image/svg+xml">{preload}<link rel="stylesheet" href="{base}assets/styles.css?v=seo-20261118"><link rel="stylesheet" href="{base}assets/contact.css">{home_css}<script type="application/ld+json">{j({'@context':'https://schema.org','@graph':graph})}</script><script src="{base}assets/site.js" defer></script>{home_script}</head><body{body_attrs}>{header(base,rel)}<main id="main">{body}{location_section()}</main>{footer(base)}{METRIKA}</body></html>'''

def photo(p,base='',eager=False):
    if p['photoStatus']=='needs-model-photo':
        return f'<div class="photo-gap"><span>{esc(p["name"].replace("Винтовой компрессор ",""))}</span><p>Запросите фото<br>конкретного исполнения.</p></div>'
    slug=p['slug'];sizes='(max-width: 700px) calc(100vw - 40px), 45vw' if eager else '(max-width: 600px) calc(100vw - 40px), (max-width: 1000px) 45vw, 28vw';loading='fetchpriority="high"' if eager else 'loading="lazy"'
    return f'<img src="{base}assets/products/{slug}.webp" srcset="{base}assets/products/{slug}-440.webp 440w, {base}assets/products/{slug}.webp 1000w" sizes="{sizes}" alt="{esc(p.get("photoAlt") or (p["name"] + " — фото из карточки QazAirPress"))}" width="1000" height="1000" {loading} decoding="async">'

def specs_short(p):
    if p['power'] is not None:return [(str(p['power']).removesuffix('.0').replace('.',','),'кВт'),(str(p['flow']).removesuffix('.0').replace('.',','),'м³/мин'),(str(p['pressure']).removesuffix('.0'),'атм')]
    return [(p['specs'][0][1],p['specs'][0][0])]

def card(p,base=''):
    url=base+'products/'+p['slug']+'.html'
    attrs=' '.join(f'data-{k}="{esc(v)}"' for k,v in {'category':p['categoryId'],'name':p['name'].lower(),'price':p['priceValue'],'power':p['power'] or '', 'pressure':p['pressure'] or '', 'flow':p['flow'] or ''}.items())
    chips=''.join(f'<div><b>{esc(v)}</b><span>{esc(u)}</span></div>' for v,u in specs_short(p))
    return f'''<article class="product-card" {attrs}><a class="card-image" href="{url}" aria-label="{esc(p['name'])}">{photo(p,base)}<span class="image-category">{esc(CATS[p['categoryId']])}</span></a><div class="card-body">{'<span class="review-badge">Совместимость на проверке</span>' if p['reviewOnly'] else ''}<h3>{link(url,esc(p['name']))}</h3><div class="card-specs">{chips}</div><div class="card-price"><div><small>Цена по каталогу*</small><b>{esc(p['price'])}</b></div>{link(url,'↗','arrow-link')}</div>{cta(p['name'],'Запросить предложение','btn card-cta')}</div></article>'''

def section_head(num,kicker,title,text='',action=''):
    return f'<div class="section-heading"><div><span class="eyebrow">{num} / {kicker}</span><h2>{title}</h2></div><div class="section-aside">{f"<p>{text}</p>" if text else ""}{action}</div></div>'

def enquiry(base='',model=''):
    return f'''<form class="lead-form"><input type="hidden" name="model" value="{esc(model)}"><div class="form-grid"><label>Ваше имя<input name="name" autocomplete="name" required minlength="2" maxlength="90" placeholder="Как к вам обращаться"></label><label>Телефон<input name="phone" type="tel" autocomplete="tel" inputmode="tel" required maxlength="30" placeholder="+7 ___ ___ __ __"></label><label>Компания<input name="company" autocomplete="organization" maxlength="120" placeholder="Название организации"></label><label>Город поставки<input name="city" autocomplete="address-level2" required maxlength="100" placeholder="Например, Караганда"></label><label>Мощность, кВт<input name="power" type="number" min="0.1" max="10000" step="any" inputmode="decimal" placeholder="Необязательно"></label><label>Давление, бар<input name="pressure" type="number" min="0.1" max="1000" step="any" inputmode="decimal" placeholder="По требованиям станка"></label><label>Расход, м³/мин<input name="flow" type="number" min="0.01" max="10000" step="any" inputmode="decimal" placeholder="Необязательно"></label><label>Требования к воздуху<select name="air"><option>Нужна консультация</option><option>Общепромышленный воздух</option><option>Для лазерной резки</option><option>Нужны осушение и фильтрация</option><option>Есть требования ISO 8573-1</option></select></label><label class="full">Какие станки или работы нужно обеспечить воздухом?<textarea name="task" rows="3" maxlength="1500" placeholder="Например: три станка в цехе, работают в две смены. Нужен подбор с осушителем."></textarea></label></div><label class="consent"><input type="checkbox" name="consent" required><span>Согласен передать указанные данные QazAirPress через WhatsApp. <a href="{base}privacy.html">Обработка данных</a></span></label><button type="submit" class="btn primary">Открыть запрос в WhatsApp <span aria-hidden="true">↗</span></button><p class="form-note">Проверьте готовый текст в WhatsApp и нажмите «Отправить».</p><p class="form-status" role="status" aria-live="polite"></p><a class="wa-fallback" hidden>Открыть подготовленное сообщение ↗</a><noscript><p>Для заполнения формы включите JavaScript или <a href="{wa('Здравствуйте! Нужен подбор оборудования для производства.')}">напишите в WhatsApp</a>.</p></noscript></form>'''

def home():
    lead=BY['abk15-10tb']
    hero_specs=''.join(f'<span><b>{esc(value)}</b> {esc(unit)}</span>' for value,unit in specs_short(lead))
    hero_image='<img class="hero-machine" src="assets/hero/abk15-10tb-768.webp" srcset="assets/hero/abk15-10tb-384.webp 384w, assets/hero/abk15-10tb-768.webp 768w" sizes="(max-width: 850px) calc(100vw - 56px), 50vw" width="768" height="1115" alt="Компрессор QazAirPress ABK15-10TB с маркировкой модели" fetchpriority="high" decoding="async">'
    body=f'''<section class="wow-hero" aria-labelledby="hero-title">
      <div class="hero-technical-line"><span><i></i> ПРОМЫШЛЕННЫЕ ВОЗДУШНЫЕ СИСТЕМЫ</span><span>QAZAIRPRESS <b>/</b> KAZAKHSTAN</span></div>
      <div class="container wow-hero-grid">
        <div class="wow-hero-copy"><span class="eyebrow">Подбор и поставка по Казахстану</span>
          <h1 id="hero-title">Промышленные<br><em>компрессоры</em></h1>
          <p>Винтовые компрессоры 7,5–75 кВт, ресиверы и оборудование для подготовки воздуха. Поможем с подбором и рассчитаем поставку по Казахстану.</p>
          <div class="button-row">{link('#selection','Подобрать компрессор <span aria-hidden="true">↗</span>','btn primary')}{link('catalog/index.html','Смотреть каталог <span aria-hidden="true">↗</span>','hero-catalog-link')}</div>
          <div class="hero-human-note"><span aria-hidden="true">＋</span><p>Если точные параметры неизвестны,<br><strong>пришлите модели станков и опишите режим работы.</strong></p></div>
        </div>
        <figure class="wow-hero-stage"><div class="stage-ring" aria-hidden="true"></div><span class="stage-coordinate" aria-hidden="true">AIR / 10</span>
          {hero_image}
          <figcaption><a href="products/abk15-10tb.html"><span><small>ВИНТОВОЙ КОМПРЕССОР</small><b>ABK15-10TB</b></span><span class="round-arrow" aria-hidden="true">↗</span></a><div class="stage-specs">{hero_specs}</div></figcaption><small class="hero-image-credit">Изображение модели предоставлено QazAirPress</small>
        </figure>
      </div>
      <div class="container hero-bottom-line"><a href="#directions" class="scroll-cue"><span aria-hidden="true">↓</span> Посмотреть оборудование</a><span>Параметры по каталогу · точное исполнение согласуем при подборе</span></div>
    </section>
    <div class="container overview-strip"><div><strong>7,5—75</strong><span>кВт<br>мощность компрессоров</span></div><div><strong>1,18—13</strong><span>м³/мин<br>расход воздуха по каталогу</span></div><div><strong>23</strong><span>позиции<br>оборудование и комплектующие</span></div></div>'''

    body+=f'''<section class="section home-assortment" id="directions"><div class="container">
      {section_head('01','Оборудование','Компрессоры<br><span class="quiet-heading">и комплектующие</span>','В каталоге — компрессоры, ресиверы, фильтры, сепараторы и масла. Подберём оборудование и расходные материалы для вашего предприятия.',link('catalog/index.html','Открыть каталог ↗','text-link'))}
      <div class="assortment-bento" data-reveal>
        <article class="bento-main"><div class="bento-card-top"><span class="mono-label">01 / КОМПРЕССОРЫ</span>{link('catalog/index.html?category=compressors','↗','round-arrow')}</div><h3>Винтовые<br>компрессоры</h3><p>7 моделей мощностью 7,5–75 кВт.<br>Для станков, цехов и производственных линий.</p><img class="bento-lineup" src="assets/company/lineup.webp" srcset="assets/company/lineup-800.webp 800w, assets/company/lineup.webp 1600w" sizes="(max-width: 700px) 85vw, 40vw" width="1600" height="498" loading="lazy" decoding="async" alt="Линейка компрессоров QazAirPress с маркировкой моделей — ИИ-визуализация"><div class="bento-bottom"><a href="catalog/index.html?category=compressors">7,5–75 кВт <span aria-hidden="true">↗</span></a><small>Линейка QazAirPress · ИИ-визуализация</small></div></article>
        <article class="bento-receiver"><div><span class="mono-label">02 / РЕСИВЕРЫ</span><h3>Ресиверы<br>сжатого воздуха</h3><p>Объём 500 и 900 л.<br>Запас воздуха в пневмосети.</p>{link('catalog/index.html?category=receivers','Выбрать ресивер ↗','text-link')}</div><img src="assets/products/rv-500-10-440.webp" width="440" height="440" loading="lazy" decoding="async" alt="Ресивер серии РВ из каталога QazAirPress"></article>
        <article class="bento-components"><div class="bento-card-top"><span class="mono-label">03 / РАСХОДНЫЕ МАТЕРИАЛЫ</span>{link('catalog/index.html?category=filters','↗','round-arrow')}</div><h3>Фильтры, сепараторы<br>и компрессорные масла</h3><div class="components-bottom"><div class="component-links">{link('catalog/index.html?category=filters','Фильтры ↗')}{link('catalog/index.html?category=separators','Сепараторы ↗')}{link('catalog/index.html?category=oils','Масла ↗')}</div><img src="assets/products/oil-filter-wd13145-440.webp" width="440" height="440" loading="lazy" decoding="async" alt="Масляный фильтр WD13145"></div></article>
      </div></div></section>'''

    machine_models=[]
    for slug in ['abk7-5-8tb','abk15-10tb','abk37-8tb']:
        p=BY[slug]
        values=specs_short(p)
        machine_models.append({'slug':slug,'name':p['name'],'model':p['name'].replace('Винтовой компрессор ',''),'price':p['price'],'description':p['description'],'power':values[0][0],'flow':values[1][0],'pressure':values[2][0],'image':'assets/products/'+slug+'.webp','smallImage':'assets/products/'+slug+'-440.webp','url':'products/'+slug+'.html','requestUrl':wa('Здравствуйте! Интересует '+p['name']+'. Прошу уточнить цену, комплектацию и поставку.')})
    selectors=''.join(f'<button type="button" class="machine-option" data-machine-index="{i}" aria-pressed="{str(i==1).lower()}" aria-controls="machinePreview"><span><b>{esc(m["power"])}</b> кВт</span><span>{esc(m["model"])}<small>{esc(m["flow"])} м³/мин · {esc(m["pressure"])} атм</small></span><i aria-hidden="true">↗</i></button>' for i,m in enumerate(machine_models))
    body+=f'''<section class="section home-models" id="catalog-preview"><div class="container">
      {section_head('02','Выбор мощности','Сравнение<br><span class="quiet-heading">моделей компрессоров</span>','Выберите мощность, чтобы посмотреть фото, параметры и цену модели. Для окончательного подбора учтём расход, давление и режим работы оборудования.')}
      <div class="machine-browser" data-reveal><div class="machine-browser-left"><span class="mono-label">ЛИНЕЙКА QAZAIRPRESS / ВИНТОВЫЕ КОМПРЕССОРЫ</span><h3>Выберите модель<br>для сравнения</h3><div class="machine-options" data-machine-options hidden aria-label="Выберите модель для сравнения">{selectors}</div><p>Нужна помощь с выбором?<br>{link('#selection','Поможем с подбором ↗','text-link')}</p><noscript><p>{link('catalog/index.html?category=compressors','Сравните все модели в каталоге ↗','text-link')}</p></noscript></div>
        <article class="machine-preview" id="machinePreview"><div class="machine-preview-top"><span class="mono-label">QAZAIRPRESS / ПРОМЫШЛЕННЫЙ ВОЗДУХ</span><span class="machine-index" data-machine-number>02 / 03</span></div><div class="machine-photo-wrap"><img data-machine-photo src="assets/products/abk15-10tb.webp" srcset="assets/products/abk15-10tb-440.webp 440w, assets/products/abk15-10tb.webp 1000w" sizes="(max-width: 850px) 85vw, 38vw" width="1000" height="1000" alt="Винтовой компрессор ABK15-10TB — фото модели" loading="lazy" decoding="async"></div><div class="machine-preview-info"><span class="mono-label">ВИНТОВОЙ КОМПРЕССОР</span><h3 data-machine-name aria-live="polite">{esc(machine_models[1]["model"])}</h3><div class="machine-parameters"><div><b data-machine-power>{esc(machine_models[1]["power"])}</b><span>кВт / мощность</span></div><div><b data-machine-flow>{esc(machine_models[1]["flow"])}</b><span>м³/мин / расход</span></div><div><b data-machine-pressure>{esc(machine_models[1]["pressure"])}</b><span>атм / давление</span></div></div><div class="machine-preview-bottom"><div><small>Цена по каталогу*</small><strong data-machine-price>{esc(lead['price'])}</strong></div>{cta(lead['name'],'Получить предложение','btn primary machine-request')}</div>{link('products/abk15-10tb.html','Характеристики модели ↗','text-link machine-detail-link')}</div></article>
      </div><p class="smallprint">* Цены и параметры сверены с каталогом QazAirPress на Satu.kz 17.11.2026. Актуальные цена, наличие и комплектация — в предложении.</p><script type="application/json" id="machineData">{j(machine_models)}</script>
    </div></section>'''

    body+=f'''<section class="section home-industries" id="applications"><div class="container">
      {section_head('03','Отраслевые задачи','Компрессоры<br><span>для разных производств</span>','Подбор зависит от требований оборудования к давлению, расходу и чистоте воздуха.')}
      <div class="industry-editorial" data-reveal>
        <article class="sector-feature"><figure><img src="assets/applications/laser-cutting.webp" srcset="assets/applications/laser-cutting-480.webp 480w, assets/applications/laser-cutting.webp 960w" sizes="(max-width: 850px) 90vw, 50vw" width="960" height="720" loading="lazy" decoding="async" alt="ИИ-визуализация системы сжатого воздуха с ресивером и осушителем"><figcaption>Подготовка воздуха · ИИ-визуализация</figcaption></figure><div class="sector-feature-copy"><div><span class="mono-label">01 / ТОЧНОСТЬ И ЧИСТОТА</span><h3>Лазерная резка</h3><p>Подберём компрессор, осушитель и фильтры по требованиям лазерного станка.</p></div>{link('products/abk15-16-laser.html','↗','round-arrow')}</div></article>
        <div class="sector-side"><article><figure><img src="assets/applications/metalworking.webp" srcset="assets/applications/metalworking-480.webp 480w, assets/applications/metalworking.webp 960w" sizes="(max-width: 600px) 90vw, 26vw" width="960" height="720" loading="lazy" decoding="async" alt="ИИ-визуализация ABK15-10TB для металлообработки"><figcaption>ABK15-10TB · ИИ-визуализация</figcaption></figure><div><span class="mono-label">02 / СТАНКИ И ИНСТРУМЕНТ</span><h3>Металлообработка</h3><p>Воздух для пневмоприводов, инструмента и продувки деталей.</p>{link('catalog/index.html?category=compressors','Подобрать для цеха ↗','text-link')}</div></article><article><figure><img src="assets/applications/production-lines.webp" srcset="assets/applications/production-lines-480.webp 480w, assets/applications/production-lines.webp 960w" sizes="(max-width: 600px) 90vw, 26vw" width="960" height="720" loading="lazy" decoding="async" alt="ИИ-визуализация компрессора BK75-8G в техническом помещении"><figcaption>BK75-8G · ИИ-визуализация</figcaption></figure><div><span class="mono-label">03 / ПРОИЗВОДСТВЕННЫЕ ЛИНИИ</span><h3>Бетон и ЖБИ</h3><p>Сжатый воздух для пневмоцилиндров, заслонок и автоматики производственной линии.</p>{link('#selection','Запросить подбор ↗','text-link')}</div></article></div>
      </div><p class="industry-note">ИИ-визуализации предоставлены QazAirPress и показывают варианты размещения оборудования. Состав системы и условия установки подбираются под требования производства.</p>
    </div></section>'''

    icons=[
      '<rect x="10" y="10" width="40" height="40" rx="4"/><path d="M16 40h12m-12-6h12m7-17h9v8h-9zM17 18h9"/>',
      '<rect x="18" y="6" width="24" height="46" rx="11"/><path d="M22 52v4m16-4v4M12 22h6m24 14h6"/><circle cx="30" cy="20" r="4"/>',
      '<path d="M14 16h32v8H14zM18 24v25h24V24M24 24v25m12-25v25M9 16h5m32 0h5"/>',
      '<path d="M8 51V27l14-8v10l13-9v12h16v19H8zM11 27V10h8v12M17 39h5m8 0h5m8 0h5"/>'
    ]
    stages=[('Компрессор','Создаёт поток воздуха с нужным расходом и давлением.'),('Ресивер','Помогает сгладить короткие пики потребления.'),('Подготовка воздуха','Осушение и фильтрация под требования процесса.'),('Станок или линия','Получает воздух с параметрами, необходимыми для работы.')]
    flow=''.join(f'<li><div class="air-step-symbol"><svg viewBox="0 0 60 60" aria-hidden="true">{icons[i]}</svg></div><span class="mono-label">0{i+1}</span><h3>{title}</h3><p>{description}</p></li>' for i,(title,description) in enumerate(stages))
    body+=f'''<section class="section home-engineering" id="systems"><div class="container"><div class="engineering-intro"><div><span class="eyebrow">04 / Система сжатого воздуха</span><h2>Компрессор<br><span class="quiet-heading">и подготовка воздуха</span></h2></div><p>Компрессор подаёт воздух, ресивер создаёт запас, осушитель и фильтры отвечают за подготовку воздуха. Состав системы зависит от требований оборудования.</p></div><figure class="engineering-visual"><img src="assets/company/air-system.webp" srcset="assets/company/air-system-800.webp 800w, assets/company/air-system.webp 1600w" sizes="(max-width: 700px) 92vw, 85vw" width="1600" height="498" loading="lazy" decoding="async" alt="Компрессор, ресивер и осушитель — ИИ-визуализация QazAirPress"><figcaption>Система сжатого воздуха · ИИ-визуализация QazAirPress</figcaption></figure><ol class="air-system-flow" data-reveal>{flow}</ol><div class="engineering-bottom"><p>Показаны функции компонентов. Состав и порядок установки уточняются для конкретного проекта.</p>{link('#selection','Подобрать систему целиком <span aria-hidden="true">↗</span>','btn outline-dark')}</div></div></section>'''

    body+=f'''<section class="section home-partnership" id="about"><div class="container partnership-grid"><div class="partnership-intro"><span class="eyebrow">05 / Как мы работаем</span><h2>Как подбираем<br><span class="quiet-heading">оборудование</span></h2><p>Укажите известные параметры или пришлите список станков. Поможем определить требования к сжатому воздуху.</p>{link('o-kompanii/index.html','О компании ↗','text-link')}</div><div class="partnership-steps"><article><span>01</span><div><h3>Уточняем задачу</h3><p>Выясняем, какие станки используются, сколько воздуха им нужно и какое давление требуется.</p></div></article><article><span>02</span><div><h3>Выбираем комплектацию</h3><p>Подбираем компрессор, ресивер и подготовку воздуха с учётом требований производства.</p></div></article><article><span>03</span><div><h3>Готовим предложение</h3><p>Указываем модель, состав поставки и цену. Согласуем доставку, гарантию и условия обслуживания.</p></div></article></div></div></section>'''

    body+=f'''<section class="home-delivery" id="regions"><div class="container delivery-canvas"><div><span class="eyebrow">06 / Доставка по Казахстану</span><h2>Доставка<br><em>по Казахстану</em></h2><p>Укажите оборудование и адрес. Рассчитаем перевозку, согласуем срок и условия разгрузки.</p>{link('dostavka/index.html','Рассчитать доставку <span aria-hidden="true">↗</span>','btn primary')}</div><div class="delivery-typography"><div class="delivery-big-type" aria-hidden="true">KZ</div><div class="territory-counts"><div><b>17</b><span>областей</span></div><span class="territory-plus" aria-hidden="true">＋</span><div><b>3</b><span>города республиканского значения</span></div></div><div class="route-cities"><span>Астана</span><i aria-hidden="true"></i><span>Алматы</span><i aria-hidden="true"></i><span>Шымкент</span></div><small>Стоимость и срок зависят от маршрута и состава заказа</small></div></div></section>'''

    body+=f'''<section class="section home-service" id="service"><div class="container service-editorial"><div><span class="eyebrow">07 / Сервис и комплектующие</span><h2>Сервис<br>и <span class="quiet-heading">расходные материалы</span></h2><p>Фильтры, сепараторы, масло и датчики для обслуживания компрессора. Если оборудование работает с ошибкой — сообщите модель и опишите, что происходит.</p>{cta(label='Обсудить обслуживание')}<small>Возможность выезда, работы и сроки согласуем для вашего оборудования и города.</small></div><div class="service-materials"><a href="catalog/index.html?category=filters"><span><small>01 / ОБСЛУЖИВАНИЕ</small><b>Фильтры</b></span><img src="assets/products/oil-filter-wd13145-440.webp" width="440" height="440" loading="lazy" decoding="async" alt="Масляный фильтр WD13145 из каталога"><i aria-hidden="true">↗</i></a><a href="catalog/index.html?category=separators"><span><small>02 / ЗАМЕНА ПО РЕГЛАМЕНТУ</small><b>Сепараторы</b></span><img src="assets/products/separator-lb13145-3-440.webp" width="440" height="440" loading="lazy" decoding="async" alt="Сепаратор LB13145/3 из каталога"><i aria-hidden="true">↗</i></a><a href="catalog/index.html?category=oils"><span><small>03 / МАСЛЯНЫЙ КОНТУР</small><b>Масла</b></span><img src="assets/products/mol-compressol-r46-al-440.webp" width="440" height="440" loading="lazy" decoding="async" alt="Масло MOL Compressol R 46 AL из каталога"><i aria-hidden="true">↗</i></a></div></div></section>'''

    body+='<section class="section home-faq" id="faq"><div class="container faq-editorial"><div><span class="eyebrow">08 / Ответы перед покупкой</span><h2>Вопросы<br><span class="quiet-heading">о выборе и покупке</span></h2><p>Как выбрать модель, уточнить цену и согласовать условия поставки.</p><a href="tel:+77761717111" class="faq-phone">'+PHONE+'</a></div><div>'+''.join(f'<details><summary><span class="faq-index">0{i}</span>{question}</summary><p>{answer}</p></details>' for i,(question,answer) in enumerate(FAQ,1))+'</div></div></section>'

    body+=f'''<section class="section home-enquiry" id="selection"><div class="container home-enquiry-panel"><div><span class="eyebrow">09 / Запрос коммерческого предложения</span><h2>Подбор оборудования<br><em>и расчёт стоимости</em></h2><p>Укажите оборудование, режим работы и город поставки. Если технические параметры неизвестны, напишите модели станков.</p><div class="enquiry-contact"><span>Позвоните или оставьте запрос</span><a href="tel:+77761717111">{PHONE}</a></div><div class="enquiry-points"><span>Подбор по нагрузке</span><span>Согласование комплектации</span><span>Расчёт поставки</span></div></div><div class="form-panel"><span class="mono-label">ПАРАМЕТРЫ ОБОРУДОВАНИЯ И КОНТАКТЫ</span><h3>Заявка на подбор</h3>{enquiry()}</div></div></section>'''
    return page('index.html','Винтовые компрессоры в Казахстане','Подбор винтовых компрессоров QazAirPress для предприятий Казахстана. Сравните модели, комплектующие и подготовку воздуха. Запросите цену и доставку.',body,schema=[{'@type':'WebSite','url':SITE,'name':'QazAirPress'},{'@type':'FAQPage','mainEntity':[{'@type':'Question','name':q,'acceptedAnswer':{'@type':'Answer','text':a}} for q,a in FAQ]}],hero='abk15-10tb')


def catalog():
    parts=[('Каталог','')]
    body='<section class="page-intro"><div class="container">'+crumbs('../',parts)+'<span class="eyebrow">Оборудование / QazAirPress</span><h1>Найдите компрессор<br>для вашего производства.</h1><p>Сравните модели по мощности, давлению и расходу. Для обслуживания выберите нужный артикул — поможем проверить, подходит ли он вашему компрессору.</p></div></section>'
    body+='''<section class="section catalog-section"><div class="container"><form class="catalog-filters" id="catalogFilters" role="search"><div class="filter-main"><label class="search-label">Поиск по модели или артикулу<input id="search" name="q" type="search" placeholder="Например, BK37 или WD962"></label><label>Категория<select id="category" name="category"><option value="all">Всё оборудование</option>'''+''.join(f'<option value="{k}">{v}</option>' for k,v in CATS.items())+'''</select></label><label>Сортировка<select id="sort" name="sort"><option value="default">По каталогу</option><option value="asc">Сначала дешевле</option><option value="desc">Сначала дороже</option><option value="power">По мощности компрессора</option></select></label></div><details class="technical-filters"><summary>Параметры компрессора</summary><div class="filter-technical"><label>Мощность<select name="power" id="power"><option value="">Любая</option>'''+''.join(f'<option value="{v}">{str(v).replace(".",",")} кВт</option>' for v in [7.5,15,22,37,55,75])+'''</select></label><label>Давление по каталогу<select name="pressure" id="pressure"><option value="">Любое</option><option value="8">8 атм</option><option value="10">10 атм</option><option value="16">16 атм</option></select></label><label>Минимальный расход, м³/мин<input name="flow" id="flow" type="number" min="0.01" step="any" placeholder="Не задан"></label><button type="reset" class="btn outline-dark">Сбросить фильтры</button></div><p class="smallprint">Выберите мощность, давление или расход, чтобы оставить в списке подходящие компрессоры.</p></details></form><h2 class="catalog-results-title">Оборудование в каталоге</h2><div class="catalog-meta"><p id="resultCount" role="status" aria-live="polite">23 позиции</p><span>Уточните цену и срок поставки</span></div><div class="product-grid catalog-grid" id="catalogGrid">'''+''.join(card(p,'../') for p in sorted(P,key=lambda p:(list(CATS).index(p['categoryId']),p['power'] or 0)))+'''</div><div class="empty-state" id="emptyState" hidden><h2>Не нашли подходящую модель?</h2><p>Попробуйте изменить фильтры или пришлите задачу — поможем разобраться с выбором.</p>'''+cta(label='Запросить подбор')+'''</div><p class="smallprint">* Цены сверены 17.11.2026 с карточками QazAirPress на Satu.kz. Перед покупкой уточним актуальную цену, наличие и состав поставки. Совместимость расходных материалов проверяется по вашему оборудованию.</p><noscript><p>Показан полный каталог. Для поиска и фильтров включите JavaScript.</p></noscript></div></section>'''
    body+='<section class="section compact tinted"><div class="container inline-cta"><div><span class="eyebrow">Нужен инженерный подбор?</span><h2>Не знаете, какие параметры выбрать?</h2></div>'+cta(label='Подобрать оборудование')+'</div></section>'
    return page('catalog/index.html','Каталог компрессоров и комплектующих','Сравните 23 позиции QazAirPress: поиск по модели, фильтры мощности, давления и расхода. Цены по каталогу продавца, запрос КП и поставки.',body,parts,schema=[{'@type':'CollectionPage','name':'Каталог промышленного оборудования','url':SITE+'catalog/'}])

def product(p):
    parts=[('Каталог','catalog/index.html'),(p['name'],'')];base='../'
    rows=''.join(f'<tr><th scope="row">{esc(k)}</th><td>{esc(v)}</td></tr>' for k,v in p['specs'])
    caption=p.get('photoNote') or ('Фото конкретного исполнения можно запросить перед заказом.' if p['photoStatus']=='needs-model-photo' else 'Фото модели из каталога QazAirPress на Satu.kz.')
    body='<section class="product-section"><div class="container">'+crumbs(base,parts)+f'<div class="product-detail-grid"><figure class="detail-photo">{photo(p,base,eager=True)}<figcaption>{caption}</figcaption></figure><div class="detail-copy"><span class="eyebrow">{esc(CATS[p["categoryId"]])} / QazAirPress</span><h1>{esc(p["name"])}</h1><p>{esc(p["description"])}</p><div class="detail-highlights">'+''.join(f'<div><b>{esc(v)}</b><span>{esc(u)}</span></div>' for v,u in specs_short(p))+f'</div><div class="detail-price"><small>Цена по каталогу · 17.11.2026</small><strong>{esc(p["price"])}</strong><span>Уточним актуальную цену, наличие и срок поставки</span></div><div class="button-row">{cta(p["name"],"Узнать цену и срок поставки")}{link("../dostavka/index.html","Доставка в ваш регион ↗","text-link")}</div>'+('<p class="data-note">Совместимость с промышленным компрессором пока не подтверждена. Сначала проверим позицию по вашему оборудованию.</p>' if p['reviewOnly'] else '')+'</div></div></div></section>'
    body+=f'<section class="section tinted"><div class="container product-information"><div><span class="eyebrow">Параметры для выбора</span><h2>Технические характеристики</h2><div class="table-wrap"><table><caption>{esc(p["name"])} — данные каталога</caption><tbody>{rows}</tbody></table></div><p class="data-note">{esc(p["note"])}</p><details class="source-details"><summary>Источник данных и уточнения</summary><p>{esc(p["sourceNote"])}</p><a class="text-link" href="{esc(p["source"])}" rel="noopener" target="_blank">Посмотреть карточку на Satu.kz ↗</a></details></div><div class="product-notes"><article><h2>Где пригодится</h2><p>{esc(p["application"])}</p></article><article><h2>Поможем с точным подбором</h2><p>{esc(p["compatibility"])}</p></article><article><h2>Доставка и гарантия</h2><p>Укажите город — рассчитаем перевозку и согласуем срок. До покупки уточним состав заказа, гарантию и условия обслуживания.</p>{link("../dostavka/index.html","Как получить расчёт доставки ↗","text-link")}</article></div></div></section>'
    related=[x for x in P if x['slug']!=p['slug'] and x['categoryId']==p['categoryId'] and not x['reviewOnly']][:3]
    if related:body+='<section class="section"><div class="container">'+section_head('','Сравните варианты','Посмотрите другие варианты')+'<div class="product-grid related-grid">'+''.join(card(x,base) for x in related)+'</div></div></section>'
    body+=f'<section class="section compact system-section"><div class="container inline-cta"><div><span class="eyebrow">Остались вопросы?</span><h2>Проверим, подходит ли эта модель<br>вашему оборудованию.</h2></div>{cta(p["name"],"Помочь с выбором")}</div></section>'
    schema={'@type':'Product','name':p['name'],'sku':p['slug'],'description':p['description'],'category':CATS[p['categoryId']],'url':SITE+'products/'+p['slug']+'.html','additionalProperty':[{'@type':'PropertyValue','name':k,'value':v} for k,v in p['specs']]}
    if p['photoStatus']!='needs-model-photo':schema['image']=SITE+'assets/products/'+p['slug']+'.webp'
    if not p['reviewOnly']:
        offer={'@type':'Offer','url':schema['url'],'seller':{'@id':SITE+'#organization'},'priceCurrency':'KZT'}
        if p['unit']:offer['priceSpecification']={'@type':'UnitPriceSpecification','price':p['priceValue'],'priceCurrency':'KZT','referenceQuantity':{'@type':'QuantitativeValue','value':1,'unitCode':'LTR'}}
        else:offer['price']=p['priceValue']
        schema['offers']=offer
    return page('products/'+p['slug']+'.html',product_title(p),p['description']+' Запросите цену и доставку по Казахстану.',body,parts,[schema],p['slug'] if p['photoStatus']!='needs-model-photo' else None)

def delivery():
    parts=[('Доставка по Казахстану','')]
    body='<section class="page-intro"><div class="container">'+crumbs('../',parts)+'<span class="eyebrow">Логистика / Казахстан</span><h1>Доставка компрессоров<br>по Казахстану</h1><p>Укажите город, нужное оборудование и количество. Рассчитаем перевозку и согласуем поставку до вашего предприятия — в Астану, Алматы, Шымкент или любой регион страны.</p></div></section>'
    body+='<section class="section"><div class="container">'+section_head('01','Как согласовать поставку','Как получить расчёт доставки')+'<div class="benefits-grid">'+''.join(f'<article><span>0{i}</span><h3>{t}</h3><p>{d}</p></article>' for i,(t,d) in enumerate([('Сообщите задачу','Выберите модель или расскажите о задаче. Уточним количество и необходимые комплектующие.'),('Укажите адрес','Напишите город и адрес. Сообщите, есть ли ограничения для транспорта и техника для разгрузки.'),('Получите расчёт','Получите предложение с составом заказа, стоимостью доставки и согласованными сроками.'),('Подтвердите условия','Перед заказом согласуем оплату, документы и порядок приёмки оборудования.')],1))+'</div></div></section>'
    body+='<section class="section tinted"><div class="container">'+section_head('02','География','Доставляем в города<br>и населённые пункты Казахстана.','Стоимость зависит от маршрута, массы и габаритов заказа. Для доставки за пределы областного центра укажите точный адрес.')+'<div class="republic-cities">'+''.join(f'<div><small>Город республиканского значения</small><h3>{c}</h3></div>' for c in ['Астана','Алматы','Шымкент'])+'</div><div class="region-grid">'+''.join(f'<article><h3>{r}</h3><p>Областной центр: {c}</p></article>' for r,c in REGIONS)+'</div></div></section>'
    body+='<section class="section"><div class="container faq-grid"><div><span class="eyebrow">03 / До отгрузки</span><h2>Ответы о доставке<br>и получении заказа</h2></div><div>'+''.join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q,a in [('Какими способами доставляется оборудование?','Подберём способ перевозки под массу и габариты заказа. Возможность самовывоза, перевозчика и срок согласуем до оплаты — после уточнения оборудования и адреса.'),('Кто организует разгрузку?','Сообщите, есть ли на объекте погрузчик или кран и свободный подъезд. До отправки согласуем, кто отвечает за погрузку, перевозку, страхование и разгрузку.'),('Какие документы запросить?','Уточните комплект сопроводительных документов, паспорт оборудования, условия гарантии и регламент обслуживания. Для ресивера отдельно проверьте паспорт сосуда и требования к безопасной установке.')])+'</div></div></section>'
    body+=f'<section class="section selection-section"><div class="container selection-grid"><div><span class="eyebrow">04 / Расчёт поставки</span><h2>Посчитаем доставку<br>до вашего предприятия.</h2><p>Напишите, что нужно заказать и в какой город доставить. Остальные детали уточним при подготовке предложения.</p></div><div class="form-panel"><h3>Куда доставить оборудование?</h3>{enquiry("../","Поставка оборудования по Казахстану")}</div></div></section>'
    return page('dostavka/index.html','Доставка компрессоров по Казахстану','Поставка компрессоров и комплектующих в Астану, Алматы, Шымкент и 17 областей. Расчёт маршрута, комплектации, стоимости и условий разгрузки.',body,parts)

def about():
    parts=[('О компании','')]
    body='<section class="page-intro"><div class="container">'+crumbs('../',parts)+'<span class="eyebrow">О QazAirPress</span><h1>Помогаем обеспечить<br>производство сжатым воздухом.</h1><p>Подбираем компрессоры и комплектующие для предприятий Казахстана. Начинаем со станков, нагрузки и условий работы — чтобы предложить оборудование под вашу задачу.</p></div></section>'
    body+='<section class="section"><div class="container prose-grid"><div><h2>От выбора компрессора<br>до его обслуживания</h2><p>QazAirPress поставляет компрессорное оборудование: винтовые компрессоры, ресиверы, подготовку воздуха и расходные материалы. Помогаем разобраться, что нужно отдельному участку, цеху или производственной линии.</p><p>Можно обратиться с готовыми параметрами или просто описать оборудование. Уточним требования, предложим состав системы и согласуем условия поставки. Для действующего компрессора подберём расходные материалы и обсудим обслуживание.</p>'+cta(label='Рассказать о своей задаче')+'</div><aside class="fact-panel"><span class="eyebrow">С чем можно обратиться</span><dl><div><dt>Новое оборудование</dt><dd>Компрессор под нужный расход и давление</dd></div><div><dt>Подготовка воздуха</dt><dd>Ресивер, осушение и фильтрация</dd></div><div><dt>Плановое обслуживание</dt><dd>Масла, фильтры, сепараторы и датчики</dd></div><div><dt>Подбор и предложение</dt><dd>'+link('tel:+77761717111',PHONE)+'</dd></div></dl></aside></div></section>'
    body+='<section class="section tinted"><div class="container">'+section_head('01','Как работаем','Обсудим детали<br>до оформления заказа.')+'<div class="benefits-grid">'+''.join(f'<article><span>0{i}</span><h3>{title}</h3><p>{text}</p></article>' for i,(title,text) in enumerate([('Разберёмся с задачей','Какие станки работают, сколько воздуха им нужно и в каком режиме.'),('Подберём комплектацию','Учтём требования к давлению, сухости и чистоте воздуха.'),('Проверим детали заказа','Согласуем исполнение, совместимость и состав поставки.'),('Подготовим предложение','Уточним цену, доставку, срок и гарантийные условия.')],1))+'</div></div></section>'
    body+='<section class="section"><div class="container">'+section_head('02','QazAirPress в интернете','Где ещё можно найти компанию')+'<div class="source-grid"><article><span class="eyebrow">Каталог и информация</span><h3>QazAirPress на Satu.kz</h3><p>Посмотрите ассортимент и информацию о направлениях работы компании. Актуальные условия по конкретному заказу уточняйте напрямую.</p>'+link('https://qazairpress.satu.kz/about_us','Открыть профиль ↗','text-link')+'</article><article><span class="eyebrow">Городской справочник</span><h3>QazAirPress в 2ГИС</h3><p>Профиль компании по продаже компрессорного оборудования в Астане.</p>'+link('https://2gis.kz/astana/firm/70000001081683917','Открыть в 2ГИС ↗','text-link')+'</article></div></div></section>'
    body+='<section class="section compact system-section"><div class="container inline-cta"><div><span class="eyebrow">Начнём с вашей задачи</span><h2>Что нужно обеспечить воздухом?</h2><p>Напишите о производстве, нужном оборудовании и городе поставки.</p></div><div>'+link('tel:+77761717111',PHONE,'selection-phone')+cta(label='Обсудить подбор')+'</div></div></section>'
    return page('o-kompanii/index.html','О компании — поставки компрессоров','Подбор и поставка компрессорного оборудования QazAirPress. Компрессоры, подготовка воздуха, расходные материалы и обслуживание предприятий Казахстана.',body,parts)

def privacy():
    body='<section class="section"><div class="container prose">'+crumbs('',[('Обработка данных','')])+'<h1>Передача данных по заявке</h1><p>Формы сайта подготавливают сообщение в WhatsApp компании QazAirPress по номеру '+PHONE+'. Передаваемые данные: имя, телефон, компания, город и указанные вами технические требования.</p><h2>Как отправляется запрос</h2><p>После проверки заполнения открывается WhatsApp с подготовленным текстом. Вы можете проверить и изменить его. Сообщение отправится, когда вы подтвердите отправку в WhatsApp.</p><h2>Где обрабатываются данные</h2><p>До отправки сообщения поля формы обрабатываются в вашем браузере: заявка не сохраняется в базе обращений сайта. После перехода в WhatsApp действуют его условия и политика конфиденциальности. Получателем сообщения, которое вы отправите, станет QazAirPress.</p><p>Не указывайте в заявке пароли, платёжные реквизиты и другие сведения, не нужные для подбора оборудования. Для вопросов об обработке обращения свяжитесь с компанией по телефону '+link('tel:+77761717111',PHONE)+'.</p>'+link('index.html#selection','Вернуться к подбору ↗','btn primary')+'</div></section>'
    return page('privacy.html','Передача данных заявки через WhatsApp','Какие данные формы QazAirPress передаются через WhatsApp и как пользователь подтверждает отправку сообщения.',body,[('Обработка данных','')])

def build(out, production=False):
    pages={'index.html':home(),'catalog/index.html':catalog(),'dostavka/index.html':delivery(),'o-kompanii/index.html':about(),'privacy.html':privacy()}
    pages.update({'products/'+p['slug']+'.html':product(p) for p in P})
    if out!=ROOT:
        if out.exists() and any(out.iterdir()):raise SystemExit('Export output must be empty; choose a new directory to avoid stale release files.')
        out.mkdir(parents=True,exist_ok=True)
        shutil.copytree(ROOT/'assets',out/'assets',dirs_exist_ok=True)
        (out/'.nojekyll').touch()
        for name in ('BingSiteAuth.xml','googlead3cfb8a1f2aa625.html','yandex_1b5743015a6e68c8.html'):
            src=ROOT/name
            if src.is_file():shutil.copy2(src,out/name)
    indexed=[]
    for rel,content in pages.items():
        allowed=rel!='privacy.html' and rel!='products/air-filter-a569.html'
        if production and allowed:content=content.replace('noindex,nofollow,noarchive','index,follow')
        content=re.sub(r'<br\s*/?>(?=\S)',r'\g<0> ',content,flags=re.IGNORECASE)
        content=re.sub(r'href="([^"]*)"',canonical_local_href,content)
        content=re.sub(r'(assets/(?:products|applications)/[A-Za-z0-9_-]+\.webp)(?=[\s"])',r'\1?v=marked-20261117',content)
        dest=out/rel;dest.parent.mkdir(exist_ok=True,parents=True);dest.write_text(content+'\n')
        if allowed:indexed.append(SITE+('' if rel=='index.html' else rel.replace('/index.html','/')))
    robots='User-agent: *\nAllow: /\nDisallow: /privacy.html\nDisallow: /products/air-filter-a569.html\nSitemap: '+SITE+'sitemap.xml\n' if production else 'User-agent: *\nDisallow: /\n'
    (out/'robots.txt').write_text(robots)
    from xml.sax.saxutils import escape
    urls=indexed if production else []
    (out/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+escape(u)+'</loc></url>' for u in urls)+'</urlset>\n')
    print(f'{len(pages)} pages; {"production export" if production else "noindex preview"}; {len(urls)} sitemap URLs; output: {out}')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--production',action='store_true');parser.add_argument('--output',type=Path);args=parser.parse_args()
    out=args.output.resolve() if args.output else ROOT
    if args.production and (out==ROOT or ROOT in out.parents):parser.error('Production export requires --output outside the preview directory.')
    build(out,args.production)
