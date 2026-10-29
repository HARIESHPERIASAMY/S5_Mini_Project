import React from 'react';
import { Flame, FileCode2, ShieldAlert, X } from 'lucide-react';

export default function RiskHeatmap({ fileRisks = [], selectedFile, onSelectFile }) {
  // Sort files descending by risk_score
  const sortedFiles = [...fileRisks].sort((a, b) => (b.risk_score || 0) - (a.risk_score || 0));

  const getRiskStyle = (score) => {
    if (score >= 70) {
      return {
        bg: "bg-[#FEECEC]",
        border: "border-[#FECDCA]",
        text: "text-[#B42318]",
        badge: "bg-[#FEECEC] text-[#B42318] border-[#FECDCA]",
        tag: "CRITICAL"
      };
    }
    if (score >= 45) {
      return {
        bg: "bg-[#FFF4E0]",
        border: "border-[#FEDF89]",
        text: "text-[#9A5B00]",
        badge: "bg-[#FFF4E0] text-[#9A5B00] border-[#FEDF89]",
        tag: "HIGH"
      };
    }
    if (score >= 25) {
      return {
        bg: "bg-[#FEFCE8]",
        border: "border-[#FEF08A]",
        text: "text-[#854D0E]",
        badge: "bg-[#FEFCE8] text-[#854D0E] border-[#FEF08A]",
        tag: "MEDIUM"
      };
    }
    return {
      bg: "bg-[#E7F8EE]",
      border: "border-[#A6F4C5]",
      text: "text-[#14753B]",
      badge: "bg-[#E7F8EE] text-[#14753B] border-[#A6F4C5]",
      tag: "LOW"
    };
  };

  return (
    <div className="card-surface p-4 sm:p-5 bg-white border border-[#E3E8F0] rounded-2xl flex flex-col shadow-xs">
      {/* Title & Legend Bar */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between pb-3 border-b border-[#E3E8F0] mb-4 gap-3">
        <div className="flex items-center gap-2">
          <Flame className="w-4 h-4 text-[#DC2626]" />
          <h3 className="text-xs sm:text-sm font-heading font-bold text-[#0F172A] uppercase tracking-wider font-mono">
            Codebase Risk Density Heatmap
          </h3>
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-[#F1F5F9] text-[#5B6577] font-mono border border-[#E2E8F0]">
            {sortedFiles.length} Modules Monitored
          </span>
        </div>

        {/* Legend */}
        <div className="flex flex-wrap items-center gap-3 text-xs font-mono text-[#5B6577]">
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded bg-[#DC2626]" /> Critical (≥70%)
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded bg-[#D97706]" /> High (45–69%)
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded bg-[#CA8A04]" /> Medium (25–44%)
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded bg-[#16A34A]" /> Low (&lt;25%)
          </span>
        </div>
      </div>

      {/* Filter Active Indicator */}
      {selectedFile && (
        <div className="mb-4 p-2.5 rounded-xl bg-[#EAF1FF] border border-[#B2CCFF] flex items-center justify-between text-xs font-mono">
          <div className="flex items-center gap-2 text-[#1D4ED8]">
            <ShieldAlert className="w-4 h-4 flex-shrink-0" />
            <span>
              Filtering Bug Ledger to: <strong>{selectedFile}</strong>
            </span>
          </div>
          <button
            onClick={() => onSelectFile && onSelectFile(null)}
            className="flex items-center gap-1 px-2 py-0.5 rounded-md bg-white border border-[#B2CCFF] text-[#1D4ED8] hover:bg-[#F8FAFC] font-semibold text-[11px]"
          >
            <X className="w-3 h-3" />
            <span>Clear Filter</span>
          </button>
        </div>
      )}

      {/* Grid of File Tiles */}
      {sortedFiles.length === 0 ? (
        <div className="flex flex-col items-center justify-center p-8 text-[#8E9BAE] text-xs font-mono text-center">
          <FileCode2 className="w-8 h-8 text-[#CBD5E1] mb-2" />
          <span>No static risk models loaded yet. Launch analysis to build heatmap.</span>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
          {sortedFiles.map((file, idx) => {
            const risk = getRiskStyle(file.risk_score);
            const isSelected = selectedFile === file.file_path;

            return (
              <div
                key={idx}
                onClick={() => onSelectFile && onSelectFile(isSelected ? null : file.file_path)}
                className={`p-3.5 rounded-xl border ${risk.border} ${risk.bg} cursor-pointer transition-all duration-200 hover:-translate-y-0.5 hover:shadow-xs ${
                  isSelected ? "ring-2 ring-[#2563EB] shadow-sm" : ""
                }`}
                title="Click to filter bug ledger to this file"
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-2 min-w-0">
                    <FileCode2 className={`w-4 h-4 ${risk.text} flex-shrink-0`} />
                    <span className="text-xs font-mono font-bold text-[#0F172A] truncate">
                      {file.file_path}
                    </span>
                  </div>
                  <span className={`text-[10px] font-mono font-bold px-1.5 py-0.5 rounded border ${risk.badge}`}>
                    {file.risk_score}%
                  </span>
                </div>

                {/* Metrics Badges */}
                <div className="mt-3 grid grid-cols-3 gap-1.5 text-center text-[10px] font-mono">
                  <div className="p-1.5 rounded-lg bg-white/80 border border-[#E3E8F0]">
                    <span className="text-[#5B6577] block text-[9px]">LOC</span>
                    <span className="font-bold text-[#0F172A]">{file.loc}</span>
                  </div>
                  <div className="p-1.5 rounded-lg bg-white/80 border border-[#E3E8F0]">
                    <span className="text-[#5B6577] block text-[9px]">Complexity</span>
                    <span className="font-bold text-[#2563EB]">{file.cyclomatic_complexity}</span>
                  </div>
                  <div className="p-1.5 rounded-lg bg-white/80 border border-[#E3E8F0]">
                    <span className="text-[#5B6577] block text-[9px]">Smells</span>
                    <span className={`font-bold ${file.security_smells > 0 ? "text-[#DC2626]" : "text-[#16A34A]"}`}>
                      {file.security_smells}
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
