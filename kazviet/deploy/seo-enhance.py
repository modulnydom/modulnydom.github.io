#!/usr/bin/env python3
"""Enhance every KAZVIET production HTML document, not only the homepage.

Only static, verified HTML URLs are linked as language alternatives. No invented
reviews, prices, certifications, addresses or Google rich-result guarantees.
This runs in the isolated KAZVIET production build, never in QazAirPres.
"""
from __future__ import annotations

import json
import re
from html import escape
from pathlib import Path
from xml.etree import ElementTree as ET

BASE = "https://kazviet.asia"
LANGS = ("ru", "en", "kk")
# Vietnamese is disabled in production pending Article 27 / 248/2026 compliance.
NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
XNS = "http://www.w3.org/1999/xhtml"

ET.register_namespace("", NS)
ET.register_namespace("xhtml", XNS)

DESCRIPTIONS = {
    "ru": "Каталог производителей, оптовых товаров и коммерческих запросов Казахстана и Вьетнама.",
    "en": "Kazakhstan–Vietnam B2B manufacturer directory, wholesale sourcing and trade enquiries.",
    "vi": "Danh bạ nhà sản xuất, nguồn hàng bán buôn và yêu cầu thương mại Việt Nam – Kazakhstan.",
    "kk": "Қазақстан мен Вьетнам өндірушілері, көтерме тауарлары және сатып алу сұраулары каталогы.",
}


def url_path(page: Path, root: Path) -> str:
    relative = page.relative_to(root)
    return "/" if len(relative.parts) == 1 else "/" + "/".join(relative.parts[:-1]) + "/"


def language(path: str) -> str:
    first = path.strip("/").split("/")[0]
    return first if first in LANGS else "ru"


def variants(path: str, available: set[str]) -> dict[str, str]:
    # The international homepage is now a distinct landing page, not a
    # translation of the locale-specific company directories.
    if path == "/":
        return {}
    segments = path.strip("/").split("/")
    remainder = segments[1:] if segments and segments[0] in LANGS else []
    result = {}
    for code in LANGS:
        target = "/" + code + "/" + ("/".join(remainder) + "/" if remainder else "")
        if target in available:
            result[code] = BASE + target
    return result


def read_title(html: str) -> str:
    match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", match.group(1))).strip() if match else "KAZVIET"


