# Run as Administrator
sc.exe stop cloudflared
sc.exe config cloudflared start= demand
sc.exe query cloudflared
