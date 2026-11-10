# Evidence Directory

This directory stores evidence collected during security experiments within the isolated VirtualBox laboratory.

## Structure

```
evidence/
├── screenshots/     # Screen captures from experiments
├── logs/            # Copied application and database log excerpts
└── experiment-results/  # JSON/CSV results from experiment runs
```

## Important Rules

- This directory contains **synthetic data only**
- Never store real customer data, credentials, or production database contents here
- Evidence files are gitignored to prevent accidental disclosure
- Document evidence files in `documentation/09-results-and-analysis.md`

## Naming Convention

```
screenshots/   YYYY-MM-DD_scenario-N_variant-X_description.png
logs/          YYYY-MM-DD_scenario-N_app-or-db.log
experiment-results/  YYYY-MM-DD_scenario-N_variant-X.json
```

