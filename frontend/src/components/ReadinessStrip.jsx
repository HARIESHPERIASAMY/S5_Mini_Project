import React from 'react';
import { CheckCircle2, XCircle, ArrowRight, BookOpen } from 'lucide-react';
import { RELEASE_GATE_THRESHOLDS } from '../constants';

export { RELEASE_GATE_THRESHOLDS };

export default function ReadinessStrip({
  runData,
  onReviewFix,
  onExplainBug,
  hasBugs
}) {
  const bugsCount = runData?.bugs_count ?? 0;
  const verifiedFixes = runData?.fixes_verified_count ?? 0;
  const coverage = runData?.code_coverage ?? 0;
  const mutationScore = runData?.mutation_score ?? 0;
  const healthScore = runData?.suite_health_score ?? 0;

  // Count open critical defects
  const openCriticalCount = (runData?.bugs || []).filter(
    (b) => b.severity === "CRITICAL" && !b.fix_verified
  ).length;

  // 5 Release Gate Conditions
  const gateAllFixesVerified = bugsCount === 0 || (bugsCount > 0 && verifiedFixes >= bugsCount);
  const gateCoveragePass = coverage >= RELEASE_GATE_THRESHOLDS.MIN_COVERAGE;
  const gateMutationPass = mutationScore >= RELEASE_GATE_THRESHOLDS.MIN_MUTATION;
  const gateNoCriticalOpen = openCriticalCount <= RELEASE_GATE_THRESHOLDS.MAX_OPEN_CRITICAL;
  const gateHealthPass = healthScore >= RELEASE_GATE_THRESHOLDS.MIN_SUITE_HEALTH;

  // Live headline text
  let headline = "Ready for execution — launch the demo project or upload a codebase to begin";
  if (runData) {
    if (bugsCount > 0) {
      headline = `${bugsCount} defect${bugsCount === 1 ? '' : 's'} flagged, and ${verifiedFixes} fix${verifiedFixes === 1 ? '' : 'es'} already verified in sandbox`;
    } else if (runData.status === "completed") {
      headline = "Zero defects flagged — suite clean and fully verified";
    } else if (runData.status === "running") {
      headline = `Multi-agent swarm actively analyzing codebase (${runData.progress_pct || 15}% complete)...`;
    }
  }

  // Circular Health Ring calculation
  const radius = 26;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (Math.min(100, Math.max(0, healthScore)) / 100) * circumference;

  let healthColor = "#16A34A"; // success green
  if (healthScore < 50) healthColor = "#DC2626"; // danger red
  else if (healthScore < 75) healthColor = "#D97706"; // warning amber

  const gates = [
    {
      id: "fixes",
      label: "Verified Fixes",
      value: bugsCount > 0 ? `${verifiedFixes}/${bugsCount}` : "Clean",
      passed: gateAllFixesVerified,
      hint: `${verifiedFixes} of ${bugsCount} healed`
    },
    {
      id: "coverage",
      label: "Coverage",
      value: `${coverage}%`,
      passed: gateCoveragePass,
      hint: `Target: ≥${RELEASE_GATE_THRESHOLDS.MIN_COVERAGE}%`
    },
    {
      id: "mutation",
      label: "Mutation Score",
      value: `${mutationScore}%`,
      passed: gateMutationPass,
      hint: `Target: ≥${RELEASE_GATE_THRESHOLDS.MIN_MUTATION}%`
    },
    {
      id: "critical",
      label: "Critical Open",
      value: `${openCriticalCount}`,
      passed: gateNoCriticalOpen,
      hint: `Target: ${RELEASE_GATE_THRESHOLDS.MAX_OPEN_CRITICAL}`
    },
    {
      id: "health",
      label: "Suite Health",
      value: `${healthScore}/100`,
      passed: gateHealthPass,
      hint: `Target: ≥${RELEASE_GATE_THRESHOLDS.MIN_SUITE_HEALTH}`
    }
  ];

  return (
    <div className="card-surface p-4 sm:p-5 bg-white border border-[#E3E8F0] rounded-2xl shadow-xs">
      <div className="flex flex-col xl:flex-row items-start xl:items-center justify-between gap-5">
        
        {/* Left: Live Headline & Health Ring */}
        <div className="flex items-center gap-4 min-w-0">
          {/* Health Ring Gauge */}
          <div className="relative flex-shrink-0 flex items-center justify-center">
            <svg className="w-16 h-16 transform -rotate-90">
              <circle
                cx="32"
                cy="32"
                r={radius}
                stroke="#E2E8F0"
                strokeWidth="5"
                fill="transparent"
              />
              <circle
                cx="32"
                cy="32"
                r={radius}
                stroke={healthColor}
                strokeWidth="5"
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                strokeLinecap="round"
                fill="transparent"
                className="transition-all duration-700 ease-out"
              />
            </svg>
            <div className="absolute flex flex-col items-center justify-center text-center">
              <span className="text-xs font-mono font-bold text-[#0F172A] leading-none">
                {healthScore}
              </span>
              <span className="text-[9px] font-mono text-[#5B6577] mt-0.5">
                HEALTH
              </span>
            </div>
          </div>

          {/* Headline Text */}
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <span className="text-[11px] font-mono font-bold uppercase tracking-wider text-[#2563EB] bg-[#EAF1FF] px-2 py-0.5 rounded border border-[#B2CCFF]">
                Readiness Assessment
              </span>
              {runData?.status && (
                <span className="text-[10px] font-mono text-[#5B6577] uppercase">
                  Status: <strong className="text-[#0F172A]">{runData.status}</strong>
                </span>
              )}
            </div>
            <h2 className="text-base sm:text-lg font-heading font-bold text-[#0F172A] mt-1 truncate">
              {headline}
            </h2>
            <p className="text-xs text-[#5B6577] mt-0.5">
              Automated multi-agent release gating across AST verification, sandboxed regressions, and mutant survival.
            </p>
          </div>
        </div>

        {/* Right: 5 Release Gates & Action Buttons */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 w-full xl:w-auto justify-between xl:justify-end">
          {/* 5-Item Gate Checklist */}
          <div className="flex flex-wrap items-center gap-2 sm:gap-3 py-1.5 px-3 rounded-xl bg-[#F8FAFC] border border-[#E3E8F0]">
            {gates.map((g) => (
              <div
                key={g.id}
                title={g.hint}
                className="flex items-center gap-1.5 px-2 py-1 rounded-lg bg-white border border-[#E3E8F0] text-xs font-mono"
              >
                {g.passed ? (
                  <CheckCircle2 className="w-3.5 h-3.5 text-[#16A34A] flex-shrink-0" />
                ) : (
                  <XCircle className="w-3.5 h-3.5 text-[#DC2626] flex-shrink-0" />
                )}
                <span className="text-[#5B6577] text-[11px]">{g.label}:</span>
                <span className={`font-bold ${g.passed ? "text-[#0F172A]" : "text-[#DC2626]"}`}>
                  {g.value}
                </span>
              </div>
            ))}
          </div>

          {/* Action Buttons: Review the Fix & Explain the Bug */}
          <div className="flex items-center gap-2 flex-shrink-0">
            <button
              onClick={onReviewFix}
              disabled={!hasBugs}
              className={`flex items-center gap-1.5 px-3.5 h-10 rounded-[10px] text-xs font-semibold transition-all border ${
                hasBugs
                  ? "bg-[#2563EB] hover:bg-[#1D4ED8] text-white border-transparent shadow-xs cursor-pointer"
                  : "bg-[#F8FAFC] text-[#8E9BAE] border-[#E3E8F0] cursor-not-allowed"
              }`}
            >
              <span>Review the fix</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={onExplainBug}
              disabled={!hasBugs}
              className={`flex items-center gap-1.5 px-3.5 h-10 rounded-[10px] text-xs font-semibold transition-all border ${
                hasBugs
                  ? "bg-white hover:bg-[#F8FAFC] text-[#0F172A] border-[#E3E8F0] hover:border-[#CBD5E1] cursor-pointer"
                  : "bg-[#F8FAFC] text-[#8E9BAE] border-[#E3E8F0] cursor-not-allowed"
              }`}
            >
              <BookOpen className="w-3.5 h-3.5 text-[#5B6577]" />
              <span>Explain the bug</span>
            </button>
          </div>

        </div>

      </div>
    </div>
  );
}
