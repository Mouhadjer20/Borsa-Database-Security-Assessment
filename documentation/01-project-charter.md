# Project Charter — Borsa

> **Document Version:** 1.0  
> **Status:** Active  
> **Classification:** Internal Research / Educational Use Only

---

## 1. Project Overview

**Borsa** is an educational financial web application and cybersecurity research platform built to study, demonstrate, and document common web application security vulnerabilities in a controlled, isolated laboratory environment. The name *Borsa* is the Turkish/Italian word for stock exchange, reflecting the application's simulated financial domain.

The platform provides a realistic but entirely synthetic banking/investment interface backed by a production-grade technology stack (React, FastAPI, PostgreSQL). Its primary purpose is to serve as a research vehicle for studying how vulnerabilities arise, how they are exploited, and how defensive controls eliminate or mitigate risk.

---

## 2. Project Purpose

| Dimension | Description |
|-----------|-------------|
| **Academic** | Generate structured, evidence-based findings on four classes of database-layer security vulnerabilities |
| **Practical** | Demonstrate attack and defense for SQL injection, excessive privilege, broken authorization, and network exposure |
| **Comparative** | Provide before/after (vulnerable vs. secure) experimental evidence for each security scenario |
| **Pedagogical** | Serve as a teaching artifact for secure coding, database hardening, and network segmentation |

---

## 3. Scope

### 3.1 In Scope

- All research activities conducted **entirely within** the VirtualBox isolated lab (3-VM topology)
- Four primary security scenarios (see Section 7)
- Synthetic financial data only — no real personal or financial information
- PostgreSQL database-layer security hardening and misconfiguration analysis
- Application-layer controls (parameterized queries, authorization checks)
- Network-layer controls (firewall rules, pg_hba.conf segmentation)
- Documentation and reporting of all findings

### 3.2 Out of Scope

- Any testing, scanning, or probing of systems outside the VirtualBox lab
- Real user data, real financial data, or any production systems
- Physical security assessments
- Social engineering activities
- Denial-of-service testing beyond controlled lab conditions

---

## 4. Educational Objectives

Upon completion of this research project, participants will be able to:

1. **Identify** SQL injection vulnerabilities in parameterized vs. string-concatenated query patterns
2. **Demonstrate** the attack surface exposed by overprivileged database roles
3. **Explain** how Broken Object Level Authorization (BOLA/IDOR) manifests in financial APIs
4. **Implement** PostgreSQL Row-Level Security (RLS) policies as an authorization defense
5. **Configure** network segmentation using `pg_hba.conf`, firewall rules, and VM network isolation
6. **Document** security findings using industry-standard frameworks (STRIDE, MITRE ATT&CK, CWE, CVSS 4.0)
7. **Compare** vulnerable and secure configurations using empirical experimental evidence
8. **Produce** a professional security research report suitable for academic or professional review

---

## 5. Authorized Use Statement

> **⚠️ WARNING:** All security testing activities documented in this project are authorized **solely** within the VirtualBox laboratory environment described in `infrastructure/network-topology/topology.md`. No techniques, payloads, tools, or configurations described in this documentation may be used against any system, network, or service outside of this lab without explicit written authorization from the system owner.
>
> This project exists for educational purposes under controlled conditions. Unauthorized use of these techniques against real systems may constitute a criminal offense under applicable computer fraud and abuse laws.

---

## 6. Team Roles

| Role | Responsibilities |
|------|-----------------|
| **Principal Researcher** | Research design, experimental execution, final report authorship |
| **Lab Administrator** | VM provisioning, network configuration, snapshot management |
| **Security Analyst** | Vulnerability validation, evidence collection, STRIDE/CVSS analysis |
| **Documentation Lead** | Maintaining all project documentation, schema references, methodology docs |
| **Reviewer** | Independent review of findings and conclusions |

> **Note:** In a solo research context, one individual may hold all roles. Role separation is recommended when multiple researchers collaborate.

---

## 7. Security Research Scenarios

