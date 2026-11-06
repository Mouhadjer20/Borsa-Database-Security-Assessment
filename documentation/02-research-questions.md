# 02 — Research Questions and Hypotheses

## Main Research Question

> To what extent do application-level SQL injection vulnerabilities, excessive database privileges, broken authorization mechanisms, and database network exposure compromise the confidentiality and integrity of a relational database system in a simulated financial institution, and how effectively can layered security controls mitigate these risks?

## Specific Research Questions

| ID | Question |
|---|---|
| RQ1 | Can SQL injection expose financial records despite normal database authentication? |
| RQ2 | Can excessive database privileges allow an application account to perform unauthorized operations? |
| RQ3 | Can authenticated users access financial resources belonging to other customers? |
| RQ4 | Can network exposure allow unauthorized clients to establish database connections? |
| RQ5 | How do parameterized queries, least privilege, authorization controls, and network segmentation reduce these risks? |
| RQ6 | Can database audit logs provide sufficient evidence to detect the simulated unauthorized activities? |
| RQ7 | Does combining multiple weaknesses produce a greater impact than exploiting each weakness individually? |

## Hypotheses

| ID | Hypothesis |
|---|---|
| H1 | Unsafe SQL query construction permits manipulation of query semantics. |
| H2 | Excessive privileges increase the operations available to a compromised application account. |
| H3 | Missing object-level authorization permits cross-customer resource access. |
| H4 | Unrestricted database connectivity increases the number of possible access paths. |
| H5 | Applying the corresponding defensive controls reduces or eliminates the demonstrated unauthorized operations. |
| H6 | Combining application and database weaknesses increases the potential impact of an individual weakness. |

## Evaluation Criteria

- Each hypothesis is evaluated using predefined test cases with fixed accounts, data, and initial conditions.
- Outcomes are recorded as observed/not observed plus counts (records accessed/modified, operations permitted/blocked, connections succeeded/failed, events logged).
- A hypothesis is supported only by evidence collected in the lab (application logs, database logs, network observations, test results, screenshots).
- CVSS v4.0 scores reflect demonstrated behavior; pre/post scores are compared only when reassessment is justified by changed conditions.
