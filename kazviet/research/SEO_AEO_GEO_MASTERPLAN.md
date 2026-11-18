# KAZVIET.ASIA — SEO / AEO / GEO Research Masterplan
**18 Nov 2026** · research-first, do not publish planned URLs as if they exist.

## Evidence
- 220 Google autocomplete seed tests in RU/KZ, EN/US, VI/VN, KK/KZ returned 798 suggestions and 755 unique language/query combinations. **These are not monthly search volumes.**
- [Original RU/KZ long-tail results](google-suggest-ru-kz-2026-11-18.json), [RU/KZ head terms](google-suggest-ru-kz-broad-2026-11-18.json), [English](google-suggest-en-2026-11-18.json), [Vietnamese](google-suggest-vi-2026-11-18.json), [Kazakh](google-suggest-kk-2026-11-18.json).
- [549 automatically filtered, deduplicated candidate phrases](autocomplete-curated-keywords-2026-11-18.csv) include **provisional** topic, priority and route suggestions. Human assessment remains necessary for each phrase.
- Live sitemap: **58 URLs**, comprising homepage + 19 each for Russian, English and Kazakh. No Vietnamese URL. No `xhtml:link` hreflang in sitemap.
- Search Console metrics not accessible through the currently connected GSC Wizard subscription. Google Keyword Planner / Yandex Wordstat actual impressions, monthly volume and CPC are not available in this research.

## Core hierarchy (research roadmap; paths are PLANNED, not all live)

```text
/kazviet/
├── /ru/                            Directory (existing)
│   ├── suppliers/vietnam/          Vietnamese manufacturer catalog (existing)
│   ├── suppliers/kazakhstan/       Kazakhstan exporters (existing)
│   ├── from-vietnam/               Vietnamese wholesale product categories (new)
│   ├── import/vietnam-kazakhstan/  Import buyer intent (new)
│   ├── export/kazakhstan-vietnam/  Exporter intent (new)
│   ├── services/find-vietnam-supplier/ (new)
│   ├── request-quotation/          RFQ — publish when backend works
│   ├── products/
│   │   ├── vietnam-plywood/
│   │   ├── vietnam-coffee/
│   │   ├── vietnam-furniture/
│   │   ├── vietnam-cashew/
│   │   ├── vietnam-black-pepper/
│   │   ├── vietnam-rice/
│   │   ├── kazakhstan-wheat/
│   │   ├── kazakhstan-flour/
│   │   ├── kazakhstan-sunflower-oil/
│   │   ├── kazakhstan-flaxseed/
│   │   ├── kazakhstan-flaxseed-oil/
│   │   ├── kazakhstan-rapeseed/
│   │   └── kazakhstan-lentils/
│   ├── logistics/vietnam-kazakhstan/
│   └── guides/{import-from-vietnam,vietnam-eaeu-fta,certificate-eav,customs-vietnam-kazakhstan,incoterms-vietnam,check-vietnam-supplier,safe-payment-vietnam,export-to-vietnam,...}/
├── /en/                            English buyer-focused pages (some existing)
│   ├── suppliers/vietnam/
│   ├── suppliers/kazakhstan/
│   ├── vietnam-plywood-manufacturers/
│   ├── vietnam-coffee-exporters/
│   ├── kazakhstan-wheat-exporters/
│   ├── vietnam-sourcing/
│   └── [...]
├── /vi/                            Vietnamese export/import hub (MISSING, build)
│   ├── nha-cung-cap-kazakhstan/
│   ├── nha-san-xuat-viet-nam/
│   ├── nhap-khau-lua-mi-kazakhstan/
│   ├── nhap-khau-bot-mi-kazakhstan/
│   ├── xuat-khau-sang-kazakhstan/
│   ├── van-ep-xuat-khau-kazakhstan/
│   ├── ca-phe-xuat-khau-kazakhstan/
│   ├── van-chuyen-viet-nam-kazakhstan/
│   └── hiep-dinh-viet-nam-eaeu/
└── /kk/                            Improve existing Kazakh directory before expanding
```

This roadmap defines **117 URL rows** across RU/EN/VI/KK, **including 48 already-live company profile translations** and the other existing pages. Do not interpret it as 117 new pages.

## Priority and proof
1. P0: structure, working RFQ, actual products and buyer-intent pages: plywood, coffee, furniture, wheat/flour, edible oils, bilingual import/export hubs.
2. P1: Vietnam-language pages, logistics, customs, FTA, origin documentation, cashew/pepper/rice, oilseeds, and deeper guides.
3. P2: apparel, footwear, packaging and other categories **only after** supplier data and product availability are confirmed.
4. Each URL gets one canonical intent, visible semantic text, unique metadata/H1, breadcrumbs, internal product ↔ supplier ↔ logistics ↔ RFQ links, verified citations and matching structured data.

## AI Search / AEO / GEO
Google's own 2026 AI search advice says traditional crawlable SEO and unique factual content remain central. A special AI markup or `llms.txt` is **not required** for its generative answers. Avoid fabricated `Offer`, prices, inventories, reviews, ratings and supplier partnerships. Direct, referenced answers, solid navigation and provenance are preferable to keyword stuffing.

## Deliverables
- User-facing workbook: `KAZVIET_SEO_AEO_GEO_Keyword_Map_2026-11-18.xlsx` — 117 URL mapping entries, clusters, technical backlog and source links.
- `planned_sitemap_not_for_submission.csv` — information architecture planning, **not** a Google XML sitemap.
- Extended research report: `KAZVIET_SEO_AEO_GEO_Research_Report_2026-11-18.md`.
- Original and cleaned autocomplete datasets in this folder (linked above).

## Sources
- https://www.gov.kz/org/moa/press/news/details/1019537?lang=ru
- https://vntr.moit.gov.vn/fta/23/2
- https://www.wto.org/english/tratop_e/tpr_e/g459_e.pdf
- https://developers.google.com/search/docs/fundamentals/ai-optimization-guide
- https://developers.google.com/search/docs/specialty/international/localized-versions
- https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap
- https://valovietnam.com/suppliers
- https://vietnam.so/ru

**Guardrail:** Never put unpublished URLs into the live XML sitemap, and do not claim keyword frequency / exact rank without Google Ads / Wordstat / Search Console data.
