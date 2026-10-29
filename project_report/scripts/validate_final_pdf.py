"""Final PDF validation script — page-by-page inspection."""
import pypdf, sys
sys.stdout.reconfigure(encoding='utf-8')

reader = pypdf.PdfReader('output/SentinelMesh_Final_Report.pdf')
total = len(reader.pages)
print(f"Total pages: {total}")
print()

# --- Per-page summary ---
print("=== PAGE-BY-PAGE SUMMARY ===")
for i, page in enumerate(reader.pages):
    txt = (page.extract_text() or '').strip()
    lines = [l.strip() for l in txt.split('\n') if l.strip()]
    p1 = lines[0] if lines else 'EMPTY'
    p2 = lines[1] if len(lines) > 1 else ''
    print(f"Page {i+1:2d}: {p1[:45]} | {p2[:35]}")

print()

# --- Section page count check ---
print("=== SECTION PAGE COUNT VERIFICATION ===")
sections = {
    'Cover Page': None,
    'Inner Title Page': None,
    'Bonafide Certificate': None,
    'Declaration': None,
    'Acknowledgement': None,
    'Abstract': None,
    'Table of Contents': None,
    'List of Figures': None,
    'List of Tables': None,
    'List of Abbreviations': None,
    'Chapter I': None,
    'Chapter II': None,
    'Chapter III': None,
    'Chapter IV': None,
    'Chapter V': None,
    'Chapter VI': None,
    'References': None,
    'Appendix I': None,
}
keywords = {
    'Cover Page': 'INTELLIGENT MULTI-AGENT FRAMEWORK',
    'Inner Title Page': None,  # page 2
    'Bonafide Certificate': 'BONAFIDE CERTIFICATE',
    'Declaration': 'DECLARATION',
    'Acknowledgement': 'ACKNOWLEDGEMENT',
    'Abstract': 'ABSTRACT',
    'Table of Contents': 'TABLE OF CONTENTS',
    'List of Figures': 'LIST OF FIGURES',
    'List of Tables': 'LIST OF TABLES',
    'List of Abbreviations': 'LIST OF ABBREVIATIONS',
    'Chapter I': 'CHAPTER - I',
    'Chapter II': 'CHAPTER - II',
    'Chapter III': 'CHAPTER - III',
    'Chapter IV': 'CHAPTER - IV',
    'Chapter V': 'CHAPTER - V',
    'Chapter VI': 'CHAPTER - VI',
    'References': 'REFERENCES',
    'Appendix I': 'APPENDIX I',
}
found_pages = {}
for i, page in enumerate(reader.pages):
    txt = page.extract_text() or ''
    for section, kw in keywords.items():
        if kw and kw in txt and section not in found_pages:
            found_pages[section] = i + 1

# Inner Title Page is always page 2
found_pages['Inner Title Page'] = 2

# Compute page counts
sections_order = [
    ('Cover Page', 1, 1),
    ('Inner Title Page', 2, 2),
    ('Bonafide Certificate', found_pages.get('Bonafide Certificate'), found_pages.get('Declaration', 999) - 1),
    ('Declaration', found_pages.get('Declaration'), found_pages.get('Acknowledgement', 999) - 1),
    ('Acknowledgement', found_pages.get('Acknowledgement'), found_pages.get('Abstract', 999) - 1),
    ('Abstract', found_pages.get('Abstract'), found_pages.get('Table of Contents', 999) - 1),
    ('Table of Contents', found_pages.get('Table of Contents'), found_pages.get('List of Figures', 999) - 1),
    ('List of Figures', found_pages.get('List of Figures'), found_pages.get('List of Tables', 999) - 1),
    ('List of Tables', found_pages.get('List of Tables'), found_pages.get('List of Abbreviations', 999) - 1),
    ('List of Abbreviations', found_pages.get('List of Abbreviations'), found_pages.get('Chapter I', 999) - 1),
    ('Chapter I', found_pages.get('Chapter I'), found_pages.get('Chapter II', 999) - 1),
    ('Chapter II', found_pages.get('Chapter II'), found_pages.get('Chapter III', 999) - 1),
    ('Chapter III', found_pages.get('Chapter III'), found_pages.get('Chapter IV', 999) - 1),
    ('Chapter IV', found_pages.get('Chapter IV'), found_pages.get('Chapter V', 999) - 1),
    ('Chapter V', found_pages.get('Chapter V'), found_pages.get('Chapter VI', 999) - 1),
    ('Chapter VI', found_pages.get('Chapter VI'), found_pages.get('References', 999) - 1),
    ('References', found_pages.get('References'), found_pages.get('Appendix I', 999) - 1),
    ('Appendix I onward', found_pages.get('Appendix I'), total),
]

limits = {
    'Cover Page': (1, 1),
    'Inner Title Page': (1, 1),
    'Bonafide Certificate': (1, 1),
    'Declaration': (1, 1),
    'Acknowledgement': (1, 1),
    'Abstract': (1, 2),
    'Table of Contents': (2, 4),
    'List of Figures': (1, 2),
    'List of Tables': (1, 2),
    'List of Abbreviations': (1, 2),
    'Chapter I': (4, 7),
    'Chapter II': (3, 5),
    'Chapter III': (15, 20),
    'Chapter IV': (None, None),
    'Chapter V': (5, 10),
    'Chapter VI': (1, 2),
    'References': (2, 4),
    'Appendix I onward': (None, None),
}

print(f"{'Section':<30} {'Start':>5} {'End':>5} {'Count':>5} {'Req':>10} {'Status'}")
print("-" * 75)
for section, start, end in sections_order:
    if start is None:
        print(f"{section:<30} {'N/F':>5} {'N/F':>5} {'N/F':>5} {'':>10} {'NOT FOUND'}")
        continue
    end = min(end, total) if end else total
    count = end - start + 1
    lo, hi = limits.get(section, (None, None))
    if lo is None:
        status = 'INFO'
        req_str = 'N/A'
    elif lo <= count <= hi:
        status = 'PASS'
        req_str = f"{lo}-{hi}"
    else:
        status = 'FAIL'
        req_str = f"{lo}-{hi}"
    print(f"{section:<30} {start:>5} {end:>5} {count:>5} {req_str:>10} {status}")

print()
print(f"Total pages: {total}  [Required: 45-75]  {'PASS' if 45 <= total <= 75 else 'FAIL'}")
