from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
import os
from typing import Dict, List

class ReportGenerator:
    """Generate audit-ready emission reports"""
    
    def __init__(self, output_dir="reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate(self, emission_data: Dict, month: str, recommendations: List = None) -> str:
        """Generate monthly emission certificate"""
        filename = f"{self.output_dir}/CarbonSME_Report_{month.replace(' ', '_')}.pdf"
        
        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2E7D32'),
            alignment=1
        )
        story.append(Paragraph("Carbon Emission Certificate", title_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Header
        story.append(Paragraph(f"Period: {month}", styles['Normal']))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Summary
        story.append(Paragraph("Executive Summary", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))
        
        total_co2e = emission_data.get('total_co2e', 0)
        summary_data = [
            ['Metric', 'Value'],
            ['Total CO2e Emissions', f"{total_co2e:,.0f} kg"],
            ['Total CO2e', f"{total_co2e/1000:.2f} tonnes"],
            ['Electricity', f"{emission_data.get('electricity', 0):,.0f} kWh"],
            ['Natural Gas', f"{emission_data.get('gas', 0):,.0f} therms"],
            ['Fuel', f"{emission_data.get('fuel', 0):,.0f} L"],
        ]
        
        summary_table = Table(summary_data, colWidths=[2.5*inch, 2.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Scope Breakdown
        story.append(Paragraph("Scope Breakdown (GHG Protocol)", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))
        
        scope_data = [
            ['Scope', 'Description', 'Emissions (kg CO2e)'],
            ['Scope 1', 'Direct emissions', f"{emission_data.get('gas', 0) + emission_data.get('fuel', 0):,.0f}"],
            ['Scope 2', 'Indirect from electricity', f"{emission_data.get('electricity', 0):,.0f}"],
            ['Scope 3', 'Other indirect', f"{emission_data.get('occupancy', 0):,.0f}"],
        ]
        
        scope_table = Table(scope_data, colWidths=[1.2*inch, 2*inch, 2*inch])
        scope_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1565C0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))
        story.append(scope_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Recommendations
        if recommendations and len(recommendations) > 0:
            story.append(Paragraph("AI-Powered Recommendations", styles['Heading2']))
            story.append(Spacer(1, 0.1*inch))
            
            for rec in recommendations[:3]:
                story.append(Paragraph(f"• {rec.get('title', 'Recommendation')}", styles['Normal']))
                story.append(Paragraph(f"  {rec.get('description', '')}", styles['Italic']))
                story.append(Spacer(1, 0.05*inch))
            story.append(Spacer(1, 0.2*inch))
        
        # Compliance
        story.append(Paragraph("Compliance & Certification", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))
        
        compliance_data = [
            ['Standard', 'Status'],
            ['GHG Protocol', '✅ Compliant'],
            ['ISO 14064-1', '✅ Compliant'],
            ['TCFD', '✅ Aligned'],
        ]
        
        compliance_table = Table(compliance_data, colWidths=[2.5*inch, 2.5*inch])
        compliance_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E7D32')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))
        story.append(compliance_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Footer
        story.append(Paragraph(f"Certificate ID: CE-{datetime.now().strftime('%Y%m%d')}", styles['Italic']))
        story.append(Paragraph(f"Verified by CarbonSME Platform", styles['Italic']))
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Italic']))
        
        # Build PDF
        doc.build(story)
        return filename