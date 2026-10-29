"""Patch the TOC entries in build_full_report_docx.py to reflect the merged 5-chapter structure."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('build_full_report_docx.py', encoding='utf-8') as f:
    content = f.read()

old_toc = '''        ("4", "PROPOSED WORK MODULES", "21"),
        ("4.1", "Multi-Agent Orchestrator Pipeline", "21"),
        ("4.2", "AST Static Analysis and Risk Scoring Engine", "22"),
        ("4.3", "Automated Test Case Generation Engine", "23"),
        ("4.4", "Sandboxed Execution and Flakiness Detection Engine", "23"),
        ("4.5", "Defect Classification and Deduplication Module", "24"),
        ("4.6", "Root-Cause Slicing and Causal Tracing Engine", "24"),
        ("4.7", "Automated Program Repair and Patch Verification", "24"),
        ("4.8", "Critic Debate and Consensus Review Engine", "25"),
        ("4.9", "AST Mutation Testing Engine and SQLite Persistence", "25"),
        ("5", "RESULTS AND DISCUSSION", "26"),
        ("5.1", "Results", "26"),
        ("5.2", "Significance, Strengths and Limitations of the Proposed Work", "29"),
        ("5.3", "Cost Benefit Analysis", "29"),
        ("6", "CONCLUSIONS AND SUGGESTIONS FOR FUTURE WORK", "31"),
        ("6.1", "Conclusion", "31"),
        ("6.2", "Suggestions for Future Work", "32"),
        ("", "REFERENCES", "33"),
        ("APPENDIX I", "Bill of Materials", "35"),
        ("APPENDIX II", "Coding Excerpts", "36"),
        ("APPENDIX III", "Standard Tables and Supplementary Data", "38"),
        ("APPENDIX IV", "Publication Certificate", "39"),
        ("APPENDIX V", "Publication Proof", "40"),
        ("APPENDIX VI", "Work Contribution", "41"),
        ("APPENDIX VII", "Plagiarism Report", "43")'''

new_toc = '''        ("3.4", "Autonomous Agent Module Design and Implementation", "21"),
        ("3.4.1", "Multi-Agent Orchestrator Pipeline", "21"),
        ("3.4.2", "AST Static Analysis and Risk Scoring Engine", "22"),
        ("3.4.3", "Automated Test Case Generation Engine", "23"),
        ("3.4.4", "Sandboxed Execution and Flakiness Detection Engine", "23"),
        ("3.4.5", "Defect Classification and Deduplication Module", "24"),
        ("3.4.6", "Root-Cause Slicing and Causal Tracing Engine", "24"),
        ("3.4.7", "Automated Program Repair and Patch Verification", "24"),
        ("3.4.8", "Critic Debate and Consensus Review Engine", "25"),
        ("3.4.9", "AST Mutation Testing Engine and SQLite Persistence", "25"),
        ("4", "RESULTS AND DISCUSSION", "27"),
        ("4.1", "Results", "27"),
        ("4.2", "Significance, Strengths and Limitations of the Proposed Work", "30"),
        ("4.3", "Cost Benefit Analysis", "30"),
        ("5", "CONCLUSIONS AND SUGGESTIONS FOR FUTURE WORK", "32"),
        ("5.1", "Conclusion", "32"),
        ("5.2", "Suggestions for Future Work", "33"),
        ("", "REFERENCES", "34"),
        ("APPENDIX I", "Bill of Materials", "36"),
        ("APPENDIX II", "Coding Excerpts", "37"),
        ("APPENDIX III", "Standard Tables and Supplementary Data", "39"),
        ("APPENDIX IV", "Publication Certificate", "40"),
        ("APPENDIX V", "Publication Proof", "41"),
        ("APPENDIX VI", "Work Contribution", "42"),
        ("APPENDIX VII", "Plagiarism Report", "44")'''

# Normalize line endings for search
old_toc_norm = old_toc.replace('\n', '\r\n')
if old_toc_norm in content:
    content = content.replace(old_toc_norm, new_toc.replace('\n', '\r\n'))
    print("Replaced with CRLF line endings.")
elif old_toc in content:
    content = content.replace(old_toc, new_toc)
    print("Replaced with LF line endings.")
else:
    print("ERROR: Target TOC block not found. Searching for key lines...")
    for line in old_toc.split('\n'):
        if line.strip() and line.strip() not in content:
            print(f"  MISSING: {line.strip()[:60]}")
    import sys; sys.exit(1)

with open('build_full_report_docx.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("TOC entries updated successfully.")
