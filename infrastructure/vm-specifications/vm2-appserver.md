# VM 2: Application Server (Dual-Homed Linux)

## Overview
- **Role:** Hosts FastAPI backend, serves React frontend, authenticates sessions, bridges networks.
- **Operating System:** Debian 12 / Ubuntu 24.04 LTS.
- **Assigned Subnets:** Dual-homed on both `AUDIT-NET` and `DB-NET`.

## VirtualBox Specifications
- **Virtual CPU:** 2 vCPUs.
- **Memory (RAM):** 2048 MB (2 GB).
- **Storage:** 40 GB VDI.
- **Network Adapter 1:** Host-Only Adapter (`AUDIT-NET`).
  - IP Address: `192.168.100.20`
  - Subnet Mask: `255.255.255.0`
- **Network Adapter 2:** Host-Only Adapter (`DB-NET`).
  - IP Address: `192.168.200.20`
  - Subnet Mask: `255.255.255.0`

## Software Stack
- **Python:** 3.11+
- **Node.js:** v20+ / pnpm
- **ASGI Server:** Uvicorn with FastAPI
- **Web Server / Reverse Proxy:** Nginx (optional in front of Uvicorn / Vite build)
- **Firewall:** iptables / ufw configured strictly.

## Systemd Service Configuration
`/etc/systemd/system/borsa-backend.service`:
```ini
[Unit]
Description=Borsa Financial Backend Service
After=network.target

[Service]
User=borsa
WorkingDirectory=/opt/borsa/application/backend
EnvironmentFile=/opt/borsa/application/backend/.env
ExecStart=/opt/borsa/application/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

