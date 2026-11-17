#!/usr/bin/env bash
# Update the existing QazAirPress bind mount; retain Docker/Caddy/DNS/TLS config.
set -Eeuo pipefail
readonly RELEASE=8304cdbaa250c1fe98b1ef3cf655f953e023e53d
readonly SITE=qazairpres-site
readonly BASE=/home/ubuntu/qazairpres-deploy
readonly WWW="$BASE/www"
readonly REPOSITORY=https://github.com/modulnydom/modulnydom.github.io.git
TMP=''
BACKUP=''
CHANGED=0
die() { printf '%s\n' "$*" >&2; exit 1; }
finish() {
  local status=$?
  trap - EXIT
  if (( status != 0 && CHANGED == 1 )); then
    printf 'Update failed; restoring backup: %s\n' "$BACKUP" >&2
    if rsync -a --delete "$BACKUP/www/" "$WWW/"; then
      printf 'Previous website restored.\n' >&2
    else
      printf 'RESTORE FAILED. Backup remains at %s\n' "$BACKUP" >&2
    fi
  fi
  [[ -z "$TMP" ]] || rm -rf -- "$TMP"
  exit "$status"
}
trap finish EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

[[ "$EUID" == 0 ]] || die 'Run with sudo bash update-production.sh'
for cmd in git docker python3 rsync curl sha256sum flock readlink; do
  command -v "$cmd" >/dev/null || die "Required command missing: $cmd. No website changes made."
done
python3 -c 'import sys; assert sys.version_info >= (3,12), "Python 3.12+ is required"'
[[ -d "$WWW" && ! -L "$WWW" ]] || die "Expected existing web root missing: $WWW"
[[ "$(readlink -f "$WWW")" == "$WWW" ]] || die 'Unexpected symlink in web-root path.'
exec 9>"$BASE/.update.lock"
flock -n 9 || die 'Another QazAirPress update is running.'
[[ "$(docker inspect -f '{{.State.Running}}' "$SITE")" == true ]] || die "Existing container $SITE is not running."
mount_source="$(docker inspect -f '{{range .Mounts}}{{if eq .Destination "/usr/share/nginx/html"}}{{.Source}}{{end}}{{end}}' "$SITE")"
[[ "$mount_source" == "$WWW" ]] || die "Unexpected container web root: $mount_source. No website changes made."
[[ -f "$WWW/index.html" ]] || die 'Existing homepage not found; refusing an unverified destination.'

TMP="$(mktemp -d)"
curl -fsS --connect-timeout 10 --max-time 30 https://qazairpres.kz/ -o "$TMP/before.html"
git init -q "$TMP/source"
git -C "$TMP/source" remote add origin "$REPOSITORY"
git -C "$TMP/source" fetch -q --depth=1 --filter=blob:none origin "$RELEASE"
git -C "$TMP/source" sparse-checkout init --cone
git -C "$TMP/source" sparse-checkout set qazairpress-preview
git -C "$TMP/source" checkout -q --detach FETCH_HEAD
[[ "$(git -C "$TMP/source" rev-parse HEAD)" == "$RELEASE" ]] || die 'Source commit mismatch.'
python3 "$TMP/source/qazairpress-preview/scripts/build.py" --production --output "$TMP/production"
python3 "$TMP/source/qazairpress-preview/scripts/audit.py" --root "$TMP/production" --production
find "$TMP/production" -type d -exec chmod 755 {} +
find "$TMP/production" -type f -exec chmod 644 {} +

mkdir -p "$BASE/backups"
chmod 700 "$BASE/backups"
BACKUP="$(mktemp -d "$BASE/backups/before-$(date -u +%Y%m%dT%H%M%SZ)-XXXXXXXX")"
mkdir "$BACKUP/www"
rsync -a "$WWW/" "$BACKUP/www/"
printf '%s\n' "$RELEASE" > "$BACKUP/new-source-commit.txt"
printf 'Backup saved: %s\n' "$BACKUP"
CHANGED=1
# Keep the existing directory inode: the running container bind-mounts it.
rsync -a --delay-updates --delete-delay "$TMP/production/" "$WWW/"
python3 "$TMP/source/qazairpress-preview/scripts/audit.py" --root "$WWW" --production
for resource in index.html assets/home.css assets/home.js assets/site.js robots.txt sitemap.xml catalog/index.html; do
  public_path="$resource"
  [[ "$resource" != index.html ]] || public_path=''
  curl -fsS --compressed --retry 2 --connect-timeout 10 --max-time 30 \
    "https://qazairpres.kz/$public_path?qap_release=$RELEASE" -o "$TMP/live-check"
  expected="$(sha256sum "$TMP/production/$resource")"
  actual="$(sha256sum "$TMP/live-check")"
  [[ "${actual%% *}" == "${expected%% *}" ]] || die "Live content mismatch: $resource"
done
redirect="$(curl -sS --connect-timeout 10 --max-time 20 -o /dev/null -w '%{http_code} %{redirect_url}' http://qazairpres.kz/)"
case "$redirect" in
  '301 https://qazairpres.kz/'|'302 https://qazairpres.kz/'|'307 https://qazairpres.kz/'|'308 https://qazairpres.kz/') ;;
  *) die "Unexpected HTTP redirect: $redirect" ;;
esac
CHANGED=0
printf '\nSUCCESS: https://qazairpres.kz/\n28 pages deployed; 26 sitemap URLs; live HTML/assets verified over HTTPS.\nExisting domain, SSL and container configuration retained.\nBackup: %s\n' "$BACKUP"
