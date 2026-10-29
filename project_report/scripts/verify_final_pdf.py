from pypdf import PdfReader

reader = PdfReader(r'output\Final_Project_Report.pdf')
print(f'Total Pages: {len(reader.pages)}')

sample_pages = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 20, 25, 30, 35, 40, 45, 50, len(reader.pages)]

for p_num in sample_pages:
    if p_num <= len(reader.pages):
        page = reader.pages[p_num - 1]
        text = page.extract_text() or ''
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        first = lines[0] if lines else 'EMPTY'
        last = lines[-1] if lines else 'EMPTY'
        print(f'Page {p_num:02d}: Top -> "{first[:45]}" | Bottom -> "{last[:45]}"')
