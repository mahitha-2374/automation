# IAM Automation Platform

**Adaptive • Semantic • Self-Learning • Explainable**

A production-ready IAM automation platform that processes user and role exports to generate DSAP, T3, and OLA documentation automatically.

## Features

✨ **Core Capabilities**

- Adaptive schema detection (handles any column naming)
- Semantic intelligence (understands IAM concepts)
- Self-learning memory (improves over time)
- Explainability layer (audit-ready)
- No external APIs (fully offline)

📊 **Outputs**

- T3 Excel files (XLSM with formulas preserved)
- OLA Word documents (template-based)
- Audit reports (mapping explanations)

🚀 **Interfaces**

- Streamlit UI (user-friendly)
- Flask REST API (programmatic)
- CLI (command-line)

## Installation

### Requirements (Python-Only - No External Tools)

✅ **Python 3.10+** (install from python.org)  
✅ **2GB RAM minimum**  
✅ **500MB disk space for AI models**  
✅ **8 Python libraries via pip** (see requirements.txt)

**No Docker • No Node.js • No system tools required**  
**Perfect for company/restricted laptops**

👉 **For company deployment:** See [PYTHON_ONLY_DEPLOYMENT.md](PYTHON_ONLY_DEPLOYMENT.md)

### Setup

```bash
# Clone or download the project
cd iam_automation

# Create virtual environment
python -m venv venv

# Activate
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# First run (downloads semantic model ~200MB)
streamlit run app.py
```

## Usage

### Web UI (Recommended)

```bash
streamlit run app.py
```

Open http://localhost:8501 in browser

**Steps:**

1. Upload user export CSV
2. Upload role export CSV
3. Click "Run Automation"
4. Review results in tabs
5. Download T3, OLA, or Report

### REST API

```bash
# Terminal 1: Start API
python api/server.py

# Terminal 2: Process files
curl -X POST http://localhost:5000/process \
  -F "user_file=@users.csv" \
  -F "role_file=@roles.csv"
```

**Endpoints:**

- `GET /health` - Health check
- `POST /process` - Process and return JSON
- `POST /process/excel` - Process and download Excel
- `POST /process/word` - Process and download Word
- `GET /learning/memory` - View learned mappings
- `DELETE /learning/memory` - Clear memory

### Command Line

```bash
python main.py \
  --user input/users.csv \
  --role input/roles.csv \
  --output-dir output
```

**Options:**

- `--no-excel` - Skip Excel generation
- `--no-word` - Skip Word generation
- `--no-report` - Skip Report generation

### Docker

```bash
# Build
docker build -t iam-tool .

# Run UI
docker run -p 8501:8501 -p 5000:5000 iam-tool

# With volume mount
docker run -v $(pwd)/input:/app/input \
           -v $(pwd)/output:/app/output \
           -p 8501:8501 \
           iam-tool
```

## Input Format

### User Export (CSV)

Supports any schema. Examples:

```
user_id,role_name,status
UBOC-AD\user1,Admin,Active
UBOC-AD\user2,Viewer,Active
```

Or:

```
login_id,access_group
A001,Platform Admin
A002,Viewer
```

### Role Export (CSV)

Supports any schema. Examples:

```
role,permission,module
Admin,Create,System
Admin,Delete,System
Viewer,Read,System
```

Or:

```
role_name,entitlement,module
Platform_Admin,Modify_Security,Admin
Platform_Admin,Execute_Catalog,Catalog
```

## Output Files

### T3_output.xlsm

Multi-sheet Excel with:

- User_role_resource (users and their roles)
- Role_Resource (roles and entitlements)
- Role_resource_lookup (reference data)
- User_Account_lookup (user details)
- Control sheet (row counts and run date)

### OLA_output.docx

Service Level Agreement document with:

- System information
- User/role/entitlement counts
- Mapping details
- Control descriptions

### explainability_report.xlsx

Audit report showing:

- Every column mapping
- Confidence scores
- Mapping source (learned/semantic/rule)
- Summary statistics

