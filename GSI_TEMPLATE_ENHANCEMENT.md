# Enhancement: GSI-Aware Template-Based Export System

## Overview

This enhancement adds powerful GSI (Global System Identifier) and template-based export capabilities to the IAM Automation Platform. It enables users to:

1. **Retrieve GSI information** from CSV columns and filter data by GSI
2. **Select templates dynamically** for different output formats
3. **Generate multiple output formats** (Excel, Word, PDF) from a single processing run
4. **Create GSI-specific exports** with all related data and metadata
5. **Personalize outputs** based on application GSI and template selection

## Key Components

### 1. GSI Manager (`utils/gsi_manager.py`)

Handles extraction and filtering of data by GSI ID from your CSV exports.

**Features:**

- Auto-detect GSI columns from CSV files
- Extract GSI-specific data from user and role exports
- Filter dataframes by GSI ID
- Retrieve GSI summary statistics
- Support for multiple GSI IDs in single export

**Usage Example:**

```python
from utils.gsi_manager import GSIManager

gsi_mgr = GSIManager()

# Detect GSI columns
detected = gsi_mgr.detect_gsi_column(user_df, role_df)
print(f"Detected GSI columns: {detected}")

# Set the GSI column
gsi_mgr.set_gsi_column("application")

# Extract GSI data
gsi_data = gsi_mgr.extract_gsi_data(user_df, role_df)

# Get data for specific GSI
gsi_info = gsi_mgr.get_gsi_by_id("SAP_System_1")
print(f"Total users: {gsi_info['user_count']}")
print(f"Total roles: {gsi_info['role_count']}")
```

### 2. Template Manager (`utils/template_manager.py`)

Manages template registry and selection for output generation.

**Pre-configured Templates:**

- **T3_Standard**: Excel with User-Role-Resource mapping
- **OLA_Standard**: Word document template
- **Executive_Summary**: High-level PDF report
- **Detailed_Report**: Comprehensive PDF analysis
- **IAM_Audit**: Complete audit trail Excel

**Features:**

- Register custom templates
- Filter templates by format (xlsx, docx, pdf)
- Get GSI-aware templates
- Validate template availability
- Import/export template configuration

**Usage Example:**

```python
from utils.template_manager import TemplateManager

template_mgr = TemplateManager("templates")

# Get all available templates
all_templates = template_mgr.get_available_templates()

# Get templates by format
excel_templates = template_mgr.get_templates_by_format("xlsx")
pdf_templates = template_mgr.get_templates_by_format("pdf")

# Get GSI-aware templates only
gsi_templates = template_mgr.get_gsi_aware_templates()

# Register custom template
custom_config = {
    "name": "Custom Report",
    "description": "My custom report template",
    "format": "xlsx",
    "file": "my_template.xlsx",
    "gsi_aware": True,
    "supports_custom_data": True
}
template_mgr.register_template("Custom_Report", custom_config)
```

### 3. PDF Generator (`generators/pdf_generator.py`)

Generates professional PDF reports from IAM data.

**Report Types:**

- Executive Summary: Overview and key metrics
- Detailed Report: Complete analysis with users and roles
- Audit Trail: Detailed audit with schema explanations

**Features:**

- Professional formatting with custom styles
- GSI-aware headers and footers
- Automatic pagination
- Statistical summaries
- Confidence metrics on mappings

### 4. Export Manager (`utils/export_manager.py`)

Orchestrates end-to-end export process combining all components.

**Features:**

- Single template export
- Multiple template export
- Export all GSI-aware templates
- Export by format type
- Automatic GSI data preparation
- Generate export summaries
- Support for audit trails

**Export Modes:**

- **Single Template**: Use one specific template
- **Multiple Templates**: Use list of templates
- **All GSI-Aware**: Use all GSI-aware templates
- **By Format**: Use all templates in selected format

## Usage Guide

### Web UI (Streamlit)

#### 1. Basic Workflow

1. Upload user and role CSV exports
2. Enter GSI ID (auto-filled if in CSV)
3. Choose export mode and templates:
   - Single Template: Select one template
   - Multiple Templates: Select multiple templates
   - All GSI-Aware Templates: Auto-select all GSI templates
   - By Format: Select all templates in format (Excel/Word/PDF)
4. Configure advanced options:
   - Include GSI Metadata
   - Include Explanations
   - Generate Audit Trail
5. Click **"Generate Outputs with Template"**
6. Download generated files

#### 2. Advanced Options

**Include GSI Metadata:**

- Adds GSI ID, export date/time to all outputs
- Includes GSI summary statistics
- Recommended: Enable

**Include Explanations:**

- Includes schema detection explanations
- Shows confidence scores for column mappings
- Recommended: Enable for audit compliance

**Generate Audit Trail:**

- Creates separate PDF audit report
- Detailed mapping explanations
- Recommended: Enable for compliance audits

**Legacy Mode:**

- T3_Standard Excel
- OLA_Standard Word
- Explainability Report with mappings

### Command Line Interface (CLI)

#### Basic Usage

```bash
# Simple export with default settings
python main.py --user users.csv --role roles.csv --gsi-id SAP_001

# List available templates
python main.py --list-templates

# Single template export
python main.py --user users.csv --role roles.csv \
  --gsi-id SAP_001 \
  --export-mode single \
  --templates T3_Standard

# Multiple template export
python main.py --user users.csv --role roles.csv \
  --gsi-id SAP_001 \
  --export-mode multiple \
  --templates T3_Standard OLA_Standard Executive_Summary

# Export all GSI-aware templates
python main.py --user users.csv --role roles.csv \
  --gsi-id SAP_001 \
  --export-mode all-gsi-aware

# Export by format (all PDF templates)
python main.py --user users.csv --role roles.csv \
  --gsi-id SAP_001 \
  --export-mode by-format \
  --format pdf

# Include audit trail
python main.py --user users.csv --role roles.csv \
  --gsi-id SAP_001 \
  --include-audit-trail

# Auto-detect GSI column
python main.py --user users.csv --role roles.csv \
  --gsi-column application_id
```

