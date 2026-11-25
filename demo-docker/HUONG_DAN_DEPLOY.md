# Deploy Demo CRM (Docker) — cho người nhận server

Gói demo: **Frappe CRM + pushesale (Hàng hóa / Kho / Kênh) + Chatwoot**, **1 URL** (nginx).

## 1. Clone từ Git

```bash
git clone https://github.com/hoang89210/crm_frappe.git
cd crm_frappe/demo-docker
```

(Nếu repo đã có sẵn: `git pull` rồi `cd demo-docker`.)

## 2. Yêu cầu server

- Docker + Docker Compose
- Ubuntu 20.04/22.04 (hoặc tương đương)
- **RAM ≥ 8GB**
- Port **80** mở ra ngoài (IP public)
- Quyền root/sudo

## 3. Cấu hình nhanh

```bash
cp .env.example .env
nano .env   # hoặc vi
```

Sửa tối thiểu:

| Biến | Ý nghĩa | Ví dụ |
|------|---------|--------|
| `PUBLIC_BASE_URL` | URL khách mở (không `/` cuối) | `http://203.0.113.10` |
| `DB_ROOT_PASSWORD` | Mật khẩu MariaDB root | (mật khẩu mạnh) |
| `ADMIN_PASSWORD` | Login CRM Administrator | `admin` hoặc mạnh hơn |
| `CHATWOOT_SECRET_KEY_BASE` | Secret Chatwoot | xem lệnh dưới |
| `CHATWOOT_DB_PASSWORD` | Postgres Chatwoot | (mật khẩu mạnh) |

Tạo secret Chatwoot:

```bash
openssl rand -hex 64
```

Dán vào `CHATWOOT_SECRET_KEY_BASE` trong `.env`.

## 4. Chạy

```bash
docker compose up -d --build
```

Lần đầu **20–40 phút** (build image + cài CRM + seed).

Theo dõi:

```bash
docker compose logs -f backend
docker compose ps
```

Khi backend hiện `Starting Frappe with gunicorn on :8000` là CRM sẵn sàng. Nếu backend restart liên tục: `docker compose logs backend | grep entrypoint` để xem lý do (xem mục "Khởi động backend" trong `DOCKER_DEPLOY_GUIDE.md`).

## 5. Truy cập (1 IP)

| Ứng dụng | URL |
|----------|-----|
| CRM login | `http://<IP>/login` |
| CRM app | `http://<IP>/crm` |
| Hàng hóa | `http://<IP>/crm/hang-hoa` |
| Kho | `http://<IP>/crm/kho` |
| Kênh | `http://<IP>/crm/kenh` |
| Chatwoot | `http://<IP>/chatwoot/` |

**CRM login:** `Administrator` / giá trị `ADMIN_PASSWORD` (mặc định `admin`).

**Chatwoot:** lần đầu mở `/chatwoot/` → wizard SuperAdmin / onboarding → tạo account → lấy API token → dán vào màn **Kênh** trên CRM nếu cần nối inbox.

## 6. Checklist

- [ ] `git clone` xong, đứng trong `demo-docker`
- [ ] `.env` đã sửa `PUBLIC_BASE_URL` = IP thật
- [ ] `CHATWOOT_SECRET_KEY_BASE` đã random
- [ ] `docker compose up -d --build` xong, không container restart loop
- [ ] `/login` vào được
- [ ] `/crm/hang-hoa` có sản phẩm seed
- [ ] `/crm/kho`, `/crm/kenh` mở được
- [ ] `/chatwoot/` mở được

## 7. Lệnh hữu ích

```bash
docker compose ps
docker compose logs -f backend
docker compose logs -f chatwoot
docker compose restart backend nginx
docker compose down          # dừng, giữ data
docker compose down -v       # XÓA data (cẩn thận)
```

Backup site CRM:

```bash
docker compose exec backend bench --site crm.local backup --with-files
```

## 8. Lỗi thường gặp

| Hiện tượng | Xử lý |
|------------|--------|
| Port 80 bận | Đổi map `"80:80"` → `"8080:80"` trong `docker-compose.yml`, vào `http://IP:8080` |
| RAM thấp / OOM | Tăng RAM máy / Docker Desktop ≥ 8GB |
| `/chatwoot/` 502 | Đợi Chatwoot khởi động thêm 30–60s, xem `docker compose logs chatwoot` |
| CRM 404 trên IP | Đảm bảo backend đã `Starting Frappe with gunicorn`; `PUBLIC_BASE_URL` đúng host đang mở browser |
| Backend restart liên tục, log `FATAL: ... half-created` / `may hold data` | Site tạo dở hoặc hỏng. Site dở không dữ liệu được tự tạo lại khi `AUTO_RECREATE_BROKEN_SITE=1`; site có dữ liệu không bao giờ bị tự drop: backup rồi làm theo hướng dẫn in trong log |
| Build fail mạng | Cần server ra được GitHub + Docker Hub |

## 9. Repo & hỗ trợ

- **Git:** https://github.com/hoang89210/crm_frappe  
- Thư mục deploy: `demo-docker/`  
- Chi tiết kỹ thuật thêm: `demo-docker/DOCKER_DEPLOY_GUIDE.md`

Liên hệ người gửi gói nếu cần hỗ trợ online khi deploy.
