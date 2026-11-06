# Database Security Assessment — Research Design & Architecture

I think we have a much stronger project now. Your new ideas change the nature of the project: instead of demonstrating vulnerabilities in a database, we are going to conduct a controlled security assessment of a financial information system, implement defensive controls, and experimentally verify their effectiveness.

I particularly agree with three additions:

1. Use a fictional financial institution rather than a generic student database.
2. Perform the attacks, implement defenses, and repeat the exact same experiments.
3. Associate every finding with recognized security frameworks, technical evidence, and a justified CVSS score.

I would also introduce one important research principle:

We must distinguish between a vulnerability, an attack technique, an observed impact, and a security control.

For example:

- Vulnerability: SQL injection caused by unsafe query construction.
- Attack technique: Manipulating application input to alter SQL query semantics.
- Impact: Unauthorized disclosure of fictional customer records.
- Control: Parameterized queries.
- Verification: Repeat the original test and demonstrate that the SQL structure can no longer be manipulated.

This distinction will make your final report considerably more professional.

# 1. Choose a financial institution as the research scenario

I think you mean a fictional bank or bourse (stock exchange/brokerage institution), rather than a college.

I suggest creating a fictional financial institution called:

# Borsa

Fictional Financial Institution

Lab environment

Business domain: Banking and financial services.

Purpose: Manage customer accounts, transactions, employees, financial operations, and internal banking services.

Security objective: Protect financial confidentiality, integrity, and availability.

Database contains fictional records such as:

- Customer identity and contact information.
- Bank account identifiers and balances.
- Transaction histories.
- Employee and administrator accounts.
- Account ownership relationships.
- Audit records and security events.
- Internal banking operation records.

Why is this scenario better than a college?

A financial institution gives you more meaningful security requirements:

| Asset             | Security importance | Example impact                        |
| ----------------- | ------------------- | ------------------------------------- |
| Customer records  | Confidentiality     | Unauthorized disclosure               |
| Account balances  | Integrity           | Unauthorized modification             |
| Transactions      | Integrity           | Unauthorized transaction manipulation |
| Employee accounts | Authentication      | Unauthorized access                   |
| Audit logs        | Accountability      | Concealing or losing evidence         |
| Banking services  | Availability        | Service disruption                    |

Important: We will use completely fictional identities, artificial account numbers, synthetic balances, and generated transactions. We do not need real banking information, real payment systems, or connections to financial institutions.

One further idea: model the system as a small banking platform, not a complete banking application. We need enough functionality to establish realistic security boundaries without wasting time implementing banking business logic.

# 2. Research questions and hypotheses

We should establish the scientific foundation before choosing individual attacks.

I propose the following main research question:

> To what extent do application-level SQL injection vulnerabilities, excessive database privileges, broken authorization mechanisms, and database network exposure compromise the confidentiality and integrity of a relational database system in a simulated financial institution, and how effectively can layered security controls mitigate these risks?

This question connects all four attacks and the defensive phase.

## 2.1 Specific research questions

| ID  | Research question                                                                                                  |
| --- | ------------------------------------------------------------------------------------------------------------------ |
| RQ1 | Can SQL injection expose financial records despite normal database authentication?                                 |
| RQ2 | Can excessive database privileges allow an application account to perform unauthorized operations?                 |
| RQ3 | Can authenticated users access financial resources belonging to other customers?                                   |
| RQ4 | Can network exposure allow unauthorized clients to establish database connections?                                 |
| RQ5 | How do parameterized queries, least privilege, authorization controls and network segmentation reduce these risks? |
| RQ6 | Can database audit logs provide sufficient evidence to detect the simulated unauthorized activities?               |
| RQ7 | Does combining multiple weaknesses produce a greater impact than exploiting each weakness individually?            |

RQ7 is especially interesting. It gives you an opportunity to investigate vulnerability chaining rather than studying each weakness in isolation.

## 2.2 Research hypotheses

We can define testable hypotheses:

| Hypothesis | Expected observation                                                                                          |
| ---------- | ------------------------------------------------------------------------------------------------------------- |
| H1         | Unsafe SQL query construction permits manipulation of query semantics.                                        |
| H2         | Excessive privileges increase the operations available to a compromised application account.                  |
| H3         | Missing object-level authorization permits cross-customer resource access.                                    |
| H4         | Unrestricted database connectivity increases the number of possible access paths.                             |
| H5         | Applying the corresponding defensive controls reduces or eliminates the demonstrated unauthorized operations. |
| H6         | Combining application and database weaknesses increases the potential impact of an individual weakness.       |

