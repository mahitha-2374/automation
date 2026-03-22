"""
CLI Entry Point
Run automation from command line
"""

import argparse
import pandas as pd
import os
from datetime import datetime

from core.adaptive_engine import AdaptiveEngine
from generators.excel_generator import ExcelGenerator
from generators.word_generator import WordGenerator
from generators.pdf_generator import PDFGenerator
from generators.report_generator import ExplainReport
from utils.gsi_manager import GSIManager
from utils.template_manager import TemplateManager
from utils.export_manager import ExportManager


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="IAM Automation Platform - Process user and role exports with GSI and template support"
    )

    parser.add_argument(
        "--user",
        required=False,
        help="Path to user export CSV file"
    )

    parser.add_argument(
        "--role",
        required=False,
        help="Path to role export CSV file"
    )

    parser.add_argument(
        "--gsi-id",
        default=None,
        help="GSI ID of the application (optional)"
    )

    parser.add_argument(
        "--gsi-column",
        default=None,
        help="Column name for GSI ID in CSV files (auto-detected if not provided)"
    )

    parser.add_argument(
        "--output-dir",
        default="output",
        help="Output directory (default: output)"
    )

    parser.add_argument(
        "--excel-template",
        default="templates/T3_template.xlsm",
        help="Path to Excel template"
    )

    parser.add_argument(
        "--word-template",
        default="templates/OLA_template.docx",
        help="Path to Word template"
    )

    parser.add_argument(
        "--export-mode",
        choices=["single", "multiple", "all-gsi-aware", "by-format"],
        default="single",
        help="Export mode: single (default), multiple, all-gsi-aware, or by-format"
    )

    parser.add_argument(
        "--templates",
        nargs="+",
        help="Specific templates to use (for multiple/all-gsi-aware modes)"
    )

    parser.add_argument(
        "--format",
        choices=["xlsx", "docx", "pdf"],
        help="Format for by-format mode"
    )

    parser.add_argument(
        "--no-excel",
        action="store_true",
        help="Skip Excel generation (legacy)"
    )

    parser.add_argument(
        "--no-word",
        action="store_true",
        help="Skip Word generation (legacy)"
    )

    parser.add_argument(
        "--no-report",
        action="store_true",
        help="Skip Report generation"
    )

    parser.add_argument(
        "--include-audit-trail",
        action="store_true",
        help="Generate audit trail PDF"
    )

    parser.add_argument(
        "--list-templates",
        action="store_true",
        help="List available templates and exit"
    )

    parser.add_argument(
        "--custom-templates",
        action="store_true",
        help="Use custom templates from templates directory (auto-detect and fill)"
    )

    parser.add_argument(
        "--template-dir",
        default="templates",
        help="Directory containing templates (default: templates)"
    )

    parser.add_argument(
        "--list-custom-templates",
        action="store_true",
        help="List available custom templates and exit"
    )

    args = parser.parse_args()

    # List templates if requested (before other validation)
    if args.list_templates:
        template_mgr = TemplateManager("templates")
        templates = template_mgr.get_available_templates()
        print("\n📋 Available Templates:\n")
        for template_id, config in templates.items():
            print(f"  • {template_id}")
            print(f"    Name: {config['name']}")
            print(f"    Format: {config['format'].upper()}")
            print(f"    Description: {config['description']}")
            print(f"    GSI-Aware: {'Yes' if config.get('gsi_aware') else 'No'}")
            print()
        return

    # List custom templates if requested
    if args.list_custom_templates:
        from utils.universal_template_filler import UniversalTemplateFiller
        filler = UniversalTemplateFiller(args.template_dir)
        templates = filler.get_available_templates()
        
        if not templates:
            print(f"\n❌ No templates found in '{args.template_dir}' directory")
            print("\nSupported formats: .xlsx, .xlsm, .docx, .pdf")
            return
        
        print(f"\n📋 Available Custom Templates in '{args.template_dir}':\n")
        for template_name, template_info in templates.items():
            print(f"  • {template_name}")
            print(f"    File: {template_info['file']}")
            print(f"    Format: {template_info['format']}")
            print()
        return

    # Now validate required arguments for processing
    if not args.user or not args.role:
        parser.error("--user and --role are required (except with --list-templates)")

    # Validate files exist
    if not os.path.exists(args.user):
        print(f"❌ User file not found: {args.user}")
        return

    if not os.path.exists(args.role):
        print(f"❌ Role file not found: {args.role}")
        return

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    print("🔄 Processing files...")

    try:
        # Load data
        user_df = pd.read_csv(args.user)
        role_df = pd.read_csv(args.role)

        # Auto-detect templates from input data
        templates_from_input = []
        if "template" in user_df.columns:
            templates_from_input = user_df["template"].dropna().unique().tolist()
            if templates_from_input:
                print(f"  ✓ Detected templates in input: {', '.join(templates_from_input)}")
                # Use detected templates if not provided via CLI
                if not args.templates:
                    args.templates = templates_from_input

        print(f"  ✓ Loaded {len(user_df)} users")
        print(f"  ✓ Loaded {len(role_df)} roles")

        # Process with AdaptiveEngine
        engine = AdaptiveEngine()
        result = engine.process(user_df, role_df, gsi_id=args.gsi_id)

        gsi_id_str = args.gsi_id or result.get('gsi_id', 'UNKNOWN')
        
        print(f"  ✓ GSI ID: {gsi_id_str}")
        print(f"  ✓ Detected {len(result['users'])} unique users")
        print(f"  ✓ Detected {len(result['roles'])} unique roles")
        print(f"  ✓ Found {len(result['entitlements'])} entitlements")

        # Handle custom templates if requested
        if args.custom_templates:
            print(f"\n📝 Using custom templates from '{args.template_dir}'")
            export_mgr = ExportManager(args.output_dir, args.template_dir)
            custom_result = export_mgr.export_with_custom_templates(
                user_df, role_df, gsi_id_str, args.templates
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
                        if export.get('traceback'):
                            print(f"  {export.get('traceback')}")
                
                print(f"{'='*60}")
                print(f"Success: {custom_result.get('success_count', 0)} | Failed: {custom_result.get('failed_count', 0)}")
                print(f"✅ All done!")
            return

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Initialize ExportManager for new template-based exports
        export_mgr = ExportManager(args.output_dir, "templates")

        # Prepare GSI export data
        gsi_export_data = export_mgr.prepare_gsi_export(user_df, role_df, gsi_id_str, args.gsi_column)
        gsi_export_data.update(result)
        gsi_export_data["gsi_id"] = gsi_id_str

        # Execute new export modes
        # Auto-switch to multiple mode if multiple templates detected from input
        export_mode = args.export_mode
        if export_mode == "single" and args.templates and len(args.templates) > 1:
            export_mode = "multiple"
            print(f"\n📝 Auto-switched to multiple mode (templates from input)")

        if export_mode == "single":
            template_id = args.templates[0] if args.templates else "T3_Standard"
            print(f"\n📤 Exporting with single template: {template_id}")
            export_result = export_mgr.export_with_template(
                gsi_id_str,
                template_id,
                gsi_export_data,
                f"IAM_Export_{gsi_id_str}"
            )
            print(export_mgr.get_export_summary(export_result))

        elif export_mode == "multiple" and args.templates:
            print(f"\n📤 Exporting with multiple templates: {', '.join(args.templates)}")
            export_result = export_mgr.export_multiple_templates(
                gsi_id_str,
                args.templates,
                gsi_export_data,
                f"IAM_Export_{gsi_id_str}"
            )
            print(export_mgr.get_export_summary(export_result))

        elif export_mode == "all-gsi-aware":
            print(f"\n📤 Exporting with all GSI-aware templates")
            export_result = export_mgr.export_all_gsi_aware(
                gsi_id_str,
                gsi_export_data,
                f"IAM_Export_{gsi_id_str}"
            )
            print(export_mgr.get_export_summary(export_result))

        elif export_mode == "by-format":
            if not args.format:
                print("❌ --format required for by-format mode")
                return
            print(f"\n📤 Exporting all {args.format.upper()} templates")
            export_result = export_mgr.export_by_format(
                gsi_id_str,
                args.format,
                gsi_export_data,
                f"IAM_Export_{gsi_id_str}"
            )
            print(export_mgr.get_export_summary(export_result))

        # Generate audit trail if requested
        if args.include_audit_trail:
            audit_path = os.path.join(args.output_dir, f"Audit_Trail_{gsi_id_str}_{timestamp}.pdf")
            print(f"\n📋 Generating audit trail: {audit_path}")
            export_mgr.pdf_generator.generate_audit_trail(
                audit_path,
                gsi_id_str,
                gsi_export_data,
                result.get("explanations", [])
            )
            print("  ✓ Audit trail generated")

        # Legacy exports (if not skipped)
        if not args.no_excel:
            excel_path = os.path.join(args.output_dir, f"T3_output_{gsi_id_str}_{timestamp}.xlsm")
            print(f"\n📊 Generating legacy Excel: {excel_path}")
            ExcelGenerator().generate(args.excel_template, excel_path, result)
            print("  ✓ Excel generated")

        if not args.no_word:
            word_path = os.path.join(args.output_dir, f"OLA_output_{gsi_id_str}_{timestamp}.docx")
            print(f"\n📄 Generating legacy Word: {word_path}")
            WordGenerator().generate(args.word_template, word_path, result)
            print("  ✓ Word generated")

        if not args.no_report:
            report_path = os.path.join(args.output_dir, f"report_{gsi_id_str}_{timestamp}.xlsx")
            print(f"\n📋 Generating legacy Report: {report_path}")
            ExplainReport().generate(result["explanations"], report_path)
            print("  ✓ Report generated")

        print("\n✅ All done!")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
