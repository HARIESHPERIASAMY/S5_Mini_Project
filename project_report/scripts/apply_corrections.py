"""
COMPREHENSIVE CORRECTION SCRIPT
Fixes all identified compliance issues in Final_Project_Report.docx:
1. Fixes 22 paragraph alignment issues (Left -> Justify)
2. Fixes Figure numbering inconsistency (3.4 vs 3.5)
3. Fixes Table B.1 -> Table A.1 naming
4. Ensures consistent figure captions in List of Figures
5. Saves corrected DOCX to output/SentinelMesh_Final_Report.docx
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import nsdecls
from docx.oxml import parse_xml
import copy
import shutil
import os

# ---- Step 1: Backup original ----
shutil.copy('Final_Project_Report.docx', 'Final_Project_Report_BACKUP.docx')
print("[1] Backup created: Final_Project_Report_BACKUP.docx")

# ---- Step 2: Load document ----
doc = Document('Final_Project_Report.docx')
print("[2] Loaded Final_Project_Report.docx")

corrections = []
fig_num_fix = 0
align_fix = 0
table_name_fix = 0

# ---- Step 3: Fix paragraph alignment issues ----
# Issue: 22 paragraphs use LEFT alignment when they should be JUSTIFY
# These are subheadings/numbered items that are NOT headings (no H1/H2 style)
# They should be JUSTIFY per DOC-13 body text rule.
# However, true subheadings within a section (bold, marking a logical division)
# should remain JUSTIFY-aligned but may have their own sub-heading treatment.

# Paragraphs that should remain CENTER: chapter titles, figure captions, table captions, page numbers
# Paragraphs that should be JUSTIFY: all body text, including inline bold subheadings

for i, p in enumerate(doc.paragraphs):
    txt = p.text.strip()
    if not txt:
        continue
    
    # Skip: chapter title paragraphs (pure UPPERCASE, center-aligned are fine as-is)
    if txt in ['CHAPTER - I', 'CHAPTER - II', 'CHAPTER - III', 'CHAPTER - IV', 
               'CHAPTER - V', 'CHAPTER - VI', 'REFERENCES', 'BONAFIDE CERTIFICATE',
               'DECLARATION', 'ACKNOWLEDGEMENT', 'ABSTRACT', 'LIST OF FIGURES',
               'LIST OF TABLES', 'LIST OF ABBREVIATIONS', 'TABLE OF CONTENTS']:
        continue
    
    # Skip: chapter subtitle labels
    if txt in ['INTRODUCTION', 'LITERATURE SURVEY', 'OBJECTIVES AND METHODOLOGY',
               'PROPOSED WORK MODULES', 'RESULTS AND DISCUSSION',
               'CONCLUSIONS AND SUGGESTIONS FOR FUTURE WORK']:
        continue
    
    # Skip: Figure and Table captions (should be CENTER)
    if txt.startswith('Figure ') and ':' in txt:
        continue
    if txt.startswith('Table ') and ':' in txt:
        continue
    if txt.startswith('Figure ') and 'illustrates' in txt:
        pass  # Will be handled below
    
    # Check if paragraph is LEFT-aligned when it should be JUSTIFY
    align = p.alignment
    if align == WD_ALIGN_PARAGRAPH.LEFT:
        # Fix to JUSTIFY for body text paragraphs
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        align_fix += 1
        corrections.append(f'P{i}: Fixed alignment LEFT -> JUSTIFY for: "{txt[:50]}"')

print(f"[3] Fixed {align_fix} alignment issues (LEFT -> JUSTIFY)")

# ---- Step 4: Fix Figure numbering inconsistency ----
# Issue: Report has Figs 3.1, 3.2, 3.3, and the ER diagram is referred to as 
# both "Figure 3.4" in caption and "Figure 3.5" in text body
# Correct: Fig 3.4 is the ER diagram; all "Figure 3.5" text references -> "Figure 3.4"

for i, p in enumerate(doc.paragraphs):
    txt = p.text.strip()
    if not txt:
        continue
    
    # Fix "Figure 3.5" references in text body
    if 'Figure 3.5' in p.text and 'Figure 3.5:' not in p.text:
        # This is a body text reference to fig 3.5
        for run in p.runs:
            if 'Figure 3.5' in run.text:
                old_text = run.text
                run.text = run.text.replace('Figure 3.5', 'Figure 3.4')
                fig_num_fix += 1
                corrections.append(f'P{i}: Fixed "Figure 3.5" -> "Figure 3.4" in: "{old_text[:50]}"')
    
    # Fix the caption paragraph "Figure 3.4: Relational Entity-Relationship (ER) Database Schema"
    # should stay as "Figure 3.4" (already correct)
    # The body text after it says "Figure 3.5 details..." -> fix to "Figure 3.4 details..."
    if p.text.startswith('Figure 3.5 details'):
        for run in p.runs:
            if 'Figure 3.5' in run.text:
                run.text = run.text.replace('Figure 3.5', 'Figure 3.4')
                fig_num_fix += 1
                corrections.append(f'P{i}: Fixed "Figure 3.5 details" -> "Figure 3.4 details"')

print(f"[4] Fixed {fig_num_fix} figure number references (3.5 -> 3.4)")

# ---- Step 5: Fix Table B.1 -> Table A.1 ----
# Issue: Table in Appendix III is labeled "Table B.1" which is non-standard
# Should be "Table A.1" (Appendix A) or simply "Table III.1"
# We'll change it to "Table A.1" as most consistent with institutional style

for i, p in enumerate(doc.paragraphs):
    if 'Table B.1' in p.text:
        for run in p.runs:
            if 'Table B.1' in run.text:
                run.text = run.text.replace('Table B.1', 'Table A.1')
                table_name_fix += 1
                corrections.append(f'P{i}: Fixed "Table B.1" -> "Table A.1"')

# Also fix in any table headers
for t_idx, table in enumerate(doc.tables):
    for row in table.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                if 'Table B.1' in p.text:
                    for run in p.runs:
                        if 'Table B.1' in run.text:
                            run.text = run.text.replace('Table B.1', 'Table A.1')
                            table_name_fix += 1
                            corrections.append(f'Table {t_idx}: Fixed "Table B.1" -> "Table A.1"')

print(f"[5] Fixed {table_name_fix} table naming issues (B.1 -> A.1)")

# ---- Step 6: Verify figure caption numbering is consistent ----
# The report caption says "Figure 3.4: Relational Entity-Relationship (ER) Database Schema"
# but earlier text says "Figure 3.4:" for the correct ER diagram
# The body text "Detailed Explanation of Database Schema (Figure 3.5)" must be fixed
print("[6] Verifying figure captions...")
for i, p in enumerate(doc.paragraphs):
    if 'Figure 3.5' in p.text:
        print(f"  Remaining 'Figure 3.5' reference at P{i}: {p.text[:60]}")
        for run in p.runs:
            if 'Figure 3.5' in run.text:
                run.text = run.text.replace('Figure 3.5', 'Figure 3.4')
                corrections.append(f'P{i}: Final fix "Figure 3.5" -> "Figure 3.4"')

# ---- Step 7: Ensure page 7 (blank after abstract) has proper content ----
# The TOC shows "TABLE OF CONTENTS v" meaning the TOC starts at page v
# Abstract ends on page iv; page v is blank
# This is acceptable since the rule is Min 1 - Max 2 pages for Abstract
# and the abstract is on 1 content page (iv) with the next section on vi
# The blank page v is the back of page iv in duplex printing
# No action needed

# ---- Step 8: Save corrected document ----
os.makedirs('output', exist_ok=True)
output_path = 'output/SentinelMesh_Final_Report.docx'
doc.save(output_path)
print(f"\n[7] Saved corrected document to: {output_path}")

# ---- Step 9: Print correction summary ----
print(f"\n=== CORRECTION SUMMARY ===")
print(f"Total corrections made: {len(corrections)}")
print(f"  - Alignment fixes: {align_fix}")
print(f"  - Figure number fixes: {fig_num_fix}")
print(f"  - Table naming fixes: {table_name_fix}")
print(f"\nDetailed corrections:")
for c in corrections:
    print(f"  {c}")