These hypotheses will later become your experimental evaluation criteria.

# 3. PostgreSQL: why this database?

Your question about why PostgreSQL is suitable, and whether another DBMS provides the same capabilities, is an excellent academic discussion.

We should not claim that PostgreSQL is inherently more secure than every other database.

A better research question is:

> Why is PostgreSQL an appropriate platform for investigating database security mechanisms, and how do its security architecture and administrative capabilities support the selected experiments?

## 3.1 How PostgreSQL works

[PostgreSQL Internals: Inside the Storage Engine - DEV Community](https://images.openai.com/static-rsc-4/Js-V8U-4Q55Vd8tFqTpBVdLPNy-xNFrLnMopL-C3HMeOO-mQ6nu4wNP26Iq2Yn2rinzqQNwIV0ZSlBitQDZCu95lTvYX_uP4Vik7_Vi7Wuc9mHzqoB5SiRTZg3Fr0I8yC2aSIYX7361MVu9bJZHC11e8Pzo5UcMKYmCSoYRX7i8?purpose=inline)

[dev.to](https://dev.to/priteshsurana/postgresql-internals-inside-the-storage-engine-1bhm?utm_source=chatgpt.com)

We should understand the following architectural components:

| Component                 | Function                          | Security relevance                            |
| ------------------------- | --------------------------------- | --------------------------------------------- |
| Client interface          | Accepts database connections      | Authentication entry point                    |
| PostgreSQL server process | Handles client sessions           | Executes SQL operations under a database role |
| Authentication subsystem  | Verifies connection identity      | Controls database access                      |
| Role system               | Defines identities and privileges | Authorization and least privilege             |
| Query processor           | Parses, plans and executes SQL    | Relevant to SQL injection effects             |
| Shared buffers            | Caches database pages             | Database memory management                    |
| WAL                       | Write-Ahead Logging               | Durability and recovery                       |
| System catalogs           | Store database metadata           | Roles, permissions, schemas and objects       |
| Logging subsystem         | Records configured events         | Auditing and investigation                    |

One particularly important detail: PostgreSQL uses a process-per-connection architecture. Understanding the server process, session identity, and active database role will help us investigate what happens when the application connects to the database.

## 3.2 PostgreSQL security capabilities we will investigate

1\. Role-Based Access Control

PostgreSQL roles can have login capabilities, memberships, and privileges. We can create separate application identities and distinguish read-only, write-limited and administrative permissions.

2\. Schema and object-level permissions

PostgreSQL supports permissions at different levels, including database, schema, table, sequence, function and column permissions.

3\. Row-Level Security (RLS)

Important research extension

RLS allows database policies to restrict which rows a database role can read or modify.

For example, a customer should only access records belonging to that customer, subject to the database session identity and correctly designed policies.

4\. Prepared statements

Parameterized queries separate SQL instructions from supplied values, preventing ordinary input values from changing the intended query structure.

5\. Connection authentication

PostgreSQL provides configurable authentication methods through its authentication configuration, including password-based and certificate-related mechanisms.

6\. Network access control

PostgreSQL provides connection-listening configuration and client authentication rules. These can be combined with operating-system firewall restrictions.

7\. Auditing and monitoring

PostgreSQL logging and extensions can help record database activity, authentication events, and selected statements.

## 3.3 Why PostgreSQL instead of MariaDB or MySQL?

This should be a comparison of capabilities, not an unsupported security ranking.

| Security capability          | PostgreSQL                     | MariaDB / MySQL                                       |
| ---------------------------- | ------------------------------ | ----------------------------------------------------- |
| Role-based privileges        | Yes                            | Yes, with implementation differences                  |
| Prepared statements          | Yes                            | Yes                                                   |
| Row-level security           | Native RLS policies            | Different mechanisms; not equivalent native table RLS |
| Schema permissions           | Yes                            | Different database/schema model                       |
| TLS connections              | Yes                            | Yes                                                   |
| Authentication configuration | Yes                            | Yes, plugin-dependent                                 |
| Auditing                     | Native logging and extensions  | Available through different logging/plugins           |
| Fine-grained access          | Multiple object-level controls | Multiple object-level controls                        |

The strongest differentiator for this project is PostgreSQL's native Row-Level Security, combined with its role and privilege system.

That gives us an opportunity to compare application-layer authorization against database-enforced authorization.

A very good research extension: Implement customer ownership restrictions twice:

- First, using authorization checks in the Flask/FastAPI application.
- Second, using PostgreSQL Row-Level Security.

Then compare their behavior under the same controlled tests.

This is more interesting than simply showing that RLS exists.

## 3.4 What PostgreSQL version should we use?

I recommend PostgreSQL 18, using the latest available minor release within the 18 series.

As of November 2026, PostgreSQL's official version policy lists version 18 as supported, with maintenance scheduled through November 2030. PostgreSQL also supports its major versions for five years.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://www.postgresql.org\&sz=32)

PostgreSQL+1



For reproducibility, record:

- Exact PostgreSQL major and minor version.
- Operating system and kernel.
- Application framework and version.
- Python version.
- PostgreSQL extensions.
- Configuration files and relevant settings.
- Network topology.

Do not use an outdated database merely to create vulnerabilities. We should deliberately introduce controlled application and configuration weaknesses while keeping the DBMS itself on a supported release.

# 4. Three-VM architecture and network security design

I recommend separating the environment into three virtual machines, but also separating the network into two security zones.

This is an important improvement over putting all three machines on one flat internal network.

## 4.1 Proposed architecture

## Borsa — Virtual Lab Topology

VM 1 — Kali Linux

Auditor

Nmap · Burp Suite · SQLmap · Wireshark · psql

Interface: AUDIT-NET

ZONE 1 — AUDIT NETWORK

VM 2 — Application Server

Dual-homed

Linux · Python · Flask/FastAPI · Gunicorn/Uvicorn · Application logs

Interfaces: AUDIT-NET + DB-NET

ZONE 2 — DATABASE NETWORK

VM 3 — Database Server

Protected

Linux · PostgreSQL 18.x · Roles · RLS · Audit logs · Synthetic data

Interface: DB-NET only

Default network policy

- Kali → Application: permitted.
- Application → PostgreSQL: permitted on the required database port.
- Kali → PostgreSQL: denied.
- Internet/bridged access: disabled during experiments.

The interesting part is that the application server has two network interfaces. It connects the audit-facing zone to the database-facing zone, but it must not automatically act as an unrestricted router.

This gives us a realistic place to investigate trust boundaries.

## 4.2 Network design

| Network           | Members              | Purpose                |
| ----------------- | -------------------- | ---------------------- |
| AUDIT-NET         | Kali + Web VM        | Application assessment |
| DB-NET            | Web VM + DB VM       | Database communication |
| Optional MGMT-NET | Host management only | Administrative access  |

For the network-exposure experiment, we will temporarily change an explicitly documented firewall rule and observe the difference between:

- Database access restricted to the application server.
- Database access accidentally exposed to the audit network.

We will restore the restrictive policy after the experiment.

Important: Do not configure the database to listen on every interface and assume that a firewall alone is sufficient. We will combine PostgreSQL listener configuration, client authentication rules, host firewall restrictions and connection testing.

## 4.3 Why this topology is academically interesting

It allows us to investigate three different trust relationships:

1. User to application.
2. Application to database.
3. External client to database network.

It also makes it possible to demonstrate that a network-level restriction and a database authorization restriction solve different problems.

For example, preventing Kali from connecting directly to PostgreSQL does not prevent an SQL injection vulnerability from being exploited through the legitimate web application.

That distinction is central to this project.

# 5. Database design — Borsa

We need a database structure that represents realistic financial relationships without implementing an entire banking system.

I propose the following logical model.

## Borsa relational model

customers

customer_id · full_name · email · status

bank_accounts

account_id · customer_id · account_type · balance · currency · status

transactions

transaction_id · source_account · destination_account · amount · timestamp · status

employees

employee_id · name · department · status

app_users

user_id · username · password_hash · role

security_audit

event_id · actor · action · resource · timestamp

access_policies

policy_id · role · resource · permission

This is a conceptual model; we will refine the foreign keys and relationships before implementing SQL.

## 5.1 Database identities

We should distinguish application users from PostgreSQL roles.

For example:

| Identity         | Purpose                                                 |
| ---------------- | ------------------------------------------------------- |
| `db_owner`       | Database object ownership and controlled administration |
| `app_readonly`   | Read-only application operations                        |
| `app_writer`     | Limited application write operations                    |
| `app_vulnerable` | Deliberately overprivileged experimental account        |
| `auditor`        | Authorized security inspection                          |
| `migration_role` | Controlled database schema migrations                   |

The overprivileged account is an experimental identity, not an administrator account.

We should never use the PostgreSQL superuser as the normal application connection.

## 5.2 Fictional customer accounts

Create several synthetic customers:

- Customer A: owns account A.
- Customer B: owns account B.
- Customer C: owns account C.
- Employee D: has limited internal access.
- Administrator E: has explicitly defined administrative permissions.

This provides a controlled environment to test object-level authorization.

## 5.3 Introduce canary records

An additional professional feature would be to create distinctive fictional records that are not used in normal application workflows.

For example:

- A synthetic account with a unique canary identifier.
- A specially marked transaction.
- A canary customer record.

If an unauthorized test account accesses one of these records, we have an unambiguous indicator of unauthorized access.

We can record the event without collecting unnecessary information.

# 6. MITRE ATT&CK, CWE and CAPEC — how to use them correctly

I strongly support adding MITRE ATT&CK, but I want to avoid a common reporting mistake.

MITRE ATT&CK does not classify software vulnerabilities. It describes adversary tactics and techniques.

For vulnerability identification, we should use CWE. For attack patterns, CAPEC is useful. ATT&CK describes how adversaries behave during operations.

Use all three where applicable.

## Proposed attack mapping

| Scenario                                       | ATT&CK mapping                                                                                             | Weakness classification                                                        |
| ---------------------------------------------- | ---------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| SQL Injection                                  | T1190 — Exploit Public-Facing Application, where the application is externally exposed                     | CWE-89                                                                         |
| SQL Injection resulting in database collection | T1213.006 — Data from Databases                                                                            | CWE-89                                                                         |
| Excessive privileges                           | T1078 — Valid Accounts, if valid credentials are abused; other mappings depend on observed actions         | CWE-250                                                                        |
| Broken authorization                           | T1078 when legitimate accounts are misused; T1213.006 when database information is collected               | CWE-862 / CWE-863                                                              |
| Database network exposure                      | T1046 — Network Service Discovery for service discovery; T1190 if an exposed service is actually exploited | CWE-668 or a more specific misconfiguration weakness, depending on the finding |

Official references:

- [MITRE ATT&CK T1190 — Exploit Public-Facing Application](https://attack.mitre.org/techniques/T1190/?utm_source=chatgpt.com)
- [MITRE ATT&CK T1213 — Data from Information Repositories](https://attack.mitre.org/techniques/T1213/?utm_source=chatgpt.com)
- [MITRE ATT&CK T1098 — Account Manipulation](https://attack.mitre.org/techniques/T1098/?utm_source=chatgpt.com)
- [MITRE ATT&CK Enterprise techniques](https://attack.mitre.org/techniques/?utm_source=chatgpt.com)

One important qualification: not every broken authorization vulnerability maps directly to a unique ATT&CK technique. We should document the technique only when the simulated behavior actually matches it.

For each attack, create an ATT&CK mapping record containing:

1. Tactic.
2. Technique ID.
3. Technique name.
4. Adversary objective.
5. Observed lab behavior.
6. Evidence.
7. Detection opportunity.
8. Relevant mitigation.

This will make your ATT&CK mapping defensible during your presentation.

# 7. CVSS v4.0 — professional vulnerability assessment

This is one of the best additions you suggested.

Instead of assigning arbitrary severity levels such as High or Critical, we will calculate a score using the official Common Vulnerability Scoring System (CVSS) version 4.0.

Official references:

- [FIRST CVSS v4.0 specification](https://www.first.org/cvss/specification-document?utm_source=chatgpt.com)
- [CVSS v4.0 User Guide](https://www.first.org/cvss/user-guide?utm_source=chatgpt.com)
- [Official CVSS calculator](https://www.first.org/cvss/calculator/4.0?utm_source=chatgpt.com)

## 7.1 What does CVSS measure?

CVSS v4.0 considers four metric groups:

| Metric group  | What it measures                                               |
| ------------- | -------------------------------------------------------------- |
| Base          | Intrinsic exploitability and impact                            |
| Threat        | Current threat and exploit maturity                            |
| Environmental | Importance of the affected system and its specific environment |
| Supplemental  | Additional contextual information                              |

The resulting score ranges from 0 to 10.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://www.first.org\&sz=32)

first.org+1



Severity classification:

| Score    | Classification |
| -------- | -------------- |
| 0.0      | None           |
| 0.1–3.9  | Low            |
| 4.0–6.9  | Medium         |
| 7.0–8.9  | High           |
| 9.0–10.0 | Critical       |

## 7.2 How we will calculate our scores

For each finding, evaluate:

- Attack Vector (AV).
- Attack Complexity (AC).
- Attack Requirements (AT).
- Privileges Required (PR).
- User Interaction (UI).
- Vulnerable System Confidentiality (VC).
- Vulnerable System Integrity (VI).
- Vulnerable System Availability (VA).
- Subsequent System impact (SC, SI, SA).

We will not assume that every SQL injection has a Critical score. The score must reflect what our actual test demonstrates.

For example, consider two hypothetical findings:

Finding A — SQL Injection

An unauthenticated user can access fictional customer information through a vulnerable application endpoint.

Finding B — Excessive Database Privileges

An authenticated application service account can read and modify records beyond its intended responsibilities.

They have different attack prerequisites and potentially different impacts. They must be scored independently.

## 7.3 CVSS report template

I propose this structure for each finding:

| Field                  | Example                              |
| ---------------------- | ------------------------------------ |
| Finding ID             | DB-01                                |
| Vulnerability          | SQL Injection                        |
| CWE                    | CWE-89                               |
| ATT&CK                 | T1190, where applicable              |
| Affected component     | Customer API                         |
| Root cause             | Unsafe SQL construction              |
| Evidence               | Controlled test and application logs |
| Confidentiality impact | Assessed from observed access        |
| Integrity impact       | Assessed from observed modification  |
| Availability impact    | Assessed from observed effect        |
| CVSS version           | 4.0                                  |
| CVSS score             | Calculated after testing             |
| CVSS vector            | Complete vector string               |
| Remediation            | Parameterized queries                |
| Retest result          | Pass / Fail                          |

Important distinction: CVSS is not a complete business-risk assessment. We should also provide a separate risk analysis considering the importance of financial assets, likelihood, exposure and operational consequences.

Also, our lab findings may not have CVEs because we are creating vulnerabilities in our own application and configuration. That does not prevent us from documenting and scoring the findings.

# 8. SQL standard and database version legitimacy

Your point about using a legitimate SQL version is important, but there are two different concepts.

SQL standard version ≠ PostgreSQL server version.

- SQL is standardized through ISO/IEC 9075.
- PostgreSQL has its own release versions, such as 18.x.
- PostgreSQL implements SQL standard features and also provides PostgreSQL-specific extensions.

For this project, I recommend:

| Element                    | Decision                                        |
| -------------------------- | ----------------------------------------------- |
| Database engine            | PostgreSQL                                      |
| Database major version     | 18                                              |
| Database patch version     | Latest supported 18.x release at implementation |
| Query language             | Standard SQL where practical                    |
| Database-specific features | PostgreSQL-specific features when required      |
| Driver                     | Psycopg 3                                       |
| Database access            | SQLAlchemy 2 or controlled direct SQL           |

We should document which SQL features we use and whether they are standard SQL or PostgreSQL-specific.

This gives you an excellent presentation question:

> Does using a standardized query language guarantee database security, or does security primarily depend on how applications construct queries, authenticate users, and enforce privileges?

The answer is that using standard SQL alone does not guarantee security.

# 9. Four attack scenarios: experimental design

Now let's connect all the previous decisions into an actual scientific methodology.

I recommend using a controlled before-and-after experimental design.

## Experimental lifecycle

1. Phase 0 — Research preparation

   Define scope, assets, hypotheses, threat model, network boundaries and test accounts.
2. Phase 1 — Baseline assessment

   Deploy the financial application and database. Document the initial configuration and establish expected behavior.
3. Phase 2 — Vulnerability introduction

   Introduce controlled weaknesses into the application and database configuration.
4. Phase 3 — Security assessment

   Perform reconnaissance, scanning, vulnerability identification and controlled exploitation.
5. Phase 4 — Evidence collection

   Capture application logs, database logs, network observations, screenshots and test results.
6. Phase 5 — Defensive implementation

   Introduce appropriate security controls and document every modification.
7. Phase 6 — Retesting

   Repeat the same test cases against the protected environment.
8. Phase 7 — Comparative analysis

   Compare the vulnerable and secured configurations, evaluate hypotheses and calculate final risk.
9. Phase 8 — Final reporting

   Produce technical findings, ATT&CK mappings, CWE classifications, CVSS scores and recommendations.

## 9.1 Scenario 1 — SQL Injection

Vulnerable state

Research objective: Determine whether unsafe SQL query construction allows an attacker to manipulate the application's intended SQL operations.

Experimental variants:

| Variant | Query implementation           |
| ------- | ------------------------------ |
| A       | Unsafe SQL string construction |
| B       | Parameterized SQL query        |

Defensive measures:

- Prepared statements.
- Parameterized queries.
- Safe database access patterns.
- Restricted application database identity.
- Input validation as supplementary protection.

Measurements:

- Unauthorized records accessed.
- Whether query semantics were manipulated.
- Database role used.
- Corresponding application and database logs.
- Whether the same test succeeds after remediation.

## 9.2 Scenario 2 — Excessive Database Privileges

Research objective: Determine whether an application account can perform operations beyond its assigned responsibilities.

Experimental variants:

| Variant | Database identity              |
| ------- | ------------------------------ |
| A       | Excessively privileged account |
| B       | Least-privileged account       |

Defensive measures:

- Role separation.
- Explicit GRANT/REVOKE permissions.
- Restricted ownership.
- Separation of migration and runtime identities.
- PostgreSQL privilege auditing.

Measurements:

- Number of permitted operations.
- Unauthorized operations attempted.
- Unauthorized operations successfully performed.
- Difference between the two privilege configurations.

## 9.3 Scenario 3 — Broken Authorization

Research objective: Determine whether a customer can access another customer's financial resources.

Experimental variants:

| Variant | Authorization mechanism               |
| ------- | ------------------------------------- |
| A       | Missing or incorrect ownership checks |
| B       | Correct server-side authorization     |
| C       | PostgreSQL Row-Level Security         |

This is where RLS becomes particularly valuable.

You can compare:

- Application-enforced access control.
- Database-enforced row-level access control.
- Combined application and database enforcement.

We should also examine session identity carefully. RLS policies are only useful if the application establishes the correct database identity or trusted session context and users cannot manipulate that context.

Measurements:

- Cross-customer access attempts.
- Unauthorized records returned.
- Unauthorized modifications.
- Enforcement behavior at application and database layers.

## 9.4 Scenario 4 — Database Network Exposure

Research objective: Determine whether the database accepts connections from unauthorized network locations.

Experimental variants:

| Variant | Network configuration                                  |
| ------- | ------------------------------------------------------ |
| A       | Database access restricted to application VM           |
| B       | Database access unnecessarily exposed to audit network |

Defensive measures:

- Network segmentation.
- Host firewall.
- PostgreSQL listener restrictions.
- Client authentication rules.
- TLS for database connections.

Measurements:

- Port accessibility.
- Connection success/failure.
- Source network.
- Authentication outcome.
- Evidence of permitted and denied connections.

# 10. An important improvement: vulnerability chaining

I would add one experiment after the four individual scenarios.

Advanced research extension

Combined attack-path analysis

Instead of treating vulnerabilities as completely independent, investigate what happens when they are combined.

For example:

## Illustrative attack chain

Initial access through application weakness

SQL injection

Application database identity has excessive permissions

Unauthorized access to synthetic financial records

Evidence collection and impact assessment

Conceptual attack path; each stage will be validated independently before combining the conditions.

The experiment should answer:

- Does SQL injection alone expose data?
- Does excessive privilege alone create an unauthorized capability?
- Does combining both increase the demonstrated impact?
- Which individual defensive control breaks the chain?
- Do multiple defensive controls provide additional protection?

This is an excellent way to demonstrate defense in depth.

Do not assume that CVSS scores can simply be added together to calculate the risk of an attack chain. We will assess the individual findings and then separately explain the combined attack path and its business impact.

# 11. Measurement and comparative evaluation

For a research-level project, we need more than screenshots showing successful attacks.

We need measurable results.

I recommend creating a results matrix like this:

| Metric                                | Vulnerable state        | Protected state         |
| ------------------------------------- | ----------------------- | ----------------------- |
| Unauthorized SQL access               | Observed / Not observed | Observed / Not observed |
| Unauthorized database operations      | Count                   | Count                   |
| Cross-customer access                 | Count                   | Count                   |
| Unauthorized network connections      | Success / Failure       | Success / Failure       |
| Successful unauthorized modifications | Count                   | Count                   |
| Security events logged                | Count                   | Count                   |
| Detection coverage                    | Percentage              | Percentage              |

For example, if five controlled unauthorized access attempts are performed, and all five succeed before remediation but none succeeds afterward, the observed prevention rate is:

\\[ P=\frac{N\_{\text{blocked}}}{N\_{\text{attempted}}}\times100 \\]

This measures the outcome of your specific tests, not the overall security of the system.

Other useful measurements:

- Detection coverage.
- False-positive observations.
- Number of excessive privileges removed.
- Number of exposed services reduced.
- CVSS severity before and after remediation, where reassessment is justified.

We should keep the same test cases, accounts, data and initial conditions during pre- and post-defense experiments. Otherwise, the comparison will not be scientifically reliable.

# 12. Security frameworks and methodology

I recommend using four complementary references.

| Framework       | How we use it                                   |
| --------------- | ----------------------------------------------- |
| NIST SP 800-115 | Technical security testing methodology          |
| OWASP WSTG      | Web application security testing procedures     |
| MITRE ATT&CK    | Adversary behavior mapping                      |
| CWE / CAPEC     | Vulnerability and attack-pattern classification |
| FIRST CVSS 4.0  | Vulnerability severity assessment               |

Useful documentation:

- [NIST SP 800-115 — Technical Guide to Information Security Testing](https://csrc.nist.gov/pubs/sp/800/115/final?utm_source=chatgpt.com)
- [OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/?utm_source=chatgpt.com)
- [MITRE CWE](https://cwe.mitre.org/?utm_source=chatgpt.com)
- [MITRE CAPEC](https://capec.mitre.org/?utm_source=chatgpt.com)
- [MITRE ATT&CK](https://attack.mitre.org/?utm_source=chatgpt.com)

The NIST and OWASP guidance will help structure your testing. ATT&CK and CWE will help explain the technical findings.

# 13. Questions to answer during your research and presentation

I would prepare your oral presentation around questions that demonstrate understanding rather than simply describing commands.

Here are questions worth investigating.

## Database architecture and PostgreSQL

1. Why did we select PostgreSQL instead of MariaDB or MySQL?
2. How does PostgreSQL process a client connection?
3. What is the difference between a PostgreSQL role, a database user and an application user?
4. How does PostgreSQL enforce permissions?
5. What is Row-Level Security, and how does it differ from application authorization?
6. Does implementing SQL standard-compliant queries guarantee security?

## Vulnerability analysis

7. Why is SQL injection fundamentally different from excessive database privileges?
8. Can an application be vulnerable to SQL injection even when database authentication is correctly configured?
9. Can an application using prepared statements still expose confidential data?
10. Can a restricted database account limit the consequences of SQL injection?
11. Why is authentication not sufficient to guarantee authorization?
12. What happens when multiple vulnerabilities are combined?

## Defense and verification

13. Why is defense in depth more effective than depending on a single control?
14. How do parameterized queries prevent SQL injection?
15. Can RLS protect against an application that incorrectly establishes the database session identity?
16. Why should the database not be directly accessible from the user network?
17. How can database audit logs help investigate unauthorized access?
18. How do we prove that a remediation actually works?

## Risk and threat intelligence

19. What is the difference between CVSS, CWE and MITRE ATT&CK?
20. Why might two SQL injection vulnerabilities have different CVSS scores?
21. Can a vulnerability have a high business impact but a relatively low CVSS score?
22. How do we document an attack technique without incorrectly attributing an ATT&CK technique?

These questions can become a dedicated chapter in your report called Security Analysis and Research Discussion.

# 14. Final project structure

Here is the structure I would eventually use for your repository.

```
Borsa-Database-Security-Assessment/
│
├── README.md
│
├── documentation/
│   ├── 01-project-charter.md
│   ├── 02-research-questions.md
│   ├── 03-scope-and-rules-of-engagement.md
│   ├── 04-architecture.md
│   ├── 05-threat-model.md
│   ├── 06-database-design.md
│   ├── 07-methodology.md
│   └── 08-final-report.md
│
├── infrastructure/
│   ├── vm-specifications/
│   ├── network-topology/
│   ├── firewall/
│   └── database-configuration/
│
├── database/
│   ├── schema/
│   ├── seed/
│   ├── roles/
│   ├── policies/
│   └── audit/
│
├── application/
│   ├── vulnerable/
│   ├── secured/
│   ├── tests/
│   └── requirements.txt
│
├── attacks/
│   ├── 01-sql-injection/
│   ├── 02-excessive-privileges/
│   ├── 03-broken-authorization/
│   └── 04-network-exposure/
│
├── defense/
│   ├── parameterized-queries/
│   ├── least-privilege/
│   ├── authorization/
│   ├── row-level-security/
│   └── network-segmentation/
│
├── verification/
│   ├── pre-defense/
│   ├── post-defense/
│   └── regression-tests/
│
├── evidence/
│   ├── screenshots/
│   ├── application-logs/
│   ├── database-logs/
│   └── network-captures/
│
├── reporting/
│   ├── findings/
│   ├── cvss/
│   ├── attack-mapping/
│   └── comparative-results/
│
└── references/
    ├── standards.md
    └── bibliography.md
```

We will keep vulnerable and secured implementations clearly separated. The vulnerable application will only run inside the isolated lab, and snapshots will be taken before each experiment.

# 15. My final architectural recommendations

## Proposed research specification

Project

Defined

Borsa Database Security Assessment

| Component               | Recommendation                               |
| ----------------------- | -------------------------------------------- |
| Financial scenario      | Fictional bank                               |
| DBMS                    | PostgreSQL 18.x                              |
| Application             | FastAPI                                      |
| Programming language    | Python                                       |
| Database driver         | Psycopg 3                                    |
| Database access         | SQLAlchemy 2 + controlled direct SQL         |
| Web architecture        | REST API                                     |
| Application server      | Uvicorn                                      |
| Audit workstation       | Kali Linux                                   |
| Application VM          | Dedicated Linux VM                           |
| Database VM             | Dedicated Linux VM                           |
| Virtualization          | VirtualBox                                   |
| Network                 | Two isolated security zones                  |
| Testing                 | Manual validation + selected automated tools |
| Attack mapping          | MITRE ATT&CK                                 |
| Weakness classification | CWE / CAPEC                                  |
| Severity                | CVSS 4.0                                     |
| Methodology             | NIST + OWASP                                 |
| Verification            | Before-and-after testing                     |

Four primary scenarios

1. SQL Injection.
2. Excessive Database Privileges.
3. Broken Authorization.
4. Database Network Exposure.

Additional research extensions

- PostgreSQL Row-Level Security.
- Vulnerability chaining.
- Database auditing and detection.
- Quantitative comparison of defensive controls.

## 16. One final idea: make PostgreSQL security itself part of the research

I would not limit the project to attacking PostgreSQL.

We can investigate how its own security mechanisms behave under different conditions.

For example:

| Research experiment  | Question                                                                        |
| -------------------- | ------------------------------------------------------------------------------- |
| Role inheritance     | Can role membership unintentionally grant additional permissions?               |
| PUBLIC privileges    | Are default privileges broader than necessary?                                  |
| RLS                  | Can database policies enforce customer isolation?                               |
| Search path          | Can an unsafe search path create object-resolution risks?                       |
| SECURITY DEFINER     | Can incorrectly configured privileged functions expose additional capabilities? |
| Authentication rules | Can client authentication restrictions prevent unauthorized connections?        |
| TLS                  | Can database traffic confidentiality be protected in transit?                   |
| Audit logging        | Which activities can be detected and investigated?                              |

These are excellent future extensions. We should prioritize the four required attacks first and select additional experiments according to available time.

# 17. What I suggest we settle next

Before implementing anything, there are three architectural decisions still worth finalizing.

First: Application architecture.

My recommendation is FastAPI with REST endpoints. It will let us explicitly study authentication, object-level authorization and database interactions.

Second: Database enforcement.

I recommend comparing application authorization with PostgreSQL RLS rather than treating them as interchangeable.

Third: Research experiment design.

We should establish a formal test-case identifier for every attack, expected result, evidence requirement, remediation and retest result.

My proposed next milestone is:

Next milestone

Borsa — Research Design Document (Version 1.0)

The document should contain:

1. Project background and problem statement.
2. Research objectives and hypotheses.
3. Financial system assets and database entities.
4. Three-VM network architecture.
5. PostgreSQL security architecture.
6. Threat model and attack surface.
7. Four attack scenarios and ATT&CK/CWE mappings.
8. Experimental variables and measurements.
9. Defensive controls and retesting strategy.
10. CVSS methodology and reporting standards.

I would make this document the project's foundation. We should not start installing machines until its architecture and experimental requirements are agreed upon.

Would you like me to review this research design with you weekly and maintain a list of unresolved decisions, completed milestones and next technical tasks?

Weekly Borsa research review