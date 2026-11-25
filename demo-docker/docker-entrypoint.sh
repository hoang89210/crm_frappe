#!/bin/bash
# demo-docker backend entrypoint.
#
# Goals (see PR "fix/docker-half-created-site"):
#   * Never serve a half-created site. A first boot that is interrupted during
#     `bench new-site` leaves sites/$SITE_NAME on disk with a database that is
#     missing Core tables; the old entrypoint skipped new-site, swallowed the
#     install-app errors and served HTTP 500 ("Module Core not found") forever.
#   * Recreate such a site automatically, but ONLY when detection is strict:
#     no provisioning marker AND (no database OR Core tables missing/empty)
#     AND no user data. Anything ambiguous fails loudly and drops nothing.
#   * Healthy site -> always `bench migrate`. Any failure -> exit non-zero, so
#     `docker compose ps/logs` shows a restarting container instead of a 500.
#   * Serve with gunicorn (no Werkzeug debugger, no duplicate Date header).
set -Eeuo pipefail

SITE_NAME=${SITE_NAME:-crm.local}
ADMIN_PASSWORD=${ADMIN_PASSWORD:-admin}
DB_ROOT_PASSWORD=${DB_ROOT_PASSWORD:-change-me}
DB_HOST=${DB_HOST:-mariadb}
DB_PORT=${DB_PORT:-3306}
REDIS_CACHE=${REDIS_CACHE:-redis-cache:6379}
REDIS_QUEUE=${REDIS_QUEUE:-redis-queue:6379}
CHATWOOT_INTERNAL_URL=${CHATWOOT_INTERNAL_URL:-http://chatwoot:3000/chatwoot}
CHATWOOT_PUBLIC_URL=${CHATWOOT_PUBLIC_URL:-http://127.0.0.1/chatwoot}
CHATWOOT_WEBHOOK_SECRET=${CHATWOOT_WEBHOOK_SECRET:-change-me}

# 1 = drop + recreate a site that is *provably* half-created (see is_half_created).
# 0 = refuse to start and print manual recovery steps instead.
AUTO_RECREATE_BROKEN_SITE=${AUTO_RECREATE_BROKEN_SITE:-1}
# 1 = `bench serve` (Werkzeug, auto-reload, interactive debugger) for local dev only.
FRAPPE_DEV_SERVER=${FRAPPE_DEV_SERVER:-0}
GUNICORN_WORKERS=${GUNICORN_WORKERS:-2}
GUNICORN_THREADS=${GUNICORN_THREADS:-4}
GUNICORN_TIMEOUT=${GUNICORN_TIMEOUT:-120}
DB_WAIT_SECONDS=${DB_WAIT_SECONDS:-120}

BENCH=/home/frappe/frappe-bench
IMAGE_ASSETS=$BENCH/assets            # built into the image (see Dockerfile)
SITE_DIR=sites/$SITE_NAME
MARKER=$SITE_DIR/.provisioned
APPS=(crm pushesale)

cd "$BENCH"

log()  { echo "[entrypoint] $*"; }
fail() { echo "[entrypoint] FATAL: $*" >&2; exit 1; }
trap 'rc=$?; echo "[entrypoint] FATAL: command failed (exit $rc) at line $LINENO: $BASH_COMMAND" >&2; exit $rc' ERR

# Root SQL against MariaDB without putting the password on the command line.
MAIN_PID=$$
trap 'exit 1' TERM
sql_raw() { MYSQL_PWD="$DB_ROOT_PASSWORD" mysql --protocol=tcp -h"$DB_HOST" -P"$DB_PORT" -uroot -N -B -e "$1"; }
# Any SQL error aborts the WHOLE entrypoint, even when called inside $(...) or
# an `if` (where set -e is ignored). Otherwise a transient DB error could look
# like "table missing" and get a healthy site classified as half-created.
sql() {
  local out
  if ! out=$(sql_raw "$1" 2>&1); then
    echo "[entrypoint] FATAL: SQL failed, aborting without touching the site: $out" >&2
    kill -TERM "$MAIN_PID"; exit 1
  fi
  [ -z "$out" ] || printf '%s\n' "$out"
}
sql_quote() { printf "%s" "$1" | sed "s/'/''/g"; }

mkdir -p sites
printf "frappe\ncrm\npushesale\n" > sites/apps.txt

# --- Assets -------------------------------------------------------------------
# The `sites` named volume hides sites/assets from the image. Docker only seeds
# a volume once (when it is empty), so after an image rebuild the volume would
# keep stale assets.json -> 404 on new bundles. Built assets live outside
# sites/ in the image; point sites/assets at them on every boot.
if [ -d "$IMAGE_ASSETS" ]; then
  if [ "$(readlink sites/assets 2>/dev/null || true)" != "$IMAGE_ASSETS" ]; then
    rm -rf sites/assets
    ln -s "$IMAGE_ASSETS" sites/assets
    log "Linked sites/assets -> $IMAGE_ASSETS"
  fi
elif [ ! -e sites/assets/assets.json ]; then
  fail "no built assets: $IMAGE_ASSETS missing and sites/assets/assets.json missing (rebuild the image)"
fi

# --- Wait for MariaDB -----------------------------------------------------------
log "Waiting for MariaDB at $DB_HOST:$DB_PORT (max ${DB_WAIT_SECONDS}s)..."
deadline=$((SECONDS + DB_WAIT_SECONDS))
until sql_raw "SELECT 1" >/dev/null 2>&1; do
  if [ "$SECONDS" -ge "$deadline" ]; then
    sql_raw "SELECT 1" || true   # show the real error once
    fail "MariaDB at $DB_HOST:$DB_PORT not reachable with root credentials after ${DB_WAIT_SECONDS}s"
  fi
  sleep 2
done
log "MariaDB is up"

bench set-config -g db_host "$DB_HOST"
bench set-config -g redis_cache "redis://$REDIS_CACHE"
bench set-config -g redis_queue "redis://$REDIS_QUEUE"
bench set-config -g redis_socketio "redis://$REDIS_QUEUE"

# --- Site state detection --------------------------------------------------------
site_db_name() {
  [ -f "$SITE_DIR/site_config.json" ] || { echo ""; return 0; }
  env/bin/python -c 'import json,sys; print(json.load(open(sys.argv[1])).get("db_name") or "")' "$SITE_DIR/site_config.json"
}
db_exists()    { [ "$(sql "SELECT COUNT(*) FROM information_schema.SCHEMATA WHERE SCHEMA_NAME='$(sql_quote "$1")'")" != "0" ]; }
table_exists() { [ "$(sql "SELECT COUNT(*) FROM information_schema.TABLES WHERE TABLE_SCHEMA='$(sql_quote "$1")' AND TABLE_NAME='$(sql_quote "$2")'")" != "0" ]; }
table_rows()   { if table_exists "$1" "$2"; then sql "SELECT COUNT(*) FROM \`$1\`.\`$2\`"; else echo 0; fi; }

core_ok() {  # Core tables that a finished `new-site` always populates
  local db=$1
  [ "$(table_rows "$db" 'tabModule Def')" -gt 0 ] &&
  [ "$(table_rows "$db" 'tabPatch Log')" -gt 0 ] &&
  [ "$(table_rows "$db" 'tabDefaultValue')" -gt 0 ] &&
  grep -q '"frappe"' <<<"$(installed_apps "$db")"
}

# Prints a reason and returns 0 if the DB contains anything a user could have
# created: real users, CRM records, uploaded files (DB rows or files on disk).
has_user_data() {
  local db=$1 n
  n=$(table_rows "$db" 'tabUser');      [ "$n" -gt 2 ] && { echo "tabUser has $n rows"; return 0; }
  for t in 'tabCRM Lead' 'tabCRM Deal' 'tabContact' 'tabNote' 'tabComment' 'tabCommunication'; do
    n=$(table_rows "$db" "$t");         [ "$n" -gt 0 ] && { echo "$t has $n rows"; return 0; }
  done
  if table_exists "$db" 'tabFile'; then
    n=$(sql "SELECT COUNT(*) FROM \`$db\`.\`tabFile\` WHERE IFNULL(is_folder,0)=0")
    [ "$n" -gt 0 ] && { echo "tabFile has $n non-folder rows"; return 0; }
  fi
  return 1
}
has_files_on_disk() {
  local n
  n=$({ find "$SITE_DIR/public/files" "$SITE_DIR/private/files" "$SITE_DIR/private/backups" -type f 2>/dev/null || true; } | wc -l)
  [ "$n" -gt 0 ] && { echo "$n file(s) under public/private files/backups"; return 0; }
  return 1
}

installed_apps() {
  table_exists "$1" 'tabDefaultValue' || return 0
  sql "SELECT defvalue FROM \`$1\`.\`tabDefaultValue\` WHERE parent IN ('__global','__default') AND defkey='installed_apps'"
}

drop_half_site() {
  local db=$1 ts archive
  ts=$(date +%Y%m%d-%H%M%S)
  if [ -n "$db" ]; then
    log "Dropping half-created database '$db' and its DB user"
    sql "DROP DATABASE IF EXISTS \`$db\`; DROP USER IF EXISTS '$(sql_quote "$db")'@'%'; DROP USER IF EXISTS '$(sql_quote "$db")'@'localhost'; FLUSH PRIVILEGES;"
  fi
  archive=sites/.archived_broken_sites/$SITE_NAME-$ts
  mkdir -p sites/.archived_broken_sites
  mv "$SITE_DIR" "$archive"
  log "Moved leftover $SITE_DIR to $archive (site_config kept for forensics)"
}

recovery_help() {
  cat >&2 <<HELP
[entrypoint] Manual recovery (DESTROYS this site's data, back it up first):
  docker compose exec backend bench drop-site $SITE_NAME --force --db-root-password "\$DB_ROOT_PASSWORD"
  docker compose restart backend
HELP
  if [ "${1:-}" = half ]; then
    echo "[entrypoint] Or set AUTO_RECREATE_BROKEN_SITE=1 to let the entrypoint recreate this provably half-created site." >&2
  fi
}

# Returns: fresh | provisioned | legacy | half:<reason> | ambiguous:<reason>
classify_site() {
  local db reason
  if [ ! -d "$SITE_DIR" ]; then echo fresh; return; fi
  if [ -f "$MARKER" ]; then echo provisioned; return; fi
  db=$(site_db_name)
  if [ -z "$db" ]; then
    if reason=$(has_files_on_disk); then echo "ambiguous:no site_config/db_name but $reason"; return; fi
    echo "half:site dir exists without site_config.json/db_name"; return
  fi
  if ! db_exists "$db"; then
    if reason=$(has_files_on_disk); then echo "ambiguous:database '$db' missing but $reason"; return; fi
    echo "half:database '$db' does not exist"; return
  fi
  if core_ok "$db"; then echo legacy; return; fi
  if reason=$(has_user_data "$db"); then echo "ambiguous:Core tables missing/empty but $reason"; return; fi
  if reason=$(has_files_on_disk); then echo "ambiguous:Core tables missing/empty but $reason"; return; fi
  echo "half:Core tables (tabModule Def/tabPatch Log/tabDefaultValue) missing or empty, no user data"
}

state=$(classify_site)
log "Site $SITE_NAME state: $state"

case "$state" in
  half:*)
    if [ "$AUTO_RECREATE_BROKEN_SITE" = "1" ]; then
      log "WARNING: $SITE_NAME is half-created (${state#half:}); AUTO_RECREATE_BROKEN_SITE=1 -> recreating"
      drop_half_site "$(site_db_name)"
      state=fresh
    else
      echo "[entrypoint] FATAL: $SITE_NAME is half-created (${state#half:}) and AUTO_RECREATE_BROKEN_SITE=$AUTO_RECREATE_BROKEN_SITE" >&2
      recovery_help half; exit 1
    fi ;;
  ambiguous:*)
    echo "[entrypoint] FATAL: $SITE_NAME is broken but may hold data (${state#ambiguous:}). Not dropping anything." >&2
    recovery_help; exit 1 ;;
esac

write_marker() {
  { echo "provisioned_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"; echo "via=$1"; echo "apps=frappe ${APPS[*]}"; } > "$MARKER"
  log "Wrote $MARKER ($1)"
}

if [ "$state" = fresh ]; then
  log "Creating new site: $SITE_NAME"
  bench new-site "$SITE_NAME" \
    --mariadb-root-password "$DB_ROOT_PASSWORD" \
    --admin-password "$ADMIN_PASSWORD" \
    --db-host "$DB_HOST" \
    --mariadb-user-host-login-scope='%'
  printf "frappe\ncrm\npushesale\n" > sites/apps.txt
  for app in "${APPS[@]}"; do
    log "Installing $app..."
    bench --site "$SITE_NAME" install-app "$app"
    printf "frappe\ncrm\npushesale\n" > sites/apps.txt
  done
  log "Running migrate..."
  bench --site "$SITE_NAME" migrate
  log "Seeding catalog/stock..."
  bench --site "$SITE_NAME" execute pushesale.catalog.seed
  bench --site "$SITE_NAME" execute pushesale.stock.seed
  write_marker new-site
else
  # provisioned or legacy (pre-marker site whose Core tables are populated)
  db=$(site_db_name)
  [ -n "$db" ] || fail "$SITE_DIR has a marker but no db_name in site_config.json"
  core_ok "$db" || { echo "[entrypoint] FATAL: $SITE_NAME is marked provisioned but Core tables are missing/empty. Not dropping a provisioned site." >&2; recovery_help; exit 1; }
  apps_json=$(installed_apps "$db")
  for app in "${APPS[@]}"; do
    if ! grep -q "\"$app\"" <<<"$apps_json"; then
      log "App $app not installed on $SITE_NAME (interrupted install?) -> installing"
      bench --site "$SITE_NAME" install-app "$app"
      printf "frappe\ncrm\npushesale\n" > sites/apps.txt
    fi
  done
  log "Running migrate on existing site..."
  bench --site "$SITE_NAME" migrate
  [ "$state" = legacy ] && write_marker "adopted-existing-site"
fi

bench --site "$SITE_NAME" clear-cache

# Default site for bare IP / localhost access
bench use "$SITE_NAME"
echo "$SITE_NAME" > sites/currentsite.txt

# Chatwoot endpoints for pushesale (server-side + UI hint)
bench --site "$SITE_NAME" set-config CHATWOOT_URL "$CHATWOOT_INTERNAL_URL"
bench --site "$SITE_NAME" set-config CHATWOOT_PUBLIC_URL "$CHATWOOT_PUBLIC_URL"
bench --site "$SITE_NAME" set-config CHATWOOT_WEBHOOK_SECRET "$CHATWOOT_WEBHOOK_SECRET"

trap - ERR
if [ "$FRAPPE_DEV_SERVER" = "1" ]; then
  log "FRAPPE_DEV_SERVER=1 -> bench serve (Werkzeug dev server, debugger ON). Do NOT expose publicly."
  exec bench serve --port 8000
fi

log "Starting Frappe with gunicorn on :8000 (workers=$GUNICORN_WORKERS threads=$GUNICORN_THREADS timeout=$GUNICORN_TIMEOUT)"
# application_with_statics() = frappe.app.application + /assets and /files
# (nginx in this stack has no access to the sites volume, so gunicorn serves them).
exec env/bin/gunicorn \
  --chdir "$BENCH/sites" \
  --bind 0.0.0.0:8000 \
  --workers "$GUNICORN_WORKERS" \
  --threads "$GUNICORN_THREADS" \
  --worker-class gthread \
  --timeout "$GUNICORN_TIMEOUT" \
  --graceful-timeout 30 \
  --access-logfile - \
  --error-logfile - \
  "frappe.app:application_with_statics()"
