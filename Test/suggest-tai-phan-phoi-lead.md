# Suggest: cơ chế tái phân phối lead_owner (chưa làm)

Ngày ghi: 07/10/2026. Đã có: chuyển lead thủ công `pushesale.api.assign.reassign_lead`
(Manager-only, theo mã lead hoặc SĐT, ghi comment, cắt quyền chủ cũ đúng thứ tự
cancel-ToDo-trước / gán-owner-sau vì CRM mirror assignment <-> owner).

## B1. Lead mới chưa có chủ — round-robin (đề xuất, mặc định TẮT)
- Khi áp dụng: `upsert_lead` tạo mới mà không có `owner` (Chatwoot inbox, import Excel).
- Pool: user role Sales User, `enabled=1`, có Call Device `active=1`.
- Chia vòng tròn theo thứ tự, bỏ qua Sale nghỉ (không có device active).
- Ghi comment "Auto-assign round-robin".
- Config: `site_config` `PUSHESALE_ROUND_ROBIN=0/1`. Mặc định 0 — bật khi Chatwoot live để inbox không dồn hết về Admin.
- Không đụng lead đã có chủ (kể cả Admin).

## B2. Nút Manager "Tái phân phối" (đề xuất)
- Nguồn chọn 1 trong 3: lead của Sale X / lead `Mới` quá N ngày / lead không owner.
- Đích: tick chọn list Sale (mặc định Sale có máy active).
- Chia đều round-robin, mỗi lead 1 comment "Redistribute …".
- Mặc định **loại trừ** lead `Chốt` / `Hẹn gọi lại` / `Không nghe nhiều`; có tick "gồm cả đang chăm" mới lấy.
- Chạy nền (job queue) nếu > 200 lead, báo số đã chuyển.

## B3. Không làm lúc này
- Cây team / territory, quota theo KPI.
- Tự cướp lead idle (dễ shock kiểu Pushsale, Sale phản đối).
- Chuyển cả lịch sử Call Log sang Sale mới (log giữ nguyên, chỉ đổi owner).

## Cổng khi làm B1/B2
- 10 lead mới không owner → chia đều 2 Sale (5/5).
- Lead `Chốt` không bị chuyển nhầm khi không tick.
- Test cũ 43 case vẫn xanh.
