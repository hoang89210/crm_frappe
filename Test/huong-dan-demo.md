# Workflow demo nhanh (Local WSL + Quick Tunnel)

## 1. Khởi động hàng ngày

```powershell
powershell -ExecutionPolicy Bypass -File "C:\Users\Dien\Desktop\CRM_Frappe\scripts\start-demo.ps1"
```

Script chạy lần lượt:
1. Khởi động bench trong WSL (`start-bench-wsl.ps1`).
2. Tạo Cloudflare Quick Tunnel mới (`start-quick-tunnel.ps1`).
3. Kiểm tra toàn bộ (`check-after-reboot.ps1`).
4. In URL mới ra màn hình.

Lấy lại URL bất kỳ lúc nào:

```powershell
powershell -ExecutionPolicy Bypass -File "scripts\get-current-url.ps1"
```

URL được ghi tại `Test/tunnel-url.txt`, lịch sử ở `Test/tunnel-url-history.txt`.

## 2. Sửa code khi khách đang test

| Việc cần làm | Lệnh / cách làm |
|---|---|
| Sửa Python app (`catalog.py`, `stock.py`, ...) | Sửa file trong `pN_code/pushesale/...`, copy sang WSL, `bench --site crm.local clear-cache` |
| Sửa Vue (`HangHoa.vue`, `Kho.vue`, `Kenh.vue`) | Copy sang `apps/crm/frontend/src/pages/`, chạy `bench build --app crm`, khách Ctrl+F5 |
| Đổi quyền DocType (.json) | `bench --site crm.local migrate --skip-search-index` |
| Restart bench | `wsl -u frappe bash /tmp/p6-stop-bench.sh` rồi chạy lại `start-bench-wsl.ps1` |
| Restart tunnel | Chạy lại `start-quick-tunnel.ps1`, gửi URL mới cho khách |

Bench dev tự reload khi file Python thay đổi; nếu không thấy thay đổi thì restart bench.

## 3. Reset dữ liệu demo

```powershell
powershell -ExecutionPolicy Bypass -File "scripts\reset-demo-data.ps1"
```

Script sẽ:
- Xóa lead demo (`DEMO - ...`), phiếu kho `DEMO SEED`, sản phẩm/danh mục test `TMP-*`.
- Tạo lại danh mục, 8 sản phẩm, combo, tồn kho mẫu.
- Tạo 5 lead mẫu + 1 Facebook Page demo.
- Đảm bảo tài khoản sale1/2/3 tồn tại.

## 4. Backup trước/sau buổi demo

```powershell
powershell -ExecutionPolicy Bypass -File "scripts\backup-demo.ps1"
```

File backup (database + files) được copy về `Test/backups/<timestamp>/`.

## 5. Xử lý sự cố nhanh

| Hiện tượng | Cách xử lý |
|---|---|
| Không vào được link | Chạy `check-after-reboot.ps1`; nếu tunnel chết, chạy `start-quick-tunnel.ps1` lấy link mới |
| Bench không chạy | Chạy `start-bench-wsl.ps1`; kiểm tra `wsl -u frappe bash -lc "ss -lnt \| grep 8000"` |
| Trang trắng / thiếu file JS | `bench build --app crm` rồi Ctrl+F5 |
| Dữ liệu demo bị rối | Chạy `reset-demo-data.ps1` |
| Máy sleep mất kết nối | Đã tắt sleep khi cắm sạc (`powercfg /change standby-timeout-ac 0`) |
| Muốn tắt hibernate | Cần PowerShell Administrator: `powercfg /hibernate off` |

## 6. Lưu ý khi demo

- URL Quick Tunnel đổi mỗi lần restart → luôn gửi link mới nhất.
- Không sửa code trực tiếp trên VPS Docker khi đang demo; chỉ cập nhật khi đã test local.
- Trước buổi demo: chạy `reset-demo-data.ps1` + `check-after-reboot.ps1`.
