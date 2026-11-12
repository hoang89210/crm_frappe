#!/bin/bash
echo "== tunnel =="
pgrep -a cloudflared || echo NO_CLOUDFLARED
url=$(head -1 /mnt/c/Users/Dien/Desktop/CRM_Frappe/Test/tunnel-url.txt)
echo "url=$url"
echo "== check =="
for p in /login /crm; do
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 20 "$url$p")
  echo "$p => $code"
done
jar=/tmp/p6c.txt
rm -f "$jar"
curl -s -c "$jar" --max-time 20 -X POST "$url/api/method/login" -d "usr=Administrator&pwd=admin" -o /dev/null -w "login=>%{http_code}\n"
for p in /crm /crm/hang-hoa /crm/kho /crm/kenh; do
  code=$(curl -s -b "$jar" -o /dev/null -w "%{http_code}" --max-time 20 "$url$p")
  echo "$p => $code"
done
