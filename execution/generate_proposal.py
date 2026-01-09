import json
import argparse
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import os
import datetime

# --- Constants & Config ---
NAVY_BLUE = (26, 26, 62)  # #1a1a3e
LIGHT_GRAY = (240, 240, 240)
WHITE = (255, 255, 255)
TEXT_DARK = (40, 40, 40)
ACCENT_BLUE = (0, 123, 255) # For links/buttons

# Standard Legal Text
TERMS_AND_CONDITIONS = """Sipes Automation will build an automated system for {client_company} according to the description laid out in this proposal and pursuant to the attached Services Agreement. The Services Agreement protects your confidentiality and includes a nondisclosure clause that streamlines our information sharing.

Additional features, extensions, or other integrations separate from the listed requirements may affect the timeline & costs laid out above. If you have a question or comment, email msipes@sipesautomation.com

By signing below, both parties indicate their acceptance of this proposal and the attached Services Agreement and constitute approval to begin work upon {client_company}'s payment."""

SERVICES_AGREEMENT = """Prior to a contractual agreement, this proposal may be amended in consultation with the client, {client_company}, at the discretion of Sipes Automation.

Terms of Engagement
This Professional Service Agreement ("Agreement") shall become effective on the date of signing. The engagement under this Agreement shall continue for a period of the project and shall automatically terminate upon the expiration of said period unless terminated earlier in accordance with the terms herein.

Extension
The engagement may be extended by mutual written agreement of the parties, subject to any amendments to the terms, scope, or compensation, as may be mutually agreed upon.

Termination for Convenience
Either Party may terminate this Agreement for convenience with 15 day written notice to the other Party. In such cases, the Client shall pay for services rendered up to the date of termination and any reasonable costs associated with the termination.

Payment Terms
Payment for the services rendered under this Agreement is due as specified in the Investment section.

Confidentiality & Ownership
Sipes Automation ensures full confidentiality of client data. Upon full payment, the Client retains full ownership of the deliverables."""