#### CLI Arguments

```
Required:
  --user FILE                 User export CSV file
  --role FILE                 Role export CSV file

Optional:
  --gsi-id ID                GSI ID (auto-detect if in CSV)
  --gsi-column COLUMN        Column name for GSI (auto-detect if omitted)
  --output-dir DIR           Output directory (default: output)
  --excel-template PATH      Custom Excel template
  --word-template PATH       Custom Word template

Export Modes:
  --export-mode MODE         single|multiple|all-gsi-aware|by-format
  --templates IDS            Template IDs to use (for multiple mode)
  --format FORMAT            Format for by-format mode (xlsx|docx|pdf)

Options:
  --include-audit-trail      Generate audit trail PDF
  --no-excel                 Skip legacy Excel export
  --no-word                  Skip legacy Word export
  --no-report                Skip legacy Report
  --list-templates           List available templates and exit
```

## Data Flow

```
CSV Exports (Users, Roles)
    ↓
GSI Manager (Extract & Filter)
    ↓
Adaptive Engine (Process)
    ↓
Export Manager
    ├→ Template Selection
    ├→ GSI Data Preparation
    └→ Format Selection
        ├→ Excel Generator
        ├→ Word Generator
        └→ PDF Generator
            ↓
        Output Files (Templated)
                ↓
            Download/Use
```

## Integration with Existing Code

### Adding to App.py

The enhanced app.py includes:

- New template selection UI
- GSI-aware export options
- Advanced configuration options
- Multi-format export support
- Legacy export mode (backward compatible)

### Adding to Main.py

The enhanced main.py includes:

- New CLI arguments
- Template list command
- Multiple export modes
- Audit trail generation
- GSI column auto-detection

## New Dependencies

Added to requirements.txt:

```
reportlab>=4.0.0
```

## Configuration

### Available Templates

Templates are configured in `TemplateManager._initialize_default_templates()`:

```python
{
    "Template_ID": {
        "name": "Display Name",
        "description": "What this template does",
        "format": "xlsx|docx|pdf",
        "file": "template_filename",
        "gsi_aware": True,
        "supports_custom_data": True
    }
}
```

### Register Custom Template

```python
template_mgr = TemplateManager("templates")

custom_template = {
    "name": "Custom Analysis",
    "description": "Company-specific analysis template",
    "format": "xlsx",
    "file": "custom.xlsx",
    "gsi_aware": True,
    "supports_custom_data": True
}

template_mgr.register_template("Custom_Analysis", custom_template)
```

## Best Practices

1. **GSI Column Naming**: Use consistent column names:
   - `gsi`, `gsi_id`, `application`, `app_id`, `system`, `system_id`
   - GSIManager auto-detects these

2. **Template Selection**:
   - Use "All GSI-Aware Templates" for comprehensive coverage
   - Use "By Format" when you need all options in format
   - Use "Single Template" for focused exports

3. **Output Management**:
   - Enable "Include GSI Metadata" for tracking
   - Enable "Include Explanations" for audit compliance
   - Use "Generate Audit Trail" for high-security applications

4. **CSV Structure**:
   - Include GSI column in exports for auto-filtering
   - Use consistent user IDs and role names
   - Include application/system identifiers

## Troubleshooting

### GSI Column Not Detected

**Problem**: GSI column not auto-detected

**Solution**:

1. Verify column name matches patterns: gsi, app, system, application, enterprise
2. Manually specify column with `--gsi-column` or UI option
3. Check for extra spaces or special characters in column name

### Template Not Found

**Problem**: Selected template not generating output

**Solution**:

```bash
# List available templates
python main.py --list-templates

# Check template file exists
ls templates/
```

### PDF Generation Issue

**Problem**: PDF export fails

**Solution**:

1. Ensure reportlab is installed: `pip install reportlab>=4.0.0`
2. Check output directory has write permissions
3. Restart Streamlit app: `streamlit run app.py`

## Examples

### Example 1: Export SAP System

```bash
python main.py \
  --user sap_users.csv \
  --role sap_roles.csv \
  --gsi-id SAP_Production \
  --export-mode all-gsi-aware \
  --include-audit-trail
```

### Example 2: Executive Summary Only

```bash
python main.py \
  --user app_users.csv \
  --role app_roles.csv \
  --gsi-id MyApp_Prod \
  --export-mode single \
  --templates Executive_Summary
```

### Example 3: Compliance Audit Export

```bash
python main.py \
  --user users.csv \
  --role roles.csv \
  --gsi-id Compliance_Check \
  --export-mode by-format \
  --format pdf \
  --include-audit-trail
```

## Performance Considerations

- **Large Datasets**: Use format-specific exports to reduce file size
- **Multiple GSI**: Process separately or use GSI column filtering
- **PDF Generation**: Can be slow with large datasets; consider Excel/Word first
- **Template Performance**: Custom templates may impact generation speed

## Support & Next Steps

For issues or feature requests:

1. Check troubleshooting section
2. Verify dependencies are installed
3. Review generated files in output/ directory
4. Check logs for error details

## Future Enhancements

Potential features in upcoming versions:

- Dynamic template customization UI
- Database backend for GSI storage
- Batch processing multiple GSI IDs
- Custom field mapping in templates
- Template preview before export
- Email integration for automatic delivery
