# Quick Start: GSI & Template Enhancement

## 🚀 What's New?

The application now supports:

- **GSI Filtering**: Extract and filter data by Global System Identifier
- **Multiple Templates**: Choose from Excel, Word, and PDF output templates
- **Personalized Exports**: Combine templates with GSI data for targeted outputs
- **Audit Trails**: Professional audit reports with detailed mappings

## ⚡ 5-Minute Setup

### 1. Install Dependencies

```bash
pip install reportlab>=4.0.0
```

### 2. Web UI - Basic Usage

**Path**: User uploads CSV → GSI ID → Choose Template → Export

```
Step 1: Upload Files
  - User export (CSV)
  - Role export (CSV)

Step 2: Enter GSI ID
  - Application or system identifier
  - Auto-filled if column exists in CSV

Step 3: Choose Export Mode
  - Single Template: One output format
  - Multiple Templates: Several output formats
  - All GSI-Aware: Comprehensive coverage
  - By Format: All in Excel/Word/PDF

Step 4: Configure Options
  ✓ Include GSI Metadata (recommended)
  ✓ Include Explanations (recommended)
  ✓ Generate Audit Trail (optional)

Step 5: Export
  Click "✨ Generate Outputs with Template"
```

### 3. CLI - Basic Usage

**Simplest command:**

```bash
python main.py --user users.csv --role roles.csv --gsi-id MyApp_001
```

**Generate specific template:**

```bash
python main.py --user users.csv --role roles.csv --gsi-id MyApp_001 \
  --export-mode single --templates T3_Standard
```

**Generate all templates:**

```bash
python main.py --user users.csv --role roles.csv --gsi-id MyApp_001 \
  --export-mode all-gsi-aware
```

## 📋 Available Templates

| Template          | Format | Purpose                     |
| ----------------- | ------ | --------------------------- |
| T3_Standard       | Excel  | User-Role-Resource mapping  |
| OLA_Standard      | Word   | Service organization outage |
| Executive_Summary | PDF    | High-level overview         |
| Detailed_Report   | PDF    | Complete analysis           |
| IAM_Audit         | Excel  | Full audit trail            |

## 🎯 Common Use Cases

### Case 1: One-Time Export for Stakeholder

```bash
python main.py --user users.csv --role roles.csv --gsi-id SAP_001 \
  --export-mode single --templates Executive_Summary
# Generates: Executive summary PDF
```

### Case 2: All-Format Export for Compliance

```bash
python main.py --user users.csv --role roles.csv --gsi-id Compliance_App \
  --export-mode all-gsi-aware --include-audit-trail
# Generates: All templates + audit trail
```

### Case 3: Analysis & Audit

```bash
python main.py --user users.csv --role roles.csv --gsi-id Analysis_001 \
  --export-mode by-format --format pdf
# Generates: All PDF templates
```

## 🔍 Understanding Your Data

### Auto-Detect GSI Column

The system looks for these column names automatically:

- `gsi`, `gsi_id` (exact match)
- `app`, `app_id`, `application`, `application_id`
- `system`, `system_id`
- `enterprise`, `enterprise_id`

**Example CSV structure:**

```
user_id,user_name,gsi_id,role
U001,John Doe,SAP_001,Admin
U002,Jane Smith,SAP_001,User
U003,Bob Johnson,Salesforce_001,User
```

### Manual GSI Column Specification

If auto-detect doesn't work:

```bash
python main.py --user users.csv --role roles.csv \
  --gsi-id SAP_001 \
  --gsi-column my_application_id
```

Or in UI: Template Configuration → Advanced Options

## 📊 Output Files

All exports include:

- **Filename**: `IAM_Export_[GSI_ID]_[TIMESTAMP].[format]`
- **Location**: `output/` directory
- **Metadata**: GSI ID, export date/time, data summary

**Example outputs:**

```
output/
  ├─ IAM_Export_SAP_001_20240322_143022.xlsx      (T3 Standard)
  ├─ IAM_Export_SAP_001_20240322_143022.docx      (OLA Standard)
  ├─ IAM_Export_SAP_001_20240322_143022.pdf       (Executive Summary)
  └─ Audit_Trail_SAP_001_20240322_143022.pdf      (Audit Trail)
```

## 🛠️ Troubleshooting

### Issue: GSI column not found

**Solution**: Manually specify with `--gsi-column NAME`

### Issue: No templates appear in UI

**Solution**:

```bash
python main.py --list-templates  # Check available templates
```

### Issue: PDF export fails

**Solution**:

```bash
pip install --upgrade reportlab
```

## 📚 Features

### GSI Manager

- Auto-detect GSI columns
- Filter data by GSI
- Get GSI statistics
- Multi-GSI support

### Template Manager

- 5+ pre-built templates
- Register custom templates
- Filter by format
- Validate templates

### PDF Generator

- Executive summaries
- Detailed analysis reports
- Audit trail generation
- Professional formatting

### Export Manager

- Single/multiple template exports
- Format-specific exports
- GSI-aware exports
- Export summary generation

## 🎓 Next Steps

1. **Run a test export**

   ```bash
   python main.py --user sample_users.csv --role sample_roles.csv \
     --gsi-id TEST_001 --export-mode single --templates T3_Standard
   ```

2. **Try the Streamlit UI**

   ```bash
   streamlit run app.py
   ```

3. **Generate audit trail**

   ```bash
   python main.py --user users.csv --role roles.csv --gsi-id APP_001 \
     --include-audit-trail
   ```

4. **List all templates**
   ```bash
   python main.py --list-templates
   ```

## 📞 Support

For detailed information:

- See `GSI_TEMPLATE_ENHANCEMENT.md` for complete documentation
- Check `requirements.txt` for all dependencies
- Review generated files in `output/` directory for validation

---

**Happy exporting!** ✨
