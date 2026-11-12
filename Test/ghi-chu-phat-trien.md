# CRM Frappe + Chatwoot thay Pushsale

## Status
- **Phase 0 DONE**: WSL Ubuntu, bench, site `crm.local` (Frappe v15.122 + CRM **v1.85.1** + pushesale), MariaDB + Redis, `bench start` chạy ở `http://127.0.0.1:8000` (login Administrator/admin, vào `/crm`).
- **Phase 1 DONE**: `bench --site crm.local run-tests --app pushesale` → **20/20 OK**.

## Phase 1 có gì (app `pushesale`)
- 12 custom field trên `CRM Lead` (fixtures): `custom_phone_e164`, `custom_external_id`, `custom_chatwoot_*`, `custom_source_detail`, `custom_team`, `custom_care_status` (Mới/Đang chăm/Cần chăm tiếp/Hẹn gọi lại/Chốt/Churn/Không nghe nhiều), `custom_care_count`, `custom_last_call_result`, `custom_next_followup`, `custom_assigned_device`, `custom_raw_text`.
- DocType mới (module `Call Bridge`): `Call Device`, `Call Job`, `Call Log` (khác `CRM Call Log` có sẵn của CRM — không đụng Twilio/Exotel).
- `phone.py`: chuẩn hóa + bóc SĐT VN (có test 4 case plan + thêm).
- `upsert_lead`: chống trùng theo `external_id → phone_e164 → chatwoot_contact_id`; không ghi đè care status; tự tạo `CRM Lead Source` nếu thiếu.
- `import_leads.py` + `sample_leads.csv` (3 dòng): import lần 2 merge, không tạo trùng.
- Roles `Marketing`, `Bridge` (tạo ở after_install); `Sales User/Manager` dùng sẵn của Frappe.
- Row-level: Sales chỉ thấy device/job/log của mình; Marketing không thấy Call Log; lead dùng quyền gốc CRM.

## Giả định đã chốt (đọc trước khi hỏi)
1. CRM pin **v1.85.1** (nhánh `develop` đòi Frappe v17 + `automation_engine`, không cài được lên v15).
2. **Không override** permission `CRM Lead` của CRM (`lead_owner` + org hierarchy đã đủ gate A/B). `custom_team` để sẵn, chưa làm cây team.
3. `ket_qua = Thue bao` plan không định nghĩa → xử như `Cần chăm tiếp`, hẹn +1 ngày.
4. `ket_qua` Select để default rỗng (Frappe mặc định option đầu tiên → từng gây hook chạy sớm với `Khong nghe`).
5. Test cách ly dùng `frappe.get_list`/`frappe.client.get` (`frappe.get_all` và `frappe.get_doc` server-side **không** check row-level theo thiết kế).
6. List view CRM (Vue SPA): cột care status/số lần chăm bật trong Columns của từng view; filter `custom_next_followup < now` dùng được ngay.

## Chạy
Trong WSL user `frappe`, thư mục `~/frappe-bench`:
- `bench start` → mở `http://127.0.0.1:8000/crm`
- `bench --site crm.local run-tests --app pushesale`
- `bench --site crm.local execute pushesale.import_leads.run_import`

Secrets trong `sites/crm.local/site_config.json` (không commit token thật).
Code Phase 1 trong `~/frappe-bench/apps/pushesale` (đã commit git trong app).
Script dựng lại từng bước: `scripts/p0-*.sh`, `scripts/p1-*.sh` (chạy bằng `wsl sudo -u frappe bash ...`).

## Phase 2 DONE (Chatwoot webhook)
- `POST /api/method/pushesale.api.chatwoot.webhook?secret=...` — check secret `hmac.compare_digest`, chỉ nhận `message_created` incoming + `conversation_created`, bóc SĐT từ contact hoặc nội dung, `upsert_lead` (source `Chatwoot`).
- Ghi ngược `frappe_lead` vào Chatwoot contact (best-effort, cần `CHATWOOT_URL` + token).
- `run-tests`: **27/27 OK**. Live HTTP: tạo lead → gửi lại trùng lead → sai secret 403.
- Còn thiếu để nối Chatwoot thật: Chatwoot URL + Account ID + API token, Docker Chatwoot, tunnel HTTPS. Nút "Mở Chatwoot" trên form CRM dời lại (cần sửa frontend app `crm`).

## Phase 4A DONE (gọi SIM: Frappe API + nút Gọi + PWA)
- API: `register_device` / `create_job` (Sales-only) / `poll` / `disposition` / `skip_job` (device_token, guest). Job hết hạn 3 phút. `disposition` tạo Call Log → hook đổi care status; `skip_job` đóng Expired không tạo log.
- Nút **Gọi SIM** trên form CRM Lead (patch `apps/crm/frontend/src/pages/Lead.vue`, đã rebuild bundle; patch lại bằng `scripts/patch-lead-vue.py` khi pull CRM mới). Ẩn với role Marketing (frontend + backend).
- PWA: `http://127.0.0.1:8000/call` — nhập URL + device_token, poll 3s, nút `tel:` mở dialer, 7 nút kết quả + Bỏ qua.
- `run-tests`: **36/36 OK**. Live HTTP: login → đăng ký `May Live` → `CALL-JOB-2026-00001` → poll Delivered → `Hẹn gọi lại` + hẹn 08/10 15:00 (`CALL-LOG-2026-00001`).
- File test live trong `Test/` (`live-*.json`, `chatwoot-live-payload.json`).

## Chuyển lead sang Sale khác (A DONE)
- API `pushesale.api.assign.reassign_lead` (Manager-only): theo mã lead hoặc SĐT, chủ mới phải là Sales, ghi comment, cắt ToDo + share chủ cũ.
- Thứ tự bắt buộc: cancel ToDo chủ cũ trước, gán owner sau (CRM mirror assignment <-> owner).
- Test 43/43 OK (gồm: sale cũ mất quyền gọi, sale mới gọi được, sale không được chuyển, trùng SĐT phải chỉ rõ lead).
- Cơ chế tái phân phối hàng loạt: `Test/suggest-tai-phan-phoi-lead.md` (B1 round-robin, B2 nút Manager, B3 không làm).

## Phase 2 bổ sung + Phase 3 DONE (08/10)
- Màn `http://127.0.0.1:8000/kenh`: dán Chatwoot URL/token và Facebook page + Page Access Token.
- Chatwoot: kiểm tra kết nối, đồng bộ inbox, hiện URL webhook. Webhook cũ giữ nguyên.
- Facebook comment: Graph sync (nút + mỗi 10 phút), bóc SĐT VN → CRM Lead. Không SĐT thì bỏ.
- `run-tests --app pushesale` → **64/64 OK**.

## Phase 4B DONE (app Android Kotlin)
- `android/callbridge`: clone PWA `/call`, poll 3s, `ACTION_DIAL`, 7 nút kết quả. `assembleDebug` OK.
- APK: `android/callbridge/app-debug.apk` / `Test/callbridge-debug.apk`. Cài: `adb install -r`. URL Frappe = IP LAN Windows, không `127.0.0.1`.

## Tiếp theo (chưa làm)
- Nối Chatwoot thật: bật Docker + dán webhook từ `/kenh` (`Test/bo-sung-phase-chatwoot.md`).
- Webhook Meta realtime: App Secret + tunnel HTTPS (code đã có, chưa live).
- Pipeline sale tiếng Việt kiểu Pushsale: để sau.
