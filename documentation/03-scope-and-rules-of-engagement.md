# Scope and Rules of Engagement — Borsa Security Research Platform

> **Document Version:** 1.0  
> **Status:** Active — Must be read before any testing begins  
> **Classification:** Internal Research / Educational Use Only

---

## 1. Purpose

This document defines the authorized scope, rules of engagement, and operational constraints for all security research activities conducted within the Borsa laboratory environment. Every researcher must review and acknowledge this document before beginning any experimental work.

---

## 2. Lab Environment Boundary

All testing is **strictly limited** to the following VirtualBox virtual machines:

| VM | Hostname | IP Address(es) | Authorized Target |
|----|----------|----------------|-------------------|
| VM1 | `kali-audit` | `192.168.100.10` | No (attacker workstation) |
| VM2 | `app-server` | `192.168.100.20`, `192.168.200.20` | Yes |
| VM3 | `db-server` | `192.168.200.30` | Yes |

**Network Segments:**

| Network | CIDR | Purpose |
|---------|------|---------|
| AUDIT-NET | `192.168.100.0/24` | Attack/audit network |
| DB-NET | `192.168.200.0/24` | Database backend network |

> **⚠️ WARNING:** No scanning, probing, injection, or any other security testing technique described in this documentation may be directed at any IP address, hostname, domain, or service **outside** of the ranges listed above. The host machine's network adapters, home/office network, cloud services, and all internet-accessible systems are explicitly **out of scope and unauthorized**.

---

## 3. Authorized Activities

The following activities are explicitly authorized within the lab boundary:

### 3.1 Scenario 1 — SQL Injection Testing
- Crafting and submitting SQL injection payloads via HTTP requests to VM2 (port 8000 or 80)
- Using `sqlmap` against VM2's FastAPI endpoints
- Using Burp Suite to intercept and modify HTTP requests to VM2
- Reviewing PostgreSQL logs on VM3 for evidence of injected queries
- Testing all payload categories listed in `tests/security/sqli-test-payloads.md`

### 3.2 Scenario 2 — Privilege Escalation Testing
- Connecting to PostgreSQL on VM3 from VM2 using configured application roles
- Attempting DDL operations (DROP TABLE, CREATE TABLE) using `app_vulnerable` role
- Attempting DML operations outside intended scope using test roles
- Reviewing PostgreSQL audit logs for permission denial events
- Running `\dp`, `\du`, and privilege inspection queries from `psql`

### 3.3 Scenario 3 — Broken Authorization Testing
- Authenticating to the Borsa application and manipulating `account_id` parameters in API requests
- Testing whether account data belonging to synthetic test users is accessible across sessions
- Enabling and testing PostgreSQL Row-Level Security (RLS) policies
- Comparing API response bodies between authorized and unauthorized account access

### 3.4 Scenario 4 — Network Exposure Testing
- Running `nmap` scans from VM1 (Kali) targeting VM3's IP address (`192.168.200.30`)
- Attempting `psql` direct connections from VM1 to VM3 port 5432
- Modifying `pg_hba.conf` on VM3 (vulnerable and secure variants)
- Applying and verifying `iptables`/`ufw` firewall rules on VM2 and VM3
- Capturing and analyzing network traffic within the lab using Wireshark

---

## 4. Explicitly Unauthorized Activities

The following activities are **prohibited** under all circumstances:

| Prohibited Activity | Reason |
|--------------------|---------| 
| Scanning any IP outside `192.168.100.0/24` or `192.168.200.0/24` | Outside lab boundary |
| Using real personal or financial data | Privacy and legal compliance |
| Persistent backdoors or rootkits (beyond lab exercise scope) | Unnecessary risk |
| Denial-of-service attacks with intent to crash lab VMs permanently | Data loss risk |
| Sharing lab credentials, payloads, or exploits outside the research team | Security risk |
| Connecting lab VMs to external networks during active testing | Containment breach |
| Using production PostgreSQL instances or cloud databases | Outside scope |
| Testing tools or payloads not documented in the methodology | Uncontrolled experimentation |

---

## 5. Synthetic Data Requirements

All data used in the Borsa application **must be entirely synthetic**. The following requirements apply:

### 5.1 User Data
- All usernames, email addresses, and passwords are fictional
- Passwords in the database must be bcrypt-hashed (never plaintext)
- Use recognizably fake names (e.g., `alice_test`, `bob_test`, `charlie_test`)
- No real Social Security Numbers, national ID numbers, or government identifiers

### 5.2 Financial Data
- Account numbers, balances, and transaction data are entirely fabricated
- Use ranges that are clearly fictional (e.g., account numbers starting with `TEST-`)
- Transaction amounts and descriptions must not resemble real financial records

### 5.3 Data Generation
- Synthetic data is generated via the project's seed scripts
- Data generation scripts are located in `database/seed/`
- Minimum of 3 synthetic users with at least 2 accounts each is required for BOLA testing

