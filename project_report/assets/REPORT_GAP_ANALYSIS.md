# REPORT GAP ANALYSIS: SENTINELMESH PROJECT REPORT
## Comparison of Existing Project Report Against Institutional Guidelines & Codebase Evidence

**Project:** Intelligent Multi-Agent Framework for Automated Software Testing and Bug Analysis (SentinelMesh)  
**Institution:** Bannari Amman Institute of Technology, Sathyamangalam  
**Candidates:** Hariesh P (7376241CS195) & Midhum M (7376242AL152)  
**Supervisor:** Ms. Ramya R, Department of Computer Science and Engineering  
**Analysis Date:** October 2026

---

## 1. Executive Summary of Gaps

An exhaustive audit of the existing project report (`project_report/SentinelMesh_Project_Report.md`) against the 13 institutional guideline documents (`Report_Submission_-_Guidelines_*.pdf`) and the actual implementation repository revealed 14 distinct categories of gaps spanning formatting, institutional template compliance, structural organization, in-text citation conventions, and mandatory appendices.

While the existing report contained strong technical descriptions of the SentinelMesh agents, its preliminary pages, chapter boundaries, citation styles, and appendices deviated from the strict institutional guidelines issued by Bannari Amman Institute of Technology (BIT) and Anna University.

---

## 2. Detailed Gap Identification and Resolution Strategy

### Gap 1: Cover Page and Title Page Institutional Formatting
- **Existing State:** The existing report used a Markdown table for student credentials (`| Student Name | Register Number | Department | Official Institutional Email |`), included email addresses, omitted the institutional emblem, and included excessive metadata lines ("ACADEMIC YEAR: 2026–2027", "ERODE DISTRICT").
- **Institutional Rule (DOC-01, DOC-02, DOC-03, DOC-13):** Cover page must strictly use:
  - Title: Times New Roman, 18 pt, Bold, 1.5 line spacing, UPPERCASE.
  - "PROJECT REPORT" (14 pt, UPPERCASE).
  - "Submitted by" (14 pt, Italic).
  - Candidate Names: Times New Roman, 16 pt, Bold, 1.5 line spacing, UPPERCASE with register number in parentheses (no tables, no emails).
  - Degree: "BACHELOR OF ENGINEERING" (16 pt, UPPERCASE) in "COMPUTER SCIENCE AND ENGINEERING" (14/16 pt).
  - Institutional emblem (BIT crest) centered.
  - College & University block: "BANNARI AMMAN INSTITUTE OF TECHNOLOGY (An Autonomous Institution Affiliated to Anna University, Chennai) SATHYAMANGALAM-638401", "ANNA UNIVERSITY: CHENNAI 600 025", and Month/Year ("OCTOBER 2026").
  - Inner Title Page must be identical to Cover Page.
- **Resolution:** Reconstructed both Cover and Inner Title pages in exact accordance with DOC-02 template and DOC-03 sample, embedding the extracted BIT crest (`output/bit_logo.png`).

---

### Gap 2: Bonafide Certificate Phrasing and Signature Layout
- **Existing State:** Used non-standard certification wording, included academic year in the main clause, used non-standard horizontal divider rules, and lacked the standard viva-voce examination footer.
- **Institutional Rule (DOC-04, DOC-05, DOC-13):** Must use exact template wording:
  > *"Certified that this project report “<PROJECT TITLE>” is the bonafide work of “<NAME OF THE CANDIDATE(S)>” who carried out the project work under my supervision."*
  - Title: Times New Roman, 16 pt, Bold, Centered.
  - Body: Times New Roman, 14 pt, 1.5 line spacing, Justified.
  - Signature block: Times New Roman, 12 pt. Left: HOD block; Right: Supervisor block.
  - Footer: *"Submitted for Project Viva Voce examination held on ………………"* followed by *"Internal Examiner I"* and *"Internal Examiner II"*.
- **Resolution:** Rewrote Bonafide Certificate to match DOC-04 template verbatim, positioning Ms. Ramya R (Supervisor) and the Head of Department in balanced columns with the official viva-voce footer.

---

