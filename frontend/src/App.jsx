import React, { useState, useEffect, useRef } from 'react';
import Sidebar from './components/layout/Sidebar';
import TopBar from './components/layout/TopBar';
import MeshAssistant from './components/assistant/MeshAssistant';
import FileTree from './components/findings/FileTree';
import FindingsTable from './components/findings/FindingsTable';
import DefectDetailDrawer from './components/findings/DefectDetailDrawer';
import OverviewFindingsPreview from './components/overview/OverviewFindingsPreview';
import LiveRunView from './components/liverun/LiveRunView';
import StartScreen from './components/start/StartScreen';
import RunHistoryView from './components/history/RunHistoryView';
import CompareRunsModal from './components/compare/CompareRunsModal';
import ReportsView from './components/reports/ReportsView';
import IntegrationsView from './components/integrations/IntegrationsView';
import SettingsView from './components/settings/SettingsView';
import AgentNetworkGraph from './components/AgentNetworkGraph';
import AgentDebatePanel from './components/AgentDebatePanel';
import NewProjectModal from './components/NewProjectModal';
import { derivePipelineStages, deriveScoreBreakdown, setBugWorkflowState } from './api/adapters';
import { generateSarifReport, generateJUnitXml, createZipBundle } from './utils/exporters';
import { RefreshCw, Bot, AlertCircle } from 'lucide-react';

const API_BASE = "http://localhost:8000";

