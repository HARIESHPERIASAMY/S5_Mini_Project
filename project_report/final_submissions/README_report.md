# SentinelMesh Academic Project Report Deliverables

This directory (`project_report/`) contains the complete **MAIN ACADEMIC PROJECT REPORT** for the Bachelor of Engineering (B.E.) degree submission to the **Department of Computer Science and Engineering, Bannari Amman Institute of Technology (BIT)**.

## Project & Team Information

- **Project Title:** Intelligent Multi-Agent Framework for Automated Software Testing and Bug Analysis
- **Project Name:** SentinelMesh
- **Academic Year:** 2026–2027
- **Programme:** Bachelor of Engineering (B.E.) in Computer Science and Engineering
- **Batch Members:**
  1. **Hariesh P** (Reg. No.: `7376241CS195`)  
     Department: Computer Science and Engineering (CSE)  
     Official Email: `harieshp.cs24@bitsathy.ac.in`
  2. **Midhum M** (Reg. No.: `7376242AL152`)  
     Department: Artificial Intelligence and Machine Learning (AIML)  
     Official Email: `midhumm.al24@bitsathy.ac.in`
- **Project Guide:**
  - **RAMYA R** (Guide ID: `CS1906`)  
    Department of Computer Science and Engineering, BIT

---

## Deliverables Index

1. **`SentinelMesh_Project_Report.md`**  
   The complete, authoritative **Main Academic Project Report** formatted in formal academic structure:
   - **Front Matter:**
     - Cover Page & Title Page (formal B.E. project submission format)
     - Bonafide Certificate (with guide RAMYA R and both candidates with individual departments)
     - Declaration (formal joint academic declaration)
     - Acknowledgement (academic acknowledgement)
     - Abstract, Table of Contents, List of Figures, List of Tables, List of Abbreviations
   - **Chapter I — Introduction:** Background, automated testing in CI/CD, limitations of manual defect analysis, multi-agent rationale, problem statement, objectives, scope, proposed solution, significance, and report organization.
   - **Chapter II — Literature Survey:** Theoretical foundations, static analysis, AST grammars, test synthesis, defect classification, root-cause slicing, APR patch verification, multi-agent LLM systems, mutation testing, comparative analysis table, and identified research gaps.
   - **Chapter III — Objectives and Methodology:** Functional and non-functional requirements, hardware/software specifications, existing system analysis, high-level architecture topology, end-to-end workflow, data flow diagrams (Level 0 and Level 1 DFD), agent coordination, relational ER schema, and subprocess sandboxing safety.
   - **Chapter IV — System Design and Implementation:** In-depth technical breakdown of all nine agents (`OrchestratorAgent`, `StaticAnalysisAgent`, `TestGenerationAgent`, `TestExecutionAgent`, `BugClassificationAgent`, `RootCauseAgent`, `AutoFixAgent`, `CriticAgent`, `ReportAgent`), the AST mutation engine, sandbox runner with `psutil` process-tree termination, LLM provider abstraction (Offline, Gemini, OpenAI), SQLite WAL database layer, and React 19 / Vite dashboard.
   - **Chapter V — Testing, Results and Discussion:** Live runtime environment, health check verification (`/api/health`), evaluation on the reference `demo/ecommerce/` benchmark, defect diagnosis, pre-flight patch verification, multi-agent debate consensus, mutation testing score, and an audit status table of existing test suites.
   - **Chapter VI — Conclusion and Future Work:** Summary of achievements, technical contributions, verified implementation milestones, identified limitations, and future research directions.
   - **References:** Numbered IEEE-style citations ([1]–[28]) matching every in-text citation.
   - **Appendices A–F:** Project directory tree, REST API specification table, SQLite DDL schema, source code implementation excerpts, verification test matrix, and setup/execution manual.

2. **`SentinelMesh_Architecture_Diagrams/`**  
   A dedicated directory containing standalone, editable Mermaid diagram source files corresponding to the actual system implementation:
   - `01_system_architecture.mmd`: Multi-tier system topology diagram
   - `02_sequence_diagram.mmd`: End-to-end execution sequence diagram
   - `03_database_er.mmd`: Relational entity-relationship (ER) schema
   - `04_data_flow_diagram.mmd`: Level 0 and Level 1 Data Flow Diagrams (DFD)
   - `README.md`: Index and rendering instructions for Mermaid diagrams

---

## Remaining Official Placeholders to Finalize for Viva-Voce

The report is complete and verified against the actual codebase. The only placeholders remaining for final submission are institutional items that require physical/live examination:
1. **Physical Signatures:** Signature lines on the Bonafide Certificate, Declaration, and Internal/External Examiner evaluation rows.
2. **Supervisor & HOD Designations:** Official academic titles (e.g., Assistant Professor / Head of Department) and official examination date.

---

## Converting to `.docx` (Microsoft Word) or `.pdf`

- **Microsoft Word:**  
  Open `SentinelMesh_Project_Report.md` directly in Microsoft Word via **File $\rightarrow$ Open $\rightarrow$ All Files (\*.\*)**. Word automatically parses markdown tables, headers, and code blocks. You can save as `SentinelMesh_Project_Report.docx` or export to PDF.
- **Pandoc (CLI):**  
  ```bash
  pandoc project_report/SentinelMesh_Project_Report.md -o project_report/SentinelMesh_Project_Report.docx
  ```
- **Browser Print to PDF:**  
  Open the Markdown file in a browser or VS Code Markdown Preview, press `Ctrl+P`, select **"Save as PDF"**, and set margins to "Default" or "A4".
