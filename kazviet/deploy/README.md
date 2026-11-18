# KAZVIET.ASIA — production deployment

## DNS (checked 2026-11-18)

- `kazviet.asia`: `A 82.115.43.192`
- `www.kazviet.asia`: `CNAME kazviet.asia`
- Nameservers: `ns1.ps.kz`, `ns2.ps.kz`, `ns3.ps.kz`
- These settings match the web server and authoritative nameservers used for `qazairpres.kz`. **Do not change the DNS.**

## Install to the existing VPS

Use the existing SSH console for the VPS that runs QazAirPres. Run as an administrator:

```bash
curl -fsSL https://raw.githubusercontent.com/modulnydom/modulnydom.github.io/main/kazviet/deploy/deploy-kazviet.sh -o /tmp/deploy-kazviet.sh
bash -n /tmp/deploy-kazviet.sh && sudo bash /tmp/deploy-kazviet.sh
```

The script deploys only KAZVIET to a new `kazviet-site` Nginx container on the existing `modulnydom_default` Docker network. Production files go to `/home/ubuntu/kazviet-deploy/www`, with a separate `kazviet.asia` virtual host in the existing Caddy container. Caddy requests and renews HTTPS certificates automatically. QazAirPres files are untouched.

A failing build, missing Docker network, missing Caddy bind mount, mismatched existing site container, unrecognized existing KAZVIET Caddy host block or failed Caddy validation causes the script to stop. On updates, the previous KAZVIET files are backed up.

## After deployment

```bash
curl -I https://kazviet.asia/
curl -I https://www.kazviet.asia/
curl -I https://kazviet.asia/ru/
curl -I https://kazviet.asia/vi/
curl -I https://kazviet.asia/sitemap.xml
```

Expected: 200 for the first, RU/VI, sitemap; permanent 301/308 from www to bare domain; working HTTPS certificate. Search engines should use `https://kazviet.asia/` canonical URLs. The source repository's GitHub Pages preview remains available independently at `https://modulnydom.github.io/kazviet/`.

## Build only / no VPS changes

```bash
python3 kazviet/deploy/build-production.py --source kazviet --output /tmp/kazviet-production
```

The builder rewrites `/kazviet/` preview paths to `/` and preview canonicals/sitemap/hreflang to `kazviet.asia`, then audits all 141 URLs.

**Not covered by static deployment:** automatic Telegram lead delivery. The existing enquiry forms use a mailto-based fallback unless a secure POST endpoint is connected. Do not describe Telegram automation as working until its backend has been tested.

Only mark the production custom domain as live after the HTTPS and page checks succeed.