export default function App() {
  const getInitialView = () => {
    if (typeof window !== "undefined") {
      const p = new URLSearchParams(window.location.search);
      const v = p.get("view");
      if (v) return v;
    }
    return "overview";
  };

  const [activeView, setActiveViewState] = useState(getInitialView);
  const setActiveView = (view) => {
    setActiveViewState(view);
    if (typeof window !== "undefined") {
      const url = new URL(window.location);
      url.searchParams.set("view", view);
      window.history.replaceState({}, "", url);
    }
  };
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [assistantOpen, setAssistantOpen] = useState(true);

  // Core Run Data & Telemetry
  const [activeRunId, setActiveRunId] = useState(null);
  const [runData, setRunData] = useState(null);
  const [logs, setLogs] = useState([]);
  const [agentStates, setAgentStates] = useState({});
  const [currentAgent, setCurrentAgent] = useState("orchestrator");
  const [llmProvider, setLlmProvider] = useState("offline");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const [wsConnected, setWsConnected] = useState(false);

  // Finding selection & filter states
  const [selectedBugId, setSelectedBugId] = useState(null);
  const [fileFilter, setFileFilter] = useState(null);
  const [beginnerMode, setBeginnerMode] = useState(false);
  const [scoreDrawerOpen, setScoreDrawerOpen] = useState(false);
  const [pendingAssistantPrompt, setPendingAssistantPrompt] = useState(null);
  const [, setWorkflowVersion] = useState(0);

  // Cross-run comparison, runs history list, and theme
  const [allRuns, setAllRuns] = useState([]);
  const [compareModalOpen, setCompareModalOpen] = useState(false);
  const [compareBaseId, setCompareBaseId] = useState(null);
  const [compareTargetId, setCompareTargetId] = useState(null);
  const [backendDisconnected, setBackendDisconnected] = useState(false);
  const [theme, setTheme] = useState("light");

  const handleUpdateWorkflowState = (bugId, newStatus) => {
    setBugWorkflowState(activeRunId || "2841", bugId, newStatus);
    setWorkflowVersion((v) => v + 1);
  };

  const handleOpenAssistant = (prompt) => {
    setPendingAssistantPrompt(prompt);
    setAssistantOpen(true);
  };

  const wsRef = useRef(null);

  // Fetch all runs list on mount
  const fetchRunsList = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/runs?limit=25`);
      if (res.ok) {
        const data = await res.json();
        const items = data.items || [];
        setAllRuns(items);
        setBackendDisconnected(false);
        if (!activeRunId && items.length > 0) {
          setActiveRunId(items[0].id);
        }
      } else {
        setBackendDisconnected(true);
      }
    } catch (err) {
      console.warn("Backend not reachable:", err);
      setBackendDisconnected(true);
    }
  };

  useEffect(() => {
    fetchRunsList();
  }, []);

  // Poll run details
  useEffect(() => {
    if (!activeRunId) return;

    const fetchDetails = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/runs/${activeRunId}`);
        if (res.ok) {
          const data = await res.json();
          setRunData(data);
          setBackendDisconnected(false);
          if (data.status === "completed" || data.status === "failed" || data.status === "interrupted") {
            setIsRunning(false);
          } else {
            setIsRunning(true);
          }
        } else {
          setBackendDisconnected(true);
        }
      } catch (err) {
        console.error("Error fetching run details:", err);
        setBackendDisconnected(true);
      }
    };

    fetchDetails();
    const interval = setInterval(fetchDetails, 2500);
    return () => clearInterval(interval);
  }, [activeRunId]);

  // WebSocket Live Stream
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

    ws.onerror = () => setWsConnected(false);
    ws.onclose = () => setWsConnected(false);

    return () => ws.close();
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
      setActiveView("overview");

      const res = await fetch(`${API_BASE}/api/demo/launch?llm_provider=${llmProvider}`, {
        method: "POST",
      });
      let data;
      try {
        data = await res.json();
      } catch {
        throw new Error(`Server returned status ${res.status}`);
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
    setActiveView("overview");

    try {
      const projRes = await fetch(`${API_BASE}/api/projects`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, code_snippet: snippet, source_type: "snippet" }),
      });
      const proj = await projRes.json();
      if (!projRes.ok) throw new Error(proj.detail || "Project creation failed");

      const runRes = await fetch(`${API_BASE}/api/runs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ project_id: proj.id, llm_provider: llmProvider }),
      });
      const run = await runRes.json();
      if (!runRes.ok) throw new Error(run.detail || "Run launch failed");
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
    setActiveView("overview");

    try {
      const formData = new FormData();
      formData.append("file", file);

      const projRes = await fetch(`${API_BASE}/api/projects/upload?name=${encodeURIComponent(name)}`, {
        method: "POST",
        body: formData,
      });
      const proj = await projRes.json();
      if (!projRes.ok) throw new Error(proj.detail || "Project upload failed");

      const runRes = await fetch(`${API_BASE}/api/runs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ project_id: proj.id, llm_provider: llmProvider }),
      });
      const run = await runRes.json();
      if (!runRes.ok) throw new Error(run.detail || "Run launch failed");
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

  const triggerDownload = (blob, filename) => {
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleExportSarif = () => {
    if (!runData) return;
    const sarif = generateSarifReport(runData);
    const blob = new Blob([JSON.stringify(sarif, null, 2)], { type: "application/json" });
    triggerDownload(blob, `sentinelmesh_run_${(activeRunId || '2841').slice(0, 8)}.sarif`);
  };

  const handleExportJUnit = () => {
    if (!runData) return;
    const xml = generateJUnitXml(runData);
    const blob = new Blob([xml], { type: "application/xml" });
    triggerDownload(blob, `sentinelmesh_run_${(activeRunId || '2841').slice(0, 8)}_junit.xml`);
  };

  const handleExportPatchZip = () => {
    if (!runData) return;
    const bugsWithDiff = (runData.bugs || []).filter((b) => b.proposed_fix_diff);
    const files = bugsWithDiff.map((b, idx) => ({
      name: `fix_${idx + 1}_${(b.file_path || 'file').replace(/[^a-zA-Z0-9]/g, '_')}_line_${b.line_number || 1}.patch`,
      content: b.proposed_fix_diff
    }));
    if (files.length === 0) {
      files.push({
        name: "README.txt",
        content: "No unified diff patches proposed for this run."
      });
    }
    const zipBlob = createZipBundle(files);
    triggerDownload(zipBlob, `sentinelmesh_run_${(activeRunId || '2841').slice(0, 8)}_patches.zip`);
  };

  // Derive pipeline stages and metrics
  const pipelineStages = derivePipelineStages(runData);
  const scoreBreakdown = deriveScoreBreakdown(runData);

  const unverifiedBugs = bugs.filter((b) => !b.fix_verified);
  const verifiedBugsCount = bugs.filter((b) => b.fix_verified).length;
  let bannerSentence = "";
  if (bugs.length === 0) {
    bannerSentence = "All automated unit, property, and regression checks passed with zero defects.";
  } else if (unverifiedBugs.length === 0) {
    bannerSentence = `All ${bugs.length} identified defects have verified patches passing in the sandbox.`;
  } else {
    const topOpen = unverifiedBugs[0];
    bannerSentence = `${verifiedBugsCount} fix${verifiedBugsCount === 1 ? '' : 'es'} verified in sandbox. ${unverifiedBugs.length} defect${unverifiedBugs.length === 1 ? '' : 's'} (${topOpen.title}) remain${unverifiedBugs.length === 1 ? 's' : ''} under triage.`;
  }

  const criticalBugs = bugs.filter((b) => b.severity?.toUpperCase() === "CRITICAL").length;
  const highBugs = bugs.filter((b) => b.severity?.toUpperCase() === "HIGH").length;
  const medBugs = bugs.filter((b) => b.severity?.toUpperCase() === "MEDIUM").length;
  const lowBugs = bugs.filter((b) => b.severity?.toUpperCase() === "LOW").length;
  const sevParts = [];
  if (criticalBugs > 0) sevParts.push(`${criticalBugs} critical`);
  if (highBugs > 0) sevParts.push(`${highBugs} high`);
  if (medBugs > 0) sevParts.push(`${medBugs} medium`);
  if (lowBugs > 0) sevParts.push(`${lowBugs} low`);
  const bugsSeveritySubtext = sevParts.length > 0 ? sevParts.join(" · ") : (bugs.length === 0 ? "Zero defects" : "No high severity");

  const covPct = runData?.code_coverage ?? 0;
  const isCovBelowTarget = covPct < 80.0;
  const hasMultipleRuns = (allRuns || []).length >= 2;
  const trendDelta = hasMultipleRuns ? Math.round(((allRuns[0]?.suite_health_score || 0) - (allRuns[1]?.suite_health_score || 0)) * 10) / 10 : 0;

  return (
    <div className={`flex h-screen w-screen overflow-hidden font-sans antialiased ${theme === 'dark' ? 'bg-[#0B132B] text-slate-100' : 'bg-[#F8FAFC] text-[#0F172A]'}`}>
      {/* 1. Collapsible Dark Navy Sidebar */}
      <Sidebar
        activeView={activeView}
        onSelectView={setActiveView}
        collapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
        findingsCount={bugs.length}
        runId={activeRunId}
        isConnected={wsConnected || Boolean(activeRunId)}
      />

      {/* Main View Area with TopBar & Content Viewport */}
      <div className="flex-1 flex flex-col min-w-0 h-full overflow-hidden">
        {/* 2. Top Bar */}
        <TopBar
          activeViewTitle={activeView === "liverun" ? "Live run" : activeView}
          projectName="demo-shop"
          mainFile="main.py"
          llmProvider={llmProvider}
          onSelectProvider={setLlmProvider}
          onOpenAnalyzeCode={() => setIsModalOpen(true)}
          onExportPatch={handleExportPatch}
          onDownloadReport={handleDownloadReport}
          onExportSarif={handleExportSarif}
          onExportJUnit={handleExportJUnit}
          onExportPatchZip={handleExportPatchZip}
          onOpenCompare={() => setCompareModalOpen(true)}
          onToggleAssistant={() => setAssistantOpen(!assistantOpen)}
          isAssistantOpen={assistantOpen}
          runId={activeRunId}
          runsList={allRuns}
        />

        {/* Backend Disconnection Banner */}
        {backendDisconnected && (
          <div className="bg-[#FEF2F2] border-b border-[#FCA5A5] text-[#991B1B] px-4 py-2.5 text-xs flex items-center justify-between z-10">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-[#DC2626] flex-shrink-0" />
              <span className="font-semibold">Backend disconnected. Retrying connection to port 8000...</span>
            </div>
            <button
              onClick={() => {
                setBackendDisconnected(false);
                fetchRunsList();
              }}
              className="px-2.5 py-1 bg-white border border-[#FCA5A5] rounded text-[11px] font-bold text-[#991B1B] hover:bg-[#FEE2E2] cursor-pointer"
            >
              Retry
            </button>
          </div>
        )}

        {/* View Content + Mesh Assistant Flex Container */}
        <div className="flex-1 flex overflow-hidden">
          {/* Main Scrollable View Container */}
          <main className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6">
            
            {/* If no run yet and on overview: Start Screen */}
            {!activeRunId && (activeView === "overview" || activeView === "start") && (
              <StartScreen
                onLaunchDemo={handleLaunchDemo}
                onSubmitSnippet={handleSubmitSnippet}
                onUploadZip={handleUploadZip}
                llmProvider={llmProvider}
                onSelectProvider={setLlmProvider}
                isRunning={isRunning}
              />
            )}

            {/* Running Telemetry Progress Pill */}
            {isRunning && runData && (
              <div className="sm-card p-3 bg-white border border-[#2457F5]/30 rounded-xl flex items-center justify-between text-xs font-mono">
                <div className="flex items-center gap-2 text-[#2457F5] font-bold">
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  <span>Swarm Active: @{currentAgent}</span>
                </div>
                <span className="text-[#0F172A] font-bold">{runData.progress_pct || 15}% Complete</span>
              </div>
            )}

            {/* VIEW: OVERVIEW */}
            {activeView === "overview" && activeRunId && (
              <div className="space-y-6">
                {/* 1. Verdict Banner */}
                <div className="sm-card p-5 bg-white border border-[#E2E8F0] rounded-xl shadow-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-5">
                  <div className="flex items-center gap-4">
                    {/* Score Ring */}
                    <div className="relative w-16 h-16 rounded-full border-4 border-[#2457F5] flex items-center justify-center flex-shrink-0">
                      <span className="text-base font-heading font-extrabold text-[#0F172A]">
                        {runData?.suite_health_score ?? "73.5"}
                      </span>
                    </div>

                    <div>
                      <span className="px-2 py-0.5 rounded-full bg-[#FFF4E0] text-[#9A5B00] border border-[#FEDF89] text-[10px] font-mono font-bold">
                        Needs attention
                      </span>
                      <h2 className="text-base sm:text-lg font-heading font-extrabold text-[#0F172A] mt-1">
                        {bugs.length > 0 ? `${bugs.length} defects flagged, ${verifiedBugsCount} fixes already verified` : "Zero defects flagged, clean suite"}
                      </h2>
                      <p className="text-xs text-[#64748B] mt-0.5">
                        {bannerSentence}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-4">
                    {/* Health Trend Sparkline (Condition: Only shown if 2 or more real runs exist) */}
                    {hasMultipleRuns && (
                      <div className="hidden xl:flex items-center gap-2 pl-4 border-l border-[#E2E8F0]">
                        <div className="text-right">
                          <div className="flex items-center justify-end gap-1">
                            <span className="text-[10px] font-mono text-[#64748B] uppercase">Health Trend</span>
                          </div>
                          <span className={`text-xs font-bold font-mono block mt-0.5 ${trendDelta >= 0 ? "text-[#16A34A]" : "text-[#DC2626]"}`}>
                            {trendDelta >= 0 ? `+${trendDelta}` : trendDelta} pts
                          </span>
                        </div>
                        <svg className="w-20 h-8" viewBox="0 0 80 32">
                          <polyline
                            fill="none"
                            stroke="#2457F5"
                            strokeWidth="2"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            points="4,24 28,18 52,14 76,6"
                          />
                          <circle cx="4" cy="24" r="2.5" fill="#2457F5" />
                          <circle cx="28" cy="18" r="2.5" fill="#2457F5" />
                          <circle cx="52" cy="14" r="2.5" fill="#2457F5" />
                          <circle cx="76" cy="6" r="3" fill="#16A34A" />
                        </svg>
                      </div>
                    )}

                    <div className="flex items-center gap-2.5">
                      <button
                        onClick={() => {
                          setActiveView("findings");
                          if (bugs[0]) setSelectedBugId(bugs[0].id);
                        }}
                        className="px-4 h-9 rounded-lg bg-[#2457F5] hover:bg-[#1A44D4] text-white text-xs font-semibold shadow-xs transition-all cursor-pointer"
                      >
                        Review top fix
                      </button>
                      <button
                        onClick={() => setScoreDrawerOpen(!scoreDrawerOpen)}
                        className="px-3 h-9 rounded-lg bg-white hover:bg-[#F8FAFC] border border-[#E2E8F0] text-xs font-medium text-[#0F172A] transition-colors cursor-pointer"
                      >
                        Why {runData?.suite_health_score ?? "0"}? See breakdown
                      </button>
                    </div>
                  </div>
                </div>

                {/* Score Breakdown Drawer */}
                {scoreDrawerOpen && (
                  <div className="sm-card p-4 bg-[#FAFBFD] border border-[#E2E8F0] rounded-xl text-xs space-y-3">
                    <div className="flex items-center justify-between font-heading font-bold text-[#0F172A]">
                      <div className="flex items-center gap-2">
                        <span>Backend Health Score Breakdown</span>
                        <span className="text-[10px] font-mono font-normal text-[#64748B] bg-white px-2 py-0.5 rounded border border-[#E2E8F0]">
                          Source: {scoreBreakdown.sourceFile}
                        </span>
                      </div>
                      <button onClick={() => setScoreDrawerOpen(false)} className="text-[#64748B] hover:text-[#0F172A] cursor-pointer">✕</button>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3 font-mono text-[11px]">
                      {scoreBreakdown.metrics.map((m, i) => (
                        <div key={i} className="p-3 bg-white rounded-lg border border-[#E2E8F0] space-y-1">
                          <div className="flex items-center justify-between text-[#64748B]">
                            <span>{m.name}</span>
                            <span className="font-bold text-[#2457F5]">{m.weight}</span>
                          </div>
                          <strong className="text-base font-bold text-[#0F172A] block">{m.value}</strong>
                          <span className="text-[10px] text-[#64748B] block">{m.detail}</span>
                        </div>
                      ))}
                    </div>

                    <div className="p-2.5 rounded-lg bg-white border border-[#E2E8F0] font-mono text-[11px] text-[#475569] space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-[#0F172A]">Exact Formula:</span>
                        <span>{scoreBreakdown.formula}</span>
                      </div>
                      <div className="flex items-center justify-between text-[#16A34A] pt-1 border-t border-[#E2E8F0]">
                        <span className="font-bold">Calculated from Real Values:</span>
                        <span>{scoreBreakdown.verification}</span>
                      </div>
                    </div>
                  </div>
                )}

                {/* 2. ONE Row of 4 KPI Cards */}
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                  {/* Card 1 */}
                  <div className="sm-card p-4 bg-white border border-[#E2E8F0] rounded-xl">
                    <span className="text-[11px] font-mono font-bold uppercase text-[#64748B]">Bugs Found</span>
                    <div className="text-2xl font-heading font-extrabold text-[#0F172A] mt-1">
                      {bugs.length}
                    </div>
                    <span className="text-xs text-[#DC2626] font-medium">{bugsSeveritySubtext}</span>
                  </div>

                  {/* Card 2 */}
                  <div className="sm-card p-4 bg-white border border-[#E2E8F0] rounded-xl">
                    <span className="text-[11px] font-mono font-bold uppercase text-[#64748B]">Fixes Verified</span>
                    <div className="text-2xl font-heading font-extrabold text-[#0F172A] mt-1">
                      {verifiedBugsCount} / {bugs.length}
                    </div>
                    <span className="text-xs text-[#16A34A] font-medium">Re-run in sandbox</span>
                  </div>

                  {/* Card 3 */}
                  <div className="sm-card p-4 bg-white border border-[#E2E8F0] rounded-xl">
                    <span className="text-[11px] font-mono font-bold uppercase text-[#64748B]">Coverage</span>
                    <div className={`text-2xl font-heading font-extrabold mt-1 ${isCovBelowTarget ? 'text-[#D97706]' : 'text-[#0F172A]'}`}>
                      {covPct}%
                    </div>
                    <span className={`text-xs font-medium ${isCovBelowTarget ? 'text-[#D97706]' : 'text-[#64748B]'}`}>
                      {isCovBelowTarget ? 'Below target 80%' : 'Target 80% met'}
                    </span>
                  </div>

                  {/* Card 4 */}
                  <div className="sm-card p-4 bg-white border border-[#E2E8F0] rounded-xl">
                    <span className="text-[11px] font-mono font-bold uppercase text-[#64748B]">Mutants Killed</span>
                    <div className="text-2xl font-heading font-extrabold text-[#0F172A] mt-1">
                      {runData?.mutation_score ?? 0}%
                    </div>
                    <span className="text-xs text-[#64748B] font-medium">AST operator set</span>
                  </div>
                </div>

                {/* 3. Self-Healing Pipeline Strip */}
                <div className="sm-card p-4 bg-white border border-[#E2E8F0] rounded-xl">
                  <span className="text-[11px] font-mono font-bold uppercase text-[#64748B] block mb-3">
                    Self-Healing Pipeline · Run #{activeRunId ? activeRunId.slice(0, 6) : "2841"}
                  </span>
                  <div className="grid grid-cols-5 gap-2 text-center text-xs">
                    {pipelineStages.map((stage, sIdx) => (
                      <div key={sIdx} className="p-2.5 rounded-lg bg-[#F8FAFC] border border-[#E2E8F0]">
                        <span className="font-heading font-bold text-[#0F172A] block">{stage.name}</span>
                        <span className="text-[11px] text-[#64748B] font-mono mt-0.5 block">{stage.count}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* 4. Findings Table Preview (Top 5) & Inline Defect Detail (Screenshot 1) */}
                <OverviewFindingsPreview
                  bugs={bugs}
                  selectedBug={selectedBug}
                  onSelectBug={(b) => setSelectedBugId(b.id)}
                  onGoToFindings={() => {
                    setActiveView("findings");
                  }}
                  runId={activeRunId}
                  onExportPatch={handleExportPatch}
                />
              </div>
            )}

            {/* VIEW: LIVE RUN (Horizontal Agent Pipeline + Plain-Language Timeline + Raw Logs Toggle) */}
            {activeView === "liverun" && (
              <LiveRunView
                runData={runData}
                logs={logs}
                agentStates={agentStates}
                currentAgent={currentAgent}
                isRunning={isRunning}
                onSelectFinding={(bugId) => {
                  setSelectedBugId(bugId);
                  setActiveView("findings");
                }}
              />
            )}

            {/* VIEW: FINDINGS (Master-Detail 3-Column Layout - Screenshot 3) */}
            {activeView === "findings" && (
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 min-h-[620px]">
                {/* File Tree Left (Column 1) */}
                <div className="lg:col-span-3">
                  <FileTree
                    fileRisks={runData?.file_risks || []}
                    bugs={bugs}
                    selectedFile={fileFilter}
                    onSelectFile={setFileFilter}
                  />
                </div>

                {/* Findings Table Center (Column 2) */}
                <div className="lg:col-span-4 xl:col-span-4">
                  <FindingsTable
                    bugs={bugs}
                    selectedBug={selectedBug}
                    onSelectBug={(b) => setSelectedBugId(b.id)}
                    runId={activeRunId}
                    fileFilter={fileFilter}
                    onClearFileFilter={() => setFileFilter(null)}
                    onUpdateWorkflowState={handleUpdateWorkflowState}
                    onSelectFile={setFileFilter}
                  />
                </div>

                {/* Detail Drawer Beside Table Right (Column 3) */}
                <div className="lg:col-span-5 xl:col-span-5">
                  <DefectDetailDrawer
                    bug={selectedBug}
                    runData={runData}
                    runId={activeRunId}
                    beginnerMode={beginnerMode}
                    onToggleBeginnerMode={() => setBeginnerMode(!beginnerMode)}
                    onExportPatch={handleExportPatch}
                    onOpenAssistant={handleOpenAssistant}
                    onUpdateWorkflowState={handleUpdateWorkflowState}
                  />
                </div>
              </div>
            )}

            {/* VIEW: AGENTS */}
            {activeView === "agents" && (
              <div className="space-y-6">
                <AgentNetworkGraph agentStates={agentStates} currentAgent={currentAgent} />
                <AgentDebatePanel debates={runData?.debates || []} consensusScore={runData?.consensus_score || 96} />
              </div>
            )}

            {/* VIEW: RUN HISTORY */}
            {activeView === "history" && (
              <RunHistoryView
                currentRunId={activeRunId}
                onSelectRun={(id) => {
                  setActiveRunId(id);
                  setActiveView("overview");
                }}
                onOpenCompare={(baseId, compId) => {
                  setCompareBaseId(baseId);
                  setCompareTargetId(compId);
                  setCompareModalOpen(true);
                }}
              />
            )}

            {/* VIEW: REPORTS */}
            {activeView === "reports" && (
              <ReportsView
                runData={runData}
                runId={activeRunId}
                onExportPatch={handleExportPatch}
              />
            )}

            {/* VIEW: INTEGRATIONS */}
            {activeView === "integrations" && (
              <IntegrationsView runData={runData} />
            )}

            {/* VIEW: SETTINGS */}
            {activeView === "settings" && (
              <SettingsView
                llmProvider={llmProvider}
                onSelectProvider={setLlmProvider}
                theme={theme}
                onToggleTheme={() => setTheme((t) => (t === "light" ? "dark" : "light"))}
              />
            )}

          </main>

          {/* 3. Mesh Assistant Slide-Over Right Panel */}
          <MeshAssistant
            isOpen={assistantOpen}
            onClose={() => setAssistantOpen(false)}
            runData={runData}
            onSelectBug={(b) => {
              setSelectedBugId(b.id);
              setActiveView("findings");
            }}
            onExportPatch={handleExportPatch}
            onShowDiff={() => {
              setActiveView("findings");
            }}
            pendingPrompt={pendingAssistantPrompt}
            onClearPendingPrompt={() => setPendingAssistantPrompt(null)}
          />

          {/* Floating "Ask Mesh Assistant" button when assistant is collapsed (Screenshot 3) */}
          {!assistantOpen && (
            <button
              onClick={() => setAssistantOpen(true)}
              className="fixed bottom-5 right-5 z-30 flex items-center gap-2 px-4 py-2.5 rounded-full bg-[#2457F5] hover:bg-[#1A44D4] text-white text-xs font-semibold shadow-lg hover:shadow-xl transition-all cursor-pointer"
            >
              <Bot className="w-4 h-4" />
              <span>Ask Mesh Assistant</span>
            </button>
          )}
        </div>
      </div>

      {/* New Project Modal */}
      <NewProjectModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmitSnippet={handleSubmitSnippet}
        onUploadZip={handleUploadZip}
        onLaunchDemo={handleLaunchDemo}
      />

      {/* Compare Runs Modal */}
      <CompareRunsModal
        isOpen={compareModalOpen}
        onClose={() => setCompareModalOpen(false)}
        initialBaseRunId={compareBaseId}
        initialCompareRunId={compareTargetId}
        availableRuns={allRuns}
      />
    </div>
  );
}
