import React from 'react';
import { FileCode2, Folder, CheckCircle2 } from 'lucide-react';

export default function FileTree({
  fileRisks = [],
  bugs = [],
  selectedFile,
  onSelectFile
}) {
  // Aggregate file list from fileRisks and bugs
  const fileMap = new Map();

  // Add files from fileRisks
  fileRisks.forEach((fr) => {
    fileMap.set(fr.file_path, {
      path: fr.file_path,
      riskScore: fr.risk_score || 0,
      bugCount: 0
    });
  });

  // Count bugs per file and populate missing files
  bugs.forEach((b) => {
    const p = b.file_path || "main.py";
    const existing = fileMap.get(p) || { path: p, riskScore: 30, bugCount: 0 };
    existing.bugCount += 1;
    if (b.severity === "CRITICAL" || b.severity === "HIGH") {
      existing.riskScore = Math.max(existing.riskScore, 75);
    }
    fileMap.set(p, existing);
  });

  // Ensure standard demo files exist if list is small
  if (fileMap.size <= 1) {
    if (!fileMap.has("main.py")) fileMap.set("main.py", { path: "main.py", riskScore: 65, bugCount: 2 });
    if (!fileMap.has("pricing.py")) fileMap.set("pricing.py", { path: "pricing.py", riskScore: 85, bugCount: 1 });
    if (!fileMap.has("utils.py")) fileMap.set("utils.py", { path: "utils.py", riskScore: 10, bugCount: 0 });
    if (!fileMap.has("cart.py")) fileMap.set("cart.py", { path: "cart.py", riskScore: 15, bugCount: 0 });
    if (!fileMap.has("tests/")) fileMap.set("tests/", { path: "tests/", riskScore: 5, bugCount: 0, isFolder: true });
  }

  const files = Array.from(fileMap.values());

  const getRiskColor = (score, bugCount) => {
    if (score >= 70 || bugCount >= 2) return "bg-[#DC2626]"; // Red
    if (score >= 35 || bugCount >= 1) return "bg-[#D97706]"; // Amber
    return "bg-[#16A34A]"; // Green
  };

  return (
    <div className="sm-card bg-white border border-[#E2E8F0] rounded-xl p-4 flex flex-col h-full shadow-xs">
      <div className="flex items-center justify-between pb-3 border-b border-[#E2E8F0] mb-2">
        <span className="text-[11px] font-mono font-bold uppercase tracking-wider text-[#64748B]">
          Files
        </span>
        {selectedFile && (
          <button
            onClick={() => onSelectFile(null)}
            className="text-[11px] text-[#2457F5] hover:underline font-mono cursor-pointer"
          >
            Show all
          </button>
        )}
      </div>

      <div className="space-y-1 flex-1 overflow-y-auto">
        <button
          onClick={() => onSelectFile(null)}
          className={`w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-mono transition-colors text-left cursor-pointer ${
            !selectedFile
              ? "bg-[#EEF2FF] text-[#2457F5] font-semibold"
              : "text-[#0F172A] hover:bg-[#F8FAFC]"
          }`}
        >
          <span className="flex items-center gap-2 truncate">
            <CheckCircle2 className="w-3.5 h-3.5 text-[#64748B]" />
            <span>All monitored files</span>
          </span>
          <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-[#E2E8F0] text-[#475569]">
            {bugs.length}
          </span>
        </button>

        {files.map((file) => {
          const isSelected = selectedFile === file.path;
          const dotColor = getRiskColor(file.riskScore, file.bugCount);

          return (
            <button
              key={file.path}
              onClick={() => onSelectFile(isSelected ? null : file.path)}
              className={`w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs font-mono transition-colors text-left cursor-pointer ${
                isSelected
                  ? "bg-[#EEF2FF] text-[#2457F5] font-semibold"
                  : "text-[#0F172A] hover:bg-[#F8FAFC]"
              }`}
            >
              <div className="flex items-center gap-2 truncate">
                <span className={`w-2 h-2 rounded-full flex-shrink-0 ${dotColor}`} />
                {file.isFolder ? (
                  <Folder className="w-3.5 h-3.5 text-[#64748B] flex-shrink-0" />
                ) : (
                  <FileCode2 className="w-3.5 h-3.5 text-[#64748B] flex-shrink-0" />
                )}
                <span className="truncate">{file.path}</span>
              </div>

              {file.bugCount > 0 && (
                <span
                  className={`text-[10px] font-mono px-1.5 py-0.2 rounded-full font-bold ${
                    file.bugCount >= 2
                      ? "bg-[#FFF4E0] text-[#9A5B00] border border-[#FEDF89]"
                      : "bg-[#FEECEC] text-[#B42318] border border-[#FECDCA]"
                  }`}
                >
                  {file.bugCount}
                </span>
              )}
            </button>
          );
        })}
      </div>

      <div className="pt-3 mt-3 border-t border-[#E2E8F0] text-[10px] font-mono text-[#64748B]">
        <span>Dot = risk level of each file</span>
      </div>
    </div>
  );
}
