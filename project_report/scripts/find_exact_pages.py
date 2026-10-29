from pypdf import PdfReader

reader = PdfReader(r'output\Final_Project_Report.pdf')
sections = [
    'ACKNOWLEDGEMENT', 'ABSTRACT', 'TABLE OF CONTENTS', 'LIST OF FIGURES',
    'LIST OF TABLES', 'LIST OF ABBREVIATIONS', 'CHAPTER - I', 'CHAPTER - II',
    'CHAPTER - III', 'CHAPTER - IV', 'CHAPTER - V', 'CHAPTER - VI',
    'REFERENCES', 'APPENDIX I', 'APPENDIX II', 'APPENDIX III',
    'APPENDIX IV', 'APPENDIX V', 'APPENDIX VI', 'APPENDIX VII'
]

found = {}
for idx, page in enumerate(reader.pages, 1):
    text = page.extract_text() or ''
    for s in sections:
        if s not in found and s in text:
            found[s] = idx

with open('scratch_pages.txt', 'w', encoding='utf-8') as f:
    for s in sections:
        f.write(f'{s}: Page {found.get(s, "NOT FOUND")}\n')
print('Wrote scratch_pages.txt successfully!')
