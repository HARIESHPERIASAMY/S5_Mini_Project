import React, { useState } from 'react';
import { MessageSquareDiff, Scale, ArrowRight, ChevronDown, ChevronUp, ShieldCheck } from 'lucide-react';

export default function AgentDebatePanel({ debates = [], consensusScore = 96 }) {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <div className="card-surface p-4 sm:p-5 bg-white border border-[#E3E8F0] rounded-2xl flex flex-col shadow-xs">
      {/* Header with Accordion Toggle & Consensus Score */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-3 border-b border-[#E3E8F0] gap-3">
        <div
          onClick={() => setIsOpen(!isOpen)}
          className="flex items-center gap-2 cursor-pointer select-none"
        >
          <MessageSquareDiff className="w-4 h-4 text-[#7C3AED]" />
          <h3 className="text-xs sm:text-sm font-heading font-bold text-[#0F172A] tracking-wider uppercase font-mono">
            Critic Agent & Multi-Agent Debate
          </h3>
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-[#F1EAFE] text-[#6D28D9] font-mono border border-[#D9D6FE]">
            {debates.length} Audit Rounds
          </span>
          <button className="text-[#5B6577] hover:text-[#0F172A] ml-1 p-0.5 rounded">
            {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
        </div>

        {/* Swarm Consensus Meter */}
        <div className="flex items-center gap-2.5 font-mono text-xs">
          <Scale className="w-3.5 h-3.5 text-[#2563EB]" />
          <span className="text-[#5B6577]">Swarm Consensus:</span>
          <span className="text-[#16A34A] font-bold">{consensusScore}%</span>
          <div className="w-20 bg-[#E2E8F0] rounded-full h-1.5 overflow-hidden">
            <div
              className="bg-[#16A34A] h-1.5 rounded-full transition-all duration-500"
              style={{ width: `${Math.min(100, Math.max(0, consensusScore))}%` }}
            />
          </div>
        </div>
      </div>

      {/* Collapsible Content */}
      {isOpen && (
        <div className="mt-4 space-y-3.5">
          {debates.length === 0 ? (
            <div className="flex flex-col items-center justify-center p-6 text-[#8E9BAE] text-xs font-mono text-center">
              <ShieldCheck className="w-8 h-8 text-[#CBD5E1] mb-2" />
              <span>No debate rounds active yet. When agents identify bugs, the Critic will audit them here.</span>
            </div>
          ) : (
            debates.map((item, idx) => (
              <div
                key={idx}
                className="p-4 rounded-xl bg-[#FAFBFD] border border-[#E3E8F0] font-mono text-xs space-y-2.5"
              >
                {/* Round Header & Agreement Verdict */}
                <div className="flex items-center justify-between pb-2 border-b border-[#E3E8F0]">
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded-md bg-[#F1EAFE] border border-[#D9D6FE] text-[#6D28D9] text-[10px] font-bold">
                      Round #{item.round_num || idx + 1}
                    </span>
                    <span className="text-[#0F172A] font-bold flex items-center gap-1.5">
                      <span className="text-[#2563EB]">@{item.agent_from}</span>
                      <ArrowRight className="w-3 h-3 text-[#CBD5E1]" />
                      <span className="text-[#7C3AED]">@{item.agent_to}</span>
                    </span>
                  </div>
                  <span className="text-[10px] px-2.5 py-0.5 rounded-full bg-[#E7F8EE] border border-[#A6F4C5] text-[#14753B] font-bold">
                    Agreement: {Math.round((item.agreement_score || 0.95) * 100)}%
                  </span>
                </div>

                {/* Message Thread Bubbles */}
                <div className="space-y-2 text-[11px] leading-relaxed">
                  {/* Claim */}
                  <div className="p-3 rounded-lg bg-white border border-[#E3E8F0]">
                    <span className="text-[#2563EB] font-bold block mb-1">
                      @{item.agent_from} Claim:
                    </span>
                    <p className="text-[#0F172A]">{item.claim}</p>
                  </div>

                  {/* Rebuttal */}
                  <div className="p-3 rounded-lg bg-[#FFF4E0] border border-[#FEDF89]">
                    <span className="text-[#9A5B00] font-bold block mb-1">
                      @{item.agent_to} Critic Audit:
                    </span>
                    <p className="text-[#0F172A]">{item.rebuttal}</p>
                  </div>

                  {/* Resolution */}
                  <div className="p-3 rounded-lg bg-[#E7F8EE] border border-[#A6F4C5]">
                    <span className="text-[#14753B] font-bold block mb-1">
                      Consensus Resolution:
                    </span>
                    <p className="text-[#14753B] font-semibold">{item.resolution}</p>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
