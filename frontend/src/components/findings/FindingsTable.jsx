import React, { useState } from 'react';
import { Search, X, Bug, ChevronRight } from 'lucide-react';
import { getBugWorkflowState } from '../../api/adapters';

export default function FindingsTable({
  bugs = [],
  selectedBug,
  onSelectBug,
  runId,
  fileFilter,
  onClearFileFilter,
  onUpdateWorkflowState,
  onSelectFile
}) {
  const [searchQuery, setSearchQuery] = useState("");
  const [severityFilter, setSeverityFilter] = useState("ALL");
  const [statusFilter, setStatusFilter] = useState("ALL");

  const filteredBugs = bugs.filter((bug) => {
    // File filter
    if (fileFilter && bug.file_path !== fileFilter) return false;

    // Severity filter
    if (severityFilter !== "ALL" && bug.severity !== severityFilter) return false;

    // Status filter (from localStorage or adapter derivation)
    const currentStatus = getBugWorkflowState(runId, bug);
    if (statusFilter !== "ALL" && currentStatus !== statusFilter) return false;

    // Search query
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const matchLoc = (bug.file_path || "").toLowerCase().includes(q);
      const matchTitle = (bug.title || "").toLowerCase().includes(q);
      const matchDesc = (bug.description || "").toLowerCase().includes(q);
      const matchCat = (bug.category || "").toLowerCase().includes(q);
      if (!matchLoc && !matchTitle && !matchDesc && !matchCat) return false;
    }

    return true;
  });

  const getSeverityBadge = (sev) => {
    switch (sev) {
      case "CRITICAL":
        return "bg-[#FEECEC] text-[#B42318] border-[#FECDCA]";
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
      case "Dismissed":
        return "bg-[#F1F5F9] text-[#64748B] border-[#E2E8F0]";
      default: // Open
        return "bg-[#FEECEC] text-[#B42318] border-[#FECDCA]";
    }
  };

  const hasActiveFilters = fileFilter || severityFilter !== "ALL" || statusFilter !== "ALL" || searchQuery.trim().length > 0;

  const handleClearAll = () => {
    setSearchQuery("");
    setSeverityFilter("ALL");
    setStatusFilter("ALL");
    if (onClearFileFilter) onClearFileFilter();
  };

  return (
    <div className="sm-card bg-white border border-[#E2E8F0] rounded-xl flex flex-col h-full shadow-xs">
      {/* Search & Filter Header Bar */}
      <div className="p-4 border-b border-[#E2E8F0] space-y-3">
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-2.5">
          {/* Search Box */}
          <div className="relative flex-1">
            <Search className="w-3.5 h-3.5 text-[#94A3B8] absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search findings"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full h-8 pl-8 pr-3 text-xs bg-[#F8FAFC] border border-[#E2E8F0] rounded-lg text-[#0F172A] placeholder-[#94A3B8] focus:outline-none focus:border-[#2457F5]"
            />
          </div>

          {/* Filter Dropdowns */}
          <div className="flex items-center gap-2">
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              className="h-8 px-2 text-xs bg-[#F8FAFC] border border-[#E2E8F0] rounded-lg text-[#0F172A] focus:outline-none focus:border-[#2457F5] cursor-pointer"
            >
              <option value="ALL">Severity: All ▾</option>
              <option value="CRITICAL">Critical</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
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
              <option value="PR opened">PR opened</option>
              <option value="Merged">Merged</option>
              <option value="Dismissed">Dismissed</option>
            </select>
          </div>
        </div>

        {/* Active Filter Chips */}
        {hasActiveFilters && (
          <div className="flex flex-wrap items-center gap-1.5 pt-1">
            {fileFilter && (
              <span className="inline-flex items-center gap-1 text-[11px] font-mono px-2 py-0.5 rounded-md bg-[#EEF2FF] text-[#2457F5] border border-[#B2CCFF]">
                <span>File: {fileFilter}</span>
                <button onClick={onClearFileFilter} className="hover:text-[#0F172A] cursor-pointer">
                  <X className="w-3 h-3" />
                </button>
              </span>
            )}
            {severityFilter !== "ALL" && (
              <span className="inline-flex items-center gap-1 text-[11px] font-mono px-2 py-0.5 rounded-md bg-[#EEF2FF] text-[#2457F5] border border-[#B2CCFF]">
                <span>Severity: {severityFilter}</span>
                <button onClick={() => setSeverityFilter("ALL")} className="hover:text-[#0F172A] cursor-pointer">
                  <X className="w-3 h-3" />
                </button>
              </span>
            )}
            {statusFilter !== "ALL" && (
              <span className="inline-flex items-center gap-1 text-[11px] font-mono px-2 py-0.5 rounded-md bg-[#EEF2FF] text-[#2457F5] border border-[#B2CCFF]">
                <span>Status: {statusFilter}</span>
                <button onClick={() => setStatusFilter("ALL")} className="hover:text-[#0F172A] cursor-pointer">
                  <X className="w-3 h-3" />
                </button>
              </span>
            )}
            {searchQuery.trim() && (
              <span className="inline-flex items-center gap-1 text-[11px] font-mono px-2 py-0.5 rounded-md bg-[#EEF2FF] text-[#2457F5] border border-[#B2CCFF]">
                <span>&ldquo;{searchQuery}&rdquo;</span>
                <button onClick={() => setSearchQuery("")} className="hover:text-[#0F172A] cursor-pointer">
                  <X className="w-3 h-3" />
                </button>
              </span>
            )}

            <button
              onClick={handleClearAll}
              className="text-[11px] text-[#64748B] hover:text-[#0F172A] hover:underline font-mono ml-1 cursor-pointer"
            >
              Clear all
            </button>
          </div>
        )}
      </div>

      {/* Findings Table List */}
      <div className="flex-1 overflow-y-auto">
        {filteredBugs.length === 0 ? (
          <div className="flex flex-col items-center justify-center p-8 text-[#94A3B8] text-xs font-mono text-center">
            <Bug className="w-8 h-8 text-[#CBD5E1] mb-2" />
            <span>No defects match the selected filters.</span>
          </div>
        ) : (
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-[#E2E8F0] text-[#64748B] text-[10px] font-mono font-bold uppercase tracking-wider bg-[#F8FAFC]">
                <th className="py-2.5 px-4">Issue</th>
                <th className="py-2.5 px-3">Severity</th>
                <th className="py-2.5 px-3 text-right sm:text-left">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#F1F5F9]">
              {filteredBugs.map((bug) => {
                const isSelected = selectedBug?.id === bug.id;
                const status = getBugWorkflowState(runId, bug);

                return (
                  <tr
                    key={bug.id}
                    onClick={() => onSelectBug(bug)}
                    tabIndex={0}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" || e.key === " ") {
                        e.preventDefault();
                        onSelectBug(bug);
                      }
                    }}
                    className={`cursor-pointer transition-colors duration-150 ${
                      isSelected
                        ? "bg-[#EEF2FF] border-l-4 border-[#2457F5]"
                        : "hover:bg-[#F8FAFC]"
                    }`}
                  >
                    <td className="py-3 px-4">
                      <div className="font-heading font-bold text-[#0F172A] text-xs">
                        {bug.title}
                      </div>
                      <div className="text-[11px] text-[#64748B] font-mono mt-0.5">
                        {bug.file_path}:{bug.line_number}
                      </div>
                    </td>

                    <td className="py-3 px-3 whitespace-nowrap">
                      <span className={`inline-block px-2 py-0.5 rounded-full text-[10px] font-mono font-bold border ${getSeverityBadge(bug.severity)}`}>
                        {bug.severity}
                      </span>
                    </td>

                    <td className="py-3 px-3 whitespace-nowrap text-right sm:text-left" onClick={(e) => e.stopPropagation()}>
                      <select
                        value={status}
                        onChange={(e) => onUpdateWorkflowState(bug.id, e.target.value)}
                        className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded-full border cursor-pointer focus:outline-none ${getStatusBadge(status)}`}
                      >
                        <option value="Open">Open</option>
                        <option value="Fix proposed">Fix proposed</option>
                        <option value="Verified">Verified</option>
                        <option value="PR opened">PR opened</option>
                        <option value="Merged">Merged</option>
                        <option value="Dismissed">Dismissed</option>
                      </select>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      {/* Workflow Legend Footer */}
      <div className="p-3 border-t border-[#E2E8F0] text-[10px] font-mono text-[#64748B] bg-[#FAFBFD] rounded-b-xl flex items-center justify-between">
        <span>Workflow: Open → Fix proposed → Verified → PR opened → Merged</span>
        <span className="font-bold text-[#0F172A]">{filteredBugs.length} of {bugs.length}</span>
      </div>
    </div>
  );
}
