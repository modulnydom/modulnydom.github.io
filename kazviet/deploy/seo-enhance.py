#!/usr/bin/env python3
"""Enhance every KAZVIET production HTML document, not only the homepage.

Only static, verified HTML URLs are linked as language alternatives. No invented
reviews, prices, certifications, addresses or Google rich-result guarantees.
This runs in the isolated KAZVIET production build, never in QazAirPres.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from xml.etree import ElementTree as ET

BASE = "https://kazviet.asia"
LANGS = ("ru", "en", "vi", "kk")
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
    segments = path.strip("/").split("/") if path != "/" else []
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
            if not isinstance(graph, list):
                return match.group(0)
            nodes = graph
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


def improve_html(html: str, path: str, available: set[str]) -> str:
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

    additions = [
        '<link rel="canonical" href="' + canonical + '">',
        '<meta property="og:url" content="' + canonical + '">',
        '<meta property="og:site_name" content="KAZVIET.ASIA">',
        '<meta property="og:locale" content="' + {"ru": "ru_RU", "en": "en_US", "vi": "vi_VN", "kk": "kk_KZ"}[code] + '">',
        '<meta name="twitter:card" content="summary_large_image">',
        '<meta name="publisher" content="KAZVIET">',
    ]
    for other, target in variants(path, available).items():
        additions.append('<link rel="alternate" hreflang="' + other + '" href="' + target + '">')
    if path == "/" or path in ("/ru/", "/en/", "/vi/", "/kk/"):
        additions.append('<link rel="alternate" hreflang="x-default" href="' + BASE + '/">')
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


def improve_sitemap(root: Path, available: set[str]) -> None:
    source = root / "sitemap.xml"
    xml = ET.parse(source)
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
            if path in ("/", "/ru/", "/en/", "/vi/", "/kk/"):
                ET.SubElement(node, f"{{{XNS}}}link", {"rel": "alternate", "hreflang": "x-default", "href": BASE + "/"})
    xml.write(source, encoding="utf-8", xml_declaration=True)


def enhance(root: Path) -> None:
    pages = sorted(root.rglob("*.html"))
    available = {url_path(p, root) for p in pages}
    if len(available) != len(pages):
        raise RuntimeError("Conflicting HTML routes")
    for page in pages:
        path = url_path(page, root)
        original = page.read_text(encoding="utf-8")
        updated = improve_html(original, path, available)
        if updated.lower().count('<link rel="canonical"') != 1:
            raise RuntimeError("Invalid canonical count: " + path)
        if len(re.findall(r"<h1\b", updated, flags=re.IGNORECASE)) != 1:
            raise RuntimeError("Expected one H1: " + path)
        if f'content="{BASE + path}"' not in updated and f'href="{BASE + path}"' not in updated:
            raise RuntimeError("Self URL absent: " + path)
        page.write_text(updated, encoding="utf-8")
    improve_sitemap(root, available)
    print("[KAZVIET SEO] Enhanced %d HTML pages in RU / EN / VI / KK; canonical, reciprocal hreflang, JSON-LD, social previews and sitemap." % len(pages))
