# Deploy Docker lên VPS (giai đoạn 2)

Bộ file này là **template tham khảo** để chuyển từ Local WSL sang VPS Docker.
Mục tiêu: khách test trên môi trường ổn định, code vẫn sửa nhanh ở local.

## 1. Yêu cầu VPS

| Mục | Tối thiểu |
|---|---|
| OS | Ubuntu 22.04 |
| RAM | 4 GB |
| CPU | 2 vCPU |
| Disk | 40 GB |
| Quyền | root / sudo |
| Phần mềm | Docker Engine + Docker Compose plugin |
| Port | 80 (hoặc 443 nếu có domain) |

Kiểm tra nhanh trên VPS:

```bash
free -h
nproc
df -h /
docker --version
docker compose version
```

## 2. Chuẩn bị build context

```bash
# Trên máy Windows (đang ở repo CRM_Frappe)
mkdir -p docker/apps
cp -r p6_code/pushesale docker/apps/pushesale
```

Yêu cầu app `pushesale` có `pyproject.toml` hoặc `setup.py` để `bench get-app`/`install-app` nhận diện.
Nếu thiếu, bổ sung trước khi build.

## 3. Build image

```bash
cd docker
docker build -f Containerfile -t crm-demo:latest .
```

Pin version trong `apps.json` và `Containerfile` khi cần cố định (ví dụ CRM `v1.85.1`, Frappe `version-15`).

## 4. Cấu hình và chạy

```bash
cp .env.example .env
# sửa SITE_NAME, DB_ROOT_PASSWORD, ADMIN_PASSWORD

docker compose up -d
docker compose logs -f configurator
```

Tạo site và cài app (chạy 1 lần):

```bash
docker compose exec backend bench new-site "$SITE_NAME" \
  --mariadb-root-password "$DB_ROOT_PASSWORD" \
  --admin-password "$ADMIN_PASSWORD" \
  --no-mariadb-socket

docker compose exec backend bench --site "$SITE_NAME" install-app crm
docker compose exec backend bench --site "$SITE_NAME" install-app pushesale
docker compose exec backend bench --site "$SITE_NAME" migrate
docker compose exec backend bench --site "$SITE_NAME" execute pushesale.catalog.seed
docker compose exec backend bench --site "$SITE_NAME" execute pushesale.stock.seed
docker compose exec backend bench build --app crm
```

Kiểm tra:

```bash
docker compose ps
curl -I http://127.0.0.1/login
```

## 5. Truy cập khi chưa có domain

Dùng Cloudflare Quick Tunnel trỏ vào port 80 của VPS:

```bash
cloudflared tunnel --url http://127.0.0.1:80 --no-autoupdate
```

URL random đổi mỗi lần chạy lại. Khi có domain: trỏ DNS về VPS, thêm reverse proxy/SSL
(traefik hoặc nginx + certbot).

## 6. Cập nhật code (quan trọng)

Nguyên tắc: **local là nơi sửa, VPS là nơi demo**.

1. Sửa + test trên Local WSL.
2. Commit/push code.
3. Trên VPS: cập nhật source rồi rebuild:

```bash
cd docker
cp -r /duong/dan/moi/pushesale apps/pushesale
docker compose build backend
docker compose up -d backend queue-short queue-long scheduler websocket
docker compose exec backend bench --site "$SITE_NAME" migrate
docker compose exec backend bench --site "$SITE_NAME" clear-cache
```

Downtime dự kiến: 1–3 phút. Nên cập nhật ngoài giờ khách test.

Với thay đổi Vue: rebuild image (bước build ở trên đã chạy `bench build --app crm`),
sau đó khách Ctrl+F5.

## 7. Backup & restore

Backup:

```bash
docker compose exec backend bench --site "$SITE_NAME" backup --with-files
docker compose exec backend ls sites/"$SITE_NAME"/private/backups
```

Copy ra ngoài VPS định kỳ. Restore:

```bash
docker compose exec backend bench --site "$SITE_NAME" restore <db-backup.sql.gz>
```

## 8. Scheduler

Container `scheduler` chạy `bench schedule`, bao gồm
`pushesale.api.fb_pages.scheduled_sync_pages` (đồng bộ Facebook định kỳ).
Kiểm tra:

```bash
docker compose logs -f scheduler
```

## 9. Checklist trước khi mở cho khách

- [ ] `.env` đã đổi mật khẩu, không commit.
- [ ] Domain/SSL hoặc tunnel hoạt động.
- [ ] `migrate` + seed dữ liệu demo xong.
- [ ] Tài khoản sale1/2/3 tồn tại.
- [ ] Scheduler đang chạy.
- [ ] Backup định kỳ đã bật.
- [ ] Đã test đăng nhập + 3 màn `/crm/hang-hoa`, `/crm/kho`, `/crm/kenh`.
