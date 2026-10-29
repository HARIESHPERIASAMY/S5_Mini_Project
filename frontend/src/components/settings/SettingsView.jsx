import React, { useState } from 'react';
import { 
  Settings as SettingsIcon, Sliders, Moon, Sun, 
  Shield, CheckCircle2, AlertCircle, Info, Clock, DollarSign
} from 'lucide-react';

export default function SettingsView({
  llmProvider,
  onSelectProvider,
  theme = "light",
  onToggleTheme
}) {
  const [severityThreshold, setSeverityThreshold] = useState("ALL");
  const [sandboxTimeout, setSandboxTimeout] = useState("30");
  const [autoVerify, setAutoVerify] = useState(true);

  // 9 cooperating agents
  const swarmAgents = [
    { id: "orchestrator", name: "Orchestrator", desc: "Coordinates swarm state DAG and pipeline execution", enabled: true },
    { id: "static_analysis", name: "Static Analysis", desc: "AST parser and security smell detection", enabled: true },
    { id: "test_generation", name: "Test Generation", desc: "Synthesizes boundary and property-based test cases", enabled: true },
    { id: "test_execution", name: "Test Execution", desc: "Executes test runner in isolated environment", enabled: true },
    { id: "bug_classification", name: "Bug Classification", desc: "Categorizes and deduplicates defect reports", enabled: true },
    { id: "root_cause", name: "Root Cause", desc: "Traces AST causal chains and failure triggers", enabled: true },
    { id: "auto_fix", name: "Auto-Fix Engine", desc: "Generates unified diff patches", enabled: true },
    { id: "critic", name: "Critic Reviewer", desc: "Evaluates patch validity and consensus", enabled: true },
    { id: "report", name: "Report Agent", desc: "Exports technical audits and receipts", enabled: true },
  ];

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div className="sm-card p-5 bg-white border border-[#E2E8F0] rounded-xl shadow-xs">
        <div className="flex items-center gap-2">
          <SettingsIcon className="w-4 h-4 text-[#2457F5]" />
          <h3 className="font-heading font-extrabold text-[#0F172A] text-lg">
            Platform Engine & Swarm Configuration
          </h3>
        </div>
        <p className="text-xs text-[#64748B] mt-0.5">
          Manage local engine parameters, LLM model connections, sandbox timeouts, and dashboard presentation.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* 1. Swarm Execution & LLM Engine */}
        <div className="sm-card p-5 bg-white border border-[#E2E8F0] rounded-xl shadow-xs space-y-4">
          <strong className="font-heading text-sm text-[#0F172A] block">
            LLM Provider & Engine
          </strong>

          <div>
            <label className="block text-xs font-bold text-[#0F172A] mb-1">Active Swarm Intelligence</label>
            <select
              value={llmProvider}
              onChange={(e) => onSelectProvider(e.target.value)}
              className="w-full h-9 px-3 text-xs bg-[#F8FAFC] border border-[#E2E8F0] rounded-lg font-semibold focus:outline-none focus:border-[#2457F5]"
            >
              <option value="offline">Offline Engine (Zero-Key Local Fallback)</option>
              <option value="gemini">Google Gemini 2.5 Flash</option>
              <option value="openai">OpenAI / Ollama Local Server</option>
            </select>
            <span className="text-[11px] text-[#64748B] mt-1 block">
              Offline engine uses deterministic AST heuristics without external network calls.
            </span>
          </div>

          <div>
            <label className="block text-xs font-bold text-[#0F172A] mb-1">Sandbox Execution Timeout</label>
            <div className="flex items-center gap-2">
              <input
                type="number"
                value={sandboxTimeout}
                onChange={(e) => setSandboxTimeout(e.target.value)}
                min="10"
                max="120"
                className="w-24 h-9 px-3 text-xs bg-[#F8FAFC] border border-[#E2E8F0] rounded-lg font-mono focus:outline-none focus:border-[#2457F5]"
              />
              <span className="text-xs text-[#64748B]">seconds per regression test</span>
            </div>
          </div>

          <div className="pt-2 border-t border-[#E2E8F0]">
            <label className="flex items-center gap-2 text-xs text-[#0F172A] cursor-pointer">
              <input
                type="checkbox"
                checked={autoVerify}
                onChange={(e) => setAutoVerify(e.target.checked)}
                className="rounded border-[#CBD5E1] text-[#2457F5]"
              />
              <span>Auto-verify proposed patches in sandbox regression suite</span>
            </label>
          </div>
        </div>

        {/* 2. Presentation & Telemetry Cost Breakdown */}
        <div className="sm-card p-5 bg-white border border-[#E2E8F0] rounded-xl shadow-xs space-y-4">
          <strong className="font-heading text-sm text-[#0F172A] block">
            Interface Theme & Telemetry Costs
          </strong>

          {/* Theme Toggle */}
          <div>
            <label className="block text-xs font-bold text-[#0F172A] mb-1">Dashboard Theme</label>
            <div className="flex items-center gap-2">
              <button
                onClick={() => onToggleTheme && onToggleTheme("light")}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-semibold cursor-pointer ${
                  theme === "light"
                    ? "bg-[#2457F5] text-white border-[#2457F5]"
                    : "bg-white text-[#64748B] border-[#E2E8F0]"
                }`}
              >
                <Sun className="w-3.5 h-3.5" />
                <span>Light Theme (Standard)</span>
              </button>

              <button
                onClick={() => onToggleTheme && onToggleTheme("dark")}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-semibold cursor-pointer ${
                  theme === "dark"
                    ? "bg-[#2457F5] text-white border-[#2457F5]"
                    : "bg-white text-[#64748B] border-[#E2E8F0]"
                }`}
              >
                <Moon className="w-3.5 h-3.5" />
                <span>Dark Theme</span>
              </button>
            </div>
          </div>

          {/* Token & Run Cost Breakdown */}
          <div>
            <label className="block text-xs font-bold text-[#0F172A] mb-1">Token & Resource Cost Audit</label>
            <div className="p-3 rounded-lg bg-[#FAFBFD] border border-[#E2E8F0] text-xs font-mono space-y-1.5 text-[#64748B]">
              <div className="flex justify-between">
                <span>Prompt Tokens:</span>
                <span className="text-[#94A3B8]">Not available (Offline engine)</span>
              </div>
              <div className="flex justify-between">
                <span>Completion Tokens:</span>
                <span className="text-[#94A3B8]">Not available (Offline engine)</span>
              </div>
              <div className="flex justify-between">
                <span>Estimated Cost:</span>
                <strong className="text-[#16A34A]">$0.00 (Zero-Key Offline)</strong>
              </div>
            </div>
            <span className="text-[10px] text-[#94A3B8] font-mono mt-1 block">
              Token metrics are enabled when connected to cloud Gemini / OpenAI endpoints.
            </span>
          </div>
        </div>
      </div>

      {/* 3. Swarm Agents Activation Matrix */}
      <div className="sm-card p-5 bg-white border border-[#E2E8F0] rounded-xl shadow-xs space-y-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
          <div>
            <strong className="font-heading text-sm text-[#0F172A] block">
              Participating Swarm Agents (9 Active)
            </strong>
            <p className="text-xs text-[#64748B]">
              Individual agents can be audited. Pipeline execution runs all 9 agents sequentially.
            </p>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-[#FFF4E0] text-[#9A5B00] border border-[#FEDF89] font-bold">
            Agent subset execution: Not supported yet by backend
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {swarmAgents.map((ag) => (
            <div key={ag.id} className="p-3 rounded-lg border border-[#E2E8F0] bg-[#FAFBFD] flex items-start gap-2.5 text-xs">
              <CheckCircle2 className="w-4 h-4 text-[#16A34A] flex-shrink-0 mt-0.5" />
              <div>
                <strong className="text-[#0F172A] block">{ag.name}</strong>
                <span className="text-[11px] text-[#64748B] leading-tight block mt-0.5">{ag.desc}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
