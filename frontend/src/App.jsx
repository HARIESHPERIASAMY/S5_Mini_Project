import React, { useState, useEffect, useRef } from 'react';
import Header from './components/Header';
import ReadinessStrip from './components/ReadinessStrip';
import KPICards from './components/KPICards';
import AgentNetworkGraph from './components/AgentNetworkGraph';
import LiveTerminal from './components/LiveTerminal';
import RiskHeatmap from './components/RiskHeatmap';
import BugExplorer from './components/BugExplorer';
import DefectExplainer from './components/DefectExplainer';
import AgentDebatePanel from './components/AgentDebatePanel';
import StatusBar from './components/StatusBar';
import NewProjectModal from './components/NewProjectModal';
import { Sparkles, Shield, RefreshCw, WifiOff } from 'lucide-react';

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
  const [wsConnected, setWsConnected] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(() => new Date().toISOString());

  // Inter-component filters & selection state
  const [selectedBugId, setSelectedBugId] = useState(null);
  const [fileFilter, setFileFilter] = useState(null);
  const [beginnerMode, setBeginnerMode] = useState(false);

  const wsRef = useRef(null);
  const explainerRef = useRef(null);

  // Poll or refresh run details when run is active
  useEffect(() => {
    if (!activeRunId) return;

    const fetchDetails = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/runs/${activeRunId}`);
        if (res.ok) {
          const data = await res.json();
          setRunData(data);
          setLastUpdated(new Date().toISOString());
          if (data.status === "completed" || data.status === "failed" || data.status === "interrupted") {
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
    const interval = setInterval(fetchDetails, 2500);
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
      setWsConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        const { event_type, agent_name, data, level, timestamp } = payload;
        setLastUpdated(timestamp || new Date().toISOString());

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
          if (data.status === "completed" || data.status === "failed" || data.status === "interrupted") {
            setIsRunning(false);
          }
        }
      } catch (err) {
        console.error("WS parse error:", err);
      }
    };

    ws.onerror = () => {
      setWsConnected(false);
    };

    ws.onclose = () => {
      console.log("WebSocket disconnected.");
      setWsConnected(false);
    };

    return () => {
      ws.close();
    };
  }, [activeRunId]);

  const bugs = runData?.bugs || [];
  const selectedBug = bugs.find((b) => b.id === selectedBugId) || bugs[0] || null;

  // Handlers
  const handleLaunchDemo = async () => {
    try {
      setIsRunning(true);
      setLogs([]);
      setAgentStates({});
      setSelectedBugId(null);
      setFileFilter(null);
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
    setSelectedBugId(null);
    setFileFilter(null);
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
    setSelectedBugId(null);
    setFileFilter(null);
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

  // Quick Action handlers for Readiness Strip
  const handleReviewFix = () => {
    if (bugs.length > 0) {
      setSelectedBugId(bugs[0].id);
      explainerRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const handleExplainBug = () => {
    if (bugs.length > 0) {
      setSelectedBugId(bugs[0].id);
      setBeginnerMode(true);
      explainerRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="min-h-screen bg-[#F4F6FA] mesh-dotted-bg text-[#0F172A] flex flex-col selection:bg-[#2563EB] selection:text-white">
      {/* Connection Lost Alert Banner */}
      {activeRunId && !wsConnected && (
        <div className="bg-[#FFF4E0] border-b border-[#FEDF89] px-4 py-2 text-xs font-mono text-[#9A5B00] flex items-center justify-center gap-2">
          <WifiOff className="w-3.5 h-3.5" />
          <span>Real-time WebSocket disconnected. Polling fallback active at http://localhost:8000.</span>
        </div>
      )}

      {/* A. Sticky Top Bar */}
      <Header
        activeRun={runData}
        llmProvider={llmProvider}
        setLlmProvider={setLlmProvider}
        onLaunchDemo={handleLaunchDemo}
        onOpenNewProject={() => setIsModalOpen(true)}
        onExportPatch={handleExportPatch}
        onDownloadReport={handleDownloadReport}
        isRunning={isRunning}
        wsConnected={wsConnected}
      />

      {/* Main Mission Control Container (1440px desktop max-width) */}
      <main className="flex-1 max-w-[1440px] w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        
        {/* Onboarding Hero Banner (When no active run is loaded) */}
        {!activeRunId && (
          <div className="card-surface bg-white p-8 md:p-12 text-center rounded-3xl border border-[#E3E8F0] shadow-sm relative overflow-hidden">
            <div className="w-14 h-14 rounded-2xl bg-[#EAF1FF] border border-[#B2CCFF] flex items-center justify-center mx-auto text-[#2563EB] shadow-xs mb-4">
              <Shield className="w-7 h-7" />
            </div>
            <h2 className="text-2xl sm:text-3xl font-heading font-extrabold text-[#0F172A] tracking-tight">
              Autonomous Software Testing & Self-Healing Bug Analysis Platform
            </h2>
            <p className="mt-2.5 text-sm text-[#5B6577] max-w-2xl mx-auto leading-relaxed">
              9 cooperating AI agents analyze your Python codebase, synthesize boundary and property tests,
              execute sandboxed regressions, trace causal root causes, and verify self-healing patches in real time.
            </p>

            <div className="mt-7 flex flex-wrap items-center justify-center gap-3">
              <button
                onClick={handleLaunchDemo}
                className="flex items-center gap-2 px-6 h-11 rounded-[10px] bg-[#2563EB] hover:bg-[#1D4ED8] text-white font-heading font-bold text-xs shadow-md shadow-blue-500/20 active:translate-y-px transition-all cursor-pointer"
              >
                <Sparkles className="w-4 h-4" />
                <span>Launch Demo Project (Instant 1-Click)</span>
              </button>
              <button
                onClick={() => setIsModalOpen(true)}
                className="px-5 h-11 rounded-[10px] bg-white hover:bg-[#F8FAFC] border border-[#E3E8F0] hover:border-[#CBD5E1] text-xs font-semibold text-[#0F172A] transition-all cursor-pointer"
              >
                Upload Code Repository (.zip)
              </button>
            </div>
          </div>
        )}

        {/* Telemetry Progress Bar if running */}
        {isRunning && runData && (
          <div className="card-surface p-3.5 bg-white border border-[#2563EB]/40 rounded-xl shadow-xs">
            <div className="flex items-center justify-between text-xs font-mono mb-1.5">
              <span className="flex items-center gap-2 text-[#2563EB] font-bold">
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                <span>Active Swarm Agent: @{currentAgent}</span>
              </span>
              <span className="text-[#0F172A] font-bold">{runData.progress_pct || 15}% Complete</span>
            </div>
            <div className="w-full bg-[#E2E8F0] rounded-full h-2 overflow-hidden">
              <div
                className="bg-[#2563EB] h-2 rounded-full transition-all duration-300"
                style={{ width: `${Math.min(100, Math.max(8, runData.progress_pct || 15))}%` }}
              />
            </div>
          </div>
        )}

        {/* B. Readiness Strip */}
        <ReadinessStrip
          runData={runData}
          onReviewFix={handleReviewFix}
          onExplainBug={handleExplainBug}
          hasBugs={bugs.length > 0}
        />

        {/* C. KPI Row (5 Cards) */}
        <KPICards runData={runData} />

        {/* D. Two Columns: Live Agent Swarm (~60%) & Telemetry Light Console (~40%) */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
          <div className="lg:col-span-7">
            <AgentNetworkGraph agentStates={agentStates} currentAgent={currentAgent} />
          </div>
          <div className="lg:col-span-5">
            <LiveTerminal logs={logs} />
          </div>
        </div>

        {/* E. Coverage Risk Heatmap */}
        <RiskHeatmap
          fileRisks={runData?.file_risks || []}
          selectedFile={fileFilter}
          onSelectFile={setFileFilter}
        />

        {/* F. Bug Classification and Self-Healing Ledger */}
        <BugExplorer
          bugs={bugs}
          selectedBug={selectedBug}
          onSelectBug={(b) => {
            setSelectedBugId(b.id);
            explainerRef.current?.scrollIntoView({ behavior: 'smooth' });
          }}
          fileFilter={fileFilter}
          onClearFileFilter={() => setFileFilter(null)}
        />

        {/* G. DEFECT EXPLAINER (Full Width, directly under ledger) */}
        <div ref={explainerRef}>
          <DefectExplainer
            bug={selectedBug}
            runData={runData}
            beginnerMode={beginnerMode}
            onToggleBeginnerMode={() => setBeginnerMode(!beginnerMode)}
            onExportPatch={handleExportPatch}
          />
        </div>

        {/* H. Critic Agent and Multi-Agent Debate */}
        <AgentDebatePanel
          debates={runData?.debates || []}
          consensusScore={runData?.consensus_score || 96}
        />

      </main>

      {/* I. Slim Sticky Status Bar */}
      <StatusBar
        isConnected={wsConnected}
        runId={activeRunId}
        lastUpdated={lastUpdated}
        status={runData?.status || (isRunning ? "running" : "idle")}
      />

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
