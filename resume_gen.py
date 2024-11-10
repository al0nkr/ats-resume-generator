import json
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus.flowables import HRFlowable

class ResumeGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.custom_styles = {
            'Name': ParagraphStyle(
                'Name',
                parent=self.styles['Title'],
                fontSize=24,
                spaceAfter=10,
                spaceBefore=10,
                alignment=TA_CENTER,
                textColor=colors.black
            ),
            'ContactInfo': ParagraphStyle(
                'ContactInfo',
                parent=self.styles['Normal'],
                fontSize=10,
                alignment=TA_CENTER,
                spaceAfter=15,
                textColor=colors.black
            ),
            'SectionHeader': ParagraphStyle(
                'SectionHeader',
                parent=self.styles['Heading1'],
                fontSize=12,
                spaceBefore=15,
                spaceAfter=3,
                textColor=colors.black,
                textTransform='uppercase'
            ),
            'SubHeading': ParagraphStyle(
                'SubHeading',
                parent=self.styles['Normal'],
                fontSize=11,
                leading=14,
                textColor=colors.black
            ),
            'SubHeadingItalic': ParagraphStyle(
                'SubHeadingItalic',
                parent=self.styles['Normal'],
                fontSize=10,
                leading=12,
                textColor=colors.black,
                fontName='Helvetica-Oblique'
            ),
            'BulletPoint': ParagraphStyle(
                'BulletPoint',
                parent=self.styles['Normal'],
                fontSize=10,
                leftIndent=20,
                spaceBefore=0,
                spaceAfter=3,
                bulletIndent=10,
                textColor=colors.black
            )
        }

    def create_section_title(self, title):
        elements = []
        elements.append(Paragraph(title, self.custom_styles['SectionHeader']))
        elements.append(HRFlowable(
            width="100%",
            thickness=1,
            color=colors.black,
            spaceBefore=1,
            spaceAfter=6
        ))
        return elements

    def create_pdf(self, json_file_path, output_file='resume.pdf'):
        # Read JSON data
        with open(json_file_path, 'r') as file:
            data = json.load(file)

        doc = SimpleDocTemplate(
            output_file,
            pagesize=letter,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )

        story = []

        # Header
        story.append(Paragraph(data['name'], self.custom_styles['Name']))
        
        # Contact Info
        contact_items = []
        if data.get('phone'):
            contact_items.append(data['phone'])
        if data.get('email'):
            contact_items.append(f"<link href='mailto:{data['email']}'><u>{data['email']}</u></link>")
        if data.get('linkedin'):
            contact_items.append(f"<link href='{data['linkedin']}'><u>{data['linkedin'].split('/')[-1]}</u></link>")
        if data.get('github'):
            contact_items.append(f"<link href='{data['github']}'><u>{data['github'].split('/')[-1]}</u></link>")
        
        story.append(Paragraph(" | ".join(contact_items), self.custom_styles['ContactInfo']))

        # Education Section
        if data.get('education'):
            story.extend(self.create_section_title("Education"))
            for edu in data['education']:
                edu_table = [
                    [
                        Paragraph(f"<b>{edu['institution']}</b>", self.custom_styles['SubHeading']),
                        Paragraph(edu['location'], self.custom_styles['SubHeading'])
                    ],
                    [
                        Paragraph(f"<i>{edu['degree']}</i>", self.custom_styles['SubHeadingItalic']),
                        Paragraph(edu['date'], self.custom_styles['SubHeadingItalic'])
                    ]
                ]
                t = Table(edu_table, colWidths=[4*inch, None])
                t.setStyle(TableStyle([
                    ('ALIGN', (0,0), (0,-1), 'LEFT'),
                    ('ALIGN', (-1,0), (-1,-1), 'RIGHT'),
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ]))
                story.append(t)
                story.append(Spacer(1, 0.1*inch))

        # Experience Section
        if data.get('experience'):
            story.extend(self.create_section_title("Experience"))
            for exp in data['experience']:
                exp_table = [
                    [
                        Paragraph(f"<b>{exp['title']}</b>", self.custom_styles['SubHeading']),
                        Paragraph(exp['date'], self.custom_styles['SubHeading'])
                    ],
                    [
                        Paragraph(f"<i>{exp['company']}</i>", self.custom_styles['SubHeadingItalic']),
                        Paragraph(exp['location'], self.custom_styles['SubHeadingItalic'])
                    ]
                ]
                t = Table(exp_table, colWidths=[4*inch, None])
                t.setStyle(TableStyle([
                    ('ALIGN', (0,0), (0,-1), 'LEFT'),
                    ('ALIGN', (-1,0), (-1,-1), 'RIGHT'),
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ]))
                story.append(t)
                
                for bullet in exp['bullets']:
                    story.append(Paragraph(f"• {bullet}", self.custom_styles['BulletPoint']))
                story.append(Spacer(1, 0.1*inch))

        # Projects Section
        if data.get('projects'):
            story.extend(self.create_section_title("Projects"))
            for project in data['projects']:
                project_heading = f"<b>{project['name']}</b> | <i>{project['technologies']}</i>"
                story.append(Paragraph(project_heading, self.custom_styles['SubHeading']))
                
                for bullet in project['bullets']:
                    story.append(Paragraph(f"• {bullet}", self.custom_styles['BulletPoint']))
                story.append(Spacer(1, 0.1*inch))

        # Technical Skills Section
        if data.get('skills'):
            story.extend(self.create_section_title("Technical Skills"))
            for category, skills in data['skills'].items():
                skills_text = f"<b>{category}</b>: {', '.join(skills)}"
                story.append(Paragraph(skills_text, self.custom_styles['BulletPoint']))

        doc.build(story)
        return output_file

def main():
    try:
        generator = ResumeGenerator()
        pdf_file = generator.create_pdf('resume_data.json')
        print(f"Successfully generated PDF: {pdf_file}")
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")

if __name__ == "__main__":
    main()