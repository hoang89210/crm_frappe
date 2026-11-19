# Hướng dẫn Deploy Demo (CRM + Pushesale + Chatwoot) — 1 URL

## 1. Yêu cầu

- Ubuntu 20.04/22.04 hoặc Docker Desktop
- Docker + Docker Compose
- **RAM ≥ 8GB** (Frappe + Chatwoot)
- Port **80** mở (IP public nếu server)
- Quyền root/sudo

## 2. File trong gói

- `docker-compose.yml` — Frappe, CRM, pushesale, Chatwoot, nginx
- `Dockerfile` — build image CRM (có Hàng hóa / Kho / Kênh)
- `apps/pushesale/` — app pushesale
- `crm-frontend-patch/` — SPA HangHoa, Kho, Kenh
- `nginx/default.conf` — 1 URL: `/` = CRM, `/chatwoot/` = Chatwoot
- `.env.example` → copy thành `.env`

## 3. Deploy

```bash
cd demo-docker   # thư mục giải nén
cp .env.example .env
```

Sửa `.env`:

- `DB_ROOT_PASSWORD`, `ADMIN_PASSWORD` — mật khẩu mạnh
- `PUBLIC_BASE_URL` — **URL công khai không trailing slash**, ví dụ:
  - Local: `http://127.0.0.1`
  - Server: `http://203.0.113.10`
- `CHATWOOT_SECRET_KEY_BASE` — tạo bằng:

```bash
openssl rand -hex 64
```

Khởi động (lần đầu 20–40 phút):

```bash
docker compose up -d --build
```

Xem log:

```bash
docker compose logs -f backend
docker compose logs -f chatwoot
docker compose logs -f nginx
```

Khi backend hiện `Starting Frappe on :8000` và chatwoot không crash → OK.

## 4. Truy cập (1 URL)

| Ứng dụng | Đường dẫn |
|----------|-----------|
| CRM Frappe | `http://<IP>/` hoặc `http://<IP>/crm` |
| Hàng hóa | `http://<IP>/crm/hang-hoa` |
| Kho | `http://<IP>/crm/kho` |
| Kênh (Chatwoot + FB) | `http://<IP>/crm/kenh` |
| Chatwoot | `http://<IP>/chatwoot/` |

### Login CRM

- User: `Administrator`
- Pass: giá trị `ADMIN_PASSWORD` trong `.env` (mặc định `admin`)

### Chatwoot lần đầu

1. Mở `http://<IP>/chatwoot/`
2. Tạo account admin theo wizard
3. Tạo Inbox / API token
4. Vào CRM `/crm/kenh` dán:
   - URL: `http://<IP>/chatwoot` (hoặc internal nếu form hỗ trợ)
   - Account ID + API token

## 5. Backup / Restore (Frappe)

```bash
docker compose exec backend bench --site crm.local backup --with-files
```

File trong volume `sites`.

## 6. Lệnh hữu ích

```bash
docker compose ps
docker compose logs -f backend
docker compose restart backend nginx
docker compose down          # dừng, giữ data
docker compose down -v       # XÓA toàn bộ data (cẩn thận)
```

## 7. Checklist

- [ ] `.env` đã sửa (IP + secret Chatwoot)
- [ ] `docker compose up -d --build` xong
- [ ] Login CRM OK
- [ ] `/crm/hang-hoa` có sản phẩm seed
- [ ] `/crm/kho` mở được
- [ ] `/crm/kenh` mở được
- [ ] `/chatwoot/` mở wizard/login
- [ ] Đã backup nếu cần

## 8. Lưu ý

- Không commit file `.env` / secret.
- RAM thấp → Chatwoot có thể OOM; tăng RAM Docker Desktop.
- Nếu `/chatwoot/` lỗi asset: kiểm tra `PUBLIC_BASE_URL` đúng IP/host đang mở trình duyệt.
- Port 80 bận: đổi `"80:80"` trong compose sang `"8080:80"` rồi vào `http://IP:8080`.
