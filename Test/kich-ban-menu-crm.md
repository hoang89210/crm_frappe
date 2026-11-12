# Test menu CRM — Kênh + Hàng hóa

URL: https://joining-listprice-argument-mitchell.trycloudflare.com
Login: Administrator / admin

Ctrl+F5 trước khi test (PWA cache).

## 1. Menu không rời CRM
1. Mở https://joining-listprice-argument-mitchell.trycloudflare.com/crm/leads/view/list
2. Menu trái phải còn: Leads, Kênh, Hàng hóa, Deals.
3. Bấm **Hàng hóa**. URL phải thành `/crm/hang-hoa`. Sidebar vẫn còn.
4. Bấm **Kênh**. URL phải thành `/crm/kenh`. Sidebar vẫn còn.
5. Bấm **Leads**. Về list lead. Không bị trắng trang.

## 2. Hàng hóa
1. Trái thấy Mỹ phẩm, Son môi, Kem dưỡng, Thực phẩm, Bánh, Trà.
2. Bấm **Son môi** → bảng còn SON-DO, SON-NUDE.
3. Bấm **Tất cả** → thấy cả 6 sản phẩm mẫu.
4. Thêm danh mục con (tùy chọn): tên `Test nhóm`, cha Mỹ phẩm, không tick Là nhóm, Lưu.
5. Thêm sản phẩm: mã `TEST-01`, tên `Hàng test`, danh mục Test nhóm, ĐVT cái, kg 0.1, giá 10000, Lưu. Bấm nhóm đó phải thấy TEST-01.

## 3. Kênh
1. Trang hiện form Chatwoot + Facebook (không màn login riêng).
2. Dòng trạng thái: Đã tải cấu hình (Admin). Sale thường có thể bị từ chối — đúng quyền.
3. Không cần bấm Đồng bộ nếu chưa có token. Chỉ cần form hiện và URL không nhảy ra `/kenh` hay `/app`.
