# MT5 Auto Dashboard - VPS Deployment Guide

## 📋 Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+ recommended) or Windows Server
- **Python**: 3.8 or higher
- **RAM**: Minimum 2GB (4GB recommended)
- **Storage**: Minimum 5GB free space
- **Network**: Port 8050 accessible (or your configured port)

### Software Requirements
- Python 3.8+
- pip (Python package manager)
- Git (optional, for cloning repository)

---

## 🚀 Deployment Steps

### Step 1: Connect to Your VPS

#### Using SSH (Linux/Mac/Windows PowerShell)
```bash
ssh username@your-vps-ip
```

#### Using PuTTY (Windows)
- Host: `your-vps-ip`
- Port: `22`
- Connection Type: SSH

---

### Step 2: Install Python and Dependencies

#### For Ubuntu/Debian:
```bash
# Update package list
sudo apt update

# Install Python 3 and pip
sudo apt install python3 python3-pip python3-venv -y

# Verify installation
python3 --version
pip3 --version
```

#### For Windows Server:
1. Download Python from https://www.python.org/downloads/
2. Run installer (check "Add Python to PATH")
3. Verify: `python --version`

---

### Step 3: Upload/Clone Your Project

#### Option A: Upload via SCP (from your local machine)
```bash
# From your local machine
scp -r /path/to/mt5_auto_dashboard username@your-vps-ip:/home/username/
```

#### Option B: Upload via SFTP
Use FileZilla or WinSCP to transfer files

#### Option C: Clone from Git (if using repository)
```bash
cd /home/username
git clone https://github.com/your-repo/mt5_auto_dashboard.git
cd mt5_auto_dashboard
```

---

### Step 4: Set Up Virtual Environment (Recommended)

```bash
# Navigate to project directory
cd /home/username/mt5_auto_dashboard

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip
```

---

### Step 5: Install Python Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

If `requirements.txt` doesn't exist, install manually:
```bash
pip install dash dash-bootstrap-components plotly pandas pyyaml
```

---

### Step 6: Configure MT5 Data Sources

Edit `config/settings.yaml` to point to your MT5 data directories:

```yaml
mt5_sources:
  - name: "EA-1"
    path: "/path/to/mt5/terminal1/MQL5/Files/MT5_Data"
    enabled: true
    description: "First trading terminal"
    
  - name: "EA-2"
    path: "/path/to/mt5/terminal2/MQL5/Files/MT5_Data"
    enabled: true
    description: "Second trading terminal"
```

Also configure the dashboard settings:
```yaml
dashboard:
  port: 8050
  host: "0.0.0.0"  # Important: Use 0.0.0.0 to allow external access
  debug: false
  update_interval: 5000  # UI refresh (5 seconds)
  data_refresh_interval: 300000  # Data re-processing (5 minutes)
```

---

### Step 7: Test the Application

```bash
# Start the dashboard
python start_dashboard.py
```

You should see:
```
============================================================
MT5 Auto Dashboard starting...
Dashboard URL: http://0.0.0.0:8050
============================================================
```

Test locally first:
- If on VPS: `curl http://localhost:8050`
- Check for errors in terminal output

Press `CTRL+C` to stop.

---

### Step 8: Configure Firewall

#### Ubuntu/Debian (UFW):
```bash
# Allow port 8050
sudo ufw allow 8050/tcp

# Check status
sudo ufw status
```

#### CentOS/RHEL (firewalld):
```bash
sudo firewall-cmd --permanent --add-port=8050/tcp
sudo firewall-cmd --reload
```

#### Cloud Provider Firewall:
- AWS: Configure Security Group
- Azure: Configure Network Security Group
- Google Cloud: Configure Firewall Rules
- DigitalOcean: Configure Cloud Firewall

Add inbound rule:
- Protocol: TCP
- Port: 8050
- Source: Your IP or 0.0.0.0/0 (public access)

---

### Step 9: Run as Background Service (Production)

#### Option A: Using systemd (Linux - Recommended)

Create service file:
```bash
sudo nano /etc/systemd/system/mt5-dashboard.service
```

Add the following content:
```ini
[Unit]
Description=MT5 Auto Dashboard
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/home/your-username/mt5_auto_dashboard
Environment="PATH=/home/your-username/mt5_auto_dashboard/venv/bin"
ExecStart=/home/your-username/mt5_auto_dashboard/venv/bin/python start_dashboard.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Replace `your-username` with your actual username.

Enable and start the service:
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable mt5-dashboard

# Start the service
sudo systemctl start mt5-dashboard

# Check status
sudo systemctl status mt5-dashboard

# View logs
sudo journalctl -u mt5-dashboard -f
```

Service management commands:
```bash
# Stop service
sudo systemctl stop mt5-dashboard

# Restart service
sudo systemctl restart mt5-dashboard

# Disable service
sudo systemctl disable mt5-dashboard
```

#### Option B: Using nohup (Simple Background Process)

