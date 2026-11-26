#!/usr/bin/env python3
"""Install the supplied Yandex Metrika 114693011 snippet in the deployed TRENT.KZ HTML.

Runs on the existing TRENT VPS only. Does not touch Caddy, Docker, DNS,
the demo, other sites, robots.txt, sitemap.xml, or the live SEO URLs.
Dry-run is the default; --apply writes after backing up originals.
"""
import argparse
import os
import re
import shutil
import stat
import tempfile
from datetime import datetime, timezone
from pathlib import Path

COUNTER = "114693011"
SCRIPT = """<!-- Yandex.Metrika counter -->
<script type="text/javascript">
    (function(m,e,t,r,i,k,a){
        m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};
        m[i].l=1*new Date();
        for (var j = 0; j < document.scripts.length; j++) {if (document.scripts[j].src === r) { return; }}
        k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)
    })(window, document,'script','https://mc.yandex.ru/metrika/tag.js?id=114693011', 'ym');

    ym(114693011, 'init', {ssr:true, webvisor:true, clickmap:true, ecommerce:"dataLayer", referrer: document.referrer, url: location.href, accurateTrackBounce:true, trackLinks:true});
</script>
"""
NOSCRIPT = """<noscript><div><img src="https://mc.yandex.ru/watch/114693011" style="position:absolute; left:-9999px;" alt="" /></div></noscript>
<!-- /Yandex.Metrika counter -->
"""
BODY_PATTERN = re.compile(r"<body\b[^>]*>", flags=re.I)

def validate(content, path):
    if content.count("tag.js?id=" + COUNTER) != 1:
        raise RuntimeError(f"Unexpected Metrika script count: {path}")
    if content.count("watch/" + COUNTER) != 1:
        raise RuntimeError(f"Unexpected noscript count: {path}")
    if content.count("ym(" + COUNTER + ", 'init'") != 1:
        raise RuntimeError(f"Unexpected init count: {path}")
    if content.index("tag.js?id=" + COUNTER) > content.index("</head>"):
        raise RuntimeError(f"Script is not in head: {path}")
    if content.index("watch/" + COUNTER) < BODY_PATTERN.search(content).end():
        raise RuntimeError(f"Noscript is not in body: {path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="/home/ubuntu/trent-deploy/www")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    if not root.is_dir() or not (root / "index.html").is_file():
        raise SystemExit(f"TRENT web root is not present: {root}")
    pages = sorted(root.rglob("index.html"))
    if len(pages) != 36:
        raise SystemExit(f"Expected 36 TRENT pages, got {len(pages)}. Aborting without changes.")
    replacements = []
    unchanged = 0
    for page in pages:
        before = page.read_text(encoding="utf-8")
        if "114693011" in before:
            validate(before, page)
            unchanged += 1
            continue
        if before.count("</head>") != 1 or not BODY_PATTERN.search(before):
            raise SystemExit(f"Invalid page structure; no files changed: {page}")
        after = before.replace("</head>", SCRIPT + "</head>", 1)
        after = BODY_PATTERN.sub(lambda m: m.group(0) + "\n" + NOSCRIPT, after, count=1)
        validate(after, page)
        replacements.append((page, after))
    print(f"TRENT pages: {len(pages)}; to update: {len(replacements)}; already installed: {unchanged}")
    if not args.apply:
        print("DRY RUN ONLY. Add --apply to write files.")
        return
    if not replacements:
        print("All pages already contain exactly one counter. Nothing to do.")
        return
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = root.parent / "backups" / ("metrika-" + COUNTER + "-" + stamp + "-" + str(os.getpid()))
    for page, _ in replacements:
        target = backup / page.relative_to(root)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(page, target)
    print("Original pages backed up at:", backup)
    for page, after in replacements:
        fd, tmp = tempfile.mkstemp(dir=page.parent, prefix=".trent-metrika-", suffix=".html")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(after)
            os.chmod(tmp, stat.S_IMODE(page.stat().st_mode))
            os.replace(tmp, page)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)
    for page in pages:
        validate(page.read_text(encoding="utf-8"), page)
    print(f"SUCCESS: Metrika {COUNTER} installed once on all 36 pages. No service restart required.")

if __name__ == "__main__":
    main()
