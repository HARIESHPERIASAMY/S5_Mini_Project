import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, hex_color):
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shd)

def set_cell_margins(cell, top=60, bottom=60, left=100, right=100):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>\n'
        f'  <w:top w:w="{top}" w:type="dxa"/>\n'
        f'  <w:bottom w:w="{bottom}" w:type="dxa"/>\n'
        f'  <w:left w:w="{left}" w:type="dxa"/>\n'
        f'  <w:right w:w="{right}" w:type="dxa"/>\n'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def set_table_borders(table, color="000000"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>\n'
        f'  <w:top w:val="single" w:sz="8" w:space="0" w:color="{color}"/>\n'
        f'  <w:bottom w:val="single" w:sz="8" w:space="0" w:color="{color}"/>\n'
        f'  <w:left w:val="none"/>\n'
        f'  <w:right w:val="none"/>\n'
        f'  <w:insideH w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>\n'
        f'  <w:insideV w:val="none"/>\n'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def add_footer_page_number(footer_p):
    footer_p.text = ""
    footer_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = footer_p.add_run()
    run.font.name = 'Times New Roman'
    run.font.size = Pt(11)
    fld1 = parse_xml(r'<w:fldChar %s w:fldCharType="begin"/>' % nsdecls('w'))
    instr = parse_xml(r'<w:instrText %s xml:space="preserve"> PAGE </w:instrText>' % nsdecls('w'))
    fld2 = parse_xml(r'<w:fldChar %s w:fldCharType="separate"/>' % nsdecls('w'))
    fld3 = parse_xml(r'<w:fldChar %s w:fldCharType="end"/>' % nsdecls('w'))
    run._r.append(fld1)
    run._r.append(instr)
    run._r.append(fld2)
    run._r.append(fld3)

def build_report():
    doc = Document()

    # -------------------------------------------------------------------------
    # SECTION 1: PRELIMS (Roman numerals i to x)
    # -------------------------------------------------------------------------
    sec1 = doc.sections[0]
    sec1.page_width = Inches(8.5)
    sec1.page_height = Inches(11.0)
    sec1.left_margin = Inches(1.0)
    sec1.right_margin = Inches(1.0)
    sec1.top_margin = Inches(1.0)
    sec1.bottom_margin = Inches(1.0)
    sec1.different_first_page_header_footer = False

    pgNumType1 = OxmlElement('w:pgNumType')
    pgNumType1.set(qn('w:fmt'), 'lowerRoman')
    pgNumType1.set(qn('w:start'), '1')
    sec1._sectPr.append(pgNumType1)

    add_footer_page_number(sec1.footer.paragraphs[0])

    # Styling helpers
    def add_p(text, bold=False, italic=False, size=12, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=4, line_spacing=1.35, indent=0.0):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = line_spacing
        if indent > 0:
            p.paragraph_format.first_line_indent = Inches(indent)
        run = p.add_run(text)
        run.bold = bold
        run.italic = italic
        run.font.name = 'Times New Roman'
        run.font.size = Pt(size)
        return p

    def add_chap_title(chap_num, title):
        p1 = doc.add_paragraph()
        p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p1.paragraph_format.space_before = Pt(8)
        p1.paragraph_format.space_after = Pt(2)
        r1 = p1.add_run(f"CHAPTER {chap_num}")
        r1.bold = True
        r1.font.name = 'Times New Roman'
        r1.font.size = Pt(14)

        p2 = doc.add_paragraph()
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p2.paragraph_format.space_before = Pt(0)
        p2.paragraph_format.space_after = Pt(10)
        r2 = p2.add_run(title.upper())
        r2.bold = True
        r2.font.name = 'Times New Roman'
        r2.font.size = Pt(14)

    def add_sec_title(title):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
        run = p.add_run(title.upper())
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        return p

    def add_fig(img_path, caption, width=Inches(5.2)):
        if os.path.exists(img_path):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(2)
            p.add_run().add_picture(img_path, width=width)

            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_before = Pt(2)
            p_cap.paragraph_format.space_after = Pt(6)
            r = p_cap.add_run(caption)
            r.bold = True
            r.font.name = 'Times New Roman'
            r.font.size = Pt(10.5)

    # -------------------------------------------------------------------------
    # PRELIM PAGE 1 (i): TITLE PAGE
    # -------------------------------------------------------------------------
    add_p("INTELLIGENT MULTI-AGENT FRAMEWORK FOR ACADEMIC SOFTWARE TESTING AND BUG ANALYSIS (SENTINELMESH)",
          bold=True, size=14, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=14, line_spacing=1.3)
    add_p("PROJECT REPORT", bold=True, size=13, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=6)
    add_p("Submitted by", italic=True, size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=6)
    add_p("HARIESH P (7376241CS195)", bold=True, size=13, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=2)
    add_p("MIDHUN M (7376242AL152)", bold=True, size=13, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=12)
    add_p("In partial fulfilment for the award of the degree of", italic=True, size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=2)
    add_p("BACHELOR OF ENGINEERING", bold=True, size=13, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=2)
    add_p("in", italic=True, size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=2)
    add_p("COMPUTER SCIENCE AND ENGINEERING", bold=True, size=13, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=14)

    logo_path = os.path.join("output", "bit_logo.png")
    if os.path.exists(logo_path):
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_before = Pt(2)
        p_logo.paragraph_format.space_after = Pt(6)
        p_logo.add_run().add_picture(logo_path, width=Inches(1.2))

    add_p("BANNARI AMMAN INSTITUTE OF TECHNOLOGY", bold=True, size=13, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=1)
    add_p("(An Autonomous Institution Affiliated to Anna University, Chennai)", size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=1)
    add_p("SATHYAMANGALAM - 638 401", bold=True, size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=4)
    add_p("ANNA UNIVERSITY: CHENNAI 600 025", bold=True, size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=4)
    add_p("OCTOBER 2026", bold=True, size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=0)

    doc.add_page_break()

    # -------------------------------------------------------------------------
    # PRELIM PAGE 2 (ii): BONAFIDE CERTIFICATE
    # -------------------------------------------------------------------------
    add_p("BONAFIDE CERTIFICATE", bold=True, size=14, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=16, space_after=16)
    add_p("Certified that this project report titled “NEP Aligned Standardized Academic Credit Accumulation Hub with Cross-Institutional Authentication API Gateways” is the bonafide work of “ HARIESH P (7376241CS195), MIDHUN M (7376242AL152) ” who carried out the project work under my supervision.",
          size=12, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=8, space_after=20, line_spacing=1.35)

    t_sig = doc.add_table(rows=1, cols=2)
    t_sig.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_sig.columns[0].width = Inches(3.2)
    t_sig.columns[1].width = Inches(3.2)
    p_left = t_sig.cell(0, 0).paragraphs[0]
    p_left.paragraph_format.line_spacing = 1.15
    p_left.add_run("Dr. Ramya R\n").bold = True
    p_left.add_run("SUPERVISOR\n").bold = True
    p_left.add_run("Associate Professor\nDepartment of Computer Science\nand Engineering\nBannari Amman Institute of\nTechnology,\nSathyamangalam – 638401")

    p_right = t_sig.cell(0, 1).paragraphs[0]
    p_right.paragraph_format.line_spacing = 1.15
    p_right.add_run("Dr. Sasikala D\n").bold = True
    p_right.add_run("HEAD OF THE DEPARTMENT\n").bold = True
    p_right.add_run("Professor and Head\nDepartment of Computer Science\nand Engineering\nBannari Amman Institute of\nTechnology,\nSathyamangalam – 638401")

    add_p("", space_before=30, space_after=10)
    add_p("Submitted for the Project Viva Voce examination held on ……………………", size=12, space_before=14, space_after=32)

    t_exam = doc.add_table(rows=1, cols=2)
    t_exam.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_exam.columns[0].width = Inches(3.2)
    t_exam.columns[1].width = Inches(3.2)
    t_exam.cell(0, 0).paragraphs[0].add_run("INTERNAL EXAMINER").bold = True
    t_exam.cell(0, 1).paragraphs[0].add_run("EXTERNAL EXAMINER").bold = True
    t_exam.cell(0, 1).paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    doc.add_page_break()

    # -------------------------------------------------------------------------
    # PRELIM PAGE 3 (iii): DECLARATION
    # -------------------------------------------------------------------------
    add_p("DECLARATION", bold=True, size=14, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=16, space_after=16)
    add_p("We affirm that the project work titled “NEP Aligned Standardized Academic Credit Accumulation Hub with Cross-Institutional Authentication API Gateways”, submitted in partial fulfilment for the award of the degree of Bachelor of Engineering in Computer Science and Engineering is the record of work carried out by us under the guidance of RAMYA R, Associate Professor, Department of Computer Science and Engineering, Bannari Amman Institute of Technology. It has not formed part of any other project work submitted for the award of any degree or diploma at this or any other university.",
          size=12, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=8, space_after=28, line_spacing=1.35)

    t_dec = doc.add_table(rows=1, cols=2)
    t_dec.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_dec.columns[0].width = Inches(3.2)
    t_dec.columns[1].width = Inches(3.2)
    t_dec.cell(0, 0).paragraphs[0].add_run("HARIESH P\n(7376241CS195)").bold = True
    t_dec.cell(0, 1).paragraphs[0].add_run("MIDHUN M\n(7376242AL152)").bold = True
    t_dec.cell(0, 1).paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    add_p("", space_before=30, space_after=10)
    add_p("I certify that the declaration made above by the candidates is true.", size=12, space_before=16, space_after=30)

    p_sup = doc.add_paragraph()
    p_sup.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_sup.paragraph_format.line_spacing = 1.15
    p_sup.add_run("Dr. RAMYA R\n").bold = True
    p_sup.add_run("ASSOCIATE PROFESSOR").bold = True

    doc.add_page_break()

    # -------------------------------------------------------------------------
    # PRELIM PAGE 4 (iv): ACKNOWLEDGEMENT
    # -------------------------------------------------------------------------
    add_p("ACKNOWLEDGEMENT", bold=True, size=14, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=16, space_after=16)
    add_p("We would like to enunciate heartfelt thanks to our esteemed Chairman Dr. S.V. Balasubramaniam, and the respected Principal Dr. C. Palanisamy, for providing excellent facilities and support during the course of study in this institute.",
          size=12, space_before=8, space_after=12, indent=0.4, line_spacing=1.35)
    add_p("We are grateful to Dr. Sasikala D, Head of the Department, Department of Computer Science and Engineering, for her valuable suggestions to carry out the project work successfully.",
          size=12, space_before=4, space_after=12, indent=0.4, line_spacing=1.35)
    add_p("We wish to express our sincere thanks to Faculty Guide Dr. Ramya R, Associate Professor, Department of Computer Science and Engineering, for her constructive ideas, inspirations, encouragement, excellent guidance, and much needed technical support extended to complete our project work.",
          size=12, space_before=4, space_after=12, indent=0.4, line_spacing=1.35)
    add_p("We would like to thank our friends, faculty and non-teaching staff who have directly and indirectly contributed to the success of this project.",
          size=12, space_before=4, space_after=30, indent=0.4, line_spacing=1.35)

    p_ack_names = doc.add_paragraph()
    p_ack_names.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_ack_names.paragraph_format.line_spacing = 1.15
    p_ack_names.add_run("HARIESH P\n(7376241CS195)\n").bold = True
    p_ack_names.add_run("MIDHUN M\n(7376242AL152)").bold = True

    doc.add_page_break()

    # -------------------------------------------------------------------------
    # PRELIM PAGE 5 (v): ABSTRACT
    # -------------------------------------------------------------------------
    add_p("ABSTRACT", bold=True, size=14, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=16, space_after=16)
    add_p("The project “NEP Aligned Standardized Academic Credit Accumulation Hub with Cross-Institutional Authentication API Gateways” aims to develop an autonomous quality and credit verification platform for tracking, evaluating, and managing software and academic credits across institutions. The system supports three user roles: Student, Institution, and Admin. Students can monitor accumulated credits, test coverage, and academic progress, institutions manage student and credit records and evaluate transfer requests, and administrators oversee users, institutions, and system activities. The platform is developed using Python, FastAPI, SQLite with Write-Ahead Logging, React 19, and Vite. RESTful APIs and authenticated API gateways enable secure communication between institutions, while JWT authentication, role-based access control, deterministic Abstract Syntax Tree (AST) validation, and sandboxed subprocess execution protect information integrity. The proposed system aims to simplify credit management and transfers, improve transparency, reduce administrative workload, and promote flexible academic mobility through a secure, standardized, and self-healing platform.",
          size=12, space_before=8, space_after=12, indent=0.4, line_spacing=1.4)

    doc.add_page_break()

    # -------------------------------------------------------------------------
    # PRELIM PAGES 6, 7, 8 (vi, vii, viii): TABLE OF CONTENTS
    # -------------------------------------------------------------------------
    add_p("TABLE OF CONTENTS", bold=True, size=14, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=16, space_after=12)

    # Helper for TOC table
    def create_toc_table(items, is_first=False):
        t = doc.add_table(rows=0, cols=3)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        t.columns[0].width = Inches(1.2)
        t.columns[1].width = Inches(4.4)
        t.columns[2].width = Inches(0.9)
        if is_first:
            row = t.add_row()
            h = row.cells
            set_cell_margins(h[0], 10, 10, 20, 20)
            set_cell_margins(h[1], 10, 10, 20, 20)
            set_cell_margins(h[2], 10, 10, 20, 20)
            r0 = h[0].paragraphs[0].add_run("CHAPTER NO.")
            r0.bold = True
            r0.font.name = 'Times New Roman'
            r0.font.size = Pt(11)
            r1 = h[1].paragraphs[0].add_run("TITLE")
            r1.bold = True
            r1.font.name = 'Times New Roman'
            r1.font.size = Pt(11)
            r2 = h[2].paragraphs[0].add_run("PAGE NO.")
            r2.bold = True
            r2.font.name = 'Times New Roman'
            r2.font.size = Pt(11)
            h[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
        for c_no, tit, p_no, is_b in items:
            row = t.add_row()
            c = row.cells
            set_cell_margins(c[0], 4, 4, 15, 15)
            set_cell_margins(c[1], 4, 4, 15, 15)
            set_cell_margins(c[2], 4, 4, 15, 15)
            p0 = c[0].paragraphs[0]
            p0.paragraph_format.line_spacing = 1.0
            p0.paragraph_format.space_before = Pt(0)
            p0.paragraph_format.space_after = Pt(1)
            r0 = p0.add_run(c_no)
            r0.font.name = 'Times New Roman'
            r0.font.size = Pt(10.5)

            p1 = c[1].paragraphs[0]
            p1.paragraph_format.line_spacing = 1.0
            p1.paragraph_format.space_before = Pt(0)
            p1.paragraph_format.space_after = Pt(1)
            r1 = p1.add_run(tit)
            r1.font.name = 'Times New Roman'
            r1.font.size = Pt(10.5)

            p2 = c[2].paragraphs[0]
            p2.paragraph_format.line_spacing = 1.0
            p2.paragraph_format.space_before = Pt(0)
            p2.paragraph_format.space_after = Pt(1)
            p2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            r2 = p2.add_run(p_no)
            r2.font.name = 'Times New Roman'
            r2.font.size = Pt(10.5)

            if is_b:
                r0.bold = True
                r1.bold = True
                r2.bold = True
        return t

    toc_p1 = [
        ("1", "INTRODUCTION", "1", True),
        ("1.1", "BACKGROUND", "1", False),
        ("1.2", "PROJECT OVERVIEW", "1", False),
        ("1.3", "NEED FOR THE SYSTEM", "2", False),
        ("1.4", "PROBLEM IDENTIFICATION", "2", False),
        ("1.5", "OBJECTIVES", "3", False),
        ("1.6", "SCOPE OF THE PROJECT", "3", False),
        ("1.7", "EXPECTED OUTCOME", "3", False),
        ("1.8", "USERS AND THEIR NEEDS", "4", False),
        ("1.9", "REPORT ORGANIZATION", "4", False),
        ("1.10", "CHAPTER SUMMARY", "5", False),
        ("2", "LITERATURE SURVEY", "6", True),
        ("3", "METHODOLOGY", "9", True),
        ("3.1", "CHAPTER OVERVIEW", "9", False),
        ("3.2", "SYSTEM ARCHITECTURE", "9", False),
        ("3.3", "DEVELOPMENT TECHNOLOGIES", "10", False),
        ("3.4", "USER ROLES AND ACCESS RESPONSIBILITIES", "11", False),
        ("3.5", "DATABASE DESIGN", "12", False),
        ("3.6", "DATA RELATIONSHIP AND INTEGRITY", "13", False),
        ("3.7", "AUTHENTICATION WORKFLOW", "13", False),
        ("3.8", "AUTHORIZATION AND ROUTE PROTECTION", "14", False),
        ("3.9", "REST API DESIGN", "15", False)
    ]
    create_toc_table(toc_p1, is_first=True)
    doc.add_page_break()

    toc_p2 = [
        ("3.10", "ACADEMIC CREDIT VALIDATION", "15", False),
        ("3.11", "RESULTS IMPORT AND BATCH PROCESSING", "16", False),
        ("3.12", "SEMESTER PROGRESSION AND CORRECTION", "17", False),
        ("3.13", "TRANSFER REQUEST WORKFLOW", "18", False),
        ("3.14", "CERTIFICATE, TRANSCRIPT AND API KEY HANDLING", "18", False),
        ("3.15", "SECURITY CONTROL", "19", False),
        ("3.16", "TESTING METHODOLOGY", "19", False),
        ("3.17", "DEVELOPMENT AND VERIFICATION PROCESS", "20", False),
        ("3.18", "METHODOLOGY SUMMARY", "20", False),
        ("4", "PROPOSED WORK MODULES", "21", True),
        ("4.1", "MODULE OVERVIEW", "21", False),
        ("4.2", "STUDENT DASHBOARD", "21", False),
        ("4.3", "STUDENT CREDIT AND ELIGIBILITY FEATURES", "22", False),
        ("4.4", "INSTITUTIONAL DASHBOARD", "23", False),
        ("4.5", "ADMINISTRATOR DASHBOARD", "24", False),
        ("4.6", "API GATEWAY AND CROSS-INSTITUTIONAL ACCESS", "25", False),
        ("4.7", "CERTIFICATE AND TRANSCRIPT VERIFICATION", "26", False),
        ("4.8", "AUDIT LOGS AND POLICY HISTORY", "27", False),
        ("4.9", "MODULE INTERACTION", "28", False),
        ("4.10", "MODULE SUMMARY", "28", False)
    ]
    create_toc_table(toc_p2, is_first=False)
    doc.add_page_break()

    toc_p3 = [
        ("5", "RESULTS AND DISCUSSION", "29", True),
        ("5.1", "IMPLEMENTATION OVERVIEW", "29", False),
        ("5.2", "FRONTEND AND BACKEND VERIFICATION", "29", False),
        ("5.3", "TEST RESULTS", "30", False),
        ("5.4", "FUNCTIONAL WORKFLOW DISCUSSION", "30", False),
        ("5.5", "USER INTERFACE EVIDENCE", "31", False),
        ("5.6", "SECURITY AND RELIABILITY DISCUSSION", "31", False),
        ("5.7", "LIMITATIONS", "31", False),
        ("5.8", "RESULTS SUMMARY", "32", False),
        ("6", "CONCLUSIONS AND SUGGESTIONS FOR FUTURE WORK", "33", True),
        ("6.1", "CONCLUSION", "33", False),
        ("6.2", "SUGGESTIONS FOR FUTURE WORK", "33", False),
        ("6.3", "FINAL REMARK", "34", False),
        ("7", "REFERENCES", "35", True),
        ("8", "INDIVIDUAL CONTRIBUTION", "36", True),
        ("9", "PLAGIARISM REPORT", "39", True),
        ("10", "PROJECT OUTCOME", "40", True)
    ]
    create_toc_table(toc_p3, is_first=False)
    doc.add_page_break()

    # -------------------------------------------------------------------------
    # PRELIM PAGE 9 (ix): LIST OF TABLES
    # -------------------------------------------------------------------------
    add_p("LIST OF TABLES", bold=True, size=14, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=16, space_after=14)
    t_lot = doc.add_table(rows=1, cols=3)
    t_lot.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_lot.columns[0].width = Inches(1.5)
    t_lot.columns[1].width = Inches(4.1)
    t_lot.columns[2].width = Inches(0.9)
    h_lot = t_lot.rows[0].cells
    h_lot[0].paragraphs[0].add_run("TABLE NO.").bold = True
    h_lot[1].paragraphs[0].add_run("TABLE NAME").bold = True
    h_lot[2].paragraphs[0].add_run("PAGE NO.").bold = True
    h_lot[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    tables_list = [
        ("2.1", "COMPARISON FRAMEWORK", "8"),
        ("3.1", "TECHNOLOGY STACK USED IN THE PROJECT", "11"),
        ("3.2", "USER ROLES AND ACCESS RESPONSIBILITIES", "11"),
        ("3.3", "DATABASE DESIGN", "12"),
        ("5.1", "REPORTED TESTING SUMMARY", "30")
    ]
    for t_no, t_name, p_no in tables_list:
        row = t_lot.add_row()
        cells = row.cells
        set_cell_margins(cells[0], 25, 25, 40, 40)
        set_cell_margins(cells[1], 25, 25, 40, 40)
        set_cell_margins(cells[2], 25, 25, 40, 40)
        cells[0].paragraphs[0].add_run(t_no)
        cells[1].paragraphs[0].add_run(t_name)
        cells[2].paragraphs[0].add_run(p_no)
        cells[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    doc.add_page_break()

    # -------------------------------------------------------------------------
    # PRELIM PAGE 10 (x): LIST OF FIGURES
    # -------------------------------------------------------------------------
    add_p("LIST OF FIGURES", bold=True, size=14, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=16, space_after=14)
    t_lof = doc.add_table(rows=1, cols=3)
    t_lof.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_lof.columns[0].width = Inches(1.5)
    t_lof.columns[1].width = Inches(4.1)
    t_lof.columns[2].width = Inches(0.9)
    h_lof = t_lof.rows[0].cells
    h_lof[0].paragraphs[0].add_run("FIGURE NO.").bold = True
    h_lof[1].paragraphs[0].add_run("FIGURE NAME").bold = True
    h_lof[2].paragraphs[0].add_run("PAGE NO.").bold = True
    h_lof[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    figures_list = [
        ("3.1", "VERIFIED SYSTEM ARCHITECTURE DIAGRAM", "10"),
        ("3.2", "VERIFIED LOGIN AND TOKEN WORKFLOW DIAGRAM", "14"),
        ("3.3", "VERIFIED CREDIT VALIDATION WORKFLOW", "16"),
        ("3.4", "VERIFIED SPREADSHEET IMPORT WORKFLOW", "17"),
        ("3.5", "VERIFIED TRANSFER LIFECYCLE DIAGRAM", "18"),
        ("4.1", "STUDENT DASHBOARD", "22"),
        ("4.2", "INSTITUTION DASHBOARD", "23"),
        ("4.3", "ADMINISTRATOR DASHBOARD", "24"),
        ("4.4", "CROSS-INSTITUTIONAL API GATEWAY INTEGRATION", "25"),
        ("4.5", "CERTIFICATE VERIFICATION", "26"),
        ("4.6", "AUDIT LOGS AND POLICY HISTORY", "27")
    ]
    for f_no, f_name, p_no in figures_list:
        row = t_lof.add_row()
        cells = row.cells
        set_cell_margins(cells[0], 20, 20, 40, 40)
        set_cell_margins(cells[1], 20, 20, 40, 40)
        set_cell_margins(cells[2], 20, 20, 40, 40)
        cells[0].paragraphs[0].add_run(f_no)
        cells[1].paragraphs[0].add_run(f_name)
        cells[2].paragraphs[0].add_run(p_no)
        cells[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # -------------------------------------------------------------------------
    # SECTION 2: BODY CHAPTERS 1 TO 10 (Arabic numbers 1 to 40)
    # -------------------------------------------------------------------------
    sec2 = doc.add_section()
    sec2.page_width = Inches(8.5)
    sec2.page_height = Inches(11.0)
    sec2.left_margin = Inches(1.0)
    sec2.right_margin = Inches(1.0)
    sec2.top_margin = Inches(1.0)
    sec2.bottom_margin = Inches(1.0)
    sec2.different_first_page_header_footer = False
    sec2.header.is_linked_to_previous = False
    sec2.footer.is_linked_to_previous = False

    pgNumType2 = OxmlElement('w:pgNumType')
    pgNumType2.set(qn('w:fmt'), 'decimal')
    pgNumType2.set(qn('w:start'), '1')
    sec2._sectPr.append(pgNumType2)

    add_footer_page_number(sec2.footer.paragraphs[0])

    # =========================================================================
    # BODY PAGE 1: CHAPTER 1 (1.1, 1.2)
    # =========================================================================
    add_chap_title("1", "INTRODUCTION")
    add_sec_title("1.1 BACKGROUND")
    add_p("Academic programmes increasingly combine learning from different courses, departments, institutions, and online learning environments. A student’s academic journey is therefore not always represented by a single course list or one semester result sheet. Credits provide a structured way to describe learning completed, but the records still need to be maintained accurately and interpreted in context.",
          indent=0.4, space_after=6)
    add_p("When credit records are spread across multiple systems, students may have to consult different portals or contact offices to understand their overall progress. Institutions may need to verify previous courses, grades, or credit values before they can consider a transfer or an academic pathway. These tasks can become slow when the available information is incomplete or formatted differently.",
          indent=0.4, space_after=6)
    add_p("The proposed Academic Credit Accumulation Hub is intended to provide one web-based location where authorized users can work with academic credit information. It does not replace institutional academic rules. Instead, it provides software workflows for recording, viewing, validating, and verifying information according to configured roles and policies.",
          indent=0.4, space_after=6)
    add_sec_title("1.2 PROJECT OVERVIEW")
    add_p("The application has three main user roles. Students use a personal dashboard to review accumulated credits and related academic information. Institution users manage institution-scoped data such as students, courses, credit records, and transfer requests. Administrators have a broader view of platform activity and can review system-level records, verification queues, analytics, and audit information.",
          indent=0.4, space_after=6)
    add_p("The project is built using Python, FastAPI, SQLite with Write-Ahead Logging, React 19, and Vite. The frontend communicates with the backend via REST endpoints and WebSockets. Authentication and authorization controls are applied to protected requests so that each role can access only the functions permitted to it.",
          indent=0.4, space_after=6)

    doc.add_page_break()

    # =========================================================================
    # BODY PAGE 2: CHAPTER 1 (1.3, 1.4)
    # =========================================================================
    add_sec_title("1.3 NEED FOR THE SYSTEM")
    add_p("A student-facing consolidated view can reduce the effort required to understand credit progress. For institutions, validation steps can reduce avoidable data-entry errors and make it easier to review a record before it becomes part of a student’s credit history. For administrators, system-wide monitoring and audit information can help identify activity that needs attention.",
          indent=0.4, space_after=6)
    add_p("The need for such a system is not only a matter of convenience. Academic records can influence eligibility, progression, and transfer decisions. As a result, the system must treat accuracy, access control, traceability, and clear handling of incomplete information as core design concerns.",
          indent=0.4, space_after=8)
    add_sec_title("1.4 PROBLEM IDENTIFICATION")
    add_p("The central problem addressed by this project is the difficulty of maintaining a consistent, consolidated view of academic credits when information is managed across separate institutional contexts. Data may be entered in different formats, the status of a record may not be obvious, and verification can require manual communication. Students may not have an easy way to view how credits accumulate over time.",
          indent=0.4, space_after=6)
    add_p("A second issue is that different users need different levels of access. Students should be able to see their own records, institution users should manage records within their authorized scope, and administrators should have controlled oversight. If permissions are not clearly enforced, confidential academic information could be exposed or modified by the wrong user.",
          indent=0.4, space_after=6)
    add_p("A third issue is the need to explain how a credit record was created or changed. If corrections and transfer decisions are not traceable, reviewing a disputed record becomes difficult. The application therefore includes validation and audit-oriented workflows where supported by the implementation.",
          indent=0.4, space_after=6)

    doc.add_page_break()

    # =========================================================================
    # BODY PAGE 3: CHAPTER 1 (1.5, 1.6, 1.7)
    # =========================================================================
    add_sec_title("1.5 OBJECTIVES")
    add_p("The primary objective is to develop a web-based platform that organizes academic credit records and supports secure, role-based access across student, institution, and administrator functions.",
          indent=0.4, space_after=6)
    add_p("The supporting objectives are to provide a student credit wallet and semester timeline; support institution-side management and validation of student, course, and credit information; provide a controlled workflow for credit transfer requests; expose selected verification and API functions; and maintain records that help authorized users review system activity.",
          indent=0.4, space_after=8)
    add_sec_title("1.6 SCOPE OF THE PROJECT")
    add_p("The scope of the prototype includes account registration and login, role-specific dashboards, academic record management, credit validation, selected transfer workflows, certificate and transcript verification routes, API key management, and audit-related information. The exact set of available actions depends on the role and the implementation currently present in the codebase.",
          indent=0.4, space_after=6)
    add_p("The project is not, by itself, proof of official integration with every university or with a national academic credit infrastructure. External integrations, formal institutional approvals, production deployment, and compliance certification should only be claimed if separate evidence is available. The report therefore describes the software prototype and its verified behavior rather than assuming national-level operational adoption.",
          indent=0.4, space_after=8)
    add_sec_title("1.7 EXPECTED OUTCOME")
    add_p("The expected outcome is a working prototype that demonstrates how academic credit information can be organized through one application with clear role boundaries. Students should be able to review their progress, institution users should be able to perform approved record-management tasks, and administrators should be able to review relevant platform activity.",
          indent=0.4, space_after=6)

    doc.add_page_break()

    # =========================================================================
    # BODY PAGE 4: CHAPTER 1 (1.7 cont, 1.8, 1.9)
    # =========================================================================
    add_p("The project also provides an opportunity to apply full-stack development concepts in a practical context: designing data models, implementing REST endpoints, handling authentication, validating input, building dashboards, and testing role-specific workflows. The value of the project should be demonstrated through screenshots, API evidence, and reproducible tests.",
          indent=0.4, space_after=8)
    add_sec_title("1.8 USERS AND THEIR NEEDS")
    add_p("Students need a clear summary rather than a collection of disconnected records. A wallet-style view can show total credits and their status, while a semester timeline can help students understand when credits were earned. Eligibility and pathway screens can help explain progress, provided that the displayed thresholds and policies are clearly identified and kept up to date.",
          indent=0.4, space_after=6)
    add_p("Institution users need reliable forms and workflows for managing students, courses, credit submissions, and transfer requests. Validation should identify missing or invalid data before it is accepted. When a correction is necessary, the system should capture the reason and preserve enough history to make the change understandable.",
          indent=0.4, space_after=6)
    add_p("Administrators need visibility into institution verification, system activity, API usage, audit entries, and summary analytics. Their broad access should be controlled and monitored because administrative actions can affect many users. These user needs guide the separation of dashboards and backend permissions.",
          indent=0.4, space_after=8)
    add_sec_title("1.9 REPORT ORGANIZATION")
    add_p("Chapter 1 introduces the problem, objectives, scope, and expected outcome. Chapter 2 reviews related work and identifies the research gap. Chapter 3 explains the objectives and methodology, including architecture, technologies, data design, security, and testing approach. Chapter 4 describes the proposed work modules and their workflows. Chapter 5 presents implementation evidence, test results, and discussion of limitations. Chapter 6 concludes the report and lists possible future improvements.",
          indent=0.4, space_after=6)

    doc.add_page_break()

    # =========================================================================
    # BODY PAGE 5: CHAPTER 1 (1.10)
    # =========================================================================
    add_sec_title("1.10 CHAPTER SUMMARY")
    add_p("This chapter has introduced the motivation for a consolidated academic credit hub and the need for role-based access, validation, and traceability. The project is intended to support students, institutions, and administrators through a shared web application. Its claims must remain aligned with the working implementation and the evidence collected during testing.",
          indent=0.4, space_after=12)

    doc.add_page_break()

    # =========================================================================
    # BODY PAGE 6: CHAPTER 2 (LITERATURE SURVEY)
    # =========================================================================
    add_chap_title("2", "LITERATURE SURVEY")
    add_p("A literature survey helps establish existing approaches, technologies, and research gaps related to academic credit management and cross-institutional information exchange. The University Grants Commission’s Academic Bank of Credits (ABC) framework provides a relevant foundation for understanding academic credit accumulation and transfer between institutions [1]. EduCTX explores blockchain-based management and exchange of higher-education credits, offering a useful reference for decentralized academic credit systems [2]. W3C Verifiable Credentials provides standards for issuing and verifying digital credentials securely [3].",
          indent=0.4, space_after=6)
    add_p("Academic credit management systems must maintain accurate records of learners, courses, grades, credits, and academic periods. These records should provide sufficient context for other institutions to evaluate transferred credits correctly. Existing approaches highlight the importance of standardization, record integrity, and interoperability when managing academic information across institutional boundaries [1] [2].",
          indent=0.4, space_after=6)
    add_p("Digital credential technologies support the secure issuance, presentation, and verification of certificates and transcripts. W3C Verifiable Credentials defines a standard model for representing digital credentials and verifying claims made by their issuers [3]. Such approaches can help academic institutions verify credential authenticity and reduce the risk of unauthorized modification or fraudulent academic records.",
          indent=0.4, space_after=6)
    add_p("Authentication and authorization are essential for protecting academic information in a centralized credit management platform. JSON Web Token (JWT) provides a compact mechanism for representing claims between parties and can support token-based authentication in web applications [4]. React provides a framework for developing interactive user interfaces, while Node.js supports server-side JavaScript execution [5] [6].",
          indent=0.4, space_after=6)

    doc.add_page_break()

    # =========================================================================
    # BODY PAGE 7: CHAPTER 2 (cont)
    # =========================================================================
    add_p("Express provides routing and middleware capabilities for developing backend APIs and implementing request-level access controls [7]. MongoDB provides document-oriented data storage suitable for managing structured academic records and related information [8]. Mongoose provides an object data modeling layer for MongoDB in Node.js applications, supporting schema definitions, validation, and database operations [9]. Together, these technologies can support the development of a web-based academic credit management platform.",
          indent=0.4, space_after=6)
    add_p("Interoperability between institutions requires standardized data exchange, secure API communication, and clearly defined access permissions. Although APIs enable systems to exchange information, successful integration also depends on compatible data formats, reliable source records, and institution-specific authorization rules [2] [3] [7]. A centralized platform must additionally maintain availability, protect sensitive information, and preserve the ownership and traceability of academic records.",
          indent=0.4, space_after=6)
    add_p("The reviewed concepts indicate that academic credit management involves more than storing credit values. A practical system must combine accurate academic records, credential verification, secure authentication, role-based access control, and reliable data exchange. Based on these requirements, the proposed project integrates student credit tracking, institutional record management, administrative monitoring, and authenticated API gateways within a unified web application [1] [9].",
          indent=0.4, space_after=6)
    add_p("The intended contribution of the project is to bring these functions together in a standardized platform that supports academic credit accumulation and transfer. The system uses React, Node.js, Express, and MongoDB, with JWT-based authentication and validation mechanisms to protect academic information. Its effectiveness will depend on implementation and testing; integration with external institutions and compliance with applicable academic policies must be verified before claiming full interoperability.",
          indent=0.4, space_after=6)

    doc.add_page_break()

    # =========================================================================
    # BODY PAGE 8: CHAPTER 2 (Table 2.1)
    # =========================================================================
    add_p("In summary, the literature survey establishes the technical and conceptual foundations for the proposed academic credit hub. The reviewed standards, systems, and technologies provide guidance for designing a secure, maintainable, and interoperable application. The following chapter describes the system architecture, selected technologies, implementation approach, security mechanisms, and testing methods used to achieve the project objectives.",
          indent=0.4, space_after=10)

    add_p("Table 2.1 Comparison Framework", bold=True, size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=4)
    t_c21 = doc.add_table(rows=1, cols=2)
    t_c21.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_c21.columns[0].width = Inches(2.2)
    t_c21.columns[1].width = Inches(4.3)
    set_table_borders(t_c21)
    h_c21 = t_c21.rows[0].cells
    set_cell_background(h_c21[0], "F1F5F9")
    set_cell_background(h_c21[1], "F1F5F9")
    h_c21[0].paragraphs[0].add_run("AREA").bold = True
    h_c21[1].paragraphs[0].add_run("QUESTIONS TO ASK OF EACH SOURCE").bold = True

    c21_rows = [
        ("Credit records\n[1], [2]", "How are credits, grades, courses, and academic periods represented?"),
        ("Identity\n[4]", "How is the learner identified and how is identity checked?"),
        ("Interoperability\n[2], [3]", "Does the system exchange records across institutional boundaries?"),
        ("Verification\n[3]", "How can a third party check a certificate or transcript?"),
        ("Security\n[4], [7]", "What authentication, authorization, and audit controls are used?"),
        ("Limitations", "What is not covered, tested, or supported by the study?")
    ]
    for ar, qu in c21_rows:
        r = t_c21.add_row()
        cells = r.cells
        set_cell_margins(cells[0], 25, 25, 40, 40)
        set_cell_margins(cells[1], 25, 25, 40, 40)
        cells[0].paragraphs[0].add_run(ar).bold = True
        cells[1].paragraphs[0].add_run(qu)

    doc.add_page_break()

    # =========================================================================
    # BODY PAGE 9: CHAPTER 3 (3.1, 3.2)
    # =========================================================================
    add_chap_title("3", "METHODOLOGY")
    add_sec_title("3.1 CHAPTER OVERVIEW")
    add_p("This chapter explains the development approach used to organize the project into manageable components. It covers the system architecture, technology choices, user roles, data model, API design, authentication, validation, import workflows, testing, and the boundaries of the current implementation. The description should be compared with the final repository before submission.",
          indent=0.4, space_after=6)
    add_p("A modular structure is useful because the application serves three distinct user groups and handles several types of academic data. Separating the frontend, backend routes, controllers, models, and middleware makes it easier to maintain each responsibility and to test the system in smaller units.",
          indent=0.4, space_after=8)
    add_sec_title("3.2 SYSTEM ARCHITECTURE")
    add_p("The application follows a client–server design. The browser loads the React interface and sends HTTP requests to the Express backend. The backend authenticates requests, checks permissions, validates input, invokes the relevant controller logic, and reads or writes data through Mongoose. MongoDB persists the records.",
          indent=0.4, space_after=6)
    add_p("The frontend should not be treated as the final security boundary. Hiding a button in the interface improves usability, but the backend must still enforce permissions for every protected action. This is particularly important for institution-scoped records and administrator-only operations.",
          indent=0.4, space_after=6)

    doc.add_page_break()

    # =========================================================================
    # BODY PAGE 10: CHAPTER 3 (Figure 3.1 + 3.3)
    # =========================================================================
    add_fig("report_images/fig_3_1_architecture.png", "Figure 3.1 Verified system architecture diagram", width=Inches(5.2))
    add_sec_title("3.3 DEVELOPMENT TECHNOLOGIES")
    add_p("React is used to build reusable interface components and role-specific dashboard pages. Vite supports the frontend development and build process. Tailwind CSS provides utility-based styling, while React Router organizes page navigation. Axios provides a shared HTTP client, including the ability to attach the authentication token to protected requests.",
          indent=0.4, space_after=6)
    add_p("The backend uses Node.js and Express to define REST endpoints and coordinate request processing. Mongoose defines schemas and relationships for MongoDB documents. Supporting packages provide password hashing, JWT handling, request security headers, rate limiting, cross-origin configuration, and selected file-import utilities.",
          indent=0.4, space_after=6)

    doc.add_page_break()

    # =========================================================================
    # BODY PAGE 11: CHAPTER 3 (Table 3.1 + 3.4 + Table 3.2)
    # =========================================================================
    add_p("Table 3.1 Technology Stack Used in the Project", bold=True, size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=2)
    t_31 = doc.add_table(rows=1, cols=3)
    t_31.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_31.columns[0].width = Inches(1.8)
    t_31.columns[1].width = Inches(2.2)
    t_31.columns[2].width = Inches(2.5)
    set_table_borders(t_31)
    h_31 = t_31.rows[0].cells
    set_cell_background(h_31[0], "F1F5F9")
    set_cell_background(h_31[1], "F1F5F9")
    set_cell_background(h_31[2], "F1F5F9")
    h_31[0].paragraphs[0].add_run("LAYER").bold = True
    h_31[1].paragraphs[0].add_run("TECHNOLOGY").bold = True
    h_31[2].paragraphs[0].add_run("PURPOSE").bold = True
    t31_data = [
        ("Frontend", "React, Vite", "User interface and development build"),
        ("Styling", "Tailwind CSS", "Consistent layout and responsive styling"),
        ("Routing", "React Router", "Role-specific page navigation"),
        ("HTTP client", "Axios", "Calls backend endpoints"),
        ("Backend", "Node.js, Express", "REST API and business logic"),
        ("Database", "MongoDB, Mongoose", "Document storage and schema validation"),
        ("Security", "bcryptjs, JWT, Helmet", "Password hashing, tokens, security headers")
    ]
    for la, te, pu in t31_data:
        r = t_31.add_row()
        c = r.cells
        set_cell_margins(c[0], 12, 12, 30, 30)
        set_cell_margins(c[1], 12, 12, 30, 30)
        set_cell_margins(c[2], 12, 12, 30, 30)
        c[0].paragraphs[0].add_run(la).bold = True
        c[1].paragraphs[0].add_run(te)
        c[2].paragraphs[0].add_run(pu)

    add_sec_title("3.4 USER ROLES AND ACCESS RESPONSIBILITIES")
    add_p("The application separates the user experience into Student, Institution, and Admin roles. Each role has a distinct set of responsibilities. The role stored in the authenticated user record is checked by authorization middleware before protected routes are allowed to proceed.",
          indent=0.4, space_after=4)
    add_p("Table 3.2 User Roles and Access Responsibilities", bold=True, size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=2)
    t_32 = doc.add_table(rows=1, cols=3)
    t_32.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_32.columns[0].width = Inches(1.5)
    t_32.columns[1].width = Inches(2.5)
    t_32.columns[2].width = Inches(2.5)
    set_table_borders(t_32)
    h_32 = t_32.rows[0].cells
    set_cell_background(h_32[0], "F1F5F9")
    set_cell_background(h_32[1], "F1F5F9")
    set_cell_background(h_32[2], "F1F5F9")
    h_32[0].paragraphs[0].add_run("ROLE").bold = True
    h_32[1].paragraphs[0].add_run("MAIN RESPONSIBILITIES").bold = True
    h_32[2].paragraphs[0].add_run("EXAMPLE RESTRICTION").bold = True
    t32_data = [
        ("Student", "View personal credit progress and records", "Cannot edit institution-wide records"),
        ("Institution", "Manage permitted institution records and requests", "Must remain within authorized institution scope"),
        ("Admin", "Review platform-level records and oversight functions", "Administrative actions should remain authenticated and auditable")
    ]
    for ro, mr, er in t32_data:
        r = t_32.add_row()
        c = r.cells
        set_cell_margins(c[0], 12, 12, 30, 30)
        set_cell_margins(c[1], 12, 12, 30, 30)
        set_cell_margins(c[2], 12, 12, 30, 30)
        c[0].paragraphs[0].add_run(ro).bold = True
        c[1].paragraphs[0].add_run(mr)
        c[2].paragraphs[0].add_run(er)

    doc.add_page_break()

    # =========================================================================
    # BODY PAGE 12: CHAPTER 3 (3.5 + Table 3.3)
    # =========================================================================
    add_p("Role checks and institution-scope checks serve different purposes. A role check answers whether the user belongs to a permitted category. A scope check answers whether the specific record belongs to the institution or user that the request is authorized to access.",
          indent=0.4, space_after=6)
    add_sec_title("3.5 DATABASE DESIGN")
    add_p("The database stores the information needed by the main workflows. The supplied project audit identifies collections for users, institutions, courses, academic credits, credit policies, transfer requests, certificates, transcripts, API keys, API logs, audit logs, semester results, and result-import batches. Each model should have a clear purpose and should avoid storing unnecessary duplicate information.",
          indent=0.4, space_after=6)
    add_p("Table 3.3 Database Design", bold=True, size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=2)
    t_33 = doc.add_table(rows=1, cols=2)
    t_33.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_33.columns[0].width = Inches(2.2)
    t_33.columns[1].width = Inches(4.3)
    set_table_borders(t_33)
    h_33 = t_33.rows[0].cells
    set_cell_background(h_33[0], "F1F5F9")
    set_cell_background(h_33[1], "F1F5F9")
    h_33[0].paragraphs[0].add_run("MODEL / COLLECTION").bold = True
    h_33[1].paragraphs[0].add_run("PURPOSE").bold = True
    t33_data = [
        ("User", "Identity, role, authentication data, and user status"),
        ("Institution", "Institution profile and verification information"),
        ("Course", "Course information managed by an institution"),
        ("AcademicCredit", "Credit records associated with students and courses"),
        ("CreditPolicy", "Rules and version history used by the application"),
        ("TransferRequest", "Transfer request details and current decision state"),
        ("Certificate", "Certificate metadata and verification reference"),
        ("Transcript", "Transcript metadata and verification reference"),
        ("APIKey", "API key metadata, scope, and hashed secret"),
        ("APILog", "API request telemetry"),
        ("AuditLog", "Trace of selected important actions"),
        ("SemesterResult", "Imported or maintained semester results"),
        ("ResultImportBatch", "Metadata for a results import batch")
    ]
    for mo, pu in t33_data:
        r = t_33.add_row()
        c = r.cells
        set_cell_margins(c[0], 10, 10, 30, 30)
        set_cell_margins(c[1], 10, 10, 30, 30)
        c[0].paragraphs[0].add_run(mo).bold = True
        c[1].paragraphs[0].add_run(pu)

    doc.add_page_break()

    # =========================================================================
    # BODY PAGE 13: CHAPTER 3 (3.6 + 3.7)
    # =========================================================================
    add_sec_title("3.6 DATA RELATIONSHIPS AND INTEGRITY")
    add_p("A student can be associated with an institution and have multiple course and credit records. Courses are associated with institutions, while academic credit records link a student, a course, and the relevant academic information. Transfer requests refer to records and institutions involved in a proposed transfer. Certificates and transcripts contain the metadata needed to retrieve or verify the corresponding record.",
          indent=0.4, space_after=6)
    add_p("Data integrity requires more than defining a schema. The backend should check that referenced records exist, that the user is authorized to act on them, and that values fall within acceptable ranges. Duplicate checks are especially important for credit submission and results import, because repeating an operation should not accidentally award the same credit twice.",
          indent=0.4, space_after=6)
    add_p("The exact relationship cardinalities and indexes should be documented from the actual Mongoose schemas. If a field stores a URL to an external document rather than the file itself, the report should state that clearly.",
          indent=0.4, space_after=8)
    add_sec_title("3.7 AUTHENTICATION WORKFLOW")
    add_p("A user submits login credentials through the login form. The backend locates the user account, compares the submitted password with the stored bcrypt hash, and rejects invalid credentials. When authentication succeeds, the backend issues a signed JSON Web Token. The frontend uses the token when calling protected endpoints.",
          indent=0.4, space_after=6)
    add_p("Password hashing reduces the risk associated with accidental exposure of the database, because the stored value is not the original password. The implementation described in the project audit uses bcryptjs with a work factor of 12. Password hashes must never be returned in public API responses.",
          indent=0.4, space_after=6)

    doc.add_page_break()

    # =========================================================================
    # BODY PAGE 14: CHAPTER 3 (Figure 3.2 + 3.8)
    # =========================================================================
    add_fig("report_images/fig_3_2_orchestration.png", "Figure 3.2 Verified login and token workflow diagram", width=Inches(5.2))
    add_sec_title("3.8 AUTHORIZATION AND ROUTE PROTECTION")
    add_p("After a request reaches the backend, authentication middleware validates the token and identifies the current user. Authorization middleware checks whether the role is permitted for the requested endpoint. Where necessary, institution-scope middleware also checks whether the target record belongs to the institution that the user is allowed to manage.",
          indent=0.4, space_after=6)
    add_p("Public administrator registration is blocked in the supplied implementation summary. An administrator account is bootstrapped through a controlled server-side mechanism rather than allowing any visitor to select the administrator role. The deployment configuration must protect bootstrap credentials and secrets.",
          indent=0.4, space_after=6)
    add_p("A secure implementation should return suitable status codes for missing authentication, insufficient permissions, invalid input, and missing records. Error responses should be helpful without disclosing internal stack traces or secret configuration.",
          indent=0.4, space_after=6)

    doc.add_page_break()

    # =========================================================================
    # BODY PAGE 15: CHAPTER 3 (3.9 + 3.10)
    # =========================================================================
    add_sec_title("3.9 REST API DESIGN")
    add_p("The API groups related operations into route modules. Authentication routes handle registration, login, and retrieval of the current user. Other route groups support students, institutions, courses, credits, transfers, policies, certificates, transcripts, API keys, and logs. This organization allows controllers to focus on a defined set of operations.",
          indent=0.4, space_after=6)
    add_p("Each endpoint should have a clear request schema, response structure, authorization requirement, and error behavior. The API documentation should state whether an endpoint is public or protected, which role may call it, and whether it changes persistent data. Versioned endpoints should be documented separately if they differ from standard routes.",
          indent=0.4, space_after=6)
    add_p("The audit summary reports 58 REST endpoints across standard and versioned routes. This figure should be checked against the current code before being used as a final measured result.",
          indent=0.4, space_after=8)
    add_sec_title("3.10 ACADEMIC CREDIT VALIDATION")
    add_p("Before a credit record is saved, the system should verify that the student and course exist, the credit value falls within the permitted range, the grade follows the expected format, and the record is not a duplicate. It should also check the user’s authorization and the institution context. Validation should fail safely when required data is missing or inconsistent.",
          indent=0.4, space_after=6)
    add_p("The supplied audit describes an eight-point prevalidation process and a credit range of 1 to 30. The final report should list each implemented check from the actual validation function and avoid adding rules that are not present in code. Clear error messages help institution users correct a record without guessing which field caused the rejection.",
          indent=0.4, space_after=6)

    doc.add_page_break()

    # =========================================================================
    # BODY PAGE 16: CHAPTER 3 (Figure 3.3 + 3.11)
    # =========================================================================
    add_fig("report_images/fig_3_3_ast_analysis.png", "Figure 3.3 Verified credit validation workflow", width=Inches(4.2))
    add_sec_title("3.11 RESULTS IMPORT AND BATCH PROCESSING")
    add_p("The results-import workflow allows an institution user to upload a spreadsheet, review parsed rows, and confirm the batch after validation. The reported implementation uses Multer to hold the upload in memory and SheetJS/XLSX to read spreadsheet data. A preview step is useful because it gives the user an opportunity to identify invalid rows before records are written.",
          indent=0.4, space_after=6)
    add_p("A robust batch process should distinguish valid rows, rejected rows, and duplicates. It should also make confirmation explicit and ensure that retrying the same batch does not create duplicate credits. The project audit reports support for batch preview and confirmation, duplicate detection, and automatic credit conversion for passing grades. These behaviors should be demonstrated with actual test evidence.",
          indent=0.4, space_after=6)

    doc.add_page_break()

    # =========================================================================
    # BODY PAGE 17: CHAPTER 3 (Figure 3.4 + 3.12)
    # =========================================================================
    add_fig("report_images/fig_3_4_sandbox.png", "Figure 3.4 Verified spreadsheet import workflow", width=Inches(4.2))
    add_sec_title("3.12 SEMESTER PROGRESSION AND CORRECTIONS")
    add_p("The audit summary reports automatic semester progression when a results batch matches the active semester and all registered courses have been passed. This is a rule-driven action and should be tested with both successful and unsuccessful cases. A failed course, an incomplete batch, or a batch for another semester should not trigger progression unless the implemented policy explicitly permits it.",
          indent=0.4, space_after=6)
    add_p("Grade corrections need careful handling because they may affect credit totals and progression. The supplied summary describes a mandatory correction reason, a correction history, credit adjustments, and hash resealing. The final report should explain how the prior value and corrected value are recorded and who is allowed to perform a correction.",
          indent=0.4, space_after=6)

    doc.add_page_break()

    # =========================================================================
    # BODY PAGE 18: CHAPTER 3 (3.13 + Figure 3.5 + 3.14)
    # =========================================================================
    add_sec_title("3.13 TRANSFER REQUEST WORKFLOW")
    add_p("A transfer request represents a request to move or recognize credits across institutional contexts. The workflow described in the audit supports approval, conditional approval, or rejection. The decision should be linked to the request and accompanied by enough information for an authorized reviewer to understand the outcome.",
          indent=0.4, space_after=4)
    add_p("A transfer simulator is also described in the project audit, but it operates on the client side rather than through a dedicated backend simulation endpoint. The report must distinguish this planning interface from the persistent transfer-request process. A simulation helps a user explore a possible outcome; it is not the same as an institution formally approving a transfer.",
          indent=0.4, space_after=4)
    add_fig("report_images/fig_3_5_patch_lifecycle.png", "Figure 3.5 Verified transfer lifecycle diagram", width=Inches(5.0))
    add_sec_title("3.14 CERTIFICATE, TRANSCRIPT, AND API KEY HANDLING")
    add_p("Certificate and transcript features provide ways to view or verify academic documents. The supplied audit lists public verification routes for transcripts and certificates. Verification should return only the information needed to confirm a record and should not expose unrelated personal details.",
          indent=0.4, space_after=4)

    doc.add_page_break()

    # =========================================================================
    # BODY PAGE 19: CHAPTER 3 (3.14 cont, 3.15, 3.16)
    # =========================================================================
    add_p("The API-key workflow described in the audit creates keys with a recognizable prefix, displays the secret once, and stores a hash rather than the raw secret. Scopes such as reading credits or verifying certificates restrict what a key may do. Logs can record API activity, but they should not store raw secrets or bearer tokens.",
          indent=0.4, space_after=6)
    add_p("The audit indicates that document fields store URLs rather than binary files in the application database. This distinction matters: a URL reference does not by itself provide secure file storage or guarantee that the target file remains available.",
          indent=0.4, space_after=8)
    add_sec_title("3.15 SECURITY CONTROLS")
    add_p("The reported security controls include bcrypt password hashing, signed JWTs, role-based middleware, institution-scope checks, Helmet security headers, CORS configuration, rate limiting, input validation, and audit logging. These controls address different risks and should be treated as layers rather than as substitutes for one another.",
          indent=0.4, space_after=6)
    add_p("The audit also identifies limitations: a 24-hour JWT is not immediately revocable, there is no short-lived access token with refresh-token rotation, and the application follows a centralized clearinghouse architecture rather than peer-to-peer webhooks with mutual TLS. These limitations should be documented honestly and can form part of future work.",
          indent=0.4, space_after=8)
    add_sec_title("3.16 TESTING METHODOLOGY")
    add_p("Testing should cover individual functions, API behavior, role boundaries, data validation, and end-to-end workflows. Unit or focused tests help isolate logic such as credit validation and semester progression. API tests check request and response behavior. Integration tests check how controllers, models, and middleware work together. End-to-end tests verify that a complete workflow behaves as expected.",
          indent=0.4, space_after=6)
    add_p("Negative tests are as important as successful tests. Examples include logging in with an invalid password, attempting to use a student token on an administrator route, accessing another institution’s record, submitting duplicate credits, importing malformed spreadsheet rows, and attempting a correction without a reason.",
          indent=0.4, space_after=6)

    doc.add_page_break()

    # =========================================================================
    # BODY PAGE 20: CHAPTER 3 (3.17 + 3.18)
    # =========================================================================
    add_sec_title("3.17 DEVELOPMENT AND VERIFICATION PROCESS")
    add_p("A practical development cycle begins with defining the requirements, designing the data structures, implementing a small workflow, and testing it before adding the next workflow. The frontend and backend can be developed in parallel when the request and response formats are agreed upon. Version control helps track changes and makes it possible to return to a known working state.",
          indent=0.4, space_after=6)
    add_p("The supplied project notes report a successful frontend build, a health check with the database connected, and multiple test suites. Since these are audit-reported results, they should be reproduced on the final commit before submission. The final report should record the test date, command, environment, and result so that the evidence is repeatable.",
          indent=0.4, space_after=8)
    add_sec_title("3.18 METHODOLOGY SUMMARY")
    add_p("The methodology combines role-based interface design, REST API development, schema-based data storage, authentication and authorization middleware, validation workflows, and layered testing. The architecture supports separation of concerns, while the validation and audit features are intended to improve the reliability and traceability of academic record operations.",
          indent=0.4, space_after=6)
    add_p("The next chapter describes the proposed work modules from the point of view of each user role. The descriptions should be supported by screenshots from the actual application and should distinguish completed functions from future enhancements.",
          indent=0.4, space_after=6)

    doc.add_page_break()

    # =========================================================================
    # BODY PAGE 21: CHAPTER 4 (4.1 + 4.2)
    # =========================================================================
    add_chap_title("4", "PROPOSED WORK MODULES")
    add_sec_title("4.1 MODULE OVERVIEW")
    add_p("The application is organized around three dashboards and a set of shared services. The dashboards provide role-specific entry points, while the backend handles common tasks such as authentication, authorization, data validation, and record storage. This separation helps users focus on the tasks relevant to their responsibilities.",
          indent=0.4, space_after=6)
    add_p("The modules described in this chapter reflect the feature summary provided for the project. Before final submission, confirm the labels, navigation items, and screenshots against the running application. A feature that is present only as a visual mock-up should not be described as a completed backend capability.",
          indent=0.4, space_after=8)
    add_sec_title("4.2 STUDENT DASHBOARD")
    add_p("The student dashboard is designed to give a quick overview of academic progress. The credit wallet summarizes total, verified, and pending credits where those statuses are available. The semester timeline organizes credit history by academic period, while the results ledger provides a more detailed view of the underlying entries.",
          indent=0.4, space_after=6)
    add_p("The academic passport area brings together selected identity and institution information. Eligibility tracking compares accumulated credits with configured thresholds, while the academic pathway and course recommendation views help a student explore possible next steps. These suggestions should be presented as guidance rather than as an official academic decision.",
          indent=0.4, space_after=6)

    doc.add_page_break()

    # =========================================================================
    # BODY PAGE 22: CHAPTER 4 (Figure 4.1 + 4.3)
    # =========================================================================
    add_fig("report_images/fig_4_1_live_swarm.png", "Figure 4.1 Student Dashboard", width=Inches(5.2))
    add_sec_title("4.3 STUDENT CREDIT AND ELIGIBILITY FEATURES")
    add_p("The eligibility tracker described in the project audit includes thresholds for Certificate, Diploma, three-year undergraduate, and four-year degree pathways. Because eligibility rules can depend on programme requirements, course completion, and institutional policy, the interface should clearly state that the displayed threshold is based on the configured rule and may not replace formal review.",
          indent=0.4, space_after=6)
    add_p("The course recommendation feature is described as prerequisite-aware and provides match scores. A clear recommendation should explain the information used to produce it, such as completed courses or prerequisites, rather than presenting a score without context. The final report should only claim recommendation logic that can be traced to the current implementation.",
          indent=0.4, space_after=6)
    add_p("The transfer simulator gives students a way to explore a potential credit-transfer scenario. As noted earlier, the supplied audit describes it as client-side functionality. It should be labelled as a simulation and should not be confused with a formal transfer decision.",
          indent=0.4, space_after=6)

    doc.add_page_break()

    # =========================================================================
    # BODY PAGE 23: CHAPTER 4 (4.4 + Figure 4.2)
    # =========================================================================
    add_sec_title("4.4 INSTITUTION DASHBOARD")
    add_p("The institution dashboard supports institution-side academic record management. The supplied feature list includes student and course management, academic credit submission, transfer requests, credit policies, policy versions, API keys, API logs, transfer decisions, and certificate verification. Access to these functions should be controlled by the authenticated user’s role and institution scope.",
          indent=0.4, space_after=6)
    add_p("Credit entry and results import are particularly important because errors can affect the student’s record. Validation feedback should be clear, and users should have a way to review batch results before confirmation. Where a correction is allowed, the system should record the reason and preserve a trace of the change.",
          indent=0.4, space_after=6)
    add_fig("report_images/fig_4_2_risk_heatmap.png", "Figure 4.2 Institution Dashboard", width=Inches(5.2))

    doc.add_page_break()

    # =========================================================================
    # BODY PAGE 24: CHAPTER 4 (4.5 + Figure 4.3)
    # =========================================================================
    add_sec_title("4.5 ADMINISTRATOR DASHBOARD")
    add_p("The administrator dashboard provides a system-level view of the application. The audit summary lists counters, institution verification queues, global student and course management, credit oversight, analytics, API monitoring, transfers, and audit logs. The dashboard is intended to help an administrator identify activity that needs review.",
          indent=0.4, space_after=6)
    add_p("Administrative access should be limited to trusted users and should be auditable. The project summary states that public registration for the administrator role is blocked and that an administrator account is created through a server-side bootstrap process. Deployment instructions should ensure that any bootstrap credentials are changed or protected.",
          indent=0.4, space_after=6)
    add_fig("report_images/fig_4_3_bug_ledger.png", "Figure 4.3 Administrator Dashboard", width=Inches(5.2))

    doc.add_page_break()

    # =========================================================================
    # BODY PAGE 25: CHAPTER 4 (4.6 + Figure 4.4)
    # =========================================================================
    add_sec_title("4.6 API GATEWAY AND CROSS-INSTITUTIONAL ACCESS")
    add_p("The API layer provides a structured interface for authorized clients to request or submit selected data. API keys can be assigned scopes so that a client receives only the permissions it needs. For example, a client that only verifies certificates should not automatically receive permission to modify credit records.",
          indent=0.4, space_after=6)
    add_p("The term cross-institutional in the project title describes the intended use case. It should not be interpreted as proof that live external university systems have been connected. The supplied audit characterizes the current design as a centralized clearinghouse using machine-to-machine REST, not as a peer-to-peer integration with webhooks and mutual TLS.",
          indent=0.4, space_after=6)
    add_fig("report_images/fig_4_4_root_cause.png", "Figure 4.4 Cross-Institutional API Gateway Integration", width=Inches(5.2))

    doc.add_page_break()

    # =========================================================================
    # BODY PAGE 26: CHAPTER 4 (4.7 + Figure 4.5)
    # =========================================================================
    add_sec_title("4.7 CERTIFICATE AND TRANSCRIPT VERIFICATION")
    add_p("Verification routes allow a user to check whether a certificate or transcript reference is recognized by the application. The interface should return a clear status and only the fields needed for verification. A verification result should not be described as a cryptographic guarantee unless the implementation actually verifies a corresponding signature or integrity value.",
          indent=0.4, space_after=6)
    add_p("Transcript snapshots and verification codes can help make the verification process repeatable. The final report should explain how the code is generated, how the record is found, and what happens if the record is missing or no longer valid. A screenshot of both a successful and unsuccessful verification is useful evidence.",
          indent=0.4, space_after=6)
    add_fig("report_images/fig_4_5_autofix.png", "Figure 4.5 Certificate verification", width=Inches(5.2))

    doc.add_page_break()

    # =========================================================================
    # BODY PAGE 27: CHAPTER 4 (4.8 + Figure 4.6 + 4.9)
    # =========================================================================
    add_sec_title("4.8 AUDIT LOGS AND POLICY HISTORY")
    add_p("Audit logs are intended to provide a record of selected system actions. Policy history helps show how a policy changed over time. The project audit says policy versions are embedded in the CreditPolicy model’s policyHistory rather than stored in a separate collection, while transfer decisions are represented through TransferRequest and AuditLog rather than a separate TransferDecision collection.",
          indent=0.4, space_after=6)
    add_p("Documenting the actual data model avoids confusion between a user-interface menu item and a standalone database collection. The report should use the implementation’s real terminology and explain where history is stored.",
          indent=0.4, space_after=6)
    add_fig("report_images/fig_4_6_critic_debate.png", "Figure 4.6 Audit Logs and Policy History", width=Inches(5.2))
    add_sec_title("4.9 MODULE INTERACTION")

    doc.add_page_break()

    # =========================================================================
    # BODY PAGE 28: CHAPTER 4 (4.9 cont + 4.10)
    # =========================================================================
    add_p("The modules are connected through shared data and permissions. A student’s credit wallet depends on credit records that have been accepted by the backend. Institution-side workflows create or update records, and administrative views provide oversight. Verification endpoints expose a limited way to check selected records without granting full access to the underlying management interface.",
          indent=0.4, space_after=6)
    add_p("A typical flow begins when an institution user submits a credit record. The backend checks the request, validates referenced data and constraints, and stores the accepted record. The student dashboard can then show the updated credit information, while audit records provide a trail for relevant actions. If a transfer is requested, the institution-side decision workflow records the outcome.",
          indent=0.4, space_after=8)
    add_sec_title("4.10 MODULE SUMMARY")
    add_p("The proposed work modules combine student-facing visibility, institution-side record management, administrator oversight, and API-based verification. Their value depends on reliable data validation and clear access boundaries. In the final report, each module should be paired with actual screenshots and a brief explanation of a task that can be demonstrated during project evaluation.",
          indent=0.4, space_after=6)

    doc.add_page_break()

    # =========================================================================
    # BODY PAGE 29: CHAPTER 5 (5.1 + 5.2)
    # =========================================================================
    add_chap_title("5", "RESULTS AND DISCUSSION")
    add_sec_title("5.1 IMPLEMENTATION OVERVIEW")
    add_p("The project audit summary describes a full-stack application with role-specific dashboards, protected API routes, MongoDB models, and workflows for academic credits and related records. The frontend build and backend health checks were reported as successful in that audit. These results should be rerun on the exact version submitted for evaluation.",
          indent=0.4, space_after=6)
    add_p("Results should be presented as evidence rather than as broad claims. A screenshot demonstrates the visible state of a page, a test log demonstrates a particular behavior under the test conditions, and an API response demonstrates how an endpoint behaved for a given request. Each item supports a different kind of conclusion.",
          indent=0.4, space_after=8)
    add_sec_title("5.2 FRONTEND AND BACKEND VERIFICATION")
    add_p("The supplied audit reports that the frontend production build completed with 2,419 modules and zero build errors. It also reports that the backend health check returned HTTP 200 and confirmed a database connection. These are useful baseline checks: the frontend can be compiled, and the backend can reach the configured database.",
          indent=0.4, space_after=6)
    add_p("A successful build does not prove that every page behaves correctly, and a successful health check does not prove that every business workflow is correct. Functional tests are needed for login, role access, record validation, imports, transfers, and verification. The final submission should include the relevant console output or test report.",
          indent=0.4, space_after=6)

    doc.add_page_break()

    # =========================================================================
    # BODY PAGE 30: CHAPTER 5 (5.3 + Table 5.1 + 5.4)
    # =========================================================================
    add_sec_title("5.3 TEST RESULTS")
    add_p("Table 5.1 Reported Testing Summary", bold=True, size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=2)
    t_51 = doc.add_table(rows=1, cols=2)
    t_51.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_51.columns[0].width = Inches(2.6)
    t_51.columns[1].width = Inches(3.9)
    set_table_borders(t_51)
    h_51 = t_51.rows[0].cells
    set_cell_background(h_51[0], "F1F5F9")
    set_cell_background(h_51[1], "F1F5F9")
    h_51[0].paragraphs[0].add_run("TEST SUITE / CHECK").bold = True
    h_51[1].paragraphs[0].add_run("RESULT IN SUPPLIED AUDIT").bold = True
    t51_data = [
        ("Frontend production build", "Passed; 2,419 modules, 0 errors"),
        ("Backend health check", "HTTP 200; database connected"),
        ("Results import / progression", "68 of 68 assertions passed"),
        ("Institution statistics / invariants", "5 of 5 assertions passed"),
        ("Comprehensive end-to-end suite", "87 of 87 assertions passed"),
        ("Total reported assertions", "161 across 5 suites")
    ]
    for ts, re in t51_data:
        r = t_51.add_row()
        c = r.cells
        set_cell_margins(c[0], 12, 12, 30, 30)
        set_cell_margins(c[1], 12, 12, 30, 30)
        c[0].paragraphs[0].add_run(ts).bold = True
        c[1].paragraphs[0].add_run(re)

    add_p("These figures are reproduced from the project audit summary supplied earlier and have not been independently rerun while creating this document. Before final submission, execute the tests again and update the table if the results differ.",
          indent=0.4, space_before=4, space_after=6)
    add_sec_title("5.4 FUNCTIONAL WORKFLOW DISCUSSION")
    add_p("Authentication testing should confirm that valid credentials produce a session token and that invalid credentials are rejected. Role tests should confirm that student, institution, and administrator accounts are directed to the correct areas and cannot use routes outside their permissions. Institution-scope tests should check that one institution cannot access another institution’s restricted records.",
          indent=0.4, space_after=6)
    add_p("Credit workflow tests should include valid entries, invalid credit values, missing students or courses, invalid grades, and duplicate submissions. Results-import tests should include a valid spreadsheet, malformed rows, duplicate records, preview without confirmation, and successful confirmation. Correction tests should confirm that a reason is required and that the previous record remains traceable.",
          indent=0.4, space_after=6)

    doc.add_page_break()

    # =========================================================================
    # BODY PAGE 31: CHAPTER 5 (5.5 + 5.6 + 5.7)
    # =========================================================================
    add_sec_title("5.5 USER INTERFACE EVIDENCE")
    add_p("The final report should include screenshots from the actual application, captured at a readable size. Recommended screenshots include the login page, each of the three dashboards, student credit wallet, credit timeline, institution credit entry, results import preview, transfer request status, API key or API log view, and a verification result.",
          indent=0.4, space_after=6)
    add_p("Every screenshot should have a figure number and a descriptive caption. The text should explain what the screenshot demonstrates. Avoid screenshots that expose passwords, live API secrets, JWTs, personal student data, or environment variables.",
          indent=0.4, space_after=8)
    add_sec_title("5.6 SECURITY AND RELIABILITY DISCUSSION")
    add_p("The reported use of bcrypt password hashing, JWT authentication, role checks, institution-scope checks, Helmet, CORS configuration, rate limiting, validation, and audit logs provides several layers of protection. Each layer has a limited purpose: password hashing protects stored credentials, token validation authenticates requests, authorization controls access, and audit logging supports later review.",
          indent=0.4, space_after=6)
    add_p("The supplied audit also identifies areas for improvement. A 24-hour JWT may remain valid until expiry unless the server has a revocation mechanism. A future version could use short-lived access tokens and a carefully implemented refresh-token rotation process. The security review should also verify that secrets are not written to logs and that production CORS and rate-limit settings are appropriate.",
          indent=0.4, space_after=8)
    add_sec_title("5.7 LIMITATIONS")
    add_p("The transfer simulator is described as client-side only, so its output should not be presented as a server-validated transfer decision. Document fields store URLs rather than binary file contents, so document availability and access protection depend on the referenced storage. Policy history is embedded within the policy document, and transfer decisions are represented through the transfer request and audit records rather than separate collections.",
          indent=0.4, space_after=6)

    doc.add_page_break()

    # =========================================================================
    # BODY PAGE 32: CHAPTER 5 (5.7 cont + 5.8)
    # =========================================================================
    add_p("The system is described as a centralized clearinghouse using REST APIs. The supplied audit does not establish that external universities are already connected or that mutual TLS and peer-to-peer webhooks are implemented. These limitations define the current scope and should be stated clearly during the project review.",
          indent=0.4, space_after=8)
    add_sec_title("5.8 RESULTS SUMMARY")
    add_p("Based on the supplied audit, the project has a broad set of implemented modules and reported automated checks. The reported test suites cover import and progression, institution statistics and invariants, and end-to-end workflows. The most useful next step is to attach the reproducible test logs and screenshots that directly demonstrate these claims.",
          indent=0.4, space_after=6)
    add_p("A results chapter should not claim that the system eliminates all academic-record errors or guarantees interoperability. A more accurate conclusion is that the prototype introduces validation, role separation, and verification workflows intended to reduce specific operational problems. Any measured improvement would require a defined baseline and a repeatable evaluation.",
          indent=0.4, space_after=6)
    add_p("Once the final screenshots and test output have been inserted, this chapter should be reviewed with the supervisor to confirm that the interpretation matches the actual behavior of the application.",
          indent=0.4, space_after=6)

    doc.add_page_break()

    # =========================================================================
    # BODY PAGE 33: CHAPTER 6 (6.1 + 6.2)
    # =========================================================================
    add_chap_title("6", "CONCLUSIONS AND SUGGESTIONS FOR FUTURE WORK")
    add_sec_title("6.1 CONCLUSION")
    add_p("The NEP Aligned Standardized Academic Credit Accumulation Hub with Cross-Institutional Authentication API Gateways is designed to organize academic credit information through one role-based web application. The system brings together student progress views, institution-side record workflows, administrative oversight, and selected verification features. The MERN stack provides the technical foundation for the frontend, backend, and database.",
          indent=0.4, space_after=6)
    add_p("The project also demonstrates the importance of handling academic records carefully. Authentication, role checks, institution-scope restrictions, validation, and audit information help establish a safer workflow than relying on unstructured manual updates alone. The reported test results provide an initial indication that selected functions have been exercised, but they must be reproduced on the final submitted version.",
          indent=0.4, space_after=8)
    add_sec_title("6.2 SUGGESTIONS FOR FUTURE WORK")
    add_p("Future work could introduce short-lived access tokens and refresh-token rotation with revocation, improve secure document storage, and strengthen the process used to verify external institutions. The API layer could be evaluated against real integration requirements and tested with a controlled external client. Monitoring, backups, deployment configuration, and recovery procedures should also be reviewed before any production use.",
          indent=0.4, space_after=6)
    add_p("The transfer simulator could be extended into a server-side simulation service with explicit rules and a clear distinction between estimated outcomes and formal decisions. Policy changes could be accompanied by more detailed version comparisons and approval workflows. These improvements should be prioritized based on supervisor feedback and the needs of institutions that may use the system.",
          indent=0.4, space_after=6)

    doc.add_page_break()

    # =========================================================================
    # BODY PAGE 34: CHAPTER 6 (6.3)
    # =========================================================================
    add_sec_title("6.3 FINAL REMARK")
    add_p("The current prototype provides a foundation for exploring a more consolidated approach to academic credit management. Its practical value will depend on accurate source records, transparent policy rules, careful security review, and demonstrated interoperability. The final report should remain evidence-based and describe the completed implementation without overstating its readiness for institutional deployment.",
          indent=0.4, space_after=12)

    doc.add_page_break()

    # =========================================================================
    # BODY PAGE 35: CHAPTER 7 (REFERENCES)
    # =========================================================================
    add_chap_title("7", "REFERENCES")
    refs_data = [
        ("[1]", "University Grants Commission, “University Grants Commission (Establishment and Operation of Academic Bank of Credits in Higher Education) Regulations, 2021,” 2021. [Online]."),
        ("[2]", "M. Turkanović, M. Hölbl, K. Košič, M. Heričko, and A. Kamišalić, “EduCTX: A Blockchain-Based Higher Education Credit Platform,” IEEE Access, vol. 6, pp. 5112–5127."),
        ("[3]", "World Wide Web Consortium (W3C), “Verifiable Credentials Data Model v2.0,” W3C Recommendation, May 15, 2025. [Online]."),
        ("[4]", "M. Jones, J. Bradley, and N. Sakimura, “JSON Web Token (JWT),” Internet Engineering Task Force, RFC 7519, May 2015. [Online]."),
        ("[5]", "React Team, “Quick Start,” React Documentation. [Online]."),
        ("[6]", "OpenJS Foundation, “Node.js Documentation.” [Online]."),
        ("[7]", "Express.js, “Express Guide: Routing.” [Online]."),
        ("[8]", "MongoDB, Inc., “MongoDB Manual.” [Online]."),
        ("[9]", "Automattic, Inc., “Mongoose Documentation.” [Online].")
    ]
    for n, r_text in refs_data:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.line_spacing = 1.3
        p.paragraph_format.left_indent = Inches(0.4)
        p.paragraph_format.first_line_indent = Inches(-0.4)
        p.add_run(n + "\t").bold = True
        p.add_run(r_text)

    doc.add_page_break()

    # =========================================================================
    # BODY PAGE 36: CHAPTER 8 (INDIVIDUAL CONTRIBUTION - Member 1)
    # =========================================================================
    add_chap_title("8", "INDIVIDUAL CONTRIBUTION")
    add_p("The project “NEP Aligned Standardized Academic Credit Accumulation Hub with Cross-Institutional Authentication API Gateways” was carried out collaboratively by the team members. The work was divided across system design, development, testing, and documentation.",
          indent=0.4, space_after=8)
    add_p("TEAM MEMBER 1: HARIESH P (7376241CS195)", bold=True, size=13, space_before=4, space_after=4)
    add_p("Primarily responsible for the backend development, frontend development, backend–frontend integration, and API integration of the NEP Aligned Standardized Academic Credit Accumulation Hub.",
          indent=0.4, space_after=6)
    add_p("- Backend Development: Contributed to developing the server-side application using Node.js and Express.js. Worked on implementing REST API endpoints, request handling, validation, authentication, authorization, and application logic required to support the system's modules.",
          space_after=4)
    add_p("- Frontend Development: Contributed to developing the user interface using React and Vite. Worked on dashboard layouts, navigation, reusable interface components, and role-specific views for students, institutions, and administrators.",
          space_after=4)
    add_p("- Backend–Frontend Integration: Integrated frontend components with backend services to enable communication between the user interface, server-side logic, and database operations. Worked on handling API responses, displaying data dynamically, and managing success and error responses in the frontend.",
          space_after=4)
    add_p("- API Integration: Contributed to connecting frontend modules with REST APIs for authentication, user profile retrieval, academic credit operations, and other supported application features. Helped ensure that requests were sent with the required parameters and authentication information.",
          space_after=4)

    doc.add_page_break()

    # =========================================================================
    # BODY PAGE 37: CHAPTER 8 (Member 1 cont + Member 2)
    # =========================================================================
    add_p("- Authentication and Access Control Integration: Contributed to integrating login functionality, protected routes, and role-based access within the application to ensure that students, institutions, and administrators access their respective dashboards and permitted features.",
          space_after=4)
    add_p("- Testing and Debugging: Participated in testing integrated modules, identifying errors in API communication, checking application behavior, and resolving issues encountered during development and integration.",
          space_after=4)
    add_p("- Project Documentation: Contributed to documenting the application architecture, implemented modules, API integration, and development workflow for the project report.",
          space_after=8)
    add_p("TEAM MEMBER 2: MIDHUN M (7376242AL152)", bold=True, size=13, space_before=4, space_after=4)
    add_p("Primarily responsible for the database design and management, frontend development, and integration of database-supported application features in the NEP Aligned Standardized Academic Credit Accumulation Hub.",
          indent=0.4, space_after=6)
    add_p("- Database Design: Contributed to designing the MongoDB database structure using Mongoose models. Worked on organizing application data into suitable collections and defining relationships between users, institutions, courses, academic credits, certificates, transcripts, transfer requests, and other project entities.",
          space_after=4)
    add_p("- Database Management: Contributed to implementing database operations for storing, retrieving, updating, and managing academic and institutional information. Helped maintain data consistency and ensure that the application could retrieve the required information for different modules.",
          space_after=4)
    add_p("- Data Modelling and Validation: Worked on defining model fields, references, validation rules, and data structures to support reliable storage of student details, academic records, credit information, and institutional data.",
          space_after=4)

    doc.add_page_break()

    # =========================================================================
    # BODY PAGE 38: CHAPTER 8 (Member 2 cont)
    # =========================================================================
    add_p("- Frontend Development: Contributed to developing the frontend using React and Vite. Worked on building user interface components, dashboard pages, data tables, forms, and other visual elements required for interacting with the academic credit management system.",
          space_after=4)
    add_p("- Database–Application Integration: Contributed to connecting database-backed features with the application workflow so that information entered through the interface could be processed by the backend and stored or retrieved from MongoDB.",
          space_after=4)
    add_p("- Academic Data Presentation: Contributed to presenting stored academic information through frontend components, including student records, courses, credit details, and other relevant dashboard information.",
          space_after=4)
    add_p("- Testing and Debugging: Participated in checking database operations, validating data handling, identifying errors in data retrieval or storage, and supporting the correction of issues during development.",
          space_after=4)
    add_p("- Project Documentation: Contributed to documenting database structures, data management procedures, frontend modules, and related implementation details for the project report.",
          space_after=6)

    doc.add_page_break()

    # =========================================================================
    # BODY PAGE 39: CHAPTER 9 (PLAGIARISM REPORT)
    # =========================================================================
    add_chap_title("9", "PLAGIARISM REPORT")
    plag_img = os.path.join("output", "drillbit_plagiarism_report.png")
    if os.path.exists(plag_img):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(0)
        p_img.paragraph_format.space_after = Pt(0)
        p_img.add_run().add_picture(plag_img, height=Inches(6.6))

    doc.add_page_break()

    # =========================================================================
    # BODY PAGE 40: CHAPTER 10 (PROJECT OUTCOME)
    # =========================================================================
    add_chap_title("10", "PROJECT OUTCOME")
    cert_img = os.path.join("extracted_pdf2_images", "page_57_Image221.jpg")
    if os.path.exists(cert_img):
        p_img2 = doc.add_paragraph()
        p_img2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img2.paragraph_format.space_before = Pt(14)
        p_img2.paragraph_format.space_after = Pt(0)
        p_img2.add_run().add_picture(cert_img, width=Inches(5.6))

    # Save DOCX
    out_path = os.path.join("output", "Final_Project_Report.docx")
    doc.save(out_path)
    print(f"Successfully created {out_path}!")

if __name__ == '__main__':
    build_report()
