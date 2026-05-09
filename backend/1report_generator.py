from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
import os
from typing import Dict  # ADD THIS IMPORT

class ReportGenerator:
    """Generate audit-ready emission reports"""
    
    def __init__(self, output_dir="reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate(self, emission_data: Dict, month: str) -> str:
        """Generate monthly emission certificate"""
        filename = f"{self.output_dir}/certificate_{month}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
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
        
        # Emissions table
        data = [['Emission Source', 'kg CO2e', 'Scope']]
        for source, value in emission_data.get('details', {}).items():
            scope = 'Scope 2' if source == 'Electricity' else 'Scope 1' if source in ['Natural Gas', 'Fuel'] else 'Scope 3'
            data.append([source, f"{value:,.0f}", scope])
        
        data.append(['', '', ''])
        data.append(['Total', f"{emission_data.get('total_co2e_kg', 0):,.0f}", 'All Scopes'])
        
        table = Table(data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ]))
        story.append(table)
        story.append(Spacer(1, 0.3*inch))
        
        # Footer
        story.append(Paragraph("Methodology: GHG Protocol Corporate Standard", styles['Italic']))
        story.append(Paragraph(f"Certificate ID: CE-{datetime.now().strftime('%Y%m')}-{hash(month) % 10000:04d}", styles['Italic']))
        
        doc.build(story)
        return filename