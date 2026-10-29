import sys
sys.stdout.reconfigure(encoding='utf-8')

sections = [
    ('Cover Page',                  1,  1,   1, 1),
    ('Inner Title Page',            2,  2,   1, 1),
    ('Bonafide Certificate',        3,  3,   1, 1),
    ('Declaration',                 4,  4,   1, 1),
    ('Acknowledgement',             5,  5,   1, 1),
    ('Abstract',                    6,  7,   1, 2),
    ('Table of Contents',           8, 10,   2, 4),
    ('List of Figures',            11, 11,   1, 2),
    ('List of Tables',             12, 12,   1, 2),
    ('List of Abbreviations',      13, 14,   1, 2),
    ('Ch.I — Introduction',        15, 19,   4, 7),
    ('Ch.II — Literature Survey',  20, 24,   3, 5),
    ('Ch.III — Methodology+Agents',25, 38,  15,20),
    ('Ch.IV — Results & Discussion',39,43,   5,10),
    ('Ch.V — Conclusions',         44, 45,   1, 2),
    ('References',                 46, 47,   2, 4),
    ('Appendix I (BOM)',           48, 48, None, None),
    ('Appendix II (Code)',         49, 50, None, None),
    ('Appendix III (Tables)',      51, 51, None, None),
    ('Appendix IV (Pub Cert)',     52, 52, None, None),
    ('Appendix V (Pub Proof)',     53, 53, None, None),
    ('Appendix VI (Work Contrib)', 54, 55, None, None),
    ('Appendix VII (Plagiarism)',  56, 56, None, None),
]
total = 56

print(f"{'Section':<38} {'Pgs':>4} {'Req':>8}  Status")
print('-' * 60)
all_ok = True
for section, start, end, lo, hi in sections:
    count = end - start + 1
    if lo is None:
        status = 'INFO'
        req = 'N/A'
    elif lo <= count <= hi:
        status = 'PASS ✓'
        req = f'{lo}-{hi}'
    else:
        status = 'FAIL ✗'
        req = f'{lo}-{hi}'
        all_ok = False
    print(f"{section:<38} {count:>4} {req:>8}  {status}")
print('-' * 60)
tot_ok = 45 <= total <= 75
tot_status = 'PASS ✓' if tot_ok else 'FAIL ✗'
print(f"{'TOTAL':<38} {total:>4} {'45-75':>8}  {tot_status}")
print()
overall = 'ALL PASS' if (all_ok and tot_ok) else 'HAS FAILURES'
print(f"Overall: {overall} — 5-chapter merged structure")
print(f"Chapter III now spans pages 25-38 = {38-25+1} pages (requirement: 15-20)")
