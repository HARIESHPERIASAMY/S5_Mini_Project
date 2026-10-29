import React, { useState, useEffect, useRef } from 'react';
import Header from './components/Header';
import KPICards from './components/KPICards';
import AgentNetworkGraph from './components/AgentNetworkGraph';
import LiveTerminal from './components/LiveTerminal';
import RiskHeatmap from './components/RiskHeatmap';
import BugExplorer from './components/BugExplorer';
import AgentDebatePanel from './components/AgentDebatePanel';
import NewProjectModal from './components/NewProjectModal';
import { Sparkles, Shield, RefreshCw } from 'lucide-react';

const API_BASE = "http://localhost:8000";

export default function App() {
  const [activeRunId, setActiveRunId] = useState(null);
  const [runData, setRunData] = useState(null);
  const [logs, setLogs] = useState([]);
  const [agentStates, setAgentStates] = useState({});
  const [currentAgent, setCurrentAgent] = useState("orchestrator");
  const [llmProvider, setLlmProvider] = useState("offline");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const wsRef = useRef(null);

  // Poll or refresh run details when run is active
  useEffect(() => {
    if (!activeRunId) return;

    const fetchDetails = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/runs/${activeRunId}`);
        if (res.ok) {
          const data = await res.json();
          setRunData(data);
          if (data.status === "completed" || data.status === "failed") {
            setIsRunning(false);
          } else {
            setIsRunning(true);
          }
        }
      } catch (err) {
        console.error("Error fetching run details:", err);
      }
    };

    fetchDetails();
    const interval = setInterval(fetchDetails, 3000);
    return () => clearInterval(interval);
  }, [activeRunId]);

  // WebSocket live telemetry stream
  useEffect(() => {
    if (!activeRunId) return;

    const wsUrl = `ws://localhost:8000/ws/runs/${activeRunId}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log("Connected to SentinelMesh WebSocket:", activeRunId);
    };

    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        const { event_type, agent_name, data, level, timestamp } = payload;

        if (event_type === "log") {
          setLogs((prev) => [...prev, { ...data, agent_name, level, timestamp }]);
        } else if (event_type === "agent_state") {
          setCurrentAgent(agent_name);
          setAgentStates((prev) => ({
            ...prev,
            [agent_name]: data.state || "RUNNING",
          }));
          setLogs((prev) => [
            ...prev,
            { message: data.details, agent_name, level: "INFO", timestamp },
          ]);
        } else if (event_type === "telemetry") {
          if (data.current_agent) setCurrentAgent(data.current_agent);
          setRunData((prev) => ({
            ...prev,
            ...data,
            [data.key]: data.value,
          }));
        } else if (event_type === "debate") {
          setRunData((prev) => ({
            ...prev,
            debates: [...(prev?.debates || []), data],
          }));
        } else if (event_type === "run_status") {
          if (data.status === "completed" || data.status === "failed") {
            setIsRunning(false);
          }
        }
      } catch (err) {
        console.error("WS parse error:", err);
      }
    };

    ws.onclose = () => {
      console.log("WebSocket disconnected.");
    };

    return () => {
      ws.close();
    };
  }, [activeRunId]);

  // Handlers
  const handleLaunchDemo = async () => {
    try {
      setIsRunning(true);
      setLogs([]);
      setAgentStates({});
      const res = await fetch(`${API_BASE}/api/demo/launch?llm_provider=${llmProvider}`, {
        method: "POST",
      });
      let data;
      try {
        data = await res.json();
      } catch {
        throw new Error(`Server returned status ${res.status} (non-JSON response)`);
      }
      if (!res.ok) {
        throw new Error(data.detail || data.error || `Failed to launch demo (HTTP ${res.status})`);
      }
      if (data.run_id) {
        setActiveRunId(data.run_id);
      }
    } catch (err) {
      alert("Failed to launch demo: " + err.message);
      setIsRunning(false);
    }
  };

  const handleSubmitSnippet = async (name, snippet) => {
    setIsRunning(true);
    setLogs([]);
    setAgentStates({});
    try {
      const projRes = await fetch(`${API_BASE}/api/projects`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, code_snippet: snippet, source_type: "snippet" }),
      });
      let proj;
      try {
        proj = await projRes.json();
      } catch {
        throw new Error(`Server returned status ${projRes.status} (non-JSON response)`);
      }
      if (!projRes.ok) {
        throw new Error(proj.detail || proj.error || `Failed to create project (HTTP ${projRes.status})`);
      }

      const runRes = await fetch(`${API_BASE}/api/runs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ project_id: proj.id, llm_provider: llmProvider }),
      });
      let run;
      try {
        run = await runRes.json();
      } catch {
        throw new Error(`Server returned status ${runRes.status} (non-JSON response)`);
      }
      if (!runRes.ok) {
        throw new Error(run.detail || run.error || `Failed to start analysis run (HTTP ${runRes.status})`);
      }
      setActiveRunId(run.run_id);
    } catch (err) {
      setIsRunning(false);
      throw err;
    }
  };

  const handleUploadZip = async (name, file) => {
    setIsRunning(true);
    setLogs([]);
    setAgentStates({});
    try {
      const formData = new FormData();
      formData.append("file", file);

      const projRes = await fetch(`${API_BASE}/api/projects/upload?name=${encodeURIComponent(name)}`, {
        method: "POST",
        body: formData,
      });
      let proj;
      try {
        proj = await projRes.json();
      } catch {
        throw new Error(`Server returned status ${projRes.status} (non-JSON response)`);
      }
      if (!projRes.ok) {
        throw new Error(proj.detail || proj.error || `Failed to upload project (HTTP ${projRes.status})`);
      }

      const runRes = await fetch(`${API_BASE}/api/runs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ project_id: proj.id, llm_provider: llmProvider }),
      });
      let run;
      try {
        run = await runRes.json();
      } catch {
        throw new Error(`Server returned status ${runRes.status} (non-JSON response)`);
      }
      if (!runRes.ok) {
        throw new Error(run.detail || run.error || `Failed to start analysis run (HTTP ${runRes.status})`);
      }
      setActiveRunId(run.run_id);
    } catch (err) {
      setIsRunning(false);
      throw err;
    }
  };

  const handleExportPatch = () => {
    if (!activeRunId) return;
    window.open(`${API_BASE}/api/runs/${activeRunId}/patch`, "_blank");
  };

  const handleDownloadReport = () => {
    if (!activeRunId) return;
    window.open(`${API_BASE}/api/runs/${activeRunId}/report?format=html`, "_blank");
  };

  return (
    <div className="min-h-screen bg-mesh-bg text-slate-100 flex flex-col selection:bg-cyan-500 selection:text-black">
      {/* Top Header */}
      <Header
        activeRun={runData}
        llmProvider={llmProvider}
        setLlmProvider={setLlmProvider}
        onLaunchDemo={handleLaunchDemo}
        onOpenNewProject={() => setIsModalOpen(true)}
        onExportPatch={handleExportPatch}
        onDownloadReport={handleDownloadReport}
        isRunning={isRunning}
      />

      {/* Main Mission Control Dashboard */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 md:p-6 space-y-6">
        {/* If no run yet: Hero Onboarding Banner */}
        {!activeRunId && (
          <div className="glass-panel-glow rounded-3xl p-8 md:p-12 text-center relative overflow-hidden border border-cyan-500/30">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-cyan-500 to-indigo-600 flex items-center justify-center mx-auto shadow-xl shadow-cyan-500/25 mb-4">
              <Shield className="w-8 h-8 text-white" />
            </div>
            <h2 className="text-2xl md:text-3xl font-bold tracking-tight text-white">
              Intelligent Multi-Agent Testing & Bug Analysis Platform
            </h2>
            <p className="mt-3 text-sm text-slate-300 max-w-2xl mx-auto leading-relaxed">
              9 cooperating AI agents analyze your Python codebase, synthesize unit and boundary tests,
              execute sandboxed regressions, trace causal root causes, and verify auto-fixes in real time.
            </p>

            <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
              <button
                onClick={handleLaunchDemo}
                className="flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-mono font-bold text-sm shadow-xl shadow-cyan-500/30 transform hover:-translate-y-0.5 transition-all"
              >
                <Sparkles className="w-4 h-4" />
                <span>Launch Demo Project (Instant 1-Click)</span>
              </button>
              <button
                onClick={() => setIsModalOpen(true)}
                className="px-6 py-3 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 font-mono text-sm text-slate-200 transition-colors"
              >
                Upload Code Repository
              </button>
            </div>
          </div>
        )}

        {/* Telemetry Progress Bar if running */}
        {isRunning && runData && (
          <div className="glass-panel rounded-xl p-3 border border-cyan-500/40">
            <div className="flex items-center justify-between text-xs font-mono mb-1.5">
              <span className="flex items-center gap-2 text-cyan-300">
                <RefreshCw className="w-3.5 h-3.5 animate-spin text-cyan-400" />
                <span>Active Swarm Agent: @{currentAgent}</span>
              </span>
              <span className="text-white font-bold">{runData.progress_pct || 10}% Complete</span>
            </div>
            <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
              <div
                className="bg-gradient-to-r from-cyan-500 via-indigo-500 to-emerald-400 h-2 rounded-full transition-all duration-300"
                style={{ width: `${Math.min(100, Math.max(5, runData.progress_pct || 10))}%` }}
              />
            </div>
          </div>
        )}

        {/* 1. KPI Telemetry Widgets */}
        <KPICards runData={runData} />

        {/* 2. Agent Network Topology Graph + Live Terminal */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          <AgentNetworkGraph agentStates={agentStates} currentAgent={currentAgent} />
          <LiveTerminal logs={logs} />
        </div>

        {/* 3. Codebase Risk Heatmap */}
        <RiskHeatmap fileRisks={runData?.file_risks || []} />

        {/* 4. Bug Explorer (Filterable Table, Unified Diff View, Beginner Mode) */}
        <BugExplorer bugs={runData?.bugs || []} />

        {/* 5. Critic Audit & Multi-Agent Debate Ledger */}
        <AgentDebatePanel
          debates={runData?.debates || []}
          consensusScore={runData?.consensus_score || 96}
        />
      </main>

      {/* Upload & New Snippet Modal */}
      <NewProjectModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmitSnippet={handleSubmitSnippet}
        onUploadZip={handleUploadZip}
        onLaunchDemo={handleLaunchDemo}
      />
    </div>
  );
}
