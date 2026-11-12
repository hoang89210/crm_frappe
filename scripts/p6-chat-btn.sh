#!/bin/bash
set -e
export PATH="/home/frappe/.local/bin:$PATH"
python3 -c "p=open('/mnt/c/Users/Dien/Desktop/CRM_Frappe/scripts/p6-inject-open-chat.py','rb').read().replace(b'\r\n',b'\n'); open('/tmp/p6-inject-open-chat.py','wb').write(p)"
python3 -c "p=open('/mnt/c/Users/Dien/Desktop/CRM_Frappe/scripts/p6-patch-chat-btn.py','rb').read().replace(b'\r\n',b'\n'); open('/tmp/p6-patch-chat-btn.py','wb').write(p)"
python3 /tmp/p6-inject-open-chat.py
python3 /tmp/p6-patch-chat-btn.py
cd /home/frappe/frappe-bench
bench build --app crm
echo CHAT_BTN_DONE
