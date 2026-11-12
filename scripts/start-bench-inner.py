import os
import subprocess
import time

os.chdir("/home/frappe/frappe-bench")
env = os.environ.copy()
env["PATH"] = "/home/frappe/.local/bin:/usr/local/bin:/usr/bin:/bin:" + env.get("PATH", "")

# already up?
try:
    out = subprocess.check_output(["ss", "-lntp"], text=True)
    if ":8000" in out:
        print("BENCH_ALREADY_UP")
        raise SystemExit(0)
except Exception:
    pass

with open("/tmp/bench-start.log", "w") as logf:
    p = subprocess.Popen(
        ["/home/frappe/.local/bin/bench", "start"],
        stdout=logf,
        stderr=subprocess.STDOUT,
        env=env,
        start_new_session=True,
    )
print("BENCH_PID=%d" % p.pid)
time.sleep(4)
print("LOG_SIZE=%d" % os.path.getsize("/tmp/bench-start.log"))
