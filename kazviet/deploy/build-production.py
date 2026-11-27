#!/usr/bin/env python3
"""Prepare a standalone static KAZVIET.ASIA release from the GitHub Pages preview.

The /kazviet/ preview uses absolute links to /kazviet/... and canonical URLs
pointing to modulnydom.github.io. Production must use the site's own domain
root. This script never edits the preview or any other project.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

PREVIEW_HOST = "https://modulnydom.github.io/kazviet"
PRODUCTION_HOST = "https://kazviet.asia"
TEXT_EXTENSIONS = {".html", ".css", ".js", ".json", ".xml", ".svg", ".txt", ".webmanifest"}
EXCLUDE_DIRS = {"research", "deploy", "vi", ".git", "__pycache__", "node_modules"}
# Emergency 2026-11-19: Vietnamese locale disabled pending local e-commerce compliance review.
EXCLUDE_FILES = {"PHOTO-SOURCES.md", "CNAME", ".htaccess"}
MIN_URLS = 100
# Search-engine ownership files must survive deployment byte-for-byte.
VERIFICATION_FILES = {"googlead3cfb8a1f2aa625.html", "yandex_ae34fa82fbd7f2f3.html", "BingSiteAuth.xml"}


def rewrite_text(content: str) -> str:
    # First replace complete absolute URLs, then root-relative preview paths.
    content = content.replace(PREVIEW_HOST + "/", PRODUCTION_HOST + "/")
    content = content.replace(PREVIEW_HOST, PRODUCTION_HOST)
    content = content.replace("/kazviet/", "/")
    return content


def build(source: Path, output: Path) -> dict:
    if not (source / "index.html").is_file() or not (source / "sitemap.xml").is_file():
        raise RuntimeError("The supplied source is not a KAZVIET site directory.")
    source = source.resolve()
    output = output.resolve()
    if output == source or source in output.parents:
        raise RuntimeError("Refusing to output into the source tree.")
    if output.exists():
        if output.is_symlink():
            raise RuntimeError("Refusing to follow an output symlink.")
        shutil.rmtree(output)
    output.mkdir(parents=True)

    written = 0
    for path in source.rglob("*"):
        relative = path.relative_to(source)
        if any(part in EXCLUDE_DIRS for part in relative.parts):
            continue
        if path.is_symlink():
            raise RuntimeError(f"Unexpected symlink in source: {relative}")
        if not path.is_file() or path.name in EXCLUDE_FILES:
            continue
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if relative.as_posix() in VERIFICATION_FILES:
            shutil.copyfile(path, target)
        elif path.suffix.lower() in TEXT_EXTENSIONS or path.name == "robots.txt":
            data = rewrite_text(path.read_text(encoding="utf-8"))
            target.write_text(data, encoding="utf-8")
        else:
            shutil.copyfile(path, target)
        written += 1

    (output / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\nSitemap: https://kazviet.asia/sitemap.xml\n",
        encoding="utf-8",
    )
    (output / ".nojekyll").touch(exist_ok=True)
    # Site-wide SEO / AEO groundwork for every indexed language page.
    from importlib.machinery import SourceFileLoader
    seo = SourceFileLoader("kazviet_seo", str(Path(__file__).with_name("seo-enhance.py"))).load_module()
    seo.enhance(output)
    return audit(output, written)


def audit(root: Path, written: int = 0) -> dict:
    required = [
        "index.html", "sitemap.xml", "robots.txt", "favicon.svg", "site.webmanifest", "assets/kazviet-mark.svg", "assets/brand.css", "assets/approved-hub.css",
        "assets/approved-hub.js", "ru/index.html", "en/index.html",
        "kk/index.html",
    ]
    required.extend(sorted(VERIFICATION_FILES))
    missing = [x for x in required if not (root / x).is_file()]
    if missing:
        raise RuntimeError("Missing required files: " + ", ".join(missing))

    if (root / "vi").exists():
        raise RuntimeError("Vietnamese locale must not be publicly served before compliance approval.")
    urls = []
    namespace = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    xml = ET.parse(root / "sitemap.xml")
    for entry in xml.findall(f"{namespace}url"):
        location = entry.findtext(f"{namespace}loc", default="")
        if not location.startswith(PRODUCTION_HOST + "/"):
            raise RuntimeError(f"Incorrect sitemap hostname: {location}")
        urls.append(location)
        relative = location.removeprefix(PRODUCTION_HOST + "/")
        destination = root / relative
        # A sitemap directory URL resolves to index.html.
        if location.endswith("/"):
            destination = destination / "index.html"
        if not destination.is_file():
            raise RuntimeError(f"Sitemap target is missing: {location}")

    if len(urls) < MIN_URLS or len(urls) != len(set(urls)):
        raise RuntimeError(f"Unexpected sitemap count/duplicates: {len(urls)}.")

    # A favicon may simplify the full wordmark, but its K paths and colours
    # must always be identical to the mark used throughout the website.
    def k_paths(path: Path) -> list[tuple[str, str]]:
        return re.findall(r'<path\s+fill="(#[A-Fa-f0-9]+)"\s+d="([^"]+)"', path.read_text(encoding="utf-8"))
    if len(k_paths(root / "favicon.svg")) != 3 or k_paths(root / "favicon.svg") != k_paths(root / "assets/kazviet-mark.svg"):
        raise RuntimeError("Favicon and displayed KAZVIET mark have diverged.")

    html_count = 0
    for page in root.rglob("*.html"):
        if page.relative_to(root).as_posix() in VERIFICATION_FILES or "research" in page.parts:
            continue
        contents = page.read_text(encoding="utf-8")
        if PREVIEW_HOST in contents or "/kazviet/" in contents:
            raise RuntimeError(f"Unrewritten preview URL in {page.relative_to(root)}")
        if 'name="description"' not in contents or "<h1" not in contents:
            raise RuntimeError(f"Missing SEO metadata or H1: {page.relative_to(root)}")
        if 'rel="canonical"' not in contents:
            raise RuntimeError(f"Missing canonical: {page.relative_to(root)}")
        if 'rel="icon" type="image/svg+xml" href="/favicon.svg"' not in contents:
            raise RuntimeError(f"Missing favicon on {page.relative_to(root)}")
        if 'href="/assets/brand.css?v=20261119"' not in contents:
            raise RuntimeError(f"Missing shared brand stylesheet on {page.relative_to(root)}")
        if contents.count('class="kvBrandSymbol"') != 2:
            raise RuntimeError(f"Expected branded header and footer on {page.relative_to(root)}")
        if contents.count('src="/assets/kazviet-mark.svg"') != 2:
            raise RuntimeError(f"Logo differs between header and footer on {page.relative_to(root)}")
        if 'hreflang="vi"' in contents:
            raise RuntimeError(f"Disabled Vietnamese language advertised by {page.relative_to(root)}")
        html_count += 1

    return {
        "domain": PRODUCTION_HOST,
        "files_copied": written,
        "pages": html_count,
        "sitemap_urls": len(urls),
        "sitemap_unique": len(set(urls)),
        "root": str(root),
        "status": "valid",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build KAZVIET production static files")
    parser.add_argument("--source", required=True, type=Path, help="Path to kazviet/ preview folder")
    parser.add_argument("--output", required=True, type=Path, help="New isolated production folder")
    parser.add_argument("--audit-only", action="store_true")
    args = parser.parse_args()
    summary = audit(args.output.resolve()) if args.audit_only else build(args.source, args.output)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