## How It Works

### Schema Detection Pipeline

```
Input CSV
    ↓
Semantic Engine (checks memory)
    ↓
Column Classification
    ↓
Confidence Scoring
    ↓
Learning Storage
    ↓
Mapped Schema
```

### Intelligent Features

**1. Semantic Understanding**

```
Column "Access_Bundle" → Recognized as "role"
Column "Capability" → Recognized as "entitlement"
Column "Platform_Area" → Recognized as "module"
```

**2. Self-Learning**

- First run: Uses semantic matching
- Subsequent runs: Uses learned mappings (faster)
- Memory stored in `memory/knowledge.json`

**3. Explainability**
Shows why each column was mapped:

- Confidence score (0-1)
- Source (learned/semantic/rule)
- Reasoning

## Project Structure

```
iam_automation/
├── app.py                     # Streamlit UI
├── main.py                    # CLI entry
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker build
│
├── core/                      # Intelligence layer
│   ├── adaptive_engine.py     # Main processor
│   ├── semantic_engine.py     # Semantic matching
│   ├── learning_engine.py     # Learning memory
│   └── explainer.py           # Explainability
│
├── generators/                # Output generation
│   ├── excel_generator.py     # T3 Excel
│   ├── word_generator.py      # OLA Word
│   └── report_generator.py    # Audit reports
│
├── api/                       # REST API
│   └── server.py              # Flask app
│
├── utils/                     # Utilities
│   └── config.py              # Configuration
│
├── memory/                    # Learning storage
│   └── knowledge.json         # Learned mappings
│
├── input/                     # Input files (your data)
├── output/                    # Generated outputs
├── templates/                 # Excel/Word templates
└── logs/                      # Application logs
```

## Performance

- **Small datasets** (< 1GB): < 10 seconds
- **Medium datasets** (1-10GB): < 1 minute
- **Large datasets** (> 10GB): Depends on system RAM

## Troubleshooting

### Issue: Low confidence mappings

**Solution:** Review in "Explainability" tab and manually correct if needed. System will learn from corrections.

### Issue: Missing columns in output

**Solution:** Ensure all required columns (user, role, entitlement) present in export files. Check explanation report.

### Issue: Out of memory on large files

**Solution:**

1. Split files into smaller batches
2. Increase system RAM
3. Use streaming mode (if available)

### Issue: Templates not found

**Solution:** Place Excel/Word templates in `templates/` folder with correct names:

- `T3_template.xlsm`
- `OLA_template.docx`

## Advanced Usage

### Confidence Threshold

Adjust in UI via sidebar slider to:

- Filter low-confidence mappings
- See warnings in explainability tab

### Clear Learning Memory

```bash
curl -X DELETE http://localhost:5000/learning/memory
```

Or via API call to reset all learned mappings.

### Custom Templates

1. Prepare Excel/Word templates
2. Place in `templates/` folder
3. System will auto-fill all data sections

## Architecture Highlights

| Component      | Purpose                                      |
| -------------- | -------------------------------------------- |
| SemanticEngine | Understands column meaning via ML embeddings |
| LearningEngine | Stores & reuses successful mappings          |
| AdaptiveEngine | Orchestrates entire pipeline                 |
| Explainer      | Generates audit trails                       |
| ExcelGenerator | Safe formulae-preserving output              |
| WordGenerator  | Template-based document generation           |

## API Examples

### Process and Download Excel

```bash
curl -X POST http://localhost:5000/process/excel \
  -F "user_file=@users.csv" \
  -F "role_file=@roles.csv" \
  -o output.xlsm
```

### Detect Schema Only

```bash
curl -X POST http://localhost:5000/schema/detect \
  -F "file=@users.csv" | jq .
```

### Get Learning Memory

```bash
curl http://localhost:5000/learning/memory | jq .
```

## License

Internal Use Only - Company Proprietary

## Contact

For questions or issues, contact your IAM team or platform administrator.

---

**Built with Python • Powered by Semantic AI • Enterprise Ready** ✨
