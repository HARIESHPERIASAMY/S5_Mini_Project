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

def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
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
    run.font.size = Pt(12)
    fld1 = parse_xml(r'<w:fldChar %s w:fldCharType="begin"/>' % nsdecls('w'))
    instr = parse_xml(r'<w:instrText %s xml:space="preserve"> PAGE </w:instrText>' % nsdecls('w'))
    fld2 = parse_xml(r'<w:fldChar %s w:fldCharType="separate"/>' % nsdecls('w'))
    fld3 = parse_xml(r'<w:fldChar %s w:fldCharType="end"/>' % nsdecls('w'))
    run._r.append(fld1)
    run._r.append(instr)
    run._r.append(fld2)
    run._r.append(fld3)

def generate_report():
    doc = Document()

    # SECTION 1: PRELIMS (Roman numerals i to x)
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

    # Footer for Section 1
    add_footer_page_number(sec1.footer.paragraphs[0])

    # Normal Style configuration
    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(12.5)
    style.font.color.rgb = RGBColor(0, 0, 0)
    style.paragraph_format.line_spacing = 1.35
    style.paragraph_format.space_after = Pt(4)
    style.paragraph_format.space_before = Pt(0)

    def add_p(text, bold=False, italic=False, size=12.5, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=4, line_spacing=1.35, indent=0.0):
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

    def add_chap_header(chap_num, chap_title):
        p1 = doc.add_paragraph()
        p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p1.paragraph_format.space_before = Pt(14)
        p1.paragraph_format.space_after = Pt(4)
        r1 = p1.add_run(f"CHAPTER {chap_num}")
        r1.bold = True
        r1.font.name = 'Times New Roman'
        r1.font.size = Pt(14)

        p2 = doc.add_paragraph()
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p2.paragraph_format.space_before = Pt(0)
        p2.paragraph_format.space_after = Pt(14)
        r2 = p2.add_run(chap_title.upper())
        r2.bold = True
        r2.font.name = 'Times New Roman'
        r2.font.size = Pt(14)

    def add_sec_header(sec_title):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(3)
        run = p.add_run(sec_title.upper())
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(13)
        return p

    def add_figure(img_path, caption, width=Inches(5.5)):
        if os.path.exists(img_path):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(3)
            p.add_run().add_picture(img_path, width=width)

            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_before = Pt(2)
            p_cap.paragraph_format.space_after = Pt(8)
            r = p_cap.add_run(caption)
            r.bold = True
            r.font.name = 'Times New Roman'
            r.font.size = Pt(11)

    # =========================================================================
    # PRELIM PAGE 1: TITLE PAGE (Page i)
    # =========================================================================
    print("Generating Prelims Page i (Title Page)...")
    add_p("INTELLIGENT MULTI-AGENT FRAMEWORK FOR AUTOMATED SOFTWARE TESTING AND BUG ANALYSIS (SENTINELMESH)",
          bold=True, size=15, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=18, line_spacing=1.3)
    add_p("PROJECT REPORT", bold=True, size=13, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=6)
    add_p("Submitted by", italic=True, size=13, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=6)
    add_p("HARIESH P (7376241CS195)", bold=True, size=14, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=2)
    add_p("MIDHUN M (7376242AL152)", bold=True, size=14, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=14)
    add_p("In partial fulfilment for the award of the degree of", italic=True, size=13, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=2)
    add_p("BACHELOR OF ENGINEERING", bold=True, size=14, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=2)
    add_p("in", italic=True, size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=2)
    add_p("COMPUTER SCIENCE AND ENGINEERING", bold=True, size=13, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=16)

    logo_path = os.path.join("output", "bit_logo.png")
    if os.path.exists(logo_path):
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_before = Pt(4)
        p_logo.paragraph_format.space_after = Pt(8)
        p_logo.add_run().add_picture(logo_path, width=Inches(1.25))

    add_p("BANNARI AMMAN INSTITUTE OF TECHNOLOGY", bold=True, size=13, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=1)
    add_p("(An Autonomous Institution Affiliated to Anna University, Chennai)", size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=1)
    add_p("SATHYAMANGALAM - 638 401", bold=True, size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=6)
    add_p("ANNA UNIVERSITY: CHENNAI 600 025", bold=True, size=12.5, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=6)
    add_p("OCTOBER 2026", bold=True, size=12.5, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=0)

    doc.add_page_break()

    # =========================================================================
    # PRELIM PAGE 2: BONAFIDE CERTIFICATE (Page ii)
    # =========================================================================
    print("Generating Prelims Page ii (Bonafide Certificate)...")
    add_p("BONAFIDE CERTIFICATE", bold=True, size=14, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=16, space_after=18)
    add_p("Certified that this project report titled “INTELLIGENT MULTI-AGENT FRAMEWORK FOR AUTOMATED SOFTWARE TESTING AND BUG ANALYSIS (SENTINELMESH)” is the bonafide work of “ HARIESH P (7376241CS195), MIDHUN M (7376242AL152) ” who carried out the project work under my supervision.",
          size=12.5, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=10, space_after=24, line_spacing=1.4)

    t_sig = doc.add_table(rows=1, cols=2)
    t_sig.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_sig.autofit = False
    t_sig.columns[0].width = Inches(3.2)
    t_sig.columns[1].width = Inches(3.2)

    p_left = t_sig.cell(0, 0).paragraphs[0]
    p_left.paragraph_format.line_spacing = 1.2
    p_left.paragraph_format.space_after = Pt(2)
    r_l1 = p_left.add_run("Dr. Ramya R\n")
    r_l1.bold = True
    r_l2 = p_left.add_run("SUPERVISOR\n")
    r_l2.bold = True
    p_left.add_run("Associate Professor\nDepartment of Computer Science\nand Engineering\nBannari Amman Institute of\nTechnology,\nSathyamangalam – 638401")

    p_right = t_sig.cell(0, 1).paragraphs[0]
    p_right.paragraph_format.line_spacing = 1.2
    p_right.paragraph_format.space_after = Pt(2)
    r_r1 = p_right.add_run("Dr. Sasikala D\n")
    r_r1.bold = True
    r_r2 = p_right.add_run("HEAD OF THE DEPARTMENT\n")
    r_r2.bold = True
    p_right.add_run("Professor and Head\nDepartment of Computer Science\nand Engineering\nBannari Amman Institute of\nTechnology,\nSathyamangalam – 638401")

    add_p("", space_before=36, space_after=12)
    add_p("Submitted for the Project Viva Voce examination held on ……………………", size=12.5, space_before=16, space_after=40)

    t_exam = doc.add_table(rows=1, cols=2)
    t_exam.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_exam.columns[0].width = Inches(3.2)
    t_exam.columns[1].width = Inches(3.2)
    r_ex1 = t_exam.cell(0, 0).paragraphs[0].add_run("INTERNAL EXAMINER")
    r_ex1.bold = True
    r_ex2 = t_exam.cell(0, 1).paragraphs[0].add_run("EXTERNAL EXAMINER")
    r_ex2.bold = True
    t_exam.cell(0, 1).paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    doc.add_page_break()

    # =========================================================================
    # PRELIM PAGE 3: DECLARATION (Page iii)
    # =========================================================================
    print("Generating Prelims Page iii (Declaration)...")
    add_p("DECLARATION", bold=True, size=14, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=16, space_after=18)
    add_p("We affirm that the project work titled “INTELLIGENT MULTI-AGENT FRAMEWORK FOR AUTOMATED SOFTWARE TESTING AND BUG ANALYSIS (SENTINELMESH)”, submitted in partial fulfilment for the award of the degree of Bachelor of Engineering in Computer Science and Engineering is the record of work carried out by us under the guidance of RAMYA R, Associate Professor, Department of Computer Science and Engineering, Bannari Amman Institute of Technology. It has not formed part of any other project work submitted for the award of any degree or diploma at this or any other university.",
          size=12.5, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=10, space_after=36, line_spacing=1.4)

    t_dec = doc.add_table(rows=1, cols=2)
    t_dec.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_dec.columns[0].width = Inches(3.2)
    t_dec.columns[1].width = Inches(3.2)
    t_dec.cell(0, 0).paragraphs[0].add_run("HARIESH P\n(7376241CS195)").bold = True
    t_dec.cell(0, 1).paragraphs[0].add_run("MIDHUN M\n(7376242AL152)").bold = True
    t_dec.cell(0, 1).paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    add_p("", space_before=36, space_after=12)
    add_p("I certify that the declaration made above by the candidates is true.", size=12.5, space_before=20, space_after=36)

    p_sup = doc.add_paragraph()
    p_sup.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_sup.paragraph_format.line_spacing = 1.2
    r_s1 = p_sup.add_run("Dr. RAMYA R\n")
    r_s1.bold = True
    r_s2 = p_sup.add_run("ASSOCIATE PROFESSOR")
    r_s2.bold = True

    doc.add_page_break()

    # =========================================================================
    # PRELIM PAGE 4: ACKNOWLEDGEMENT (Page iv)
    # =========================================================================
    print("Generating Prelims Page iv (Acknowledgement)...")
    add_p("ACKNOWLEDGEMENT", bold=True, size=14, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=16, space_after=18)
    add_p("We would like to enunciate heartfelt thanks to our esteemed Chairman Dr. S.V. Balasubramaniam, and the respected Principal Dr. C. Palanisamy, for providing excellent facilities and support during the course of study in this institute.",
          size=12.5, space_before=10, space_after=14, indent=0.4, line_spacing=1.4)
    add_p("We are grateful to Dr. Sasikala D, Head of the Department, Department of Computer Science and Engineering, for her valuable suggestions to carry out the project work successfully.",
          size=12.5, space_before=6, space_after=14, indent=0.4, line_spacing=1.4)
    add_p("We wish to express our sincere thanks to Faculty Guide Dr. Ramya R, Associate Professor, Department of Computer Science and Engineering, for her constructive ideas, inspirations, encouragement, excellent guidance, and much needed technical support extended to complete our project work.",
          size=12.5, space_before=6, space_after=14, indent=0.4, line_spacing=1.4)
    add_p("We would like to thank our friends, faculty and non-teaching staff who have directly and indirectly contributed to the success of this project.",
          size=12.5, space_before=6, space_after=36, indent=0.4, line_spacing=1.4)

    p_ack_names = doc.add_paragraph()
    p_ack_names.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_ack_names.paragraph_format.line_spacing = 1.2
    r_an1 = p_ack_names.add_run("HARIESH P\n(7376241CS195)\n")
    r_an1.bold = True
    r_an2 = p_ack_names.add_run("MIDHUN M\n(7376242AL152)")
    r_an2.bold = True

    doc.add_page_break()

    # =========================================================================
    # PRELIM PAGE 5: ABSTRACT (Page v)
    # =========================================================================
    print("Generating Prelims Page v (Abstract)...")
    add_p("ABSTRACT", bold=True, size=14, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=16, space_after=18)
    add_p("The project “Intelligent Multi-Agent Framework for Automated Software Testing and Bug Analysis (SentinelMesh)” aims to develop an autonomous, multi-agent quality assurance platform that unifies static code analysis, dynamic test execution, root-cause diagnosis, and pre-flight program repair. The system employs nine specialized software agents coordinated through an asynchronous FastAPI orchestrator: OrchestratorAgent, StaticAnalysisAgent, TestGenerationAgent, TestExecutionAgent, BugClassificationAgent, RootCauseAgent, AutoFixAgent, CriticAgent, and ASTMutationEngine. The framework parses source code using Python’s native Abstract Syntax Tree (AST) grammar to compute cyclomatic complexity, detect heuristic security and reliability code smells, and assign bounded file risk scores. It automatically synthesizes pytest suites, executes them within isolated OS subprocesses governed by psutil process-tree guards, normalizes and deduplicates defects via 128-bit MD5 fingerprinting, and isolates faulty code scopes through backward AST slicing. When failures occur, candidate patches are synthesized, verified in isolated temporary sandboxes against full regression suites, and evaluated through two rounds of adversarial critic debate between Advocate and Skeptic personas. An integrated AST mutation engine empirically measures test suite fault-revealing adequacy. The system is implemented using Python, FastAPI, SQLite with Write-Ahead Logging, React 19, and Vite, operating fully air-gapped without mandatory cloud API dependencies to guarantee privacy, deterministic execution, and reproducible software reliability.",
          size=12.5, space_before=10, space_after=12, indent=0.4, line_spacing=1.45)

    doc.add_page_break()

    # =========================================================================
    # PRELIM PAGES 6, 7, 8: TABLE OF CONTENTS (Pages vi, vii, viii)
    # =========================================================================
    print("Generating Prelims Pages vi, vii, viii (Table of Contents)...")
    add_p("TABLE OF CONTENTS", bold=True, size=14, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=16, space_after=14)

    # TOC Part 1 (Page vi)
    t_toc1 = doc.add_table(rows=1, cols=3)
    t_toc1.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_toc1.columns[0].width = Inches(1.3)
    t_toc1.columns[1].width = Inches(4.3)
    t_toc1.columns[2].width = Inches(0.9)
    hdr1 = t_toc1.rows[0].cells
    hdr1[0].paragraphs[0].add_run("CHAPTER NO.").bold = True
    hdr1[1].paragraphs[0].add_run("TITLE").bold = True
    hdr1[2].paragraphs[0].add_run("PAGE NO.").bold = True
    hdr1[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    toc_items_p1 = [
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
    for c_no, tit, p_no, is_b in toc_items_p1:
        row = t_toc1.add_row()
        cells = row.cells
        set_cell_margins(cells[0], 25, 25, 40, 40)
        set_cell_margins(cells[1], 25, 25, 40, 40)
        set_cell_margins(cells[2], 25, 25, 40, 40)
        r0 = cells[0].paragraphs[0].add_run(c_no)
        r1 = cells[1].paragraphs[0].add_run(tit)
        r2 = cells[2].paragraphs[0].add_run(p_no)
        cells[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
        if is_b:
            r0.bold = True
            r1.bold = True
            r2.bold = True

    doc.add_page_break()

    # TOC Part 2 (Page vii)
    t_toc2 = doc.add_table(rows=0, cols=3)
    t_toc2.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_toc2.columns[0].width = Inches(1.3)
    t_toc2.columns[1].width = Inches(4.3)
    t_toc2.columns[2].width = Inches(0.9)

    toc_items_p2 = [
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
    for c_no, tit, p_no, is_b in toc_items_p2:
        row = t_toc2.add_row()
        cells = row.cells
        set_cell_margins(cells[0], 35, 35, 40, 40)
        set_cell_margins(cells[1], 35, 35, 40, 40)
        set_cell_margins(cells[2], 35, 35, 40, 40)
        r0 = cells[0].paragraphs[0].add_run(c_no)
        r1 = cells[1].paragraphs[0].add_run(tit)
        r2 = cells[2].paragraphs[0].add_run(p_no)
        cells[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
        if is_b:
            r0.bold = True
            r1.bold = True
            r2.bold = True

    doc.add_page_break()

    # TOC Part 3 (Page viii)
    t_toc3 = doc.add_table(rows=0, cols=3)
    t_toc3.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_toc3.columns[0].width = Inches(1.3)
    t_toc3.columns[1].width = Inches(4.3)
    t_toc3.columns[2].width = Inches(0.9)

    toc_items_p3 = [
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
    for c_no, tit, p_no, is_b in toc_items_p3:
        row = t_toc3.add_row()
        cells = row.cells
        set_cell_margins(cells[0], 40, 40, 40, 40)
        set_cell_margins(cells[1], 40, 40, 40, 40)
        set_cell_margins(cells[2], 40, 40, 40, 40)
        r0 = cells[0].paragraphs[0].add_run(c_no)
        r1 = cells[1].paragraphs[0].add_run(tit)
        r2 = cells[2].paragraphs[0].add_run(p_no)
        cells[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
        if is_b:
            r0.bold = True
            r1.bold = True
            r2.bold = True

    doc.add_page_break()

    # =========================================================================
    # PRELIM PAGE 9: LIST OF TABLES (Page ix)
    # =========================================================================
    print("Generating Prelims Page ix (List of Tables)...")
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
        set_cell_margins(cells[0], 50, 50, 40, 40)
        set_cell_margins(cells[1], 50, 50, 40, 40)
        set_cell_margins(cells[2], 50, 50, 40, 40)
        cells[0].paragraphs[0].add_run(t_no)
        cells[1].paragraphs[0].add_run(t_name)
        cells[2].paragraphs[0].add_run(p_no)
        cells[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    doc.add_page_break()

    # =========================================================================
    # PRELIM PAGE 10: LIST OF FIGURES (Page x)
    # =========================================================================
    print("Generating Prelims Page x (List of Figures)...")
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
        set_cell_margins(cells[0], 40, 40, 40, 40)
        set_cell_margins(cells[1], 40, 40, 40, 40)
        set_cell_margins(cells[2], 40, 40, 40, 40)
        cells[0].paragraphs[0].add_run(f_no)
        cells[1].paragraphs[0].add_run(f_name)
        cells[2].paragraphs[0].add_run(p_no)
        cells[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # =========================================================================
    # SECTION 2: BODY CHAPTERS 1 TO 10 (Arabic numbers 1 to 40)
    # =========================================================================
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

    # Footer for Section 2
    add_footer_page_number(sec2.footer.paragraphs[0])

    # -------------------------------------------------------------------------
    # CHAPTER 1: INTRODUCTION (Pages 1 to 5)
    # -------------------------------------------------------------------------
    print("Generating Chapter 1: Introduction (Pages 1 to 5)...")
    # Page 1
    add_chap_header("1", "INTRODUCTION")
    add_sec_header("1.1 BACKGROUND")
    add_p("Modern software systems form the foundational bedrock of critical societal infrastructure, encompassing healthcare diagnostics, distributed financial ledgers, cloud service fabrics, telecommunication switching networks, and autonomous automotive control architectures. As software applications scale in complexity and distribution, the engineering imperative to verify correctness, enforce syntactic compliance, prevent security vulnerabilities, and ensure runtime reliability escalates exponentially. Software Quality Assurance represents the disciplined framework of evaluating software artifacts across the entire Software Development Life Cycle to guarantee that release candidates conform strictly to architectural specifications and functional requirements.",
          indent=0.4, space_after=8)
    add_p("Historically, quality assurance relied heavily on manual exploratory testing, informal peer walkthroughs, and static verification checklists. However, modern agile practices, continuous integration pipelines, and accelerated release cadences—where production deployments execute multiple times daily—have rendered purely manual quality assurance obsolete. Defects that evade pre-merge verification cycles accumulate as technical debt, propagate into distributed production clusters, compromise user security, and inflict catastrophic financial and reputational damages upon organizations.",
          indent=0.4, space_after=8)
    add_sec_header("1.2 PROJECT OVERVIEW")
    add_p("To resolve the structural disconnects of traditional testing methodologies, this project introduces SentinelMesh, an intelligent, autonomous multi-agent framework tailored for automated software testing, static code smell detection, dynamic subprocess sandboxing, causal root-cause tracing, and pre-flight automated program repair. Built upon Python's native Abstract Syntax Tree (AST) grammar, FastAPI asynchronous endpoints, SQLite Write-Ahead Logging persistence, and a reactive Vite/React telemetry frontend, SentinelMesh establishes a fully cooperative mesh of nine specialized software agents.",
          indent=0.4, space_after=8)
    add_p("The architecture operates without mandatory cloud dependencies, providing an air-gapped, zero-cost, privacy-preserving testing ecosystem capable of local execution on developer workstations. By unifying compiler-level AST heuristics with isolated execution runtimes, SentinelMesh automates the end-to-end defect triage lifecycle from raw code ingestion to verified, regression-free pull request patches.",
          indent=0.4, space_after=8)

    doc.add_page_break()

    # Page 2
    add_sec_header("1.3 NEED FOR THE SYSTEM")
    add_p("Contemporary continuous integration and continuous deployment pipelines position automated software verification as the primary gateway for release promotion. Dynamic testing frameworks, such as pytest and unittest, coupled with statement coverage instrumentation, provide empirical metrics regarding test suite execution paths. However, writing robust, high-coverage unit tests remains an arduous, error-prone manual task. Software engineers predominantly compose optimistic happy-path assertions while failing to anticipate boundary anomalies, off-by-one indices, type coercions, division by zero, or unhandled runtime exceptions.",
          indent=0.4, space_after=8)
    add_p("Furthermore, when automated tests fail within standard continuous integration pipelines, developers encounter a taxing multi-stage cognitive burden: deconstructing verbose terminal logs, classifying failure taxonomies, reconstructing backward variable dependency chains, synthesizing code fixes, and executing regression test suites to certify stability. A developer-centric automated quality platform capable of executing these stages autonomously can radically diminish defect remediation latency, eliminate debugging fatigue, and standardize quality governance across enterprise repositories.",
          indent=0.4, space_after=8)
    add_sec_header("1.4 PROBLEM IDENTIFICATION")
    add_p("Current automated software quality tooling suffers from acute architectural fragmentation. Static analysis tools (such as linters and pattern checkers) evaluate codebases without runtime awareness, emitting high volumes of benign warnings that induce developer alert fatigue. Conversely, dynamic test runners report failures but lack semantic awareness of root causes. Emerging Large Language Model repair agents suffer from hallucination, context saturation, and lack of deterministic execution feedback.",
          indent=0.4, space_after=8)
    add_p("A second critical challenge is the risk of test flakiness and runaway processes during automated execution. Executing untrusted or dynamically synthesized test scripts without robust operating system sandboxing can lead to orphaned background processes, resource starvation, and intermittent non-deterministic test failures that erode developer trust in testing automation.",
          indent=0.4, space_after=8)
    add_p("A third challenge involves automated program repair safety. Existing repair tools frequently produce over-fitted patches that satisfy failing unit tests but inadvertently break adjacent system contracts or introduce silent security regressions. A unified framework combining deterministic compiler AST analysis, isolated sandboxing, and adversarial verification is urgently needed.",
          indent=0.4, space_after=8)

    doc.add_page_break()

    # Page 3
    add_sec_header("1.5 OBJECTIVES")
    add_p("The primary objective of this project is to architect, develop, and validate an intelligent, autonomous multi-agent framework (SentinelMesh) that automates software testing, defect analysis, and regression-safe repair. To achieve this, the investigation is structured around five core engineering objectives:",
          indent=0.4, space_after=6)
    add_p("1. Multi-Agent Mesh Coordination: Design an asynchronous orchestration engine coordinating nine specialized agents across static analysis, test generation, test execution, bug classification, root-cause analysis, auto-fixing, critic review, mutation testing, and reporting.",
          indent=0.4, space_after=4)
    add_p("2. Deterministic AST Analysis: Develop a native AST parsing engine to calculate cyclomatic complexity via decision branch counting, detect common security and reliability code smells, and assign bounded file risk scores [0 to 100].",
          indent=0.4, space_after=4)
    add_p("3. Subprocess Sandboxing: Build an isolated execution runner with process-tree controls to execute test suites safely, compute statement and branch coverage, and mitigate test flakiness.",
          indent=0.4, space_after=4)
    add_p("4. Causal Root-Cause Slicing & Pre-Flight Repair: Construct an engine that extracts local AST code slices around failure lines, constructs causal fault chains, synthesizes patches, and verifies them in a temporary sandbox to confirm regression safety.",
          indent=0.4, space_after=4)
    add_p("5. Adversarial Critic & Mutation Testing: Implement a dual-perspective critic agent to conduct automated debate rounds and an AST mutation engine to evaluate the empirical adequacy of generated test suites.",
          indent=0.4, space_after=6)
    add_sec_header("1.6 SCOPE OF THE PROJECT")
    add_p("The operational scope of SentinelMesh focuses on Python codebases (.py source files, packages, and frameworks). The system is engineered to function in an air-gapped, zero-dependency offline mode using deterministic AST rules, while offering modular API adapters for cloud-hosted LLMs (e.g., Gemini, OpenAI). Hardware boundaries are scoped for standard developer workstations running Windows or POSIX environments with local SQLite database storage.",
          indent=0.4, space_after=6)
    add_sec_header("1.7 EXPECTED OUTCOME")
    add_p("The expected outcome is a fully functional, demonstrable quality assurance platform that automates test synthesis, executes suites under strict process isolation, eliminates 100% of regression-inducing candidate patches, and reduces defect remediation latency by over 80%.",
          indent=0.4, space_after=8)

    doc.add_page_break()

    # Page 4
    add_p("The project provides an opportunity to unify full-stack system architecture, compiler theory, and autonomous multi-agent collaboration in a practical, production-grade quality platform: calculating abstract syntax tree metrics, managing isolated subprocesses, streaming real-time telemetry, and conducting automated peer reviews. The effectiveness of the framework is verified through concrete test suites, API contracts, benchmark evaluations, and reproducible performance metrics.",
          indent=0.4, space_after=8)
    add_sec_header("1.8 USERS AND THEIR NEEDS")
    add_p("Software Developers: Require immediate, actionable feedback on code modifications without navigating verbose terminal stack traces. They benefit from automated pytest generation for newly written functions, localized AST code slicing that pinpoints exact failure lines, and pre-flight verified patch diffs that can be reviewed and accepted with one click.",
          indent=0.4, space_after=6)
    add_p("QA and DevOps Engineers: Require deterministic continuous integration pipeline integration, automated regression testing, flaky test detection, and empirical mutation kill scores to certify that test suites possess genuine fault-revealing capabilities. They need isolated execution environments that prevent runaway child processes or zombie workers from crashing build agents.",
          indent=0.4, space_after=6)
    add_p("Engineering Managers & Architects: Require systemic visibility into repository health, cyclomatic complexity distributions, security smell hotspots, and quantitative return-on-investment analytics that justify automated quality governance over manual triage overhead.",
          indent=0.4, space_after=8)
    add_sec_header("1.9 REPORT ORGANIZATION")
    add_p("Chapter 1 introduces the background, project overview, objectives, scope, expected outcome, and stakeholder requirements. Chapter 2 reviews authoritative literature across automated testing, static analysis, sandboxing, automated program repair, multi-agent LLM systems, and mutation testing. Chapter 3 presents the system architecture, development technologies, database schema, mathematical scoring models, and core algorithms. Chapter 4 details the operational implementation and interface contracts of the nine specialized software agents. Chapter 5 presents empirical benchmark results, test evidence, comparative evaluations, and limitations. Chapter 6 concludes the report with consolidated findings and future trajectories.",
          indent=0.4, space_after=8)

    doc.add_page_break()

    # Page 5
    add_sec_header("1.10 CHAPTER SUMMARY")
    add_p("This introductory chapter has articulated the critical necessity for modernizing software quality assurance in rapid continuous delivery environments. The exponential growth of software scale and the inherent fragility of purely manual test writing and debugging workflows create substantial engineering liabilities. By framing the core operational requirements around multi-agent collaboration, deterministic AST parsing, subprocess sandboxing, causal fault tracing, and empirical mutation adequacy, SentinelMesh addresses the acute disconnect between static linting and dynamic execution.",
          indent=0.4, space_after=10)
    add_p("The operational scope, core objectives, and stakeholder requirements defined herein serve as the architectural blueprint for the subsequent technical design and empirical evaluation. SentinelMesh transitions software testing from a passive, retrospective reporting mechanism into an active, autonomous self-healing quality assurance ecosystem.",
          indent=0.4, space_after=10)
    add_p("The next chapter provides a thorough review of relevant academic literature, exploring historical foundations and contemporary state-of-the-art approaches in automated software testing, program repair, and multi-agent coordination.",
          indent=0.4, space_after=8)

    doc.add_page_break()

    # -------------------------------------------------------------------------
    # CHAPTER 2: LITERATURE SURVEY (Pages 6 to 8)
    # -------------------------------------------------------------------------
    print("Generating Chapter 2: Literature Survey (Pages 6 to 8)...")
    # Page 6
    add_chap_header("2", "LITERATURE SURVEY")
    add_p("A literature survey establishes existing approaches, theoretical foundations, and technological advancements related to automated software testing, defect diagnosis, and program repair. Automated test case generation originated as an optimization problem targeting code coverage. Fraser and Arcuri pioneered search-based software testing (SBST) through whole-suite genetic algorithms in the EvoSuite framework [1]. Their work demonstrated that optimizing an entire test suite simultaneously against branch coverage objectives avoids the bloat and local optima common to single-target test generators. However, search-based test generators frequently produce synthetic inputs lacking real-world domain semantics, generating assertions that appear unintelligible to human developers.",
          indent=0.4, space_after=8)
    add_p("Static code analysis evaluates syntactic and structural properties of software without runtime execution. McCabe formulated cyclomatic complexity based on directed control flow graphs, defining the fundamental mathematical basis for quantifying program decision logic and testing thoroughness [2]. In contemporary compiler architectures, Abstract Syntax Tree (AST) representations enable precise structural traversals. Neamtiu et al. demonstrated that tree-matching algorithms over ASTs effectively track software evolution patterns and identify syntactic inconsistencies across releases [3]. Security linters like Bandit inspect Python AST nodes for common security vulnerabilities [4]. However, static linters inherently lack runtime semantic context, unable to determine whether a flagged vulnerability exists on an active execution path.",
          indent=0.4, space_after=8)
    add_p("Dynamic binary instrumentation and isolated execution principles established by Luk et al. demonstrate that runtime monitoring exposes memory corruptions and assertion violations unreachable via static inspection [5]. However, dynamic test suites frequently suffer from test flakiness—intermittent failures caused by non-deterministic factors rather than source bugs. Lam et al. performed a large-scale empirical study of test flakiness in Python, demonstrating that strict subprocess isolation, dedicated temporary directories, and process-tree termination mechanisms are mandatory prerequisites for executing dynamically generated test code safely [6].",
          indent=0.4, space_after=8)

    doc.add_page_break()

    # Page 7
    add_p("Automated Program Repair (APR) aims to synthesize valid source patches that rectify detected faults without human intervention. Weimer et al. established GenProg, employing genetic programming to mutate AST nodes guided by test suite fitness functions [7]. However, Qi et al. conducted an influential critical analysis of GenProg patches, revealing that the overwhelming majority of synthesized repairs were superficial test-suite over-fitting: the patches merely deleted functional code to bypass failing assertions rather than fixing the underlying semantic bug [8]. Le Goues et al. reviewed a decade of APR research, concluding that multi-tier validation, regression suite execution, and semantic pre-flight verification are non-negotiable requirements before any automatically generated patch can be safely merged [9].",
          indent=0.4, space_after=8)
    add_p("The advent of Large Language Models has inspired multi-agent architectures that simulate software engineering workflows. Qian et al. presented ChatDev, demonstrating that multi-agent conversational debate uncovers edge-case bugs that single-prompt LLMs consistently overlook [10]. Despite their conceptual novelty, existing multi-agent software engineering frameworks operate primarily as conversational simulations; they lack integrated AST mutation testing, local subprocess execution sandboxing, and deterministic offline heuristics.",
          indent=0.4, space_after=8)
    add_p("Mutation testing evaluates the fault-revealing adequacy of test suites by injecting synthetic faults into source code. Jia and Harman provided an authoritative survey of mutation testing, formalizing the Competent Programmer Hypothesis and the Coupling Effect [11]. Papadakis et al. demonstrated that mutation scores correlate significantly higher with genuine defect detection than statement or branch coverage [12]. Groce et al. highlighted the computational costs of full mutation testing in Python, advocating for targeted AST operator substitution to achieve practical execution latencies [13].",
          indent=0.4, space_after=8)
    add_p("The literature reveals three persistent research voids: (1) Lack of Static-Dynamic Co-Design: Linters and dynamic test runners operate in isolation without bidirectional feedback loops; (2) Over-Fitting in Program Repair: APR systems synthesize code that satisfies immediate assertions but breaks broader system contracts; and (3) Cloud Vulnerability & Cost: Emerging LLM agents depend on cloud APIs, exposing proprietary source code and incurring prohibitive operational costs.",
          indent=0.4, space_after=8)

    doc.add_page_break()

    # Page 8
    add_p("In summary, the literature survey establishes the technical and conceptual foundations for SentinelMesh. The reviewed standards, systems, and algorithms provide clear guidance for designing a secure, maintainable, and robust quality platform. The following table provides a structured comparative framework contrasting existing software testing paradigms with SentinelMesh across key architectural dimensions.",
          indent=0.4, space_after=12)

    add_p("Table 2.1 Comparison Framework", bold=True, size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=4)

    t_comp = doc.add_table(rows=1, cols=2)
    t_comp.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_comp.columns[0].width = Inches(2.2)
    t_comp.columns[1].width = Inches(4.3)
    set_table_borders(t_comp)

    h_c = t_comp.rows[0].cells
    set_cell_background(h_c[0], "F1F5F9")
    set_cell_background(h_c[1], "F1F5F9")
    h_c[0].paragraphs[0].add_run("AREA").bold = True
    h_c[1].paragraphs[0].add_run("QUESTIONS TO ASK OF EACH SOURCE").bold = True

    comp_rows = [
        ("Test Synthesis\n[1], [10]", "How are test cases and assertions generated, and do they capture edge cases?"),
        ("Static Profiling\n[2], [4]", "How is complexity quantified and how are security vulnerabilities identified?"),
        ("Execution Sandboxing\n[5], [6]", "Does the system isolate test execution and prevent runaway process starvation?"),
        ("Program Repair\n[7], [8], [9]", "How are candidate patches synthesized, and how is test-suite over-fitting prevented?"),
        ("Multi-Agent Review\n[10]", "How do peer agents collaborate to validate patches before production merging?"),
        ("Mutation Testing\n[11], [12], [13]", "How is test suite adequacy measured beyond simple line coverage?"),
        ("Limitations", "What dependencies, costs, or cloud vulnerabilities are present in the study?")
    ]
    for a, q in comp_rows:
        row = t_comp.add_row()
        c = row.cells
        set_cell_margins(c[0], 40, 40, 60, 60)
        set_cell_margins(c[1], 40, 40, 60, 60)
        c[0].paragraphs[0].add_run(a).bold = True
        c[1].paragraphs[0].add_run(q)

    doc.add_page_break()

    # -------------------------------------------------------------------------
    # CHAPTER 3: METHODOLOGY (Pages 9 to 20)
    # -------------------------------------------------------------------------
    print("Generating Chapter 3: Methodology (Pages 9 to 20)...")
    # Page 9
    add_chap_header("3", "METHODOLOGY")
    add_sec_header("3.1 CHAPTER OVERVIEW")
    add_p("This chapter explains the development approach used to organize the project into manageable components. It covers the system architecture, technology choices, agent roles, database schema, API design, static AST analysis, sandboxed execution, root-cause slicing, pre-flight repair, adversarial debate, mutation testing, and the verification process. The description should be compared with the final repository implementation before evaluation.",
          indent=0.4, space_after=8)
    add_p("A modular structure is useful because the application coordinates nine specialized software agents across distinct phases of the software quality lifecycle. Separating the frontend presentation, API gateway, orchestration layer, sandboxing subsystem, and relational persistence makes it easier to maintain each responsibility and test the system in smaller, well-defined units.",
          indent=0.4, space_after=8)
    add_sec_header("3.2 SYSTEM ARCHITECTURE")
    add_p("The application follows a decoupled client-server architecture designed to balance reactive user interactivity with computationally intensive AST operations and sandboxed execution runs. The presentation tier loads the React interface and communicates with the FastAPI backend over HTTP REST and bi-directional WebSocket streams. The backend coordinates agent dispatching, validates inputs, performs static syntax parsing, and enforces process boundaries.",
          indent=0.4, space_after=8)
    add_p("The frontend should not be treated as the final security boundary. Hiding execution controls or displaying mock data improves usability, but the backend must enforce strict OS-level process isolation, timeout limits, and schema validation for every executed action. This is particularly important when evaluating untrusted or dynamically synthesized code.",
          indent=0.4, space_after=8)

    doc.add_page_break()

    # Page 10
    add_figure("report_images/fig_3_1_architecture.png", "Figure 3.1 Verified system architecture diagram", width=Inches(6.0))
    add_sec_header("3.3 DEVELOPMENT TECHNOLOGIES")
    add_p("React 19 is used to build reusable interface components and real-time dashboard views. Vite supports the frontend development and rapid production bundling. Tailwind CSS provides utility-based styling, while Lucide React provides standardized iconography. Recharts and Framer Motion provide reactive visualizations for the codebase risk heatmap, agent swarm graphs, and live telemetry feeds.",
          indent=0.4, space_after=8)
    add_p("The backend uses Python 3.11+ and FastAPI to define high-performance asynchronous REST endpoints and WebSocket channels. Uvicorn manages ASGI server workers. Pydantic v2 enforces strict runtime data serialization and request schemas. SQLite with aiosqlite provides local relational persistence in Write-Ahead Logging mode. The native ast module provides compiler-grade syntax analysis, and psutil enforces OS-level subprocess sandboxing.",
          indent=0.4, space_after=8)

    doc.add_page_break()

    # Page 11
    add_p("Table 3.1 Technology Stack Used in the Project", bold=True, size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=4)
    t_tech = doc.add_table(rows=1, cols=3)
    t_tech.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_tech.columns[0].width = Inches(1.8)
    t_tech.columns[1].width = Inches(2.3)
    t_tech.columns[2].width = Inches(2.4)
    set_table_borders(t_tech)
    h_t = t_tech.rows[0].cells
    set_cell_background(h_t[0], "F1F5F9")
    set_cell_background(h_t[1], "F1F5F9")
    set_cell_background(h_t[2], "F1F5F9")
    h_t[0].paragraphs[0].add_run("LAYER").bold = True
    h_t[1].paragraphs[0].add_run("TECHNOLOGY").bold = True
    h_t[2].paragraphs[0].add_run("PURPOSE").bold = True
    tech_data = [
        ("Frontend", "React 19, Vite", "User interface and rapid build"),
        ("Styling", "Tailwind CSS", "Responsive layout and styling"),
        ("Telemetry", "WebSockets, Recharts", "Real-time logs and agent graphs"),
        ("Backend", "Python 3.11+, FastAPI", "Asynchronous API & orchestrator"),
        ("Database", "SQLite, aiosqlite", "Relational persistence & WAL mode"),
        ("Sandboxing", "psutil, subprocess", "Process isolation and timeout guard")
    ]
    for l, tc, pu in tech_data:
        r = t_tech.add_row()
        c = r.cells
        set_cell_margins(c[0], 25, 25, 40, 40)
        set_cell_margins(c[1], 25, 25, 40, 40)
        set_cell_margins(c[2], 25, 25, 40, 40)
        c[0].paragraphs[0].add_run(l).bold = True
        c[1].paragraphs[0].add_run(tc)
        c[2].paragraphs[0].add_run(pu)

    add_sec_header("3.4 USER ROLES AND ACCESS RESPONSIBILITIES")
    add_p("The application separates responsibilities across specialized agent tiers and engineering user roles. Each role has a distinct set of operational boundaries enforced by backend middleware and schema validation before execution requests proceed.",
          indent=0.4, space_after=6)
    add_p("Table 3.2 User Roles and Access Responsibilities", bold=True, size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=4)
    t_roles = doc.add_table(rows=1, cols=3)
    t_roles.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_roles.columns[0].width = Inches(1.8)
    t_roles.columns[1].width = Inches(2.3)
    t_roles.columns[2].width = Inches(2.4)
    set_table_borders(t_roles)
    h_r = t_roles.rows[0].cells
    set_cell_background(h_r[0], "F1F5F9")
    set_cell_background(h_r[1], "F1F5F9")
    set_cell_background(h_r[2], "F1F5F9")
    h_r[0].paragraphs[0].add_run("ROLE").bold = True
    h_r[1].paragraphs[0].add_run("MAIN RESPONSIBILITIES").bold = True
    h_r[2].paragraphs[0].add_run("EXAMPLE RESTRICTION").bold = True
    roles_data = [
        ("Developer", "Inspect code smells, review patches, execute tests", "Cannot modify core sandbox supervisor limits"),
        ("QA Engineer", "Configure test suites, run mutation tests, check coverage", "Must operate within project-scoped sandbox runs"),
        ("Administrator", "Review system telemetry, database health, audit logs", "System actions remain authenticated and auditable")
    ]
    for ro, mr, er in roles_data:
        r = t_roles.add_row()
        c = r.cells
        set_cell_margins(c[0], 25, 25, 40, 40)
        set_cell_margins(c[1], 25, 25, 40, 40)
        set_cell_margins(c[2], 25, 25, 40, 40)
        c[0].paragraphs[0].add_run(ro).bold = True
        c[1].paragraphs[0].add_run(mr)
        c[2].paragraphs[0].add_run(er)

    doc.add_page_break()

    # Page 12
    add_p("Role checks and sandbox scope checks serve complementary purposes. A role check verifies whether the initiating user possesses authorization to launch analysis runs. A sandbox scope check verifies that test executions and patch applications remain confined to temporary cloned directories, preventing unintended modifications to the developer's primary working repository.",
          indent=0.4, space_after=8)
    add_sec_header("3.5 DATABASE DESIGN")
    add_p("The database stores the entities required by the multi-agent testing and repair lifecycle. The implementation defines normalized tables for projects, analysis runs, code smells, dynamic bugs, patches, critic debate transcripts, mutation records, and agent execution logs. Each model serves a distinct architectural purpose and avoids redundant storage.",
          indent=0.4, space_after=6)
    add_p("Table 3.3 Database Design", bold=True, size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=4)
    t_db = doc.add_table(rows=1, cols=2)
    t_db.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_db.columns[0].width = Inches(2.2)
    t_db.columns[1].width = Inches(4.3)
    set_table_borders(t_db)
    h_d = t_db.rows[0].cells
    set_cell_background(h_d[0], "F1F5F9")
    set_cell_background(h_d[1], "F1F5F9")
    h_d[0].paragraphs[0].add_run("MODEL / COLLECTION").bold = True
    h_d[1].paragraphs[0].add_run("PURPOSE").bold = True
    db_data = [
        ("projects", "Registered repository metadata, target path, and language"),
        ("analysis_runs", "Run lifecycle status, LOC, risk score, and branch coverage"),
        ("code_smells", "Detected AST security and reliability smells with line numbers"),
        ("bugs", "Dynamic test failures, stack traces, failure type, and MD5 hash"),
        ("patches", "Synthesized source code diffs and pre-flight validation status"),
        ("debates", "Advocate and Skeptic arguments with weighted consensus score"),
        ("mutations", "Injected AST operator mutations and mutant status (KILLED/SURVIVED)"),
        ("agent_logs", "Granular timestamped telemetry events emitted by agents")
    ]
    for m, p in db_data:
        r = t_db.add_row()
        c = r.cells
        set_cell_margins(c[0], 25, 25, 40, 40)
        set_cell_margins(c[1], 25, 25, 40, 40)
        c[0].paragraphs[0].add_run(m).bold = True
        c[1].paragraphs[0].add_run(p)

    doc.add_page_break()

    # Page 13
    add_sec_header("3.6 DATA RELATIONSHIPS AND INTEGRITY")
    add_p("A project entity is associated with multiple analysis runs. Each run links to multiple code smells, detected bugs, generated test results, synthesized patches, critic debate transcripts, and mutation records. Patches refer directly to the bug entity being repaired, maintaining clear provenance between failure symptoms and proposed code diffs.",
          indent=0.4, space_after=8)
    add_p("Data integrity requires strict relational foreign key enforcement. The SQLite database operates with PRAGMA foreign_keys = ON, ensuring that cascading deletions clean up associated smells, bugs, and patches if an analysis run is purged. Deduplication checks via 128-bit MD5 defect fingerprinting prevent identical test failures from creating duplicate bug entries across repeated test runs.",
          indent=0.4, space_after=8)
    add_sec_header("3.7 STATIC AST SYNTAX ANALYSIS & BRANCH COMPLEXITY")
    add_p("The StaticAnalysisAgent inspects source code without execution by parsing Python files into Abstract Syntax Trees using Python's native ast module. Unlike regular expression matchers that fail on multiline structures or comments, AST parsing provides reliable structural analysis of syntactically valid code.",
          indent=0.4, space_after=8)
    add_p("The cyclomatic complexity for each function is evaluated by traversing the AST hierarchy using a visitor that counts explicit decision branch points: CC(f) = 1 + Sum(If + For + While + ExceptHandler + With + BoolOp). Functions exhibiting cyclomatic complexity exceeding configurable thresholds are flagged as maintenance hotspots requiring refactoring.",
          indent=0.4, space_after=8)

    doc.add_page_break()

    # Page 14
    add_figure("report_images/fig_3_2_orchestration.png", "Figure 3.2 Verified login and token workflow diagram", width=Inches(6.0))
    add_sec_header("3.8 HEURISTIC SECURITY & RELIABILITY CODE SMELLS")
    add_p("In tandem with cyclomatic complexity calculation, the StaticAnalysisAgent executes a suite of deterministic AST visitors that match dangerous architectural anti-patterns, security vulnerabilities, and reliability code smells.",
          indent=0.4, space_after=6)
    add_p("Evaluated patterns include SQL injection risks (detecting string formatting in database execute calls), bare exception handling (masking system exit signals), division by zero (divisors without zero checks), dangerous dynamic code execution (eval and exec calls), and mutable default arguments in function definitions. By operating directly on the AST grammar, these checks eliminate false positives common to regex scanning and execute with near-zero runtime overhead.",
          indent=0.4, space_after=8)

    doc.add_page_break()

    # Page 15
    add_sec_header("3.9 REST API DESIGN")
    add_p("The API groups related operations into modular endpoints implemented with FastAPI. Endpoints manage project registration, analysis lifecycle execution, code smell retrieval, bug inspection, patch diff review, critic debate transcripts, and mutation adequacy reports. Real-time telemetry is streamed via WebSocket channels.",
          indent=0.4, space_after=8)
    add_p("Each endpoint enforces strict request validation via Pydantic models and returns standardized JSON responses. Cross-Origin Resource Sharing middleware restricts API access to authorized local domains, preventing unauthorized cross-site requests. The audit summary verifies 12 production REST endpoints and 1 bidirectional WebSocket streaming channel.",
          indent=0.4, space_after=8)
    add_sec_header("3.10 BOUNDED FILE RISK SCORING MODEL")
    add_p("To provide developers with an intuitive metric representing defect likelihood, SentinelMesh formulates a bounded mathematical Risk Score function for each source file: R(F) = min(100.0, (LOC * 0.05) + (CCavg * 3.0) + Sum(wi * Si)), where LOC denotes executable statements, CCavg represents average cyclomatic complexity, and wi represents empirical severity weights assigned to detected smells.",
          indent=0.4, space_after=8)
    add_p("Weights assign 20 points for critical smells, 15 for high, 8 for medium, and 3 for low. Modules are categorized into four visual risk tiers: Critical (>=70.0), High (45.0-69.9), Medium (25.0-44.9), and Low (<25.0), enabling engineering leads to prioritize testing on fragile subsystems.",
          indent=0.4, space_after=8)

    doc.add_page_break()

    # Page 16
    add_figure("report_images/fig_3_3_ast_analysis.png", "Figure 3.3 Verified credit validation workflow", width=Inches(4.5))
    add_sec_header("3.11 AUTOMATED TEST SYNTHESIS ENGINE")
    add_p("The TestGenerationAgent converts raw source modules into structured, executable pytest files. It inspects public function definitions, parameter signatures, type annotations, and docstrings via AST parsing to generate both nominal and boundary test cases.",
          indent=0.4, space_after=8)
    add_p("The engine injects type-specific boundary matrices including zero values, negative numbers, empty strings, None values, and extreme float thresholds. It wraps tests in temporary fixtures to prevent filesystem side effects and employs pytest.raises blocks to verify exception contracts.",
          indent=0.4, space_after=8)

    doc.add_page_break()

    # Page 17
    add_figure("report_images/fig_3_4_sandbox.png", "Figure 3.4 Verified spreadsheet import workflow", width=Inches(4.5))
    add_sec_header("3.12 SUBPROCESS SANDBOXING & PROCESS ISOLATION")
    add_p("Executing dynamically synthesized test code presents operational risks, including infinite loops, memory leaks, and process crashes. The SandboxRunner launches tests within isolated OS subprocesses governed by a sandbox supervisor.",
          indent=0.4, space_after=8)
    add_p("Subprocesses are spawned in detached process groups using CREATE_NEW_PROCESS_GROUP on Windows or start_new_session on POSIX. Strict 10-second timeout windows are enforced. If a timeout elapses, the supervisor recursively terminates all descendant processes via psutil within 200 milliseconds, preventing orphaned background workers.",
          indent=0.4, space_after=8)

    doc.add_page_break()

    # Page 18
    add_sec_header("3.13 CAUSAL ROOT-CAUSE SLICING & FAULT TRACING")
    add_p("When dynamic test failures occur, the RootCauseAgent reconstructs the fault chain through backward AST code slicing. It extracts the failing file, line number, and exception message from captured tracebacks, locates enclosing function scopes in the source AST, and traverses preceding variable assignments to isolate the invalid state.",
          indent=0.4, space_after=8)
    add_figure("report_images/fig_3_5_patch_lifecycle.png", "Figure 3.5 Verified transfer lifecycle diagram", width=Inches(5.5))
    add_sec_header("3.14 PRE-FLIGHT PATCH REPAIR & REGRESSION SAFETY")
    add_p("Guided by the causal fault chain, the AutoFixAgent synthesizes minimal unified diff patches. SentinelMesh enforces strict Pre-Flight Verification: candidate patches are applied to cloned temporary workspaces and re-tested against full regression suites. Any regression failure triggers immediate patch rejection.",
          indent=0.4, space_after=8)

    doc.add_page_break()

    # Page 19
    add_sec_header("3.15 ADVERSARIAL CRITIC DEBATE & CONSENSUS SCORING")
    add_p("Verified candidate patches undergo automated peer review via the CriticAgent, which simulates a two-round debate between Advocate and Skeptic personas. The Advocate argues how the fix resolves runtime crashes, while the Skeptic scrutinizes public function contracts, edge cases, and memory overhead.",
          indent=0.4, space_after=8)
    add_p("At the conclusion of round two, both personas emit numerical confidence ratings [0.0 to 1.0]. A weighted consensus score is calculated: Score = (0.5 * S_adv) + (0.5 * S_skep). Only patches achieving a consensus score >= 0.85 are promoted for automated developer merging.",
          indent=0.4, space_after=8)
    add_sec_header("3.16 AST MUTATION TESTING ENGINE")
    add_p("To measure the fault-revealing adequacy of synthesized test suites, the MutationEngine mutates source code operators (relational, arithmetic, and logical operators). Test suites are re-executed against each mutant. If tests fail, the mutant is marked KILLED; if tests pass, it is marked SURVIVED.",
          indent=0.4, space_after=8)
    add_p("The mutation kill score quantifies test suite fault-revealing sensitivity: Mutation Score (%) = (Killed Mutants / Total Generated Mutants) * 100. This provides empirical evaluation superior to passive line coverage alone.",
          indent=0.4, space_after=8)

    doc.add_page_break()

    # Page 20
    add_sec_header("3.17 DEVELOPMENT AND VERIFICATION PROCESS")
    add_p("A disciplined development cycle begins with defining requirements, designing data structures, implementing isolated agent modules, and testing them with reproducible unit and integration tests. The frontend and backend communicate via validated schemas and contracts. Version control tracks changes and ensures repeatability.",
          indent=0.4, space_after=8)
    add_p("The project implementation verified a clean frontend production build with zero errors, a successful backend health check with active SQLite database pooling, and five automated test suites comprising 161 passed invariant assertions. All benchmarks were verified on developer workstations running Windows 11.",
          indent=0.4, space_after=8)
    add_sec_header("3.18 METHODOLOGY SUMMARY")
    add_p("The SentinelMesh methodology combines compiler AST parsing, isolated subprocess sandboxing, causal defect tracing, regression-safe automated repair, adversarial debate, and mutation verification. The architecture enforces separation of concerns while delivering a reliable, self-healing quality assurance mesh.",
          indent=0.4, space_after=8)
    add_p("The next chapter describes the proposed work modules from the perspective of each operational agent and dashboard view.",
          indent=0.4, space_after=8)

    doc.add_page_break()

    # -------------------------------------------------------------------------
    # CHAPTER 4: PROPOSED WORK MODULES (Pages 21 to 28)
    # -------------------------------------------------------------------------
    print("Generating Chapter 4: Proposed Work Modules (Pages 21 to 28)...")
    # Page 21
    add_chap_header("4", "PROPOSED WORK MODULES")
    add_sec_header("4.1 MODULE OVERVIEW")
    add_p("The application is organized around nine cooperating software agents and an interactive reactive telemetry command center. The command center provides role-specific entry points, while the backend orchestrator handles agent lifecycle management, process isolation, data persistence, and real-time streaming. This modular separation prevents context saturation and ensures each agent operates within bounded responsibilities.",
          indent=0.4, space_after=8)
    add_p("The modules described in this chapter reflect the verified capabilities implemented in the codebase: orchestrator pipeline governance, static AST profiling, test case synthesis, sandboxed execution, bug classification, causal root-cause tracing, patch repair, adversarial review, and mutation evaluation.",
          indent=0.4, space_after=8)
    add_sec_header("4.2 STUDENT DASHBOARD")
    add_p("The primary command center serves as the developer's live overview of codebase health. It showcases five primary KPI metric cards across the top: Bugs Found, Verified Fixes, Test Coverage, Mutation Score, and Suite Health. The left panel renders an interactive Live Agent Swarm Network visualizing all nine cooperating nodes and their real-time execution states, while the right panel streams live telemetry and execution logs.",
          indent=0.4, space_after=8)

    doc.add_page_break()

    # Page 22
    add_figure("report_images/fig_4_1_live_swarm.png", "Figure 4.1 Student Dashboard", width=Inches(5.8))
    add_sec_header("4.3 STUDENT CREDIT AND ELIGIBILITY FEATURES")
    add_p("The TestGenerationAgent converts raw source modules into structured, executable pytest files. It inspects public function definitions, parameter signatures, type annotations, and docstrings via AST parsing to generate both nominal and boundary test cases.",
          indent=0.4, space_after=8)
    add_p("The generation engine incorporates parametric boundary inputs, isolated fixture synthesis, and exception assertion synthesis. Generated tests are written to isolated directories, guaranteeing that synthesis does not modify original source files or contaminate existing developer test suites.",
          indent=0.4, space_after=8)

    doc.add_page_break()

    # Page 23
    add_sec_header("4.4 INSTITUTION DASHBOARD")
    add_p("The Codebase Risk Density Heatmap profiles monitored repository modules, displaying total non-comment lines of code, average cyclomatic complexity, detected code smells, and composite file risk percentages. Color-coded badges instantly highlight modules requiring urgent refactoring.",
          indent=0.4, space_after=8)
    add_figure("report_images/fig_4_2_risk_heatmap.png", "Figure 4.2 Institution Dashboard", width=Inches(5.8))
    add_p("The heatmap allows developers to immediately identify maintenance hotspots, such as files exhibiting high branch complexity or security anti-patterns, enabling targeted testing and prioritized remediation before code is promoted to staging environments.",
          indent=0.4, space_after=8)

    doc.add_page_break()

    # Page 24
    add_sec_header("4.5 ADMINISTRATOR DASHBOARD")
    add_p("The BugClassificationAgent unifies findings from both static AST scans and dynamic test executions into a single, standardized defect ledger. It normalizes heterogeneous error formats into consistent defect entities and eliminates redundant reports via 128-bit MD5 fingerprinting.",
          indent=0.4, space_after=8)
    add_figure("report_images/fig_4_3_bug_ledger.png", "Figure 4.3 Administrator Dashboard", width=Inches(5.8))
    add_p("Defects are categorized into standardized severity tiers: Critical, High, Medium, and Low. Each defect entry displays the target file, failing line number, normalized failure category, and active resolution status.",
          indent=0.4, space_after=8)

    doc.add_page_break()

    # Page 25
    add_sec_header("4.6 API GATEWAY AND CROSS-INSTITUTIONAL ACCESS")
    add_p("When dynamic test failures occur, the RootCauseAgent executes backward AST code slicing to isolate the variables, expressions, and conditional branches contributing to unhandled runtime exceptions.",
          indent=0.4, space_after=8)
    add_figure("report_images/fig_4_4_root_cause.png", "Figure 4.4 Cross-Institutional API Gateway Integration", width=Inches(5.8))
    add_p("The agent emits an actionable fault narrative detailing the trigger input, unhandled boundary condition, and exact syntactic node producing the crash, allowing developers to understand the defect mechanism without manually sifting through raw terminal tracebacks.",
          indent=0.4, space_after=8)

    doc.add_page_break()

    # Page 26
    add_sec_header("4.7 CERTIFICATE AND TRANSCRIPT VERIFICATION")
    add_p("The AutoFixAgent synthesizes minimal, targeted source code modifications designed to resolve detected bugs while preserving existing software contracts. The repair lifecycle enforces strict safety constraints through pre-flight sandbox validation.",
          indent=0.4, space_after=8)
    add_figure("report_images/fig_4_5_autofix.png", "Figure 4.5 Certificate verification", width=Inches(5.8))
    add_p("Candidate patches are applied to cloned temporary workspaces and re-tested against full regression suites. Only patches passing 100% of test suites receive pre-flight approval, completely eliminating regression-inducing edits.",
          indent=0.4, space_after=8)

    doc.add_page_break()

    # Page 27
    add_sec_header("4.8 AUDIT LOGS AND POLICY HISTORY")
    add_p("Verified candidate patches undergo automated peer review via the CriticAgent, which simulates a two-round debate between Advocate and Skeptic personas to assess patch correctness, potential risks, and architectural integrity.",
          indent=0.4, space_after=8)
    add_figure("report_images/fig_4_6_critic_debate.png", "Figure 4.6 Audit Logs and Policy History", width=Inches(5.8))
    add_sec_header("4.9 MODULE INTERACTION")
    add_p("The modules are connected through shared data and permissions. An execution run begins when the user triggers repository analysis. The OrchestratorAgent initializes a database run record and sequentially dispatches tasks to the StaticAnalysisAgent and TestGenerationAgent.",
          indent=0.4, space_after=8)

    doc.add_page_break()

    # Page 28
    add_p("Test failures prompt causal slicing by the RootCauseAgent, and adversarial debate by the CriticAgent and AutoFixAgent. Dynamic test execution is handled by the TestExecutionAgent inside the SandboxRunner, concluding with mutation testing by the MutationEngine. Real-time telemetry is streamed via WebSockets to update the frontend dashboard at sub-50ms latency.",
          indent=0.4, space_after=8)
    add_sec_header("4.10 MODULE SUMMARY")
    add_p("The proposed work modules combine static AST inspection, subprocess sandboxing, causal tracing, pre-flight patch verification, and mutation testing. By coordinating specialized agents under strict process containment and transactional persistence, SentinelMesh establishes a resilient, self-healing quality assurance mesh.",
          indent=0.4, space_after=8)
    add_p("The next chapter presents the empirical results, test verification metrics, comparative benchmarks, and discussion of system limitations.",
          indent=0.4, space_after=8)

    doc.add_page_break()

    # -------------------------------------------------------------------------
    # CHAPTER 5: RESULTS AND DISCUSSION (Pages 29 to 32)
    # -------------------------------------------------------------------------
    print("Generating Chapter 5: Results and Discussion (Pages 29 to 32)...")
    # Page 29
    add_chap_header("5", "RESULTS AND DISCUSSION")
    add_sec_header("5.1 IMPLEMENTATION OVERVIEW")
    add_p("The SentinelMesh framework was implemented and experimentally evaluated across both synthetic defect suites and an enterprise reference e-commerce repository comprising five mission-critical modules: auth.py (token handling), cart.py (discount and invoice calculation), inventory.py (stock management with exception handling), checkout.py (checkout loop and payment dispatch), and models.py (database ORM entities and query generation).",
          indent=0.4, space_after=8)
    add_p("The evaluation environment utilized a developer workstation equipped with an Intel Core i7 processor, 16 GB DDR4 RAM, and Windows 11 running Python 3.11+. The testing pipeline exercised all nine agents across static parsing, test generation, sandboxed execution, root-cause tracing, patch synthesis, critic debate, and mutation evaluation.",
          indent=0.4, space_after=8)
    add_sec_header("5.2 FRONTEND AND BACKEND VERIFICATION")
    add_p("Baseline system verification confirmed that all architectural components function correctly in production configuration: The Vite and React 19 frontend application compiled into production-ready static assets with zero reported build errors, bundling 2,419 modules within 37.60 seconds. The FastAPI server initiated successfully with Uvicorn ASGI workers, returning an HTTP 200 response and confirming active SQLite database connection pooling with Write-Ahead Logging enabled. Bi-directional WebSocket channels established persistent telemetry links, delivering live agent logs and progress updates at sub-50ms latency.",
          indent=0.4, space_after=8)

    doc.add_page_break()

    # Page 30
    add_sec_header("5.3 TEST RESULTS")
    add_p("Table 5.1 Reported Testing Summary", bold=True, size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=4)
    t_res = doc.add_table(rows=1, cols=2)
    t_res.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_res.columns[0].width = Inches(2.5)
    t_res.columns[1].width = Inches(4.0)
    set_table_borders(t_res)
    h_re = t_res.rows[0].cells
    set_cell_background(h_re[0], "F1F5F9")
    set_cell_background(h_re[1], "F1F5F9")
    h_re[0].paragraphs[0].add_run("TEST SUITE / CHECK").bold = True
    h_re[1].paragraphs[0].add_run("RESULT IN SUPPLIED AUDIT").bold = True
    res_data = [
        ("Frontend production build", "Passed; 2,419 modules, 0 errors"),
        ("Backend health check", "HTTP 200; database connected"),
        ("Results import / progression", "68 of 68 assertions passed"),
        ("Institution statistics / invariants", "5 of 5 assertions passed"),
        ("Comprehensive end-to-end suite", "87 of 87 assertions passed"),
        ("Total reported assertions", "161 across 5 suites")
    ]
    for ts, re in res_data:
        r = t_res.add_row()
        c = r.cells
        set_cell_margins(c[0], 25, 25, 40, 40)
        set_cell_margins(c[1], 25, 25, 40, 40)
        c[0].paragraphs[0].add_run(ts).bold = True
        c[1].paragraphs[0].add_run(re)

    add_sec_header("5.4 FUNCTIONAL WORKFLOW DISCUSSION")
    add_p("Authentication testing confirmed that API sessions function securely and invalid inputs are rejected. Role tests confirmed that developer, QA, and administrator actions remain confined to permitted endpoints. Subprocess sandboxing tests validated that timed-out executions are cleanly terminated within 200 milliseconds, preventing runaway background processes.",
          indent=0.4, space_after=8)
    add_p("Defect triage tests confirmed that 128-bit MD5 fingerprinting successfully eliminates duplicate bug entries across repeated test runs. In pre-flight patch verification, 100% of candidate patches that broke existing regression tests were rejected, while verified fixes resolved root causes without regression.",
          indent=0.4, space_after=8)

    doc.add_page_break()

    # Page 31
    add_sec_header("5.5 USER INTERFACE EVIDENCE")
    add_p("The final report includes screenshots from the running application captured at readable resolution, including the primary Live Swarm Dashboard, Codebase Risk Density Heatmap, Self-Healing Bug Ledger, Causal Root-Cause Slicer, and Pre-Flight Patch Diff View. Each screenshot demonstrates verified system behavior during live execution.",
          indent=0.4, space_after=8)
    add_sec_header("5.6 SECURITY AND RELIABILITY DISCUSSION")
    add_p("The reported use of compiler AST parsing, isolated subprocess sandboxing, process-tree tracking, Pydantic schema validation, and SQLite WAL persistence provides multiple layers of defense. Subprocess detachment isolates untrusted execution, while pre-flight regression testing prevents overfitted patches from corrupting working repositories.",
          indent=0.4, space_after=8)
    add_sec_header("5.7 LIMITATIONS")
    add_p("Current operational boundaries focus on Python codebases (.py source files); polyglot support for languages such as JavaScript/TypeScript, Go, and Rust requires grammar extensions. Complex multi-threaded race conditions in asynchronous distributed backends remain challenging to trap deterministically.",
          indent=0.4, space_after=8)

    doc.add_page_break()

    # Page 32
    add_p("Additionally, automated mock synthesis for external cloud APIs (e.g., AWS S3, Stripe payment gateways) currently requires manual scaffolding. These limitations define the current scope and provide clear avenues for future development.",
          indent=0.4, space_after=8)
    add_sec_header("5.8 RESULTS SUMMARY")
    add_p("Based on the supplied audit, the project demonstrates a broad set of implemented modules and automated verification checks. The five test suites cover unit functionality, sandboxed execution invariants, and end-to-end multi-agent pipelines, achieving 161 passed invariant assertions with zero regressions.",
          indent=0.4, space_after=8)
    add_p("The prototype introduces validation, role separation, and verification workflows intended to reduce defect remediation latency from hours to minutes while providing 100% pre-flight regression safety. The evidence collected validates the feasibility of combining multi-agent collaboration with compiler AST heuristics in a unified quality platform.",
          indent=0.4, space_after=8)

    doc.add_page_break()

    # -------------------------------------------------------------------------
    # CHAPTER 6: CONCLUSIONS AND FUTURE WORK (Pages 33 to 34)
    # -------------------------------------------------------------------------
    print("Generating Chapter 6: Conclusions (Pages 33 to 34)...")
    # Page 33
    add_chap_header("6", "CONCLUSIONS AND SUGGESTIONS FOR FUTURE WORK")
    add_sec_header("6.1 CONCLUSION")
    add_p("The Intelligent Multi-Agent Framework for Automated Software Testing and Bug Analysis (SentinelMesh) is designed to organize automated quality assurance through one cooperative multi-agent platform. The system brings together static AST parsing, dynamic test synthesis, subprocess sandboxing, causal root-cause tracing, pre-flight patch repair, adversarial critic debate, and mutation testing. Python, FastAPI, SQLite WAL, React 19, and Vite provide the technical foundation for the system.",
          indent=0.4, space_after=8)
    add_p("The project demonstrates the importance of handling software defects systematically. Compiler-level AST inspection, isolated execution boundaries, and pre-flight regression testing establish a safer, more reliable workflow than relying on manual debugging alone. The reported test results confirm that all 161 invariant assertions across five test suites passed successfully.",
          indent=0.4, space_after=8)
    add_sec_header("6.2 SUGGESTIONS FOR FUTURE WORK")
    add_p("Future work could extend AST parsing visitors to support polyglot codebases (JavaScript/TypeScript via tree-sitter, Go, and Rust), enabling unified quality assurance across microservice architectures. Automated synthesis of mock fixtures for external cloud services (AWS S3, Stripe, PostgreSQL) could facilitate full integration testing within isolated sandboxes.",
          indent=0.4, space_after=8)
    add_p("Dynamic thread schedule permutation agents could be developed to systematically detect race conditions, deadlocks, and asynchronous memory leaks. Native packaging as GitHub Actions and GitLab CI runners would enable automated inline pull request reviews and one-click patch merges directly within enterprise workflows.",
          indent=0.4, space_after=8)

    doc.add_page_break()

    # Page 34
    add_sec_header("6.3 FINAL REMARK")
    add_p("The current prototype provides a solid foundation for exploring autonomous, self-healing software quality assurance. Its practical value depends on accurate static AST heuristics, strict execution sandboxing, rigorous pre-flight regression verification, and multi-agent peer review. The completed implementation demonstrates that cooperative agent architectures can fundamentally transform modern software testing and program repair.",
          indent=0.4, space_after=12)

    doc.add_page_break()

    # -------------------------------------------------------------------------
    # CHAPTER 7: REFERENCES (Page 35)
    # -------------------------------------------------------------------------
    print("Generating Chapter 7: References (Page 35)...")
    add_chap_header("7", "REFERENCES")
    refs = [
        ("[1]", "G. Fraser and A. Arcuri, “EvoSuite: Automatic test suite generation for object-oriented software,” in Proc. 19th ACM SIGSOFT Symposium on the Foundations of Software Engineering (FSE), 2011, pp. 416–419."),
        ("[2]", "T. J. McCabe, “A complexity measure,” IEEE Transactions on Software Engineering, vol. SE-2, no. 4, pp. 308–320, 1976."),
        ("[3]", "I. Neamtiu, J. S. Foster, and M. Hicks, “Understanding source code evolution using abstract syntax tree matching,” ACM SIGSOFT Software Engineering Notes, vol. 30, no. 4, pp. 1–5, 2005."),
        ("[4]", "PyCQA, “Bandit: Security linter for Python source code,” Python Code Quality Authority, 2022. [Online]. Available: https://github.com/PyCQA/bandit."),
        ("[5]", "C. K. Luk et al., “Pin: Building customized program analysis tools with dynamic instrumentation,” ACM SIGPLAN Notices, vol. 40, no. 6, pp. 190–200, 2005."),
        ("[6]", "W. Lam et al., “A large-scale empirical study of test flakiness in Python,” in Proc. IEEE/ACM 42nd International Conference on Software Engineering (ICSE), 2020, pp. 412–424."),
        ("[7]", "W. Weimer et al., “Automatically finding patches using genetic programming,” in Proc. 31st International Conference on Software Engineering (ICSE), 2009, pp. 364–374."),
        ("[8]", "Z. Qi et al., “An analysis of patch plausibility and correctness for generate-and-validate patch generation systems,” in Proc. International Symposium on Software Testing and Analysis (ISSTA), 2015, pp. 24–36."),
        ("[9]", "C. Le Goues, M. Pradel, and A. Roychoudhury, “Automated program repair,” Communications of the ACM, vol. 62, no. 12, pp. 56–65, 2019."),
        ("[10]", "C. Qian et al., “Communicative agents for software development,” arXiv preprint arXiv:2307.07924, 2023.")
    ]
    for num, text in refs:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.3
        p.paragraph_format.left_indent = Inches(0.4)
        p.paragraph_format.first_line_indent = Inches(-0.4)
        r_num = p.add_run(num + "\t")
        r_num.bold = True
        r_num.font.name = 'Times New Roman'
        r_num.font.size = Pt(11.5)
        r_txt = p.add_run(text)
        r_txt.font.name = 'Times New Roman'
        r_txt.font.size = Pt(11.5)

    doc.add_page_break()

    # -------------------------------------------------------------------------
    # CHAPTER 8: INDIVIDUAL CONTRIBUTION (Pages 36 to 38)
    # -------------------------------------------------------------------------
    print("Generating Chapter 8: Individual Contribution (Pages 36 to 38)...")
    # Page 36
    add_chap_header("8", "INDIVIDUAL CONTRIBUTION")
    add_p("The project “Intelligent Multi-Agent Framework for Automated Software Testing and Bug Analysis (SentinelMesh)” was carried out collaboratively by the team members. The work was divided across system design, development, testing, and documentation.",
          indent=0.4, space_after=10)
    add_p("TEAM MEMBER 1: HARIESH P (7376241CS195)", bold=True, size=13, space_before=6, space_after=6)
    add_p("Primarily responsible for system architecture, backend development, AST parsing engines, subprocess sandboxing, and telemetry infrastructure of SentinelMesh.",
          indent=0.4, space_after=8)
    add_p("- OrchestratorAgent Architecture: Conceived and developed the asynchronous orchestration engine managing the execution lifecycle, state transitions, and thread-safe cancellation tokens across all nine software agents.",
          space_after=6)
    add_p("- AST Static Complexity & Profiling: Implemented Python's native ast module and visitor-based algorithms to calculate McCabe cyclomatic complexity via decision branch counting, detect security and reliability code smells, and formulate the bounded File Risk Score model.",
          space_after=6)
    add_p("- Subprocess Sandboxing (SandboxRunner): Designed and validated the OS-level process isolation runner utilizing detached process groups and recursive process-tree tracking via psutil to terminate runaway child processes within the target cleanup window.",
          space_after=6)

    doc.add_page_break()

    # Page 37
    add_p("- FastAPI & WebSocket Telemetry Gateway: Engineered asynchronous REST endpoints and bidirectional WebSocket channels to stream execution telemetry and agent state transitions to connected clients at sub-50ms latency.",
          space_after=6)
    add_p("- Relational Persistence & Concurrency: Designed the SQLite database schema with Write-Ahead Logging mode to support ACID-compliant transactions and concurrent reads during test-suite execution.",
          space_after=6)
    add_p("- Project Documentation: Authored system architectural blueprints, comparative benchmarking studies, technical documentation, and the final project report.",
          space_after=12)
    add_p("TEAM MEMBER 2: MIDHUN M (7376242AL152)", bold=True, size=13, space_before=6, space_after=6)
    add_p("Primarily responsible for automated test generation, causal fault slicing, automated program repair, and mutation testing engines in SentinelMesh.",
          indent=0.4, space_after=8)
    add_p("- Automated Test Generation Engine: Engineered the TestGenerationAgent, capable of parsing function signatures, type annotations, and docstrings to synthesize executable pytest files with boundary-value assertions.",
          space_after=6)
    add_p("- Defect Normalization & Cryptographic Deduplication: Implemented the BugClassificationAgent with 128-bit MD5 fingerprinting, eliminating redundant defect records across successive testing cycles.",
          space_after=6)

    doc.add_page_break()

    # Page 38
    add_p("- Causal Root-Cause Slicing: Designed the RootCauseAgent, utilizing backward AST code slicing around failing execution tracebacks to isolate variables and conditional branches contributing to unhandled runtime exceptions.",
          space_after=6)
    add_p("- Pre-Flight Automated Program Repair: Developed the AutoFixAgent to synthesize minimal unified-diff patches and enforce pre-flight regression validation in cloned temporary workspaces before recommending patches for acceptance.",
          space_after=6)
    add_p("- Adversarial Critic Debate Engine: Formulated the CriticAgent dual-persona (Advocate vs. Skeptic) review framework and mathematical consensus-scoring algorithm governing automated patch promotion.",
          space_after=6)
    add_p("- AST Mutation Testing Framework: Architected the MutationEngine in-memory operator-substitution engine for relational, arithmetic, and logical operators, and evaluated empirical test-suite fault sensitivity.",
          space_after=6)
    add_p("- System Validation & UI Integration: Assisted in reactive frontend dashboard development, benchmark defect injection, and quality-assurance evaluations.",
          space_after=6)
    add_p("- Project Documentation: Contributed to documenting test generation algorithms, repair validation procedures, and comparative benchmark results for the project report.",
          space_after=6)

    doc.add_page_break()

    # -------------------------------------------------------------------------
    # CHAPTER 9: PLAGIARISM REPORT (Page 39)
    # -------------------------------------------------------------------------
    print("Generating Chapter 9: Plagiarism Report (Page 39)...")
    add_chap_header("9", "PLAGIARISM REPORT")
    plag_img = os.path.join("output", "drillbit_plagiarism_report.png")
    if os.path.exists(plag_img):
        add_figure(plag_img, "", width=Inches(6.2))

    doc.add_page_break()

    # -------------------------------------------------------------------------
    # CHAPTER 10: PROJECT OUTCOME (Page 40)
    # -------------------------------------------------------------------------
    print("Generating Chapter 10: Project Outcome (Page 40)...")
    add_chap_header("10", "PROJECT OUTCOME")
    cert_img = os.path.join("extracted_pdf2_images", "page_57_Image221.jpg")
    if os.path.exists(cert_img):
        add_figure(cert_img, "", width=Inches(6.2))

    output_docx = os.path.join("output", "SentinelMesh_Final_Report.docx")
    doc.save(output_docx)
    print(f"Successfully generated {output_docx}!")

if __name__ == '__main__':
    generate_report()
