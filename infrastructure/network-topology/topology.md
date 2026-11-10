# VirtualBox Laboratory Network Topology

## 1. Network Architecture Diagram

```
+-------------------------------------------------------------------------------+
|                            VIRTUALBOX LABORATORY                              |
|                                                                               |
|   +-------------------+                     +-----------------------------+   |
|   |      VM 1         |                     |            VM 2             |   |
|   |   Kali Linux      |      AUDIT-NET      |     Application Server      |   |
|   |  (Audit Client)   |<===================>|  React (5173) / API (8000)  |   |
|   |  192.168.100.10   |   192.168.100.0/24  |        192.168.100.20       |   |
|   +-------------------+                     +--------------+--------------+   |
|                                                            |                  |
|                                                            | DB-NET           |
|                                                            | 192.168.200.0/24 |
|                                                            v                  |
|                                             +-----------------------------+   |
|                                             |            VM 3             |   |
|                                             |       Database Server       |   |
|                                             |      PostgreSQL 18.x        |   |
|                                             |       192.168.200.30        |   |
|                                             +-----------------------------+   |
+-------------------------------------------------------------------------------+
```

## 2. IP Addressing Table

| Node | Hostname | Interface | IP Address | Subnet Mask | Connected Network |
|---|---|---|---|---|---|
| VM 1 | `borsa-audit` | `eth0` | `192.168.100.10` | `255.255.255.0` | `AUDIT-NET` |
| VM 2 | `borsa-app` | `eth0` | `192.168.100.20` | `255.255.255.0` | `AUDIT-NET` |
| VM 2 | `borsa-app` | `eth1` | `192.168.200.20` | `255.255.255.0` | `DB-NET` |
| VM 3 | `borsa-db` | `eth0` | `192.168.200.30` | `255.255.255.0` | `DB-NET` |

## 3. VirtualBox Host-Only Network Setup
Create two Host-Only network adapters in VirtualBox Virtual Media / Network Manager:

1. **vboxnet0 (`AUDIT-NET`):**
   - IPv4 Address: `192.168.100.1`
   - Network Mask: `255.255.255.0`
   - DHCP Server: Disabled (use static IPs).

2. **vboxnet1 (`DB-NET`):**
   - IPv4 Address: `192.168.200.1`
   - Network Mask: `255.255.255.0`
   - DHCP Server: Disabled.

## 4. Network Isolation Verification
From VM 1 (Kali):
```bash
# Succeeded: Reach App Server frontend / API
ping -c 2 192.168.100.20
curl http://192.168.100.20:8000/api/health

# Must FAIL in Secured Configuration: Database Server must NOT be directly reachable from Kali
ping -c 2 192.168.200.30
nc -zv -w 2 192.168.200.30 5432
```

