import React, { useState } from 'react';
import { 
  Shield, Sparkles, Upload, FileCode2, 
  Settings, ArrowRight, CheckCircle2, AlertCircle, 
  RefreshCw, Terminal
} from 'lucide-react';

const GitRepoIcon = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22" />
  </svg>
);

export default function StartScreen({
  onLaunchDemo,
  onSubmitSnippet,
  onUploadZip,
  llmProvider,
  onSelectProvider,
  isRunning = false
}) {
  const [activeTab, setActiveTab] = useState("demo"); // "demo" | "snippet" | "upload" | "github"
  const [projectName, setProjectName] = useState("my-python-app");
  const [snippetCode, setSnippetCode] = useState(
`def calculate_discount(price, total):
    # Potential edge-case defect at boundary threshold
    if total > 100:
        return price * 0.90
    return price
`
  );
  const [selectedFile, setSelectedFile] = useState(null);
  const [showSettingsPopover, setShowSettingsPopover] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);

  // Detected framework derived from snippet content
  const detectedLanguage = "Python 3.11";
  const detectedFramework = snippetCode.includes("def test_") ? "pytest / unittest" : "pytest (default)";

  const handleSnippetSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage(null);
    try {
      await onSubmitSnippet(projectName, snippetCode);
    } catch (err) {
      setErrorMessage(err.message || "Failed to analyze code snippet");
    }
  };

  const handleFileUpload = async (e) => {
    e.preventDefault();
    if (!selectedFile) {
      setErrorMessage("Please select a .zip file to upload.");
      return;
    }
    setErrorMessage(null);
    try {
      await onUploadZip(projectName, selectedFile);
    } catch (err) {
      setErrorMessage(err.message || "Failed to upload repository zip");
    }
  };

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 space-y-6">
      {/* 1. Hero Header */}
      <div className="text-center space-y-2">
        <div className="w-12 h-12 rounded-xl bg-[#EEF2FF] text-[#2457F5] flex items-center justify-center mx-auto shadow-xs border border-[#2457F5]/20">
          <Shield className="w-6 h-6" />
        </div>
        <h1 className="text-2xl sm:text-3xl font-heading font-extrabold text-[#0F172A] tracking-tight">
          SentinelMesh Autonomous QA
        </h1>
        <p className="text-sm text-[#64748B] max-w-xl mx-auto">
          Multi-agent software testing, isolated boundary regression, and self-healing bug analysis platform.
        </p>
      </div>

      {/* 2. Main Input Card */}
      <div className="sm-card bg-white border border-[#E2E8F0] rounded-xl shadow-xs overflow-hidden">
        {/* Navigation Tabs */}
        <div className="flex items-center border-b border-[#E2E8F0] bg-[#F8FAFC] px-4 overflow-x-auto">
          {[
            { id: "demo", label: "Run Demo Project", icon: Sparkles },
            { id: "snippet", label: "Paste Code Snippet", icon: FileCode2 },
            { id: "upload", label: "Upload ZIP Archive", icon: Upload },
            { id: "github", label: "GitHub Repo URL", icon: GitRepoIcon, disabled: true, tag: "Offline" },
          ].map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => !tab.disabled && setActiveTab(tab.id)}
                disabled={tab.disabled}
                className={`flex items-center gap-2 px-4 py-3 text-xs font-semibold border-b-2 whitespace-nowrap transition-all cursor-pointer ${
                  activeTab === tab.id
                    ? "border-[#2457F5] text-[#2457F5] bg-white"
                    : tab.disabled
                    ? "border-transparent text-[#94A3B8] cursor-not-allowed opacity-60"
                    : "border-transparent text-[#64748B] hover:text-[#0F172A]"
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{tab.label}</span>
                {tab.tag && (
                  <span className="text-[9px] font-mono px-1.5 py-0.2 rounded bg-[#F1F5F9] text-[#64748B] border border-[#CBD5E1]">
                    {tab.tag}
                  </span>
                )}
              </button>
            );
          })}

          {/* Settings Button */}
          <div className="ml-auto pl-2 relative">
            <button
              onClick={() => setShowSettingsPopover(!showSettingsPopover)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-[#E2E8F0] hover:bg-white text-xs font-medium text-[#64748B] hover:text-[#0F172A] cursor-pointer"
            >
              <Settings className="w-3.5 h-3.5" />
              <span>Run Settings</span>
            </button>

            {/* Run Settings Popover */}
            {showSettingsPopover && (
              <div className="absolute right-0 top-10 w-72 bg-white border border-[#E2E8F0] rounded-xl shadow-lg p-4 z-30 space-y-3 text-xs font-sans">
                <div className="flex items-center justify-between pb-2 border-b border-[#E2E8F0]">
                  <strong className="font-heading text-[#0F172A]">Run Execution Settings</strong>
                  <button onClick={() => setShowSettingsPopover(false)} className="text-[#64748B] hover:text-[#0F172A]">✕</button>
                </div>

                <div>
                  <label className="block text-[#64748B] font-medium mb-1">LLM Swarm Engine</label>
                  <select
                    value={llmProvider}
                    onChange={(e) => onSelectProvider(e.target.value)}
                    className="w-full h-8 px-2 bg-[#F8FAFC] border border-[#E2E8F0] rounded-lg font-semibold"
                  >
                    <option value="offline">Offline Engine (Zero-Key Local)</option>
                    <option value="gemini">Google Gemini 2.5</option>
                    <option value="openai">OpenAI / Ollama</option>
                  </select>
                </div>

                <div>
                  <div className="flex items-center justify-between text-[#64748B] mb-1">
                    <span className="font-medium">Sandbox Timeout</span>
                    <span className="text-[10px] font-mono text-[#94A3B8]">Backend default</span>
                  </div>
                  <input type="text" readOnly defaultValue="30 seconds" className="w-full h-8 px-2 bg-[#F8FAFC] border border-[#E2E8F0] rounded-lg text-[#64748B]" />
                </div>

                <div className="pt-2 border-t border-[#E2E8F0] text-[10px] font-mono text-[#94A3B8]">
                  <span>Custom agent subsets: Not supported yet by backend</span>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Tab Viewports */}
        <div className="p-6">
          {errorMessage && (
            <div className="mb-4 p-3 rounded-lg bg-[#FEECEC] border border-[#FECDCA] text-[#B42318] text-xs flex items-center gap-2 font-medium">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{errorMessage}</span>
            </div>
          )}

          {/* TAB 1: RUN DEMO PROJECT */}
          {activeTab === "demo" && (
            <div className="space-y-5 text-center max-w-lg mx-auto py-4">
              <div className="space-y-2">
                <h3 className="text-base font-heading font-extrabold text-[#0F172A]">
                  Pre-Packaged Regression: demo-shop
                </h3>
                <p className="text-xs text-[#64748B] leading-relaxed">
                  Includes pricing rules, threshold discount calculations, inventory balance checks, and unit tests designed to demonstrate boundary failures and self-healing.
                </p>
              </div>

              <div className="p-3 bg-[#F8FAFC] rounded-xl border border-[#E2E8F0] text-xs font-mono text-left space-y-1.5 text-[#475569]">
                <div className="flex justify-between">
                  <span>Detected Environment:</span>
                  <strong className="text-[#0F172A]">Python 3.11 / pytest</strong>
                </div>
                <div className="flex justify-between">
                  <span>Modules Monitored:</span>
                  <strong className="text-[#0F172A]">main.py, pricing.py, utils.py</strong>
                </div>
                <div className="flex justify-between">
                  <span>Swarm Engine:</span>
                  <strong className="text-[#2457F5]">{llmProvider === 'offline' ? 'Offline Rule Engine' : llmProvider}</strong>
                </div>
              </div>

              <button
                onClick={onLaunchDemo}
                disabled={isRunning}
                className="w-full flex items-center justify-center gap-2 h-11 rounded-lg bg-[#2457F5] hover:bg-[#1A44D4] disabled:opacity-60 text-white text-xs font-semibold shadow-xs transition-all cursor-pointer"
              >
                {isRunning ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span>Executing Swarm Pipeline...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    <span>Launch Demo Project Analysis</span>
                  </>
                )}
              </button>
            </div>
          )}

          {/* TAB 2: PASTE CODE SNIPPET */}
          {activeTab === "snippet" && (
            <form onSubmit={handleSnippetSubmit} className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-bold text-[#0F172A] mb-1">Project Name</label>
                  <input
                    type="text"
                    value={projectName}
                    onChange={(e) => setProjectName(e.target.value)}
                    required
                    className="w-full h-9 px-3 text-xs bg-[#F8FAFC] border border-[#E2E8F0] rounded-lg font-mono focus:outline-none focus:border-[#2457F5]"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-[#0F172A] mb-1">Detected Language</label>
                  <input
                    type="text"
                    readOnly
                    value={detectedLanguage}
                    className="w-full h-9 px-3 text-xs bg-[#F1F5F9] border border-[#E2E8F0] rounded-lg font-mono text-[#64748B]"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-[#0F172A] mb-1">Test Runner</label>
                  <input
                    type="text"
                    readOnly
                    value={detectedFramework}
                    className="w-full h-9 px-3 text-xs bg-[#F1F5F9] border border-[#E2E8F0] rounded-lg font-mono text-[#64748B]"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-[#0F172A] mb-1">
                  Python Source Code
                </label>
                <textarea
                  value={snippetCode}
                  onChange={(e) => setSnippetCode(e.target.value)}
                  rows={9}
                  required
                  className="w-full p-3 text-xs font-mono bg-[#0F172A] text-slate-100 border border-[#CBD5E1] rounded-lg focus:outline-none"
                />
              </div>

              <button
                type="submit"
                disabled={isRunning}
                className="w-full flex items-center justify-center gap-2 h-10 rounded-lg bg-[#2457F5] hover:bg-[#1A44D4] disabled:opacity-60 text-white text-xs font-semibold shadow-xs transition-all cursor-pointer"
              >
                {isRunning ? <RefreshCw className="w-4 h-4 animate-spin" /> : <PlaySquare className="w-4 h-4" />}
                <span>Analyze Custom Code Snippet</span>
              </button>
            </form>
          )}

          {/* TAB 3: UPLOAD ZIP ARCHIVE */}
          {activeTab === "upload" && (
            <form onSubmit={handleFileUpload} className="space-y-4 max-w-lg mx-auto py-2">
              <div>
                <label className="block text-xs font-bold text-[#0F172A] mb-1">Project Name</label>
                <input
                  type="text"
                  value={projectName}
                  onChange={(e) => setProjectName(e.target.value)}
                  required
                  className="w-full h-9 px-3 text-xs bg-[#F8FAFC] border border-[#E2E8F0] rounded-lg font-mono focus:outline-none focus:border-[#2457F5]"
                />
              </div>

              <div className="border-2 border-dashed border-[#CBD5E1] rounded-xl p-6 text-center space-y-2 bg-[#F8FAFC]">
                <Upload className="w-8 h-8 text-[#64748B] mx-auto" />
                <div className="text-xs font-medium text-[#0F172A]">
                  {selectedFile ? selectedFile.name : "Choose a project .zip archive"}
                </div>
                <p className="text-[11px] text-[#64748B]">
                  Must contain .py source files and optional pytest test files.
                </p>
                <input
                  type="file"
                  accept=".zip"
                  onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                  className="text-xs cursor-pointer"
                />
              </div>

              <button
                type="submit"
                disabled={isRunning || !selectedFile}
                className="w-full flex items-center justify-center gap-2 h-10 rounded-lg bg-[#2457F5] hover:bg-[#1A44D4] disabled:opacity-60 text-white text-xs font-semibold shadow-xs transition-all cursor-pointer"
              >
                {isRunning ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
                <span>Upload and Run Analysis</span>
              </button>
            </form>
          )}

          {/* TAB 4: GITHUB (Disabled in Offline Mode) */}
          {activeTab === "github" && (
            <div className="p-8 text-center space-y-2 max-w-md mx-auto">
              <Github className="w-8 h-8 text-[#94A3B8] mx-auto" />
              <h4 className="font-heading font-bold text-sm text-[#0F172A]">Direct Git Repository Clone</h4>
              <p className="text-xs text-[#64748B]">
                Direct GitHub URL cloning requires internet access and OAuth credentials.
                SentinelMesh is currently operating in 100% offline air-gapped mode.
              </p>
              <div className="pt-2 text-[11px] font-mono text-[#D97706] bg-[#FFF4E0] border border-[#FEDF89] p-2 rounded-lg">
                Status: Requires internet · See docs/needs-backend.md
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
