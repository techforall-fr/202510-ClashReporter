# ⚡ Quick Start Guide - 5 Minutes to Demo

## 🚀 Fastest Way to Run (Windows)

### Option 1: PowerShell Script (Recommended)

**Mock Mode (default - no credentials needed):**
```powershell
# Open PowerShell in project root
.\start.ps1
```

**Live Mode (requires APS credentials in .env):**
```powershell
.\start.ps1 -UseLive
```

That's it! The script will:
- ✅ Start backend API (port 8000)
- ✅ Start frontend UI (port 8501)
- ✅ Open browser automatically

### Option 2: Python Demo Script
```powershell
# From project root
cd backend
python -m app.demo --mock
```

---

## 🐧 Quick Start (Linux/Mac)

```bash
# Make script executable
chmod +x start.sh

# Mock Mode (default)
./start.sh

# Live Mode (set USE_MOCK=false in .env first)
USE_MOCK=false ./start.sh

# Or use Python demo
cd backend
python -m app.demo --mock
```

---

## 📦 First Time Setup

### 1. Install Python 3.11+
Download from [python.org](https://www.python.org/downloads/)

### 2. Install Dependencies

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
pip install -r requirements.txt
```

### 3. Run in Mock Mode (No credentials needed!)

```bash
# Quick start script
.\start.ps1          # Windows
./start.sh           # Linux/Mac

# Or manual
cd backend
python -m uvicorn app.main:app --reload

# In another terminal
cd frontend
streamlit run streamlit_app.py
```

### 4. Access Application

- **Frontend:** http://localhost:8501
- **API:** http://localhost:8000
- **Docs:** http://localhost:8000/docs

---

## 🎯 What to Try First

1. **View KPIs**
   - See total clashes, severity distribution
   - Check the charts

2. **Filter Clashes**
   - Sidebar → Select "Haute" severity
   - Table updates instantly

3. **Generate PDF Report**
   - Sidebar → Enter report title
   - Click "🚀 Générer PDF"
   - Download and view PDF

4. **Export CSV**
   - Scroll to table
   - Click "📥 Exporter CSV"

---

## 🔧 Troubleshooting

### "Module not found" errors
```bash
# Reinstall dependencies
cd backend
pip install -r requirements.txt --force-reinstall
```

### Port already in use
```bash
# Change ports in .env
API_PORT=8001
FRONTEND_PORT=8502
```

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.11+

# Try running directly
cd backend
python -m app.main
```

### Frontend connection error
```bash
# Verify backend is running
curl http://localhost:8000/api/health

# Check frontend env
# frontend/.env should have:
API_BASE_URL=http://localhost:8000
```

---

## 📖 Next Steps

- Read [README.md](README.md) for full documentation
- Check [DEMO.md](DEMO.md) for video demo storyboard
- See [CONTRIBUTING.md](CONTRIBUTING.md) to contribute

---

## 🆘 Still Having Issues?

1. Check logs in terminal
2. Verify Python version (3.11+)
3. Ensure all dependencies installed
4. Try mock mode first
5. Open an issue on GitHub

---

**🎉 Enjoy using Smart Clash Reporter!**
