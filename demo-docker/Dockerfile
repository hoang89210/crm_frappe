ARG FRAPPE_BRANCH=version-15
FROM frappe/base:${FRAPPE_BRANCH}

ARG FRAPPE_BRANCH=version-15

USER root
RUN apt-get update \
 && apt-get install -y --no-install-recommends cron default-mysql-client \
 && rm -rf /var/lib/apt/lists/*

USER frappe
WORKDIR /home/frappe

COPY --chown=frappe:frappe apps.json /tmp/apps.json

RUN bench init \
      --skip-redis-config-generation \
      --frappe-branch ${FRAPPE_BRANCH} \
      /home/frappe/frappe-bench

COPY --chown=frappe:frappe apps/pushesale /home/frappe/frappe-bench/apps/pushesale
COPY --chown=frappe:frappe crm-frontend-patch /tmp/crm-frontend-patch

USER root
RUN chmod +x /tmp/crm-frontend-patch/apply-patch.sh \
 && sed -i 's/\r$//' /tmp/crm-frontend-patch/apply-patch.sh
USER frappe

RUN cd /home/frappe/frappe-bench \
 && echo "pushesale" >> sites/apps.txt \
 && ./env/bin/pip install -e ./apps/pushesale --quiet \
 && bench get-app https://github.com/frappe/crm --branch v1.85.1 \
 && bash /tmp/crm-frontend-patch/apply-patch.sh \
 && bench setup requirements --node \
 && bench build --app crm \
 && bench build --app frappe

# Keep built assets OUTSIDE sites/: the `sites` named volume hides sites/assets
# and is only seeded once, so after a rebuild it would serve stale assets.json.
# The entrypoint symlinks sites/assets -> /home/frappe/frappe-bench/assets on boot.
RUN cd /home/frappe/frappe-bench \
 && cp -a sites/assets /home/frappe/frappe-bench/assets \
 && rm -rf sites/assets

COPY --chown=frappe:frappe docker-entrypoint.sh /home/frappe/frappe-bench/docker-entrypoint.sh
USER root
RUN sed -i 's/\r$//' /home/frappe/frappe-bench/docker-entrypoint.sh \
 && chmod +x /home/frappe/frappe-bench/docker-entrypoint.sh
USER frappe
WORKDIR /home/frappe/frappe-bench
