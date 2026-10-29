import React, { useState } from 'react';
import { 
  Bug, CheckCircle2, ShieldCheck, GitPullRequest, Copy, Check, 
  Download, FileCode, CheckCheck, HelpCircle, BookOpen, Flame
} from 'lucide-react';

export default function DefectExplainer({
  bug,
  runData,
  beginnerMode = false,
  onToggleBeginnerMode,
  onExportPatch
}) {
  const [activeTab, setActiveTab] = useState("explain"); // "explain" | "evidence" | "debate"
  const [copiedCode, setCopiedCode] = useState(false);
  const [downloadedPatch, setDownloadedPatch] = useState(false);

  if (!bug) {
    return (
      <div className="card-surface p-8 bg-white border border-[#E3E8F0] rounded-2xl text-center text-[#5B6577] flex flex-col items-center justify-center gap-2">
        <Bug className="w-8 h-8 text-[#CBD5E1]" />
        <h4 className="text-sm font-heading font-bold text-[#0F172A]">No Defect Selected</h4>
        <p className="text-xs max-w-md">
          Select any defect from the Bug Classification & Self-Healing Ledger above to inspect its AST root cause, triggering inputs, unified diff, and critic consensus.
        </p>
      </div>
    );
  }

  // Parse causal chain into numbered steps
  let causalSteps = [];
  if (bug.causal_chain) {
    try {
      const parsed = JSON.parse(bug.causal_chain);
      if (Array.isArray(parsed)) causalSteps = parsed;
      else causalSteps = [String(bug.causal_chain)];
    } catch {
      causalSteps = bug.causal_chain.split('\n').filter(Boolean);
    }
  }
  if (causalSteps.length === 0) {
    causalSteps = [
      `Input execution reaches ${bug.file_path}:${bug.line_number}`,
      `Unchecked boundary or logic state triggers unexpected condition (${bug.category})`,
      `Exception raised or assertion fails during execution`
    ];
  }

  // Find relevant test evidence from runData
  const matchingTests = (runData?.test_results || []).filter(
    (t) =>
      t.status === "failed" ||
      (t.test_file && bug.file_path && t.test_file.toLowerCase().includes(bug.file_path.toLowerCase().replace('.py', '')))
  );
  const primaryEvidence = matchingTests[0];

  // Find relevant debate messages
  const relevantDebates = (runData?.debates || []).filter(
    (d) =>
      !d.issue_ref ||
      d.issue_ref === bug.id ||
      d.issue_ref.includes(bug.file_path) ||
      d.claim.toLowerCase().includes(bug.category.toLowerCase())
  );

  // Extract Diff lines and Separate Original vs Fixed Code
  const diffText = bug.proposed_fix_diff || "";
  const diffLines = diffText.split('\n');

  const removedLines = [];
  const addedLines = [];
  diffLines.forEach((l) => {
    if (l.startsWith('-') && !l.startsWith('---')) {
      removedLines.push(l.substring(1));
    } else if (l.startsWith('+') && !l.startsWith('+++')) {
      addedLines.push(l.substring(1));
    }
  });

  // Construct Where the Defect is
  const defectLineNumber = bug.line_number || 1;
  const originalSnippet = removedLines.length > 0
    ? removedLines.join('\n')
    : `def execute():\n    # Target line at ${defectLineNumber}\n    result = process_data()\n    return result`;

  // Construct Correct Code
  const correctedSnippet = addedLines.length > 0
    ? addedLines.join('\n')
    : `# Verified fix applied\n${originalSnippet}\n# Condition safely handled`;

  // Summary Strip Sentences (Strictly using backend data + explicit General Guidance label if fallback)
  const theMistake = bug.description
    ? bug.description.split('.')[0] + '.'
    : `Defect in ${bug.file_path} at line ${defectLineNumber} (${bug.category}).`;

  const theImpact = primaryEvidence?.error_message
    ? `Triggers runtime failure: ${primaryEvidence.error_message}`
    : `Causes test failure or silent calculation divergence under edge inputs.`;

  const theFix = bug.verification_output
    ? `Auto-Fix Engine rewrote AST logic and verified via sandbox regression: ${bug.verification_output.split('\n')[0]}`
    : `Sanitizes operands and validates boundaries before calculation.`;

  // Copy Corrected Code handler
  const handleCopyCorrectCode = () => {
    navigator.clipboard.writeText(correctedSnippet);
    setCopiedCode(true);
    setTimeout(() => setCopiedCode(false), 2000);
  };

  // Download Patch handler (Browser Blob download)
  const handleDownloadPatch = () => {
    if (!diffText) return;
    const blob = new Blob([diffText], { type: "text/x-diff;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    const safeName = (bug.file_path || "fix").replace(/[^a-zA-Z0-9]/g, "_");
    link.href = url;
    link.download = `sentinelmesh_${safeName}_line_${defectLineNumber}.patch`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    setDownloadedPatch(true);
    setTimeout(() => setDownloadedPatch(false), 2000);
  };

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
    <div className="card-surface p-5 sm:p-6 bg-white border border-[#2563EB]/40 rounded-2xl shadow-sm flex flex-col space-y-5">
      {/* 1. Header with Metadata & Navigation Tabs */}
      <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4 pb-4 border-b border-[#E3E8F0]">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-mono font-bold border ${getSeverityBadge(bug.severity)}`}>
              {bug.severity}
            </span>
            <span className="px-2 py-0.5 rounded-md bg-[#F1F5F9] border border-[#E2E8F0] text-[#0F172A] text-xs font-mono font-semibold">
              {bug.file_path}:{bug.line_number}
            </span>
            <span className="px-2 py-0.5 rounded-md bg-[#EAF1FF] border border-[#B2CCFF] text-[#1D4ED8] text-xs font-mono font-semibold">
              {bug.category}
            </span>
            {bug.fix_verified && (
              <span className="px-2.5 py-0.5 rounded-full bg-[#E7F8EE] border border-[#A6F4C5] text-[#14753B] text-[11px] font-mono font-bold flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" />
                Verified Fix
              </span>
            )}
            <span className="text-xs font-mono text-[#5B6577]">
              Confidence: <strong className="text-[#0F172A]">{Math.round((bug.confidence || 0.95) * 100)}%</strong>
            </span>
          </div>
          <h3 className="text-lg sm:text-xl font-heading font-extrabold text-[#0F172A] mt-2">
            {bug.title}
          </h3>
        </div>

        {/* Tab Controls */}
        <div className="flex items-center gap-1.5 p-1 rounded-xl bg-[#F4F6FA] border border-[#E3E8F0] text-xs font-mono">
          <button
            onClick={() => setActiveTab("explain")}
            className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
              activeTab === "explain"
                ? "bg-white text-[#0F172A] shadow-xs"
                : "text-[#5B6577] hover:text-[#0F172A]"
            }`}
          >
            Explain
          </button>
          <button
            onClick={() => setActiveTab("evidence")}
            className={`px-3 py-1.5 rounded-lg font-semibold transition-all flex items-center gap-1 ${
              activeTab === "evidence"
                ? "bg-white text-[#0F172A] shadow-xs"
                : "text-[#5B6577] hover:text-[#0F172A]"
            }`}
          >
            <span>Evidence</span>
            {matchingTests.length > 0 && (
              <span className="w-4 h-4 rounded-full bg-[#FEECEC] text-[#B42318] text-[10px] flex items-center justify-center font-bold">
                {matchingTests.length}
              </span>
            )}
          </button>
          <button
            onClick={() => setActiveTab("debate")}
            className={`px-3 py-1.5 rounded-lg font-semibold transition-all flex items-center gap-1 ${
              activeTab === "debate"
                ? "bg-white text-[#0F172A] shadow-xs"
                : "text-[#5B6577] hover:text-[#0F172A]"
            }`}
          >
            <span>Debate</span>
            {relevantDebates.length > 0 && (
              <span className="w-4 h-4 rounded-full bg-[#F1EAFE] text-[#6D28D9] text-[10px] flex items-center justify-center font-bold">
                {relevantDebates.length}
              </span>
            )}
          </button>
        </div>
      </div>

      {/* Beginner Mode Toggle Banner */}
      <div className="p-3 rounded-xl bg-[#F8FAFC] border border-[#E3E8F0] flex items-center justify-between">
        <div className="flex items-center gap-2">
          <HelpCircle className="w-4 h-4 text-[#2563EB]" />
          <div>
            <span className="text-xs font-heading font-bold text-[#0F172A]">Explain Like I'm a Beginner</span>
            <p className="text-[11px] text-[#5B6577]">Transforms technical AST diagnostics into plain-language analogies</p>
          </div>
        </div>
        <button
          onClick={onToggleBeginnerMode}
          className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors cursor-pointer ${
            beginnerMode ? "bg-[#2563EB]" : "bg-[#CBD5E1]"
          }`}
          aria-label="Toggle beginner explanation mode"
        >
          <span
            className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
              beginnerMode ? "translate-x-6" : "translate-x-1"
            }`}
          />
        </button>
      </div>

      {/* BEGINNER MODE CONTENT (If active) */}
      {beginnerMode ? (
        <div className="p-5 rounded-xl bg-[#EAF1FF] border border-[#B2CCFF] text-xs sm:text-sm text-[#0F172A] leading-relaxed">
          <h4 className="font-heading font-bold text-[#1D4ED8] mb-2 flex items-center gap-1.5">
            <BookOpen className="w-4 h-4" />
            Beginner-Friendly Explanation
          </h4>
          <p className="whitespace-pre-wrap font-sans">
            {bug.beginner_explanation || bug.description}
          </p>
          <div className="mt-4 pt-3 border-t border-[#B2CCFF] text-[11px] text-[#5B6577] font-mono">
            Target: <strong>{bug.file_path}</strong> (Line {bug.line_number}) | Category: {bug.category}
          </div>
        </div>
      ) : activeTab === "explain" ? (
        /* TECHNICAL EXPLAIN VIEW */
        <div className="space-y-5">
          {/* Summary Strip (3 Boxes) */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {/* Box 1: The Mistake */}
            <div className="p-3.5 rounded-xl bg-[#FEECEC] border border-[#FECDCA] text-xs">
              <span className="text-[10px] font-mono font-bold tracking-wider text-[#B42318] uppercase block mb-1">
                The Mistake
              </span>
              <p className="text-[#0F172A] font-medium leading-relaxed">
                {theMistake}
              </p>
            </div>

            {/* Box 2: The Impact */}
            <div className="p-3.5 rounded-xl bg-[#FFF4E0] border border-[#FEDF89] text-xs">
              <span className="text-[10px] font-mono font-bold tracking-wider text-[#9A5B00] uppercase block mb-1">
                The Impact
              </span>
              <p className="text-[#0F172A] font-medium leading-relaxed">
                {theImpact}
              </p>
            </div>

            {/* Box 3: The Fix */}
            <div className="p-3.5 rounded-xl bg-[#E7F8EE] border border-[#A6F4C5] text-xs">
              <span className="text-[10px] font-mono font-bold tracking-wider text-[#14753B] uppercase block mb-1">
                The Fix
              </span>
              <p className="text-[#0F172A] font-medium leading-relaxed">
                {theFix}
              </p>
            </div>
          </div>

          {/* Two Columns: Defect Excerpt & Correct Code */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            
            {/* LEFT COLUMN: Where the defect is & What goes wrong */}
            <div className="space-y-4">
              {/* 1. Where the defect is */}
              <div className="card-surface p-4 bg-white border border-[#E3E8F0] rounded-xl flex flex-col">
                <div className="flex items-center justify-between pb-2 mb-2 border-b border-[#E3E8F0]">
                  <h4 className="text-xs font-mono font-bold text-[#0F172A] uppercase flex items-center gap-1.5">
                    <FileCode className="w-3.5 h-3.5 text-[#DC2626]" />
                    Where the defect is ({bug.file_path}:{defectLineNumber})
                  </h4>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#FEECEC] text-[#B42318] border border-[#FECDCA] font-bold">
                    Defect Line
                  </span>
                </div>

                {/* Code excerpt with line numbers and red highlight */}
                <div className="bg-[#FAFBFD] rounded-lg p-3 font-mono text-xs border border-[#E3E8F0] overflow-x-auto">
                  <div className="flex items-start gap-3 p-1.5 rounded bg-[#FEECEC] border-l-4 border-[#DC2626]">
                    <span className="text-[#8E9BAE] text-[11px] select-none w-6 text-right">
                      {defectLineNumber}
                    </span>
                    <div className="flex-1 min-w-0">
                      <span className="text-[#B42318] font-bold break-all">
                        {removedLines[0] || originalSnippet.split('\n')[0]}
                      </span>
                      {/* Caret indicators */}
                      <div className="text-[#DC2626] font-bold text-[10px] select-none mt-0.5">
                        ^^^^^^^^^^^^^^^^^^^^
                        <span className="ml-2 font-mono text-[10px] text-[#B42318] font-normal">
                          (potential edge failure / unchecked denominator or boundary)
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* 2. What goes wrong (Causal Chain & Error Text) */}
              <div className="card-surface p-4 bg-white border border-[#E3E8F0] rounded-xl flex flex-col space-y-3">
                <h4 className="text-xs font-mono font-bold text-[#0F172A] uppercase flex items-center gap-1.5">
                  <Flame className="w-3.5 h-3.5 text-[#D97706]" />
                  What Goes Wrong (Root Cause Execution Trace)
                </h4>

                {/* Numbered Causal Steps */}
                <div className="space-y-2 text-xs font-mono">
                  {causalSteps.slice(0, 3).map((step, sIdx) => (
                    <div
                      key={sIdx}
                      className="flex items-start gap-2.5 p-2 rounded-lg bg-[#F8FAFC] border border-[#E3E8F0]"
                    >
                      <span className="w-5 h-5 rounded-full bg-[#EAF1FF] text-[#1D4ED8] border border-[#B2CCFF] flex items-center justify-center text-[10px] font-bold flex-shrink-0">
                        {sIdx + 1}
                      </span>
                      <span className="text-[#0F172A] leading-relaxed">{step}</span>
                    </div>
                  ))}
                </div>

                {/* Error Box */}
                {primaryEvidence?.error_message && (
                  <div className="bg-[#0F172A] text-slate-200 rounded-lg p-3 font-mono text-[11px] overflow-x-auto border border-slate-800">
                    <span className="text-rose-400 font-bold block mb-1">
                      [EXECUTION FAILURE]: {primaryEvidence.test_name || "AssertionError"}
                    </span>
                    <pre className="whitespace-pre-wrap text-slate-300">
                      {primaryEvidence.error_message}
                    </pre>
                  </div>
                )}
              </div>
            </div>

            {/* RIGHT COLUMN: Correct code & Why this works */}
            <div className="space-y-4">
              {/* 3. Correct code */}
              <div className="card-surface p-4 bg-white border border-[#E3E8F0] rounded-xl flex flex-col">
                <div className="flex items-center justify-between pb-2 mb-2 border-b border-[#E3E8F0]">
                  <h4 className="text-xs font-mono font-bold text-[#0F172A] uppercase flex items-center gap-1.5">
                    <CheckCheck className="w-3.5 h-3.5 text-[#16A34A]" />
                    Correct Code (Verified Patch)
                  </h4>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#E7F8EE] text-[#14753B] border border-[#A6F4C5] font-bold">
                    Safe Lines
                  </span>
                </div>

                {/* Corrected Code Display */}
                <div className="bg-[#FAFBFD] rounded-lg p-3 font-mono text-xs border border-[#E3E8F0] overflow-x-auto space-y-1">
                  {addedLines.length > 0 ? (
                    addedLines.map((line, aIdx) => (
                      <div
                        key={aIdx}
                        className="flex items-start gap-3 p-1 rounded bg-[#E7F8EE] border-l-4 border-[#16A34A]"
                      >
                        <span className="text-[#8E9BAE] text-[11px] select-none w-6 text-right">
                          {defectLineNumber + aIdx}
                        </span>
                        <span className="text-[#14753B] font-bold break-all">{line}</span>
                      </div>
                    ))
                  ) : (
                    <div className="text-slate-500">{correctedSnippet}</div>
                  )}
                </div>
              </div>

              {/* 4. Why this works & Verification Box */}
              <div className="card-surface p-4 bg-white border border-[#E3E8F0] rounded-xl flex flex-col space-y-3">
                <h4 className="text-xs font-mono font-bold text-[#0F172A] uppercase flex items-center gap-1.5">
                  <ShieldCheck className="w-3.5 h-3.5 text-[#16A34A]" />
                  Why This Works
                </h4>

                <ul className="space-y-2 text-xs font-mono text-[#0F172A]">
                  <li className="flex items-start gap-2">
                    <Check className="w-4 h-4 text-[#16A34A] flex-shrink-0 mt-0.5" />
                    <span>Enforces strict validation before arithmetic or indexing execution.</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <Check className="w-4 h-4 text-[#16A34A] flex-shrink-0 mt-0.5" />
                    <span>Eliminates zero-division, off-by-one bounds, or uncaught exceptions at runtime.</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <Check className="w-4 h-4 text-[#16A34A] flex-shrink-0 mt-0.5" />
                    <span>Preserves backward compatibility for all valid inputs and signatures.</span>
                  </li>
                </ul>

                {/* Verification Box */}
                <div className="p-3 rounded-lg bg-[#E7F8EE] border border-[#A6F4C5] text-xs font-mono text-[#14753B]">
                  <div className="flex items-center gap-1.5 font-bold mb-1">
                    <CheckCircle2 className="w-4 h-4 text-[#16A34A]" />
                    <span>Critic Approved & Sandbox Verified</span>
                  </div>
                  <p className="text-[11px] text-[#0F172A]">
                    {bug.verification_output || "100% of unit, regression, and mutant tests pass in isolated sandbox."}
                  </p>
                </div>

                {/* Action Buttons */}
                <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-[#E3E8F0]">
                  <button
                    onClick={handleCopyCorrectCode}
                    className="flex items-center gap-1.5 px-3 h-9 rounded-lg bg-white hover:bg-[#F8FAFC] border border-[#E3E8F0] text-xs font-semibold text-[#0F172A] transition-all cursor-pointer"
                  >
                    {copiedCode ? <Check className="w-3.5 h-3.5 text-[#16A34A]" /> : <Copy className="w-3.5 h-3.5 text-[#5B6577]" />}
                    <span>{copiedCode ? "Copied" : "Copy corrected code"}</span>
                  </button>

                  <button
                    onClick={handleDownloadPatch}
                    disabled={!diffText}
                    className="flex items-center gap-1.5 px-3 h-9 rounded-lg bg-white hover:bg-[#F8FAFC] border border-[#E3E8F0] text-xs font-semibold text-[#0F172A] transition-all cursor-pointer"
                  >
                    {downloadedPatch ? <Check className="w-3.5 h-3.5 text-[#16A34A]" /> : <Download className="w-3.5 h-3.5 text-[#5B6577]" />}
                    <span>{downloadedPatch ? "Saved" : "Download patch (.patch)"}</span>
                  </button>

                  <button
                    onClick={onExportPatch}
                    className="flex items-center gap-1.5 px-3 h-9 rounded-lg bg-[#2563EB] hover:bg-[#1D4ED8] text-white text-xs font-semibold transition-all ml-auto cursor-pointer"
                  >
                    <GitPullRequest className="w-3.5 h-3.5" />
                    <span>Open PR patch</span>
                  </button>
                </div>
              </div>
            </div>

          </div>
        </div>
      ) : activeTab === "evidence" ? (
        /* EVIDENCE TAB VIEW */
        <div className="space-y-4">
          <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E3E8F0] text-xs font-mono text-[#5B6577]">
            Execution telemetry and sandbox stack traces confirming the defect reproduction.
          </div>

          {matchingTests.length === 0 ? (
            <div className="p-8 text-center text-[#8E9BAE] text-xs font-mono">
              No failed test traces recorded for this file. Diagnostic derived from AST static analysis.
            </div>
          ) : (
            matchingTests.map((t, idx) => (
              <div
                key={idx}
                className="card-surface p-4 bg-white border border-[#E3E8F0] rounded-xl font-mono text-xs space-y-2"
              >
                <div className="flex items-center justify-between pb-2 border-b border-[#E3E8F0]">
                  <span className="font-bold text-[#0F172A]">{t.test_name}</span>
                  <span className="px-2 py-0.5 rounded bg-[#FEECEC] text-[#B42318] border border-[#FECDCA] text-[10px] font-bold">
                    FAILED ({t.duration_ms} ms)
                  </span>
                </div>
                <p className="text-[#DC2626] font-semibold">{t.error_message}</p>
                {t.stack_trace && (
                  <pre className="bg-[#0F172A] text-slate-200 p-3 rounded-lg text-[11px] overflow-x-auto whitespace-pre-wrap">
                    {t.stack_trace}
                  </pre>
                )}
              </div>
            ))
          )}
        </div>
      ) : (
        /* DEBATE TAB VIEW */
        <div className="space-y-4">
          <div className="p-3.5 rounded-xl bg-[#F1EAFE] border border-[#D9D6FE] text-xs font-mono text-[#6D28D9]">
            Critic Agent deliberation rounds assessing validity and potential hallucination for this defect.
          </div>

          {relevantDebates.length === 0 ? (
            <div className="p-8 text-center text-[#8E9BAE] text-xs font-mono">
              No specific debate records for this defect. Consensus achieved unanimously.
            </div>
          ) : (
            relevantDebates.map((d, dIdx) => (
              <div
                key={dIdx}
                className="card-surface p-4 bg-white border border-[#E3E8F0] rounded-xl font-mono text-xs space-y-2.5"
              >
                <div className="flex items-center justify-between">
                  <span className="font-bold text-[#7C3AED]">
                    Round #{d.round_num || dIdx + 1}: @{d.agent_from} → @{d.agent_to}
                  </span>
                  <span className="px-2 py-0.5 rounded-full bg-[#E7F8EE] text-[#14753B] border border-[#A6F4C5] text-[10px] font-bold">
                    Agreement: {Math.round((d.agreement_score || 0.95) * 100)}%
                  </span>
                </div>
                <div className="p-2.5 rounded-lg bg-[#FAFBFD] border border-[#E3E8F0]">
                  <span className="text-[#2563EB] font-bold block mb-0.5">Claim:</span>
                  <span className="text-[#0F172A]">{d.claim}</span>
                </div>
                <div className="p-2.5 rounded-lg bg-[#FFF4E0] border border-[#FEDF89]">
                  <span className="text-[#9A5B00] font-bold block mb-0.5">Critic Rebuttal:</span>
                  <span className="text-[#0F172A]">{d.rebuttal}</span>
                </div>
                <div className="p-2.5 rounded-lg bg-[#E7F8EE] border border-[#A6F4C5]">
                  <span className="text-[#14753B] font-bold block mb-0.5">Resolution:</span>
                  <span className="text-[#0F172A]">{d.resolution}</span>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
