"""
fill_pptx.py -- Fills the BIT Second Review PPTX template with real SentinelMesh data.
Run: .venv\Scripts\python.exe project_report/fill_pptx.py
"""
import shutil, subprocess
from pathlib import Path
from lxml import etree

from pptx import Presentation
from pptx.util import Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

SRC = Path(r"C:\Users\HARIESH\Downloads\PPT Format for Second Review.pptx")
DST = Path(r"C:\Users\HARIESH\Downloads\S5 Mini Project\project_report\SentinelMesh_Second_Review.pptx")

BLUE   = RGBColor(0x1F, 0x49, 0x7D)
MAROON = RGBColor(0x80, 0x00, 0x00)
BLACK  = RGBColor(0x00, 0x00, 0x00)
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
DARK   = RGBColor(0x1A, 0x1A, 0x1A)
TEAL   = RGBColor(0x00, 0x70, 0x70)
DATE_STR = "13-10-2026"

ALIGN_MAP = {
    PP_ALIGN.LEFT: 'l',
    PP_ALIGN.CENTER: 'ctr',
    PP_ALIGN.RIGHT: 'r',
    PP_ALIGN.JUSTIFY: 'just',
}


def qn(tag):
    from pptx.oxml.ns import qn as _qn
    return _qn(tag)


def set_tf(tf, lines, default_size=Pt(18), default_color=BLACK,
           default_bold=False, align=PP_ALIGN.LEFT):
    txBody = tf._txBody
    paras = txBody.findall(qn('a:p'))
    for p in paras[1:]:
        txBody.remove(p)

    first = True
    for item in lines:
        if isinstance(item, str):
            item = {"text": item}
        text   = item.get("text", "")
        size   = item.get("size", default_size)
        color  = item.get("color", default_color)
        bold   = item.get("bold", default_bold)
        aln    = item.get("align", align)
        spB    = item.get("space_before", 0)
        italic = item.get("italic", False)

        if first:
            p_elem = txBody.findall(qn('a:p'))[0]
            for r in p_elem.findall(qn('a:r')):
                p_elem.remove(r)
            for br in p_elem.findall(qn('a:br')):
                p_elem.remove(br)
            first = False
        else:
            p_elem = etree.SubElement(txBody, qn('a:p'))

        pPr = p_elem.find(qn('a:pPr'))
        if pPr is None:
            pPr = etree.SubElement(p_elem, qn('a:pPr'))
            p_elem.insert(0, pPr)
        pPr.set('algn', ALIGN_MAP.get(aln, 'l'))
        if spB:
            spcBef = etree.SubElement(pPr, qn('a:spcBef'))
            spcPts = etree.SubElement(spcBef, qn('a:spcPts'))
            spcPts.set('val', str(int(spB * 100)))

        r_elem = etree.SubElement(p_elem, qn('a:r'))
        rPr = etree.SubElement(r_elem, qn('a:rPr'))
        rPr.set('lang', 'en-IN')
        rPr.set('sz', str(int(size.pt * 100)))
        rPr.set('b', '1' if bold else '0')
        rPr.set('i', '1' if italic else '0')
        rPr.set('dirty', '0')
        solidFill = etree.SubElement(rPr, qn('a:solidFill'))
        srgbClr   = etree.SubElement(solidFill, qn('a:srgbClr'))
        srgbClr.set('val', '%02X%02X%02X' % (color[0], color[1], color[2]))
        latin = etree.SubElement(rPr, qn('a:latin'))
        latin.set('typeface', 'Cambria')
        t_elem = etree.SubElement(r_elem, qn('a:t'))
        t_elem.text = text


def simple(tf, text, size=Pt(18), color=BLACK, bold=False, align=PP_ALIGN.LEFT):
    set_tf(tf, [{"text": text, "size": size, "color": color, "bold": bold, "align": align}])


def update_footer(slide, date_str, slide_num):
    for sh in slide.shapes:
        if not sh.has_text_frame:
            continue
        txt = sh.text_frame.text.strip()
        if '17-07-2023' in txt or '13-10-2026' in txt:
            simple(sh.text_frame, date_str, size=Pt(14))
        elif 'SECOND REVIEW PRESENTATION' in txt.upper():
            simple(sh.text_frame, 'SECOND REVIEW PRESENTATION', size=Pt(14), align=PP_ALIGN.CENTER)
        elif txt.isdigit():
            simple(sh.text_frame, str(slide_num), size=Pt(14), align=PP_ALIGN.RIGHT)


