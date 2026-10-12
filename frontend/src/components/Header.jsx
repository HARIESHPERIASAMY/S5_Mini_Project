import React from 'react';
import { Shield, Play, Download, FileCode, Cpu, Sparkles, RefreshCw } from 'lucide-react';

export default function Header({
  activeRun,
  llmProvider,
  setLlmProvider,
  onLaunchDemo,
  onOpenNewProject,
  onExportPatch,
  onDownloadReport,
  isRunning
}) {
  return (
    <header className="glass-panel border-b border-mesh-border px-6 py-4 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Brand & Status */}
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <Shield className="w-6 h-6 text-white" />
            </div>
            {isRunning && (
              <span className="absolute -top-1 -right-1 flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-cyan-500"></span>
              </span>
            )}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold tracking-tight bg-gradient-to-r from-white via-cyan-200 to-cyan-400 bg-clip-text text-transparent">
                SentinelMesh
              </h1>
              <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded-full bg-cyan-950/80 border border-cyan-800 text-cyan-300 font-semibold">
                Multi-Agent Swarm v1.0
              </span>
            </div>
            <p className="text-xs text-slate-400 font-mono">
              Autonomous Software Testing & Self-Healing Bug Analysis Platform
            </p>
          </div>
        </div>

        {/* Global Controls & Actions */}
        <div className="flex flex-wrap items-center gap-3">
          {/* LLM Engine Toggle */}
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900/80 border border-slate-800 text-xs text-slate-300 font-mono">
            <Cpu className="w-3.5 h-3.5 text-cyan-400" />
            <span>LLM:</span>
            <select
              value={llmProvider}
              onChange={(e) => setLlmProvider(e.target.value)}
              className="bg-transparent text-cyan-300 font-semibold focus:outline-none cursor-pointer"
            >
              <option value="offline" className="bg-slate-900 text-slate-200">Offline Engine (Zero-Key)</option>
              <option value="gemini" className="bg-slate-900 text-slate-200">Google Gemini 2.5</option>
              <option value="openai" className="bg-slate-900 text-slate-200">OpenAI / Ollama</option>
            </select>
          </div>

          {/* 1-Click Demo Trigger */}
          <button
            onClick={onLaunchDemo}
            disabled={isRunning}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-xs transition-all duration-200 ${
              isRunning
                ? "bg-slate-800 text-slate-500 cursor-not-allowed"
                : "bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white shadow-lg shadow-cyan-500/25 hover:shadow-cyan-500/40 transform hover:-translate-y-0.5 active:translate-y-0"
            }`}
          >
            {isRunning ? (
              <RefreshCw className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <Sparkles className="w-3.5 h-3.5" />
            )}
            <span>{isRunning ? "Agent Swarm Active..." : "Run Demo Project"}</span>
          </button>

          {/* New Project / Snippet */}
          <button
            onClick={onOpenNewProject}
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 text-xs font-medium text-slate-200 transition-colors"
          >
            <FileCode className="w-3.5 h-3.5 text-cyan-400" />
            <span>Analyze Code</span>
          </button>

          {/* Export Patch */}
          <button
            onClick={onExportPatch}
            disabled={!activeRun || !activeRun.fixes_verified_count}
            title="Download PR-ready Unified Fix Patch"
            className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium transition-colors border ${
              activeRun && activeRun.fixes_verified_count
                ? "bg-emerald-950/40 hover:bg-emerald-900/40 border-emerald-700/60 text-emerald-300"
                : "bg-slate-900/40 border-slate-800 text-slate-600 cursor-not-allowed"
            }`}
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export PR Patch</span>
          </button>

          {/* Download Report */}
          <button
            onClick={onDownloadReport}
            disabled={!activeRun}
            title="Export Technical Audit Report"
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-slate-800/60 hover:bg-slate-700/60 border border-slate-700 text-xs font-medium text-slate-300 transition-colors"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Report (HTML)</span>
          </button>
        </div>
      </div>
    </header>
  );
}
