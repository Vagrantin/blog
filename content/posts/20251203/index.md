{
  "title": "Raspberry Pi Router & DNS Server Setup",
  "publishDate": "2025-12-03T09:00:00+09:00",
  "draft": false,
  "url": "/20251203/raspberry-router-dns.html",
  "params": {
    "legacy": true
  },
  "description": "Context: I’m in the process of setting up a wired home network, and while my cabling is ready, my network rack isn’t set up yet. In the meantime, I’m using my Raspberry Pi as an internal router for my wired…"
}

## Using a Raspberry Pi as a Wired Network Router and DNS Server

**Context:** I’m in the process of setting up a wired home network, and while my cabling is ready, my network rack isn’t set up yet. In the meantime, I’m using my Raspberry Pi as an internal router for my wired machines. Here’s how I configured it to route traffic between my wired LAN (*eth0*) and WiFi (*wlan0*), and also act as a DNS server for my local network.

### 1. Update and Install Required Packages

First, update your system and install the necessary packages:

*sudo apt update && sudo apt upgrade -y*

*sudo apt install dnsmasq iptables*

*sudo apt install iptables-persistent*

### 2. Enable IP Forwarding

Edit */etc/sysctl.conf* and add the following lines to enable IP forwarding and disable IPv6 (if not needed):

*net.ipv4.ip_forward=1*

*net.ipv6.conf.all.disable_ipv6=1*

*net.ipv6.conf.default.disable_ipv6=1*

Apply the changes and enable the *sysctl* service:

*sudo sysctl -p*

*sudo systemctl enable systemd-sysctl*

*sudo systemctl start systemd-sysctl*

### 3. Configure iptables for NAT and Forwarding

Set up NAT and forwarding rules:

*sudo iptables -t nat -A POSTROUTING -o wlan0 -j MASQUERADE*

*sudo iptables -A FORWARD -i wlan0 -o eth0 -m state --state RELATED,ESTABLISHED -j ACCEPT*

*sudo iptables -A FORWARD -i eth0 -o wlan0 -j ACCEPT*

Save the iptables configuration to persist after reboot:

*sudo netfilter-persistent save*

At this point, your wired machines should be able to access the internet through the Raspberry Pi!

### 4. Disable WiFi Power Management for Stability

Create or edit */etc/rc.local*:

*sudo nano /etc/rc.local*

Add the following content to disable WiFi power saving:

*\#!/bin/sh -e*

*\#*

*\# rc.local*

*\#*

*\# This script is executed at the end of each multiuser runlevel.*

*\# Make sure that the script will "exit 0" on success or any other*

*\# value on error.*

*\#*

*\# By default, this script does nothing.*

*\# Disable WiFi power saving*

*iwconfig wlan0 power off*

*exit 0*

Make it executable and enable the service:

*sudo chmod +x /etc/rc.local*

*sudo systemctl enable rc-local*

*sudo systemctl start rc-local*

Verify the setting:

*iwconfig wlan0 \| grep "Power Management"*

* \> Power Management:off*

### 5. Ensure IP Forwarding Persists After Reboot

Unfortunately, IP forwarding is still being disabled at boot. To fix this, I created a custom service that should start late in the boot process to avoid the config to be overwritten:

Create */etc/systemd/system/late-ip-forward.service*:

*\[Unit\]*

*Description=Set IP forwarding (late)*

*After=network-online.target dnsmasq.service netfilter-persistent.service NetworkManager-wait-online.service*

*Wants=network-online.target*

*\[Service\]*

*Type=oneshot*

*ExecStart=/sbin/sysctl -w net.ipv4.ip_forward=1*

*\[Install\]*

*WantedBy=multi-user.target*

Enable the service:

*sudo systemctl daemon-reload*

*sudo systemctl enable late-ip-forward.service*

Reboot your Raspberry Pi. IP forwarding is now persistent!

### 6. Configure dnsmasq for Local DNS Resolution

I want my RPI to be the DNS server for my internal network, I’m using dnsmasq to handle that.

Edit */etc/dnsmasq.conf*:

*\# Listen only on the wired LAN interface (eth0)*

*interface=eth0*

*\# Specify the local domain*

*local=/mydomain.local/*

*\# Forward DNS requests for non-local domains to upstream DNS (via wlan0)*

*server=1.1.1.1*

*server=8.8.8.8*

*\# Use /etc/hosts for local hostname lookup*

*addn-hosts=/etc/hosts*

Add your local hosts to */etc/hosts*:

*192.168.1.1 rpi.mydomain.local*

*192.168.1.100 machine1.mydomain.local*

**\# Add more entries as needed**

Restart *dnsmasq*:

*sudo systemctl restart dnsmasq*

Now, you can ping machines by their fully qualified domain names (FQDN):

*ping rpi.mydomain.local*

### 7. Simplify Access with Search Domains

To avoid typing the full FQDN, update your client’s network configuration to include the search domain. On Ubuntu (and flavors), edit your Netplan config (e.g., */etc/netplan/01-netcfg.yaml*):

*network:*

* version: 2*

* renderer: networkd*

* ethernets:*

* eth0:*

* dhcp4: no*

* addresses: \[192.168.1.100/24\]*

* gateway4: 192.168.1.1*

* nameservers:*

* addresses: \[192.168.1.1\] *\# Your RPi's IP (DNS server)**

* search: \[mydomain.local\]*

Apply the changes:

*sudo netplan apply*

Now, you can ping machines using just their hostnames:

*ping pi*

### Conclusion

With these steps, your Raspberry Pi is now acting as both a router and a DNS server for your local network. Your wired machines can access the internet, and you can resolve local hostnames easily. This setup is a great temporary solution while I’m preparing my more permanent network infrastructure.
