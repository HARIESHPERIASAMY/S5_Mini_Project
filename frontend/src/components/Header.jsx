import React from 'react';
import { Shield, Download, FileCode, Cpu, Sparkles, RefreshCw, GitPullRequest } from 'lucide-react';

export default function Header({
  activeRun,
  llmProvider,
  setLlmProvider,
  onLaunchDemo,
  onOpenNewProject,
  onExportPatch,
  onDownloadReport,
  isRunning,
  wsConnected = true
}) {
  const verifiedFixesCount = activeRun?.fixes_verified_count ?? 0;
  const hasPatch = Boolean(activeRun && verifiedFixesCount > 0);

  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-md border-b border-[#E3E8F0] shadow-xs">
      <div className="max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Brand & Tagline */}
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-[#2563EB] to-[#1D4ED8] flex items-center justify-center shadow-md shadow-blue-500/20 text-white">
              <Shield className="w-5 h-5" />
            </div>
            {isRunning && (
              <span className="absolute -top-1 -right-1 flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-blue-600"></span>
              </span>
            )}
          </div>
          <div>
            <div className="flex items-center gap-2.5">
              <span className="text-xl font-heading font-extrabold tracking-tight text-[#0F172A]">
                SentinelMesh
              </span>
              <span className="text-[11px] font-mono font-semibold px-2 py-0.5 rounded-full bg-[#EAF1FF] text-[#1D4ED8] border border-[#B2CCFF]">
                v2.0 Swarm
              </span>
            </div>
            <p className="text-xs text-[#5B6577]">
              Autonomous software testing and self-healing bug analysis platform
            </p>
          </div>
        </div>

        {/* Global Controls & Actions */}
        <div className="flex flex-wrap items-center gap-2.5">
          {/* Model Chip with Connection Dot */}
          <div className="flex items-center gap-2 px-3 h-10 rounded-[10px] bg-[#F4F6FA] border border-[#E3E8F0] text-xs text-[#0F172A] font-medium">
            <div className="flex items-center gap-1.5">
              <span
                className={`w-2 h-2 rounded-full ${
                  isRunning
                    ? "bg-blue-600 animate-pulse"
                    : wsConnected
                    ? "bg-[#16A34A]"
                    : "bg-[#D97706]"
                }`}
                title={wsConnected ? "Telemetry stream active" : "Stream offline / connecting"}
              />
              <Cpu className="w-3.5 h-3.5 text-[#5B6577]" />
            </div>
            <span className="text-[#5B6577] text-[11px] uppercase tracking-wider font-mono">Model:</span>
            <select
              value={llmProvider}
              onChange={(e) => setLlmProvider(e.target.value)}
              className="bg-transparent text-[#0F172A] font-semibold text-xs focus:outline-none cursor-pointer pr-1"
              aria-label="Select LLM Engine"
            >
              <option value="offline">Offline Engine (Zero-Key)</option>
              <option value="gemini">Google Gemini 2.5</option>
              <option value="openai">OpenAI / Ollama</option>
            </select>
          </div>

          {/* Action 1: Run Demo Project (Primary Blue) */}
          <button
            onClick={onLaunchDemo}
            disabled={isRunning}
            className={`flex items-center gap-2 px-4 h-10 rounded-[10px] font-semibold text-xs text-white transition-all shadow-sm ${
              isRunning
                ? "bg-blue-400 cursor-not-allowed opacity-90"
                : "bg-[#2563EB] hover:bg-[#1D4ED8] active:translate-y-px shadow-blue-500/25"
            }`}
          >
            {isRunning ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Sparkles className="w-4 h-4" />
            )}
            <span>{isRunning ? "Running Swarm..." : "Run Demo Project"}</span>
          </button>

          {/* Action 2: Analyze Code */}
          <button
            onClick={onOpenNewProject}
            className="flex items-center gap-1.5 px-3.5 h-10 rounded-[10px] bg-white hover:bg-[#F8FAFC] border border-[#E3E8F0] hover:border-[#CBD5E1] text-xs font-semibold text-[#0F172A] transition-all"
          >
            <FileCode className="w-3.5 h-3.5 text-[#2563EB]" />
            <span>Analyze Code</span>
          </button>

          {/* Action 3: Report (PR Patch) */}
          <button
            onClick={onExportPatch}
            disabled={!hasPatch}
            title={hasPatch ? "Download PR-ready Unified Fix Patch (.patch)" : "Available when verified fixes exist"}
            className={`flex items-center gap-1.5 px-3.5 h-10 rounded-[10px] text-xs font-semibold transition-all border ${
              hasPatch
                ? "bg-[#E7F8EE] hover:bg-[#D3F5E1] border-[#A6F4C5] text-[#14753B] cursor-pointer"
                : "bg-[#F8FAFC] border-[#E3E8F0] text-[#8E9BAE] cursor-not-allowed"
            }`}
          >
            <GitPullRequest className="w-3.5 h-3.5" />
            <span>Report (PR Patch)</span>
          </button>

          {/* Action 4: Report (HTML) */}
          <button
            onClick={onDownloadReport}
            disabled={!activeRun}
            title={activeRun ? "Download Standalone HTML Technical Audit Report" : "Available after analysis run"}
            className={`flex items-center gap-1.5 px-3.5 h-10 rounded-[10px] text-xs font-semibold transition-all border ${
              activeRun
                ? "bg-white hover:bg-[#F8FAFC] border-[#E3E8F0] hover:border-[#CBD5E1] text-[#0F172A] cursor-pointer"
                : "bg-[#F8FAFC] border-[#E3E8F0] text-[#8E9BAE] cursor-not-allowed"
            }`}
          >
            <Download className="w-3.5 h-3.5 text-[#5B6577]" />
            <span>Report (HTML)</span>
          </button>
        </div>
      </div>
    </header>
  );
}
