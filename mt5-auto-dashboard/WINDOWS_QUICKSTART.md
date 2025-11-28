# MT5 Auto Dashboard - Windows Quick Start Guide

## 🚀 Quick Setup (3 Simple Steps)

### Step 1: Install Python (if not already installed)

1. Download Python 3.8 or higher from [python.org](https://www.python.org/downloads/)
2. **IMPORTANT**: Check "Add Python to PATH" during installation
3. Restart your computer after installation

### Step 2: Run Setup

1. Open the project folder
2. **Double-click** `setup_windows.bat`
3. Wait for installation to complete (may take a few minutes)

### Step 3: Start Dashboard

1. **Double-click** `start_dashboard.bat`
2. Open your browser to: `http://localhost:8050`

That's it! 🎉

---

## 📁 File Structure Overview

```
mt5_auto_dashboard/
├── setup_windows.bat          ← Run this FIRST (one-time setup)
├── start_dashboard.bat        ← Run this to start dashboard
├── config/
│   └── settings.yaml          ← Configure MT5 data paths here
├── data/
│   └── Dummy_Data_dir/        ← Sample MT5 data
└── venv/                      ← Created by setup (Python environment)
```

---

## ⚙️ Configuration

### Configure MT5 Data Sources

Edit `config\settings.yaml` with your MT5 terminal paths:

```yaml
mt5_sources:
  - name: "Trading Account 1"
    path: "C:\\Users\\YourName\\AppData\\Roaming\\MetaQuotes\\Terminal\\XXXXX\\MQL5\\Files\\MT5_Data"
    enabled: true
    
  - name: "Trading Account 2"
    path: "C:\\Users\\YourName\\AppData\\Roaming\\MetaQuotes\\Terminal\\YYYYY\\MQL5\\Files\\MT5_Data"
    enabled: true
```

**Finding Your MT5 Terminal Path:**
1. Open MT5
2. Go to: **File → Open Data Folder**
3. Navigate to: `MQL5\Files\MT5_Data`
4. Copy the full path and paste into `settings.yaml`

---

## 🎯 Usage

### Starting the Dashboard

**Method 1: Double-click** (Easiest)
- Double-click `start_dashboard.bat`
- Window will open showing status
- Keep window open while using dashboard

**Method 2: Command Prompt**
```cmd
start_dashboard.bat
```

### Stopping the Dashboard

- Press `Ctrl+C` in the command window
- Or simply close the window

### Accessing the Dashboard

Open your web browser and go to:
- `http://localhost:8050`

---

## 🔧 Troubleshooting

### "Python is not installed or not in PATH"

**Solution:**
1. Reinstall Python from [python.org](https://www.python.org/downloads/)
2. Make sure to check "Add Python to PATH" ✅
3. Restart your computer
4. Run `setup_windows.bat` again

### "Required packages not installed"

**Solution:**
```cmd
setup_windows.bat
```
This will install all required packages.

### Dashboard won't start

**Solution:**
1. Open Command Prompt as Administrator
2. Navigate to project folder:
   ```cmd
   cd C:\path\to\mt5_auto_dashboard
   ```
3. Run setup again:
   ```cmd
   setup_windows.bat
   ```

### Port 8050 already in use

**Solution:**
Edit `config\settings.yaml` and change the port:
```yaml
dashboard:
  port: 8051  # Change to different port
```

### No data showing in dashboard

**Check:**
1. MT5 data paths in `config\settings.yaml` are correct
2. MT5 EA is exporting data properly
3. CSV files exist in the MT5_Data folders

---

## 📝 Advanced Options

### Running as Windows Service

For 24/7 operation, you can run the dashboard as a Windows Service:

**Option 1: Using NSSM (Non-Sucking Service Manager)**
1. Download [NSSM](https://nssm.cc/download)
2. Open Command Prompt as Administrator
3. Install service:
   ```cmd
   nssm install MT5Dashboard "C:\path\to\mt5_auto_dashboard\venv\Scripts\python.exe" "C:\path\to\mt5_auto_dashboard\start_dashboard.py"
   nssm set MT5Dashboard AppDirectory "C:\path\to\mt5_auto_dashboard"
   nssm start MT5Dashboard
   ```

**Option 2: Using Task Scheduler**
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: "When computer starts"
4. Action: "Start a program"
5. Program: `C:\path\to\mt5_auto_dashboard\start_dashboard.bat`

### Accessing from Other Devices (Network)

1. Edit `config\settings.yaml`:
   ```yaml
   dashboard:
     host: "0.0.0.0"  # Allow network access
   ```

2. Configure Windows Firewall:
   - Open Windows Defender Firewall
   - Advanced Settings → Inbound Rules → New Rule
   - Port: 8050, TCP
   - Allow the connection

3. Find your PC's IP address:
   ```cmd
   ipconfig
   ```

4. Access from other devices:
   `http://YOUR_PC_IP:8050`

---

## 🔄 Updating

To update the dashboard:

1. Stop the dashboard (Ctrl+C)
2. Get latest version (if using Git):
   ```cmd
   git pull
   ```
3. Update packages:
   ```cmd
   setup_windows.bat
   ```
4. Restart dashboard:
   ```cmd
   start_dashboard.bat
   ```

---

## 📊 System Requirements

- **OS**: Windows 10 or Windows 11
- **Python**: 3.8 or higher
- **RAM**: Minimum 2GB (4GB recommended)
- **Browser**: Chrome, Firefox, or Edge (latest versions)

---

## 🆘 Getting Help

### Check Logs

Logs are stored in the `logs/` folder. Check these for error details.

### Common Commands

```cmd
# Check Python version
python --version

# Check installed packages
pip list

# Reinstall requirements
pip install -r requirements.txt

# Test dashboard manually
python start_dashboard.py
```

---

## ✅ Checklist

- [ ] Python 3.8+ installed with "Add to PATH" ✅
- [ ] Ran `setup_windows.bat` successfully
- [ ] Configured MT5 paths in `config\settings.yaml`
- [ ] Dashboard starts without errors
- [ ] Can access dashboard at `http://localhost:8050`
- [ ] MT5 data is showing correctly

---

## 🎓 Tips

1. **Keep the command window open** - Closing it stops the dashboard
2. **Bookmark the URL** - `http://localhost:8050` for quick access
3. **Check logs** - If something goes wrong, check the `logs/` folder
4. **Regular updates** - Update your MT5 EA and dashboard regularly
5. **Backup settings** - Keep a backup of your `settings.yaml` file

---

Happy Trading! 📈

For more detailed information, see:
- `README.md` - Full project documentation
- `DEPLOYMENT_GUIDE.md` - Advanced deployment options
