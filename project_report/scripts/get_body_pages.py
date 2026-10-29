from pypdf import PdfReader

reader = PdfReader(r'output\Final_Project_Report.pdf')
targets = [
    'CHAPTER - I', 'CHAPTER - II', 'CHAPTER - III', 'CHAPTER - IV',
    'CHAPTER - V', 'CHAPTER - VI', 'REFERENCES', 'APPENDIX I',
    'APPENDIX II', 'APPENDIX III', 'APPENDIX IV', 'APPENDIX V',
    'APPENDIX VI', 'APPENDIX VII'
]

found = {}
for idx in range(14, len(reader.pages)):
    text = reader.pages[idx].extract_text() or ''
    for t in targets:
        if t not in found and t in text:
            found[t] = idx + 1 # 1-based page in PDF

with open('scratch_body_pages.txt', 'w', encoding='utf-8') as f:
    for t in targets:
        pdf_pg = found.get(t, -1)
        body_pg = pdf_pg - 14 if pdf_pg != -1 else -1
        f.write(f'{t}: PDF Page {pdf_pg}, Body Page {body_pg}\n')

print('Done writing scratch_body_pages.txt')
