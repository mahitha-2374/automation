"""
Polished Streamlit UI
Production-ready interface with all features
"""

import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime

from core.adaptive_engine import AdaptiveEngine
from generators.excel_generator import ExcelGenerator
from generators.word_generator import WordGenerator
from generators.pdf_generator import PDFGenerator
from generators.report_generator import ExplainReport
from utils.gsi_manager import GSIManager
from utils.template_manager import TemplateManager
from utils.export_manager import ExportManager


def load_input_dataframe(file_obj):
    """Load CSV or Excel file into a DataFrame based on file extension."""
    file_name = (getattr(file_obj, "name", "") or "").lower()
    if file_name.endswith(".csv"):
        return pd.read_csv(file_obj)
    if file_name.endswith((".xlsx", ".xls")):
        return pd.read_excel(file_obj, engine="openpyxl")
    raise ValueError("Unsupported file type. Please upload CSV, XLSX, or XLS files.")

# ========== PAGE CONFIG ==========
st.set_page_config(
    page_title="IAM Automation Platform",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== CUSTOM STYLING ==========
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .stButton>button {
        width: 100%;
        padding: 10px;
        font-weight: bold;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3cd;
        border: 1px solid #ffc107;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)

# ========== MAIN UI STRUCTURE ==========
st.title("🔐 IAM Automation Platform")
st.markdown("**Adaptive • Semantic • Self-Learning • Explainable**")

# Initialize session state
if "processed_data" not in st.session_state:
    st.session_state.processed_data = None
if "explanations" not in st.session_state:
    st.session_state.explanations = None

# ========== SIDEBAR ==========
with st.sidebar:
    st.header("⚙️ Configuration")

    confidence_threshold = st.slider(
        "Confidence Threshold",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.1,
        help="Show mappings below this confidence as warnings"
    )

    st.divider()
    st.header("🎯 Application Configuration")
    
    gsi_id = st.text_input(
        "GSI ID of Application",
        value="",
        placeholder="e.g., GSI_001, APP_SAP, etc.",
        help="Enter the Global System Identifier (GSI ID) for the application"
    )

    st.divider()
    st.header("📁 File Upload")

    user_file = st.file_uploader(
        "Select User Export (CSV/XLSX/XLS)",
        type=["csv", "xlsx", "xls"],
        help="Upload your user export file in CSV or Excel format"
    )

    role_file = st.file_uploader(
        "Select Role Export (CSV/XLSX/XLS)",
        type=["csv", "xlsx", "xls"],
        help="Upload your role/entitlement export file in CSV or Excel format"
    )

    st.divider()
    st.header("📋 Template & Export Configuration")
    
    # Initialize template manager
    template_mgr = TemplateManager("templates")
    
    # Template selection options
    export_mode = st.radio(
        "Export Mode:",
        options=["Single Template", "Multiple Templates", "All GSI-Aware Templates", "By Format"],
        help="Choose how to generate output files"
    )
    
    selected_templates = []
    selected_format = None
    
    if export_mode == "Single Template":
        st.subheader("Select Single Template")
        available_templates = template_mgr.get_available_templates()
        
        template_options = {v['name']: k for k, v in available_templates.items()}
        selected_name = st.selectbox(
            "Choose Template:",
            options=list(template_options.keys()),
            help="Select a template for export"
        )
        selected_templates = [template_options[selected_name]]
        
        # Show template info
        template_info = available_templates[selected_templates[0]]
        st.info(f"""
        **{template_info['name']}**
        
        Format: {template_info['format'].upper()}
        
        {template_info['description']}
        """)
    
    elif export_mode == "Multiple Templates":
        st.subheader("Select Multiple Templates")
        available_templates = template_mgr.get_available_templates()
        
        selected_templates_names = st.multiselect(
            "Choose Templates:",
            options=[v['name'] for v in available_templates.values()],
            help="Select multiple templates for export"
        )
        
        # Map names back to IDs
        template_options = {v['name']: k for k, v in available_templates.items()}
        selected_templates = [template_options[name] for name in selected_templates_names]
    
    elif export_mode == "All GSI-Aware Templates":
        gsi_aware = template_mgr.get_gsi_aware_templates()
        selected_templates = list(gsi_aware.keys())
        st.info(f"✓ Will use all {len(selected_templates)} GSI-aware templates")
    
    elif export_mode == "By Format":
        format_choice = st.selectbox(
            "Select Format:",
            options=["Excel (XLSX)", "Word (DOCX)", "PDF"],
            help="Generate all templates in selected format"
        )
        
        format_map = {"Excel (XLSX)": "xlsx", "Word (DOCX)": "docx", "PDF": "pdf"}
        selected_format = format_map[format_choice]
        
        templates_in_format = template_mgr.get_templates_by_format(selected_format)
        st.info(f"✓ Will generate {len(templates_in_format)} {format_choice} templates")
    
    st.divider()
    st.header("🎯 Advanced Options")
    
    # Advanced export options
    include_gsi_metadata = st.checkbox(
        "Include GSI Metadata",
        value=True,
        help="Add GSI information and metadata to all outputs"
    )
    
    include_explanations = st.checkbox(
        "Include Explanations",
        value=True,
        help="Include schema detection explanations in outputs"
    )
    
    generate_audit_trail = st.checkbox(
        "Generate Audit Trail",
        value=False,
        help="Create detailed audit trail report"
    )
    
    st.divider()
    
    template_option = st.radio(
        "Legacy Output Files:",
        options=["Excel & Word", "Excel Only", "Word Only", "Custom Templates"],
        help="(Legacy) Select which output files to generate"
    )
    
    excel_template_path = "templates/T3_template.xlsm"
    word_template_path = "templates/OLA_template.docx"
    
    if template_option == "Custom Templates":
        st.subheader("Upload Custom Templates")
        excel_custom = st.file_uploader(
            "Excel Template (XLSM)",
            type=["xlsm"],
            key="excel_template_upload"
        )
        word_custom = st.file_uploader(
            "Word Template (DOCX)",
            type=["docx"],
            key="word_template_upload"
        )
        
        if excel_custom:
            excel_template_path = excel_custom
        if word_custom:
            word_template_path = word_custom

    st.divider()

    process_btn = st.button(
        "🚀 Run Automation",
        use_container_width=True,
        type="primary",
        key="process_btn"
    )

# ========== MAIN CONTENT ==========

# File Preview Section
if user_file or role_file:
    col1, col2 = st.columns(2 if user_file and role_file else 1)

    with col1:
        if user_file:
            st.subheader("👥 User File Preview")
            try:
                user_df = load_input_dataframe(user_file)
                st.info(f"📊 {len(user_df)} rows, {len(user_df.columns)} columns")
                st.dataframe(user_df.head(), use_container_width=True)
            except Exception as e:
                st.error(f"Error reading user file: {str(e)}")
                user_df = None

    with col2:
        if role_file:
            st.subheader("🔑 Role File Preview")
            try:
                role_df = load_input_dataframe(role_file)
                st.info(f"📊 {len(role_df)} rows, {len(role_df.columns)} columns")
                st.dataframe(role_df.head(), use_container_width=True)
            except Exception as e:
                st.error(f"Error reading role file: {str(e)}")
                role_df = None

# ========== PROCESSING ==========
if process_btn and user_file and role_file:
    if not gsi_id:
        st.error("❌ Please enter the GSI ID of the application to proceed")
    else:
        try:
            with st.spinner("🔄 Processing files..."):
                engine = AdaptiveEngine()
                result = engine.process(user_df, role_df, gsi_id=gsi_id)

                st.session_state.processed_data = result
                st.session_state.explanations = result.get("explanations", [])

            st.success("✅ Processing Completed Successfully!")
            st.info(f"🎯 GSI ID: **{gsi_id}** - All data will be included in generated outputs")

            # ========== RESULTS TABS ==========
            tab1, tab2, tab3, tab4, tab5 = st.tabs(
                ["📊 Summary", "👥 Users", "🔑 Roles", "🎯 Entitlements", "🔍 Explainability"]
            )

            with tab1:
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric(
                        "Total Users",
                        len(result["users"]),
                        help="Number of unique users"
                    )

                with col2:
                    st.metric(
                        "Total Roles",
                        len(result["roles"]),
                        help="Number of unique roles"
                    )

                with col3:
                    st.metric(
                        "Total Entitlements",
                        len(result["entitlements"]),
                        help="Total unique entitlements"
                    )

                with col4:
                    user_role_count = sum(len(u["roles"]) for u in result["users"])
                    st.metric(
                        "User-Role Mappings",
                        user_role_count,
                        help="Total user-role assignments"
                    )

            with tab2:
                st.subheader("User Details")
                users_data = []
                for user in result["users"]:
                    users_data.append({
                        "User ID": user["user_id"],
                        "Roles": ", ".join(user["roles"]),
                        "Role Count": len(user["roles"]),
                        "Status": user.get("account_status", "ACTIVE")
                    })

                if users_data:
                    users_df = pd.DataFrame(users_data)
                    st.dataframe(users_df, use_container_width=True)
                else:
                    st.warning("No users found")

            with tab3:
                st.subheader("Role Details")
                roles_data = []
                for role in result["roles"]:
                    roles_data.append({
                        "Role Name": role["role_name"],
                        "Entitlements": ", ".join(role["entitlements"][:3]) + ("..." if len(role["entitlements"]) > 3 else ""),
                        "Entitlement Count": len(role["entitlements"])
                    })

                if roles_data:
                    roles_df = pd.DataFrame(roles_data)
                    st.dataframe(roles_df, use_container_width=True)
                else:
                    st.warning("No roles found")

            with tab4:
                st.subheader("Entitlements")
                ent_data = []
                for ent in result["entitlements"]:
                    ent_data.append({
                        "Resource": ent["resource_name"],
                        "Description": ent.get("description", "N/A")
                    })

                if ent_data:
                    ent_df = pd.DataFrame(ent_data)
                    st.dataframe(ent_df, use_container_width=True)
                else:
                    st.warning("No entitlements found")

            with tab5:
                st.subheader("Schema Detection & Explanations")

                explain_df = pd.DataFrame(result["explanations"])

                # Summary Statistics
                col1, col2, col3 = st.columns(3)

                with col1:
                    high_conf = len(explain_df[explain_df["confidence"] >= 0.7])
                    st.metric("High Confidence", high_conf, delta=f"≥0.7")

                with col2:
                    med_conf = len(explain_df[(explain_df["confidence"] >= 0.5) & (explain_df["confidence"] < 0.7)])
                    st.metric("Medium Confidence", med_conf, delta="0.5-0.7")

                with col3:
                    low_conf = len(explain_df[explain_df["confidence"] < 0.5])
                    st.metric("Low Confidence", low_conf, delta="<0.5")

                st.divider()

                # Detailed explanations
                st.write("**Column Mapping Details:**")
                st.dataframe(explain_df, use_container_width=True)

                # Highlight problematic mappings
                if len(explain_df[explain_df["confidence"] < confidence_threshold]) > 0:
                    st.warning(f"⚠️ {len(explain_df[explain_df['confidence'] < confidence_threshold])} mappings below confidence threshold")
                    problematic = explain_df[explain_df["confidence"] < confidence_threshold]
                    st.dataframe(problematic, use_container_width=True)

            # ========== OUTPUT GENERATION ==========
            st.divider()
            st.subheader("📤 Generate Outputs with Templates")

            os.makedirs("output", exist_ok=True)

            # Initialize Export Manager
            export_mgr = ExportManager("output", "templates")

            # Enhanced export with template and GSI support
            col1, col2 = st.columns(2)

            with col1:
                st.write("**Export Mode:** " + export_mode)
                st.write(f"**Templates Selected:** {len(selected_templates) if export_mode != 'By Format' else len(template_mgr.get_templates_by_format(selected_format))}")

            with col2:
                st.write("**GSI Metadata:** " + ("✓ Enabled" if include_gsi_metadata else "✗ Disabled"))
                st.write("**Audit Trail:** " + ("✓ Enabled" if generate_audit_trail else "✗ Disabled"))

            st.divider()

            # New enhanced export button
            if st.button("✨ Generate Outputs with Template", use_container_width=True, type="primary"):
                with st.spinner("🔄 Preparing data and generating outputs..."):
                    try:
                        # Prepare GSI export
                        gsi_export_data = export_mgr.prepare_gsi_export(user_df, role_df, gsi_id)
                        
                        # Add explanations if requested
                        if include_explanations:
                            gsi_export_data["explanations"] = result.get("explanations", [])
                        
                        # Merge with processing result
                        gsi_export_data.update(result)
                        gsi_export_data["gsi_id"] = gsi_id

                        # Execute export based on mode
                        if export_mode == "Single Template" and selected_templates:
                            export_result = export_mgr.export_with_template(
                                gsi_id,
                                selected_templates[0],
                                gsi_export_data,
                                f"IAM_Export_{gsi_id}"
                            )
                        elif export_mode == "Multiple Templates" and selected_templates:
                            export_result = export_mgr.export_multiple_templates(
                                gsi_id,
                                selected_templates,
                                gsi_export_data,
                                f"IAM_Export_{gsi_id}"
                            )
                        elif export_mode == "All GSI-Aware Templates":
                            export_result = export_mgr.export_all_gsi_aware(
                                gsi_id,
                                gsi_export_data,
                                f"IAM_Export_{gsi_id}"
                            )
                        elif export_mode == "By Format":
                            export_result = export_mgr.export_by_format(
                                gsi_id,
                                selected_format,
                                gsi_export_data,
                                f"IAM_Export_{gsi_id}"
                            )

                        # Generate audit trail if requested
                        if generate_audit_trail:
                            audit_path = os.path.join(
                                "output",
                                f"Audit_Trail_{gsi_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                            )
                            export_mgr.pdf_generator.generate_audit_trail(
                                audit_path,
                                gsi_id,
                                gsi_export_data,
                                result.get("explanations", [])
                            )
                            if "generated_files" in export_result:
                                export_result["generated_files"].append({
                                    "file": audit_path,
                                    "format": "PDF",
                                    "type": "Audit Trail"
                                })
                            else:
                                export_result["generated_files"] = [{
                                    "file": audit_path,
                                    "format": "PDF",
                                    "type": "Audit Trail"
                                }]

                        # Display results
                        st.success("✅ Export Generated Successfully!")
                        
                        # Show export summary
                        summary_text = export_mgr.get_export_summary(export_result)
                        st.code(summary_text, language="text")

                        # Display download buttons
                        st.subheader("📥 Download Generated Files")
                        
                        if "generated_files" in export_result:
                            for i, file_info in enumerate(export_result["generated_files"]):
                                file_path = file_info.get("file")
                                if os.path.exists(file_path):
                                    with open(file_path, "rb") as f:
                                        file_data = f.read()
                                    
                                    file_name = os.path.basename(file_path)
                                    file_type = file_info.get("type", "File")
                                    
                                    # Determine MIME type
                                    mime_types = {
                                        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                        ".pdf": "application/pdf"
                                    }
                                    
                                    file_ext = os.path.splitext(file_path)[1].lower()
                                    mime_type = mime_types.get(file_ext, "application/octet-stream")
                                    
                                    st.download_button(
                                        label=f"📥 {file_type} ({file_info.get('format')})",
                                        data=file_data,
                                        file_name=file_name,
                                        mime=mime_type,
                                        key=f"download_{i}"
                                    )
                        elif "exports" in export_result:
                            # Handle multiple export results
                            for export_idx, export_item in enumerate(export_result["exports"]):
                                for file_idx, file_info in enumerate(export_item.get("generated_files", [])):
                                    file_path = file_info.get("file")
                                    if os.path.exists(file_path):
                                        with open(file_path, "rb") as f:
                                            file_data = f.read()
                                        
                                        file_name = os.path.basename(file_path)
                                        file_type = file_info.get("type", "File")
                                        
                                        mime_types = {
                                            ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                            ".pdf": "application/pdf"
                                        }
                                        
                                        file_ext = os.path.splitext(file_path)[1].lower()
                                        mime_type = mime_types.get(file_ext, "application/octet-stream")
                                        
                                        st.download_button(
                                            label=f"📥 {file_type} ({file_info.get('format')})",
                                            data=file_data,
                                            file_name=file_name,
                                            mime=mime_type,
                                            key=f"download_{export_idx}_{file_idx}"
                                        )

                    except Exception as e:
                        st.error(f"❌ Error generating outputs: {str(e)}")
                        import traceback
                        st.error(traceback.format_exc())

            # ========== LEGACY BATCH DOWNLOAD ==========
            st.divider()
            st.subheader("📦 Legacy Output Generation (Excel, Word, Report)")

            col1, col2, col3 = st.columns(3)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            excel_path = f"output/T3_output_{gsi_id}_{timestamp}.xlsm"
            word_path = f"output/OLA_output_{gsi_id}_{timestamp}.docx"
            report_path = f"output/explainability_report_{gsi_id}_{timestamp}.xlsx"

            with col1:
                if st.button("📊 Generate T3 Excel", use_container_width=True):
                    with st.spinner("Generating Excel..."):
                        try:
                            ExcelGenerator().generate(
                                excel_template_path,
                                excel_path,
                                result
                            )
                            st.success("✅ T3 Excel generated")

                            with open(excel_path, "rb") as f:
                                st.download_button(
                                    "⬇️ Download T3 Excel",
                                    f,
                                    file_name=os.path.basename(excel_path),
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                )
                        except Exception as e:
                            st.error(f"Error: {str(e)}")

            with col2:
                if st.button("📄 Generate OLA Word", use_container_width=True):
                    with st.spinner("Generating Word document..."):
                        try:
                            WordGenerator().generate(
                                word_template_path,
                                word_path,
                                result
                            )
                            st.success("✅ OLA Word generated")

                            with open(word_path, "rb") as f:
                                st.download_button(
                                    "⬇️ Download OLA Word",
                                    f,
                                    file_name=os.path.basename(word_path),
                                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                                )
                        except Exception as e:
                            st.error(f"Error: {str(e)}")

            with col3:
                if st.button("📋 Generate Report", use_container_width=True):
                    with st.spinner("Generating report..."):
                        try:
                            ExplainReport().generate(result["explanations"], report_path)
                            st.success("✅ Report generated")

                            with open(report_path, "rb") as f:
                                st.download_button(
                                    "⬇️ Download Report",
                                    f,
                                    file_name=os.path.basename(report_path),
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                )
                        except Exception as e:
                            st.error(f"Error: {str(e)}")

            st.divider()

            if st.button("📦 Generate ALL Legacy Outputs", use_container_width=True):
                with st.spinner("Generating all legacy outputs..."):
                    try:
                        # Generate all
                        ExcelGenerator().generate(excel_template_path, excel_path, result)
                        WordGenerator().generate(word_template_path, word_path, result)
                        ExplainReport().generate(result["explanations"], report_path)

                        st.success("✅ All legacy outputs generated!")

                        col1, col2, col3 = st.columns(3)

                        with col1:
                            with open(excel_path, "rb") as f:
                                st.download_button(
                                    "📊 T3 Excel",
                                    f,
                                    file_name=os.path.basename(excel_path),
                                    key="excel_all"
                                )

                        with col2:
                            with open(word_path, "rb") as f:
                                st.download_button(
                                    "📄 OLA Word",
                                    f,
                                    file_name=os.path.basename(word_path),
                                    key="word_all"
                                )

                        with col3:
                            with open(report_path, "rb") as f:
                                st.download_button(
                                    "📋 Report",
                                    f,
                                    file_name=os.path.basename(report_path),
                                    key="report_all"
                                )

                    except Exception as e:
                        st.error(f"Error generating outputs: {str(e)}")

        except Exception as e:
            st.error(f"❌ Error during processing: {str(e)}")

# ========== FOOTER ==========
st.divider()
st.markdown("""
---
**IAM Automation Platform** • v1.0
- ✨ Adaptive Schema Detection
- 🧠 Semantic Intelligence
- 📚 Self-Learning Memory
- 🔍 Explainable Decisions
- ☁️ No External APIs
- 🚀 Enterprise Ready

For support, contact your IAM team.
""")
