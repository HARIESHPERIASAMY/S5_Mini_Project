import React, { useState } from 'react';
import { 
  Bug, CheckCircle2, Cpu, 
  HelpCircle, GitPullRequest, Copy, Check, ChevronRight, X
} from 'lucide-react';

export default function BugExplorer({ bugs = [] }) {
  const [selectedBug, setSelectedBug] = useState(null);
  const [filterSeverity, setFilterSeverity] = useState("ALL");
  const [filterCategory, setFilterCategory] = useState("ALL");
  const [beginnerMode, setBeginnerMode] = useState(false);
  const [copiedDiff, setCopiedDiff] = useState(false);

  const filteredBugs = bugs.filter(b => {
    if (filterSeverity !== "ALL" && b.severity !== filterSeverity) return false;
    if (filterCategory !== "ALL" && b.category !== filterCategory) return false;
    return true;
  });

  const getSeverityBadge = (sev) => {
    switch (sev) {
      case "CRITICAL":
        return "bg-rose-950/80 text-rose-300 border-rose-700/80";
      case "HIGH":
        return "bg-amber-950/80 text-amber-300 border-amber-700/80";
      case "MEDIUM":
        return "bg-yellow-950/80 text-yellow-300 border-yellow-700/80";
      default:
        return "bg-slate-800 text-slate-300 border-slate-700";
    }
  };

  const handleCopyDiff = (diffText) => {
    navigator.clipboard.writeText(diffText || "");
    setCopiedDiff(true);
    setTimeout(() => setCopiedDiff(false), 2000);
  };

  return (
    <div className="glass-panel rounded-2xl p-5 border border-slate-800 flex flex-col">
      {/* Table Header & Controls */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-3 pb-4 border-b border-mesh-border mb-4">
        <div className="flex items-center gap-2">
          <Bug className="w-4 h-4 text-rose-400" />
          <h3 className="text-sm font-semibold text-white tracking-wide uppercase font-mono">
            Bug Classification & Self-Healing Ledger
          </h3>
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 font-mono">
            {bugs.length} Defects Detected
          </span>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-2 text-xs font-mono">
          <select
            value={filterSeverity}
            onChange={(e) => setFilterSeverity(e.target.value)}
            className="bg-slate-900 border border-slate-700 text-slate-300 rounded px-2.5 py-1 text-xs focus:outline-none"
          >
            <option value="ALL">ALL SEVERITIES</option>
            <option value="CRITICAL">CRITICAL</option>
            <option value="HIGH">HIGH</option>
            <option value="MEDIUM">MEDIUM</option>
            <option value="LOW">LOW</option>
          </select>

          <select
            value={filterCategory}
            onChange={(e) => setFilterCategory(e.target.value)}
            className="bg-slate-900 border border-slate-700 text-slate-300 rounded px-2.5 py-1 text-xs focus:outline-none"
          >
            <option value="ALL">ALL CATEGORIES</option>
            <option value="LOGIC">LOGIC</option>
            <option value="SECURITY">SECURITY</option>
            <option value="INPUT_VALIDATION">INPUT VALIDATION</option>
            <option value="CONCURRENCY">CONCURRENCY</option>
          </select>
        </div>
      </div>

      {/* Bugs Table */}
      {filteredBugs.length === 0 ? (
        <div className="flex flex-col items-center justify-center p-8 text-slate-500 text-xs font-mono">
          <span>No bugs match current filters.</span>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400">
                <th className="py-2.5 px-3">LOCATION</th>
                <th className="py-2.5 px-3">SEVERITY</th>
                <th className="py-2.5 px-3">CATEGORY</th>
                <th className="py-2.5 px-3">DEFECT TITLE</th>
                <th className="py-2.5 px-3">SELF-HEALING FIX</th>
                <th className="py-2.5 px-3 text-right">ACTION</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filteredBugs.map((bug, idx) => {
                const isSelected = selectedBug?.id === bug.id;
                const isVerified = bug.fix_verified;

                return (
                  <tr
                    key={idx}
                    onClick={() => setSelectedBug(bug)}
                    className={`hover:bg-slate-900/60 cursor-pointer transition-colors ${isSelected ? "bg-slate-900/80 border-l-2 border-cyan-400" : ""}`}
                  >
                    <td className="py-3 px-3 text-cyan-300 font-bold whitespace-nowrap">
                      {bug.file_path}:{bug.line_number}
                    </td>
                    <td className="py-3 px-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${getSeverityBadge(bug.severity)}`}>
                        {bug.severity}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-slate-300">
                      {bug.category}
                    </td>
                    <td className="py-3 px-3 text-white font-medium truncate max-w-xs">
                      {bug.title}
                    </td>
                    <td className="py-3 px-3">
                      {isVerified ? (
                        <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-emerald-950/80 border border-emerald-500/80 text-emerald-300 text-[10px] font-bold">
                          <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                          VERIFIED FIX
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-slate-800 border border-slate-700 text-slate-400 text-[10px]">
                          PROPOSED DIFF
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-3 text-right">
                      <button className="text-cyan-400 hover:text-cyan-300 p-1">
                        <ChevronRight className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Side Drawer for Selected Bug */}
      {selectedBug && (
        <div className="fixed inset-y-0 right-0 w-full md:w-[620px] glass-panel-glow border-l border-mesh-border z-50 p-6 flex flex-col overflow-y-auto shadow-2xl">
          {/* Drawer Header */}
          <div className="flex items-start justify-between pb-4 border-b border-mesh-border">
            <div>
              <div className="flex items-center gap-2">
                <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold border ${getSeverityBadge(selectedBug.severity)}`}>
                  {selectedBug.severity}
                </span>
                <span className="text-xs font-mono text-cyan-300">
                  {selectedBug.category}
                </span>
                {selectedBug.fix_verified && (
                  <span className="px-2 py-0.5 rounded-full bg-emerald-950 border border-emerald-600 text-emerald-300 text-[10px] font-mono font-bold flex items-center gap-1">
                    <CheckCircle2 className="w-3 h-3" />
                    Verified Fix
                  </span>
                )}
              </div>
              <h2 className="text-base font-bold text-white mt-1.5">{selectedBug.title}</h2>
              <p className="text-xs font-mono text-slate-400 mt-0.5">
                Target: {selectedBug.file_path} (Line {selectedBug.line_number})
              </p>
            </div>
            <button
              onClick={() => setSelectedBug(null)}
              className="p-1 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* "Explain like I'm a beginner" Toggle */}
          <div className="mt-4 p-3 rounded-xl bg-slate-900/80 border border-slate-800 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <HelpCircle className="w-4 h-4 text-cyan-400" />
              <div>
                <span className="text-xs font-semibold text-white">Explain Like I'm a Beginner</span>
                <p className="text-[10px] text-slate-400">Simplify technical failure into an intuitive analogy</p>
              </div>
            </div>
            <button
              onClick={() => setBeginnerMode(!beginnerMode)}
              className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${beginnerMode ? "bg-cyan-500" : "bg-slate-700"}`}
            >
              <span className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white transition-transform ${beginnerMode ? "translate-x-4" : "translate-x-1"}`} />
            </button>
          </div>

          {/* Explanation Content */}
          <div className="mt-4">
            {beginnerMode ? (
              <div className="p-4 rounded-xl bg-cyan-950/30 border border-cyan-800/60 text-xs text-slate-200 leading-relaxed whitespace-pre-wrap">
                {selectedBug.beginner_explanation || selectedBug.description}
              </div>
            ) : (
              <div className="space-y-4">
                {/* Description */}
                <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 text-xs text-slate-300 font-mono">
                  <span className="text-slate-400 block mb-1 font-bold">FAILURE DIAGNOSTIC:</span>
                  {selectedBug.description}
                </div>

                {/* Root Cause Causal Chain */}
                {selectedBug.causal_chain && (
                  <div>
                    <h4 className="text-xs font-mono font-bold text-white mb-2 flex items-center gap-1.5">
                      <Cpu className="w-3.5 h-3.5 text-cyan-400" />
                      ROOT CAUSE CAUSAL TRACE
                    </h4>
                    <div className="space-y-1.5 font-mono text-[11px]">
                      {(() => {
                        try {
                          const steps = JSON.parse(selectedBug.causal_chain);
                          return Array.isArray(steps) ? steps.map((s, i) => (
                            <div key={i} className="p-2 rounded bg-slate-900/80 border border-slate-800/80 text-slate-300">
                              {s}
                            </div>
                          )) : null;
                        } catch {
                          return <div className="text-slate-400">{selectedBug.causal_chain}</div>;
                        }
                      })()}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Proposed Fix Diff View */}
          <div className="mt-6 flex-1 flex flex-col">
            <div className="flex items-center justify-between pb-2">
              <h4 className="text-xs font-mono font-bold text-white flex items-center gap-1.5">
                <GitPullRequest className="w-3.5 h-3.5 text-emerald-400" />
                VERIFIED SELF-HEALING DIFF PATCH
              </h4>
              <button
                onClick={() => handleCopyDiff(selectedBug.proposed_fix_diff)}
                className="flex items-center gap-1 text-[11px] font-mono text-cyan-400 hover:text-cyan-300 px-2 py-0.5 rounded bg-slate-800"
              >
                {copiedDiff ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                <span>{copiedDiff ? "Copied" : "Copy Diff"}</span>
              </button>
            </div>

            {/* Sandbox Verification Output */}
            {selectedBug.verification_output && (
              <div className="mb-2 p-2 rounded bg-emerald-950/40 border border-emerald-800/60 text-[11px] font-mono text-emerald-300">
                {selectedBug.verification_output}
              </div>
            )}

            {/* Diff Syntax Highlight Box */}
            <div className="flex-1 bg-slate-950 rounded-xl p-3 border border-slate-800 font-mono text-[11px] overflow-x-auto leading-relaxed">
              {selectedBug.proposed_fix_diff ? (
                selectedBug.proposed_fix_diff.split('\n').map((line, lIdx) => {
                  let lineStyle = "text-slate-400";
                  if (line.startsWith('+') && !line.startsWith('+++')) {
                    lineStyle = "text-emerald-400 bg-emerald-950/30";
                  } else if (line.startsWith('-') && !line.startsWith('---')) {
                    lineStyle = "text-rose-400 bg-rose-950/30";
                  } else if (line.startsWith('@@')) {
                    lineStyle = "text-cyan-400 font-bold";
                  }
                  return (
                    <div key={lIdx} className={`${lineStyle} px-1 rounded`}>
                      {line}
                    </div>
                  );
                })
              ) : (
                <div className="text-slate-500">Patch generation in progress...</div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
