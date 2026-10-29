import re

with open('build_full_report_docx.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_toc_entries = '''toc_entries = [
        ("", "ACKNOWLEDGEMENT", "iii"),
        ("", "ABSTRACT", "iv"),
        ("", "TABLE OF CONTENTS", "v"),
        ("", "LIST OF FIGURES", "vii"),
        ("", "LIST OF TABLES", "viii"),
        ("", "LIST OF ABBREVIATIONS", "ix"),
        ("1", "INTRODUCTION", "1"),
        ("1.1", "Background of the Work", "2"),
        ("1.2", "Motivation (Scope of the Proposed Work)", "3"),
        ("2", "LITERATURE SURVEY", "6"),
        ("2.1", "Foundations of Automated Software Testing", "6"),
        ("2.2", "Static Code Analysis and AST Complexity Profiling", "7"),
        ("2.3", "Dynamic Test Generation and Subprocess Sandboxing", "7"),
        ("2.4", "Automated Program Repair and Pre-flight Verification", "8"),
        ("2.5", "Multi-Agent Architectures in Software Engineering", "8"),
        ("2.6", "Mutation Testing and Test Suite Adequacy", "9"),
        ("3", "OBJECTIVES AND METHODOLOGY", "11"),
        ("3.1", "Objectives of the Proposed Work", "11"),
        ("3.2", "Architecture and Flow Diagram of the Proposed Work", "12"),
        ("3.3", "Selection of Components, Tools, and Testing Methods", "17"),
        ("4", "PROPOSED WORK MODULES", "21"),
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
        ("APPENDIX VII", "Plagiarism Report", "43")
    ]'''

new_lof_entries = '''figures = [
        ("Figure 3.1", "SentinelMesh High-Level Multi-Tier Architectural Topology", "13"),
        ("Figure 3.2", "End-to-End Multi-Agent Orchestration Sequence Diagram", "14"),
        ("Figure 3.3", "Level 0 and Level 1 Subsystem Data Flow Diagram (DFD)", "16"),
        ("Figure 3.4", "Relational Entity-Relationship (ER) Database Schema", "17")
    ]'''

new_lot_entries = '''tables = [
        ("Table 2.1", "Comparative Analysis of Existing SQA and Defect Analysis Frameworks", "8"),
        ("Table 3.1", "Minimum Hardware Specifications for Local Execution", "18"),
        ("Table 3.2", "Core Software Stack and Dependency Specifications", "19"),
        ("Table 4.1", "Implemented Security and Reliability Heuristic Code Smells", "22"),
        ("Table 5.1", "Verified E-Commerce Benchmark Injected Defects and Agent Outcomes", "27"),
        ("Table 5.2", "Benchmarking SentinelMesh Against Baseline Tools", "28"),
        ("Table 5.3", "Cost-Benefit Economic Analysis of SentinelMesh Framework", "30"),
        ("Table B.1", "SentinelMesh REST API Specification and HTTP Status Codes", "38")
    ]'''

content = re.sub(r'toc_entries = \[.*?\]\n', new_toc_entries + '\n', content, flags=re.DOTALL)
content = re.sub(r'figures = \[.*?\]\n', new_lof_entries + '\n', content, flags=re.DOTALL)
content = re.sub(r'tables = \[.*?\]\n', new_lot_entries + '\n', content, flags=re.DOTALL)

# Also ensure Figure 3.4 caption matches the List of Figures
content = content.replace("Figure 3.5: Relational Entity-Relationship (ER) Database Schema", "Figure 3.4: Relational Entity-Relationship (ER) Database Schema")

with open('build_full_report_docx.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Updated build_full_report_docx.py successfully!')
