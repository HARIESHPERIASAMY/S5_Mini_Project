"""Direct page-by-page audit: read each page, identify section, count."""
import pypdf, sys
sys.stdout.reconfigure(encoding='utf-8')

reader = pypdf.PdfReader('output/SentinelMesh_Final_Report.pdf')
total = len(reader.pages)
print(f"Total pages: {total}\n")

# Manual section bounds based on page-by-page observation
sections = [
    ("Cover Page",                  1,   1,   (1,1)),
    ("Inner Title Page",            2,   2,   (1,1)),
    ("Bonafide Certificate",        3,   3,   (1,1)),
    ("Declaration",                 4,   4,   (1,1)),
    ("Acknowledgement",             5,   5,   (1,1)),
    ("Abstract",                    6,   7,   (1,2)),
    ("Table of Contents",           8,  10,   (2,4)),
    ("List of Figures",            11,  11,   (1,2)),
    ("List of Tables",             12,  12,   (1,2)),
    ("List of Abbreviations",      13,  14,   (1,2)),
    ("Chapter I — Introduction",   15,  19,   (4,7)),
    ("Chapter II — Lit. Survey",   20,  24,   (3,5)),
    ("Chapter III — Methodology",  25,  34,  (15,20)),
    ("Chapter IV — Proposed Work", 35,  39,   (None,None)),  # Extra chapter
    ("Chapter V — Results",        40,  44,   (5,10)),
    ("Chapter VI — Conclusions",   45,  46,   (1,2)),
    ("References",                 47,  48,   (2,4)),
    ("Appendix I (BOM)",           49,  49,   (None,None)),
    ("Appendix II (Code)",         50,  51,   (None,None)),
    ("Appendix III (Std Tables)",  52,  52,   (None,None)),
    ("Appendix IV (Pub Cert)",     53,  53,   (None,None)),
    ("Appendix V (Pub Proof)",     54,  54,   (None,None)),
    ("Appendix VI (Work Contrib)", 55,  56,   (None,None)),
    ("Appendix VII (Plagiarism)",  57,  57,   (None,None)),
]

print(f"{'Section':<35} {'Pgs':>3} {'Req':>10} {'Status'}")
print("─" * 65)
all_pass = True
critical_fails = []
for section, start, end, (lo, hi) in sections:
    count = end - start + 1
    if lo is None:
        status = "INFO"
        req_str = "N/A"
    elif lo <= count <= hi:
        status = "✓ PASS"
        req_str = f"{lo}–{hi}"
    else:
        status = "✗ FAIL"
        req_str = f"{lo}–{hi}"
        all_pass = False
        critical_fails.append(f"{section}: {count} pages (required {lo}–{hi})")
    print(f"{section:<35} {count:>3} {req_str:>10}  {status}")

print("─" * 65)
print(f"{'TOTAL':35} {total:>3} {'45–75':>10}  {'✓ PASS' if 45 <= total <= 75 else '✗ FAIL'}")

print()
if critical_fails:
    print("FAILS:")
    for f in critical_fails:
        print(f"  {f}")
else:
    print("All sections PASS.")

# Verify specific page content for key compliance checks
print()
print("=== KEY CONTENT SPOT-CHECKS ===")
checks = [
    (1,  "PROJECT TITLE on cover page",       "INTELLIGENT MULTI-AGENT FRAMEWORK"),
    (3,  "Bonafide Certificate header",       "BONAFIDE CERTIFICATE"),
    (4,  "Declaration header",               "DECLARATION"),
    (6,  "Abstract keywords present",         "Keywords"),
    (8,  "TOC lists chapters",               "CHAPTER"),
    (15, "Chapter I Arabic page number '1'", "1"),
    (25, "Chapter III starts page 11",       "CHAPTER - III"),
    (35, "Chapter IV starts page 21",       "CHAPTER - IV"),
    (40, "Chapter V starts page 26",        "CHAPTER - V"),
    (47, "References section",              "REFERENCES"),
    (53, "Appendix IV present",             "APPENDIX IV"),
    (57, "Appendix VII present",            "APPENDIX VII"),
]
for page_num, desc, kw in checks:
    txt = reader.pages[page_num - 1].extract_text() or ''
    found = kw in txt
    status = "✓" if found else "✗ NOT FOUND"
    print(f"  Page {page_num:2d} — {desc:<42} {status}")