```bash
# Start in background
nohup python start_dashboard.py > dashboard.log 2>&1 &

# Find process ID
ps aux | grep start_dashboard.py

# Stop process
kill <process-id>
```

#### Option C: Using screen (Session Management)

```bash
# Install screen
sudo apt install screen

# Create new screen session
screen -S mt5-dashboard

# Start dashboard
python start_dashboard.py

# Detach from screen: Press CTRL+A then D

# Reattach to screen
screen -r mt5-dashboard

# List screens
screen -ls
```

---

### Step 10: Access Your Dashboard

#### From Browser:
```
http://your-vps-ip:8050
```

Example:
- `http://192.168.1.100:8050`
- `http://your-domain.com:8050`

---

## 🔒 Security Best Practices

### 1. Use Reverse Proxy with NGINX (Recommended)

Install NGINX:
```bash
sudo apt install nginx -y
```

Create NGINX configuration:
```bash
sudo nano /etc/nginx/sites-available/mt5-dashboard
```

Add configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8050;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/mt5-dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

Now access via: `http://your-domain.com`

### 2. Enable HTTPS with SSL Certificate

Using Let's Encrypt (Free):
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d your-domain.com

# Certificate auto-renewal is configured automatically
```

Access via: `https://your-domain.com`

### 3. Add Basic Authentication

```bash
# Install apache2-utils
sudo apt install apache2-utils -y

# Create password file
sudo htpasswd -c /etc/nginx/.htpasswd username

# Update NGINX config
sudo nano /etc/nginx/sites-available/mt5-dashboard
```

Add to location block:
```nginx
auth_basic "Restricted Access";
auth_basic_user_file /etc/nginx/.htpasswd;
```

Restart NGINX:
```bash
sudo systemctl restart nginx
```

### 4. Use VPN for Access

- Set up WireGuard or OpenVPN
- Only allow dashboard access from VPN network
- Block port 8050 from public internet

---

## 📊 Monitoring & Maintenance

### Check Service Status
```bash
sudo systemctl status mt5-dashboard
```

### View Live Logs
```bash
# systemd service logs
sudo journalctl -u mt5-dashboard -f

# Application logs (if using nohup)
tail -f dashboard.log
```

### Check Resource Usage
```bash
# CPU and Memory
htop

# Disk space
df -h

# Process specific
ps aux | grep python
```

### Restart Dashboard
```bash
sudo systemctl restart mt5-dashboard
```

---

## 🔄 Updating the Application

```bash
# Stop service
sudo systemctl stop mt5-dashboard

# Navigate to project directory
cd /home/username/mt5_auto_dashboard

# Activate virtual environment
source venv/bin/activate

# Pull updates (if using git)
git pull

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart service
sudo systemctl start mt5-dashboard
```

---

## 🐛 Troubleshooting

### Dashboard Won't Start

**Check logs:**
```bash
sudo journalctl -u mt5-dashboard -n 50
```

**Common issues:**
1. Port already in use:
   ```bash
   sudo lsof -i :8050
   # Kill process if needed
   sudo kill <PID>
   ```

2. Permission errors:
   ```bash
   # Fix permissions
   sudo chown -R your-username:your-username /home/username/mt5_auto_dashboard
   ```

3. Python package missing:
   ```bash
   # Reinstall requirements
   pip install -r requirements.txt
   ```

### Can't Access Dashboard Remotely

1. Check firewall rules
2. Verify dashboard is listening on `0.0.0.0` not `127.0.0.1`
3. Check cloud provider security groups
4. Test with curl: `curl http://localhost:8050`

### Data Not Updating

1. Check MT5 data paths in `config/settings.yaml`
2. Verify file permissions for MT5 data directories
3. Check logs for processing errors
4. Manually test data processor:
   ```bash
   python -c "from core.data_processor import MT5DataProcessor; MT5DataProcessor().process_all_sources()"
   ```

---

## 📝 Quick Reference Commands

```bash
# Start dashboard (foreground)
python start_dashboard.py

# Start service (background)
sudo systemctl start mt5-dashboard

# Stop service
sudo systemctl stop mt5-dashboard

# Restart service
sudo systemctl restart mt5-dashboard

# View logs
sudo journalctl -u mt5-dashboard -f

# Check status
sudo systemctl status mt5-dashboard

# Test connection
curl http://localhost:8050
```

---

## 🎯 Summary Checklist

- [ ] VPS server set up and accessible
- [ ] Python 3.8+ installed
- [ ] Project files uploaded to VPS
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Configuration file updated
- [ ] Firewall configured
- [ ] Dashboard tested locally
- [ ] Service configured (systemd)
- [ ] Dashboard accessible remotely
- [ ] Security measures implemented (NGINX, SSL)
- [ ] Monitoring set up

---

## 📞 Need Help?

If you encounter issues:
1. Check logs: `sudo journalctl -u mt5-dashboard -f`
2. Verify configuration: `cat config/settings.yaml`
3. Test manually: `python start_dashboard.py`
4. Check firewall: `sudo ufw status`
5. Review this guide for missed steps

Happy Trading! 📈