class ProposalPDF(FPDF):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.set_auto_page_break(auto=True, margin=15)
        self.section_counter = 1

    def header(self):
        # Skip header on cover page (page 1)
        if self.page_no() == 1:
            return
            
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(150, 150, 150)
        title_text = f'SIPES AUTOMATION | {self.data.get("proposal_number", "PROPOSAL")}'
        self.cell(0, 10, title_text, align='R', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)

    def footer(self):
        # Skip footer
        if self.page_no() == 1:
            return
            
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        
        company = self.data.get('client_company', 'Client')
        # Shorten if it's the full legal name
        if " (PTY) Ltd" in company:
            company = company.replace(" (PTY) Ltd", "")
            
        text = f"Sipes Automation | Prepared for {company} | Confidential | Page {self.page_no()}"
        self.cell(0, 10, text, align='C')

    def draw_cover_page(self):
        self.add_page()
        
        # Background Color (Full Page)
        self.set_fill_color(*NAVY_BLUE)
        self.rect(0, 0, 210, 297, 'F')
        
        # Content
        self.set_text_color(*WHITE)
        
        # Vertical Spacer
        self.ln(60)
        
        # Branding
        self.set_font('Helvetica', 'B', 14)
        self.cell(0, 10, "SIPES AUTOMATION", align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(10)
        
        # Project Title
        self.set_font('Helvetica', 'B', 32)
        # Handle long titles with multi_cell but centered
        title = self.data.get('project_title', 'Automation Project').upper()
        self.multi_cell(0, 15, title, align='C')
        # Title
        self.set_y(100)
        self.set_font('Helvetica', 'B', 24)
        self.set_text_color(*TEXT_DARK)
        self.cell(0, 10, "AUTOMATION PROPOSAL", align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        # Subtitle / J-Number
        j_num = self.data.get('j_number', '')
        rev = self.data.get('revision', '')
        subtitle = f"{j_num} {'| Rev ' + str(rev) if rev else ''}"
        
        self.ln(5)
        self.set_font('Helvetica', '', 14)
        self.set_text_color(*NAVY_BLUE)
        self.cell(0, 10, subtitle, align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        # Prepared For
        self.ln(30)
        self.set_font('Helvetica', '', 12)
        # White text for cover page background
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, "PREPARED FOR", align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, self.data.get('client_name', 'Client Name'), align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font('Helvetica', '', 14)
        self.cell(0, 8, self.data.get('client_company', 'Client Company'), align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        # Address / Reg
        if self.data.get('client_address') or self.data.get('client_reg_no'):
            self.ln(2)
            self.set_font('Helvetica', '', 10)
            self.set_text_color(230, 230, 230) # Slightly off-white for secondary info
            if self.data.get('client_reg_no'):
                self.cell(0, 6, f"Reg No: {self.data.get('client_reg_no')}", align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            if self.data.get('client_address'):
                self.cell(0, 6, self.data.get('client_address'), align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def sanitize_text(self, text):
        if not isinstance(text, str):
            return str(text)
        replacements = {
            '\u2013': '-',   # en-dash
            '\u2014': '-',   # em-dash
            '\u2018': "'",   # left single quote
            '\u2019': "'",   # right single quote
            '\u201c': '"',   # left double quote
            '\u201d': '"',   # right double quote
            '\u2022': '*',   # bullet
            '\u2026': '...'  # ellipsis
        }
        for char, repl in replacements.items():
            text = text.replace(char, repl)
        
        # Ensure compatible encoding
        return text.encode('latin-1', 'replace').decode('latin-1')

    def body_text(self, text, style='', size=11):
        self.set_font('Helvetica', style, size)
        self.set_text_color(*TEXT_DARK)
        self.multi_cell(0, 6, self.sanitize_text(text))
        self.ln(2)

    def chapter_title(self, label):
        # Section Number Block
        self.set_fill_color(*NAVY_BLUE)
        self.set_text_color(*WHITE)
        self.set_font('Helvetica', 'B', 14)
        
        # Square with number
        num_str = str(self.section_counter)
        self.cell(12, 12, num_str, fill=True, align='C', new_x=XPos.RIGHT)
        
        # Title text
        self.set_text_color(*NAVY_BLUE)
        self.cell(5, 12, "", new_x=XPos.RIGHT) # Spacer
        self.cell(0, 12, self.sanitize_text(label.upper()), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        self.ln(5)
        self.section_counter += 1

    def check_page_break(self, height_needed):
        """Check if we need a new page before printing something of height_needed."""
        if self.get_y() + height_needed > 270: # 297mm height - margins
            self.add_page()
            
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        
        company = self.data.get('client_company', 'Client')
        self.cell(0, 10, f'Confidential | Prepared for {self.sanitize_text(company)} | Page {self.page_no()}', align='C')

    def draw_callout(self, text):
        """Draws a text block with a vertical accent bar on the left."""
        self.check_page_break(20)
        # Accent Bar
        start_x = self.get_x()
        start_y = self.get_y()
        self.set_fill_color(*NAVY_BLUE)
        self.rect(start_x, start_y, 1.5, 8, 'F') # 1.5mm wide bar
        
        # Text
        self.set_x(start_x + 4) # Indent past bar
        self.set_font('Helvetica', 'I', 10)
        self.set_text_color(*TEXT_DARK)
        self.multi_cell(0, 5, self.sanitize_text(text))
        
        # Add some spacing after
        self.ln(3)

    def generate(self):
        # 1. Cover Page
        self.draw_cover_page()
        
        self.add_page()
        
        # 2. Executive Summary (Problem & Solution)
        
        # Section 1: The Problem
        self.check_page_break(40) # Ensure title + some text fits
        self.chapter_title("The Problem")
        problem = self.data.get('problem_statement', self.data.get('executive_summary', ''))
        self.body_text(problem)
        self.ln(5)

        # Optional: Diagram (Moved to Problem Section)
        diagram_path = self.data.get('diagram_image')
        if diagram_path and os.path.exists(diagram_path):
            # Check if image fits on current page, else add page
            space_left = 270 - self.get_y()
            if space_left < 100: # Assume image needs ~100mm
                self.add_page()
                
            self.set_font('Helvetica', 'I', 9)
            self.cell(0, 5, "Figure 1: Current vs. Future Process Flow", align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            
            img_width = 180
            x_pos = (210 - img_width) / 2
            self.image(diagram_path, x=x_pos, w=img_width)
            self.ln(5)

            # Phasing / Diagram Context
            phasing = self.data.get('project_phasing')
            if phasing:
                self.check_page_break(40)
                # Note
                if phasing.get('note'):
                    self.draw_callout(f"Note: {phasing['note']}")
                
                # Included Steps
                steps = phasing.get('included_steps', [])
                if steps:
                    self.set_font('Helvetica', 'B', 10)
                    self.set_text_color(*TEXT_DARK)
                    self.cell(0, 6, "Included in this Phase:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    self.set_font('Helvetica', '', 10)
                    for step in steps:
                        self.cell(5, 5, "-", align='R', new_x=XPos.RIGHT)
                        self.cell(0, 5, self.sanitize_text(step), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    self.ln(3)
            self.ln(5)
        
        # Section 2: The Solution
        self.check_page_break(40)
        self.chapter_title("The Solution")
        solution = self.data.get('proposed_solution', '')
        self.body_text(solution)
        self.ln(5)
        
        # Section 3: Scope of Work
        self.check_page_break(60)
        self.chapter_title("Scope of Work")
        for item in self.data.get('scope_of_work', []):
            self.check_page_break(30)
            
            title = item.get('title', 'Deliverable')
            desc = item.get('description', '')
            
            # Bullet point style
            self.set_font('Helvetica', 'B', 11)
            self.set_text_color(*NAVY_BLUE)
            self.cell(5, 6, chr(149), align='R', new_x=XPos.RIGHT) # Bullet char
            self.cell(0, 6, self.sanitize_text(title), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            
            # Indented description
            self.set_x(self.get_x() + 7) 
            self.body_text(desc)
            self.ln(2)
        
        # Exclusions
        exclusions = self.data.get('exclusions', [])
        if exclusions:
            self.check_page_break(30)
            self.set_font('Helvetica', 'B', 11)
            self.set_text_color(*TEXT_DARK)
            self.cell(0, 6, "Exclusions:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.set_font('Helvetica', '', 10)
            for excl in exclusions:
                self.cell(5, 5, "-", align='R', new_x=XPos.RIGHT)
                self.cell(0, 5, self.sanitize_text(excl), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(3)

        # Revision Policy (Styled)
        self.draw_callout("Review Policy: Scope includes two (2) rounds of refinements. Additional feature requests billed hourly. Client agrees to provide feedback within 48 hours.")
        self.ln(2)
            
        # Section 4: Timeline
        self.check_page_break(50)
        self.chapter_title("Timeline")
        
        timeline_val = self.data.get('timeline', 'TBD')
        
        # Primary Delivery Date
        self.set_font('Helvetica', 'B', 11)
        self.cell(40, 6, "Initial Delivery:", new_x=XPos.RIGHT)
        self.set_font('Helvetica', '', 11)
        self.cell(0, 6, timeline_val, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(3)

        # Standard Notes (Styled)
        notes = [
            "We will monitor the system for 30 days immediately following delivery.",
            "Alert: Delays in receiving access to systems will cause corresponding delays in delivery."
        ]
        
        for note in notes:
            self.draw_callout(note)
        
        self.ln(5)

        # Section 5: Access Requirements
        access_reqs = self.data.get('access_requirements', [])
        if access_reqs:
            self.check_page_break(60) 
            self.chapter_title("Access Requirements")
            self.body_text("Preliminary list of systems requiring access credentials:")
            
            for req in access_reqs:
                self.check_page_break(15)
                self.set_font('Helvetica', 'B', 11)
                self.set_text_color(*NAVY_BLUE)
                self.cell(5, 6, chr(149), align='R', new_x=XPos.RIGHT) # Bullet
                self.cell(0, 6, self.sanitize_text(req), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(5)

        # Section 6: Related Systems
        related = self.data.get('related_systems')
        if related:
            self.check_page_break(60)
            self.chapter_title("Related Systems")
            self.body_text("Additional high-ROI systems we have successfully deployed:")
            self.ln(2)
            
            for sys_item in related:
                self.check_page_break(30)
                if isinstance(sys_item, dict):
                    r_title = sys_item.get('title', 'System')
                    r_desc = sys_item.get('description', '')
                    
                    self.set_font('Helvetica', 'B', 11)
                    self.set_text_color(*NAVY_BLUE)
                    self.cell(5, 6, "-", align='R', new_x=XPos.RIGHT)
                    self.cell(0, 6, self.sanitize_text(r_title), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    
                    self.set_x(self.get_x() + 7)
                    self.body_text(r_desc)
                    self.ln(2)
                else:
                    self.set_font('Helvetica', 'B', 11)
                    self.cell(5, 6, "-", align='R', new_x=XPos.RIGHT)
                    self.cell(0, 6, self.sanitize_text(str(sys_item)), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(5)

        # Section 6.5: Relevant Experience (Proof of Work)
        relevant_projects = self.data.get('relevant_projects')
        if relevant_projects:
            self.check_page_break(60)
            self.chapter_title("Relevant Experience")
            self.body_text("We have successfully delivered similar automation systems for other clients:")
            self.ln(2)

            for project in relevant_projects:
                self.check_page_break(30)
                
                # Title & Stats
                title = project.get('title', 'Project')
                industry = project.get('industry', '')
                
                self.set_font('Helvetica', 'B', 11)
                self.set_text_color(*NAVY_BLUE)
                self.cell(5, 6, chr(149), align='R', new_x=XPos.RIGHT)
                
                # Title line with Industry if available
                header_text = title
                if industry:
                    header_text += f" ({industry})"
                
                self.cell(0, 6, self.sanitize_text(header_text), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                
                # Description
                desc = project.get('description', '')
                self.set_x(self.get_x() + 7)
                self.body_text(desc)
                
                # Tech Stack line
                tech = project.get('technologies', [])
                if tech:
                    self.set_x(self.get_x() + 7)
                    self.set_font('Helvetica', 'I', 9)
                    self.set_text_color(100, 100, 100)
                    tech_str = ", ".join(tech)
                    self.cell(0, 5, self.sanitize_text(f"Tech: {tech_str}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                
                self.ln(3)
            self.ln(5)

        # Section 7: Your Investment
        self.add_page() # Force new page for pricing
        self.chapter_title("Your Investment")
        
        # Table Header
        self.set_fill_color(*LIGHT_GRAY)
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(*TEXT_DARK)
        self.cell(110, 10, "  Item", fill=True, border=0)
        self.cell(30, 10, "Price", fill=True, align='R', border=0)
        self.cell(40, 10, "Type", fill=True, align='R', border=0) 
        self.ln()
        
        # Table Body (Zebra Striped)
        self.set_font('Helvetica', '', 10)
        total = 0
        
        # Draw top line
        self.set_draw_color(200, 200, 200)
        self.line(self.get_x(), self.get_y(), self.get_x() + 180, self.get_y())
        
        # Zebra settings
        fill_rows = False
        
        for cost in self.data.get('investment', []):
            price = cost.get('cost', 0)
            total += price
            
            if fill_rows:
                self.set_fill_color(245, 245, 245) # Very light gray for stripe
            else:
                self.set_fill_color(255, 255, 255)
            
            # Row
            self.cell(110, 10, f"  {self.sanitize_text(cost.get('item', 'Service'))}", border='B', fill=fill_rows)
            self.cell(30, 10, f"${price:,.2f}", align='R', border='B', fill=fill_rows)
            self.cell(40, 10, "Fee  ", align='R', border='B', fill=fill_rows)
            self.ln()
            
            fill_rows = not fill_rows

        # Totals
        deposit = total * 0.5
        self.ln(5)
        
        self.set_font('Helvetica', 'B', 12)
        self.cell(110, 10, "TOTAL INVESTMENT", align='R')
        self.cell(30, 10, f"${total:,.2f}", align='R')
        self.ln()
        
        self.set_text_color(*NAVY_BLUE)
        self.cell(110, 10, "50% DEPOSIT DUE NOW", align='R')
        self.cell(30, 10, f"${deposit:,.2f}", align='R')
        self.ln(10)

        # Optional: Future Phases
        future_phases = self.data.get('future_phases')
        if future_phases:
            self.draw_callout(f"Future Phase: {future_phases}")
        
        # Billing Terms
        self.check_page_break(30)
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(*TEXT_DARK)
        self.cell(0, 8, "Billing Terms:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font('Helvetica', '', 10)
        
        default_terms = "A 50% deposit is required to commence work. The remaining 50% is due upon delivery of the system for testing."
        terms = self.data.get('billing_terms', default_terms)
        
        self.multi_cell(0, 6, self.sanitize_text(terms))
        self.ln(10)
        
        # Payment Link Button
        link = self.data.get('payment_link')
        if link:
            self.check_page_break(30)
            self.set_fill_color(*ACCENT_BLUE)
            self.set_text_color(*WHITE)
            self.set_font('Helvetica', 'B', 12)
            # Center button
            self.set_x(65)
            self.cell(80, 14, "PAY DEPOSIT ONLINE", fill=True, align='C', link=link)
            self.set_text_color(*TEXT_DARK)
            self.ln(20)

        # Section 8: Services Agreement (Signatures)
        self.add_page()
        self.chapter_title("Services Agreement")
        agreement_text = SERVICES_AGREEMENT.format(client_company=self.data.get('client_company', 'Client'))
        self.body_text(agreement_text, size=10)
        self.ln(5)
        
        # Agreement Note
        self.draw_callout("By signing below you agree to the service agreement above and terms and conditions below.")
        
        self.check_page_break(60) 
        self.signature_block("Analysis & Agreement")

        # Section 9: Terms and Conditions
        self.ln(10)
        self.check_page_break(50)
        self.chapter_title("Terms and Conditions")
        terms_text = TERMS_AND_CONDITIONS.format(client_company=self.data.get('client_company', 'Client'))
        self.body_text(terms_text, size=9)


    def signature_block(self, title):
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(*NAVY_BLUE)
        self.cell(0, 10, "ACCEPTED AND AGREED:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(5)
        
        col_width = 80
        
        # Save Y position
        start_y = self.get_y()
        
        # Left Column: Sipes
        self.set_text_color(*TEXT_DARK)
        self.set_font('Helvetica', 'B', 10)
        self.cell(col_width, 6, "Sipes Automation", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(15) # Sig space
        
        self.set_draw_color(100, 100, 100)
        sipes_sig_y = self.get_y()
        self.line(self.get_x(), sipes_sig_y, self.get_x() + col_width, sipes_sig_y)
        self.ln(2)
        
        self.set_font('Helvetica', '', 9)
        self.cell(col_width, 5, "Michael Sipes, Owner", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        self.ln(5)
        sipes_date_y = self.get_y()
        self.line(self.get_x(), sipes_date_y, self.get_x() + col_width, sipes_date_y)
        self.ln(6)
        self.cell(col_width, 5, "Date", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        # Right Column: Client
        # Reset Y to top of block, move X over
        self.set_y(start_y)
        self.set_x(110) # Offset
        
        self.set_font('Helvetica', 'B', 10)
        self.cell(col_width, 6, self.data.get('client_company', 'Client Company'), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        # We need to manually manage X for the subsequent lines because cell() with new_x=LMARGIN resets to left margin
        # So we use set_x(110) for each line
        
        self.ln(15) # Sig space
        self.set_x(110)
        sig_line_y = self.get_y() # Capture Y for Sig
        self.line(110, sig_line_y, 110 + col_width, sig_line_y)
        
        self.ln(2)
        self.set_x(110)
        self.set_font('Helvetica', '', 9)
        self.cell(col_width, 5, f"Name: {self.data.get('client_name', '')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        self.ln(5)
        self.set_x(110)
        date_line_y = self.get_y() # Capture Y for Date
        self.line(110, date_line_y, 110 + col_width, date_line_y)
        self.ln(1)
        self.set_x(110)
        self.cell(col_width, 5, "Date", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        # Save Metadata for DocuSeal
        metadata = {
            "page": self.page_no(),
            "client_sig_y": sig_line_y,
            "client_date_y": date_line_y,
            "client_col_x": 110,
            "sipes_sig_y": sipes_sig_y,
            "sipes_date_y": sipes_date_y,
            "sipes_col_x": 10,  # Left Margin
            "col_width": col_width
        }
        with open(".tmp/pdf_metadata.json", "w") as f:
            json.dump(metadata, f)

        # Reset X
        self.set_x(10)


def generate_proposal(data_file_path):
    with open(data_file_path, 'r') as f:
        data = json.load(f)

    # Determine Output Filename
    # Format: [J-Number]_[ClientName]_Proposal_Rev[Rev].pdf
    j_num = data.get('j_number', 'J00000')
    rev = data.get('revision', 1)
    
    # Clean client name
    client_safe = "".join([c for c in data.get('client_name', 'Client') if c.isalpha() or c.isdigit() or c==' ']).strip().replace(' ', '_')
    
    filename = f"{j_num}_{client_safe}_Proposal_Rev{rev}.pdf"
    output_path = os.path.join('.tmp', filename)
    
    pdf = ProposalPDF(data)
    pdf.generate()
    pdf.output(output_path)
    print(f"Proposal generated: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, help="Path to JSON data file")
    args = parser.parse_args()
    
    generate_proposal(args.data)
