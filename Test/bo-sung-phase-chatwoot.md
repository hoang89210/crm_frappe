# Bổ sung Phase Chatwoot — nối Chatwoot thật

Ngày ghi: 07/10/2026. Webhook Frappe đã xong (Phase 2, test 27/27).
File này liệt kê 4 thứ còn thiếu để tin nhắn inbox thật đổ thành CRM Lead.

## Webhook đã có sẵn
```
POST {PUBLIC_URL}/api/method/pushesale.api.chatwoot.webhook?secret=<CHATWOOT_WEBHOOK_SECRET>
```
- Chỉ nhận `message_created` loại `incoming` và `conversation_created`.
- Secret so bằng `hmac.compare_digest`; sai secret trả 403.
- Test live ngày 07/10: tạo lead → gửi lại trùng lead → sai secret 403. OK.

## 4 thứ còn thiếu

### 1. Chatwoot chạy bằng Docker
Services: `chatwoot` (rails `:3000`) + `chatwoot-worker` (sidekiq) + DB `pgvector/pgvector:pg16` + `redis`.
Lưu ý từ project cũ: image mặc định boot `irb` → phải set command `rails s` / `sidekiq`; lần đầu chạy `db:chatwoot_prepare`.
Docker Desktop trên máy đang tắt — bật lên trước.

### 2. Onboarding tay 1 lần trong Chatwoot
- Mở `:3000` → tạo tài khoản admin.
- Tạo inbox (Website trước; Facebook cần `CHATWOOT_FRONTEND_URL` là URL tunnel rồi recreate).
- Lấy **Account ID** (URL) + **API token** (Profile → Access Token).
- Settings → Webhooks → URL Frappe ở trên, event `message_created`.

### 3. Tunnel HTTPS về Frappe
Chatwoot/Meta không gọi được `127.0.0.1` hay `crm.local`.
Dùng cloudflared hoặc ngrok trỏ về `http://127.0.0.1:8000`, webhook dùng URL tunnel + `?secret=...`.

### 4. Điền config vào site
Trong `sites/crm.local/site_config.json` (không commit token thật):
```
CHATWOOT_URL=            (VD https://xxx.ngrok.io hoặc http://chatwoot nội bộ)
CHATWOOT_ACCOUNT_ID=
CHATWOOT_API_TOKEN=
CHATWOOT_WEBHOOK_SECRET=change-me  (đổi chuỗi mạnh khi live)
```

## Cổng "nối thật"
Nhắn inbox 1 tin có số `0912...` → ~10 giây sau có đúng 1 CRM Lead (source `Chatwoot`).
Nhắn lại cùng số → không tạo lead thứ hai.
Contact Chatwoot có custom attribute `frappe_lead` = mã CRM Lead (ghi ngược best-effort).
