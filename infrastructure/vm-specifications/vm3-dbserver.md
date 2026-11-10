# VM 3: Database Server (PostgreSQL 18.x Server)

## Overview
- **Role:** Dedicated database engine for synthetic financial data and security controls.
- **Operating System:** Debian 12 / Ubuntu 24.04 LTS.
- **Assigned Subnet:** `DB-NET` only (`192.168.200.0/24`).
- **Security Rule:** No direct route or interface to `AUDIT-NET`.

## VirtualBox Specifications
- **Virtual CPU:** 2 vCPUs.
- **Memory (RAM):** 2048 MB (2 GB).
- **Storage:** 40 GB VDI.
- **Network Adapter 1:** Host-Only Adapter (`DB-NET`).
  - IP Address: `192.168.200.30`
  - Subnet Mask: `255.255.255.0`
  - Default Gateway: None.

## PostgreSQL 18.x Installation & Configuration
- **Package:** PostgreSQL 18.x.
- **Service Port:** 5432.
- **Configuration Files:**
  - `/etc/postgresql/18/main/postgresql.conf`
  - `/etc/postgresql/18/main/pg_hba.conf`
- **Security Hardening:**
  - TLS enabled (`ssl = on`).
  - Strict host-based access control (`pg_hba.conf`).
  - In secured mode, listener binds only to `192.168.200.30`.