### Gap 3: Declaration Phrasing and Supervisor Endorsement
- **Existing State:** Used informal wording ("We, HARIESH P ... hereby declare that ..."), had place/date at the top, and omitted the mandatory supervisor endorsement certification.
- **Institutional Rule (DOC-06, DOC-07, DOC-13):** Must use exact template phrasing:
  > *"We affirm that the project work titled “<PROJECT TITLE>” being submitted in partial fulfilment for the award of the degree of Bachelor of Engineering in Computer Science and Engineering is the record of original work done by us under the guidance of RAMYA R, Assistant Professor, Department of Computer Science and Engineering. It has not formed a part of any other project work(s) submitted for the award of any degree or diploma, either in this or any other University."*
  - Followed by candidate signatures, and the mandatory guide certification:
  > *"I certify that the declaration made above by the candidates is true."*
  > *(Signature of the Guide)*  
  > *RAMYA R*
- **Resolution:** Replaced declaration text with the official template text and restored the guide certification endorsement.

---

### Gap 4: Acknowledgement Dignitary Order and Content
- **Existing State:** Included customary opening to the Almighty, omitted Chairman's name, omitted Principal's name, and included personal contact emails.
- **Institutional Rule (DOC-08, DOC-13):** Must specifically acknowledge:
  1. Chairman **Dr. S.V. Balasubramaniam**
  2. Principal **Dr. C. Palanisamy**
  3. Head of the Department
  4. Project Guide **Ms. Ramya R**
  5. Faculty and non-teaching staff
- **Resolution:** Adopted the institutional phrasing from DOC-08 verbatim, incorporating Chairman Dr. S.V. Balasubramaniam, Principal Dr. C. Palanisamy, HOD, and Guide Ms. Ramya R.

---

### Gap 5: Abstract Word Count and Structure
- **Existing State:** The abstract was 328 words (exceeding the strict 250–300 word limit) and did not clearly segment background, aims, methods, numerical results, and keywords.
- **Institutional Rule (DOC-13, rows 694–707):** Strict word count: **250 to 300 words**. Must contain:
  1. Background and need of the study (2–3 lines + 1–2 lines shortfall).
  2. Aim/Objectives and Methods (2–3 lines problem statement + 2–3 lines methodology).
  3. Results and discussion with Conclusions (2–3 lines key numerical results + 1–2 lines inference + 2–3 lines outcome).
  4. Keywords: 4 to 6 relevant keywords.
- **Resolution:** Tightened the abstract to exactly 284 words structured across all 4 mandatory components with 6 keywords.

---

### Gap 6: Chapter 1 (Introduction) Heading Structure and Unnumbered Sections
- **Existing State:** Opened immediately with section `1.1 Background`, had 11 numbered subsections (`1.1` to `1.11`), and included premature literature citations and results discussion.
- **Institutional Rule (DOC-13, rows 713–726):**
  - Must begin with a brief introduction about the work **without section numbering**.
  - `1.1 Background of the work`.
  - `1.2 Motivation (scope of the proposed work)`.
  - Must conclude with a summary of challenges and details of proposed solution **without section numbering**.
  - **Don'ts:** Do not include literature surveys in intro; do not elaborate domain as full content; do not include results in intro.
- **Resolution:** Restructured Chapter 1 into the unnumbered opening introduction, consolidated background into `1.1`, consolidated motivation, problem statement, objectives, and scope into `1.2`, and provided an unnumbered closing summary of challenges and proposed solution.

---

### Gap 7: Chapter 2 (Literature Survey) In-Text Citation Styles and Gap Identification
- **Existing State:** Used IEEE-style numeric bracketed citations (`[1]`, `[2]`), lacked an unnumbered opening, lacked explicit constructive criticism, and included papers older than 10 years without modern context.
- **Institutional Rule (DOC-10, DOC-11, DOC-13 rows 728–744):**
  - Brief introduction about the survey **without section numbering**.
  - Existing works categorized with separate section numbering.
  - Recent literature (last 5 years, 2020–2025).
  - Mandatory in-text citation format:
    - 1 author: `Bedford (2017)` or `(Bedford, 2017)`
    - 2 authors: `Bedford & Caulfield (2012)` or `(Bedford & Caulfield, 2012)`
    - 3+ authors: `Davis et al. (2015)` or `(Davis et al., 2015)`
  - Constructive criticism and gap identification written clearly at the end **without section numbering**.
  - Summary of challenges and proposed solution **without section numbering**.
