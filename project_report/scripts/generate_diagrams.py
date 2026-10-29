import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os
from PIL import Image

os.makedirs('report_images', exist_ok=True)

plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'

def draw_fig_3_1():
    # Figure 3.1: System Architecture Diagram (like PDF 1 page 20)
    fig, ax = plt.subplots(figsize=(10, 4.4), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Main boxes
    # Users
    ax.add_patch(patches.FancyBboxPatch((2, 50), 14, 42, boxstyle="round,pad=1", ec="#222222", fc="#F8FAFC", lw=1.5))
    ax.text(9, 87, "Users", fontsize=11, fontweight='bold', ha='center', va='center')
    ax.text(9, 74, "Developer", fontsize=9, ha='center', va='center')
    ax.text(9, 62, "QA Engineer", fontsize=9, ha='center', va='center')
    ax.text(9, 53, "(Local Workstation)", fontsize=8, fontstyle='italic', ha='center', va='center', color='#555555')

    # Arrow 1
    ax.annotate("", xy=(21, 71), xytext=(16, 71), arrowprops=dict(arrowstyle="->", lw=1.5, color="#222222"))
    ax.text(18.5, 75, "HTTP / WS", fontsize=7.5, ha='center', va='center')

    # Frontend
    ax.add_patch(patches.FancyBboxPatch((21, 50), 19, 42, boxstyle="round,pad=1", ec="#222222", fc="#F8FAFC", lw=1.5))
    ax.text(30.5, 87, "Frontend (React 19 + Vite)", fontsize=10, fontweight='bold', ha='center', va='center')
    ax.text(30.5, 77, "• Swarm Network Graph", fontsize=8, ha='center', va='center')
    ax.text(30.5, 69, "• Risk Heatmap Viewer", fontsize=8, ha='center', va='center')
    ax.text(30.5, 61, "• Self-Healing Bug Ledger", fontsize=8, ha='center', va='center')
    ax.text(30.5, 53, "• Critic Debate Panel", fontsize=8, ha='center', va='center')

    # Arrow 2
    ax.annotate("", xy=(46, 71), xytext=(40, 71), arrowprops=dict(arrowstyle="->", lw=1.5, color="#222222"))
    ax.text(43, 75, "REST / WS", fontsize=7.5, ha='center', va='center')

    # Backend
    ax.add_patch(patches.FancyBboxPatch((46, 50), 25, 42, boxstyle="round,pad=1", ec="#222222", fc="#F8FAFC", lw=1.5))
    ax.text(58.5, 87, "Backend (FastAPI + Python)", fontsize=10, fontweight='bold', ha='center', va='center')
    ax.text(58.5, 77, "• REST API (Pydantic v2)", fontsize=8, ha='center', va='center')
    ax.text(58.5, 69, "• Multi-Agent Orchestrator", fontsize=8, ha='center', va='center')
    ax.text(58.5, 61, "• AST Static Parser & Slicer", fontsize=8, ha='center', va='center')
    ax.text(58.5, 53, "• EventBus WebSocket Stream", fontsize=8, ha='center', va='center')

    # Arrow 3
    ax.annotate("", xy=(77, 71), xytext=(71, 71), arrowprops=dict(arrowstyle="<->", lw=1.5, color="#222222"))
    ax.text(74, 75, "aiosqlite", fontsize=7.5, ha='center', va='center')

    # Database
    ax.add_patch(patches.FancyBboxPatch((77, 50), 20, 42, boxstyle="round,pad=1", ec="#222222", fc="#F8FAFC", lw=1.5))
    ax.text(87, 87, "Database (SQLite)", fontsize=10, fontweight='bold', ha='center', va='center')
    ax.text(87, 77, "• WAL Concurrency Mode", fontsize=8, ha='center', va='center')
    ax.text(87, 69, "• 8 Normalized Entities", fontsize=8, ha='center', va='center')
    ax.text(87, 61, "• Event-Sourced Logs", fontsize=8, ha='center', va='center')
    ax.text(87, 53, "• FK Cascade Integrity", fontsize=8, ha='center', va='center')

    # Lower Boxes: Sandbox and Inference Layer
    # Sandbox Runner
    ax.add_patch(patches.FancyBboxPatch((18, 6), 31, 35, boxstyle="round,pad=1", ec="#222222", fc="#FFFFFF", lw=1.3))
    ax.text(33.5, 36, "Execution & Sandbox Boundary", fontsize=9.5, fontweight='bold', ha='center', va='center')
    ax.text(33.5, 27, "• Subprocess Isolation & Process Groups", fontsize=8, ha='center', va='center')
    ax.text(33.5, 20, "• psutil Recursive Process-Tree Guard", fontsize=8, ha='center', va='center')
    ax.text(33.5, 13, "• Hard CPU / Wall-Clock Timeout (10s)", fontsize=8, ha='center', va='center')

    # Intelligence & Security Layer
    ax.add_patch(patches.FancyBboxPatch((55, 6), 37, 35, boxstyle="round,pad=1", ec="#222222", fc="#FFFFFF", lw=1.3))
    ax.text(73.5, 36, "Intelligence & Security Layer", fontsize=9.5, fontweight='bold', ha='center', va='center')
    ax.text(73.5, 27, "• Air-Gapped Offline Heuristic Engine", fontsize=8, ha='center', va='center')
    ax.text(73.5, 20, "• Modular LLM Adapters (Gemini / OpenAI)", fontsize=8, ha='center', va='center')
    ax.text(73.5, 13, "• MD5 Defect Fingerprinting & Deduplication", fontsize=8, ha='center', va='center')

    # Connecting arrows to lower boxes
    ax.annotate("", xy=(33.5, 41), xytext=(52, 50), arrowprops=dict(arrowstyle="->", lw=1.2, color="#444444", linestyle="--"))
    ax.annotate("", xy=(73.5, 41), xytext=(65, 50), arrowprops=dict(arrowstyle="->", lw=1.2, color="#444444", linestyle="--"))

    plt.tight_layout()
    fig.savefig('report_images/fig_3_1_architecture.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved fig_3_1_architecture.png")

def draw_fig_3_2():
    # Figure 3.2: Multi-Agent Orchestration Workflow (like PDF 1 page 24)
    fig, ax = plt.subplots(figsize=(10, 4.4), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Row 1: Steps 1 to 4
    steps_r1 = [
        ("1", "Trigger Analysis", "• Upload folder / repo\n• Select LLM provider\n• Dispatch Run event", 3),
        ("2", "Orchestrator Init", "• Init SQLite run record\n• Set status RUNNING\n• Check cancel token", 27.5),
        ("3", "Static AST Analysis", "• ast.parse source files\n• Calculate CC(f) metric\n• Detect code smells", 52),
        ("4", "Test Synthesis", "• Inspect signatures\n• Generate pytest files\n• Assert boundaries", 76.5)
    ]
    for num, title, desc, x in steps_r1:
        ax.add_patch(patches.FancyBboxPatch((x, 56), 20.5, 38, boxstyle="round,pad=1", ec="#222222", fc="#FFFFFF", lw=1.3))
        ax.add_patch(patches.Circle((x + 2.8, 88.5), 2.2, ec="#222222", fc="#222222"))
        ax.text(x + 2.8, 88.5, num, fontsize=9, fontweight='bold', color="#FFFFFF", ha='center', va='center')
        ax.text(x + 11.5, 88.5, title, fontsize=8.5, fontweight='bold', ha='center', va='center')
        ax.text(x + 10.2, 69, desc, fontsize=7.5, ha='center', va='center')

    # Arrows Row 1
    ax.annotate("", xy=(27.5, 75), xytext=(23.5, 75), arrowprops=dict(arrowstyle="->", lw=1.3, color="#222222"))
    ax.annotate("", xy=(52, 75), xytext=(48, 75), arrowprops=dict(arrowstyle="->", lw=1.3, color="#222222"))
    ax.annotate("", xy=(76.5, 75), xytext=(72.5, 75), arrowprops=dict(arrowstyle="->", lw=1.3, color="#222222"))

    # Turn down arrow from step 4 to step 5
    ax.annotate("", xy=(86.7, 48), xytext=(86.7, 56), arrowprops=dict(arrowstyle="->", lw=1.3, color="#222222"))

    # Row 2: Steps 5 to 7 + End (right to left or left to right)
    steps_r2 = [
        ("5", "Sandboxed Execution", "• Isolated subprocess\n• psutil timeout guard\n• Compute branch cov", 3),
        ("6", "Defect Slicing & Patch", "• MD5 deduplication\n• Backward AST slicing\n• Synthesize diff patch", 27.5),
        ("7", "Pre-Flight & Debate", "• Temp sandbox verify\n• Critic debate rounds\n• Consensus score >=0.85", 52)
    ]
    for num, title, desc, x in steps_r2:
        ax.add_patch(patches.FancyBboxPatch((x, 6), 20.5, 38, boxstyle="round,pad=1", ec="#222222", fc="#FFFFFF", lw=1.3))
        ax.add_patch(patches.Circle((x + 2.8, 38.5), 2.2, ec="#222222", fc="#222222"))
        ax.text(x + 2.8, 38.5, num, fontsize=9, fontweight='bold', color="#FFFFFF", ha='center', va='center')
        ax.text(x + 11.5, 38.5, title, fontsize=8.5, fontweight='bold', ha='center', va='center')
        ax.text(x + 10.2, 19, desc, fontsize=7.5, ha='center', va='center')

    # Arrow from 7 to End
    ax.annotate("", xy=(27.5, 25), xytext=(23.5, 25), arrowprops=dict(arrowstyle="<-", lw=1.3, color="#222222"))
    ax.annotate("", xy=(52, 25), xytext=(48, 25), arrowprops=dict(arrowstyle="<-", lw=1.3, color="#222222"))
    ax.annotate("", xy=(72.5, 25), xytext=(76.5, 25), arrowprops=dict(arrowstyle="<-", lw=1.3, color="#222222"))

    # End Box
    ax.add_patch(patches.FancyBboxPatch((76.5, 6), 20.5, 38, boxstyle="round,pad=1", ec="#222222", fc="#F1F5F9", lw=1.3))
    ax.text(86.7, 36, "Pipeline Complete", fontsize=9, fontweight='bold', ha='center', va='center')
    ax.text(86.7, 23, "• AST Mutation Score\n• Update SQLite Run\n• Broadcast WebSocket", fontsize=7.5, ha='center', va='center')
    ax.add_patch(patches.FancyBboxPatch((81.7, 9), 10, 6, boxstyle="round,pad=0.5", ec="#16A34A", fc="#DCFCE7", lw=1))
    ax.text(86.7, 12, "COMPLETED", fontsize=7.5, fontweight='bold', color="#15803D", ha='center', va='center')

    plt.tight_layout()
    fig.savefig('report_images/fig_3_2_orchestration.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved fig_3_2_orchestration.png")

def draw_fig_3_3():
    # Figure 3.3: AST Static Code Analysis Workflow (vertical flowchart like PDF 1 page 26)
    fig, ax = plt.subplots(figsize=(6.2, 7.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Start pill
    ax.add_patch(patches.FancyBboxPatch((38, 93), 24, 5, boxstyle="round,pad=1", ec="#222222", fc="#FFFFFF", lw=1.3))
    ax.text(50, 95.5, "Start", fontsize=9, fontweight='bold', ha='center', va='center')
    ax.annotate("", xy=(50, 88), xytext=(50, 93), arrowprops=dict(arrowstyle="->", lw=1.3, color="#222222"))

    # Step 1: Ingest Python Source
    ax.add_patch(patches.FancyBboxPatch((20, 80), 60, 8, boxstyle="round,pad=0.8", ec="#222222", fc="#FFFFFF", lw=1.2))
    ax.text(50, 84, "Receive Python Source Files (.py)", fontsize=8.5, fontweight='bold', ha='center', va='center')
    ax.text(90, 84, "Input: source files,\npackages, config", fontsize=6.5, color="#555555", ha='left', va='center')
    ax.annotate("", xy=(50, 75), xytext=(50, 80), arrowprops=dict(arrowstyle="->", lw=1.3, color="#222222"))

    # Step 2: AST Parsing
    ax.add_patch(patches.FancyBboxPatch((20, 67), 60, 8, boxstyle="round,pad=0.8", ec="#222222", fc="#FFFFFF", lw=1.2))
    ax.text(50, 71, "Parse Source via Native Python ast Module", fontsize=8.5, fontweight='bold', ha='center', va='center')
    ax.text(90, 71, "✓ Syntax validation\n✓ Zero external linter", fontsize=6.5, color="#15803D", ha='left', va='center')
    ax.annotate("", xy=(50, 62), xytext=(50, 67), arrowprops=dict(arrowstyle="->", lw=1.3, color="#222222"))

    # Step 3: Branch Counting CC(f)
    ax.add_patch(patches.FancyBboxPatch((20, 54), 60, 8, boxstyle="round,pad=0.8", ec="#222222", fc="#FFFFFF", lw=1.2))
    ax.text(50, 58, "Traverse AST & Compute Cyclomatic Complexity CC(f)", fontsize=8.5, fontweight='bold', ha='center', va='center')
    ax.text(90, 58, "✓ If, For, While nodes\n✓ Try/Except branches", fontsize=6.5, color="#15803D", ha='left', va='center')
    ax.annotate("", xy=(50, 49), xytext=(50, 54), arrowprops=dict(arrowstyle="->", lw=1.3, color="#222222"))

    # Step 4: Code Smell Matching
    ax.add_patch(patches.FancyBboxPatch((20, 41), 60, 8, boxstyle="round,pad=0.8", ec="#222222", fc="#FFFFFF", lw=1.2))
    ax.text(50, 45, "Heuristic Security & Reliability Code Smell Matcher", fontsize=8.5, fontweight='bold', ha='center', va='center')
    ax.text(90, 45, "✓ SQLi, Bare except\n✓ Div by zero, eval()", fontsize=6.5, color="#15803D", ha='left', va='center')
    ax.annotate("", xy=(50, 36), xytext=(50, 41), arrowprops=dict(arrowstyle="->", lw=1.3, color="#222222"))

    # Step 5: Bounded Risk Calculation
    ax.add_patch(patches.FancyBboxPatch((20, 28), 60, 8, boxstyle="round,pad=0.8", ec="#222222", fc="#FFFFFF", lw=1.2))
    ax.text(50, 32, "Evaluate Mathematical File Risk Model R(F)", fontsize=8.5, fontweight='bold', ha='center', va='center')
    ax.text(90, 32, "✓ min(100, LOC+CC+w·S)\n✓ Critical/High tiers", fontsize=6.5, color="#15803D", ha='left', va='center')
    ax.annotate("", xy=(50, 23), xytext=(50, 28), arrowprops=dict(arrowstyle="->", lw=1.3, color="#222222"))

    # Decision Diamond: Complexity / Smells Check
    ax.add_patch(patches.Polygon([[50, 23], [66, 17], [50, 11], [34, 17]], closed=True, ec="#222222", fc="#FFFFFF", lw=1.2))
    ax.text(50, 17, "Critical\nRisk Found?", fontsize=7.5, fontweight='bold', ha='center', va='center')

    # Branches
    # No branch -> Safe
    ax.annotate("", xy=(50, 4), xytext=(50, 11), arrowprops=dict(arrowstyle="->", lw=1.3, color="#222222"))
    ax.text(52, 7.5, "No", fontsize=7.5, color="#15803D", fontweight='bold')
    ax.add_patch(patches.FancyBboxPatch((35, 1), 30, 4.5, boxstyle="round,pad=0.5", ec="#16A34A", fc="#DCFCE7", lw=1.2))
    ax.text(50, 3.2, "Save Metrics to SQLite & Proceed", fontsize=7.5, fontweight='bold', color="#15803D", ha='center', va='center')

    # Yes branch -> Flag
    ax.annotate("", xy=(82, 17), xytext=(66, 17), arrowprops=dict(arrowstyle="->", lw=1.3, color="#DC2626"))
    ax.text(71, 19, "Yes", fontsize=7.5, color="#DC2626", fontweight='bold')
    ax.add_patch(patches.FancyBboxPatch((82, 14), 16, 6, boxstyle="round,pad=0.5", ec="#DC2626", fc="#FEE2E2", lw=1.2))
    ax.text(90, 17, "Flag Hotspot &\nPrioritize Triage", fontsize=7, fontweight='bold', color="#B91C1C", ha='center', va='center')
    ax.annotate("", xy=(65, 3.2), xytext=(90, 14), arrowprops=dict(arrowstyle="->", lw=1.2, color="#444444", connectionstyle="angle,angleA=0,angleB=90,rad=3"))

    plt.tight_layout()
    fig.savefig('report_images/fig_3_3_ast_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved fig_3_3_ast_analysis.png")

def draw_fig_3_4():
    # Figure 3.4: Subprocess Sandbox Execution Workflow (like PDF 1 page 27)
    fig, ax = plt.subplots(figsize=(6.2, 7.2), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    stages = [
        ("1", "Process Group Detachment", [
            "• Spawn isolated OS subprocess",
            "• CREATE_NEW_PROCESS_GROUP (Windows)",
            "• start_new_session=True (POSIX)"
        ]),
        ("2", "Sandbox Execution Launch", [
            "• Execute synthesized pytest suite",
            "• Stream redirection: capture stdout / stderr",
            "• Direct memory buffer to prevent terminal lock"
        ]),
        ("3", "Resource & Process-Tree Guard", [
            "• Active psutil monitor thread",
            "• Hard CPU & wall-clock timeout (10s)",
            "• Recursive tree traversal via psutil.Process"
        ]),
        ("4", "Timeout Guard & Clean Termination", [
            "• Elapse trigger: immediate terminate()",
            "• Recursive kill() on all orphaned children",
            "• Clean process teardown within < 200ms"
        ]),
        ("5", "Post-Execution Extraction & Telemetry", [
            "• Extract pass/fail assertions & error traces",
            "• Calculate statement & branch coverage",
            "• Store run records in SQLite ledger"
        ])
    ]

    y_pos = [82, 63, 44, 25, 6]
    for i, (num, title, bullets) in enumerate(stages):
        y = y_pos[i]
        # Box
        ax.add_patch(patches.FancyBboxPatch((15, y), 70, 14, boxstyle="round,pad=0.8", ec="#222222", fc="#FFFFFF", lw=1.2))
        # Number badge
        ax.add_patch(patches.Circle((20, y + 10), 3, ec="#222222", fc="#222222"))
        ax.text(20, y + 10, num, fontsize=9.5, fontweight='bold', color="#FFFFFF", ha='center', va='center')
        # Title
        ax.text(26, y + 10, title, fontsize=9, fontweight='bold', ha='left', va='center')
        # Bullets
        for b_idx, bullet in enumerate(bullets):
            ax.text(26, y + 6.5 - (b_idx * 2.5), bullet, fontsize=7.2, color="#333333", ha='left', va='center')

        # Arrow down
        if i < len(stages) - 1:
            ax.annotate("", xy=(50, y_pos[i+1] + 14), xytext=(50, y), arrowprops=dict(arrowstyle="->", lw=1.3, color="#222222"))

    plt.tight_layout()
    fig.savefig('report_images/fig_3_4_sandbox.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved fig_3_4_sandbox.png")

def draw_fig_3_5():
    # Figure 3.5: Pre-Flight Patch Repair Lifecycle (like PDF 1 page 28)
    fig, ax = plt.subplots(figsize=(8.5, 6.2), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Step 1: Defect Detected
    ax.add_patch(patches.FancyBboxPatch((5, 68), 42, 26, boxstyle="round,pad=1", ec="#222222", fc="#FFFFFF", lw=1.2))
    ax.add_patch(patches.Circle((10, 89), 2.5, ec="#222222", fc="#222222"))
    ax.text(10, 89, "1", fontsize=9, fontweight='bold', color="#FFFFFF", ha='center', va='center')
    ax.text(14, 89, "Defect Detected & Sliced", fontsize=9, fontweight='bold', ha='left', va='center')
    ax.text(10, 80, "• Traceback frame parser extracts line & file\n• Backward AST slicing isolates variable bounds\n• Status: DETERMINISTIC_DEFECT", fontsize=7.5, ha='left', va='center')

    # Step 2: Patch Synthesis
    ax.add_patch(patches.FancyBboxPatch((53, 68), 42, 26, boxstyle="round,pad=1", ec="#222222", fc="#FFFFFF", lw=1.2))
    ax.add_patch(patches.Circle((58, 89), 2.5, ec="#222222", fc="#222222"))
    ax.text(58, 89, "2", fontsize=9, fontweight='bold', color="#FFFFFF", ha='center', va='center')
    ax.text(62, 89, "Patch Synthesis", fontsize=9, fontweight='bold', ha='left', va='center')
    ax.text(58, 80, "• AutoFixAgent drafts minimal unified diff\n• Enforces boundary guard (zero/None check)\n• Status: CANDIDATE_PATCH", fontsize=7.5, ha='left', va='center')

    # Step 3: Pre-Flight Sandbox Verification
    ax.add_patch(patches.FancyBboxPatch((5, 36), 42, 26, boxstyle="round,pad=1", ec="#222222", fc="#FFFFFF", lw=1.2))
    ax.add_patch(patches.Circle((10, 57), 2.5, ec="#222222", fc="#222222"))
    ax.text(10, 57, "3", fontsize=9, fontweight='bold', color="#FFFFFF", ha='center', va='center')
    ax.text(14, 57, "Pre-Flight Sandbox Verify", fontsize=9, fontweight='bold', ha='left', va='center')
    ax.text(10, 48, "• Clone codebase to isolated temp directory\n• Apply unified diff to temporary clone\n• Re-run unit and regression test suites", fontsize=7.5, ha='left', va='center')

    # Step 4: Decision (Approve / Reject)
    ax.add_patch(patches.FancyBboxPatch((53, 36), 42, 26, boxstyle="round,pad=1", ec="#222222", fc="#FFFFFF", lw=1.2))
    ax.add_patch(patches.Circle((58, 57), 2.5, ec="#222222", fc="#222222"))
    ax.text(58, 57, "4", fontsize=9, fontweight='bold', color="#FFFFFF", ha='center', va='center')
    ax.text(62, 57, "Regression Decision", fontsize=9, fontweight='bold', ha='left', va='center')
    ax.text(58, 48, "• 100% Tests Pass -> PRE_FLIGHT_PASSED\n• Any Regression Failure -> REJECTED\n• Status: VERIFIED_SAFE", fontsize=7.5, ha='left', va='center')

    # Step 5: Adversarial Critic Review
    ax.add_patch(patches.FancyBboxPatch((5, 4), 42, 26, boxstyle="round,pad=1", ec="#222222", fc="#FFFFFF", lw=1.2))
    ax.add_patch(patches.Circle((10, 25), 2.5, ec="#222222", fc="#222222"))
    ax.text(10, 25, "5", fontsize=9, fontweight='bold', color="#FFFFFF", ha='center', va='center')
    ax.text(14, 25, "Adversarial Critic Debate", fontsize=9, fontweight='bold', ha='left', va='center')
    ax.text(10, 16, "• 2-Round debate: Advocate vs. Skeptic\n• Examine side-effects & memory overhead\n• Compute consensus score (threshold >=0.85)", fontsize=7.5, ha='left', va='center')

    # Step 6: Self-Healing Merge & Telemetry
    ax.add_patch(patches.FancyBboxPatch((53, 4), 42, 26, boxstyle="round,pad=1", ec="#222222", fc="#FFFFFF", lw=1.2))
    ax.add_patch(patches.Circle((58, 25), 2.5, ec="#222222", fc="#222222"))
    ax.text(58, 25, "6", fontsize=9, fontweight='bold', color="#FFFFFF", ha='center', va='center')
    ax.text(62, 25, "Merge & Telemetry Stream", fontsize=9, fontweight='bold', ha='left', va='center')
    ax.text(58, 16, "• Store verified patch in SQLite ledger\n• Stream patch review card via WebSocket\n• Developer 1-click apply promotion", fontsize=7.5, ha='left', va='center')

    # Connecting arrows
    ax.annotate("", xy=(53, 81), xytext=(47, 81), arrowprops=dict(arrowstyle="->", lw=1.3, color="#222222"))
    ax.annotate("", xy=(26, 68), xytext=(74, 68), arrowprops=dict(arrowstyle="->", lw=1.2, color="#444444", connectionstyle="arc3,rad=-0.25"))
    ax.annotate("", xy=(53, 49), xytext=(47, 49), arrowprops=dict(arrowstyle="->", lw=1.3, color="#222222"))
    ax.annotate("", xy=(26, 36), xytext=(74, 36), arrowprops=dict(arrowstyle="->", lw=1.2, color="#444444", connectionstyle="arc3,rad=-0.25"))
    ax.annotate("", xy=(53, 17), xytext=(47, 17), arrowprops=dict(arrowstyle="->", lw=1.3, color="#222222"))

    plt.tight_layout()
    fig.savefig('report_images/fig_3_5_patch_lifecycle.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved fig_3_5_patch_lifecycle.png")

if __name__ == '__main__':
    draw_fig_3_1()
    draw_fig_3_2()
    draw_fig_3_3()
    draw_fig_3_4()
    draw_fig_3_5()
