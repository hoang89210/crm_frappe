import os
import re
import subprocess
import time
from datetime import datetime, timedelta, timezone

log_path = "/tmp/cloudflared-quick.log"
url_path = "/mnt/c/Users/Dien/Desktop/CRM_Frappe/Test/tunnel-url.txt"
hist_path = "/mnt/c/Users/Dien/Desktop/CRM_Frappe/Test/tunnel-url-history.txt"
bin_path = "/home/frappe/.local/bin/cloudflared"

subprocess.call(["pkill", "-f", "cloudflared tunnel --url"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)

with open(log_path, "w") as logf:
    subprocess.Popen(
        [bin_path, "tunnel", "--url", "http://127.0.0.1:8000", "--no-autoupdate"],
        stdout=logf,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )

url = None
for _ in range(40):
    time.sleep(1)
    if not os.path.exists(log_path):
        continue
    txt = open(log_path, errors="ignore").read()
    if not url:
        m = re.search(r"https://[a-z0-9]+(?:-[a-z0-9]+)+\.trycloudflare\.com", txt)
        if m:
            url = m.group(0)
    if "Registered tunnel connection" in txt:
        break

if not url:
    print("NO_URL")
    raise SystemExit(1)

ts = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S")
line = "%s  %s" % (ts, url)

with open(url_path, "w") as f:
    f.write(url + "\n")
    f.write("time: " + ts + "\n")
    f.write("status: current\n")

old = ""
if os.path.exists(hist_path):
    old = open(hist_path, encoding="utf-8", errors="ignore").read()
with open(hist_path, "w", encoding="utf-8") as f:
    f.write(line + "\n")
    f.write(old)

print("TUNNEL_URL=" + url)
print("TUNNEL_TIME=" + ts)
