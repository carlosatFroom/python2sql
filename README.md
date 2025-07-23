Installing MariaDB in Proxmox LXC
# Install MariaDB server
apt install mariadb-server mariadb-client -y

# Secure installation (set root password)
mysql_secure_installation

# Edit bind-address to allow external connections
nano /etc/mysql/mariadb.conf.d/50-server.cnf
# Find line "bind-address = 127.0.0.1" and change to:
bind-address = 0.0.0.0
Create privileged user for external access
# Connect to MariaDB
mysql -u root -p

CREATE USER 'admin'@'%' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON *.* TO 'admin'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;
EXIT;
Configure firewall in Proxmox host
# Allow port 3306 TCP traffic to your LXC container
iptables -A FORWARD -p tcp --dport 3306 -d [LXC_CONTAINER_IP] -j ACCEPT
Restart MariaDB
systemctl restart mariadb
Test connection from remote machine
mysql -h [LXC_CONTAINER_IP] -u admin -p
Security note
This configuration allows connections from any IP address. For production:

Restrict user to specific IP: CREATE USER 'admin'@'192.168.1.100'
Use firewall rules to limit source IPs
Consider TLS connections for WAN access
