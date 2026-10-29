import React, { useState, useEffect, useRef } from 'react';
import { Terminal, Copy, Check, Pause, Play } from 'lucide-react';

export default function LiveTerminal({ logs = [] }) {
  const [filterLevel, setFilterLevel] = useState("ALL");
  const [filterAgent, setFilterAgent] = useState("ALL");
  const [copied, setCopied] = useState(false);
  const [autoScroll, setAutoScroll] = useState(true);
  const terminalEndRef = useRef(null);

  useEffect(() => {
    if (autoScroll && terminalEndRef.current) {
      terminalEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, autoScroll]);

  // Extract unique agent names for filter
  const agentList = Array.from(new Set(logs.map((l) => l.agent_name).filter(Boolean)));

  const filteredLogs = logs.filter((l) => {
    if (filterLevel !== "ALL" && (l.level || "INFO").toUpperCase() !== filterLevel) {
      return false;
    }
    if (filterAgent !== "ALL" && l.agent_name !== filterAgent) {
      return false;
    }
    return true;
  });

  const handleCopyLogs = () => {
    const text = filteredLogs
      .map(
        (l) =>
          `[${l.timestamp || ''}] [${l.agent_name || 'system'}] [${l.level || 'INFO'}]: ${
            l.message || JSON.stringify(l.data || '')
          }`
      )
      .join('\n');
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getLevelBadge = (level) => {
    switch ((level || "INFO").toUpperCase()) {
      case "ERROR":
        return "bg-[#FEECEC] text-[#B42318] border-[#FECDCA]";
      case "WARN":
        return "bg-[#FFF4E0] text-[#9A5B00] border-[#FEDF89]";
      case "TELEMETRY":
        return "bg-[#EAF1FF] text-[#1D4ED8] border-[#B2CCFF]";
      default:
        return "bg-[#E7F8EE] text-[#14753B] border-[#A6F4C5]";
    }
  };

  const getAgentTag = (name) => {
    const colors = [
      "bg-[#EAF1FF] text-[#1D4ED8]",
      "bg-[#F1EAFE] text-[#6D28D9]",
      "bg-[#E7F8EE] text-[#14753B]",
      "bg-[#FFF4E0] text-[#9A5B00]",
      "bg-[#F8FAFC] text-[#0F172A]"
    ];
    let hash = 0;
    const str = name || "system";
    for (let i = 0; i < str.length; i++) hash = (hash + str.charCodeAt(i)) % colors.length;
    return colors[hash];
  };

  return (
    <div className="card-surface p-4 sm:p-5 bg-white border border-[#E3E8F0] rounded-2xl flex flex-col h-[520px] shadow-xs relative font-mono">
      {/* Title & Controls Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-3 border-b border-[#E3E8F0] gap-2.5">
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4 text-[#2563EB]" />
          <h3 className="text-xs sm:text-sm font-bold text-[#0F172A] tracking-wider uppercase font-mono">
            Telemetry & Agent Log
          </h3>
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-[#F1F5F9] border border-[#E2E8F0] text-[#5B6577]">
            {filteredLogs.length} events
          </span>
        </div>

        {/* Toolbar */}
        <div className="flex flex-wrap items-center gap-1.5 w-full sm:w-auto justify-end">
          {/* Agent Filter */}
          <select
            value={filterAgent}
            onChange={(e) => setFilterAgent(e.target.value)}
            className="h-8 px-2 text-[11px] bg-[#F8FAFC] border border-[#E3E8F0] rounded-lg text-[#0F172A] focus:outline-none cursor-pointer"
            title="Filter by Swarm Agent"
          >
            <option value="ALL">All Agents</option>
            {agentList.map((a) => (
              <option key={a} value={a}>
                @{a}
              </option>
            ))}
          </select>

          {/* Level Filter */}
          <select
            value={filterLevel}
            onChange={(e) => setFilterLevel(e.target.value)}
            className="h-8 px-2 text-[11px] bg-[#F8FAFC] border border-[#E3E8F0] rounded-lg text-[#0F172A] focus:outline-none cursor-pointer"
            title="Filter by Severity Level"
          >
            <option value="ALL">All Levels</option>
            <option value="INFO">INFO</option>
            <option value="WARN">WARN</option>
            <option value="ERROR">ERROR</option>
            <option value="TELEMETRY">TELEMETRY</option>
          </select>

          {/* Pause Scroll Toggle */}
          <button
            onClick={() => setAutoScroll(!autoScroll)}
            title={autoScroll ? "Pause live auto-scroll" : "Resume auto-scroll"}
            className={`h-8 px-2.5 rounded-lg flex items-center gap-1 text-[11px] font-semibold border transition-all cursor-pointer ${
              autoScroll
                ? "bg-[#EAF1FF] text-[#1D4ED8] border-[#B2CCFF]"
                : "bg-[#F8FAFC] text-[#5B6577] border-[#E3E8F0]"
            }`}
          >
            {autoScroll ? <Pause className="w-3 h-3" /> : <Play className="w-3 h-3" />}
            <span className="hidden md:inline">{autoScroll ? "Live" : "Paused"}</span>
          </button>

          {/* Copy Log */}
          <button
            onClick={handleCopyLogs}
            title="Copy filtered logs to clipboard"
            className="h-8 px-2.5 rounded-lg bg-white hover:bg-[#F8FAFC] border border-[#E3E8F0] text-[#0F172A] text-[11px] font-semibold flex items-center gap-1 transition-all cursor-pointer"
          >
            {copied ? <Check className="w-3 h-3 text-[#16A34A]" /> : <Copy className="w-3 h-3 text-[#5B6577]" />}
            <span>{copied ? "Copied" : "Copy"}</span>
          </button>
        </div>
      </div>

      {/* Output Console Box */}
      <div className="flex-1 overflow-y-auto pt-3 text-[11px] leading-relaxed space-y-1.5 pr-1 select-text bg-[#FAFBFD] rounded-xl p-3 mt-2 border border-[#F1F5F9]">
        {filteredLogs.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-[#8E9BAE] text-center gap-2 p-6">
            <Terminal className="w-8 h-8 stroke-1 text-[#CBD5E1]" />
            <p className="font-semibold text-xs text-[#5B6577]">Waiting for multi-agent swarm activity...</p>
            <span className="text-[11px] max-w-sm">
              Click "Run Demo Project" or submit custom code to stream real-time AST, test execution, and auto-fix events.
            </span>
          </div>
        ) : (
          filteredLogs.map((log, idx) => {
            const timeStr = log.timestamp
              ? new Date(log.timestamp).toLocaleTimeString()
              : '--:--:--';
            const levelStyle = getLevelBadge(log.level);
            const agentTagStyle = getAgentTag(log.agent_name);

            return (
              <div
                key={idx}
                className="flex items-start gap-2 hover:bg-white p-1 rounded-md transition-colors border border-transparent hover:border-[#E3E8F0]"
              >
                <span className="text-[#8E9BAE] flex-shrink-0 text-[10px] select-none pt-0.5">
                  [{timeStr}]
                </span>
                <span
                  className={`px-1.5 py-0.2 rounded border text-[9px] uppercase font-bold flex-shrink-0 ${levelStyle}`}
                >
                  {log.level || "INFO"}
                </span>
                <span
                  className={`px-1.5 py-0.2 rounded text-[10px] font-bold flex-shrink-0 ${agentTagStyle}`}
                >
                  @{log.agent_name || "orchestrator"}
                </span>
                <span className="text-[#0F172A] break-words flex-1 font-mono text-[11px]">
                  {log.message || JSON.stringify(log.data || "")}
                </span>
              </div>
            );
          })
        )}
        <div ref={terminalEndRef} />
      </div>

      {/* Console Footer */}
      <div className="pt-2 mt-2 border-t border-[#E3E8F0] flex items-center justify-between text-[11px] text-[#5B6577]">
        <span className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-[#16A34A]" />
          <span>WebSocket Stream Synchronized</span>
        </span>
        <span className="text-[10px] text-[#8E9BAE] font-mono">
          channel: /ws/runs
        </span>
      </div>
    </div>
  );
}
