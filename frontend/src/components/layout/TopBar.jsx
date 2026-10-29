import React, { useState, useRef, useEffect } from 'react';
import { 
  Download, FileCode, Sliders, ChevronDown, 
  Bot, GitPullRequest, FileText, Shield
} from 'lucide-react';

export default function TopBar({
  activeViewTitle = "Overview",
  projectName = "demo-shop",
  mainFile = "main.py",
  llmProvider = "offline",
  onSelectProvider,
  onOpenAnalyzeCode,
  onExportPatch,
  onDownloadReport,
  onExportSarif,
  onExportJUnit,
  onExportPatchZip,
  onOpenCompare,
  onToggleAssistant,
  isAssistantOpen = false,
  _runId,
  _runsList = []
}) {
  const [exportOpen, setExportOpen] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const exportRef = useRef(null);
  const settingsRef = useRef(null);

  // Close dropdowns on outside click
  useEffect(() => {
    function handleClickOutside(e) {
      if (exportRef.current && !exportRef.current.contains(e.target)) {
        setExportOpen(false);
      }
      if (settingsRef.current && !settingsRef.current.contains(e.target)) {
        setSettingsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const providerLabel = {
    offline: "Offline Engine (Zero-Key)",
    gemini: "Gemini 2.5",
    openai: "OpenAI / Ollama"
  }[llmProvider] || llmProvider;

  return (
    <header className="h-16 bg-white border-b border-[#E2E8F0] px-4 sm:px-6 flex items-center justify-between gap-4 sticky top-0 z-20">
      {/* Left Title & Project Context */}
      <div className="flex items-center gap-3 min-w-0">
        <div>
          <h1 className="text-lg font-heading font-extrabold text-[#0F172A] tracking-tight capitalize leading-none">
            {activeViewTitle}
          </h1>
          <p className="text-xs text-[#64748B] mt-1 truncate">
            Project: <strong className="text-[#0F172A] font-semibold">{projectName}</strong> · {mainFile} · {providerLabel}
          </p>
        </div>
      </div>

      {/* Right Controls Bar */}
      <div className="flex items-center gap-2 sm:gap-2.5">
        {/* Comparison Dropdown / Pill */}
        <button
          onClick={onOpenCompare}
          className="hidden md:flex items-center gap-1.5 px-3 h-9 rounded-lg bg-[#F8FAFC] hover:bg-[#F1F5F9] border border-[#E2E8F0] text-xs font-medium text-[#0F172A] transition-colors cursor-pointer"
        >
          <span>Compare runs</span>
        </button>

        {/* Run Settings Popover Trigger (Contains Model & Severity) */}
        <div className="relative" ref={settingsRef}>
          <button
            onClick={() => setSettingsOpen(!settingsOpen)}
            title="Configure LLM model and sandbox settings"
            className="flex items-center gap-1.5 px-3 h-9 rounded-lg bg-[#F8FAFC] hover:bg-[#F1F5F9] border border-[#E2E8F0] text-xs font-medium text-[#0F172A] transition-colors cursor-pointer"
          >
            <Sliders className="w-3.5 h-3.5 text-[#64748B]" />
            <span className="hidden sm:inline">Run settings</span>
            <ChevronDown className="w-3 h-3 text-[#64748B]" />
          </button>

          {/* Settings Popover Dropdown */}
          {settingsOpen && (
            <div className="absolute right-0 mt-2 w-72 bg-white rounded-xl border border-[#E2E8F0] shadow-lg p-4 text-xs z-50 space-y-3">
              <div className="font-heading font-bold text-[#0F172A] pb-2 border-b border-[#E2E8F0] flex items-center justify-between">
                <span>Run Settings</span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#EEF2FF] text-[#2457F5] font-semibold">
                  Active
                </span>
              </div>

              <div>
                <label className="block text-[#64748B] font-medium mb-1">LLM Engine</label>
                <select
                  value={llmProvider}
                  onChange={(e) => {
                    onSelectProvider(e.target.value);
                    setSettingsOpen(false);
                  }}
                  className="w-full h-8 px-2.5 bg-[#F8FAFC] border border-[#E2E8F0] rounded-lg text-xs font-semibold text-[#0F172A] focus:outline-none focus:border-[#2457F5]"
                >
                  <option value="offline">Offline Engine (Zero-Key)</option>
                  <option value="gemini">Google Gemini 2.5</option>
                  <option value="openai">OpenAI / Ollama</option>
                </select>
              </div>

              <div>
                <label className="block text-[#64748B] font-medium mb-1">Severity Filter</label>
                <select className="w-full h-8 px-2.5 bg-[#F8FAFC] border border-[#E2E8F0] rounded-lg text-xs font-semibold text-[#0F172A]">
                  <option value="ALL">All Severities</option>
                  <option value="HIGH_CRITICAL">Critical & High Only</option>
                </select>
              </div>

              <div>
                <label className="block text-[#64748B] font-medium mb-1">Sandbox Execution Timeout</label>
                <input
                  type="text"
                  defaultValue="30 seconds"
                  readOnly
                  className="w-full h-8 px-2.5 bg-[#F8FAFC] border border-[#E2E8F0] rounded-lg text-xs text-[#64748B]"
                />
              </div>
            </div>
          )}
        </div>

        {/* Single "Export ▾" Dropdown */}
        <div className="relative" ref={exportRef}>
          <button
            onClick={() => setExportOpen(!exportOpen)}
            className="flex items-center gap-1.5 px-3 h-9 rounded-lg bg-white hover:bg-[#F8FAFC] border border-[#E2E8F0] text-xs font-semibold text-[#0F172A] transition-colors cursor-pointer"
          >
            <span>Export</span>
            <ChevronDown className="w-3 h-3 text-[#64748B]" />
          </button>

          {exportOpen && (
            <div className="absolute right-0 mt-2 w-56 bg-white rounded-xl border border-[#E2E8F0] shadow-lg py-1.5 text-xs z-50 divide-y divide-[#F1F5F9]">
              <div className="py-1">
                <button
                  onClick={() => {
                    onExportPatch?.();
                    setExportOpen(false);
                  }}
                  className="w-full text-left px-3.5 py-2 hover:bg-[#F8FAFC] text-[#0F172A] flex items-center gap-2 cursor-pointer"
                >
                  <GitPullRequest className="w-3.5 h-3.5 text-[#16A34A]" />
                  <span>PR Patch (.patch)</span>
                </button>
                <button
                  onClick={() => {
                    onDownloadReport?.();
                    setExportOpen(false);
                  }}
                  className="w-full text-left px-3.5 py-2 hover:bg-[#F8FAFC] text-[#0F172A] flex items-center gap-2 cursor-pointer"
                >
                  <FileText className="w-3.5 h-3.5 text-[#2457F5]" />
                  <span>Technical Report (HTML)</span>
                </button>
                <button
                  onClick={() => {
                    window.print();
                    setExportOpen(false);
                  }}
                  className="w-full text-left px-3.5 py-2 hover:bg-[#F8FAFC] text-[#0F172A] flex items-center gap-2 cursor-pointer"
                >
                  <Download className="w-3.5 h-3.5 text-[#7C3AED]" />
                  <span>Executive Summary (PDF)</span>
                </button>
              </div>

              <div className="py-1">
                <button
                  onClick={() => {
                    onExportSarif?.();
                    setExportOpen(false);
                  }}
                  className="w-full text-left px-3.5 py-2 hover:bg-[#F8FAFC] text-[#0F172A] flex items-center gap-2 cursor-pointer"
                >
                  <Shield className="w-3.5 h-3.5 text-[#1D4ED8]" />
                  <span>OASIS SARIF 2.1.0 (.sarif)</span>
                </button>
                <button
                  onClick={() => {
                    onExportJUnit?.();
                    setExportOpen(false);
                  }}
                  className="w-full text-left px-3.5 py-2 hover:bg-[#F8FAFC] text-[#0F172A] flex items-center gap-2 cursor-pointer"
                >
                  <FileCode className="w-3.5 h-3.5 text-[#16A34A]" />
                  <span>JUnit XML Test Results (.xml)</span>
                </button>
                <button
                  onClick={() => {
                    onExportPatchZip?.();
                    setExportOpen(false);
                  }}
                  className="w-full text-left px-3.5 py-2 hover:bg-[#F8FAFC] text-[#0F172A] flex items-center gap-2 cursor-pointer"
                >
                  <Download className="w-3.5 h-3.5 text-[#D97706]" />
                  <span>Patch Bundle Archive (.zip)</span>
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Primary Action Button: "Analyze code" */}
        <button
          onClick={onOpenAnalyzeCode}
          className="flex items-center gap-1.5 px-4 h-9 rounded-lg bg-[#2457F5] hover:bg-[#1A44D4] text-white text-xs font-semibold shadow-xs transition-all cursor-pointer"
        >
          <FileCode className="w-3.5 h-3.5" />
          <span>Analyze code</span>
        </button>

        {/* Assistant Toggle Button */}
        <button
          onClick={onToggleAssistant}
          className={`flex items-center gap-1.5 px-3 h-9 rounded-lg border text-xs font-semibold transition-all cursor-pointer ${
            isAssistantOpen
              ? "bg-[#EEF2FF] border-[#2457F5] text-[#2457F5]"
              : "bg-white hover:bg-[#F8FAFC] border-[#E2E8F0] text-[#0F172A]"
          }`}
          title="Open Mesh Assistant Chatbot"
        >
          <Bot className="w-3.5 h-3.5 text-[#2457F5]" />
          <span className="hidden xl:inline">Mesh Assistant</span>
        </button>
      </div>
    </header>
  );
}

