---
title: uptime
---

# uptime-kuma

A fancy self-hosted monitoring tool  
<https://github.com/louislam/uptime-kuma>

## Podman

As root:

```bash
adduser uptimekuma
systemctl --user enable --now podman.socket
loginctl enable-linger <uptimekumauser>
```

As user:

```bash
podman auto-update
systemctl --user status podman-auto-update.{service,timer}
systemctl --user restart podman-uptimekuma.service
# check service unit: .config/systemd/user/podman-uptimekuma.service
podman run -d --replace --restart=always -p 3001:3001 -v uptime-kuma:/app/data --name uptime-kuma louislam/uptime-kuma:1
```
