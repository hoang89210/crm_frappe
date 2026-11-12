# Gọi SIM — app Android (Phase 4B)

Clone PWA `/call`. Cùng API Frappe. Không FCM.

## Cài APK debug
File: `app-debug.apk` (hoặc `Test/callbridge-debug.apk`).

1. Điện thoại: bật **Tùy chọn nhà phát triển** → **USB debugging**. Cho phép nguồn không rõ.
2. Cùng WiFi với PC. Frappe URL = `http://<IP-LAN-Windows>:8000` (không dùng `127.0.0.1`).
3. `adb install -r app-debug.apk`
4. Login `sale1@crm.local` / `Sale1#crm2026` → Bắt đầu nghe lệnh gọi.
5. Trên CRM bấm **Gọi SIM** → app hiện SĐT → **GỌI NGAY** → chọn kết quả.

Build lại:
```
cd android/callbridge
gradlew.bat assembleDebug
```
APK: `app/build/outputs/apk/debug/app-debug.apk`

Cần `JAVA_HOME` (JDK 17) và `ANDROID_HOME=C:\Android\sdk`.