def fill_table(table, data, hdr_color=BLUE, font_size=Pt(14)):
    for r_idx, row_data in enumerate(data):
        if r_idx >= len(table.rows):
            break
        row = table.rows[r_idx]
        for c_idx, cell_text in enumerate(row_data):
            if c_idx >= len(row.cells):
                break
            cell = row.cells[c_idx]
            cell.text_frame.word_wrap = True
            tcPr = cell._tc.find(qn('a:tcPr'))
            if tcPr is None:
                tcPr = etree.SubElement(cell._tc, qn('a:tcPr'))
            for child in list(tcPr):
                tag = child.tag
                if tag.endswith('}solidFill') or tag.endswith('}gradFill') or tag.endswith('}noFill'):
                    tcPr.remove(child)
            sf = etree.SubElement(tcPr, qn('a:solidFill'))
            sc = etree.SubElement(sf, qn('a:srgbClr'))
            if r_idx == 0:
                sc.set('val', '%02X%02X%02X' % (hdr_color[0], hdr_color[1], hdr_color[2]))
                txt_color, bold = WHITE, True
            elif r_idx % 2 == 0:
                sc.set('val', 'F2F2F2')
                txt_color, bold = BLACK, False
            else:
                sc.set('val', 'FFFFFF')
                txt_color, bold = BLACK, False
            simple(cell.text_frame, cell_text, size=font_size, color=txt_color, bold=bold)


