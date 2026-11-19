# CRM Frappe + Pushesale

CRM Frappe tích hợp Chatwoot, Facebook comment (nhiều Page), quản lý hàng hóa (danh mục cây + combo) và sổ kho.

## Tính năng
- Hàng hóa: danh mục nhiều cấp, combo giá riêng, import Excel
- Sổ kho: kho nhiều cấp, phiếu nhập/xuất/điều chuyển, tồn kho
- Facebook: nhiều Page, token riêng, đồng bộ comment thành Lead
- Chatwoot: cấu hình kết nối, đồng bộ inbox, nút Chat trên Lead
- Xóa sản phẩm/combo có cảnh báo

## Cấu trúc
- `p1_code` … `p6_code`: code app `pushesale` và frontend theo giai đoạn
- `android/`: app Android gọi SIM
- `scripts/`: script deploy, test, khởi động bench/tunnel
- `Test/`: test case và ghi chú phát triển chi tiết

## Chạy demo
```powershell
powershell -ExecutionPolicy Bypass -File "scripts\start-demo.ps1"
```

Lấy URL hiện tại: `scripts\get-current-url.ps1`
Reset dữ liệu demo: `scripts\reset-demo-data.ps1`
Backup: `scripts\backup-demo.ps1`

## Deploy demo Docker (gửi server / người quen)

```bash
git clone https://github.com/hoang89210/crm_frappe.git
cd crm_frappe/demo-docker
```

Hướng dẫn đầy đủ (tiếng Việt): **`demo-docker/HUONG_DAN_DEPLOY.md`**

Stack: Frappe CRM + pushesale (Hàng hóa/Kho/Kênh) + Chatwoot, **1 URL** qua nginx.

## Tài liệu
- `demo-docker/HUONG_DAN_DEPLOY.md`: deploy Docker cho người nhận server
- `Test/huong-dan-demo.md`: workflow demo + sửa code
- `Test/huong-dan-su-dung.pdf`: hướng dẫn cho khách test
- `docker/README.md`: template VPS Docker (tham khảo)

Chi tiết từng giai đoạn: `Test/ghi-chu-phat-trien.md`.
