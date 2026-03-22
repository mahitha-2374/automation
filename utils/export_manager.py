"""
Export Manager - Coordinate exports with GSI and template support
Manages end-to-end export process combining GSI data with selected templates
"""

import os
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Any

from utils.gsi_manager import GSIManager
from utils.template_manager import TemplateManager
from utils.universal_template_filler import UniversalTemplateFiller
from generators.excel_generator import ExcelGenerator
from generators.word_generator import WordGenerator
from generators.pdf_generator import PDFGenerator
from generators.report_generator import ExplainReport


class ExportManager:
    """Manage complete export workflow with GSI and template support"""

    def __init__(self, output_dir: str = "output", templates_dir: str = "templates"):
        """
        Initialize Export Manager
        
        Args:
            output_dir: Output directory for generated files
            templates_dir: Directory containing templates
        """
        self.output_dir = output_dir
        self.templates_dir = templates_dir
        
        # Initialize components
        self.gsi_manager = GSIManager()
        self.template_manager = TemplateManager(templates_dir)
        self.universal_filler = UniversalTemplateFiller(templates_dir)
        self.excel_generator = ExcelGenerator()
        self.word_generator = WordGenerator()
        self.pdf_generator = PDFGenerator()
        self.report_generator = ExplainReport()
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

    def prepare_gsi_export(self, user_df: pd.DataFrame, role_df: pd.DataFrame,
                          gsi_id: str, gsi_column: Optional[str] = None) -> Dict[str, Any]:
        """
        Prepare data for GSI-specific export
        
        Args:
            user_df: User export dataframe
            role_df: Role export dataframe
            gsi_id: The GSI ID to export
            gsi_column: Optional column name containing GSI IDs
            
        Returns:
            Dictionary with prepared GSI export data
        """
        # Detect and set GSI column if not provided
        if gsi_column:
            self.gsi_manager.set_gsi_column(gsi_column)
        else:
            detected = self.gsi_manager.detect_gsi_column(user_df, role_df)
            if detected:
                self.gsi_manager.set_gsi_column(detected[0])
        
        # Extract GSI data
        self.gsi_manager.extract_gsi_data(user_df, role_df)
        
        # Get GSI-specific data
        gsi_data = self.gsi_manager.get_gsi_by_id(gsi_id)
        
        if not gsi_data:
            # If GSI not found, use all data
            gsi_data = {
                "gsi_id": gsi_id,
                "users": user_df.to_dict('records'),
                "roles": role_df.to_dict('records'),
                "entitlements": [],
                "user_count": len(user_df),
                "role_count": len(role_df),
                "entitlement_count": 0
            }
        
        # Add metadata
        gsi_data["export_date"] = datetime.now().strftime("%Y-%m-%d")
        gsi_data["export_time"] = datetime.now().strftime("%H:%M:%S")
        
        return gsi_data

    def export_with_template(self, gsi_id: str, template_id: str, processed_data: Dict,
                            file_prefix: str = "IAM_Export") -> Dict[str, str]:
        """
        Export data using specified template and GSI
        
        Args:
            gsi_id: GSI ID for the export
            template_id: Template to use for export
            processed_data: Processed IAM data
            file_prefix: Prefix for output files
            
        Returns:
            Dictionary with export results and file paths
        """
        results = {
            "gsi_id": gsi_id,
            "template_id": template_id,
            "generated_files": [],
            "errors": [],
            "success": True
        }
        
        # Validate template
        is_valid, error_msg = self.template_manager.validate_template(template_id)
        if not is_valid:
            results["errors"].append(error_msg)
            results["success"] = False
            return results
        
        # Get template info
        template_info = self.template_manager.get_template_info(template_id)
        template_format = template_info.get("format")
        
        # Prepare output filename with GSI and timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"{file_prefix}_{gsi_id}_{timestamp}"
        
        try:
            # Generate based on template format
            if template_format == "xlsx":
                output_file = os.path.join(self.output_dir, f"{base_name}.xlsx")
                self.excel_generator.generate(
                    self.template_manager.get_template_path(template_id) or 
                    os.path.join(self.templates_dir, "T3_template.xlsm"),
                    output_file,
                    processed_data
                )
                results["generated_files"].append({
                    "file": output_file,
                    "format": "Excel",
                    "type": template_info.get("name")
                })
            
            elif template_format == "docx":
                output_file = os.path.join(self.output_dir, f"{base_name}.docx")
                self.word_generator.generate(
                    self.template_manager.get_template_path(template_id) or 
                    os.path.join(self.templates_dir, "OLA_template.docx"),
                    output_file,
                    processed_data
                )
                results["generated_files"].append({
                    "file": output_file,
                    "format": "Word",
                    "type": template_info.get("name")
                })
            
            elif template_format == "pdf":
                output_file = os.path.join(self.output_dir, f"{base_name}.pdf")
                
                if "Executive" in template_info.get("name", ""):
                    self.pdf_generator.generate_executive_summary(
                        output_file, gsi_id, processed_data
                    )
                elif "Detailed" in template_info.get("name", ""):
                    self.pdf_generator.generate_detailed_report(
                        output_file, gsi_id, processed_data
                    )
                else:
                    self.pdf_generator.generate_audit_trail(
                        output_file, gsi_id, processed_data,
                        processed_data.get("explanations", [])
                    )
                
                results["generated_files"].append({
                    "file": output_file,
                    "format": "PDF",
                    "type": template_info.get("name")
                })
        
        except Exception as e:
            results["errors"].append(f"Error generating {template_format} file: {str(e)}")
            results["success"] = False
        
        return results

    def export_multiple_templates(self, gsi_id: str, template_ids: List[str],
                                 processed_data: Dict,
                                 file_prefix: str = "IAM_Export") -> Dict[str, Any]:
        """
        Export using multiple templates in one operation
        
        Args:
            gsi_id: GSI ID for the export
            template_ids: List of template IDs to use
            processed_data: Processed IAM data
            file_prefix: Prefix for output files
            
        Returns:
            Dictionary with results from all exports
        """
        all_results = {
            "gsi_id": gsi_id,
            "export_date": datetime.now().strftime("%Y-%m-%d"),
            "export_time": datetime.now().strftime("%H:%M:%S"),
            "requested_templates": template_ids,
            "exports": [],
            "total_files": 0,
            "all_success": True
        }
        
        for template_id in template_ids:
            result = self.export_with_template(
                gsi_id, template_id, processed_data, file_prefix
            )
            all_results["exports"].append(result)
            all_results["total_files"] += len(result.get("generated_files", []))
            
            if not result.get("success"):
                all_results["all_success"] = False
        
        return all_results

    def export_by_format(self, gsi_id: str, format_type: str, processed_data: Dict,
                        file_prefix: str = "IAM_Export") -> Dict[str, Any]:
        """
        Export all templates of a specific format
        
        Args:
            gsi_id: GSI ID for the export
            format_type: Format type (xlsx, docx, pdf)
            processed_data: Processed IAM data
            file_prefix: Prefix for output files
            
        Returns:
            Dictionary with results from all exports
        """
        templates = self.template_manager.get_templates_by_format(format_type)
        return self.export_multiple_templates(
            gsi_id, templates, processed_data, file_prefix
        )

    def export_all_gsi_aware(self, gsi_id: str, processed_data: Dict,
                            file_prefix: str = "IAM_Export") -> Dict[str, Any]:
        """
        Export using all GSI-aware templates
        
        Args:
            gsi_id: GSI ID for the export
            processed_data: Processed IAM data
            file_prefix: Prefix for output files
            
        Returns:
            Dictionary with results from all exports
        """
        templates = self.template_manager.get_gsi_aware_templates()
        template_ids = list(templates.keys())
        return self.export_multiple_templates(
            gsi_id, template_ids, processed_data, file_prefix
        )

    def get_export_summary(self, export_results: Dict) -> str:
        """
        Generate human-readable export summary
        
        Args:
            export_results: Results dictionary from export operation
            
        Returns:
            Formatted summary string
        """
        summary = []
        summary.append(f"\n{'='*60}")
        summary.append(f"EXPORT SUMMARY - GSI: {export_results.get('gsi_id')}")
        summary.append(f"{'='*60}")
        
        if "exports" in export_results:
            for i, export in enumerate(export_results["exports"], 1):
                template = export.get("template_id", "Unknown")
                status = "✓ SUCCESS" if export.get("success") else "✗ FAILED"
                summary.append(f"\n[{i}] Template: {template} - {status}")
                
                for file_info in export.get("generated_files", []):
                    summary.append(f"    📄 {file_info.get('type')}: {file_info.get('file')}")
                
                if export.get("errors"):
                    for error in export["errors"]:
                        summary.append(f"    ⚠️  {error}")
        
        else:
            template = export_results.get("template_id", "Unknown")
            status = "✓ SUCCESS" if export_results.get("success") else "✗ FAILED"
            summary.append(f"\nTemplate: {template} - {status}")
            
            for file_info in export_results.get("generated_files", []):
                summary.append(f"📄 {file_info.get('type')}: {file_info.get('file')}")
            
            if export_results.get("errors"):
                for error in export_results["errors"]:
                    summary.append(f"⚠️  {error}")
        
        summary.append(f"\nTotal Files Generated: {export_results.get('total_files', len(export_results.get('generated_files', [])))}")
        summary.append(f"{'='*60}\n")
        
        return "\n".join(summary)

    def list_available_exports(self) -> Dict[str, List[str]]:
        """
        List all available export options
        
        Returns:
            Dictionary with available templates by format
        """
        return {
            "xlsx_templates": self.template_manager.get_templates_by_format("xlsx"),
            "docx_templates": self.template_manager.get_templates_by_format("docx"),
            "pdf_templates": self.template_manager.get_templates_by_format("pdf"),
            "gsi_aware": list(self.template_manager.get_gsi_aware_templates().keys())
        }

    def export_with_custom_templates(self, users_df: pd.DataFrame, roles_df: pd.DataFrame,
                                    gsi_id: Optional[str] = None, 
                                    template_names: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Export using custom/user-provided templates
        Auto-detects and fills any template format (Excel, Word, PDF)
        
        Args:
            users_df: User export dataframe
            roles_df: Role export dataframe
            gsi_id: Optional GSI ID to filter by
            template_names: List of template names to use (auto-detect if None)
            
        Returns:
            Export results with file information
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results = {
            'gsi_id': gsi_id or 'ALL',
            'timestamp': timestamp,
            'exports': [],
            'total_files': 0,
            'success_count': 0,
            'failed_count': 0
        }
        
        # Get available templates
        available = self.universal_filler.get_available_templates()
        
        if not available:
            return {
                **results,
                'error': 'No templates found in templates directory'
            }
        
        # Determine which templates to use
        if template_names:
            templates_to_use = {k: v for k, v in available.items() 
                              if k in template_names}
        else:
            templates_to_use = available
        
        # Fill each template
        for template_name, template_info in templates_to_use.items():
            try:
                # Generate output filename
                output_name = f"{template_name}_{gsi_id}_{timestamp}{template_info['format']}"
                output_path = os.path.join(self.output_dir, output_name)
                
                # Fill template
                success, message = self.universal_filler.fill_template(
                    template_name,
                    output_path,
                    users_df,
                    roles_df,
                    gsi_id
                )
                
                export_record = {
                    'template_name': template_name,
                    'format': template_info['format'],
                    'output_file': output_name,
                    'success': success,
                    'message': message
                }
                
                if success:
                    results['success_count'] += 1
                    results['total_files'] += 1
                else:
                    results['failed_count'] += 1
                
                results['exports'].append(export_record)
                
            except Exception as e:
                import traceback
                results['exports'].append({
                    'template_name': template_name,
                    'success': False,
                    'error': str(e),
                    'traceback': traceback.format_exc()
                })
                results['failed_count'] += 1
        
        return results
    
    def get_template_info(self) -> Dict[str, Any]:
        """
        Get information about available templates
        
        Returns:
            Information about all detectable templates
        """
        available = self.universal_filler.get_available_templates()
        
        info = {
            'total_templates': len(available),
            'templates': {},
            'supported_formats': list(self.universal_filler.SUPPORTED_FORMATS.keys())
        }
        
        for template_name, template_data in available.items():
            info['templates'][template_name] = {
                'file': template_data['file'],
                'format': template_data['format'],
                'type': template_data['type']
            }
        
        return info
