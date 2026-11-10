# VM 1: Audit Workstation (Kali Linux)

## Overview
- **Role:** Security assessment, authorized penetration testing, vulnerability verification.
- **Operating System:** Kali Linux 2024.x / Rolling.
- **Assigned Subnet:** `AUDIT-NET` only (`192.168.100.0/24`).

## VirtualBox Specifications
- **Virtual CPU:** 2 vCPUs.
- **Memory (RAM):** 4096 MB (4 GB).
- **Storage:** 60 GB VDI (Dynamically allocated).
- **Network Adapter 1:** Host-Only Adapter (`AUDIT-NET`).
  - IP Address: `192.168.100.10`
  - Subnet Mask: `255.255.255.0`
  - Default Gateway: None (isolated network) or controlled laboratory router.

## Installed Tooling
- **Reconnaissance & Port Scanning:** `nmap`, `masscan`.
- **Web Application Assessment:** Burp Suite Community / Professional, OWASP ZAP.
- **SQL Injection Verification:** `sqlmap`.
- **Database Client:** `postgresql-client` (`psql`).
- **HTTP Testing:** `curl`, `httpie`, Python `requests` / `httpx`.

## Configuration Commands
```bash
# Set static IP on AUDIT-NET interface (e.g. eth0)
sudo ip addr add 192.168.100.10/24 dev eth0
sudo ip link set eth0 up

# Verify connectivity to Application Server
ping -c 3 192.168.100.20
```

