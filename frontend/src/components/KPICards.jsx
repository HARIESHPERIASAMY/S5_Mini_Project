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
      <div className="card-surface p-4 relative overflow-hidden bg-white border border-[#E3E8F0] rounded-2xl hover:border-[#CBD5E1] transition-all">
        <div className="flex items-center justify-between">
          <span className="text-[11px] font-mono font-bold tracking-wider text-[#5B6577] uppercase">
            Bugs Found
          </span>
          <div className="w-8 h-8 rounded-lg bg-[#FEECEC] border border-[#FECDCA] flex items-center justify-center text-[#B42318]">
            <Bug className="w-4 h-4" />
          </div>
        </div>
        <div className="mt-2.5 flex items-baseline gap-2">
          <span className="text-2xl sm:text-3xl font-heading font-extrabold text-[#0F172A] tracking-tight">
            {bugsCount}
          </span>
          <span className="text-xs font-mono font-semibold text-[#DC2626]">
            {bugsCount > 0 ? "Defects flagged" : "Clean suite"}
          </span>
        </div>
        <div className="mt-2 text-[11px] text-[#5B6577] font-mono flex items-center gap-1.5">
          <AlertTriangle className="w-3.5 h-3.5 text-[#D97706]" />
          <span>Code Risk: <strong className="text-[#0F172A]">{riskScore}%</strong></span>
        </div>
        <div className="absolute top-0 left-0 right-0 h-1 bg-[#DC2626]" />
      </div>

      {/* 2. Verified Fixes (Self-Healing) */}
      <div className="card-surface p-4 relative overflow-hidden bg-white border border-[#E3E8F0] rounded-2xl hover:border-[#CBD5E1] transition-all">
        <div className="flex items-center justify-between">
          <span className="text-[11px] font-mono font-bold tracking-wider text-[#5B6577] uppercase">
            Verified Fixes
          </span>
          <div className="w-8 h-8 rounded-lg bg-[#E7F8EE] border border-[#A6F4C5] flex items-center justify-center text-[#14753B]">
            <CheckCircle2 className="w-4 h-4" />
          </div>
        </div>
        <div className="mt-2.5 flex items-baseline gap-2">
          <span className="text-2xl sm:text-3xl font-heading font-extrabold text-[#0F172A] tracking-tight">
            {verifiedFixes}
          </span>
          <span className="text-xs font-mono font-semibold text-[#16A34A]">
            {fixRate}% Self-Healed
          </span>
        </div>
        <div className="mt-2 text-[11px] text-[#5B6577] font-mono">
          Re-tested & verified in sandbox
        </div>
        <div className="absolute top-0 left-0 right-0 h-1 bg-[#16A34A]" />
      </div>

      {/* 3. Code Coverage */}
      <div className="card-surface p-4 relative overflow-hidden bg-white border border-[#E3E8F0] rounded-2xl hover:border-[#CBD5E1] transition-all">
        <div className="flex items-center justify-between">
          <span className="text-[11px] font-mono font-bold tracking-wider text-[#5B6577] uppercase">
            Test Coverage
          </span>
          <div className="w-8 h-8 rounded-lg bg-[#EAF1FF] border border-[#B2CCFF] flex items-center justify-center text-[#1D4ED8]">
            <ShieldCheck className="w-4 h-4" />
          </div>
        </div>
        <div className="mt-2.5 flex items-baseline gap-2">
          <span className="text-2xl sm:text-3xl font-heading font-extrabold text-[#0F172A] tracking-tight">
            {coverage}%
          </span>
          <span className={`text-xs font-mono font-semibold ${coverage >= 80 ? "text-[#16A34A]" : "text-[#D97706]"}`}>
            {coverage >= 80 ? "Target met (≥80%)" : "Under target"}
          </span>
        </div>
        {/* Progress Bar */}
        <div className="mt-2.5 w-full bg-[#E2E8F0] rounded-full h-1.5 overflow-hidden">
          <div
            className="bg-[#2563EB] h-1.5 rounded-full transition-all duration-500"
            style={{ width: `${Math.min(100, Math.max(0, coverage))}%` }}
          />
        </div>
        <div className="absolute top-0 left-0 right-0 h-1 bg-[#2563EB]" />
      </div>

      {/* 4. Mutation Testing Score */}
      <div className="card-surface p-4 relative overflow-hidden bg-white border border-[#E3E8F0] rounded-2xl hover:border-[#CBD5E1] transition-all">
        <div className="flex items-center justify-between">
          <span className="text-[11px] font-mono font-bold tracking-wider text-[#5B6577] uppercase">
            Mutation Score
          </span>
          <div className="w-8 h-8 rounded-lg bg-[#F1EAFE] border border-[#D9D6FE] flex items-center justify-center text-[#6D28D9]">
            <Dna className="w-4 h-4" />
          </div>
        </div>
        <div className="mt-2.5 flex items-baseline gap-2">
          <span className="text-2xl sm:text-3xl font-heading font-extrabold text-[#0F172A] tracking-tight">
            {mutationScore}%
          </span>
          <span className="text-xs font-mono font-semibold text-[#7C3AED]">
            Mutants Killed
          </span>
        </div>
        <div className="mt-2 text-[11px] text-[#5B6577] font-mono">
          AST Operator Inversions
        </div>
        <div className="absolute top-0 left-0 right-0 h-1 bg-[#7C3AED]" />
      </div>

      {/* 5. Suite Health Score */}
      <div className="card-surface p-4 relative overflow-hidden bg-white border border-[#E3E8F0] rounded-2xl hover:border-[#CBD5E1] transition-all col-span-2 md:col-span-1">
        <div className="flex items-center justify-between">
          <span className="text-[11px] font-mono font-bold tracking-wider text-[#5B6577] uppercase">
            Suite Health
          </span>
          <div className="w-8 h-8 rounded-lg bg-[#F8FAFC] border border-[#E3E8F0] flex items-center justify-center text-[#2563EB]">
            <Activity className="w-4 h-4" />
          </div>
        </div>
        <div className="mt-2.5 flex items-baseline gap-2">
          <span className="text-2xl sm:text-3xl font-heading font-extrabold text-[#0F172A] tracking-tight">
            {healthScore}
          </span>
          <span className="text-xs text-[#5B6577] font-mono">/ 100</span>
          <span className={`text-xs font-mono font-semibold ${healthScore >= 75 ? "text-[#16A34A]" : "text-[#D97706]"}`}>
            {healthScore >= 75 ? "Resilient" : "Flaky Risk"}
          </span>
        </div>
        <div className="mt-2 text-[11px] text-[#5B6577] font-mono">
          Pass Rate + Flake Penalty
        </div>
        <div className="absolute top-0 left-0 right-0 h-1 bg-[#2563EB]" />
      </div>
    </div>
  );
}
