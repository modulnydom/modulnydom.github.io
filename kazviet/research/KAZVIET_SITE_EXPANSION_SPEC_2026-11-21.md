# KAZVIET.ASIA — техническое задание на расширение сайта, 21.11.2026

## Статус
Утверждённая модель KAZVIET 2.3 и карта сайта 3.0. Обязательный DESIGN LOCK. Исходный сайт находится в каталоге `kazviet/` репозитория `modulnydom/modulnydom.github.io`. Production: `kazviet.asia`, развёртывание отдельным скриптом `kazviet/deploy/deploy-kazviet.sh` на VPS. Данные сайта не должны затрагивать другие проекты VPS.

## Неприкосновенный дизайн
- Сохранить утверждённые цвета, типографику Manrope, логотип, favicon, сетку, отступы, фон, карточки, кнопки, адаптивную верстку и общий визуальный характер.
- Новые страницы используют существующие `assets/portal.css`, `assets/brand.css`, `assets/approved-hub.css` и действующие компоненты.
- Запрещено глобально заменять CSS, удалять работающие секции, ломать формы, менять структуру карточек или делать редизайн.
- Любые дополнительные элементы должны гармонично продолжать текущий интерфейс. Изменения визуального языка — только после отдельного утверждения.

## Brand voice — обязательный стандарт
- Живой, уверенный, конкретный русский язык, тон действующей международной бизнес-платформы.
- Без «не X, а Y», «не просто X, а Y», канцелярита, извиняющегося тона, неподтверждённых суперлативов.
- Сильные заголовки и реальные действия. У каждой страницы полезная информация, внутренние ссылки и подходящий CTA.
- Запрещены вымышленные партнёры, инвестиции, лицензии, соглашения с администрацией, цены, отзывы, подтверждения и сделки.
- Конкретные факты проверять по источникам и фиксировать дату проверки.

## Действующие URL — сохранять
- Главные `/`, `/ru/`, `/en/`, `/kk/`.
- `/ru/suppliers/kazakhstan/`, `/ru/suppliers/vietnam/`, все существующие карточки компаний.
- `/ru/products/*`, `/ru/import/vietnam-kazakhstan/`, `/ru/export/kazakhstan-vietnam/`.
- `/ru/logistics/vietnam-kazakhstan/`, `/ru/services/find-supplier/`, `/ru/request/`.
- `/ru/guides/vietnam-eaeu-fta/`, `/ru/guides/certificate-eav/`, `/ru/guides/check-supplier/`, `/ru/guides/incoterms/`.
- Не менять canonical без соответствующей миграции и редиректов.

## Новые основные хабы
- `/ru/industry/` — производители и отрасли Вьетнама.
- `/ru/knowledge/` — знания и инструкции по международной торговле.
- `/ru/investment/` — инвестиционные возможности.
- `/ru/property/` — недвижимость.
- `/ru/quy-nhon/` — Куинён, туризм, бизнес и инвестиции.

## Следующие страницы после проверки данных
- Industry: `/ru/industry/manufacturers/`, `wood-furniture/`, `textiles/`, `footwear/`, `electronics/`, `machinery/`, `construction-materials/`, `plastics-packaging/`, `food-agriculture/`, `regions/`, `statistics/`.
- Trade: `/ru/trade/`, `/ru/products/vietnam/`, `/ru/products/kazakhstan/`.
- Services: `/ru/services/supplier-verification/`, `factory-inspection/`, `customs/`, `translation/`, `trade-support/`.
- Logistics: `/ru/logistics/`, `/ru/logistics/kazakhstan-vietnam/`, `containers/`, `lcl-fcl/`, `cost/`.
- Quy Nhon: `/ru/quy-nhon/tourism/`, `investment/`, `business/`, `travel/`, `market/`.
- Property: `/ru/property/buy/`, `rent/`, `quy-nhon/`, `apartments/`, `villas/`, `commercial/`, `hotels/`, `foreign-buyers/`.
- Knowledge: `/ru/knowledge/import-documents/`, `landed-cost/`, `safe-payment/`, `hs-codes/`, `insurance/`.
- Tools: `/ru/tools/`, `import-cost/`, `document-checklist/`, `rfq-template/`.
- Ecosystem: `/ru/talent/`, `academy/`, `expeditions/`, `house/`, `studio/`, `partners/`, `about/`, `contact/`.
- Journal: `/ru/journal/`, `factory-stories/`, `market-reviews/`.

