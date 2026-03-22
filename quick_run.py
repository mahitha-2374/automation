"""
Quick test runner - Skip heavy imports for fast execution
"""
import sys
import os
import pandas as pd
from datetime import datetime

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

# Import only what we need
from utils.export_manager import ExportManager


def load_input_dataframe(file_path):
    """Load CSV or Excel file based on extension."""
    lower_path = file_path.lower()
    if lower_path.endswith(".csv"):
        return pd.read_csv(file_path)
    if lower_path.endswith((".xlsx", ".xls")):
        return pd.read_excel(file_path, engine="openpyxl")
    raise ValueError(f"Unsupported file type: {file_path}. Use CSV, XLSX, or XLS.")

def main():
    # Configuration
    user_file = "input/users_sample.csv"
    role_file = "input/roles_sample.csv"
    gsi_id = "APP-001"
    
    print("🔄 Processing files...")
    
    # Load data
    user_df = load_input_dataframe(user_file)
    role_df = load_input_dataframe(role_file)
    
    print(f"  ✓ Loaded {len(user_df)} users")
    print(f"  ✓ Loaded {len(role_df)} roles")
    print(f"  ✓ GSI ID: {gsi_id}")
    
    # Export with custom templates
    print(f"\n📝 Using custom templates from 'templates'")
    
    export_mgr = ExportManager("output", "templates")
    custom_result = export_mgr.export_with_custom_templates(
        user_df, role_df, gsi_id, None
    )
    
    if 'error' in custom_result:
        print(f"❌ {custom_result['error']}")
    else:
        print(f"\n📤 Custom Template Export Results:")
        print(f"{'='*60}")
        for export in custom_result.get('exports', []):
            status = "✓ SUCCESS" if export.get('success') else "✗ FAILED"
            print(f"[{export.get('template_name')}] {status}")
            if export.get('success'):
                print(f"  📄 {export.get('output_file')}")
            elif export.get('message'):
                print(f"  ⚠️  {export.get('message')}")
            elif export.get('error'):
                print(f"  ⚠️  {export.get('error')}")
        
        print(f"{'='*60}")
        print(f"Success: {custom_result.get('success_count', 0)} | Failed: {custom_result.get('failed_count', 0)}")
        print(f"✅ All done!")

if __name__ == "__main__":
    main()
