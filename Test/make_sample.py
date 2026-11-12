import openpyxl

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Leads"

headers = ["first_name", "mobile_no", "source", "custom_source_detail", "custom_external_id"]
ws.append(headers)

rows = [
    ["Nguyen Van An", "0912345671", "Website", "Facebook page", "xlsx-001"],
    ["Tran Thi Binh", "0987654321", "Website", "Form dang ky", "xlsx-002"],
    ["Le Van Cuong", "+84 912 345 672", "Website", "File import", "xlsx-003"],
    ["Pham Thi Dao", "0901.111.222", "Website", "Hotline", "xlsx-004"],
    ["Hoang Van Em", "84933334444", "Website", "Event", "xlsx-005"],
    ["Vu Thi Phuong", "0978123456", "Facebook", "Comment page", "xlsx-006"],
    ["Dang Van Giang", "0888999000", "Website", "Landing", "xlsx-007"],
    ["Bui Thi Hoa", "0912000000", "Website", "Excel test", "xlsx-008"],
]
for r in rows:
    ws.append(r)

for col in ws.columns:
    max_len = max(len(str(c.value or "")) for c in col)
    ws.column_dimensions[col[0].column_letter].width = min(max_len + 2, 30)

out = r"C:\Users\Dien\Desktop\CRM_Frappe\Test\sample_leads.xlsx"
wb.save(out)
print("saved:", out, "| rows:", ws.max_row - 1)