def main():
    shutil.copy2(SRC, DST)
    prs = Presentation(str(DST))
    sls = prs.slides

    # --- Slide 1: Title ---
    s1 = sls[0]
    for sh in s1.shapes:
        if not sh.has_text_frame:
            continue
        txt = sh.text_frame.text.strip()
        if 'Academic Year' in txt or ('2026' in txt and 'S5' in txt):
            set_tf(sh.text_frame, [
                {"text": "ACADEMIC YEAR 2026 - 2027", "size": Pt(20), "color": BLUE, "bold": True, "align": PP_ALIGN.CENTER},
                {"text": "S5 PROJECT WORK I  |  SECOND REVIEW", "size": Pt(18), "color": MAROON, "bold": True, "align": PP_ALIGN.CENTER},
            ])
        elif 'PROJECT TITLE' in txt or len(txt) > 5 and all(c in '.\u2026 ' for c in txt):
            set_tf(sh.text_frame, [
                {"text": "INTELLIGENT MULTI-AGENT FRAMEWORK FOR", "size": Pt(22), "color": DARK, "bold": True, "align": PP_ALIGN.CENTER},
                {"text": "AUTOMATED SOFTWARE TESTING AND BUG ANALYSIS", "size": Pt(22), "color": DARK, "bold": True, "align": PP_ALIGN.CENTER},
                {"text": "(SentinelMesh)", "size": Pt(18), "color": TEAL, "bold": True, "align": PP_ALIGN.CENTER},
            ])
        elif 'BATCH MEMBERS' in txt or 'YOHAN' in txt or 'MAHZHIL' in txt:
            set_tf(sh.text_frame, [
                {"text": "BATCH MEMBERS", "size": Pt(16), "color": BLUE, "bold": True},
                {"text": "Hariesh P  (7376241CS195)  -  Dept. of CSE", "size": Pt(15), "color": BLACK},
                {"text": "Midhum M  (7376242AL152)   -  Dept. of AIML", "size": Pt(15), "color": BLACK},
            ])
        elif 'GUIDE' in txt or 'RAMAN' in txt or 'Mechanical' in txt:
            set_tf(sh.text_frame, [
                {"text": "PROJECT GUIDE", "size": Pt(16), "color": BLUE, "bold": True},
                {"text": "Ms. Ramya R  (CS1906)", "size": Pt(15), "color": BLACK},
                {"text": "Assistant Professor", "size": Pt(14), "color": BLACK},
                {"text": "Dept. of Computer Science and Engineering", "size": Pt(13), "color": BLACK},
            ])
        elif 'BIP PROJECT ID' in txt or '24S7' in txt:
            set_tf(sh.text_frame, [
                {"text": "BIT PROJECT ID", "size": Pt(14), "color": MAROON, "bold": True},
                {"text": "S5-CSE-2026-195", "size": Pt(14), "color": BLACK},
            ])
        elif 'CATERGORY' in txt or 'INTERNAL' in txt:
            set_tf(sh.text_frame, [
                {"text": "CATEGORY", "size": Pt(14), "color": MAROON, "bold": True},
                {"text": "INTERNAL  -  OWN PROJECT", "size": Pt(14), "color": BLACK},
            ])

    # --- Slide 2: Project Work Plan ---
    s2 = sls[1]
    update_footer(s2, DATE_STR, 2)
    for sh in s2.shapes:
        if not sh.has_text_frame:
            continue
        txt = sh.text_frame.text.strip()
        if 'Background should be White' in txt or 'Cambria' in txt or 'Font Size' in txt:
            set_tf(sh.text_frame, [
                {"text": "Phase 1  -  Problem Analysis & Literature Survey  (Weeks 1-2)", "size": Pt(16), "color": MAROON, "bold": True},
                {"text": "  Identified limitations in manual software testing and defect triage workflows.", "size": Pt(15), "color": BLACK},
                {"text": "  Reviewed static analysis, mutation testing, and multi-agent coordination research.", "size": Pt(15), "color": BLACK},
                {"text": "", "size": Pt(6)},
                {"text": "Phase 2  -  Architecture & Agent Design  (Weeks 2-3)", "size": Pt(16), "color": MAROON, "bold": True},
                {"text": "  Designed 9-agent coordination graph: Orchestrator, Static Analysis, Test Generation,", "size": Pt(15), "color": BLACK},
                {"text": "  Test Execution, Bug Classification, Root Cause, Auto-Fix, Critic, Report agents.", "size": Pt(15), "color": BLACK},
                {"text": "", "size": Pt(6)},
                {"text": "Phase 3  -  Implementation  (Weeks 3-5)", "size": Pt(16), "color": MAROON, "bold": True},
                {"text": "  Implemented AST-based analysis, test synthesis, sandbox execution, and reporting.", "size": Pt(15), "color": BLACK},
                {"text": "  Integrated FastAPI backend, SQLite/SQLAlchemy, and React mission-control dashboard.", "size": Pt(15), "color": BLACK},
                {"text": "", "size": Pt(6)},
                {"text": "Phase 4  -  Validation & Documentation  (Weeks 6-7)", "size": Pt(16), "color": MAROON, "bold": True},
                {"text": "  Validated: 37/37 tests passing, 85% platform code coverage.", "size": Pt(15), "color": BLACK},
                {"text": "  Prepared full academic project report and Second Review presentation.", "size": Pt(15), "color": BLACK},
            ])
        elif 'PROJECT WORK PLAN' in txt:
            simple(sh.text_frame, "PROJECT WORK PLAN", size=Pt(22), color=BLUE, bold=True)

    # --- Slide 3: Modern Tools ---
    s3 = sls[2]
    update_footer(s3, DATE_STR, 3)
    for sh in s3.shapes:
        if not sh.has_text_frame:
            continue
        txt = sh.text_frame.text.strip()
        if 'Background should be White' in txt or 'Cambria' in txt:
            set_tf(sh.text_frame, [
                {"text": "Python 3.11+", "size": Pt(16), "color": MAROON, "bold": True},
                {"text": "   Core agent logic, AST parsing, sandboxed test execution, and backend services.", "size": Pt(15), "color": BLACK},
                {"text": "FastAPI + Uvicorn", "size": Pt(16), "color": MAROON, "bold": True},
                {"text": "   RESTful API gateway, WebSocket communication, and health-monitoring endpoints.", "size": Pt(15), "color": BLACK},
                {"text": "Python AST Module", "size": Pt(16), "color": MAROON, "bold": True},
                {"text": "   Structural code parsing, cyclomatic-complexity scoring, security-smell detection.", "size": Pt(15), "color": BLACK},
                {"text": "SQLite + SQLAlchemy ORM", "size": Pt(16), "color": MAROON, "bold": True},
                {"text": "   Persistent storage of analysis results, test records, patch history, agent state.", "size": Pt(15), "color": BLACK},
                {"text": "React 18 (Vite)", "size": Pt(16), "color": MAROON, "bold": True},
                {"text": "   Mission-control dashboard: real-time telemetry, risk heat-map, report viewer.", "size": Pt(15), "color": BLACK},
                {"text": "pytest + coverage.py", "size": Pt(16), "color": MAROON, "bold": True},
                {"text": "   37/37 automated tests passing; 85% platform code coverage measured.", "size": Pt(15), "color": BLACK},
                {"text": "Subprocess Sandbox", "size": Pt(16), "color": MAROON, "bold": True},
                {"text": "   Isolated test execution with 20-second timeout and archive-size controls.", "size": Pt(15), "color": BLACK},
                {"text": "Git + GitHub", "size": Pt(16), "color": MAROON, "bold": True},
                {"text": "   Version control  -  github.com/HARIESHPERIASAMY/S5_Mini_Project", "size": Pt(15), "color": BLACK},
            ])
        elif 'EFFECTIVE UTILIZATION' in txt:
            simple(sh.text_frame, "EFFECTIVE UTILIZATION OF MODERN TOOLS", size=Pt(22), color=BLUE, bold=True)

    # --- Slide 4: Flow Chart ---
    s4 = sls[3]
    update_footer(s4, DATE_STR, 4)
    for sh in s4.shapes:
        if not sh.has_text_frame:
            continue
        txt = sh.text_frame.text.strip()
        if 'PROPOSED METHODOLOGY' in txt and 'Flow' in txt:
            simple(sh.text_frame, "PROPOSED METHODOLOGY (FLOW CHART)", size=Pt(22), color=BLUE, bold=True)
        elif txt == '':
            set_tf(sh.text_frame, [
                {"text": "User submits repository or demo project ZIP", "size": Pt(15), "color": BLUE, "bold": True, "align": PP_ALIGN.CENTER},
                {"text": "  |", "size": Pt(14), "color": MAROON, "bold": True, "align": PP_ALIGN.CENTER},
                {"text": "FastAPI gateway validates and routes to Orchestrator Agent", "size": Pt(14), "color": BLACK, "align": PP_ALIGN.CENTER},
                {"text": "  |", "size": Pt(14), "color": MAROON, "bold": True, "align": PP_ALIGN.CENTER},
                {"text": "Static Analysis Agent  >>  AST parsing, risk scoring, security-smell detection", "size": Pt(14), "color": BLACK},
                {"text": "  |", "size": Pt(14), "color": MAROON, "bold": True, "align": PP_ALIGN.CENTER},
                {"text": "Test Generation Agent  >>  unit, boundary, edge-case & mutation test cases", "size": Pt(14), "color": BLACK},
                {"text": "  |", "size": Pt(14), "color": MAROON, "bold": True, "align": PP_ALIGN.CENTER},
                {"text": "Test Execution Agent  >>  sandbox run, coverage collection", "size": Pt(14), "color": BLACK},
                {"text": "  |", "size": Pt(14), "color": MAROON, "bold": True, "align": PP_ALIGN.CENTER},
                {"text": "Bug Classification Agent  >>  severity tagging, duplicate detection", "size": Pt(14), "color": BLACK},
                {"text": "  |", "size": Pt(14), "color": MAROON, "bold": True, "align": PP_ALIGN.CENTER},
                {"text": "Root Cause Agent  >>  stack-trace mapping, causal explanation", "size": Pt(14), "color": BLACK},
                {"text": "  |", "size": Pt(14), "color": MAROON, "bold": True, "align": PP_ALIGN.CENTER},
                {"text": "Auto-Fix Agent  >>  unified-diff patch generation, sandbox re-verification", "size": Pt(14), "color": BLACK},
                {"text": "  |", "size": Pt(14), "color": MAROON, "bold": True, "align": PP_ALIGN.CENTER},
                {"text": "Critic/Reviewer Agent  >>  findings debate, consensus scoring", "size": Pt(14), "color": BLACK},
                {"text": "  |", "size": Pt(14), "color": MAROON, "bold": True, "align": PP_ALIGN.CENTER},
                {"text": "Report Agent  >>  executive report + dashboard telemetry export", "size": Pt(14), "color": BLACK},
                {"text": "", "size": Pt(6)},
                {"text": "Feedback loop: failed tests >> patch proposal >> sandbox re-run >> verified/unresolved", "size": Pt(13), "color": TEAL, "italic": True},
            ])

    # --- Slide 5: Gantt Chart ---
    s5 = sls[4]
    update_footer(s5, DATE_STR, 5)
    for sh in s5.shapes:
        if sh.has_text_frame and 'GANTT' in sh.text_frame.text.upper():
            simple(sh.text_frame, "PROPOSED METHODOLOGY (GANTT CHART)", size=Pt(22), color=BLUE, bold=True)
        if sh.has_table:
            fill_table(sh.table, [
                ["Work Package", "W1", "W2", "W3", "W4", "W5", "W6", "W7"],
                ["Requirements & literature review", "OK", "OK", "", "", "", "", ""],
                ["Architecture & agent design", "", "OK", "OK", "", "", "", ""],
                ["Agent implementation (9 agents)", "", "", "OK", "OK", "OK", "", ""],
                ["Sandbox & mutation testing", "", "", "", "OK", "OK", "OK", ""],
                ["Frontend / backend integration", "", "", "", "", "OK", "OK", ""],
                ["Validation, debugging & tests", "", "", "", "", "", "OK", "OK"],
                ["Report & review preparation", "", "", "", "", "", "OK", "OK"],
            ], font_size=Pt(14))

    # --- Slide 6: Modules ---
    s6 = sls[5]
    update_footer(s6, DATE_STR, 6)
    for sh in s6.shapes:
        if not sh.has_text_frame:
            continue
        txt = sh.text_frame.text.strip()
        if 'Background should be White' in txt or 'Cambria' in txt:
            set_tf(sh.text_frame, [
                {"text": "1. Orchestrator Agent", "size": Pt(15), "color": BLUE, "bold": True},
                {"text": "   Manages execution graph, agent retries, and lifecycle state transitions.", "size": Pt(14), "color": BLACK},
                {"text": "2. Static Analysis Agent", "size": Pt(15), "color": BLUE, "bold": True},
                {"text": "   AST parsing, cyclomatic complexity, security-smell detection, risk scores per file.", "size": Pt(14), "color": BLACK},
                {"text": "3. Test Generation Agent", "size": Pt(15), "color": BLUE, "bold": True},
                {"text": "   Prioritised unit, boundary, edge-case, and property-based pytest case generation.", "size": Pt(14), "color": BLACK},
                {"text": "4. Test Execution Agent", "size": Pt(15), "color": BLUE, "bold": True},
                {"text": "   Runs tests in isolated subprocess sandbox; tracks coverage and flaky-test flags.", "size": Pt(14), "color": BLACK},
                {"text": "5. Bug Classification Agent", "size": Pt(15), "color": BLUE, "bold": True},
                {"text": "   Labels defect type, severity level; detects duplicate findings.", "size": Pt(14), "color": BLACK},
                {"text": "6. Root Cause Agent", "size": Pt(15), "color": BLUE, "bold": True},
                {"text": "   Maps stack traces to source locations; generates causal explanations.", "size": Pt(14), "color": BLACK},
                {"text": "7. Auto-Fix Agent", "size": Pt(15), "color": BLUE, "bold": True},
                {"text": "   Proposes unified-diff patches; verifies by re-running tests in sandbox.", "size": Pt(14), "color": BLACK},
                {"text": "8. Critic / Reviewer Agent", "size": Pt(15), "color": BLUE, "bold": True},
                {"text": "   Challenges findings via debate; computes consensus quality score.", "size": Pt(14), "color": BLACK},
                {"text": "9. Report Agent", "size": Pt(15), "color": BLUE, "bold": True},
                {"text": "   Builds executive & technical reports; streams telemetry to React dashboard.", "size": Pt(14), "color": BLACK},
            ])
        elif 'MODULES' in txt:
            simple(sh.text_frame, "SYSTEM MODULES", size=Pt(22), color=BLUE, bold=True)

    # --- Slide 7: Advantages & Disadvantages ---
    s7 = sls[6]
    update_footer(s7, DATE_STR, 7)
    for sh in s7.shapes:
        if not sh.has_text_frame:
            continue
        txt = sh.text_frame.text.strip()
        if 'Background should be White' in txt or 'Cambria' in txt:
            set_tf(sh.text_frame, [
                {"text": "ADVANTAGES", "size": Pt(18), "color": BLUE, "bold": True},
                {"text": "  Nine specialised agents divide testing tasks - no single point of failure.", "size": Pt(15), "color": BLACK},
                {"text": "  AST-based static analysis provides deep source-level risk signals.", "size": Pt(15), "color": BLACK},
                {"text": "  Subprocess sandbox limits execution time (20 s) and extraction size.", "size": Pt(15), "color": BLACK},
                {"text": "  Patch proposals are re-tested in sandbox before being marked verified.", "size": Pt(15), "color": BLACK},
                {"text": "  Structured JSON reports and risk heat-map improve review visibility.", "size": Pt(15), "color": BLACK},
                {"text": "  Offline deterministic fallback - works without a cloud LLM provider.", "size": Pt(15), "color": BLACK},
                {"text": "  37/37 tests passing; 85% platform code coverage validated.", "size": Pt(15), "color": BLACK},
                {"text": "", "size": Pt(8)},
                {"text": "LIMITATIONS", "size": Pt(18), "color": MAROON, "bold": True},
                {"text": "  Static and test-generation rules are currently Python-focused.", "size": Pt(15), "color": BLACK},
                {"text": "  Rule-based detectors may miss context-dependent or semantic defects.", "size": Pt(15), "color": BLACK},
                {"text": "  LLM-assisted features depend on external API quotas (configurable).", "size": Pt(15), "color": BLACK},
                {"text": "  Sandbox 20-second timeout may be insufficient for very large codebases.", "size": Pt(15), "color": BLACK},
                {"text": "  Auto-generated tests do not guarantee complete path/branch coverage.", "size": Pt(15), "color": BLACK},
                {"text": "  Multi-language support (Java, C++) is planned future work.", "size": Pt(15), "color": BLACK},
            ])
        elif 'ADVANTAGES AND DISADVANTAGES' in txt:
            simple(sh.text_frame, "ADVANTAGES AND DISADVANTAGES", size=Pt(22), color=BLUE, bold=True)

    # --- Slide 8: Conclusion ---
    s8 = sls[7]
    update_footer(s8, DATE_STR, 8)
    for sh in s8.shapes:
        if not sh.has_text_frame:
            continue
        txt = sh.text_frame.text.strip()
        if 'Background should be White' in txt or 'Cambria' in txt:
            set_tf(sh.text_frame, [
                {"text": "  SentinelMesh demonstrates that multi-agent coordination can automate the full", "size": Pt(15), "color": BLACK},
                {"text": "  software quality lifecycle - from static analysis to sandbox-verified auto-fix.", "size": Pt(15), "color": BLACK},
                {"text": "", "size": Pt(5)},
                {"text": "  Nine dedicated agents collaborate via an event-driven bus without tight coupling,", "size": Pt(15), "color": BLACK},
                {"text": "  enabling independent extensibility and testing of each component.", "size": Pt(15), "color": BLACK},
                {"text": "", "size": Pt(5)},
                {"text": "  FastAPI backend, SQLite persistence, sandboxed execution, and a React dashboard", "size": Pt(15), "color": BLACK},
                {"text": "  provide a production-grade foundation for local-first quality engineering.", "size": Pt(15), "color": BLACK},
                {"text": "", "size": Pt(5)},
                {"text": "  Validated result: 37/37 automated tests passing; 85% platform code coverage.", "size": Pt(15), "color": BLACK},
                {"text": "", "size": Pt(5)},
                {"text": "  Future directions: multi-language analysis (Java, C++, Go), cloud deployment,", "size": Pt(15), "color": BLACK},
                {"text": "  LLM-augmented patch generation, and cross-repository trend analytics.", "size": Pt(15), "color": BLACK},
                {"text": "", "size": Pt(8)},
                {"text": "Outcome:", "size": Pt(16), "color": MAROON, "bold": True},
                {"text": "  A fully traceable workflow from source-code submission to structured bug evidence,", "size": Pt(15), "color": BLACK},
                {"text": "  root-cause explanation, sandbox-verified patches, and exportable executive report.", "size": Pt(15), "color": BLACK},
            ])
        elif 'CONCLUSION' in txt:
            simple(sh.text_frame, "CONCLUSION", size=Pt(22), color=BLUE, bold=True)

    # --- Slide 9: Cost-Benefit ---
    s9 = sls[8]
    update_footer(s9, DATE_STR, 9)
    for sh in s9.shapes:
        if sh.has_text_frame and 'COST' in sh.text_frame.text.upper():
            simple(sh.text_frame, "COST BENEFIT ANALYSIS", size=Pt(22), color=BLUE, bold=True)
        if sh.has_table:
            fill_table(sh.table, [
                ["Area", "Cost / Consideration", "Expected Benefit"],
                ["Software Tools", "Open-source: Python, FastAPI, React, SQLite, pytest - zero licensing cost.", "Full ecosystem access; community support; production-ready stack."],
                ["Compute", "Local development machine; sandboxed runs consume CPU/memory transiently.", "Repeatable, isolated, safe local validation with every run."],
                ["Development Effort", "7-week project; 9-agent design, backend, frontend, 37 test cases authored.", "Reusable modular workflow applicable to any Python repository."],
                ["Maintenance", "Periodic updates to analysis rules, dependencies, and agent logic.", "Centralised reporting and repeatable test execution reduce manual effort."],
                ["Risk Mitigation", "False positives possible; auto-fix patches are re-tested before acceptance.", "Structured findings and sandbox-verified patches lower regression risk."],
            ], font_size=Pt(13))

    # --- Slide 10: Contributions - Hariesh ---
    s10 = sls[9]
    update_footer(s10, DATE_STR, 10)
    for sh in s10.shapes:
        if not sh.has_text_frame:
            continue
        txt = sh.text_frame.text.strip()
        if 'Batch Member 1' in txt or 'Reg No' in txt or '.....' in txt:
            set_tf(sh.text_frame, [
                {"text": "Member 1 :  HARIESH P  (7376241CS195)  -  Dept. of CSE", "size": Pt(16), "color": MAROON, "bold": True},
                {"text": "", "size": Pt(6)},
                {"text": "1.  Designed overall system architecture and 9-agent coordination graph.", "size": Pt(15), "color": BLACK},
                {"text": "2.  Implemented Orchestrator, Static Analysis, Bug Classification & Root Cause agents.", "size": Pt(15), "color": BLACK},
                {"text": "3.  Developed FastAPI backend: API gateway, WebSocket endpoints, health checks.", "size": Pt(15), "color": BLACK},
                {"text": "4.  Built SQLAlchemy ORM models, database schema, and migration scripts.", "size": Pt(15), "color": BLACK},
                {"text": "5.  Wrote 37 automated unit and integration tests; achieved 85% code coverage.", "size": Pt(15), "color": BLACK},
                {"text": "6.  Authored full academic project report and Second Review documentation.", "size": Pt(15), "color": BLACK},
                {"text": "7.  Managed Git repository and maintained clean commit history on GitHub.", "size": Pt(15), "color": BLACK},
            ])
        elif 'INDIVIDUAL CONTRIBUTIONS' in txt:
            simple(sh.text_frame, "INDIVIDUAL CONTRIBUTIONS TO THE WORK", size=Pt(22), color=BLUE, bold=True)

    # --- Slide 11: Contributions - Midhum ---
    s11 = sls[10]
    update_footer(s11, DATE_STR, 11)
    for sh in s11.shapes:
        if not sh.has_text_frame:
            continue
        txt = sh.text_frame.text.strip()
        if 'Batch Member 1' in txt or 'Reg No' in txt or '.....' in txt:
            set_tf(sh.text_frame, [
                {"text": "Member 2 :  MIDHUM M  (7376242AL152)  -  Dept. of AIML", "size": Pt(16), "color": MAROON, "bold": True},
                {"text": "", "size": Pt(6)},
                {"text": "1.  Implemented Test Generation, Test Execution, and Auto-Fix agents.", "size": Pt(15), "color": BLACK},
                {"text": "2.  Designed and integrated the subprocess sandbox with timeout & size controls.", "size": Pt(15), "color": BLACK},
                {"text": "3.  Developed Critic / Reviewer Agent for consensus scoring and debate logic.", "size": Pt(15), "color": BLACK},
                {"text": "4.  Built Report Agent and executive / technical report generation pipeline.", "size": Pt(15), "color": BLACK},
                {"text": "5.  Developed React 18 (Vite) mission-control dashboard with real-time telemetry.", "size": Pt(15), "color": BLACK},
                {"text": "6.  Integrated frontend with backend WebSocket streams and risk heat-map.", "size": Pt(15), "color": BLACK},
                {"text": "7.  Assisted in validation testing, debugging, and Second Review preparation.", "size": Pt(15), "color": BLACK},
            ])
        elif 'INDIVIDUAL CONTRIBUTIONS' in txt:
            simple(sh.text_frame, "INDIVIDUAL CONTRIBUTIONS TO THE WORK", size=Pt(22), color=BLUE, bold=True)

    # --- Slide 12: System Architecture (repurpose 3rd member slot) ---
    s12 = sls[11]
    update_footer(s12, DATE_STR, 12)
    for sh in s12.shapes:
        if not sh.has_text_frame:
            continue
        txt = sh.text_frame.text.strip()
        if 'Batch Member 1' in txt or 'Reg No' in txt or '.....' in txt:
            set_tf(sh.text_frame, [
                {"text": "SYSTEM ARCHITECTURE OVERVIEW", "size": Pt(18), "color": MAROON, "bold": True},
                {"text": "", "size": Pt(5)},
                {"text": "Client Layer", "size": Pt(15), "color": BLUE, "bold": True},
                {"text": "   React 18 dashboard: repository upload, live agent log, risk heat-map, report download.", "size": Pt(14), "color": BLACK},
                {"text": "API Gateway", "size": Pt(15), "color": BLUE, "bold": True},
                {"text": "   FastAPI + Uvicorn: REST endpoints, WebSocket streams, CORS, request validation.", "size": Pt(14), "color": BLACK},
                {"text": "Agent Orchestration Layer", "size": Pt(15), "color": BLUE, "bold": True},
                {"text": "   Event-driven bus coordinates 9 agents with retry, timeout, lifecycle management.", "size": Pt(14), "color": BLACK},
                {"text": "Analysis & Execution Layer", "size": Pt(15), "color": BLUE, "bold": True},
                {"text": "   Python AST engine, pytest runner, unified-diff patch applier, subprocess sandbox.", "size": Pt(14), "color": BLACK},
                {"text": "Persistence Layer", "size": Pt(15), "color": BLUE, "bold": True},
                {"text": "   SQLite + SQLAlchemy ORM: analysis sessions, test records, patches, agent logs.", "size": Pt(14), "color": BLACK},
            ])
        elif 'INDIVIDUAL CONTRIBUTIONS' in txt:
            simple(sh.text_frame, "SYSTEM ARCHITECTURE OVERVIEW", size=Pt(22), color=BLUE, bold=True)

    # --- Slide 13: Status Part 1 ---
    s13 = sls[12]
    update_footer(s13, DATE_STR, 13)
    for sh in s13.shapes:
        if sh.has_text_frame:
            txt = sh.text_frame.text.strip()
            if 'Status on Partial' in txt or 'STATUS ON PARTIAL' in txt:
                simple(sh.text_frame, "STATUS ON PARTIAL COMPLETION AND SUBMISSION OF PROJECT REPORT", size=Pt(16), color=BLUE, bold=True)
            elif 'List of Documents' in txt:
                simple(sh.text_frame, "List of Documents to be Submitted", size=Pt(15), color=MAROON, bold=True)
        if sh.has_table:
            fill_table(sh.table, [
                ["SL. No.", "List of Documents", "Status"],
                ["1", "Cover Page & Title Page", "Completed"],
                ["2", "Bonafide Certificate", "Completed"],
                ["3", "Declaration", "Completed"],
                ["4", "Acknowledgement", "Completed"],
                ["5", "Chapter I - Introduction", "Completed"],
                ["6", "Chapter II - Literature Survey", "Completed"],
            ])

    # --- Slide 14: Status Part 2 ---
    s14 = sls[13]
    update_footer(s14, DATE_STR, 14)
    for sh in s14.shapes:
        if sh.has_text_frame:
            txt = sh.text_frame.text.strip()
            if 'Submission of Project Report' in txt or 'SUBMISSION' in txt:
                simple(sh.text_frame, "SUBMISSION OF PROJECT REPORT", size=Pt(20), color=BLUE, bold=True)
            elif 'List of Documents' in txt:
                simple(sh.text_frame, "List of Documents to be Submitted", size=Pt(15), color=MAROON, bold=True)
        if sh.has_table:
            fill_table(sh.table, [
                ["SL. No.", "List of Documents", "Status"],
                ["7",  "Chapter III - Objectives & Methodology",  "Completed"],
                ["8",  "Chapter IV - Proposed Work Modules",       "Completed"],
                ["9",  "Chapter V - Results and Discussion",       "Completed"],
                ["10", "Chapter VI - Conclusions & Future Work",   "Completed"],
                ["11", "References (IEEE format, 28 entries)",     "Completed"],
                ["12", "Appendices A - F",                         "Completed"],
            ])

    # --- Slide 15: Publications ---
    s15 = sls[14]
    update_footer(s15, DATE_STR, 15)
    for sh in s15.shapes:
        if sh.has_text_frame and 'PUBLICATIONS' in sh.text_frame.text.upper():
            simple(sh.text_frame, "PUBLICATIONS (CONFERENCE / JOURNAL / PATENT)", size=Pt(20), color=BLUE, bold=True)
        if sh.has_table:
            fill_table(sh.table, [
                ["SL. No.", "Paper / Manuscript Title", "Status"],
                ["1", "Manuscript in preparation: SentinelMesh - Multi-Agent Automated Software Testing using AST Analysis and Sandboxed Execution", "In progress"],
                ["2", "No conference/journal/patent submitted as of Second Review date.", "-"],
            ], font_size=Pt(13))

    # --- Slide 16: Originality Score ---
    s16 = sls[15]
    update_footer(s16, DATE_STR, 16)
    for sh in s16.shapes:
        if sh.has_text_frame and 'ORIGINALITY' in sh.text_frame.text.upper():
            simple(sh.text_frame, "ORIGINALITY SCORE", size=Pt(22), color=BLUE, bold=True)
        if sh.has_table:
            fill_table(sh.table, [
                ["SL. No.", "Tool Name for Checking Originality Score", "Status / Score / Link"],
                ["1", "Turnitin / iThenticate", "Pending - to be submitted before final viva"],
                ["2", "Grammarly Plagiarism Checker (secondary)", "Pending"],
            ])

    # --- Slide 17: References ---
    s17 = sls[16]
    update_footer(s17, DATE_STR, 17)
    for sh in s17.shapes:
        if not sh.has_text_frame:
            continue
        txt = sh.text_frame.text.strip()
        if txt == 'REFERENCES' or ('REFERENCES' in txt and 'Journal Papers' in txt):
            simple(sh.text_frame, "REFERENCES", size=Pt(22), color=BLUE, bold=True)
        elif 'As per IEEE Format' in txt or '[1].' in txt:
            set_tf(sh.text_frame, [
                {"text": "[1]  HARIESHPERIASAMY, S5_Mini_Project - SentinelMesh, GitHub, 2026. https://github.com/HARIESHPERIASAMY/S5_Mini_Project", "size": Pt(12), "color": BLACK},
                {"text": "[2]  Python Software Foundation, ast - Abstract Syntax Trees, Python 3.11 Docs. https://docs.python.org/3/library/ast.html", "size": Pt(12), "color": BLACK},
                {"text": "[3]  T. Ramirez, FastAPI Documentation, Tiangolo, 2024. https://fastapi.tiangolo.com/", "size": Pt(12), "color": BLACK},
                {"text": "[4]  Pytest Development Team, pytest Documentation, 2024. https://docs.pytest.org/", "size": Pt(12), "color": BLACK},
                {"text": "[5]  SQLAlchemy Authors, SQLAlchemy Documentation, 2024. https://docs.sqlalchemy.org/", "size": Pt(12), "color": BLACK},
                {"text": "[6]  React Authors, React 18 Documentation, Meta Open Source, 2024. https://react.dev/", "size": Pt(12), "color": BLACK},
                {"text": "[7]  M. Wooldridge and N. Jennings, Intelligent Agents: Theory and Practice, Knowledge Engineering Review, vol.10, no.2, pp.115-152, 1995.", "size": Pt(12), "color": BLACK},
                {"text": "[8]  A. Zeller, Why Programs Fail: A Guide to Systematic Debugging, 2nd ed., Morgan Kaufmann, 2009.", "size": Pt(12), "color": BLACK},
                {"text": "[9]  P. Ammann and J. Offutt, Introduction to Software Testing, 2nd ed., Cambridge University Press, 2016.", "size": Pt(12), "color": BLACK},
                {"text": "[10] S. Yoo and M. Harman, Regression Testing Minimisation, Selection and Prioritisation: A Survey, STVR, vol.22, no.2, pp.67-120, 2012.", "size": Pt(12), "color": BLACK},
                {"text": "[11] G. Fraser and A. Arcuri, EvoSuite: Automatic Test Suite Generation for Object-Oriented Software, in Proc. FSE, 2011, pp.416-419.", "size": Pt(12), "color": BLACK},
                {"text": "[12] R. Feldt et al., Finding test data in existing code, in Proc. ICSME, 2013, pp.1-10.", "size": Pt(12), "color": BLACK},
                {"text": "[13] M. Harman and B. Jones, Search-based software engineering, Information & Software Technology, vol.43, no.14, pp.833-839, 2001.", "size": Pt(12), "color": BLACK},
            ])

    # Save PPTX
    prs.save(str(DST))
    print("Saved PPTX:", DST)

    # Export to PDF using PowerPoint COM
    pdf_out = DST.with_suffix('.pdf')
    dst_str = str(DST).replace('\\', '\\\\')
    pdf_str = str(pdf_out).replace('\\', '\\\\')
    ps = r"""
$ErrorActionPreference = 'Stop'
try {
    $ppt = New-Object -ComObject PowerPoint.Application
    $ppt.Visible = [Microsoft.Office.Core.MsoTriState]::msoTrue
    $prs = $ppt.Presentations.Open("DST_PATH", $false, $false, $true)
    Start-Sleep -Seconds 4
    $prs.SaveAs("PDF_PATH", 32)
    $prs.Close()
    $ppt.Quit()
    [System.GC]::Collect()
    Write-Host "PDF_OK"
} catch {
    Write-Error $_
}
""".replace("DST_PATH", str(DST)).replace("PDF_PATH", str(pdf_out))

    ps_path = Path("project_report/export_ppt.ps1")
    ps_path.write_text(ps, encoding='utf-8')
    print("Exporting PDF via PowerPoint COM...")
    res = subprocess.run(
        ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(ps_path)],
        capture_output=True, text=True, timeout=120
    )
    ps_path.unlink(missing_ok=True)
    print("STDOUT:", res.stdout.strip())
    if res.stderr.strip():
        print("STDERR:", res.stderr.strip())

    if pdf_out.exists():
        kb = pdf_out.stat().st_size // 1024
        print(f"\nPDF ready: {pdf_out}  ({kb} KB)")
    else:
        print("PDF not created. Check PowerPoint COM output above.")


if __name__ == "__main__":
    main()
