---
description: Guide to self-hosting Reacher.email on a VPS for high-accuracy email verification
---

# Self-Host Reacher.email Workflow

This workflow walks you step-by-step through installing Reacher.email on your own VPS.

## Prerequisites
- A VPS with Port 25 open (Recommended: HostCram)
- Ubuntu 22.04 or 24.04
- Root access

## Step 1: Log Into Your Server
Connect to your VPS using SSH.
```bash
ssh root@<YOUR_VPS_IP>
```

## Step 2: Install Docker
Run the following commands to install Docker and Docker Compost.
// turbo
```bash
apt update -y
apt install -y ca-certificates curl gnupg
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" > /etc/apt/sources.list.d/docker.list
apt update -y
apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
systemctl enable --now docker
docker --version
```

## Step 3: Setup Reacher Directory
```bash
mkdir -p /opt/reacher
cd /opt/reacher
```

## Step 4: Create docker-compose.yml
Create `/opt/reacher/docker-compose.yml` with the following content.
**IMPORTANT**: Replace `RCH__API__SECRET`, `RCH__HELLO_NAME`, and `RCH__FROM_EMAIL`.

```yaml
services:
  reacher:
    image: reacherhq/backend:latest
    container_name: reacher
    restart: unless-stopped
    environment:
      - RCH__API__SECRET=CHANGE_THIS_TO_A_LONG_RANDOM_STRING
      - RCH__HELLO_NAME=yourdomain.com
      - RCH__FROM_EMAIL=verify@yourdomain.com
    expose:
      - "8080"

  caddy:
    image: caddy:2
    container_name: caddy
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy_data:/data
      - caddy_config:/config
    depends_on:
      - reacher

volumes:
  caddy_data:
  caddy_config:
```

## Step 5: Configure Caddy (SSL)
Create `/opt/reacher/Caddyfile`:

```
reacher.yourdomain.com {
  reverse_proxy reacher:8080
}
```

## Step 6: DNS Configuration
Point your domain's A record to the VPS IP.
- Type: A
- Name: reacher
- Value: <YOUR_VPS_IP>
- Proxy: DNS Only (if using Cloudflare)

## Step 7: Configure Firewall
```bash
ufw allow 22
ufw allow 80
ufw allow 443
ufw --force enable
```

## Step 8: Start Reacher
```bash
cd /opt/reacher
docker compose up -d
docker ps
```

## Step 9: Verify Port 25
```bash
nc -vz gmail-smtp-in.l.google.com 25
```
