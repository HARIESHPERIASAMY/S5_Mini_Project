import React, { useState } from 'react';
import { Bug, CheckCircle2, Search, ChevronRight, X } from 'lucide-react';

export default function BugExplorer({
  bugs = [],
  selectedBug,
  onSelectBug,
  fileFilter,
  onClearFileFilter
}) {
  const [filterSeverity, setFilterSeverity] = useState("ALL");
  const [filterCategory, setFilterCategory] = useState("ALL");
  const [searchQuery, setSearchQuery] = useState("");

  const filteredBugs = bugs.filter((b) => {
    // Heatmap file filter
    if (fileFilter && b.file_path !== fileFilter) return false;
    // Severity filter
    if (filterSeverity !== "ALL" && b.severity !== filterSeverity) return false;
    // Category filter
    if (filterCategory !== "ALL" && b.category !== filterCategory) return false;
    // Search query across fields
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const matchLoc = (b.file_path || "").toLowerCase().includes(q);
      const matchTitle = (b.title || "").toLowerCase().includes(q);
      const matchDesc = (b.description || "").toLowerCase().includes(q);
      const matchCat = (b.category || "").toLowerCase().includes(q);
      if (!matchLoc && !matchTitle && !matchDesc && !matchCat) return false;
    }
    return true;
  });

  const getSeverityBadge = (sev) => {
    switch (sev) {
      case "CRITICAL":
        return "bg-[#FEECEC] text-[#B42318] border-[#FECDCA]";
      case "HIGH":
        return "bg-[#FFF4E0] text-[#9A5B00] border-[#FEDF89]";
      case "MEDIUM":
        return "bg-[#FEFCE8] text-[#854D0E] border-[#FEF08A]";
      default:
        return "bg-[#F1F5F9] text-[#5B6577] border-[#E2E8F0]";
    }
  };

  return (
    <div className="card-surface p-4 sm:p-5 bg-white border border-[#E3E8F0] rounded-2xl flex flex-col shadow-xs">
      {/* Table Header & Controls */}
      <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between pb-4 border-b border-[#E3E8F0] gap-3">
        <div className="flex items-center gap-2">
          <Bug className="w-4 h-4 text-[#DC2626]" />
          <h3 className="text-xs sm:text-sm font-heading font-bold text-[#0F172A] tracking-wider uppercase font-mono">
            Bug Classification & Self-Healing Ledger
          </h3>
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-[#F1F5F9] text-[#5B6577] font-mono border border-[#E2E8F0]">
            {filteredBugs.length} of {bugs.length} Defects
          </span>
          {fileFilter && (
            <span className="flex items-center gap-1 text-[11px] px-2 py-0.5 rounded-md bg-[#EAF1FF] text-[#1D4ED8] font-mono border border-[#B2CCFF]">
              <span>File: {fileFilter}</span>
              <button onClick={onClearFileFilter} className="hover:text-[#0F172A] cursor-pointer">
                <X className="w-3 h-3" />
              </button>
            </span>
          )}
        </div>

        {/* Filters and Search Box */}
        <div className="flex flex-wrap items-center gap-2 w-full lg:w-auto">
          {/* Search Box */}
          <div className="relative flex-1 sm:w-60">
            <Search className="w-3.5 h-3.5 text-[#8E9BAE] absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search defects, files..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full h-9 pl-8 pr-3 text-xs font-mono bg-[#F8FAFC] border border-[#E3E8F0] rounded-lg text-[#0F172A] placeholder-[#8E9BAE] focus:outline-none focus:border-[#2563EB]"
            />
          </div>

          {/* Severity Dropdown */}
          <select
            value={filterSeverity}
            onChange={(e) => setFilterSeverity(e.target.value)}
            className="h-9 px-2.5 text-xs font-mono bg-[#F8FAFC] border border-[#E3E8F0] rounded-lg text-[#0F172A] focus:outline-none focus:border-[#2563EB]"
          >
            <option value="ALL">All Severities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>

          {/* Category Dropdown */}
          <select
            value={filterCategory}
            onChange={(e) => setFilterCategory(e.target.value)}
            className="h-9 px-2.5 text-xs font-mono bg-[#F8FAFC] border border-[#E3E8F0] rounded-lg text-[#0F172A] focus:outline-none focus:border-[#2563EB]"
          >
            <option value="ALL">All Categories</option>
            <option value="LOGIC">Logic</option>
            <option value="SECURITY">Security</option>
            <option value="INPUT_VALIDATION">Input Validation</option>
            <option value="CONCURRENCY">Concurrency</option>
          </select>
        </div>
      </div>

      {/* Bugs Table */}
      {filteredBugs.length === 0 ? (
        <div className="flex flex-col items-center justify-center p-8 text-[#8E9BAE] text-xs font-mono text-center">
          <Bug className="w-8 h-8 text-[#CBD5E1] mb-2" />
          <span>No defects match the selected filters.</span>
        </div>
      ) : (
        <div className="overflow-x-auto mt-2">
          <table className="w-full text-left text-xs font-mono border-collapse">
            <thead>
              <tr className="border-b border-[#E3E8F0] text-[#5B6577]">
                <th className="py-2.5 px-3 font-bold text-[10px] uppercase tracking-wider">Location</th>
                <th className="py-2.5 px-3 font-bold text-[10px] uppercase tracking-wider">Severity</th>
                <th className="py-2.5 px-3 font-bold text-[10px] uppercase tracking-wider">Category</th>
                <th className="py-2.5 px-3 font-bold text-[10px] uppercase tracking-wider">Defect</th>
                <th className="py-2.5 px-3 font-bold text-[10px] uppercase tracking-wider">Self-Healing Fix</th>
                <th className="py-2.5 px-3 font-bold text-[10px] uppercase tracking-wider text-right">Inspect</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#F1F5F9]">
              {filteredBugs.map((bug, idx) => {
                const isSelected = selectedBug?.id === bug.id;
                const isVerified = bug.fix_verified;

                return (
                  <tr
                    key={idx}
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
                        ? "bg-[#EAF1FF] border-l-4 border-[#2563EB]"
                        : "hover:bg-[#F8FAFC]"
                    }`}
                  >
                    <td className="py-3 px-3 font-bold text-[#2563EB] whitespace-nowrap">
                      {bug.file_path}:{bug.line_number}
                    </td>
                    <td className="py-3 px-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${getSeverityBadge(bug.severity)}`}>
                        {bug.severity}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-[#5B6577] font-semibold">
                      {bug.category}
                    </td>
                    <td className="py-3 px-3 text-[#0F172A] font-medium truncate max-w-sm">
                      {bug.title}
                    </td>
                    <td className="py-3 px-3 whitespace-nowrap">
                      {isVerified ? (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-[#E7F8EE] border border-[#A6F4C5] text-[#14753B] text-[10px] font-bold">
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          VERIFIED FIX
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-[#F1F5F9] border border-[#E2E8F0] text-[#5B6577] text-[10px]">
                          PROPOSED DIFF
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-3 text-right">
                      <button
                        className={`p-1 rounded-md transition-colors ${
                          isSelected ? "text-[#2563EB] bg-white shadow-xs" : "text-[#8E9BAE] hover:text-[#0F172A]"
                        }`}
                        aria-label={`Inspect defect at ${bug.file_path}`}
                      >
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
    </div>
  );
}