## Industry: обязательная модель данных
`manufacturer_id`, `company_name_original`, `company_name_en`, `province_current`, `industry_id`, `product_categories`, `manufacturer_vs_trader_status`, `evidence_urls`, `evidence_type`, `verified_at`, `verified_by`, `verification_level`, `product_specs`, `capacity_value`, `capacity_unit`, `capacity_year`, `certificates_verified`, `public_status`, `next_review_at`, `correction_log`. Не публиковать неподтверждённые сведения. Данные «актуальны на ноябрь 2026» только после реальной проверки в ноябре. Приоритетные карточки обновлять каждые 3 месяца, остальные каждые 6 месяцев. Контакты производителей публично не размещать; CTA ведёт к запросу KAZVIET.

## Property и Investment
- Публиковать только подтверждённые объекты/проекты. Для карточек: ID, тип, локация, цена/валюта, площадь, фотографии, дата проверки, правовой статус, доступность, ограничения для иностранцев.
- До правового подтверждения не заявлять статус лицензированного брокера и не принимать задатки/оплату за объект.
- Предварительные контакты с администрацией Куинёна не описывать как официальное партнёрство или одобрение проекта.

## SEO / AEO / GEO
- Каждый URL: уникальный title, description, H1, canonical, breadcrumbs, внутренние ссылки, полезная самостоятельная информация.
- Структурированные данные: WebSite/Organization/BreadcrumbList и уместные сущности по фактам страницы; без фиктивных Review, FAQ или Offer.
- Генерировать sitemap только из реальных indexable HTML, `lastmod` — дата фактического изменения.
- Проверить reciprocal hreflang только для реально существующих переводов. `/vi/` не публиковать до юридического разрешения.
- Избегать пустых страниц, массовых шаблонных дублей, фальшивых дат и keyword stuffing.
- Следить за CLS, LCP, INP, мобильной версией, доступностью, работой форм и отсутствием битых ссылок.
- Канонический домен production `https://kazviet.asia/`; GitHub Pages — предпросмотр.

## Воронка и аналитика
- CTA по смыслу: запрос поставщика, подбор недвижимости, обсуждение инвестиционного интереса, Telegram, Instagram. Социальные URL — только после подтверждения реальных адресов.
- События: `page_id`, `content_cluster`, `cta_type`, `cta_position`, `language`, `lead_type`. Не отправлять персональные данные в аналитические события.
- Раздельные метрики по направлениям: органические клики, целевые обращения, конверсия, прибыль, трудоёмкость, повторные запросы. Пересмотр каждые 30 дней, первый горизонт 90 дней.

## Процесс выпуска
1. Снять бэкап и зафиксировать SHA production.
2. Изменять только `kazviet/`, сохранить соседние проекты.
3. Проверить build: `python3 kazviet/deploy/build-production.py --source kazviet --output /tmp/kazviet-check`.
4. Проверить sitemap, все HTML, logo/favicon, `/vi/`, внутренние ссылки, формы, мобильный UI.
5. Развернуть на VPS: `sudo bash /tmp/deploy-kazviet.sh` после скачивания утверждённого скрипта из GitHub.
6. Проверить `https://kazviet.asia/`, `/sitemap.xml`, пять новых хабов, SSL, 200/404, формы и canonical.
7. Если проверка не пройдена — автоматический rollback и разбор ошибок.

## Запрет на неподтверждённое завершение
Коммит в GitHub ≠ публикация на домене. Успех развёртывания подтверждается только после исполнения скрипта на VPS и HTTP-проверки production.
