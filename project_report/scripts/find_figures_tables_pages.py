from pypdf import PdfReader

reader = PdfReader(r'output\Final_Project_Report.pdf')

figures = [
    "Figure 3.1", "Figure 3.2", "Figure 3.3", "Figure 3.5",
    "Figure 4.1", "Figure 4.2", "Figure 4.3", "Figure 4.4", "Figure 4.5",
    "Figure 5.1", "Figure 5.2", "Figure 5.3", "Figure 5.4"
]

tables = [
    "Table 2.1", "Table 3.1", "Table 3.2", "Table 4.1", "Table 4.2",
    "Table 4.3", "Table 4.4", "Table 5.1", "Table 5.2", "Table 5.3",
    "Table 5.4", "Table B.1"
]

fig_pages = {}
table_pages = {}

# Search body pages (15 to 57 in PDF, corresponding to body pages 1 to 43)
for idx in range(14, len(reader.pages)):
    text = reader.pages[idx].extract_text() or ''
    b_page = idx - 14 + 1
    for f in figures:
        if f not in fig_pages and f in text:
            fig_pages[f] = b_page
    for t in tables:
        if t not in table_pages and t in text:
            table_pages[t] = b_page

with open('scratch_fig_tab_pages.txt', 'w', encoding='utf-8') as out:
    out.write("FIGURES:\n")
    for f in figures:
        out.write(f"{f}: Body Page {fig_pages.get(f, 'NOT FOUND')}\n")
    out.write("\nTABLES:\n")
    for t in tables:
        out.write(f"{t}: Body Page {table_pages.get(t, 'NOT FOUND')}\n")

print("Done writing scratch_fig_tab_pages.txt")
