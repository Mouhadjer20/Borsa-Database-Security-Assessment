# Firewall Policies and Rules

## 1. Overview
Host-based firewall rules enforce strict micro-segmentation across the 3 virtual machines.

---

## 2. VM 2: Application Server Rules

The application server accepts incoming traffic on ports 5173/8000 only from `AUDIT-NET` (`192.168.100.0/24`), and initiates outbound connections to PostgreSQL on `DB-NET` (`192.168.200.30:5432`).

### UFW Commands:
```bash
# Reset UFW to default deny
sudo ufw default deny incoming
sudo ufw default deny outgoing

# Allow loopback
sudo ufw allow in on lo
sudo ufw allow out on lo

# Allow inbound HTTP/API from AUDIT-NET only
sudo ufw allow in on eth0 from 192.168.100.0/24 to 192.168.100.20 port 8000 proto tcp
sudo ufw allow in on eth0 from 192.168.100.0/24 to 192.168.100.20 port 5173 proto tcp

# Allow outbound database queries to VM 3 only
sudo ufw allow out on eth1 to 192.168.200.30 port 5432 proto tcp

# Enable firewall
sudo ufw enable
```

### iptables Equivalent:
```bash
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT DROP

iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

# Accept established / related
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -A OUTPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# Allow API & UI traffic from AUDIT-NET
iptables -A INPUT -i eth0 -s 192.168.100.0/24 -p tcp -m multiport --dports 5173,8000 -j ACCEPT

# Allow egress to PostgreSQL on DB-NET
iptables -A OUTPUT -o eth1 -d 192.168.200.30 -p tcp --dport 5432 -j ACCEPT
```

---

## 3. VM 3: Database Server Rules

The PostgreSQL server must strictly reject all incoming connections except those originating from the Application Server (`192.168.200.20`).

### UFW Commands:
```bash
sudo ufw default deny incoming
sudo ufw default deny outgoing

sudo ufw allow in on lo
sudo ufw allow out on lo

# Allow PostgreSQL incoming traffic strictly from App Server IP
sudo ufw allow in on eth0 from 192.168.200.20 to 192.168.200.30 port 5432 proto tcp

# Allow established response traffic
sudo ufw allow out on eth0 to 192.168.200.20 proto tcp

sudo ufw enable
```

---

## 4. Verification Commands
```bash
# Verify active iptables filter rules
sudo iptables -L -n -v

# Check listening sockets on VM 2 / VM 3
ss -tulpn
```

