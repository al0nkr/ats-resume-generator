from fpdf import FPDF
from fpdf.enums import XPos, YPos
import json

class ResumePDF(FPDF):
    def __init__(self):
        super().__init__(format='letter')
        # Reduce margins
        self.set_margins(left=10, top=10, right=10)
        self.set_auto_page_break(auto=True, margin=10)

    def header(self):
        pass

    def footer(self):
        pass

    def add_name(self, name):
        self.set_font('helvetica', 'B', 16)
        self.cell(0, 8, name, align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def add_contact_info(self, email, phone, linkedin, github):
        self.set_font('helvetica', '', 9)
        contact_parts = []
        if phone: contact_parts.append(phone)
        if email: contact_parts.append(email)
        if linkedin: contact_parts.append(f"linkedin.com/in/{linkedin}")
        if github: contact_parts.append(f"github.com/{github}")
        
        contact_line = " | ".join(contact_parts)
        self.cell(0, 4, contact_line, align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(4)

    def section_title(self, title):
        self.ln(2)
        self.set_font('helvetica', 'B', 12)
        self.cell(0, 5, title.upper(), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2)

    def add_education_item(self, institution, location, degree, date):
        self.set_font('helvetica', 'B', 10)
        
        # Split space 75% for institution, 25% for date
        left_width = self.epw * 0.75  # epw is effective page width (page width - margins)
        right_width = self.epw * 0.25
        
        inst_text = self.add_ellipsis(institution, left_width)
        self.cell(left_width, 4, inst_text, new_x=XPos.RIGHT)
        self.cell(right_width, 4, date, align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        if degree or location:
            self.set_font('helvetica', 'I', 9)
            text = degree
            if location:
                text = f"{text}, {location}" if text else location
            self.cell(0, 4, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(1)

    def add_ellipsis(self, text, width):
        while self.get_string_width(text) > width and len(text) > 3:
            text = text[:-1]
        return text

    def add_experience_item(self, title, company, location, date, bullets):
        self.set_font('helvetica', 'B', 10)
        
        left_width = self.epw * 0.75
        right_width = self.epw * 0.25
        
        title_text = self.add_ellipsis(title, left_width)
        self.cell(left_width, 4, title_text, new_x=XPos.RIGHT)
        self.cell(right_width, 4, date, align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        if company or location:
            self.set_font('helvetica', 'I', 9)
            text = company
            if location:
                text = f"{text}, {location}" if text else location
            self.cell(0, 4, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        if bullets:
            self.set_font('helvetica', '', 9)
            for bullet in bullets:
                self.set_x(15)  # Indent for bullet points
                self.cell(3, 4, "-", new_x=XPos.RIGHT)
                self.multi_cell(0, 4, bullet.strip())
        self.ln(1)

    def add_project_item(self, name, technologies, bullets):
        self.set_font('helvetica', 'B', 10)
        
        # Project name
        name_width = self.get_string_width(name)
        available_width = self.epw - 20  # Leave space for technologies
        
        if technologies:
            self.cell(name_width, 4, name, new_x=XPos.RIGHT)
            self.set_font('helvetica', 'I', 9)
            self.cell(0, 4, f" | {technologies}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        else:
            self.cell(0, 4, name, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        if bullets:
            self.set_font('helvetica', '', 9)
            for bullet in bullets:
                self.set_x(15)
                self.cell(3, 4, "-", new_x=XPos.RIGHT)
                self.multi_cell(0, 4, bullet.strip())
        self.ln(1)

    def add_skills_section(self, skills):
        first = True
        for category, items in skills.items():
            if items:
                if not first:
                    self.ln(1)
                self.set_font('helvetica', 'B', 9)
                category_text = f"{category}: "
                self.cell(self.get_string_width(category_text), 4, category_text, new_x=XPos.RIGHT)
                
                self.set_font('helvetica', '', 9)
                self.multi_cell(0, 4, ", ".join(items))
                first = False

def generate_resume(json_file='formatted_resume.json'):
    try:
        with open(json_file, 'r') as file:
            data = json.load(file)

        pdf = ResumePDF()
        pdf.add_page()

        # Header with name and contact info
        pdf.add_name(data['name'])
        pdf.add_contact_info(data['email'], data['phone'], data['linkedin'], data['github'])

        # Education Section
        if data['education']:
            pdf.section_title('Education')
            for edu in data['education']:
                pdf.add_education_item(
                    edu['institution'],
                    edu['location'],
                    edu['degree'],
                    edu['date']
                )

        # Experience Section
        if data['experience']:
            pdf.section_title('Experience')
            for exp in data['experience']:
                pdf.add_experience_item(
                    exp['title'],
                    exp['company'],
                    exp['location'],
                    exp['date'],
                    exp['bullets']
                )

        # Projects Section
        if data['projects']:
            pdf.section_title('Projects')
            for project in data['projects']:
                pdf.add_project_item(
                    project['name'],
                    project['technologies'],
                    project['bullets']
                )

        # Skills Section
        if data['skills']:
            pdf.section_title('Technical Skills')
            pdf.add_skills_section(data['skills'])

        # Generate PDF
        output_filename = f"{data['name'].lower().replace(' ', '_')}_resume.pdf"
        pdf.output(output_filename)
        print(f"Resume generated successfully as {output_filename}!")
        
    except FileNotFoundError:
        print(f"Error: The file '{json_file}' was not found.")
    except json.JSONDecodeError:
        print(f"Error: The file '{json_file}' contains invalid JSON.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    generate_resume()