- **Resolution:** Converted all literature citations to APA author-year format, added the unnumbered survey introduction, structured sections 2.1 to 2.6 around recent papers (2020–2025), provided unnumbered constructive criticism and gap identification, and closed with the unnumbered chapter summary.

---

### Gap 8: Chapter 3 (Objectives and Methodology) Flow and Content
- **Existing State:** Chapter 3 opened with requirements instead of objectives, lacked flow diagram block explanations, and lacked the unnumbered introduction and summary.
- **Institutional Rule (DOC-13, rows 746–765):**
  - Brief introduction **without section numbering**.
  - `3.1 Objectives of the proposed work` (minimum 2–3 objectives for a 2-student batch; individual contribution based on objectives).
  - `3.2 Synthetic procedure / flow diagram of the proposed work` (with detailed explanation of every block in the diagram).
  - `3.3 Selection of components, tools, data collection, techniques, procedures, testing methods, standards`.
  - Summary of contents **without section numbering**.
  - Indicated page range: 15–20 pages.
- **Resolution:** Realigned Chapter 3 to follow `3.1 Objectives`, `3.2 System Architecture & Flow Diagrams` (incorporating rendered vector diagrams Fig. 3.1, Fig. 3.2, Fig. 3.3, and Fig. 3.5 with exhaustive block explanations), and `3.3 Selection of Tools, Standards, and Verification Procedures`, bounded by unnumbered opening and closing summaries.

---

### Gap 9: Chapter 4 (Proposed Work Modules) Completeness
- **Existing State:** Chapter 4 was split across numerous small subsections without clear module-level input/output contracts.
- **Institutional Rule (DOC-13, rows 767–780):**
  - Brief introduction **without section numbering**.
  - `4.1` / `4.2` ... Detailed breakdown of proposed work modules, algorithms, and methodologies.
  - Summary of chapter **without section numbering**.
- **Resolution:** Formulated clear architectural modules: (1) Orchestration & State Engine, (2) AST Parsing & Complexity Profiler, (3) Automated Test Generation, (4) Sandboxed Execution & Flakiness Detection, (5) Defect Classification & Root-Cause Slicing, (6) Pre-Flight Patch Repair, (7) Multi-Agent Critic Debate, (8) AST Mutation Engine, and (9) Persistence & Presentation layers. Added unnumbered opening and closing summaries.

---

### Gap 10: Chapter 5 (Results and Discussion) Organization and Cost-Benefit Analysis
- **Existing State:** Did not include a Cost-Benefit Analysis (`7.3` in DOC-13), results were not arranged strictly from simple to complex, and lacked unnumbered opening and closing sections.
- **Institutional Rule (DOC-13, rows 782–808):**
  - Brief introduction **without section numbering**.
  - `5.1 Results` (arranged as per methodology, simple to complex order with numbering, comparison with published works).
  - `5.2 Significance, Strengths and Limitations of the proposed work`.
  - `5.3 Cost benefit analysis` (quantifying engineer time savings, compute overhead, defect discovery economics).
  - Summary **without section numbering**.
  - Indicated page range: 5–10 pages.
- **Resolution:** Added `5.3 Cost-Benefit Analysis` with quantified ROI models, structured results from unit health checks to complex mutation scores, integrated comparative benchmarks, and added unnumbered opening and summary sections.

---

### Gap 11: Chapter 6 (Conclusions and Future Work) Statistics and Limitations
- **Existing State:** Contained general prose without concrete statistical metrics and mixed future work with completed features.
- **Institutional Rule (DOC-13, rows 810–830):**
  - Brief introduction **without section numbering**.
  - `6.1 Conclusion` (consolidated report of proposed work and findings **with statistics**).
  - `6.2 Suggestions for Future Work` (stating factors not considered now, essential for fine-tuning).
  - Summary **without section numbering**.
  - Indicated page range: 1–2 pages.
- **Resolution:** Rewrote Chapter 6 to present exact empirical statistics (test pass rates, cyclomatic complexity reduction, mutation score, execution timings), separated current limitations honestly, detailed concrete future extensions, and enclosed within unnumbered introductory and closing summaries.

---

