import React, { useState } from 'react';
import { 
  Network, Cpu, FileSearch, FlaskConical, PlaySquare, 
  Tag, Compass, Wrench, MessageSquareDiff, FileSpreadsheet,
  CheckCircle2, Loader2, ArrowRight, Route
} from 'lucide-react';

export default function AgentNetworkGraph({ agentStates = {}, currentAgent = "orchestrator" }) {
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [viewMode, setViewMode] = useState("network"); // "network" | "flightpath"

  // 9 cooperating agents with coordinates in topology
  const agents = [
    { id: "orchestrator", name: "Orchestrator", step: 1, icon: Cpu, role: "Swarm Coordinator & State DAG Planner", x: 400, y: 55 },
    { id: "static_analysis_agent", name: "Static Analysis", step: 2, icon: FileSearch, role: "AST Parser & Security Smell Auditor", x: 160, y: 155 },
    { id: "test_generation_agent", name: "Test Generation", step: 3, icon: FlaskConical, role: "Boundary & Property Test Synthesizer", x: 400, y: 165 },
    { id: "test_execution_agent", name: "Test Execution", step: 4, icon: PlaySquare, role: "Sandboxed Runner & Flaky Detector", x: 640, y: 155 },
    { id: "bug_classification_agent", name: "Bug Classifier", step: 5, icon: Tag, role: "Severity & Category Deduplicator", x: 160, y: 285 },
    { id: "root_cause_agent", name: "Root Cause", step: 6, icon: Compass, role: "AST Line Tracer & Causal Chain Builder", x: 400, y: 285 },
    { id: "auto_fix_agent", name: "Auto-Fix Engine", step: 7, icon: Wrench, role: "Unified Diff Patcher & Sandbox Re-verifier", x: 640, y: 285 },
    { id: "critic_agent", name: "Critic Reviewer", step: 8, icon: MessageSquareDiff, role: "Hallucination Auditor & Debate Consensus", x: 270, y: 405 },
    { id: "report_agent", name: "Report Agent", step: 9, icon: FileSpreadsheet, role: "Executive Audit & Report Synthesizer", x: 530, y: 405 }
  ];

  // Pipeline connections for network view
  const connections = [
    { from: "orchestrator", to: "static_analysis_agent" },
    { from: "orchestrator", to: "test_generation_agent" },
    { from: "orchestrator", to: "test_execution_agent" },
    { from: "static_analysis_agent", to: "test_generation_agent" },
    { from: "test_generation_agent", to: "test_execution_agent" },
    { from: "test_execution_agent", to: "bug_classification_agent" },
    { from: "bug_classification_agent", to: "root_cause_agent" },
    { from: "root_cause_agent", to: "auto_fix_agent" },
    { from: "auto_fix_agent", to: "critic_agent" },
    { from: "critic_agent", to: "report_agent" },
    { from: "report_agent", to: "orchestrator" },
  ];

  const getAgentStatus = (id) => {
    if (agentStates[id]) return agentStates[id];
    if (currentAgent === id) return "RUNNING";
    return "IDLE";
  };

  const getStatusStyle = (status) => {
    switch (status) {
      case "RUNNING":
        return {
          bg: "bg-[#EAF1FF]",
          border: "#2563EB",
          text: "text-[#1D4ED8]",
          badgeBg: "bg-[#EAF1FF] text-[#1D4ED8] border-[#B2CCFF]",
          cardBg: "#FFFFFF",
          glow: "rgba(37, 99, 235, 0.25)"
        };
      case "COMPLETED":
        return {
          bg: "bg-[#E7F8EE]",
          border: "#16A34A",
          text: "text-[#14753B]",
          badgeBg: "bg-[#E7F8EE] text-[#14753B] border-[#A6F4C5]",
          cardBg: "#FFFFFF",
          glow: "rgba(22, 163, 74, 0.15)"
        };
      case "FAILED":
        return {
          bg: "bg-[#FEECEC]",
          border: "#DC2626",
          text: "text-[#B42318]",
          badgeBg: "bg-[#FEECEC] text-[#B42318] border-[#FECDCA]",
          cardBg: "#FFFFFF",
          glow: "rgba(220, 38, 38, 0.2)"
        };
      default:
        return {
          bg: "bg-[#F8FAFC]",
          border: "#E2E8F0",
          text: "text-[#5B6577]",
          badgeBg: "bg-[#F1F5F9] text-[#5B6577] border-[#E2E8F0]",
          cardBg: "#FAFCFF",
          glow: "transparent"
        };
    }
  };

  return (
    <div className="card-surface p-4 sm:p-5 bg-white border border-[#E3E8F0] rounded-2xl flex flex-col h-[520px] shadow-xs relative">
      {/* Header & View Toggle */}
      <div className="flex items-center justify-between pb-3 border-b border-[#E3E8F0] gap-3">
        <div className="flex items-center gap-2">
          <Network className="w-4 h-4 text-[#2563EB]" />
          <h3 className="text-xs sm:text-sm font-heading font-bold text-[#0F172A] uppercase tracking-wider font-mono">
            Live Agent Swarm
          </h3>
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-[#F1F5F9] border border-[#E2E8F0] text-[#5B6577] font-mono">
            9 Cooperating Nodes
          </span>
        </div>

        {/* View Toggle + Status Legend */}
        <div className="flex items-center gap-3">
          {/* Toggle Button */}
          <div className="flex items-center p-0.5 rounded-lg bg-[#F1F5F9] border border-[#E2E8F0] text-xs font-mono">
            <button
              onClick={() => setViewMode("network")}
              className={`flex items-center gap-1 px-2.5 py-1 rounded-[6px] transition-all cursor-pointer ${
                viewMode === "network"
                  ? "bg-white text-[#0F172A] font-bold shadow-xs"
                  : "text-[#5B6577] hover:text-[#0F172A]"
              }`}
            >
              <Network className="w-3 h-3" />
              <span>Network</span>
            </button>
            <button
              onClick={() => setViewMode("flightpath")}
              className={`flex items-center gap-1 px-2.5 py-1 rounded-[6px] transition-all cursor-pointer ${
                viewMode === "flightpath"
                  ? "bg-white text-[#0F172A] font-bold shadow-xs"
                  : "text-[#5B6577] hover:text-[#0F172A]"
              }`}
            >
              <Route className="w-3 h-3" />
              <span>Flight Path</span>
            </button>
          </div>

          {/* Legend */}
          <div className="hidden sm:flex items-center gap-2.5 text-[11px] font-mono text-[#5B6577]">
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-[#2563EB] animate-pulse" />
              <span>Active</span>
            </span>
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-[#16A34A]" />
              <span>Done</span>
            </span>
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-[#CBD5E1]" />
              <span>Standby</span>
            </span>
          </div>
        </div>
      </div>

      {/* Main View Area */}
      <div className="relative flex-1 w-full h-full min-h-0 overflow-hidden">
        {viewMode === "network" ? (
          /* Network 2D Canvas */
          <svg className="w-full h-full" viewBox="0 0 800 480" preserveAspectRatio="xMidYMid meet">
            <defs>
              <filter id="lightGlow" x="-20%" y="-20%" width="140%" height="140%">
                <feDropShadow dx="0" dy="2" stdDeviation="4" floodColor="#2563EB" floodOpacity="0.2" />
              </filter>
            </defs>

            {/* Connection Lines */}
            {connections.map((c, i) => {
              const a1 = agents.find((a) => a.id === c.from);
              const a2 = agents.find((a) => a.id === c.to);
              if (!a1 || !a2) return null;
              const isBeamActive = currentAgent === c.from || currentAgent === c.to;
              return (
                <g key={`conn-${i}`}>
                  <line
                    x1={a1.x}
                    y1={a1.y}
                    x2={a2.x}
                    y2={a2.y}
                    stroke={isBeamActive ? "#2563EB" : "#E2E8F0"}
                    strokeWidth={isBeamActive ? "2" : "1.5"}
                    strokeDasharray={isBeamActive ? "6, 4" : "none"}
                  />
                  {isBeamActive && (
                    <circle r="3.5" fill="#2563EB">
                      <animateMotion
                        path={`M ${a1.x} ${a1.y} L ${a2.x} ${a2.y}`}
                        dur="1.8s"
                        repeatCount="indefinite"
                      />
                    </circle>
                  )}
                </g>
              );
            })}

            {/* Nodes */}
            {agents.map((agent) => {
              const status = getAgentStatus(agent.id);
              const style = getStatusStyle(status);
              const isSelected = selectedAgent?.id === agent.id;
              const Icon = agent.icon;

              return (
                <g
                  key={agent.id}
                  transform={`translate(${agent.x}, ${agent.y})`}
                  onClick={() => setSelectedAgent(agent)}
                  className="cursor-pointer transition-transform hover:scale-105"
                >
                  {/* Outer Pulse Ring for Running */}
                  {status === "RUNNING" && (
                    <circle
                      r="36"
                      fill="none"
                      stroke="#2563EB"
                      strokeWidth="2"
                      opacity="0.4"
                      className="animate-ping"
                    />
                  )}

                  {/* Node Rect Card */}
                  <rect
                    x="-75"
                    y="-25"
                    width="150"
                    height="50"
                    rx="12"
                    fill={style.cardBg}
                    stroke={isSelected ? "#2563EB" : style.border}
                    strokeWidth={isSelected ? "2.5" : "1.5"}
                    filter="drop-shadow(0 1px 2px rgba(15, 23, 42, 0.05))"
                  />

                  {/* Node Content */}
                  <foreignObject x="-70" y="-21" width="140" height="42">
                    <div className="flex items-center gap-2 h-full px-1">
                      <div
                        className={`w-7 h-7 rounded-lg ${style.bg} border flex items-center justify-center ${style.text} flex-shrink-0`}
                        style={{ borderColor: style.border }}
                      >
                        <Icon className="w-3.5 h-3.5" />
                      </div>
                      <div className="flex flex-col min-w-0">
                        <span className="text-[11px] font-bold text-[#0F172A] truncate font-heading">
                          {agent.name}
                        </span>
                        <div className="flex items-center gap-1">
                          {status === "RUNNING" ? (
                            <Loader2 className="w-2.5 h-2.5 animate-spin text-[#2563EB]" />
                          ) : status === "COMPLETED" ? (
                            <CheckCircle2 className="w-2.5 h-2.5 text-[#16A34A]" />
                          ) : (
                            <span className="w-1.5 h-1.5 rounded-full bg-[#CBD5E1]" />
                          )}
                          <span className={`text-[9px] uppercase font-mono font-semibold ${style.text}`}>
                            {status}
                          </span>
                        </div>
                      </div>
                    </div>
                  </foreignObject>
                </g>
              );
            })}
          </svg>
        ) : (
          /* Flight Path (Horizontal Pipeline Timeline) */
          <div className="h-full flex flex-col justify-center px-4 overflow-y-auto">
            <div className="space-y-2.5 py-4">
              {agents.map((agent, idx) => {
                const status = getAgentStatus(agent.id);
                const style = getStatusStyle(status);
                const Icon = agent.icon;
                const isCurrent = currentAgent === agent.id;

                return (
                  <div
                    key={agent.id}
                    onClick={() => setSelectedAgent(agent)}
                    className={`flex items-center justify-between p-2.5 rounded-xl border bg-white cursor-pointer transition-all ${
                      isCurrent
                        ? "border-[#2563EB] ring-2 ring-[#EAF1FF] shadow-xs"
                        : "border-[#E3E8F0] hover:border-[#CBD5E1]"
                    }`}
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      <span className="text-[10px] font-mono font-bold text-[#5B6577] w-5 text-right">
                        0{agent.step}
                      </span>
                      <div className={`w-8 h-8 rounded-lg ${style.bg} flex items-center justify-center ${style.text} flex-shrink-0 border`} style={{ borderColor: style.border }}>
                        <Icon className="w-4 h-4" />
                      </div>
                      <div className="min-w-0">
                        <h4 className="text-xs font-bold text-[#0F172A] truncate font-heading">
                          {agent.name}
                        </h4>
                        <p className="text-[11px] text-[#5B6577] truncate">{agent.role}</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded border ${style.badgeBg}`}>
                        {status}
                      </span>
                      {idx < agents.length - 1 && (
                        <ArrowRight className="w-3.5 h-3.5 text-[#CBD5E1] hidden sm:block" />
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Selected Agent Quick Inspector Drawer */}
        {selectedAgent && (
          <div className="absolute bottom-2 left-2 right-2 bg-white/95 backdrop-blur-md rounded-xl p-3 flex items-center justify-between border border-[#2563EB] shadow-md z-10">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-[#EAF1FF] border border-[#B2CCFF] flex items-center justify-center text-[#2563EB]">
                <selectedAgent.icon className="w-4 h-4" />
              </div>
              <div>
                <h4 className="text-xs font-bold text-[#0F172A] font-heading">{selectedAgent.name}</h4>
                <p className="text-[11px] text-[#5B6577]">{selectedAgent.role}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-[#F1F5F9] border border-[#E2E8F0] text-[#0F172A]">
                State: {getAgentStatus(selectedAgent.id)}
              </span>
              <button
                onClick={() => setSelectedAgent(null)}
                className="text-xs text-[#5B6577] hover:text-[#0F172A] px-2 py-0.5 rounded hover:bg-[#F1F5F9] cursor-pointer"
              >
                ✕
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Report Agent Status Bar */}
      <div className="pt-2.5 border-t border-[#E3E8F0] flex items-center justify-between text-xs font-mono text-[#5B6577]">
        <div className="flex items-center gap-2 truncate">
          <FileSpreadsheet className="w-3.5 h-3.5 text-[#2563EB] flex-shrink-0" />
          <span className="truncate">
            Phase: <strong className="text-[#0F172A]">@{currentAgent}</strong> active
          </span>
        </div>
        <span className="text-[11px] text-[#2563EB] font-bold">
          {agentStates["report_agent"] === "COMPLETED" ? "Audit Ready" : "Swarm In-Flight"}
        </span>
      </div>
    </div>
  );
}
