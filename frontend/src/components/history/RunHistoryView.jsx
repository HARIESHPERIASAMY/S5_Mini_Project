import React, { useState, useEffect } from 'react';
import { 
  History, ArrowRight, GitCompare, RefreshCw, 
  CheckCircle2, AlertTriangle, Shield, Clock, TrendingUp
} from 'lucide-react';

const API_BASE = "http://localhost:8000";

export default function RunHistoryView({
  currentRunId,
  onSelectRun,
  onOpenCompare
}) {
  const [runs, setRuns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchRuns = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API_BASE}/api/runs?limit=25`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setRuns(data.items || []);
      setError(null);
    } catch (err) {
      setError(err.message || "Failed to load runs history");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRuns();
  }, [currentRunId]);

  // Derived trend sparkline coordinates (Only shown if 2 or more real runs)
  const hasMultipleRuns = runs.length >= 2;
  const recentRuns = [...runs].reverse().slice(-5);
  const scores = recentRuns.map((r) => r.suite_health_score || 0);

  let sparklinePoints = "";
  let scoreDelta = 0;
  if (hasMultipleRuns && scores.length >= 2) {
    const min = Math.min(...scores, 0);
    const max = Math.max(...scores, 100);
    const range = max - min || 1;
    sparklinePoints = scores
      .map((s, idx) => {
        const x = 10 + (idx / (scores.length - 1)) * 120;
        const y = 30 - ((s - min) / range) * 24;
        return `${x},${y}`;
      })
      .join(" ");
    scoreDelta = Math.round((scores[scores.length - 1] - scores[0]) * 10) / 10;
  }

  return (
    <div className="space-y-6">
      {/* Header Bar */}
      <div className="sm-card p-5 bg-white border border-[#E2E8F0] rounded-xl shadow-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <History className="w-4 h-4 text-[#2457F5]" />
            <h3 className="font-heading font-extrabold text-[#0F172A] text-lg">
              Historical Run Ledger & Regression Benchmarks
            </h3>
          </div>
          <p className="text-xs text-[#64748B] mt-0.5">
            Audit logs of past swarm analyses, health scores, and verified self-healing repairs.
          </p>
        </div>

        {/* Multi-Run Trend Sparkline (Condition B2: Hidden unless 2 or more real runs) */}
        {hasMultipleRuns ? (
          <div className="flex items-center gap-3 p-2.5 bg-[#FAFBFD] border border-[#E2E8F0] rounded-xl text-xs font-mono">
            <div className="text-right">
              <span className="text-[10px] text-[#64748B] uppercase block">Score Trend ({runs.length} runs)</span>
              <strong className={scoreDelta >= 0 ? "text-[#16A34A]" : "text-[#DC2626]"}>
                {scoreDelta >= 0 ? `+${scoreDelta}` : scoreDelta} pts
              </strong>
            </div>
            <svg className="w-32 h-8" viewBox="0 0 140 32">
              <polyline
                fill="none"
                stroke="#2457F5"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                points={sparklinePoints}
              />
              {scores.map((s, idx) => {
                const x = 10 + (idx / (scores.length - 1)) * 120;
                const y = 30 - ((s - Math.min(...scores, 0)) / (Math.max(...scores, 100) - Math.min(...scores, 0) || 1)) * 24;
                return <circle key={idx} cx={x} cy={y} r="2.5" fill="#2457F5" />;
              })}
            </svg>
          </div>
        ) : (
          <div className="text-[11px] font-mono text-[#64748B] bg-[#F8FAFC] border border-[#E2E8F0] px-3 py-1.5 rounded-lg">
            At least 2 runs needed to calculate historical trend
          </div>
        )}
      </div>

      {/* Runs Table */}
      <div className="sm-card bg-white border border-[#E2E8F0] rounded-xl shadow-xs overflow-hidden">
        <div className="p-4 border-b border-[#E2E8F0] flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="font-heading font-bold text-xs uppercase text-[#64748B] tracking-wider font-mono">
              Executed Runs ({runs.length})
            </span>
          </div>
          <button
            onClick={fetchRuns}
            disabled={loading}
            className="flex items-center gap-1 text-xs text-[#2457F5] font-semibold hover:underline cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
            <span>Refresh</span>
          </button>
        </div>

        {loading ? (
          <div className="p-12 text-center text-xs font-mono text-[#64748B]">
            <RefreshCw className="w-6 h-6 animate-spin mx-auto text-[#2457F5] mb-2" />
            <span>Loading run records from SQLite database...</span>
          </div>
        ) : runs.length === 0 ? (
          <div className="p-12 text-center text-xs font-mono text-[#64748B]">
            No runs recorded yet. Launch a run from the start screen or top bar.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-[#E2E8F0] text-[#64748B] text-[10px] font-mono font-bold uppercase tracking-wider bg-[#F8FAFC]">
                  <th className="py-2.5 px-4">Run ID</th>
                  <th className="py-2.5 px-4">Timestamp</th>
                  <th className="py-2.5 px-4">Suite Health</th>
                  <th className="py-2.5 px-4">Defects</th>
                  <th className="py-2.5 px-4">Fixes Verified</th>
                  <th className="py-2.5 px-4">Status</th>
                  <th className="py-2.5 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#F1F5F9]">
                {runs.map((r) => {
                  const isCurrent = currentRunId === r.id;
                  const dateStr = r.started_at ? new Date(r.started_at).toLocaleString() : "Unknown";

                  return (
                    <tr
                      key={r.id}
                      className={`hover:bg-[#F8FAFC] transition-colors ${
                        isCurrent ? "bg-[#EEF2FF] border-l-4 border-[#2457F5]" : ""
                      }`}
                    >
                      <td className="py-3 px-4 font-mono font-bold text-[#0F172A]">
                        #{r.id.slice(0, 8)}
                        {isCurrent && (
                          <span className="ml-2 text-[9px] font-mono px-1.5 py-0.2 rounded bg-[#2457F5] text-white">
                            Active
                          </span>
                        )}
                      </td>
                      <td className="py-3 px-4 font-mono text-[11px] text-[#64748B]">
                        {dateStr}
                      </td>
                      <td className="py-3 px-4 font-mono font-bold text-[#0F172A]">
                        {r.suite_health_score ?? 0}
                      </td>
                      <td className="py-3 px-4 font-mono text-[#DC2626]">
                        {r.bugs_count ?? 0}
                      </td>
                      <td className="py-3 px-4 font-mono text-[#16A34A]">
                        {r.fixes_verified_count ?? 0}
                      </td>
                      <td className="py-3 px-4">
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-mono font-bold border ${
                          r.status === "completed"
                            ? "bg-[#E7F8EE] text-[#14753B] border-[#A6F4C5]"
                            : r.status === "failed"
                            ? "bg-[#FEECEC] text-[#B42318] border-[#FECDCA]"
                            : "bg-[#FFF4E0] text-[#9A5B00] border-[#FEDF89]"
                        }`}>
                          {r.status}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => onSelectRun(r.id)}
                            className="px-2.5 py-1 rounded-md bg-white border border-[#E2E8F0] hover:bg-[#F8FAFC] text-[11px] font-semibold text-[#0F172A] cursor-pointer"
                          >
                            Inspect
                          </button>
                          <button
                            onClick={() => onOpenCompare(r.id)}
                            className="flex items-center gap-1 px-2.5 py-1 rounded-md bg-[#EEF2FF] text-[#2457F5] hover:bg-[#E0E7FF] text-[11px] font-semibold cursor-pointer"
                          >
                            <GitCompare className="w-3 h-3" />
                            <span>Compare</span>
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