| # | Scenario | CWE | Primary Control Layer |
|---|----------|-----|-----------------------|
| 1 | **SQL Injection** | CWE-89 | Application (query construction) |
| 2 | **Excessive Database Privileges** | CWE-250 | Database (role permissions) |
| 3 | **Broken Object Level Authorization (BOLA)** | CWE-284 | Application + Database (RLS) |
| 4 | **Database Network Exposure** | CWE-668 | Network (firewall + pg_hba.conf) |

Each scenario is tested in both a **Vulnerable** configuration and a **Secure** configuration, with evidence collected for both states.

---

## 8. Technology Stack

### Application Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Frontend** | React (Vite) | 18.x |
| **Backend API** | FastAPI | 0.110+ |
| **Database** | PostgreSQL | 18.x |
| **Language (Backend)** | Python | 3.11+ |
| **Language (Frontend)** | TypeScript | 5.x |
| **Package Manager (FE)** | pnpm | 8.x+ |
| **ORM/Driver** | asyncpg / psycopg | 3.x |

### Infrastructure Stack

| Component | Technology |
|-----------|-----------|
| **Virtualization** | Oracle VirtualBox |
| **OS (VM1)** | Kali Linux (rolling) |
| **OS (VM2, VM3)** | Ubuntu Server 24.04 LTS |
| **Web Server / Proxy** | Nginx (optional, VM2) |
| **Process Manager** | systemd |
| **Networking** | VirtualBox Host-Only Adapters |

### Security Research Tools (VM1 — Kali)

| Tool | Purpose |
|------|---------|
| `nmap` | Network reconnaissance and port scanning |
| `sqlmap` | Automated SQL injection detection |
| `Burp Suite Community` | HTTP proxy and manual testing |
| `curl` | HTTP request crafting |
| `psql` | Direct PostgreSQL client testing |
| `wireshark` | Network traffic capture and analysis |

---

## 9. Project Timeline

```
Phase 1 — Infrastructure Setup        (Weeks 1–2)
  ├─ VirtualBox lab provisioning
  ├─ VM installation and configuration
  ├─ Network topology validation
  └─ Baseline connectivity testing

Phase 2 — Application Deployment      (Weeks 2–3)
  ├─ Database schema deployment
  ├─ FastAPI backend deployment
  ├─ React frontend deployment
  └─ Synthetic data generation

Phase 3 — Vulnerable Mode Research    (Weeks 3–5)
  ├─ Scenario 1: SQL Injection
  ├─ Scenario 2: Excessive Privileges
  ├─ Scenario 3: BOLA/IDOR
  └─ Scenario 4: Network Exposure

Phase 4 — Secure Mode Research        (Weeks 5–7)
  ├─ Apply all security controls
  ├─ Re-run all 4 scenarios
  └─ Compare results

Phase 5 — Analysis & Reporting        (Weeks 7–8)
  ├─ Findings synthesis
  ├─ CVSS 4.0 scoring
  └─ Final report authorship
```

---

## 10. Deliverables

| Deliverable | Location |
|-------------|----------|
| Project Charter | `documentation/01-project-charter.md` |
| Research Questions | `documentation/02-research-questions.md` |
| Architecture Documentation | `documentation/04-architecture.md` |
| Threat Model | `documentation/05-threat-model.md` |
| Security Experiments | `documentation/08-security-experiments.md` |
| Results & Analysis | `documentation/09-results-and-analysis.md` |
| Final Report | `documentation/10-final-report.md` |
| Infrastructure Configs | `infrastructure/` |
| Database Reference SQL | `database/` |

---

## 11. Success Criteria

The project is considered successful when:

- [ ] All 4 scenarios are executed in both Vulnerable and Secure modes
- [ ] Evidence (screenshots, logs, command outputs) is collected for each experimental run
- [ ] Quantitative comparison between vulnerable and secure states is documented
- [ ] Final report meets professional security research standards
- [ ] All infrastructure configurations are reproducible from documentation alone
- [ ] No external systems were accessed during research

---

*Document Owner: Principal Researcher | Last Updated: See version control*
