import React, { useState, useEffect, useRef } from 'react';
import { Terminal, Copy, Check, ArrowDownCircle } from 'lucide-react';

export default function LiveTerminal({ logs = [] }) {
  const [filterLevel, setFilterLevel] = useState("ALL");
  const [copied, setCopied] = useState(false);
  const [autoScroll, setAutoScroll] = useState(true);
  const terminalEndRef = useRef(null);

  useEffect(() => {
    if (autoScroll && terminalEndRef.current) {
      terminalEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, autoScroll]);

  const filteredLogs = logs.filter(l => {
    if (filterLevel === "ALL") return true;
    return (l.level || "INFO").toUpperCase() === filterLevel;
  });

  const handleCopyLogs = () => {
    const text = logs.map(l => `[${l.timestamp || ''}] [${l.agent_name || 'system'}] [${l.level || 'INFO'}]: ${l.message || ''}`).join('\n');
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getLevelStyle = (level) => {
    switch ((level || "INFO").toUpperCase()) {
      case "ERROR":
        return "text-rose-400 bg-rose-950/60 border-rose-800/60";
      case "WARN":
        return "text-amber-400 bg-amber-950/60 border-amber-800/60";
      case "TELEMETRY":
        return "text-cyan-400 bg-cyan-950/60 border-cyan-800/60";
      default:
        return "text-emerald-400 bg-emerald-950/60 border-emerald-800/60";
    }
  };

  return (
    <div className="glass-panel rounded-2xl p-4 flex flex-col h-[520px] relative overflow-hidden font-mono border border-slate-800">
      {/* Terminal Title Bar */}
      <div className="flex items-center justify-between pb-3 border-b border-mesh-border text-xs">
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4 text-cyan-400" />
          <span className="font-semibold text-white tracking-wide uppercase">
            Telemetry & Agent Log Stream
          </span>
          <span className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 text-[10px]">
            {logs.length} lines
          </span>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          {/* Level Filter */}
          <select
            value={filterLevel}
            onChange={(e) => setFilterLevel(e.target.value)}
            className="bg-slate-900 border border-slate-700 text-slate-300 rounded px-2 py-0.5 text-[11px] focus:outline-none"
          >
            <option value="ALL">ALL LEVELS</option>
            <option value="INFO">INFO</option>
            <option value="WARN">WARN</option>
            <option value="ERROR">ERROR</option>
            <option value="TELEMETRY">TELEMETRY</option>
          </select>

          {/* Copy */}
          <button
            onClick={handleCopyLogs}
            title="Copy Logs"
            className="p-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
          </button>

          {/* Auto Scroll Toggle */}
          <button
            onClick={() => setAutoScroll(!autoScroll)}
            title="Auto-Scroll"
            className={`p-1 rounded transition-colors ${autoScroll ? "bg-cyan-950 text-cyan-300 border border-cyan-800" : "bg-slate-800 text-slate-500"}`}
          >
            <ArrowDownCircle className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Terminal Output Area */}
      <div className="flex-1 overflow-y-auto pt-3 text-[11px] leading-relaxed space-y-1.5 pr-1 select-text">
        {filteredLogs.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-slate-500 gap-2">
            <span className="animate-pulse">Waiting for multi-agent swarm activity...</span>
            <span className="text-[10px] text-slate-600">Click "Run Demo Project" to launch analysis stream</span>
          </div>
        ) : (
          filteredLogs.map((log, idx) => {
            const timeStr = log.timestamp
              ? new Date(log.timestamp).toLocaleTimeString()
              : '--:--:--';
            const levelClass = getLevelStyle(log.level);

            return (
              <div key={idx} className="flex items-start gap-2 hover:bg-slate-900/50 rounded px-1.5 py-0.5 transition-colors">
                <span className="text-slate-500 flex-shrink-0 text-[10px]">[{timeStr}]</span>
                <span className={`px-1.5 py-0.2 rounded border text-[9px] uppercase font-bold flex-shrink-0 ${levelClass}`}>
                  {log.level || "INFO"}
                </span>
                <span className="text-cyan-400 font-semibold flex-shrink-0 text-[10px]">
                  @{log.agent_name || "orchestrator"}:
                </span>
                <span className="text-slate-300 break-words flex-1">
                  {log.message || JSON.stringify(log.data || "")}
                </span>
              </div>
            );
          })
        )}
        <div ref={terminalEndRef} />
      </div>

      {/* Bottom Prompt Bar */}
      <div className="mt-2 pt-2 border-t border-mesh-border flex items-center justify-between text-[10px] text-slate-500">
        <span className="flex items-center gap-1">
          <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping" />
          <span>WebSocket Stream Connected</span>
        </span>
        <span>sentinel-node://localhost:8000/ws</span>
      </div>
    </div>
  );
}
