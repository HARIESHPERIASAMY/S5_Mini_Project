import React, { useState } from 'react';
import { Flame, FileCode2, ShieldAlert } from 'lucide-react';

export default function RiskHeatmap({ fileRisks = [] }) {
  const [activeFile, setActiveFile] = useState(null);

  const getRiskColor = (score) => {
    if (score >= 70) return { bg: "bg-rose-950/80", border: "border-rose-500", text: "text-rose-400", glow: "shadow-[0_0_15px_rgba(244,63,94,0.3)]", tag: "CRITICAL" };
    if (score >= 45) return { bg: "bg-amber-950/80", border: "border-amber-500", text: "text-amber-400", glow: "shadow-[0_0_12px_rgba(245,158,11,0.25)]", tag: "HIGH" };
    if (score >= 25) return { bg: "bg-yellow-950/70", border: "border-yellow-500/70", text: "text-yellow-400", glow: "", tag: "MEDIUM" };
    return { bg: "bg-emerald-950/70", border: "border-emerald-500/60", text: "text-emerald-400", glow: "", tag: "LOW" };
  };

  return (
    <div className="glass-panel rounded-2xl p-5 border border-slate-800 flex flex-col">
      <div className="flex items-center justify-between pb-3 border-b border-mesh-border mb-4">
        <div className="flex items-center gap-2">
          <Flame className="w-4 h-4 text-rose-400" />
          <h3 className="text-sm font-semibold text-white tracking-wide uppercase font-mono">
            Codebase Risk Density Heatmap
          </h3>
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 font-mono">
            {fileRisks.length} Modules Monitored
          </span>
        </div>

        {/* Legend */}
        <div className="flex items-center gap-3 text-xs font-mono">
          <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded bg-rose-500" /> Critical (&gt;70%)</span>
          <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded bg-amber-500" /> High (45-70%)</span>
          <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded bg-yellow-500" /> Medium (25-45%)</span>
          <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded bg-emerald-500" /> Low (&lt;25%)</span>
        </div>
      </div>

      {/* Grid of File Tiles */}
      {fileRisks.length === 0 ? (
        <div className="flex flex-col items-center justify-center p-8 text-slate-500 text-xs font-mono">
          <span>No static risk models loaded yet. Launch analysis to build heatmap.</span>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
          {fileRisks.map((file, idx) => {
            const risk = getRiskColor(file.risk_score);
            const isSelected = activeFile?.file_path === file.file_path;

            return (
              <div
                key={idx}
                onClick={() => setActiveFile(file)}
                className={`p-3.5 rounded-xl border ${risk.border} ${risk.bg} ${risk.glow} cursor-pointer transition-all duration-200 transform hover:-translate-y-0.5 ${isSelected ? "ring-2 ring-cyan-400" : ""}`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-2 min-w-0">
                    <FileCode2 className={`w-4 h-4 ${risk.text} flex-shrink-0`} />
                    <span className="text-xs font-mono font-bold text-white truncate">
                      {file.file_path}
                    </span>
                  </div>
                  <span className={`text-[10px] font-mono font-bold px-1.5 py-0.5 rounded border border-current ${risk.text}`}>
                    {file.risk_score}%
                  </span>
                </div>

                {/* Metrics Badges */}
                <div className="mt-3 grid grid-cols-3 gap-1.5 text-center text-[10px] font-mono">
                  <div className="p-1 rounded bg-slate-900/60 border border-slate-800">
                    <span className="text-slate-400 block">LOC</span>
                    <span className="font-bold text-white">{file.loc}</span>
                  </div>
                  <div className="p-1 rounded bg-slate-900/60 border border-slate-800">
                    <span className="text-slate-400 block">Cyclomatic</span>
                    <span className="font-bold text-cyan-400">{file.cyclomatic_complexity}</span>
                  </div>
                  <div className="p-1 rounded bg-slate-900/60 border border-slate-800">
                    <span className="text-slate-400 block">Smells</span>
                    <span className={`font-bold ${file.security_smells > 0 ? "text-rose-400" : "text-emerald-400"}`}>
                      {file.security_smells}
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Selected File Detailed Drawer */}
      {activeFile && (
        <div className="mt-4 p-4 rounded-xl glass-panel-glow border border-cyan-500/40 text-xs font-mono flex flex-col md:flex-row items-start justify-between gap-3">
          <div className="flex items-start gap-3">
            <ShieldAlert className="w-5 h-5 text-cyan-400 flex-shrink-0 mt-0.5" />
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-white text-sm">{activeFile.file_path}</span>
                <span className="px-2 py-0.5 rounded bg-cyan-950 border border-cyan-800 text-cyan-300">
                  Risk Level: {activeFile.risk_level} ({activeFile.risk_score}%)
                </span>
              </div>
              <p className="text-slate-400 mt-1 text-[11px]">
                Analyzed lines: {activeFile.loc} | Cyclomatic Complexity: {activeFile.cyclomatic_complexity} | Smells detected: {activeFile.security_smells}
              </p>
            </div>
          </div>
          <button
            onClick={() => setActiveFile(null)}
            className="text-slate-400 hover:text-white px-2 py-1 bg-slate-800 rounded text-xs"
          >
            Close Details
          </button>
        </div>
      )}
    </div>
  );
}
