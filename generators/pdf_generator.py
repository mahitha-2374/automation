"""
PDF Report Generator
Generates professional PDF reports from IAM data with GSI information
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from datetime import datetime
import os


class PDFGenerator:
    """Generate professional PDF reports"""

    def __init__(self):
        """Initialize PDF Generator"""
        self.styles = getSampleStyleSheet()
        self._add_custom_styles()

    def _add_custom_styles(self):
        """Add custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=30,
            alignment=1
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c5aa0'),
            spaceAfter=12,
            spaceBefore=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='GSIInfo',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#333333'),
            spaceAfter=6
        ))

    def generate_executive_summary(self, output_path: str, gsi_id: str, data: dict):
        """
        Generate executive summary PDF
        
        Args:
            output_path: Where to save the PDF
            gsi_id: GSI ID for the report
            data: Processed IAM data
        """
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch
        )

        story = []

        # Title
        title = Paragraph("IAM Executive Summary Report", self.styles['CustomTitle'])
        story.append(title)

        # GSI Information Box
        gsi_info_data = [
            ["Application GSI ID", gsi_id],
            ["Generated Date", datetime.now().strftime("%Y-%m-%d")],
            ["Generated Time", datetime.now().strftime("%H:%M:%S")],
        ]

        gsi_table = Table(gsi_info_data, colWidths=[2 * inch, 3 * inch])
        gsi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8eef7')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        story.append(gsi_table)
        story.append(Spacer(1, 12))

        # Summary Statistics
        story.append(Paragraph("Summary Statistics", self.styles['CustomHeading']))

        stats_data = [
            ["Metric", "Value"],
            ["Total Users", str(len(data.get("users", [])))],
            ["Total Roles", str(len(data.get("roles", [])))],
            ["Total Entitlements", str(len(data.get("entitlements", [])))],
            ["User-Role Mappings", str(sum(len(u.get("roles", [])) for u in data.get("users", [])))],
        ]

        stats_table = Table(stats_data, colWidths=[3 * inch, 2 * inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')])
        ]))

        story.append(stats_table)
        story.append(Spacer(1, 12))

        # Key Findings
        story.append(Paragraph("Key Information", self.styles['CustomHeading']))
        story.append(Spacer(1, 6))

        findings = [
            f"GSI ID: {gsi_id}",
            f"User Population: {len(data.get('users', []))} active users",
            f"Role Structure: {len(data.get('roles', []))} defined roles",
            f"Data Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ]

        for finding in findings:
            story.append(Paragraph(f"• {finding}", self.styles['GSIInfo']))
            story.append(Spacer(1, 4))

        story.append(Spacer(1, 12))
        
        # Footer
        story.append(Paragraph(
            "_" * 80,
            self.styles['Normal']
        ))
        story.append(Spacer(1, 6))
        story.append(Paragraph(
            f"<i>This report contains confidential IAM information for {gsi_id}. "
            "Please handle appropriately.</i>",
            self.styles['Normal']
        ))

        # Build PDF
        doc.build(story)

    def generate_detailed_report(self, output_path: str, gsi_id: str, data: dict):
        """
        Generate detailed analysis PDF
        
        Args:
            output_path: Where to save the PDF
            gsi_id: GSI ID for the report
            data: Processed IAM data
        """
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch
        )

        story = []

        # Title
        title = Paragraph("IAM Detailed Analysis Report", self.styles['CustomTitle'])
        story.append(title)

        # GSI Information
        story.append(Paragraph(f"Application: {gsi_id}", self.styles['CustomHeading']))
        story.append(Spacer(1, 6))

        gsi_info = [
            f"GSI ID: <b>{gsi_id}</b>",
            f"Report Date: <b>{datetime.now().strftime('%Y-%m-%d')}</b>",
            f"Report Time: <b>{datetime.now().strftime('%H:%M:%S')}</b>"
        ]

        for info in gsi_info:
            story.append(Paragraph(info, self.styles['GSIInfo']))
            story.append(Spacer(1, 3))

        story.append(Spacer(1, 12))

        # User Analysis
        story.append(Paragraph("User Analysis", self.styles['CustomHeading']))
        story.append(Spacer(1, 6))

        user_summary = f"Total Users: <b>{len(data.get('users', []))}</b>"
        story.append(Paragraph(user_summary, self.styles['GSIInfo']))
        story.append(Spacer(1, 6))

        # User Table
        user_data = [["User ID", "Roles"]]
        for user in data.get("users", [])[:10]:  # Show first 10 users
            user_id = user.get("user_id", "N/A")
            role_count = len(user.get("roles", []))
            user_data.append([user_id, str(role_count)])

        if len(data.get("users", [])) > 10:
            user_data.append(["...", "..."])
            user_data.append(["Total Users", str(len(data.get("users", [])))])

        user_table = Table(user_data, colWidths=[3 * inch, 2 * inch])
        user_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))

        story.append(user_table)
        story.append(Spacer(1, 12))

        # Role Analysis
        story.append(PageBreak())
        story.append(Paragraph("Role Analysis", self.styles['CustomHeading']))
        story.append(Spacer(1, 6))

        role_summary = f"Total Roles: <b>{len(data.get('roles', []))}</b>"
        story.append(Paragraph(role_summary, self.styles['GSIInfo']))
        story.append(Spacer(1, 6))

        # Role Table
        role_data = [["Role Name", "Entitlements"]]
        for role in data.get("roles", [])[:10]:  # Show first 10 roles
            role_name = role.get("role_name", "N/A")
            ent_count = len(role.get("entitlements", []))
            role_data.append([role_name, str(ent_count)])

        if len(data.get("roles", [])) > 10:
            role_data.append(["...", "..."])
            role_data.append(["Total Roles", str(len(data.get("roles", [])))])

        role_table = Table(role_data, colWidths=[3 * inch, 2 * inch])
        role_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))

        story.append(role_table)

        # Build PDF
        doc.build(story)

    def generate_audit_trail(self, output_path: str, gsi_id: str, data: dict, 
                            explanations: list = None):
        """
        Generate audit trail PDF from explanations
        
        Args:
            output_path: Where to save the PDF
            gsi_id: GSI ID for the report
            data: Processed IAM data
            explanations: List of explanation dictionaries
        """
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch
        )

        story = []

        # Title
        title = Paragraph("IAM Audit Trail Report", self.styles['CustomTitle'])
        story.append(title)

        # GSI Information
        story.append(Paragraph(f"Application: {gsi_id}", self.styles['CustomHeading']))
        story.append(Spacer(1, 12))

        # Audit Information
        if explanations:
            audit_data = [["Column", "Category", "Confidence", "Method"]]
            
            for exp in explanations[:20]:  # Show first 20
                audit_data.append([
                    exp.get("column", "N/A"),
                    exp.get("category", "N/A"),
                    f"{exp.get('confidence', 0):.2f}",
                    exp.get("method", "N/A")
                ])

            if len(explanations) > 20:
                audit_data.append(["...", "...", "...", "..."])

            audit_table = Table(audit_data, colWidths=[1.5*inch, 1.5*inch, 1.2*inch, 1.2*inch])
            audit_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))

            story.append(audit_table)

        # Build PDF
        doc.build(story)
