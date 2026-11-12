# Demo Notes — CRM + Gọi SIM + Kênh

**Ngày demo**: 24/10/2026 (cập nhật tunnel 06/11/2026)
**Tunnel URL**: https://diesel-consequences-shaft-sessions.trycloudflare.com
**File URL mới**: `Test/tunnel-url.txt` (đổi mỗi lần Quick Tunnel restart)
**Trạng thái**: Demo xong. Quick Tunnel + Task Scheduler logon. Named Tunnel service tắt (Manual).


---

## 1. Chức năng cần có — Xem lại phần FB API

- Đồng bộ comment Facebook (Graph `/feed?fields=comments`)
- Xử lý comment có nhiều SĐT → tạo nhiều lead
- Bỏ qua comment không có SĐT Việt Nam hợp lệ
- Webhook Meta (GET `hub.challenge` + POST chữ ký `X-Hub-Signature-256`)
- Cần: Meta App Secret, Verify Token, Page Access Token, tunnel HTTPS ổn định
- Ghi log debug khi comment không có số

## 2. API với GHTK, VnPost

- Tích hợp API tạo đơn Giao Hàng Tiết Kiệm (GHTK)
- Tích hợp API Vietnam Post
- Mapping từ CRM Lead/Deal → đơn hàng
- Cập nhật trạng thái đơn (đang giao, hoàn, hủy)
- Lưu tracking code vào CRM
- Ghi log lỗi khi gọi API giao vận

## 3. Build danh mục sản phẩm

Đã có v1 (06/11/2026), Desk `/app/crm-product` và `/app/product-category`:

- [x] Dùng CRM Product sẵn có (SKU `product_code`, tên, giá, ảnh, mô tả)
- [x] Cây danh mục `Product Category`: Mỹ phẩm (Son môi, Kem dưỡng), Thực phẩm (Bánh, Trà)
- [x] Custom field: danh mục, đơn vị, khối lượng kg, dài/rộng/cao, mô tả ngắn
- [x] 6 sản phẩm mẫu: SON-DO, SON-NUDE, KEM-AM, KEM-CN, BANH-QY, TRA-XANH
- [x] Gắn sản phẩm vào Lead (tab Products). Deal dùng cùng child table CRM Products
- [ ] Giá theo khách / vùng
- [ ] Tồn kho
- [ ] GHTK (chưa code)

---

## Hướng triển khai tiếp (3 hướng tạm thời)

### Hướng A — Ưu tiên Facebook + Lead (nhanh nhất)
- Hoàn thiện FB comment → Lead (Phase 3 thực tế)
- Bổ sung FB Messenger inbox (nếu khách cần)
- Nối Chatwoot thật (Docker + webhook secret)
- Ưu điểm: Lead tự động, ít code mới
- Nhược điểm: Phụ thuộc Meta policy + tunnel HTTPS

### Hướng B — Ưu tiên Giao vận + Đơn hàng
- API GHTK + VnPost
- Tạo đơn từ CRM Lead/Deal
- Tracking + trạng thái đơn
- Ưu điểm: Giải quyết đau điểm vận hành ngay
- Nhược điểm: Cần dữ liệu đơn hàng + mapping phức tạp hơn

### Hướng C — Ưu tiên Sản phẩm + Bán hàng
- Danh mục sản phẩm + giá
- Tồn kho (nếu cần)
- Gắn sản phẩm vào Deal → tạo đơn
- Ưu điểm: Nền tảng cho bán hàng sau này
- Nhược điểm: Scope lớn, cần thời gian

**Ghi chú**: Khách chọn 1 hướng để tập trung trước. Có thể làm song song nếu nguồn lực cho phép.

---

## Các mục khác cần lưu ý (nếu có)

- Pipeline sale tiếng Việt (đã có plan, chưa làm)
- Round-robin phân phối lead (B1/B2)
- APK Kotlin nâng cấp (FCM, chạy nền)
- Pipeline sale (file Word demo)
