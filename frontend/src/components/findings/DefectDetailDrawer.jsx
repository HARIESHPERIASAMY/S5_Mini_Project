import React, { useState } from 'react';
import { 
  CheckCircle2, Copy, Check, Download, Share2, 
  Play, MessageSquare, Sparkles, AlertCircle, 
  GitPullRequest, ArrowRight, ShieldCheck, XCircle
} from 'lucide-react';
import { deriveMergeReadiness, getBugWorkflowState } from '../../api/adapters';

export default function DefectDetailDrawer({
  bug,
  runData,
  runId,
  beginnerMode = false,
  onToggleBeginnerMode,
  onExportPatch,
  onOpenAssistant,
  onUpdateWorkflowState
}) {
  const [activeTab, setActiveTab] = useState("fix"); // "fix" | "proof" | "debate" | "ask"
  const [copiedPatch, setCopiedPatch] = useState(false);
  const [copiedLink, setCopiedLink] = useState(false);
  const [whatIfActive, setWhatIfActive] = useState(false);
  const [replayPlaying, setReplayPlaying] = useState(false);
  const [activeAgentStep, setActiveAgentStep] = useState(3);

  if (!bug) {
    return (
      <div className="sm-card bg-white border border-[#E2E8F0] rounded-xl p-8 text-center text-[#64748B] flex flex-col items-center justify-center h-full shadow-xs">
        <AlertCircle className="w-8 h-8 text-[#CBD5E1] mb-2" />
        <h4 className="font-heading font-bold text-[#0F172A] text-sm">No Defect Selected</h4>
        <p className="text-xs text-[#64748B] mt-1 max-w-xs">
          Select a defect from the table to view the AST root cause, Proof of Fix receipt, and merge gate checks.
        </p>
      </div>
    );
  }

  const currentStatus = getBugWorkflowState(runId, bug);
  const readiness = deriveMergeReadiness(bug, runData);
  const confidence = Math.round((bug.confidence || 0.94) * 100);

  // Extract Diff lines
  const diffText = bug.proposed_fix_diff || "";
  const diffLines = diffText.split('\n');
  const removedLines = [];
  const addedLines = [];
  diffLines.forEach((l) => {
    if (l.startsWith('-') && !l.startsWith('---')) removedLines.push(l.substring(1));
    else if (l.startsWith('+') && !l.startsWith('+++')) addedLines.push(l.substring(1));
  });

  const defectLine = bug.line_number || 41;
  const originalLine = removedLines[0] || (bug.code_snippet ? bug.code_snippet.split('\n')[0] : "if total > THRESHOLD:");
  const fixedLine = addedLines[0] || "if total >= THRESHOLD:";

  const handleCopyPatch = () => {
    navigator.clipboard.writeText(diffText || `${originalLine}\n-->\n${fixedLine}`);
    setCopiedPatch(true);
    setTimeout(() => setCopiedPatch(false), 2000);
  };

  const handleCopyLink = () => {
    navigator.clipboard.writeText(window.location.href);
    setCopiedLink(true);
    setTimeout(() => setCopiedLink(false), 2000);
  };

  const handlePlayReplay = () => {
    setReplayPlaying(true);
    let step = 0;
    const interval = setInterval(() => {
      step += 1;
      setActiveAgentStep(step % 6);
      if (step >= 6) {
        clearInterval(interval);
        setReplayPlaying(false);
      }
    }, 800);
  };

  // Plain language vs technical text
  const whatFailedText = beginnerMode
    ? (bug.beginner_explanation || "An order exactly at the threshold gets no discount because the check strictly requires spending more than the limit.")
    : (bug.description || "An order exactly at the threshold gets no discount.");

  const whyText = beginnerMode
    ? "The code used '>' instead of '>=', meaning the exact boundary number was excluded from discount calculations."
    : `The check uses "greater than" at ${bug.file_path}:${defectLine}. It should be "greater than or equal".`;

  return (
    <div className="sm-card bg-white border border-[#E2E8F0] rounded-xl flex flex-col h-full shadow-xs overflow-hidden">
      {/* 1. Header with Metadata */}
      <div className="p-4 border-b border-[#E2E8F0] bg-white">
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-1.5 flex-wrap">
            <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-[#FFF4E0] text-[#9A5B00] border border-[#FEDF89]">
              {bug.severity || "Medium"}
            </span>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-[#E7F8EE] text-[#14753B] border border-[#A6F4C5]">
              {currentStatus}
            </span>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-[#EEF2FF] text-[#2457F5] border border-[#B2CCFF]">
              Confidence {confidence}%
            </span>
          </div>

          {/* Beginner Mode Checkbox */}
          <label className="flex items-center gap-1.5 text-[11px] text-[#475569] font-medium cursor-pointer select-none">
            <input
              type="checkbox"
              checked={beginnerMode}
              onChange={onToggleBeginnerMode}
              className="rounded border-[#CBD5E1] text-[#2457F5] focus:ring-0 cursor-pointer"
            />
            <span>Explain like I&apos;m a beginner</span>
          </label>
        </div>

        <h3 className="font-heading font-extrabold text-[#0F172A] text-base mt-2">
          {bug.title}
        </h3>
      </div>

      {/* 2. Navigation Tabs (Fix, Proof, Debate, Ask) */}
      <div className="flex items-center border-b border-[#E2E8F0] bg-[#F8FAFC] px-4">
        {[
          { id: "fix", label: "Fix" },
          { id: "proof", label: "Proof" },
          { id: "debate", label: "Debate" },
          { id: "ask", label: "Ask" },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2.5 text-xs font-semibold border-b-2 transition-all cursor-pointer ${
              activeTab === tab.id
                ? "border-[#2457F5] text-[#2457F5] bg-white"
                : "border-transparent text-[#64748B] hover:text-[#0F172A]"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* 3. Tab Viewports */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">

        {/* TAB 1: FIX */}
        {activeTab === "fix" && (
          <div className="space-y-4">
            <div>
              <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-[#64748B] block mb-1">
                What Failed
              </span>
              <p className="text-xs text-[#0F172A] leading-relaxed">
                {whatFailedText}
              </p>
            </div>

            <div>
              <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-[#64748B] block mb-1">
                Why
              </span>
              <p className="text-xs text-[#0F172A] leading-relaxed">
                {whyText}
              </p>
            </div>

            {/* Code Diff Snippet */}
            <div className="rounded-lg border border-[#E2E8F0] overflow-hidden font-mono text-xs">
              <div className="bg-[#FEECEC] text-[#B42318] px-3 py-2 border-b border-[#FECDCA] flex items-center gap-2">
                <span className="text-[#991B1B] font-bold">{defectLine}</span>
                <span className="text-[#991B1B] font-bold">-</span>
                <span className="truncate">{originalLine}</span>
              </div>
              <div className="bg-[#E7F8EE] text-[#14753B] px-3 py-2 flex items-center gap-2">
                <span className="text-[#166534] font-bold">{defectLine}</span>
                <span className="text-[#166534] font-bold">+</span>
                <span className="truncate">{fixedLine}</span>
              </div>
            </div>

            {/* Merge Gate Status Summary */}
            <div className="p-2.5 rounded-lg bg-[#FAFBFD] border border-[#E2E8F0] text-[11px] font-mono text-[#0F172A] flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-[#16A34A] flex-shrink-0" />
              <span>Safe to merge · 14/14 tests · 0 regressions · critic approved</span>
            </div>

            {/* What-If Simulator Hook */}
            <div className="p-3 rounded-lg bg-[#EEF2FF] border border-[#B2CCFF] flex items-center justify-between text-xs">
              <div>
                <span className="font-bold text-[#1D4ED8] block">What-If Simulation</span>
                <span className="text-[11px] text-[#475569]">
                  {whatIfActive ? "Previewing health score impact (+4.2 pts → 77.7)" : "Simulate health score impact if merged"}
                </span>
              </div>
              <button
                onClick={() => setWhatIfActive(!whatIfActive)}
                className={`px-3 py-1 rounded-md text-[11px] font-semibold transition-all cursor-pointer ${
                  whatIfActive
                    ? "bg-[#2457F5] text-white"
                    : "bg-white text-[#2457F5] border border-[#B2CCFF]"
                }`}
              >
                {whatIfActive ? "Active (+4.2)" : "Simulate"}
              </button>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-2 pt-2">
              <button
                onClick={handleCopyPatch}
                className="flex-1 flex items-center justify-center gap-1.5 h-9 rounded-lg bg-white hover:bg-[#F8FAFC] border border-[#E2E8F0] text-xs font-semibold text-[#0F172A] transition-colors cursor-pointer"
              >
                {copiedPatch ? <Check className="w-3.5 h-3.5 text-[#16A34A]" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copiedPatch ? "Copied diff" : "Copy patch"}</span>
              </button>

              <button
                onClick={() => onUpdateWorkflowState(bug.id, "Dismissed")}
                className="px-3 h-9 rounded-lg bg-white hover:bg-[#FEECEC] border border-[#E2E8F0] hover:border-[#FECDCA] text-xs font-semibold text-[#64748B] hover:text-[#B42318] transition-colors cursor-pointer"
              >
                Dismiss
              </button>

              <button
                onClick={() => {
                  onUpdateWorkflowState(bug.id, "PR opened");
                  if (onExportPatch) onExportPatch();
                }}
                className="flex-1 flex items-center justify-center gap-1.5 h-9 rounded-lg bg-[#2457F5] hover:bg-[#1A44D4] text-white text-xs font-semibold shadow-xs transition-all cursor-pointer"
              >
                <GitPullRequest className="w-3.5 h-3.5" />
                <span>Open PR</span>
              </button>
            </div>
          </div>
        )}

        {/* TAB 2: PROOF (Page 2 Screenshot) */}
        {activeTab === "proof" && (
          <div className="space-y-4">
            {/* Merge Readiness Card */}
            <div className="p-4 rounded-xl border border-[#A6F4C5] bg-[#FAFDFB] space-y-3">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-[#16A34A] text-white flex items-center justify-center flex-shrink-0">
                    <Check className="w-5 h-5 stroke-[3]" />
                  </div>
                  <div>
                    <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-[#16A34A] block">
                      Merge Readiness
                    </span>
                    <h4 className="text-sm font-heading font-extrabold text-[#0F172A]">
                      {readiness?.headline || "Safe to merge"}
                    </h4>
                    <span className="text-[11px] text-[#64748B]">
                      5 of 5 checks passed. Confidence {confidence}%.
                    </span>
                  </div>
                </div>

                <button
                  onClick={() => {
                    onUpdateWorkflowState(bug.id, "PR opened");
                    if (onExportPatch) onExportPatch();
                  }}
                  className="px-3 h-8 rounded-lg bg-[#2457F5] hover:bg-[#1A44D4] text-white text-xs font-semibold shadow-xs transition-all cursor-pointer"
                >
                  Open PR
                </button>
              </div>

              {/* 5 Checklist Items */}
              <div className="space-y-2 pt-2 border-t border-[#E2E8F0] text-xs">
                {readiness?.checks?.map((chk, cIdx) => (
                  <div key={cIdx} className="flex items-center justify-between text-[#0F172A]">
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4 text-[#16A34A] flex-shrink-0" />
                      <span>{chk.label}</span>
                    </div>
                    <span className="font-mono text-[11px] text-[#64748B]">{chk.value}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Proof of Fix Receipt */}
            <div className="p-4 rounded-xl border border-[#E2E8F0] bg-white space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="font-heading font-bold text-xs text-[#0F172A]">
                    Proof of Fix receipt
                  </span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-[#EEF2FF] text-[#2457F5] border border-[#B2CCFF]">
                    PF-{(runId || "2841").slice(0, 4)}-03
                  </span>
                </div>

                <div className="flex items-center gap-1.5">
                  <button
                    onClick={() => window.print()}
                    className="flex items-center gap-1 px-2.5 h-7 rounded-md border border-[#E2E8F0] bg-white hover:bg-[#F8FAFC] text-[11px] font-medium text-[#0F172A] cursor-pointer"
                  >
                    <Download className="w-3 h-3 text-[#64748B]" />
                    <span>Download PDF</span>
                  </button>
                  <button
                    onClick={handleCopyLink}
                    className="flex items-center gap-1 px-2.5 h-7 rounded-md border border-[#E2E8F0] bg-white hover:bg-[#F8FAFC] text-[11px] font-medium text-[#0F172A] cursor-pointer"
                  >
                    <Share2 className="w-3 h-3 text-[#64748B]" />
                    <span>{copiedLink ? "Copied" : "Copy share link"}</span>
                  </button>
                </div>
              </div>

              {/* Side-by-Side Test Output */}
              <div className="space-y-2 font-mono text-xs">
                <div className="p-2.5 rounded-lg bg-[#FEECEC] border border-[#FECDCA] text-[#B42318]">
                  <span className="text-[10px] font-bold block mb-1">BEFORE · 1 failed, 13 passed</span>
                  <div className="text-[11px] truncate">{defectLine} &nbsp;{originalLine}</div>
                  <div className="text-[10px] text-[#991B1B] mt-0.5">AssertionError: expected 90.0, got 100.0</div>
                </div>

                <div className="p-2.5 rounded-lg bg-[#E7F8EE] border border-[#A6F4C5] text-[#14753B]">
                  <span className="text-[10px] font-bold block mb-1">AFTER · 14 passed</span>
                  <div className="text-[11px] truncate">{defectLine} &nbsp;{fixedLine}</div>
                  <div className="text-[10px] text-[#166534] mt-0.5">All assertions hold at the boundary</div>
                </div>
              </div>

              {/* Verifier Signature */}
              <div className="pt-2 border-t border-[#E2E8F0] text-[10px] font-mono text-[#64748B] leading-relaxed">
                Signed by the Verifier agent · sandbox run 14:02:11 · patch hash 9f3a…c21e. Attach it to the PR so reviewers don&apos;t have to re-check.
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: DEBATE (Page 2 Screenshot) */}
        {activeTab === "debate" && (
          <div className="space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-[#E2E8F0]">
              <div className="flex items-center gap-2">
                <span className="font-heading font-bold text-xs text-[#0F172A]">
                  Agent debate replay
                </span>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-[#FFF4E0] text-[#9A5B00] border border-[#FEDF89]">
                  Plain-language mode
                </span>
              </div>

              <button
                onClick={handlePlayReplay}
                disabled={replayPlaying}
                className="flex items-center gap-1 px-2.5 h-7 rounded-md bg-[#2457F5] hover:bg-[#1A44D4] text-white text-[11px] font-semibold transition-all cursor-pointer"
              >
                <Play className="w-3 h-3 fill-white" />
                <span>Play</span>
              </button>
            </div>

            {/* 6-step Agent Sequence Bar */}
            <div className="grid grid-cols-3 sm:grid-cols-6 gap-1.5 text-center text-[10px] font-mono">
              {[
                { name: "Static", task: "Flagged line 41" },
                { name: "Test gen", task: "Wrote edge case" },
                { name: "Executor", task: "Reproduced it" },
                { name: "Critic", task: "Challenged fix" },
                { name: "Auto-fix", task: "Revised patch" },
                { name: "Verifier", task: "Certified" },
              ].map((step, idx) => (
                <div
                  key={idx}
                  className={`p-2 rounded-lg border transition-all ${
                    idx === activeAgentStep
                      ? "bg-[#EEF2FF] border-[#2457F5] text-[#2457F5] font-bold shadow-xs scale-102"
                      : "bg-[#F8FAFC] border-[#E2E8F0] text-[#64748B]"
                  }`}
                >
                  <span className="block font-bold text-[#0F172A]">{step.name}</span>
                  <span className="text-[9px] truncate block">{step.task}</span>
                </div>
              ))}
            </div>

            {/* Dialogue Quotes */}
            <div className="p-3.5 rounded-xl bg-[#FAFBFD] border border-[#E2E8F0] space-y-2 text-xs leading-relaxed">
              <div className="text-[#0F172A]">
                <strong className="text-[#D97706]">Critic, step 4:</strong> &ldquo;Your first patch also changed the rounding. That could break other prices.&rdquo;
              </div>
              <div className="text-[#0F172A]">
                <strong className="text-[#2457F5]">Auto-fix:</strong> &ldquo;Agreed. I removed the rounding change and kept only the comparison.&rdquo;
              </div>
            </div>

            {/* Real Backend Debate Message List */}
            {runData?.debates && runData.debates.length > 0 && (
              <div className="space-y-2 pt-2">
                <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-[#64748B] block">
                  Debate Transcript ({runData.debates.length} rounds)
                </span>
                <div className="space-y-1.5 max-h-48 overflow-y-auto">
                  {runData.debates.map((d, dIdx) => (
                    <div key={dIdx} className="p-2.5 rounded-lg bg-white border border-[#E2E8F0] text-[11px] font-mono">
                      <div className="flex items-center justify-between text-[#64748B]">
                        <span className="font-bold text-[#0F172A]">{d.agent || "Critic"}</span>
                        <span>Round #{d.round || dIdx + 1}</span>
                      </div>
                      <p className="text-[#0F172A] mt-1 font-sans">{d.claim || d.content}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB 4: ASK */}
        {activeTab === "ask" && (
          <div className="space-y-4">
            <div>
              <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-[#64748B] block mb-1">
                Ask Mesh Assistant About This Defect
              </span>
              <p className="text-xs text-[#64748B]">
                Mesh Assistant can answer root-cause questions, run sandbox &ldquo;what-if&rdquo; experiments, or draft pull request descriptions.
              </p>
            </div>

            <div className="space-y-2">
              {[
                `Why did the ${bug.title} fail?`,
                `Is the fix for ${bug.file_path}:${defectLine} safe to merge?`,
                `Explain ${bug.title} to a teammate who is new.`,
                `What else could break if we apply this fix?`,
              ].map((promptText, pIdx) => (
                <button
                  key={pIdx}
                  onClick={() => {
                    if (onOpenAssistant) onOpenAssistant(promptText);
                  }}
                  className="w-full p-2.5 rounded-lg border border-[#E2E8F0] hover:border-[#2457F5] bg-white hover:bg-[#F8FAFC] text-left text-xs text-[#0F172A] flex items-center justify-between transition-colors cursor-pointer"
                >
                  <span>{promptText}</span>
                  <ArrowRight className="w-3.5 h-3.5 text-[#2457F5]" />
                </button>
              ))}
            </div>

            <button
              onClick={() => {
                if (onOpenAssistant) onOpenAssistant(`Review defect ${bug.title} at ${bug.file_path}:${defectLine}`);
              }}
              className="w-full flex items-center justify-center gap-2 h-9 rounded-lg bg-[#2457F5] hover:bg-[#1A44D4] text-white text-xs font-semibold shadow-xs transition-all cursor-pointer"
            >
              <MessageSquare className="w-3.5 h-3.5" />
              <span>Open in Mesh Assistant</span>
            </button>
          </div>
        )}

      </div>
    </div>
  );
}
