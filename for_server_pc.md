# Hướng dẫn Setup Máy Server (Windows) - Phương án B

## 1. Mục tiêu

Thiết lập **1 máy Windows cố định** làm server chạy đầy đủ hệ thống CRM Frappe, bao gồm:
- Frappe Bench + site `crm.local`
- Named Tunnel (URL cố định)
- Agent quản lý
- Backup định kỳ

Máy server này sẽ là nơi duy nhất cần bật để khách test demo.

## 2. Tại sao cần máy server cố định?

- Dễ quản lý lâu dài
- URL ổn định (Named Tunnel)
- Tự động chạy khi bật máy
- Dễ backup và bảo trì
- Chuẩn bị cho giai đoạn sau khi khách chốt (thêm domain)

## 3. Yêu cầu máy server

| Yêu cầu | Mô tả |
|--------|-------|
| Hệ điều hành | Windows 10/11 |
| RAM | Tối thiểu 8GB (khuyến nghị 16GB) |
| CPU | 4 core trở lên |
| Ổ cứng | 100GB+ trống |
| Kết nối | Internet ổn định |
| Quyền | Administrator |

## 4. Tổng quan các bước

1. Cài WSL + Ubuntu
2. Cài Frappe Bench
3. Clone repo `CRM_Frappe`
4. Restore site `crm.local`
5. Setup Named Tunnel + Windows Service
6. Tạo Agent quản lý
7. Cấu hình Backup
8. Chuyển từ máy hiện tại sang máy server

## 5. Chi tiết từng bước

### 5.1 Cài WSL + Ubuntu

Mở PowerShell (Administrator) và chạy:

```powershell
wsl --install
```

Sau khi cài xong, khởi động Ubuntu và cập nhật:

```bash
sudo apt update && sudo apt upgrade -y
```

### 5.2 Cài Frappe Bench

Tham khảo script `wsl-frappe-bench-init.sh` trong repo hoặc làm theo hướng dẫn chính thức của Frappe.

Yêu cầu:
- Python 3.10+
- Node.js 18+
- MariaDB + Redis

### 5.3 Clone repo CRM_Frappe

Trên máy server, chạy:

```bash
git clone https://github.com/hoang89210/crm_frappe.git
cd crm_frappe
```

### 5.4 Restore site crm.local

Sử dụng file backup đã tạo từ máy cũ (bằng script `backup-demo.ps1`):

```bash
bench --site crm.local restore <backup>.sql.gz \
  --with-public-files <files>.tar \
  --with-private-files <private>.tar
```

Sau đó chạy:

```bash
bench --site crm.local migrate
bench --site crm.local clear-cache
```

### 5.5 Setup Named Tunnel + Windows Service

1. Cài `cloudflared` trên Windows.
2. Login Cloudflare:

```bash
cloudflared tunnel login
```

3. Tạo tunnel:

```bash
cloudflared tunnel create crm-demo
```

4. Tạo file `config.yml` (ví dụ):

```yaml
tunnel: <Tunnel-ID>
credentials-file: C:\Users\Server\.cloudflared\<Tunnel-ID>.json

ingress:
  - hostname: crm-demo.trycloudflare.com
    service: http://localhost:8000
  - service: http_status:404
```

5. Cài Windows Service (tự động chạy khi khởi động):

```powershell
cloudflared service install
```

### 5.6 Tạo Agent quản lý

Tạo file PowerShell `agent.ps1` với các lệnh cơ bản:

```powershell
param(
    [string]$Action
)

switch ($Action) {
    "start"   { Start-Service cloudflared }
    "stop"    { Stop-Service cloudflared }
    "restart" { Restart-Service cloudflared }
    "status"  { Get-Service cloudflared }
    default   { Write-Host "Usage: .\agent.ps1 -Action start|stop|restart|status" }
}
```

Bạn có thể mở rộng agent sau này để quản lý cả bench.

### 5.7 Cấu hình Backup

Nên backup định kỳ các thứ sau:

- Token tunnel: `C:\Users\Server\.cloudflared\<Tunnel-ID>.json`
- File config: `config.yml`
- Dữ liệu site: Dùng script `backup-demo.ps1`

Lưu trữ backup ở nơi an toàn (USB, OneDrive, ổ cứng ngoài).

## 6. Quy trình chuyển từ máy hiện tại sang máy server

1. Dừng Quick Tunnel trên máy cũ.
2. Restore site `crm.local` trên máy server.
3. Chạy Named Tunnel trên máy server.
4. Cập nhật link mới gửi cho khách.
5. Dần chuyển toàn bộ hoạt động sang máy server.
6. Tắt máy cũ sau khi ổn định.

## 7. Lưu ý quan trọng

- Token tunnel (`<Tunnel-ID>.json`) là quan trọng nhất → phải backup.
- Máy server nên được cắm nguồn liên tục.
- Nên test kỹ trước khi gửi link mới cho khách.
- Khi khách chốt, có thể mua domain và trỏ DNS vào tunnel.

## 8. Checklist

- [ ] Máy server đã cài WSL + Ubuntu
- [ ] Đã cài Frappe Bench
- [ ] Đã clone repo `CRM_Frappe`
- [ ] Đã restore site `crm.local`
- [ ] Đã setup Named Tunnel
- [ ] Đã cài Windows Service cho tunnel
- [ ] Đã tạo Agent quản lý
- [ ] Đã cấu hình backup định kỳ
- [ ] Đã test truy cập qua URL cố định
- [ ] Đã backup token + config an toàn

## 9. Commit và Push file này lên Git

Sau khi tạo hoặc cập nhật file này, chạy:

```bash
git add for_server_pc.md
git commit -m "docs: add server PC setup guide (Plan B)"
git push
```

## 10. Lấy file này trên máy server

```bash
git clone https://github.com/hoang89210/crm_frappe.git
cd crm_frappe
```

---

**File đã được tạo thành công tại:** `for_server_pc.md`

Bạn có muốn commit và push file này lên Git ngay bây giờ không?