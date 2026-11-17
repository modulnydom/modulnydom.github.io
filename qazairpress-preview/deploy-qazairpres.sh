#!/usr/bin/env bash
# QazAirPress: non-destructive production deployment on the existing shared VPS.
# Run on the VPS as root: sudo bash deploy-qazairpres.sh
# Does not touch other websites or overwrite the global Caddyfile apart from
# one new, individually marked virtual-host block.
set -Eeuo pipefail
DOMAIN="qazairpres.kz"
SITE="qazairpres-site"
NETWORK="modulnydom_default"
DEPLOY_DIR="/home/ubuntu/qazairpres-deploy"
WWW="$DEPLOY_DIR/www"
GITHUB="https://github.com/modulnydom/modulnydom.github.io.git"
CADDY_ID=""
CADDYFILE=""
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

if [[ "$EUID" != 0 ]]; then echo "Run with sudo/root." >&2; exit 1; fi
for cmd in git docker python3 rsync; do
  command -v "$cmd" >/dev/null || { echo "Required command missing: $cmd" >&2; exit 1; }
done
docker network inspect "$NETWORK" >/dev/null || {
  echo "Docker network $NETWORK not found; refusing to alter existing hosts." >&2; exit 1;
}

# Discover the shared Caddy using its file/directory mount, without assuming
# a particular container name. Fail closed if configuration is not accessible.
for id in $(docker ps -q); do
  docker exec "$id" caddy version >/dev/null 2>&1 || continue
  file="$(docker inspect -f '{{range .Mounts}}{{if eq .Destination "/etc/caddy/Caddyfile"}}{{.Source}}{{end}}{{end}}' "$id")"
  if [[ -z "$file" ]]; then
    dir="$(docker inspect -f '{{range .Mounts}}{{if eq .Destination "/etc/caddy"}}{{.Source}}{{end}}{{end}}' "$id")"
    [[ -n "$dir" ]] && file="$dir/Caddyfile"
  fi
  [[ -f "$file" ]] || continue
  docker inspect -f '{{json .NetworkSettings.Networks}}' "$id" | grep -q "\"$NETWORK\"" || continue
  CADDY_ID="$id"
  CADDYFILE="$file"
  break
done
[[ -n "$CADDY_ID" ]] || {
  echo "Could not find the shared Caddyfile bind mount on $NETWORK; no changes made." >&2; exit 1;
}

# Fetch only the source website folder; public GitHub preview remains unchanged.
git clone -q --depth=1 --filter=blob:none --sparse "$GITHUB" "$TMP/source"
git -C "$TMP/source" sparse-checkout -q set qazairpress-preview
mkdir -p "$TMP/production"
python3 "$TMP/source/qazairpress-preview/scripts/build.py" \
  --production --output "$TMP/production"

# Publish only to the dedicated QazAirPress directory; other sites unchanged.
mkdir -p "$WWW"
rsync -a --delete "$TMP/production/" "$WWW/"
if docker inspect "$SITE" >/dev/null 2>&1; then
  live_mount="$(docker inspect -f '{{range .Mounts}}{{if eq .Destination "/usr/share/nginx/html"}}{{.Source}}{{end}}{{end}}' "$SITE")"
  [[ "$live_mount" == "$WWW" ]] || {
    echo "Existing container $SITE has a different web root: $live_mount; refusing to replace." >&2; exit 1;
  }
  docker start "$SITE" >/dev/null
else
  docker run -d --name "$SITE" --restart unless-stopped \
    --network "$NETWORK" --mount "type=bind,src=$WWW,dst=/usr/share/nginx/html,readonly" \
    nginx:stable-alpine >/dev/null
fi

# Add only a new virtual host to shared Caddy; validate before hot reload.
MARKER="# BEGIN QAZAIRPRES.KZ — managed by deploy-qazairpres.sh"
if ! grep -Fq "$MARKER" "$CADDYFILE"; then
  if grep -Eq '^[[:space:]]*(www\.)?qazairpres\.kz([[:space:][:punct:]]|$)' "$CADDYFILE"; then
    echo "Domain already configured outside our marker. No Caddy changes made." >&2; exit 1
  fi
  cp -a "$CADDYFILE" "$CADDYFILE.bak-$(date +%Y%m%d-%H%M%S)"
  cp -a "$CADDYFILE" "$TMP/Caddyfile.backup"
  cat >> "$CADDYFILE" <<'CADDY'

# BEGIN QAZAIRPRES.KZ — managed by deploy-qazairpres.sh
qazairpres.kz {
  encode zstd gzip
  reverse_proxy qazairpres-site:80
}

www.qazairpres.kz {
  redir https://qazairpres.kz{uri} permanent
}
# END QAZAIRPRES.KZ
CADDY
  if ! docker exec "$CADDY_ID" caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile; then
    cp "$TMP/Caddyfile.backup" "$CADDYFILE"
    echo "Caddy validation failed. Original Caddyfile restored; Caddy NOT reloaded." >&2
    exit 1
  fi
fi
docker exec "$CADDY_ID" caddy reload --config /etc/caddy/Caddyfile --adapter caddyfile
echo "Production files installed: $WWW"
echo "Main domain: https://$DOMAIN/"
echo "Sitemap: https://$DOMAIN/sitemap.xml"
echo "Required PS.KZ DNS: @ A 82.115.43.192; www A 82.115.43.192"
echo "Check HTTPS after DNS propagation; Caddy must reach ports 80/443."