---

## 6. Lab Isolation Requirements

### 6.1 Network Isolation
- VMs must be configured with **Host-Only** VirtualBox adapters only during active testing
- **NAT adapters** (for internet access) must be disabled before beginning any security scenario
- VirtualBox "Internal Network" adapters are acceptable for VM-to-VM communication
- Confirm isolation before each test session:

```bash
# On VM1 — verify no external routes
ip route show
ping -c 1 8.8.8.8  # Should FAIL if properly isolated

# Verify only lab IPs are reachable
ping -c 1 192.168.100.20  # Should succeed
ping -c 1 192.168.200.30  # Should FAIL (different network segment from VM1)
```

### 6.2 Physical Isolation
- The host machine should not be connected to untrusted networks during active penetration testing phases
- Lab sessions involving active exploitation should not be conducted on shared/public Wi-Fi

---

## 7. Snapshot Policy

Snapshots are **mandatory** to enable reproducible experiments and safe rollback.

### 7.1 Required Snapshots

| Snapshot Name | Description | When to Create |
|---------------|-------------|----------------|
| `baseline-clean` | Fresh VM with OS installed, no app | After OS install, before any config |
| `baseline-configured` | Networking configured, tools installed | After infrastructure setup complete |
| `vulnerable-mode` | Application deployed in vulnerable configuration | Before Scenario 1–4 vulnerable testing |
| `secure-mode` | All security controls applied | Before Scenario 1–4 secure testing |
| `post-scenario-N` | State after each scenario (optional) | After each experiment for reproducibility |

### 7.2 Snapshot Procedure

```bash
# Create a snapshot from VirtualBox CLI (host machine)
VBoxManage snapshot "vm-name" take "snapshot-name" --description "Description"

# List snapshots
VBoxManage snapshot "vm-name" list

# Restore a snapshot
VBoxManage snapshot "vm-name" restore "snapshot-name"
```

> **⚠️ WARNING:** Always create a `vulnerable-mode` snapshot **before** beginning exploitation testing. If a VM is damaged during testing, restore from snapshot rather than attempting manual repair.

---

## 8. Evidence Collection Guidelines

Evidence must be systematically collected to support research findings. All evidence files are stored in the `evidence/` directory, which is excluded from version control (see `.gitignore`).

### 8.1 Directory Structure

```
evidence/
├── scenario-1-sqli/
│   ├── vulnerable/
│   │   ├── sqlmap-output.txt
│   │   ├── burp-requests/
│   │   └── screenshots/
│   └── secure/
│       └── ...
├── scenario-2-privileges/
├── scenario-3-bola/
├── scenario-4-network/
└── chaining/
```

### 8.2 Evidence Types and Requirements

| Evidence Type | Required Format | Naming Convention |
|---------------|-----------------|-------------------|
| Terminal output | `.txt` file (copy/paste) | `YYYY-MM-DD_tool-name_description.txt` |
| HTTP requests/responses | Burp export or `.txt` | `YYYY-MM-DD_endpoint_variant.txt` |
| Screenshots | `.png` (1920×1080 preferred) | `YYYY-MM-DD_scenario_step.png` |
| PostgreSQL logs | `.log` file (excerpt) | `YYYY-MM-DD_pg_scenario.log` |
| `nmap` output | `-oN` and `-oX` formats | `YYYY-MM-DD_nmap_target.txt` |

### 8.3 Chain of Custody

For each piece of evidence:
1. Record the **date and time** of collection (UTC)
2. Record the **VM and user context** (which VM, which OS user, which DB role)
3. Record the **exact command(s)** used to generate the evidence
4. Note the **snapshot state** at the time of collection (vulnerable or secure variant)

---

## 9. Responsible Research Principles

This research is conducted under the following ethical principles:

1. **Minimum necessary access** — Use the lowest privilege level that permits the research objective to be tested
2. **No persistent harm** — Restore snapshots after destructive tests; do not leave the lab in a broken state
3. **Accurate reporting** — Report both successful attacks and failed attacks; do not omit negative results
4. **Bounded scope** — If a test technique would require going outside the authorized scope to demonstrate impact, document the theoretical extension rather than executing it
5. **Transparency** — All test tools, payloads, and techniques are pre-documented in methodology files before execution

---

## 10. Acknowledgment

Before beginning security testing, all researchers must confirm:

- [ ] I have read and understood the full scope defined in this document
- [ ] I have verified that all lab VMs are running in isolated VirtualBox networks only
- [ ] I have created a `vulnerable-mode` snapshot of all three VMs
- [ ] I have confirmed that no real personal or financial data is present in the database
- [ ] I understand that testing outside the lab boundary is unauthorized and potentially illegal

---

*Document Owner: Lab Administrator | Last Updated: See version control*
