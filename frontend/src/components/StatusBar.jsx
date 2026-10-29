import React, { useState } from 'react';
import { Copy, Check, Clock } from 'lucide-react';

export default function StatusBar({
  isConnected = true,
  runId,
  lastUpdated,
  status = "idle"
}) {
  const [copiedRun, setCopiedRun] = useState(false);

  const handleCopyRunId = () => {
    if (!runId) return;
    navigator.clipboard.writeText(runId);
    setCopiedRun(true);
    setTimeout(() => setCopiedRun(false), 2000);
  };

  return (
    <footer className="sticky bottom-0 z-40 bg-white/95 backdrop-blur-md border-t border-[#E3E8F0] px-4 py-2 text-xs font-mono text-[#5B6577] shadow-xs">
      <div className="max-w-[1440px] mx-auto flex flex-wrap items-center justify-between gap-3">
        {/* Left: Backend Connection Indicator */}
        <div className="flex items-center gap-2">
          {isConnected ? (
            <span className="flex items-center gap-1.5 text-[#14753B] font-semibold">
              <span className="w-2 h-2 rounded-full bg-[#16A34A] animate-pulse" />
              <span>Backend Connected</span>
            </span>
          ) : (
            <span className="flex items-center gap-1.5 text-[#B42318] font-semibold">
              <span className="w-2 h-2 rounded-full bg-[#DC2626]" />
              <span>Reconnecting Stream...</span>
            </span>
          )}
          <span className="text-[#CBD5E1] hidden sm:inline">|</span>
          <span className="hidden sm:inline text-[#5B6577]">
            Status: <strong className="text-[#0F172A] uppercase">{status}</strong>
          </span>
        </div>

        {/* Center: Active Run ID */}
        <div className="flex items-center gap-2">
          {runId ? (
            <div className="flex items-center gap-1.5 bg-[#F1F5F9] px-2 py-0.5 rounded border border-[#E2E8F0]">
              <span className="text-[#5B6577] text-[11px]">Run ID:</span>
              <span className="font-bold text-[#0F172A]">{runId.slice(0, 16)}...</span>
              <button
                onClick={handleCopyRunId}
                title="Copy full Run ID"
                className="hover:text-[#0F172A] p-0.5 text-[#5B6577] cursor-pointer"
              >
                {copiedRun ? <Check className="w-3 h-3 text-[#16A34A]" /> : <Copy className="w-3 h-3" />}
              </button>
            </div>
          ) : (
            <span className="text-[#8E9BAE] text-[11px]">No active run</span>
          )}
        </div>

        {/* Right: Last Updated Time & Protocol */}
        <div className="flex items-center gap-3 text-[11px]">
          <span className="flex items-center gap-1">
            <Clock className="w-3 h-3 text-[#8E9BAE]" />
            <span>Updated: {lastUpdated ? new Date(lastUpdated).toLocaleTimeString() : 'Just now'}</span>
          </span>
          <span className="text-[#CBD5E1] hidden sm:inline">|</span>
          <span className="hidden sm:inline text-[#8E9BAE]">
            Protocol: WebSocket 1.0 (WAL-safe)
          </span>
        </div>
      </div>
    </footer>
  );
}
