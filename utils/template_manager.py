"""
Template Manager - Handle template selection and customization
Manages available templates and applies them to output generation
"""

import os
import json
from typing import Dict, List, Any, Optional
from pathlib import Path


class TemplateManager:
    """Manage output templates for different formats"""

    def __init__(self, templates_dir: str = "templates"):
        """
        Initialize Template Manager
        
        Args:
            templates_dir: Directory containing template files
        """
        self.templates_dir = templates_dir
        self.templates = {}
        self.template_metadata = {}
        
        # Create templates directory if it doesn't exist
        os.makedirs(templates_dir, exist_ok=True)
        
        # Initialize with default templates
        self._initialize_default_templates()

    def _initialize_default_templates(self):
        """Initialize default template configurations"""
        default_templates = {
            "T3_Standard": {
                "name": "T3 Standard",
                "description": "Standard T3 Excel template with User-Role-Resource mapping",
                "format": "xlsx",
                "file": "T3_template.xlsm",
                "sheets": [
                    "Summary",
                    "User_role_resource",
                    "Role_Resource",
                    "Role_resource_lookup",
                    "User_Account_lookup",
                    "gsi_user-role-resource-cntrl"
                ],
                "gsi_aware": True,
                "supports_custom_data": True
            },
            "OLA_Standard": {
                "name": "OLA Standard",
                "description": "Standard OLA document template for Word output",
                "format": "docx",
                "file": "OLA_template.docx",
                "sections": ["Header", "GSI_Info", "Users", "Roles", "Mappings", "Footer"],
                "gsi_aware": True,
                "supports_custom_data": True
            },
            "Executive_Summary": {
                "name": "Executive Summary",
                "description": "High-level executive summary report",
                "format": "pdf",
                "file": "Executive_Summary_template.pdf",
                "sections": ["Title", "Overview", "Statistics", "Recommendations"],
                "gsi_aware": True,
                "supports_custom_data": False
            },
            "Detailed_Report": {
                "name": "Detailed Report",
                "description": "Comprehensive detailed analysis report",
                "format": "pdf",
                "file": "Detailed_Report_template.pdf",
                "sections": ["Title", "GSI_Details", "User_Analysis", "Role_Analysis", 
                            "Mapping_Details", "Anomalies", "Recommendations"],
                "gsi_aware": True,
                "supports_custom_data": True
            },
            "IAM_Audit": {
                "name": "IAM Audit",
                "description": "Complete IAM audit trail with all user-role-entitlement mappings",
                "format": "xlsx",
                "file": "IAM_Audit_template.xlsx",
                "sheets": ["Audit_Summary", "User_Details", "Role_Details", 
                          "Complete_Mapping", "Errors_Warnings"],
                "gsi_aware": True,
                "supports_custom_data": True
            }
        }
        
        self.template_metadata = default_templates

    def get_available_templates(self, format_filter: Optional[str] = None) -> Dict[str, Dict]:
        """
        Get list of available templates
        
        Args:
            format_filter: Filter by format (xlsx, docx, pdf, etc.)
            
        Returns:
            Dictionary of available templates
        """
        if format_filter:
            return {
                k: v for k, v in self.template_metadata.items()
                if v.get("format") == format_filter
            }
        return self.template_metadata

    def get_template_info(self, template_id: str) -> Optional[Dict]:
        """
        Get metadata for a specific template
        
        Args:
            template_id: Template identifier
            
        Returns:
            Template metadata or None if not found
        """
        return self.template_metadata.get(template_id)

    def register_template(self, template_id: str, template_config: Dict) -> bool:
        """
        Register a new template
        
        Args:
            template_id: Unique identifier for template
            template_config: Template configuration dictionary
            
        Returns:
            True if registered successfully
        """
        required_fields = ["name", "description", "format", "file"]
        
        if not all(field in template_config for field in required_fields):
            return False
        
        self.template_metadata[template_id] = template_config
        return True

    def get_template_path(self, template_id: str) -> Optional[str]:
        """
        Get file path for a template
        
        Args:
            template_id: Template identifier
            
        Returns:
            Full path to template file or None if not found
        """
        template_info = self.get_template_info(template_id)
        if not template_info:
            return None
        
        template_file = template_info.get("file")
        if not template_file:
            return None
        
        full_path = os.path.join(self.templates_dir, template_file)
        return full_path if os.path.exists(full_path) else None

    def get_templates_by_format(self, format_type: str) -> List[str]:
        """
        Get template IDs by format type
        
        Args:
            format_type: Format type (xlsx, docx, pdf)
            
        Returns:
            List of template IDs matching the format
        """
        return [
            template_id for template_id, config in self.template_metadata.items()
            if config.get("format") == format_type
        ]

    def create_custom_template(self, template_id: str, template_config: Dict, 
                               template_file_path: str) -> bool:
        """
        Create a custom template from a file
        
        Args:
            template_id: Unique identifier
            template_config: Template configuration
            template_file_path: Path to template file
            
        Returns:
            True if created successfully
        """
        if not os.path.exists(template_file_path):
            return False
        
        # Copy template file to templates directory
        filename = os.path.basename(template_file_path)
        dest_path = os.path.join(self.templates_dir, filename)
        
        if not os.path.exists(dest_path):
            import shutil
            shutil.copy(template_file_path, dest_path)
        
        # Register template
        template_config["file"] = filename
        return self.register_template(template_id, template_config)

    def get_gsi_aware_templates(self) -> Dict[str, Dict]:
        """
        Get templates that are GSI-aware
        
        Returns:
            Dictionary of GSI-aware templates
        """
        return {
            k: v for k, v in self.template_metadata.items()
            if v.get("gsi_aware", False)
        }

    def validate_template(self, template_id: str) -> tuple:
        """
        Validate that a template exists and is accessible
        
        Args:
            template_id: Template identifier
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        template_info = self.get_template_info(template_id)
        
        if not template_info:
            return False, f"Template '{template_id}' not found in registry"
        
        template_path = self.get_template_path(template_id)
        if not template_path:
            return False, f"Template file not found: {template_info.get('file')}"
        
        return True, ""

    def get_template_sheet_mapping(self, template_id: str) -> Optional[Dict]:
        """
        Get sheet/section mapping for a template
        
        Args:
            template_id: Template identifier
            
        Returns:
            Dictionary with sheet/section mappings or None
        """
        template_info = self.get_template_info(template_id)
        if not template_info:
            return None
        
        mapping = {}
        
        if "sheets" in template_info:
            mapping["sheets"] = template_info["sheets"]
        
        if "sections" in template_info:
            mapping["sections"] = template_info["sections"]
        
        return mapping if mapping else None

    def list_templates_by_capability(self, capability: str) -> List[str]:
        """
        Get templates that support a specific capability
        
        Args:
            capability: Capability name (e.g., 'custom_data', 'gsi_aware')
            
        Returns:
            List of template IDs supporting the capability
        """
        capability_key = f"supports_{capability}" if not capability.startswith("supports_") else capability
        
        return [
            template_id for template_id, config in self.template_metadata.items()
            if config.get(capability_key, False)
        ]

    def export_template_config(self, output_file: str) -> bool:
        """
        Export template metadata to JSON file
        
        Args:
            output_file: Path to output JSON file
            
        Returns:
            True if exported successfully
        """
        try:
            with open(output_file, 'w') as f:
                json.dump(self.template_metadata, f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting template config: {e}")
            return False

    def import_template_config(self, config_file: str) -> bool:
        """
        Import template metadata from JSON file
        
        Args:
            config_file: Path to JSON config file
            
        Returns:
            True if imported successfully
        """
        try:
            with open(config_file, 'r') as f:
                imported_templates = json.load(f)
            
            self.template_metadata.update(imported_templates)
            return True
        except Exception as e:
            print(f"Error importing template config: {e}")
            return False
