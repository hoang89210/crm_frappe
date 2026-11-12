# Kịch bản demo CRM + Gọi SIM

Môi trường demo nội bộ. Chưa nối Chatwoot / Facebook thật.

## Địa chỉ (Quick Tunnel — URL đổi mỗi lần restart)

URL hiện tại (cập nhật 06/11/2026): **https://diesel-consequences-shaft-sessions.trycloudflare.com**

File luôn mới nhất: `Test/tunnel-url.txt`

- CRM: https://diesel-consequences-shaft-sessions.trycloudflare.com/crm
- Login: https://diesel-consequences-shaft-sessions.trycloudflare.com/login
- Kênh: https://diesel-consequences-shaft-sessions.trycloudflare.com/kenh
- Gọi SIM (điện thoại, Chrome): https://diesel-consequences-shaft-sessions.trycloudflare.com/call
- App Android: cài `callbridge-debug.apk` — điền cùng URL tunnel (không dùng `127.0.0.1`)

Điện thoại không cần cùng WiFi nếu dùng tunnel HTTPS.

## Tài khoản demo
| Vai trò | Email | Mật khẩu |
|---|---|---|
| Admin | Administrator | admin |
| Sale 1 | sale1@crm.local | Sale1#crm2026 |
| Sale 2 | sale2@crm.local | Sale2#crm2026 |

## 1. Xem lead trên CRM (máy tính)
1. Mở CRM, đăng nhập **Administrator**.
2. Vào danh sách Lead. Có tên, SĐT, nguồn, trạng thái chăm sóc.
3. Đăng xuất. Đăng nhập **sale1**. Sale 1 chỉ thấy lead của mình (sale 2 không thấy).

## 2. Gắn máy gọi SIM
**Cách A — Chrome trên điện thoại**
1. Mở https://diesel-consequences-shaft-sessions.trycloudflare.com/call
2. Địa chỉ Frappe: `https://diesel-consequences-shaft-sessions.trycloudflare.com`
3. Email / mật khẩu Sale 1, tên máy ví dụ `Dien thoai Sale1`
4. Đăng nhập & gắn máy → **Bắt đầu nghe lệnh gọi**

**Cách B — App APK**
1. Cài `callbridge-debug.apk` (cho phép nguồn không rõ).
2. Cùng form login như trên. Để app mở, màn hình sáng.

## 3. Một vòng gọi (cổng chính)
1. Máy tính: CRM bằng **sale1**, mở 1 lead có số điện thoại.
2. Bấm **Gọi SIM**.
3. Trong 3 giây điện thoại hiện tên + SĐT.
4. Bấm **GỌI NGAY** → bàn phím gọi đúng số.
5. Quay lại app, chọn **Hẹn gọi lại**, nhập giờ hẹn, gửi.
6. Máy tính: lead đổi trạng thái **Hẹn gọi lại**, có dòng Call Log.

Job hết hạn 3 phút nếu không nhận. Bấm Gọi SIM lại nếu cần.

## 4. Việc chưa demo hôm nay
- Inbox Chatwoot / comment Facebook đổ lead tự động: code có, chưa nối kênh thật.
- App không ghi âm, không gọi câm (chỉ mở bàn phím SIM).

## Checklist trước khi khách vào
- [x] Bench + Quick Tunnel auto (Task `CRM-Demo-Start` lúc logon)
- [x] `/login` `/call` `/kenh` qua tunnel = 200
- [ ] App đã login Sale 1 và đang **nghe lệnh gọi**
- [ ] 1 vòng Gọi SIM → Hẹn gọi lại thành công
