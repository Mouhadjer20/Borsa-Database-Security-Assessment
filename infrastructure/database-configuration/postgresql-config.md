# PostgreSQL 18.x Server Configuration

## 1. `postgresql.conf` Hardening Settings

### Network Binding & Port
```ini
# Listen ONLY on the internal DB-NET interface in Secure Mode
listen_addresses = '192.168.200.30, localhost'
port = 5432
max_connections = 100
```
*(In Vulnerable Lab Variant for Scenario 4, listen_addresses is temporarily altered to `'*'`).*

### TLS / SSL Encryption
```ini
ssl = on
ssl_cert_file = '/etc/ssl/certs/borsa-db.crt'
ssl_key_file = '/etc/ssl/private/borsa-db.key'
ssl_min_protocol_version = 'TLSv1.3'
```

### Logging & Auditing
```ini
logging_collector = on
log_directory = 'log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_connections = on
log_disconnections = on
log_duration = off
log_line_prefix = '%m [%p] %q%u@%d '
log_statement = 'ddl'  # In lab auditing, set to 'all' or configure pgaudit
```

---

## 2. Client Authentication (`pg_hba.conf`)

### A. Secure Mode Configuration
```
# TYPE  DATABASE        USER            ADDRESS                 METHOD
# Local socket connections
local   all             postgres                                peer
local   all             all                                     scram-sha-256

# Application Server on DB-NET (192.168.200.20) only
hostssl borsa           app_readonly    192.168.200.20/32       scram-sha-256
hostssl borsa           app_writer      192.168.200.20/32       scram-sha-256
hostssl borsa           auditor         192.168.200.20/32       scram-sha-256

# Reject all other incoming TCP connections
host    all             all             0.0.0.0/0               reject
```

### B. Vulnerable Lab Configuration (Scenario 4 Network Exposure Demonstration)
```
# Insecure: accepts connection directly from Kali (192.168.100.10) or any subnet
host    borsa           all             192.168.100.0/24        scram-sha-256
host    borsa           app_vulnerable  0.0.0.0/0               scram-sha-256
```

---

## 3. Reloading Configuration
```bash
sudo systemctl reload postgresql
# Or from psql:
# SELECT pg_reload_conf();
```

