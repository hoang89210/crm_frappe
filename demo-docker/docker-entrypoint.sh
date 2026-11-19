#!/bin/bash
set -e

SITE_NAME=${SITE_NAME:-crm.local}
ADMIN_PASSWORD=${ADMIN_PASSWORD:-admin}
DB_ROOT_PASSWORD=${DB_ROOT_PASSWORD:-change-me}
DB_HOST=${DB_HOST:-mariadb}
REDIS_CACHE=${REDIS_CACHE:-redis-cache:6379}
REDIS_QUEUE=${REDIS_QUEUE:-redis-queue:6379}
CHATWOOT_INTERNAL_URL=${CHATWOOT_INTERNAL_URL:-http://chatwoot:3000/chatwoot}
CHATWOOT_PUBLIC_URL=${CHATWOOT_PUBLIC_URL:-http://127.0.0.1/chatwoot}

cd /home/frappe/frappe-bench

mkdir -p sites
printf "frappe\ncrm\npushesale\n" > sites/apps.txt

echo "Waiting for MariaDB..."
for i in $(seq 1 60); do
  if mysqladmin ping -h"$DB_HOST" -uroot -p"$DB_ROOT_PASSWORD" --silent 2>/dev/null; then
    echo "MariaDB is up"
    break
  fi
  echo "  ... ($i/60)"
  sleep 2
done

bench set-config -g db_host "$DB_HOST" || true
bench set-config -g redis_cache "redis://$REDIS_CACHE" || true
bench set-config -g redis_queue "redis://$REDIS_QUEUE" || true
bench set-config -g redis_socketio "redis://$REDIS_QUEUE" || true

if [ ! -d "sites/$SITE_NAME" ]; then
  echo "Creating new site: $SITE_NAME"
  bench new-site "$SITE_NAME" \
    --mariadb-root-password "$DB_ROOT_PASSWORD" \
    --admin-password "$ADMIN_PASSWORD" \
    --db-host "$DB_HOST" \
    --mariadb-user-host-login-scope='%'

  printf "frappe\ncrm\npushesale\n" > sites/apps.txt

  echo "Installing crm..."
  bench --site "$SITE_NAME" install-app crm
  printf "frappe\ncrm\npushesale\n" > sites/apps.txt

  echo "Installing pushesale..."
  bench --site "$SITE_NAME" install-app pushesale

  echo "Running migrate..."
  bench --site "$SITE_NAME" migrate

  echo "Seeding catalog/stock..."
  bench --site "$SITE_NAME" execute pushesale.catalog.seed || true
  bench --site "$SITE_NAME" execute pushesale.stock.seed || true

  bench --site "$SITE_NAME" clear-cache || true
else
  printf "frappe\ncrm\npushesale\n" > sites/apps.txt
  bench --site "$SITE_NAME" install-app crm 2>/dev/null || true
  bench --site "$SITE_NAME" install-app pushesale 2>/dev/null || true
fi

# Default site for bare IP access
bench use "$SITE_NAME" || true
echo "$SITE_NAME" > sites/currentsite.txt

# Chatwoot endpoints for pushesale (server-side + UI hint)
bench --site "$SITE_NAME" set-config CHATWOOT_URL "$CHATWOOT_INTERNAL_URL" || true
bench --site "$SITE_NAME" set-config CHATWOOT_PUBLIC_URL "$CHATWOOT_PUBLIC_URL" || true
bench --site "$SITE_NAME" set-config CHATWOOT_WEBHOOK_SECRET "${CHATWOOT_WEBHOOK_SECRET:-change-me}" || true

echo "Starting Frappe on :8000 ..."
exec bench serve --port 8000
