import React, { useState } from 'react';
import { 
  Network, Cpu, FileSearch, FlaskConical, PlaySquare, 
  Tag, Compass, Wrench, MessageSquareDiff, FileSpreadsheet,
  CheckCircle2, Loader2, AlertCircle
} from 'lucide-react';

export default function AgentNetworkGraph({ agentStates = {}, currentAgent = "orchestrator" }) {
  const [selectedAgent, setSelectedAgent] = useState(null);

  // 9 cooperating agents with coordinates in topology
  const agents = [
    { id: "orchestrator", name: "Orchestrator", icon: Cpu, role: "Swarm Coordinator & State DAG Planner", x: 400, y: 50 },
    { id: "static_analysis_agent", name: "Static Analysis", icon: FileSearch, role: "AST Parser & Security Smell Auditor", x: 160, y: 150 },
    { id: "test_generation_agent", name: "Test Generation", icon: FlaskConical, role: "Boundary & Property Test Synthesizer", x: 400, y: 160 },
    { id: "test_execution_agent", name: "Test Execution", icon: PlaySquare, role: "Sandboxed Runner & Flaky Detector", x: 640, y: 150 },
    { id: "bug_classification_agent", name: "Bug Classifier", icon: Tag, role: "Severity & Category Deduplicator", x: 160, y: 280 },
    { id: "root_cause_agent", name: "Root Cause", icon: Compass, role: "AST Line Tracer & Causal Chain Builder", x: 400, y: 280 },
    { id: "auto_fix_agent", name: "Auto-Fix Engine", icon: Wrench, role: "Unified Diff Patcher & Sandbox Re-verifier", x: 640, y: 280 },
    { id: "critic_agent", name: "Critic Reviewer", icon: MessageSquareDiff, role: "Hallucination Auditor & Debate Consensus", x: 260, y: 400 },
    { id: "report_agent", name: "Report Agent", icon: FileSpreadsheet, role: "Executive Audit & Report Synthesizer", x: 540, y: 400 }
  ];

  // Connections in workflow
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

  const getStatusColor = (status) => {
    switch (status) {
      case "RUNNING":
        return {
          bg: "bg-cyan-950/80",
          border: "border-cyan-400",
          text: "text-cyan-300",
          shadow: "shadow-[0_0_20px_rgba(6,182,212,0.6)]",
          glow: "#06b6d4"
        };
      case "COMPLETED":
        return {
          bg: "bg-emerald-950/80",
          border: "border-emerald-400",
          text: "text-emerald-300",
          shadow: "shadow-[0_0_15px_rgba(16,185,129,0.4)]",
          glow: "#10b981"
        };
      case "FAILED":
        return {
          bg: "bg-rose-950/80",
          border: "border-rose-400",
          text: "text-rose-300",
          shadow: "shadow-[0_0_15px_rgba(244,63,94,0.5)]",
          glow: "#f43f5e"
        };
      case "THINKING":
        return {
          bg: "bg-amber-950/80",
          border: "border-amber-400",
          text: "text-amber-300",
          shadow: "shadow-[0_0_15px_rgba(245,158,11,0.5)]",
          glow: "#f59e0b"
        };
      default:
        return {
          bg: "bg-slate-900/70",
          border: "border-slate-800",
          text: "text-slate-400",
          shadow: "",
          glow: "#334155"
        };
    }
  };

  return (
    <div className="glass-panel rounded-2xl p-4 relative overflow-hidden flex flex-col h-[520px]">
      {/* Topology Header */}
      <div className="flex items-center justify-between pb-3 border-b border-mesh-border">
        <div className="flex items-center gap-2">
          <Network className="w-4 h-4 text-cyan-400" />
          <h2 className="text-sm font-semibold tracking-wide text-white uppercase font-mono">
            Live Agent Swarm Network
          </h2>
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-800 border border-slate-700 text-slate-300 font-mono">
            9 Cooperating Nodes
          </span>
        </div>
        <div className="flex items-center gap-3 text-xs font-mono">
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
            <span className="text-cyan-300">Active</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-400" />
            <span className="text-emerald-300">Verified</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-slate-600" />
            <span className="text-slate-400">Standby</span>
          </div>
        </div>
      </div>

      {/* SVG Canvas Topology */}
      <div className="relative flex-1 w-full h-full">
        <svg className="w-full h-full" viewBox="0 0 800 480" preserveAspectRatio="xMidYMid meet">
          <defs>
            {/* Animated Gradient Beam */}
            <linearGradient id="beamGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.8" />
              <stop offset="50%" stopColor="#8b5cf6" stopOpacity="0.8" />
              <stop offset="100%" stopColor="#22d3ee" stopOpacity="0.3" />
            </linearGradient>
            <filter id="glowFilter" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          </defs>

          {/* Connection Lines with glowing data flow */}
          {connections.map((c, i) => {
            const a1 = agents.find(a => a.id === c.from);
            const a2 = agents.find(a => a.id === c.to);
            if (!a1 || !a2) return null;
            const isBeamActive = currentAgent === c.from || currentAgent === c.to;
            return (
              <g key={`conn-${i}`}>
                <line
                  x1={a1.x}
                  y1={a1.y}
                  x2={a2.x}
                  y2={a2.y}
                  stroke={isBeamActive ? "#06b6d4" : "#1e293b"}
                  strokeWidth={isBeamActive ? "2.5" : "1.5"}
                  strokeDasharray={isBeamActive ? "6, 4" : "none"}
                  className={isBeamActive ? "animate-pulse" : ""}
                  filter={isBeamActive ? "url(#glowFilter)" : "none"}
                />
                {isBeamActive && (
                  <circle r="3" fill="#22d3ee">
                    <animateMotion
                      path={`M ${a1.x} ${a1.y} L ${a2.x} ${a2.y}`}
                      dur="2s"
                      repeatCount="indefinite"
                    />
                  </circle>
                )}
              </g>
            );
          })}

          {/* Agent Nodes */}
          {agents.map((agent) => {
            const status = getAgentStatus(agent.id);
            const style = getStatusColor(status);
            const isSelected = selectedAgent?.id === agent.id;
            const Icon = agent.icon;

            return (
              <g
                key={agent.id}
                transform={`translate(${agent.x}, ${agent.y})`}
                onClick={() => setSelectedAgent(agent)}
                className="cursor-pointer transition-transform hover:scale-105"
              >
                {/* Outer Pulse Halo if RUNNING */}
                {status === "RUNNING" && (
                  <circle
                    r="34"
                    fill="none"
                    stroke="#06b6d4"
                    strokeWidth="2"
                    opacity="0.6"
                    className="animate-ping"
                  />
                )}

                {/* Node Body Card */}
                <rect
                  x="-75"
                  y="-26"
                  width="150"
                  height="52"
                  rx="12"
                  fill="#0b1120"
                  stroke={style.glow}
                  strokeWidth={isSelected ? "2.5" : "1.5"}
                  filter={status === "RUNNING" ? "url(#glowFilter)" : "none"}
                />

                {/* Node Label & Icon */}
                <foreignObject x="-70" y="-22" width="140" height="44">
                  <div className="flex items-center gap-2 h-full px-1">
                    <div className={`w-8 h-8 rounded-lg ${style.bg} border ${style.border} flex items-center justify-center ${style.text} flex-shrink-0`}>
                      <Icon className="w-4 h-4" />
                    </div>
                    <div className="flex flex-col min-w-0">
                      <span className="text-[11px] font-semibold text-white truncate font-sans">
                        {agent.name}
                      </span>
                      <div className="flex items-center gap-1">
                        {status === "RUNNING" ? (
                          <Loader2 className="w-2.5 h-2.5 animate-spin text-cyan-400" />
                        ) : status === "COMPLETED" ? (
                          <CheckCircle2 className="w-2.5 h-2.5 text-emerald-400" />
                        ) : (
                          <span className="w-1.5 h-1.5 rounded-full bg-slate-600" />
                        )}
                        <span className={`text-[9px] uppercase font-mono ${style.text}`}>
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

        {/* Selected Agent Quick Inspector Drawer */}
        {selectedAgent && (
          <div className="absolute bottom-3 left-3 right-3 glass-panel-glow rounded-xl p-3 flex items-center justify-between border border-cyan-500/30">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-cyan-950/80 border border-cyan-500/60 flex items-center justify-center text-cyan-400">
                <selectedAgent.icon className="w-4 h-4" />
              </div>
              <div>
                <h4 className="text-xs font-bold text-white font-mono">{selectedAgent.name}</h4>
                <p className="text-[11px] text-slate-400">{selectedAgent.role}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950/70 border border-cyan-800 text-cyan-300">
                Status: {getAgentStatus(selectedAgent.id)}
              </span>
              <button
                onClick={() => setSelectedAgent(null)}
                className="text-xs text-slate-400 hover:text-white px-2 py-0.5"
              >
                ✕
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
