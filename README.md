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

Chi tiết từng giai đoạn: `Test/ghi-chu-phat-trien.md`.
