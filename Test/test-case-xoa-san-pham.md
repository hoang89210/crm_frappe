# Test case thủ công – Xóa sản phẩm / Combo (màn Hàng hóa)

## 1. Chuẩn bị
- Mở `/crm/hang-hoa`, đăng nhập bằng `Administrator` / `admin`.
- Dữ liệu test đã được script tự động tạo sẵn (giữ lại):
  - `TMP-UI-01` – sản phẩm lẻ
  - `TMP-UI-02` – sản phẩm lẻ (nằm trong combo)
  - `TMP-UI-COMBO` – combo chứa `TMP-UI-01` + `TMP-UI-02`
- Danh mục: `Nhóm test xóa`.
- Log tự động: `/tmp/p6-delete-test-*.log`
- Chạy lại script tự động khi cần:
  ```
  wsl -u frappe bash -lc 'cd /home/frappe/frappe-bench && bench --site crm.local execute pushesale._p6_delete_test.run'
  ```

## 2. Các bước test

### Case 1 – Xóa sản phẩm lẻ không nằm trong combo
1. Bấm **Thêm sản phẩm**, tạo nhanh `TMP-UI-03` (Lẻ, danh mục `Nhóm test xóa`) → **Lưu sản phẩm**.
2. Mở `TMP-UI-03` → bấm **Xóa**.
3. Hộp thoại `Xóa TMP-UI-03?` → bấm **OK**.
4. **Kết quả mong đợi:**
   - Thông báo `Đã xóa sản phẩm.`
   - Bảng tự tải lại, sản phẩm không còn.
   - F5 lại trang: sản phẩm vẫn không còn.

### Case 2 – Xóa sản phẩm lẻ đang nằm trong combo (không gỡ)
1. Mở `TMP-UI-01` → bấm **Xóa** → OK.
2. **Kết quả mong đợi:**
   - Hiện cảnh báo: `Đang trong combo: TMP-UI-COMBO. Gỡ khỏi combo rồi xóa?`
   - Bấm **Cancel** → sản phẩm vẫn còn.
   - Bấm **OK** → hệ thống gỡ khỏi combo rồi xóa sản phẩm.
   - Mở `TMP-UI-COMBO`: dòng `TMP-UI-01` đã mất, combo vẫn còn `TMP-UI-02`.

### Case 3 – Xóa sản phẩm lẻ trong combo (đồng ý gỡ)
1. (Tiếp Case 2) bấm **OK** ở cảnh báo gỡ combo.
2. **Kết quả mong đợi:**
   - `TMP-UI-01` biến mất khỏi danh sách.
   - Không còn dòng `Product Combo Line` trỏ tới `TMP-UI-01`.
   - Combo `TMP-UI-COMBO` **vẫn tồn tại**.

### Case 4 – Xóa Combo (phải cảnh báo, nhưng vẫn cho xóa)
1. Mở `TMP-UI-COMBO` → bấm **Xóa**.
2. Hộp thoại `Xóa TMP-UI-COMBO?` → **OK**.
3. **Kết quả mong đợi:**
   - Hiện cảnh báo: `Combo này chứa N sản phẩm lẻ. Bạn có chắc muốn xóa?`
   - Bấm **Cancel** → combo vẫn còn.
   - Bấm **OK** → combo bị xóa.
   - Các sản phẩm lẻ bên trong combo (`TMP-UI-02`) **vẫn còn**.
   - Không còn dòng `Product Combo Line` nào của combo.

### Case 5 – Reload sau khi xóa
1. F5 trang Hàng hóa.
2. **Kết quả mong đợi:**
   - Không còn sản phẩm/combo đã xóa.
   - Không có lỗi đỏ trên banner.
   - Cột `Tồn` vẫn hiển thị bình thường.

### Case 6 – Sales User (phân quyền)
1. Đăng xuất, đăng nhập `sale1@crm.local` / `Sale1#crm2026`.
2. Mở `/crm/hang-hoa` → xóa một SP test.
3. **Kết quả mong đợi:** xóa được (Sales User có quyền delete).

## 3. Kiểm tra dữ liệu sau test
- Vào `/crm/hang-hoa`, xác nhận:
  - `TMP-UI-01`, `TMP-UI-02`, `TMP-UI-COMBO` biến mất sau khi xóa.
  - Danh mục `Nhóm test xóa` vẫn còn (xóa danh mục thủ công nếu muốn).
- Kiểm tra log script: mở file `/tmp/p6-delete-test-*.log` xem đầy đủ request/response.

## 4. Tiêu chí Pass
- Tất cả 6 case đúng kết quả mong đợi.
- Không có `Internal Server Error`.
- Thông báo lỗi/cảnh báo bằng tiếng Việt, đúng ngữ cảnh.
