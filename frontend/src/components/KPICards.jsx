import React from 'react';
import { Bug, CheckCircle2, ShieldCheck, Dna, Activity, AlertTriangle } from 'lucide-react';

export default function KPICards({ runData }) {
  const bugsCount = runData?.bugs_count ?? 0;
  const verifiedFixes = runData?.fixes_verified_count ?? 0;
  const coverage = runData?.code_coverage ?? 0;
  const mutationScore = runData?.mutation_score ?? 0;
  const healthScore = runData?.suite_health_score ?? 0;
  const riskScore = runData?.risk_score ?? 0;

  const fixRate = bugsCount > 0 ? Math.round((verifiedFixes / bugsCount) * 100) : 100;

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3.5">
      {/* 1. Bugs Detected */}
      <div className="glass-panel rounded-xl p-4 relative overflow-hidden border border-slate-800 hover:border-rose-500/40 transition-all duration-200">
        <div className="flex items-center justify-between">
          <span className="text-xs font-mono text-slate-400">BUGS FOUND</span>
          <div className="w-7 h-7 rounded-lg bg-rose-950/60 border border-rose-800/60 flex items-center justify-center text-rose-400">
            <Bug className="w-4 h-4" />
          </div>
        </div>
        <div className="mt-3 flex items-baseline gap-2">
          <span className="text-2xl font-bold font-mono text-white">{bugsCount}</span>
          <span className="text-xs text-rose-400 font-mono">
            {bugsCount > 0 ? "Defects flagged" : "Clean suite"}
          </span>
        </div>
        <div className="mt-2 text-[11px] text-slate-500 font-mono flex items-center gap-1">
          <AlertTriangle className="w-3 h-3 text-amber-400" />
          <span>Code Risk: {riskScore}%</span>
        </div>
        <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-rose-500 to-transparent" />
      </div>

      {/* 2. Verified Fixes (Self-Healing) */}
      <div className="glass-panel rounded-xl p-4 relative overflow-hidden border border-slate-800 hover:border-emerald-500/40 transition-all duration-200">
        <div className="flex items-center justify-between">
          <span className="text-xs font-mono text-slate-400">VERIFIED FIXES</span>
          <div className="w-7 h-7 rounded-lg bg-emerald-950/60 border border-emerald-800/60 flex items-center justify-center text-emerald-400">
            <CheckCircle2 className="w-4 h-4" />
          </div>
        </div>
        <div className="mt-3 flex items-baseline gap-2">
          <span className="text-2xl font-bold font-mono text-white">{verifiedFixes}</span>
          <span className="text-xs text-emerald-400 font-mono">
            {fixRate}% Self-Healed
          </span>
        </div>
        <div className="mt-2 text-[11px] text-slate-400 font-mono">
          Re-tested & verified in sandbox
        </div>
        <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-emerald-500 to-transparent" />
      </div>

      {/* 3. Code Coverage */}
      <div className="glass-panel rounded-xl p-4 relative overflow-hidden border border-slate-800 hover:border-cyan-500/40 transition-all duration-200">
        <div className="flex items-center justify-between">
          <span className="text-xs font-mono text-slate-400">TEST COVERAGE</span>
          <div className="w-7 h-7 rounded-lg bg-cyan-950/60 border border-cyan-800/60 flex items-center justify-center text-cyan-400">
            <ShieldCheck className="w-4 h-4" />
          </div>
        </div>
        <div className="mt-3 flex items-baseline gap-2">
          <span className="text-2xl font-bold font-mono text-white">{coverage}%</span>
          <span className={`text-xs font-mono ${coverage >= 80 ? "text-emerald-400" : "text-amber-400"}`}>
            {coverage >= 80 ? "Optimal" : "Monitored"}
          </span>
        </div>
        {/* Progress Bar */}
        <div className="mt-2.5 w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
          <div
            className="bg-gradient-to-r from-cyan-500 to-blue-500 h-1.5 rounded-full transition-all duration-500"
            style={{ width: `${Math.min(100, coverage)}%` }}
          />
        </div>
        <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-cyan-500 to-transparent" />
      </div>

      {/* 4. Mutation Testing Score */}
      <div className="glass-panel rounded-xl p-4 relative overflow-hidden border border-slate-800 hover:border-violet-500/40 transition-all duration-200">
        <div className="flex items-center justify-between">
          <span className="text-xs font-mono text-slate-400">MUTATION SCORE</span>
          <div className="w-7 h-7 rounded-lg bg-violet-950/60 border border-violet-800/60 flex items-center justify-center text-violet-400">
            <Dna className="w-4 h-4" />
          </div>
        </div>
        <div className="mt-3 flex items-baseline gap-2">
          <span className="text-2xl font-bold font-mono text-white">{mutationScore}%</span>
          <span className="text-xs text-violet-400 font-mono">
            Mutants Killed
          </span>
        </div>
        <div className="mt-2 text-[11px] text-slate-400 font-mono">
          AST Operator Inversion
        </div>
        <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-violet-500 to-transparent" />
      </div>

      {/* 5. Suite Health Score */}
      <div className="glass-panel rounded-xl p-4 relative overflow-hidden border border-slate-800 hover:border-blue-500/40 transition-all duration-200 col-span-2 md:col-span-1">
        <div className="flex items-center justify-between">
          <span className="text-xs font-mono text-slate-400">SUITE HEALTH</span>
          <div className="w-7 h-7 rounded-lg bg-blue-950/60 border border-blue-800/60 flex items-center justify-center text-blue-400">
            <Activity className="w-4 h-4" />
          </div>
        </div>
        <div className="mt-3 flex items-baseline gap-2">
          <span className="text-2xl font-bold font-mono text-white">{healthScore}</span>
          <span className="text-xs text-slate-400 font-mono">/ 100</span>
          <span className={`text-xs font-mono ${healthScore >= 75 ? "text-emerald-400" : "text-amber-400"}`}>
            {healthScore >= 75 ? "Resilient" : "Flaky Risk"}
          </span>
        </div>
        <div className="mt-2 text-[11px] text-slate-400 font-mono">
          Pass Rate + Flake Penalty
        </div>
        <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-blue-500 to-transparent" />
      </div>
    </div>
  );
}
