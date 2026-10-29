import React, { useState, useEffect } from 'react';
import { 
  GitCompare, X, CheckCircle2, AlertCircle, 
  ArrowRight, ShieldCheck, RefreshCw, Plus, Minus, Equal
} from 'lucide-react';

const API_BASE = "http://localhost:8000";

export default function CompareRunsModal({
  isOpen,
  onClose,
  initialBaseRunId,
  initialCompareRunId,
  availableRuns = []
}) {
  const [baseRunId, setBaseRunId] = useState(initialBaseRunId || availableRuns[1]?.id || availableRuns[0]?.id || "");
  const [compareRunId, setCompareRunId] = useState(initialCompareRunId || availableRuns[0]?.id || "");

  const [baseData, setBaseData] = useState(null);
  const [compareData, setCompareData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!isOpen) return;

    const fetchRunDetails = async () => {
      if (!baseRunId || !compareRunId) return;
      try {
        setLoading(true);
        setError(null);
        const [resBase, resCompare] = await Promise.all([
          fetch(`${API_BASE}/api/runs/${baseRunId}`),
          fetch(`${API_BASE}/api/runs/${compareRunId}`)
        ]);

        if (!resBase.ok || !resCompare.ok) throw new Error("Failed to fetch run details for comparison");

        const dataBase = await resBase.json();
        const dataCompare = await resCompare.json();

        setBaseData(dataBase);
        setCompareData(dataCompare);
      } catch (err) {
        setError(err.message || "Failed to compare runs");
      } finally {
        setLoading(false);
      }
    };

    fetchRunDetails();
  }, [isOpen, baseRunId, compareRunId]);

  if (!isOpen) return null;

  // Comparison Logic: Match bugs by file_path + category + normalized title
  const normalize = (str) => (str || "").toLowerCase().replace(/[^a-z0-9]/g, '');

  const bugsA = baseData?.bugs || [];
  const bugsB = compareData?.bugs || [];

  const getKey = (b) => `${b.file_path}::${b.category}::${normalize(b.title)}`;

  const mapA = new Map(bugsA.map(b => [getKey(b), b]));
  const mapB = new Map(bugsB.map(b => [getKey(b), b]));

  const fixedBugs = [];    // In A, absent in B
  const unchangedBugs = [];// In both A and B
  const newBugs = [];      // In B, absent in A

  bugsA.forEach((bA) => {
    const k = getKey(bA);
    if (mapB.has(k)) {
      unchangedBugs.push({ base: bA, current: mapB.get(k) });
    } else {
      fixedBugs.push(bA);
    }
  });

  bugsB.forEach((bB) => {
    const k = getKey(bB);
    if (!mapA.has(k)) {
      newBugs.push(bB);
    }
  });

  const scoreA = baseData?.suite_health_score ?? 0;
  const scoreB = compareData?.suite_health_score ?? 0;
  const scoreDelta = Math.round((scoreB - scoreA) * 10) / 10;

  return (
    <div className="fixed inset-0 z-50 bg-[#0F172A]/40 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white border border-[#E2E8F0] rounded-2xl shadow-xl w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden">
        {/* Header */}
        <div className="p-5 border-b border-[#E2E8F0] flex items-center justify-between bg-white">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-[#EEF2FF] text-[#2457F5] flex items-center justify-center border border-[#2457F5]/20">
              <GitCompare className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-heading font-extrabold text-[#0F172A] text-base">
                Cross-Run Differential Comparison
              </h3>
              <p className="text-[11px] text-[#64748B]">
                Bugs matched by file path + issue category + normalized title
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-[#64748B] hover:text-[#0F172A] p-1 rounded-md hover:bg-[#F8FAFC] cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Run Selector Bar */}
        <div className="p-4 bg-[#F8FAFC] border-b border-[#E2E8F0] flex flex-col sm:flex-row items-center justify-between gap-4 text-xs">
          <div className="flex items-center gap-2 w-full sm:w-auto">
            <span className="font-bold text-[#64748B]">Baseline (Run A):</span>
            <select
              value={baseRunId}
              onChange={(e) => setBaseRunId(e.target.value)}
              className="h-8 px-2 bg-white border border-[#E2E8F0] rounded-lg font-mono focus:outline-none"
            >
              {availableRuns.map((r) => (
                <option key={r.id} value={r.id}>
                  #{r.id.slice(0, 8)} (Score: {r.suite_health_score})
                </option>
              ))}
            </select>
          </div>

          <ArrowRight className="w-4 h-4 text-[#94A3B8] hidden sm:block" />

          <div className="flex items-center gap-2 w-full sm:w-auto">
            <span className="font-bold text-[#64748B]">Compare (Run B):</span>
            <select
              value={compareRunId}
              onChange={(e) => setCompareRunId(e.target.value)}
              className="h-8 px-2 bg-white border border-[#E2E8F0] rounded-lg font-mono focus:outline-none"
            >
              {availableRuns.map((r) => (
                <option key={r.id} value={r.id}>
                  #{r.id.slice(0, 8)} (Score: {r.suite_health_score})
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Content Body */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1">
          {loading ? (
            <div className="p-12 text-center text-xs font-mono text-[#64748B]">
              <RefreshCw className="w-6 h-6 animate-spin mx-auto text-[#2457F5] mb-2" />
              <span>Comparing AST topologies and bug ledgers...</span>
            </div>
          ) : error ? (
            <div className="p-4 rounded-xl bg-[#FEECEC] border border-[#FECDCA] text-[#B42318] text-xs">
              {error}
            </div>
          ) : (
            <>
              {/* Score Delta Strip */}
              <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
                <div className="p-3 bg-white border border-[#E2E8F0] rounded-xl">
                  <span className="text-[10px] font-mono text-[#64748B] uppercase block">Health Delta</span>
                  <strong className={`text-xl font-heading font-extrabold block mt-0.5 ${scoreDelta >= 0 ? 'text-[#16A34A]' : 'text-[#DC2626]'}`}>
                    {scoreDelta >= 0 ? `+${scoreDelta}` : scoreDelta} pts
                  </strong>
                  <span className="text-[10px] text-[#64748B]">{scoreA} → {scoreB}</span>
                </div>

                <div className="p-3 bg-white border border-[#E2E8F0] rounded-xl">
                  <span className="text-[10px] font-mono text-[#64748B] uppercase block">Fixed Defects</span>
                  <strong className="text-xl font-heading font-extrabold text-[#16A34A] block mt-0.5">
                    {fixedBugs.length}
                  </strong>
                  <span className="text-[10px] text-[#64748B]">Resolved in Run B</span>
                </div>

                <div className="p-3 bg-white border border-[#E2E8F0] rounded-xl">
                  <span className="text-[10px] font-mono text-[#64748B] uppercase block">New Regressions</span>
                  <strong className="text-xl font-heading font-extrabold text-[#DC2626] block mt-0.5">
                    {newBugs.length}
                  </strong>
                  <span className="text-[10px] text-[#64748B]">Introduced in Run B</span>
                </div>

                <div className="p-3 bg-white border border-[#E2E8F0] rounded-xl">
                  <span className="text-[10px] font-mono text-[#64748B] uppercase block">Unchanged</span>
                  <strong className="text-xl font-heading font-extrabold text-[#0F172A] block mt-0.5">
                    {unchangedBugs.length}
                  </strong>
                  <span className="text-[10px] text-[#64748B]">Persistent in both</span>
                </div>
              </div>

              {/* Fixed Bugs List */}
              {fixedBugs.length > 0 && (
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-xs font-bold text-[#16A34A] uppercase tracking-wider font-mono">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Fixed Defects ({fixedBugs.length})</span>
                  </div>
                  <div className="space-y-1.5">
                    {fixedBugs.map((b, i) => (
                      <div key={i} className="p-2.5 rounded-lg border border-[#A6F4C5] bg-[#E7F8EE] flex items-center justify-between text-xs">
                        <div>
                          <strong className="text-[#0F172A]">{b.title}</strong>
                          <span className="text-[11px] font-mono text-[#166534] block">{b.file_path}:{b.line_number}</span>
                        </div>
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-white text-[#16A34A] border border-[#A6F4C5] font-bold">
                          Fixed in #{compareRunId.slice(0, 6)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* New Regressions List */}
              {newBugs.length > 0 && (
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-xs font-bold text-[#DC2626] uppercase tracking-wider font-mono">
                    <AlertCircle className="w-4 h-4" />
                    <span>New Regressions ({newBugs.length})</span>
                  </div>
                  <div className="space-y-1.5">
                    {newBugs.map((b, i) => (
                      <div key={i} className="p-2.5 rounded-lg border border-[#FECDCA] bg-[#FEECEC] flex items-center justify-between text-xs">
                        <div>
                          <strong className="text-[#0F172A]">{b.title}</strong>
                          <span className="text-[11px] font-mono text-[#991B1B] block">{b.file_path}:{b.line_number}</span>
                        </div>
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-white text-[#DC2626] border border-[#FECDCA] font-bold">
                          New in #{compareRunId.slice(0, 6)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Unchanged Bugs List */}
              {unchangedBugs.length > 0 && (
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-xs font-bold text-[#64748B] uppercase tracking-wider font-mono">
                    <Equal className="w-4 h-4" />
                    <span>Persistent Findings ({unchangedBugs.length})</span>
                  </div>
                  <div className="space-y-1.5">
                    {unchangedBugs.map(({ current }, i) => (
                      <div key={i} className="p-2.5 rounded-lg border border-[#E2E8F0] bg-[#FAFBFD] flex items-center justify-between text-xs">
                        <div>
                          <strong className="text-[#0F172A]">{current.title}</strong>
                          <span className="text-[11px] font-mono text-[#64748B] block">{current.file_path}:{current.line_number}</span>
                        </div>
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-white text-[#64748B] border border-[#E2E8F0]">
                          Open
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-[#E2E8F0] bg-[#FAFBFD] flex items-center justify-between text-xs font-mono">
          <span className="text-[#64748B]">Matching algorithm: Path + Category + Normalized title</span>
          <button
            onClick={onClose}
            className="px-4 h-8 rounded-lg bg-[#2457F5] text-white font-semibold cursor-pointer"
          >
            Close Comparison
          </button>
        </div>
      </div>
    </div>
  );
}

