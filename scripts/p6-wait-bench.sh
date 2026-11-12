#!/bin/bash
export PATH="/home/frappe/.local/bin:$PATH"
for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 3 http://127.0.0.1:8000/login || true)
  echo "try $i $code"
  if [ "$code" = "200" ]; then
    exit 0
  fi
  sleep 2
done
exit 1
