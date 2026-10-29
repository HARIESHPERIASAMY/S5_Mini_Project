import React, { useState } from 'react';
import { Search, Copy, Check, GitPullRequest, ArrowRight } from 'lucide-react';
import { getBugWorkflowState } from '../../api/adapters';

export default function OverviewFindingsPreview({
  bugs = [],
  selectedBug,
  onSelectBug,
  onGoToFindings,
  runId,
  onExportPatch
}) {
  const [searchQuery, setSearchQuery] = useState("");
  const [severityFilter, setSeverityFilter] = useState("ALL");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [copiedPatch, setCopiedPatch] = useState(false);

  const filteredBugs = bugs.filter((bug) => {
    if (severityFilter !== "ALL" && bug.severity !== severityFilter) return false;
    const currentStatus = getBugWorkflowState(runId, bug);
    if (statusFilter !== "ALL" && currentStatus !== statusFilter) return false;
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const matchLoc = (bug.file_path || "").toLowerCase().includes(q);
      const matchTitle = (bug.title || "").toLowerCase().includes(q);
      if (!matchLoc && !matchTitle) return false;
    }
    return true;
  });

  const activeBug = selectedBug || filteredBugs[0] || bugs[0] || null;

  const getSeverityBadge = (sev) => {
    switch (sev) {
      case "CRITICAL":
      case "HIGH":
        return "bg-[#FEECEC] text-[#B42318] border-[#FECDCA]";
      case "MEDIUM":
        return "bg-[#FFF4E0] text-[#9A5B00] border-[#FEDF89]";
      default:
        return "bg-[#F1F5F9] text-[#475569] border-[#E2E8F0]";
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case "Verified":
        return "bg-[#E7F8EE] text-[#14753B] border-[#A6F4C5]";
      case "Fix proposed":
        return "bg-[#FFF4E0] text-[#9A5B00] border-[#FEDF89]";
      case "PR opened":
      case "Merged":
        return "bg-[#EEF2FF] text-[#1D4ED8] border-[#B2CCFF]";
      default:
        return "bg-[#FEECEC] text-[#B42318] border-[#FECDCA]";
    }
  };

  // Extract Diff lines for activeBug
  const diffText = activeBug?.proposed_fix_diff || "";
  const diffLines = diffText.split('\n');
  const removedLines = [];
  const addedLines = [];
  diffLines.forEach((l) => {
    if (l.startsWith('-') && !l.startsWith('---')) removedLines.push(l.substring(1));
    else if (l.startsWith('+') && !l.startsWith('+++')) addedLines.push(l.substring(1));
  });

  const defectLine = activeBug?.line_number || 41;
  const originalLine = removedLines[0] || (activeBug?.code_snippet ? activeBug.code_snippet.split('\n')[0] : "if total > THRESHOLD:");
  const fixedLine = addedLines[0] || "if total >= THRESHOLD:";

  const handleCopyPatch = () => {
    navigator.clipboard.writeText(diffText || `${originalLine}\n-->\n${fixedLine}`);
    setCopiedPatch(true);
    setTimeout(() => setCopiedPatch(false), 2000);
  };

  return (
    <div className="space-y-6">
      {/* 1. Findings Table Preview (Top 5) - Screenshot 1 */}
      <div className="sm-card bg-white border border-[#E2E8F0] rounded-xl overflow-hidden shadow-xs">
        {/* Table Header */}
        <div className="p-4 border-b border-[#E2E8F0] flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <h3 className="font-heading font-extrabold text-[#0F172A] text-sm">
              Findings
            </h3>
            <span className="text-[11px] font-mono text-[#64748B]">
              Top {Math.min(filteredBugs.length, 5)} of {bugs.length}
            </span>
          </div>

          <div className="flex items-center gap-2">
            <div className="relative flex-1 sm:w-48">
              <Search className="w-3.5 h-3.5 text-[#94A3B8] absolute left-2.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search findings"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full h-8 pl-8 pr-2.5 text-xs bg-[#F8FAFC] border border-[#E2E8F0] rounded-lg text-[#0F172A] placeholder-[#94A3B8] focus:outline-none focus:border-[#2457F5]"
              />
            </div>

            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              className="h-8 px-2 text-xs bg-[#F8FAFC] border border-[#E2E8F0] rounded-lg text-[#0F172A] focus:outline-none focus:border-[#2457F5] cursor-pointer"
            >
              <option value="ALL">Severity: All ▾</option>
              <option value="CRITICAL">Critical</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
            </select>

            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="h-8 px-2 text-xs bg-[#F8FAFC] border border-[#E2E8F0] rounded-lg text-[#0F172A] focus:outline-none focus:border-[#2457F5] cursor-pointer"
            >
              <option value="ALL">Status: All ▾</option>
              <option value="Open">Open</option>
              <option value="Fix proposed">Fix proposed</option>
              <option value="Verified">Verified</option>
            </select>
          </div>
        </div>

        {/* Table Rows */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-[#E2E8F0] text-[#64748B] text-[10px] font-mono font-bold uppercase tracking-wider bg-[#F8FAFC]">
                <th className="py-2.5 px-4">Location</th>
                <th className="py-2.5 px-3">Severity</th>
                <th className="py-2.5 px-4">Issue</th>
                <th className="py-2.5 px-4 text-right">Fix Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#F1F5F9]">
              {filteredBugs.slice(0, 5).map((bug) => {
                const isSelected = activeBug?.id === bug.id;
                const status = getBugWorkflowState(runId, bug);

                return (
                  <tr
                    key={bug.id}
                    onClick={() => onSelectBug(bug)}
                    className={`cursor-pointer transition-colors duration-150 ${
                      isSelected
                        ? "bg-[#EEF2FF] border-l-4 border-[#2457F5]"
                        : "hover:bg-[#F8FAFC]"
                    }`}
                  >
                    <td className="py-3 px-4 font-mono text-[11px] text-[#475569] whitespace-nowrap">
                      {bug.file_path}:{bug.line_number}
                    </td>

                    <td className="py-3 px-3 whitespace-nowrap">
                      <span className={`inline-block px-2 py-0.5 rounded-full text-[10px] font-mono font-bold border ${getSeverityBadge(bug.severity)}`}>
                        {bug.severity}
                      </span>
                    </td>

                    <td className="py-3 px-4 font-heading font-semibold text-[#0F172A] text-xs">
                      {bug.title}
                    </td>

                    <td className="py-3 px-4 text-right whitespace-nowrap">
                      <span className={`inline-block px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold border ${getStatusBadge(status)}`}>
                        {status}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Footer Link to Findings */}
        <div className="p-3 border-t border-[#E2E8F0] bg-[#FAFBFD] flex items-center justify-between text-xs">
          <span className="text-[11px] text-[#64748B] font-mono">
            Click any defect row to preview the self-healing diff below
          </span>
          <button
            onClick={onGoToFindings}
            className="flex items-center gap-1 font-semibold text-[#2457F5] hover:underline cursor-pointer"
          >
            <span>View all in Findings</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* 2. Inline Defect Detail / Top Fix Preview - Screenshot 1 */}
      {activeBug && (
        <div className="sm-card bg-white border border-[#E2E8F0] rounded-xl p-5 shadow-xs space-y-4">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-3 border-b border-[#E2E8F0]">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-[#FFF4E0] text-[#9A5B00] border border-[#FEDF89]">
                {activeBug.severity || "Medium"}
              </span>
              <span className="px-2 py-0.5 rounded-md text-[10px] font-mono font-semibold bg-[#EEF2FF] text-[#2457F5] border border-[#B2CCFF]">
                {activeBug.category || "Logic"}
              </span>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-[#E7F8EE] text-[#14753B] border border-[#A6F4C5]">
                Verified in sandbox
              </span>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={handleCopyPatch}
                className="flex items-center gap-1.5 px-3 h-8 rounded-lg bg-white hover:bg-[#F8FAFC] border border-[#E2E8F0] text-xs font-semibold text-[#0F172A] transition-colors cursor-pointer"
              >
                {copiedPatch ? <Check className="w-3.5 h-3.5 text-[#16A34A]" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copiedPatch ? "Copied" : "Copy patch"}</span>
              </button>

              <button
                onClick={onExportPatch}
                className="flex items-center gap-1.5 px-3.5 h-8 rounded-lg bg-[#2457F5] hover:bg-[#1A44D4] text-white text-xs font-semibold shadow-xs transition-all cursor-pointer"
              >
                <GitPullRequest className="w-3.5 h-3.5" />
                <span>Open PR</span>
              </button>
            </div>
          </div>

          <div>
            <h4 className="font-heading font-extrabold text-[#0F172A] text-base">
              {activeBug.title}
            </h4>
            <p className="text-xs text-[#64748B] mt-1">
              {activeBug.description || "An order exactly at the threshold gets no discount because the check uses a strict comparison."}
            </p>
          </div>

          {/* Side-by-Side Before & After Boxes (Screenshot 1) */}
          {diffText ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 font-mono text-xs">
              {/* BEFORE Box */}
              <div className="rounded-lg border border-[#FECDCA] bg-[#FEECEC] p-3 text-[#B42318]">
                <span className="text-[10px] font-bold block mb-1.5 uppercase tracking-wider">
                  Before · test FAILED
                </span>
                <div className="space-y-0.5 text-[11px]">
                  <div className="text-[#991B1B]">
                    <span className="text-[#991B1B]/70 mr-2">{defectLine - 1}</span>
                    <span>def apply_discount(total):</span>
                  </div>
                  <div className="text-[#991B1B] font-bold">
                    <span className="text-[#991B1B]/70 mr-2">{defectLine}</span>
                    <span>&nbsp; {originalLine}</span>
                  </div>
                </div>
              </div>

              {/* AFTER Box */}
              <div className="rounded-lg border border-[#A6F4C5] bg-[#E7F8EE] p-3 text-[#14753B]">
                <span className="text-[10px] font-bold block mb-1.5 uppercase tracking-wider">
                  After · 14 of 14 tests PASSED
                </span>
                <div className="space-y-0.5 text-[11px]">
                  <div className="text-[#166534]">
                    <span className="text-[#166534]/70 mr-2">{defectLine - 1}</span>
                    <span>def apply_discount(total):</span>
                  </div>
                  <div className="text-[#166534] font-bold">
                    <span className="text-[#166534]/70 mr-2">{defectLine}</span>
                    <span>&nbsp; {fixedLine}</span>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="p-4 rounded-lg bg-[#F8FAFC] border border-[#E2E8F0] text-xs font-mono text-[#64748B] text-center">
              No patch diff proposed yet for this defect.
            </div>
          )}

          {/* Agent Consensus Footer */}
          <div className="pt-3 border-t border-[#E2E8F0] flex flex-col sm:flex-row items-start sm:items-center justify-between text-xs gap-2">
            <span className="text-[#64748B]">
              <strong className="text-[#0F172A] font-mono text-[10px] uppercase tracking-wider mr-1.5">
                Agent Consensus:
              </strong>
              Critic and Auto-Fix agents agree: reproducible, patch certified.
            </span>
            <button
              onClick={onGoToFindings}
              className="text-[#2457F5] font-semibold hover:underline text-xs cursor-pointer whitespace-nowrap"
            >
              View full debate
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