def improve_jsonld(html: str, path: str, code: str) -> str:
    canonical = BASE + path
    org_ref = BASE + "/#organization"
    site_ref = BASE + "/#website"

    def update(match: re.Match) -> str:
        try:
            document = json.loads(match.group(2))
        except (ValueError, TypeError):
            return match.group(0)
        if isinstance(document, dict):
            graph = document.get("@graph")
            if isinstance(graph, list):
                nodes = graph
            else:
                # A standalone WebPage node is also valid JSON-LD. Preserve it
                # while adding the common Organization and WebSite entities.
                document = [document]
                nodes = document
        elif isinstance(document, list):
            nodes = document
        else:
            return match.group(0)
        if not all(isinstance(x, dict) for x in nodes):
            return match.group(0)
        for node in nodes:
            kind = node.get("@type")
            types = kind if isinstance(kind, list) else [kind]
            if "WebPage" in types or "CollectionPage" in types or "AboutPage" in types:
                node["@id"] = canonical + "#webpage"
                node["publisher"] = {"@id": org_ref}
                node["isPartOf"] = {"@id": site_ref}
            if "WebSite" in types and node.get("url") == BASE + "/":
                node["@id"] = site_ref
                node["inLanguage"] = list(LANGS)
                node["publisher"] = {"@id": org_ref}
        if not any("Organization" in (x.get("@type") if isinstance(x.get("@type"), list) else [x.get("@type")]) and x.get("@id") == org_ref for x in nodes):
            nodes.append({
                "@context": "https://schema.org",
                "@type": "Organization",
                "@id": org_ref,
                "name": "KAZVIET",
                "url": BASE + "/",
                "description": DESCRIPTIONS[code],
                "areaServed": [
                    {"@type": "Country", "name": "Kazakhstan"},
                    {"@type": "Country", "name": "Vietnam"},
                ],
            })
        if not any("WebSite" in (x.get("@type") if isinstance(x.get("@type"), list) else [x.get("@type")]) and x.get("@id") == site_ref for x in nodes):
            nodes.append({
                "@context": "https://schema.org",
                "@type": "WebSite",
                "@id": site_ref,
                "name": "KAZVIET.ASIA",
                "url": BASE + "/",
                "inLanguage": list(LANGS),
                "publisher": {"@id": org_ref},
            })
        return match.group(1) + json.dumps(document, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c") + match.group(3)

    # All existing pages have a server-rendered JSON-LD script.
    return re.sub(r'(<script\s+type="application/ld\+json"\s*>)(.*?)(</script>)', update, html, count=1, flags=re.DOTALL | re.IGNORECASE)



# A single static brand lockup is used in headers and footers across all three
# language families, including pages generated from different HTML templates.
# The mark's geometry is identical to favicon.svg.
BRAND_INNER = (
    '<span class="kvBrandSymbol" aria-hidden="true">'
    '<img src="/assets/kazviet-mark.svg" width="52" height="42" alt=""></span>'
    '<span class="kvBrandType">'
    '<strong class="kvBrandWord">KAZVIET<span>.ASIA</span></strong>'
    '<small class="kvBrandCaption">TRADE NETWORK</small></span>'
)


def unify_branding(html: str, path: str) -> str:
    header_count = 0

    def replace_header(match: re.Match) -> str:
        nonlocal header_count
        opening, contents = match.group(1), match.group(2)
        if "KAZVIET" not in contents or "<svg" not in contents:
            return match.group(0)
        header_count += 1
        opening = opening.replace('class="', 'class="kvBrand ', 1)
        return opening + BRAND_INNER + '</a>'

    # These two legacy conventions cover the homepage, locale index and
    # product/company/detail page templates. We do not modify unrelated links.
    html = re.sub(
        r'(<a\b[^>]*\bclass="[^"]*\b(?:logo|brand)\b[^"]*"[^>]*>)(.*?)</a>',
        replace_header, html, flags=re.IGNORECASE | re.DOTALL
    )

    # Home and locale directory pages use a div.logo in the footer.
    html, footer_modern = re.subn(
        r'<div class="logo"><span class="brandmark">.*?<div class="brandcaption">TRADE NETWORK</div></span></div>',
        '<div class="logo kvBrand kvBrandFooter">' + BRAND_INNER + '</div>',
        html, flags=re.IGNORECASE | re.DOTALL
    )

    # Product/supplier/service pages use a text-only footer; give these the
    # same full lockup as every other page.
    html, footer_legacy = re.subn(
        r'<(div|span)\b[^>]*\bclass="brand-text"[^>]*>KAZVIET<span>\.ASIA</span></\1>',
        lambda m: '<a class="kvBrand kvBrandFooter" href="/" aria-label="KAZVIET.ASIA — главная">'
            + BRAND_INNER + '</a>',
        html, flags=re.IGNORECASE | re.DOTALL
    )
    if header_count != 1 or footer_modern + footer_legacy != 1:
        raise RuntimeError(
            f"Brand must appear exactly once in header and footer on {path}: "
            f"header={header_count}, footer={footer_modern + footer_legacy}"
        )
    return html


def improve_html(html: str, path: str, available: set[str]) -> str:
    html = unify_branding(html, path)
    # Remove every advertised Vietnamese language entry from the production UI.
    # All /vi/ HTML has been excluded; do not present any dead language switches.
    html = re.sub(r'<a\b(?=[^>]*\bhref="/vi/[^"]*")[^>]*>.*?</a>', '', html, flags=re.IGNORECASE | re.DOTALL)
    code = language(path)
    canonical = BASE + path
    title = read_title(html)
    if path == "/":
        count = 0
        def only_main_h1(match: re.Match) -> str:
            nonlocal count
            count += 1
            if count == 1:
                return match.group(0)
            return "<h2" + match.group(1) + ">" + match.group(2) + "</h2>"
        html = re.sub(r"<h1([^>]*)>(.*?)</h1>", only_main_h1, html, flags=re.DOTALL | re.IGNORECASE)
        html = html.replace(".subHead h1", ".subHead h2")
    head_end = html.lower().find("</head>")
    if head_end == -1:
        raise RuntimeError("HTML head missing on " + path)
    head, body = html[:head_end], html[head_end:]
    head = re.sub(r'<link\b[^>]*\bhreflang="[^"]+"[^>]*>', "", head, flags=re.IGNORECASE)
    head = re.sub(r'<link\b[^>]*\brel="canonical"[^>]*>', "", head, flags=re.IGNORECASE)
    head = re.sub(r'<meta\b[^>]*\bproperty="og:url"[^>]*>', "", head, flags=re.IGNORECASE)
    head = re.sub(r'<meta\b[^>]*\bproperty="og:locale(?::alternate)?"[^>]*>', "", head, flags=re.IGNORECASE)
    head = re.sub(r'<meta\b[^>]*\bname="theme-color"[^>]*>', "", head, flags=re.IGNORECASE)

    additions = [
        '<link rel="icon" type="image/svg+xml" href="/favicon.svg" sizes="any">',
        '<link rel="stylesheet" href="/assets/brand.css?v=20261119">',
        '<link rel="manifest" href="/site.webmanifest">',
        '<meta name="theme-color" content="#0b2540">',
        '<link rel="canonical" href="' + canonical + '">',
        '<meta property="og:url" content="' + canonical + '">',
        '<meta property="og:site_name" content="KAZVIET.ASIA">',
        '<meta property="og:locale" content="' + {"ru": "ru_RU", "en": "en_US", "vi": "vi_VN", "kk": "kk_KZ"}[code] + '">',
        '<meta name="twitter:card" content="summary_large_image">',
        '<meta name="publisher" content="KAZVIET">',
    ]
    for other, target in variants(path, available).items():
        additions.append('<link rel="alternate" hreflang="' + other + '" href="' + target + '">')
    if path in ("/ru/", "/en/", "/kk/"):
        additions.append('<link rel="alternate" hreflang="x-default" href="' + BASE + '/ru/">')
    if path == "/" or path in ("/ru/", "/en/", "/kk/"):
        additions.append('<link rel="preload" as="image" href="/assets/hero-v13.avif" fetchpriority="high">')
    if path == "/" and 'property="og:image"' not in head:
        additions.append('<meta property="og:image" content="' + BASE + '/assets/hero-v13.avif">')
    if path == "/" and "fonts.googleapis.com" in head:
        additions.append('<link rel="preconnect" href="https://fonts.googleapis.com">')
        additions.append('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>')
    if 'property="og:image"' in head or path == "/":
        additions.append('<meta property="og:image:alt" content="' + title.replace("&", "&amp;").replace('"', "&quot;") + '">')
    html = head + "\n" + "\n".join(additions) + "\n" + body
    html = improve_jsonld(html, path, code)
    return html




# Visible sourcing and buyer-specific purchasing fields are more useful than
# meta-keyword stuffing. They are localized and do not imply any price or deal.
LABELS = {
    "ru": ("Что проверить в коммерческом предложении", "Уточните эти параметры до сравнения предложений:", "Составить запрос на закупку", "Источники данных о компании", "Сведения взяты из общедоступного источника. KAZVIET пока не проверял компанию, не подтверждал её согласие на участие в каталоге или интерес к экспорту. Условия сделки уточняйте напрямую.", "Публичный источник", "Дата проверки источника"),
    "en": ("Wholesale quotation checklist", "Before comparing supplier offers, request:", "Prepare a purchasing enquiry", "Company information sources", "Information comes from a public source. KAZVIET has not yet independently verified this company, obtained its consent to participate or confirmed its export interest. Confirm trading terms before any payment.", "Public source", "Source checked"),
    "vi": ("Thông tin cần xác nhận khi yêu cầu báo giá", "Trước khi so sánh báo giá, hãy hỏi rõ:", "Gửi yêu cầu mua hàng", "Nguồn thông tin doanh nghiệp", "Thông tin được tổng hợp từ nguồn công khai. KAZVIET chưa xác minh độc lập, chưa có sự đồng ý tham gia của doanh nghiệp hoặc xác nhận doanh nghiệp có nhu cầu xuất khẩu. Hãy kiểm tra điều kiện giao dịch trước khi thanh toán.", "Nguồn công khai", "Ngày kiểm tra nguồn"),
    "kk": ("Көтерме ұсыныста нені тексеру керек", "Жеткізушілердің ұсыныстарын салыстыру алдында нақтылаңыз:", "Сатып алу сұрауын жіберу", "Компания деректерінің дереккөздері", "Ақпарат ашық дереккөзден алынған. KAZVIET компанияны әлі дербес тексермеді, каталогқа қатысу келісімін немесе экспортқа қызығушылығын растаған жоқ. Төлем алдында сауда шарттарын тексеріңіз.", "Ашық дереккөз", "Дереккөз тексерілген күн"),
}

FAMILIES = {
    "vietnam-plywood": "wood",
    "vietnam-furniture": "furniture",
    "vietnam-coffee": "coffee",
    "kazakhstan-wheat": "grain",
    "kazakhstan-flour": "flour",
    "kazakhstan-edible-oils": "oil",
    "kazakhstan-flaxseed-oil": "oil",
    "kazakhstan-flaxseed": "grain",
    "kazakhstan-rapeseed": "grain",
    "kazakhstan-lentils": "grain",
    "vietnam-rice": "grain",
    "vietnam-black-pepper": "food",
    "vietnam-cashew": "food",
}
SPECS = {
    "wood": {
        "ru": ["Порода древесины, тип фанеры и назначение", "Размеры, толщина, сорт и допуски", "Марка клея, влажность и нужные протоколы испытаний", "Упаковка, объём партии и пункт доставки"],
        "en": ["Wood species, plywood construction and intended use", "Sheet dimensions, thickness, grade and tolerances", "Adhesive type, moisture limits and required test reports", "Packaging, order volume and delivery destination"],
        "vi": ["Loại gỗ, cấu tạo ván ép và mục đích sử dụng", "Kích thước, độ dày, cấp chất lượng và dung sai", "Loại keo, độ ẩm và tài liệu thử nghiệm cần thiết", "Quy cách đóng gói, số lượng và địa điểm giao hàng"],
        "kk": ["Ағаш түрі, фанера санаты және қолданылуы", "Тақта өлшемі, қалыңдығы, сұрпы және рұқсат етілген ауытқулар", "Желім түрі, ылғалдылық және қажетті сынақ құжаттары", "Қаптама, партия көлемі және жеткізу орны"],
    },
    "furniture": {
        "ru": ["Чертежи, размеры и материалы изделия", "Отделка, комплектация и требования к образцу", "Транспортная упаковка и маркировка", "Объём заказа, срок производства и место поставки"],
        "en": ["Drawings, dimensions and construction materials", "Finish, components and sample approval", "Export packaging and labelling", "Order quantity, production lead time and delivery point"],
        "vi": ["Bản vẽ, kích thước và vật liệu", "Bề mặt hoàn thiện, phụ kiện và mẫu duyệt", "Đóng gói vận chuyển và nhãn hàng", "Số lượng, thời gian sản xuất và địa điểm giao hàng"],
        "kk": ["Сызба, өлшем және материалдар", "Әрлеу, жинақ және үлгіге талаптар", "Тасымал қаптамасы мен таңбалау", "Тапсырыс көлемі, өндіріс мерзімі және жеткізу орны"],
    },
    "coffee": {
        "ru": ["Арабика или робуста, зелёный или обжаренный кофе", "Происхождение, обработка, сорт и требуемая влажность", "Образцы, документы и упаковка", "Масса партии, базис Incoterms и страна доставки"],
        "en": ["Arabica or robusta, green or roasted coffee", "Origin, processing method, grade and moisture specification", "Samples, documents and packaging", "Shipment weight, Incoterms and destination"],
        "vi": ["Arabica hoặc robusta, cà phê nhân xanh hay rang", "Nguồn gốc, phương pháp chế biến, phân hạng và độ ẩm", "Mẫu thử, chứng từ và quy cách đóng gói", "Khối lượng, điều kiện Incoterms và nơi đến"],
        "kk": ["Арабика немесе робуста, жасыл не қуырылған кофе", "Шығу тегі, өңдеу әдісі, сұрып және ылғалдылық", "Үлгілер, құжаттар және қаптама", "Партия салмағы, Incoterms шарты және жеткізу орны"],
    },
    "grain": {
        "ru": ["Культура, сорт, урожай и происхождение", "Влажность, чистота, качество и лабораторные показатели", "Фасовка или навал, фитосанитарные документы по необходимости", "Тоннаж, транспорт, базис Incoterms и пункт приёмки"],
        "en": ["Crop, variety, harvest year and origin", "Moisture, purity, grade and laboratory parameters", "Bulk or bagged shipment and applicable phytosanitary documents", "Tonnage, transport, Incoterms and delivery point"],
        "vi": ["Loại nông sản, giống, vụ mùa và xuất xứ", "Độ ẩm, độ sạch, cấp chất lượng và chỉ tiêu kiểm nghiệm", "Hàng rời hay đóng bao và chứng từ kiểm dịch khi áp dụng", "Khối lượng, phương tiện, Incoterms và nơi nhận"],
        "kk": ["Дақыл, сорты, өнім жылы және шығу тегі", "Ылғалдылық, тазалық, сапа және зертхана көрсеткіштері", "Қапталған не үйінді тасымал және қажет фитосанитарлық құжаттар", "Тоннаж, көлік, Incoterms және қабылдау пункті"],
    },
    "flour": {
        "ru": ["Сорт муки и требуемые показатели качества", "Параметры сырья, влажность и протоколы исследований", "Размер мешка, маркировка и срок годности", "Объём заказа, документы и условия доставки"],
        "en": ["Flour grade and quality specification", "Raw material, moisture and laboratory reports", "Bag size, labelling and shelf-life requirements", "Order quantity, documents and delivery terms"],
        "vi": ["Loại bột mì và các chỉ tiêu chất lượng", "Nguyên liệu, độ ẩm và phiếu kiểm nghiệm", "Khối lượng bao, nhãn và thời hạn bảo quản", "Số lượng đặt hàng, chứng từ và điều kiện giao hàng"],
        "kk": ["Ұн сұрпы мен сапа талаптары", "Шикізат, ылғалдылық және зертхана хаттамалары", "Қап салмағы, таңбалау және сақтау мерзімі", "Тапсырыс көлемі, құжаттар және жеткізу шарты"],
    },
    "oil": {
        "ru": ["Тип масла, степень рафинации и назначение", "Показатели качества, происхождение и образец", "Тара, маркировка и документы по партии", "Объём, условия хранения и базис поставки"],
        "en": ["Oil type, refining status and intended use", "Quality specification, origin and sample", "Packaging, labelling and batch documents", "Volume, storage requirements and delivery terms"],
        "vi": ["Loại dầu, mức độ tinh luyện và mục đích sử dụng", "Chỉ tiêu chất lượng, nguồn gốc và mẫu", "Bao bì, nhãn và chứng từ từng lô", "Số lượng, bảo quản và điều kiện giao hàng"],
        "kk": ["Май түрі, тазарту дәрежесі және қолданылуы", "Сапа көрсеткіштері, шығу тегі және үлгі", "Ыдыс, таңбалау және партия құжаттары", "Көлемі, сақтау талабы және жеткізу шарты"],
    },
    "food": {
        "ru": ["Товарная спецификация и критерии качества", "Происхождение, обработка и состав продукта", "Образец, допустимые показатели и документы", "Упаковка, масса партии и пункт доставки"],
        "en": ["Product specification and quality grade", "Origin, processing and composition", "Sample, acceptance criteria and documents", "Packaging, shipment weight and delivery point"],
        "vi": ["Quy cách hàng hóa và cấp chất lượng", "Nguồn gốc, chế biến và thành phần", "Mẫu, tiêu chí nghiệm thu và chứng từ", "Quy cách đóng gói, khối lượng và nơi giao"],
        "kk": ["Өнім сипаттамасы және сапа санаты", "Шығу тегі, өңделуі және құрамы", "Үлгі, қабылдау талаптары және құжаттар", "Қаптама, партия салмағы және жеткізу орны"],
    },
}


def enhance_visible_content(html: str, path: str, suppliers: dict) -> str:
    chunks = path.strip("/").split("/")
    if len(chunks) < 3 or chunks[0] not in LANGS:
        return html
    lang = chunks[0]
    labels = LABELS[lang]
    # The enquiry section's class/id attribute order differs between page templates.
    # Match the whole opening tag so both <section id="enquiry" ...> and
    # <section class="enquiry" id="enquiry"> receive the buyer guidance.
    match = re.search(r'<section\b[^>]*\bid\s*=\s*"enquiry"[^>]*>', html, flags=re.IGNORECASE)
    if match is None:
        return html
    marker = match.group(0)
    if chunks[1] == "products" and len(chunks) == 3:
        slug = chunks[2]
        family = FAMILIES.get(slug)
        if not family:
            return html
        fields = SPECS[family][lang]
        li = "".join("<li>" + escape(x) + "</li>" for x in fields)
        block = ('<section class="kv-b2b-checklist" aria-label="' + escape(labels[0]) + '">'
            '<h2>' + escape(labels[0]) + '</h2><p>' + escape(labels[1]) + '</p>'
            '<ul>' + li + '</ul><p><a href="#enquiry">' + escape(labels[2]) + ' ↗</a></p></section>')
        return html.replace(marker, block + marker, 1)
    if chunks[1] == "suppliers" and len(chunks) == 4:
        country = {"vietnam": "vn", "kazakhstan": "kz"}.get(chunks[2], "")
        company = suppliers.get((country, chunks[3]))
        if not company:
            return html
        source = company.get("source_url", "")
        if not source.startswith("https://"):
            return html
        checked = company.get("source_checked_at", "")
        block = ('<section class="kv-b2b-checklist kv-evidence" aria-label="' + escape(labels[3]) + '">'
            '<h2>' + escape(labels[3]) + '</h2><p>' + escape(labels[4]) + '</p>'
            '<p><a href="' + escape(source, quote=True) + '" target="_blank" rel="noopener noreferrer">'
            + escape(labels[5]) + ': ' + escape(company["name"]) + ' ↗</a>'
            + (' · ' + escape(labels[6]) + ': ' + escape(checked) if checked else '') + '</p></section>')
        return html.replace(marker, block + marker, 1)
    return html


def improve_sitemap(root: Path, available: set[str]) -> None:
    source = root / "sitemap.xml"
    xml = ET.parse(source)
    entries = xml.findall(f"{{{NS}}}url")
    # Purge disabled /vi/ URL entries instead of advertising 404 pages to crawlers.
    for node in list(entries):
        loc = node.findtext(f"{{{NS}}}loc", default="")
        if loc.startswith(BASE + "/vi/"):
            xml.getroot().remove(node)
    entries = xml.findall(f"{{{NS}}}url")
    existing = {node.findtext(f"{{{NS}}}loc") for node in entries}
    if existing != {BASE + p for p in available}:
        raise RuntimeError("Sitemap URLs and HTML pages differ; cannot safely rewrite alternates.")
    for node in entries:
        url = node.findtext(f"{{{NS}}}loc")
        path = url.removeprefix(BASE)
        for old in list(node):
            if old.tag == f"{{{XNS}}}link":
                node.remove(old)
        if path == "/" or path.strip("/").split("/")[0] in LANGS:
            for code, target in variants(path, available).items():
                ET.SubElement(node, f"{{{XNS}}}link", {"rel": "alternate", "hreflang": code, "href": target})
            if path in ("/ru/", "/en/", "/kk/"):
                ET.SubElement(node, f"{{{XNS}}}link", {"rel": "alternate", "hreflang": "x-default", "href": BASE + "/ru/"})
    xml.write(source, encoding="utf-8", xml_declaration=True)


def enhance(root: Path) -> None:
    pages = sorted(root.rglob("*.html"))
    available = {url_path(p, root) for p in pages}
    if len(available) != len(pages):
        raise RuntimeError("Conflicting HTML routes")
    supplier_file = root / "data/suppliers.json"
    suppliers = {}
    if supplier_file.is_file():
        data = json.loads(supplier_file.read_text(encoding="utf-8"))
        suppliers = {(x.get("country"), x.get("slug")): x for x in data.get("suppliers", [])}
    for page in pages:
        path = url_path(page, root)
        original = page.read_text(encoding="utf-8")
        updated = improve_html(enhance_visible_content(original, path, suppliers), path, available)
        if updated.lower().count('<link rel="canonical"') != 1:
            raise RuntimeError("Invalid canonical count: " + path)
        if len(re.findall(r"<h1\b", updated, flags=re.IGNORECASE)) != 1:
            raise RuntimeError("Expected one H1: " + path)
        if f'content="{BASE + path}"' not in updated and f'href="{BASE + path}"' not in updated:
            raise RuntimeError("Self URL absent: " + path)
        page.write_text(updated, encoding="utf-8")
    improve_sitemap(root, available)
    print("[KAZVIET SEO] Enhanced %d HTML pages in RU / EN / KK; branded favicon, canonical, reciprocal hreflang, JSON-LD, sourcing and sitemap." % len(pages))
