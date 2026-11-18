#!/usr/bin/env bash
# Isolated KAZVIET.ASIA production deploy beside QazAirPres on the shared VPS.
# Run on VPS as root: sudo bash deploy-kazviet.sh
set -Eeuo pipefail
umask 022

DOMAIN="kazviet.asia"
EXPECTED_IP="82.115.43.192"
SITE="kazviet-site"
NETWORK="modulnydom_default"
HOME_DIR="/home/ubuntu/kazviet-deploy"
WWW="$HOME_DIR/www"
REPO="https://github.com/modulnydom/modulnydom.github.io.git"
MARKER="# BEGIN KAZVIET.ASIA — managed by deploy-kazviet.sh"
TMP=""
BACKUP=""
CADDY_CONTAINER=""
CADDYFILE=""
NEW_BLOCK=0
NEW_CONTAINER=0
CHANGED_WWW=0
SUCCESS=0

log(){ printf '[KAZVIET] %s\n' "$*"; }
die(){ printf '[KAZVIET] ERROR: %s\n' "$*" >&2; exit 1; }
cleanup(){
  local status=$?
  trap - EXIT
  if [[ "$SUCCESS" != 1 && "$status" != 0 ]]; then
    if [[ "$CHANGED_WWW" == 1 && -n "$BACKUP" && -d "$BACKUP/www" ]]; then
      log "Restoring previous website backup."
      rsync -a --delete "$BACKUP/www/" "$WWW/" || log "WARNING: automatic WWW rollback failed. Backup: $BACKUP"
    fi
    if [[ "$NEW_BLOCK" == 1 && -f "$TMP/Caddyfile.before" ]]; then
      cp "$TMP/Caddyfile.before" "$CADDYFILE"
      docker exec "$CADDY_CONTAINER" caddy reload --config /etc/caddy/Caddyfile --adapter caddyfile >/dev/null 2>&1 || :
      log "Restored previous Caddy configuration."
    fi
    if [[ "$NEW_CONTAINER" == 1 ]]; then
      docker rm -f "$SITE" >/dev/null 2>&1 || :
    fi
  fi
  [[ -z "$TMP" ]] || rm -rf -- "$TMP"
  exit "$status"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

[[ "$EUID" == 0 ]] || die "Run on the VPS as root: sudo bash deploy-kazviet.sh"
for cmd in git docker python3 rsync curl flock grep cp mktemp; do
  command -v "$cmd" >/dev/null || die "Missing utility: $cmd"
done

docker network inspect "$NETWORK" >/dev/null 2>&1 || die "Shared network $NETWORK not found."
[[ -d "$HOME_DIR" || ! -e "$HOME_DIR" ]] || die "Unexpected deployment directory."
mkdir -p "$HOME_DIR"
exec 9>"$HOME_DIR/.deploy.lock"
flock -n 9 || die "Another KAZVIET deployment is active."

for id in $(docker ps -q); do
  docker exec "$id" caddy version >/dev/null 2>&1 || continue
  cfg="$(docker inspect -f '{{range .Mounts}}{{if eq .Destination "/etc/caddy/Caddyfile"}}{{.Source}}{{end}}{{end}}' "$id")"
  if [[ -z "$cfg" ]]; then
    folder="$(docker inspect -f '{{range .Mounts}}{{if eq .Destination "/etc/caddy"}}{{.Source}}{{end}}{{end}}' "$id")"
    [[ -z "$folder" ]] || cfg="$folder/Caddyfile"
  fi
  [[ -n "$cfg" && -f "$cfg" ]] || continue
  docker inspect -f '{{json .NetworkSettings.Networks}}' "$id" | grep -Fq "\"$NETWORK\"" || continue
  CADDY_CONTAINER="$id"
  CADDYFILE="$cfg"
  break
done
[[ -n "$CADDY_CONTAINER" ]] || die "Cannot locate shared Caddy/Caddyfile; no changes made."
grep -Fq 'qazairpres.kz' "$CADDYFILE" || die "Caddyfile does not include QazAirPres; refusing unknown reverse proxy."

if grep -Eq '^[[:space:]]*(www\.)?kazviet\.asia[[:space:]\{,]' "$CADDYFILE" &&
   ! grep -Fq "$MARKER" "$CADDYFILE"; then
  die "An unmanaged kazviet.asia block already exists."
fi

if docker inspect "$SITE" >/dev/null 2>&1; then
  current_mount="$(docker inspect -f '{{range .Mounts}}{{if eq .Destination "/usr/share/nginx/html"}}{{.Source}}{{end}}{{end}}' "$SITE")"
  [[ "$current_mount" == "$WWW" ]] || die "Existing $SITE has unexpected web root: $current_mount"
fi
if [[ -d "$WWW" && -n "$(ls -A "$WWW" 2>/dev/null)" ]]; then
  [[ -f "$WWW/.kazviet-release" ]] || die "Web root has files not installed by this script."
fi

TMP="$(mktemp -d)"
log "Fetching only the KAZVIET site from GitHub."
git clone -q --depth=1 --filter=blob:none --sparse "$REPO" "$TMP/source"
git -C "$TMP/source" sparse-checkout set kazviet
source_sha="$(git -C "$TMP/source" rev-parse HEAD)"
python3 "$TMP/source/kazviet/deploy/build-production.py" \
  --source "$TMP/source/kazviet" --output "$TMP/production" || die "Build / SEO audit failed."
printf 'source_sha=%s\n' "$source_sha" > "$TMP/production/.kazviet-release"

[[ -f "$TMP/production/index.html" ]] || die "Missing production homepage."
for lang in ru en kk; do
  [[ -f "$TMP/production/$lang/index.html" ]] || die "Missing $lang edition."
done
[[ ! -e "$TMP/production/vi" ]] || die "Vietnamese locale must remain unpublished pending legal review."
[[ -f "$TMP/production/favicon.svg" ]] || die "Missing KAZVIET favicon."
[[ -f "$TMP/production/site.webmanifest" ]] || die "Missing site manifest."
[[ -f "$TMP/production/sitemap.xml" ]] || die "Missing sitemap."

mkdir -p "$HOME_DIR/backups" "$WWW"
chmod 700 "$HOME_DIR/backups"
if [[ -f "$WWW/.kazviet-release" ]]; then
  BACKUP="$(mktemp -d "$HOME_DIR/backups/backup-$(date -u +%Y%m%dT%H%M%SZ)-XXXXXXXX")"
  mkdir -p "$BACKUP/www"
  rsync -a "$WWW/" "$BACKUP/www/"
fi
CHANGED_WWW=1
rsync -a --delay-updates --delete-delay "$TMP/production/" "$WWW/"
python3 "$TMP/source/kazviet/deploy/build-production.py" \
  --source "$TMP/source/kazviet" --output "$WWW" --audit-only || die "Installed files failed audit."
find "$WWW" -type d -exec chmod 755 {} +
find "$WWW" -type f -exec chmod 644 {} +

if docker inspect "$SITE" >/dev/null 2>&1; then
  docker start "$SITE" >/dev/null
else
  docker run -d --name "$SITE" --restart unless-stopped --network "$NETWORK" \
    --mount "type=bind,src=$WWW,dst=/usr/share/nginx/html,readonly" \
    nginx:stable-alpine >/dev/null
  NEW_CONTAINER=1
fi

if ! grep -Fq "$MARKER" "$CADDYFILE"; then
  cp -a "$CADDYFILE" "$TMP/Caddyfile.before"
  cp -a "$CADDYFILE" "$CADDYFILE.bak-kazviet-$(date -u +%Y%m%dT%H%M%SZ)"
  cat >> "$CADDYFILE" <<'CADDY'

# BEGIN KAZVIET.ASIA — managed by deploy-kazviet.sh
kazviet.asia {
  encode zstd gzip
  reverse_proxy kazviet-site:80
}

www.kazviet.asia {
  redir https://kazviet.asia{uri} permanent
}
# END KAZVIET.ASIA
CADDY
  NEW_BLOCK=1
fi

docker exec "$CADDY_CONTAINER" caddy validate \
  --config /etc/caddy/Caddyfile --adapter caddyfile || die "Caddy validation failed."
docker exec "$CADDY_CONTAINER" caddy reload \
  --config /etc/caddy/Caddyfile --adapter caddyfile || die "Caddy reload failed."
docker exec "$SITE" wget -q -O /dev/null http://127.0.0.1/ || die "Local Nginx is not serving the homepage."

SUCCESS=1
log "Dedicated files: $WWW"
log "GitHub source: $source_sha"
log "DNS expected: @ A $EXPECTED_IP; www CNAME kazviet.asia"
log "Caddy configured for automatic TLS: https://$DOMAIN/"
log "Verify: curl -I https://$DOMAIN/ and https://$DOMAIN/sitemap.xml"
log "QazAirPres files and service were not touched."
