# Quick Start Guide

## ⚠️ IMPORTANT: Python-Only Platform

**This platform uses ONLY Python and Python libraries** (no Docker, no external tools).
Perfect for company laptops with security restrictions.

See [PYTHON_ONLY_DEPLOYMENT.md](PYTHON_ONLY_DEPLOYMENT.md) for detailed company deployment.

## Installation (5 minutes)

```bash
# 1. Navigate to project
cd iam_automation

# 2. Create virtual environment
python -m venv venv

# 3. Activate
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Install packages
pip install -r requirements.txt

# 5. Run UI
streamlit run app.py
```

Browser opens to: http://localhost:8501

## First Time Use

1. **Prepare your files:**
   - Users export CSV
   - Roles export CSV

2. **Upload in UI:**
   - Click Sidebar → User File → Select CSV
   - Click Sidebar → Role File → Select CSV

3. **Run automation:**
   - Click "🚀 Run Automation"
   - Wait for processing
   - See results in tabs

4. **Download outputs:**
   - Tab 1: Summary statistics
   - Tab 2: User details
   - Tab 3: Role details
   - Tab 4: Entitlements
   - Tab 5: Explainability
   - Click "Generate ALL Outputs"

## For Developers

### Run API Only

```bash
python api/server.py
# Runs on http://localhost:5000
```

### Run CLI

```bash
python main.py \
  --user input/users.csv \
  --role input/roles.csv
```

### Run in Docker

```bash
docker build -t iam-tool .
docker run -p 8501:8501 iam-tool
```

## What Gets Stored

**Learning Memory** (`memory/knowledge.json`)

- Successful column mappings
- Confidence scores
- Timestamps

Delete anytime to reset learning.

##Common Issues

| Issue              | Fix                                            |
| ------------------ | ---------------------------------------------- |
| "Module not found" | Run: `pip install -r requirements.txt`         |
| Port 8501 in use   | Run: `streamlit run app.py --server.port=8502` |
| Slow first run     | Normal (downloading semantic model)            |
| CSV encoding issue | Save CSV as UTF-8                              |

## Key Files

- `app.py` - Streamlit UI
- `core/adaptive_engine.py` - Processing logic
- `memory/knowledge.json` - Learning storage
- `output/` - Generated files

## Next Steps

1. Review README.md for full documentation
2. Check API endpoints in api/server.py
3. Customize templates in templates/
4. Adjust config in utils/config.py

For help, see README.md
