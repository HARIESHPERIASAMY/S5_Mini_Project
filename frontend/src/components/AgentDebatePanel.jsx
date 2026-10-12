import React from 'react';
import { MessageSquareDiff, CheckCircle, ShieldCheck, Scale, ArrowRight } from 'lucide-react';

export default function AgentDebatePanel({ debates = [], consensusScore = 95 }) {
  return (
    <div className="glass-panel rounded-2xl p-5 border border-slate-800 flex flex-col">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-3 pb-4 border-b border-mesh-border mb-4">
        <div className="flex items-center gap-2">
          <MessageSquareDiff className="w-4 h-4 text-violet-400" />
          <h3 className="text-sm font-semibold text-white tracking-wide uppercase font-mono">
            Critic Audit & Multi-Agent Debate Ledger
          </h3>
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 font-mono">
            {debates.length} Audit Rounds
          </span>
        </div>

        {/* Consensus Meter */}
        <div className="flex items-center gap-2 font-mono text-xs">
          <Scale className="w-3.5 h-3.5 text-cyan-400" />
          <span className="text-slate-400">Swarm Consensus:</span>
          <span className="text-emerald-400 font-bold">{consensusScore}%</span>
          <div className="w-20 bg-slate-800 rounded-full h-1.5 overflow-hidden">
            <div
              className="bg-gradient-to-r from-emerald-500 to-cyan-400 h-1.5 rounded-full"
              style={{ width: `${Math.min(100, consensusScore)}%` }}
            />
          </div>
        </div>
      </div>

      {/* Debates Feed */}
      {debates.length === 0 ? (
        <div className="flex flex-col items-center justify-center p-8 text-slate-500 text-xs font-mono">
          <span>No debate rounds active yet. When agents identify bugs, the Critic will challenge them here.</span>
        </div>
      ) : (
        <div className="space-y-3">
          {debates.map((item, idx) => (
            <div
              key={idx}
              className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-violet-500/40 transition-colors font-mono text-xs"
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 rounded bg-violet-950/80 border border-violet-800/80 text-violet-300 text-[10px] font-bold">
                    Round #{item.round_num || idx + 1}
                  </span>
                  <span className="text-slate-400 font-bold flex items-center gap-1">
                    <span>@{item.agent_from}</span>
                    <ArrowRight className="w-3 h-3 text-slate-600" />
                    <span>@{item.agent_to}</span>
                  </span>
                </div>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-950/60 border border-emerald-800 text-emerald-300">
                  Agreement: {Math.round((item.agreement_score || 0.95) * 100)}%
                </span>
              </div>

              <div className="space-y-1.5 text-[11px]">
                <div className="p-2 rounded bg-slate-950/60 text-slate-300">
                  <span className="text-cyan-400 font-bold mr-1">Claim:</span>
                  {item.claim}
                </div>
                <div className="p-2 rounded bg-amber-950/20 border border-amber-900/30 text-amber-200">
                  <span className="text-amber-400 font-bold mr-1">Critic Audit:</span>
                  {item.rebuttal}
                </div>
                <div className="p-2 rounded bg-emerald-950/20 border border-emerald-900/30 text-emerald-300">
                  <span className="text-emerald-400 font-bold mr-1">Resolution:</span>
                  {item.resolution}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
