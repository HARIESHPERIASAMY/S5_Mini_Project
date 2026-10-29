# SentinelMesh Architecture Diagrams

This directory contains standalone, editable Mermaid diagram source files representing the actual, verified architecture and execution flow of SentinelMesh.

## Diagram Index

1. **`01_system_architecture.mmd`**: High-level multi-tier architecture diagram showing the Presentation (React + Vite), API Gateway (FastAPI), Multi-Agent Mesh (9 specialized Python agents), Execution Boundary (SandboxRunner + psutil), Database Layer (SQLite WAL mode), and LLM Provider abstraction (Offline, Gemini, OpenAI).
2. **`02_sequence_diagram.mmd`**: End-to-end execution sequence diagram detailing the HTTP/WebSocket interaction between the user interface, backend orchestrator, sandbox execution, database writes, and real-time frontend streaming.
3. **`03_database_er.mmd`**: Entity-Relationship diagram documenting the relational schema implemented in SQLAlchemy/SQLite (`projects`, `runs`, `bugs`, `file_risks`, `test_results`, `mutation_records`, `agent_logs`, `debate_messages`).
4. **`04_data_flow_diagram.mmd`**: Level 0 and Level 1 Data Flow Diagrams (DFD) showing the transformation from raw source code and tests to defect classifications, causal chains, verified patches, and reports.

## Rendering Instructions
These diagrams use standard Mermaid syntax and can be rendered using:
- Visual Studio Code Mermaid Preview extension
- GitHub / GitLab native markdown viewer
- Mermaid Live Editor (`https://mermaid.live`)
- Mermaid CLI (`mmdc -i <file>.mmd -o <file>.png`)