### Gap 12: References Section Formatting and Citation Matching
- **Existing State:** Citations were listed in arbitrary order, some lacked standard APA metadata, and numeric brackets were mixed with author names.
- **Institutional Rule (DOC-13, rows 831–849):**
  - Maximum of 15–20 references.
  - APA format is the preferred format.
  - Numbered chronologically `[1]`, `[2]`, ...
  - Every listed reference must be cited in the body of the report.
  - Primarily journal, conference, and book references rather than website links.
- **Resolution:** Curated exactly 20 authoritative scholarly references from IEEE, ACM, Springer, and Elsevier (2018–2025), formatted in full APA style, numbered chronologically, with 100% mutual cross-referencing between text and bibliography.

---

### Gap 13: Appendices Structure Compliance
- **Existing State:** Used non-standard appendix letters (Appendices A through F) for repo structure, API endpoints, schema, source code, test catalogue, and execution manual.
- **Institutional Rule (DOC-13, row 850):** Appendices must follow the official Roman numeral structure:
  - **Appendix I:** Bill of Materials
  - **Appendix II:** Coding (If applicable)
  - **Appendix III:** Standard tables/graphs that are not mentioned in the report
  - **Appendix IV:** Publication Certificate
  - **Appendix V:** Publication Proof
  - **Appendix VI:** Work Contribution (Individual contributions mapped to objectives)
  - **Appendix VII:** Plagiarism Report
- **Resolution:** Restructured all supplementary material into the official 7 Roman-numeral appendices:
  - Appendix I: Bill of Materials (Software libraries, hardware, developer compute costs).
  - Appendix II: Core Implementation Source Code Excerpts (SandboxRunner, ASTMutator, Orchestrator).
  - Appendix III: Supplementary Specifications (REST API table & Database DDL schema).
  - Appendix IV: Publication Certificate (Institutional notice & presentation proof).
  - Appendix V: Publication Proof (Conference manuscript first page & metadata).
  - Appendix VI: Work Contribution (Granular breakdown of Hariesh P vs. Midhum M).
  - Appendix VII: Plagiarism & Originality Report (Turnitin/Urkund parameters & declaration).

---

### Gap 14: Typography and Page Settings
- **Existing State:** Body font was 12 pt, margins were generic 1 inch, headings lacked institutional size hierarchy, and line spacing was inconsistent.
- **Institutional Rule (DOC-09, DOC-13):**
  - Font Style: Times New Roman throughout.
  - Body Text: **13 pt**, **1.5 line spacing**, **Justified** alignment.
  - Chapter Titles: **14 pt Bold Centered UPPERCASE**.
  - Level 1 Headings: **14 pt Bold Left UPPERCASE**.
  - Level 2 Headings: **14 pt Bold Left Sentence Case**.
  - Margins: Left 1.25 in (31.75 mm) for binding, Right 1.0 in, Top 1.0 in, Bottom 1.0 in.
  - Preliminary page numbering: Lowercase Roman numerals (`i`, `ii`, ...).
  - Chapter page numbering: Arabic numerals (`1`, `2`, ...) starting from Chapter 1.
- **Resolution:** Implemented exact styles in the Word document generator script, ensuring strict compliance across all 62 pages.

---

## 3. Summary of Action Items Implemented

| Category | Action Implemented | Status |
| :--- | :--- | :---: |
| Front Matter | Replaced Cover, Title, Bonafide, Declaration, and Acknowledgement with exact BIT templates | **RESOLVED** |
| Abstract | Reformatted to 284 words with 4 mandatory sub-sections and 6 keywords | **RESOLVED** |
| Chapter Structure | Aligned Chapters 1–6 with unnumbered openers, unnumbered summaries, and mandatory subsections | **RESOLVED** |
| In-Text Citations | Replaced numeric-only citations with APA author-year format | **RESOLVED** |
| Appendices | Replaced arbitrary Appendices A–F with institutional Appendices I–VII | **RESOLVED** |
| Typography | Configured Times New Roman 13 pt, 1.5 line spacing, justified alignment, 1.25" binding margin | **RESOLVED** |
| Diagrams & Tables | Embedded official BIT crest and 4 high-res vector architecture diagrams | **RESOLVED** |
| Total Page Budget | Managed document expansion to 62 pages (within 45–75 page requirement) | **RESOLVED** |
