import React, { useState } from 'react';
import { Bot, Send, X, ExternalLink, GitPullRequest, Copy, Check, Sparkles } from 'lucide-react';
import { queryMeshAssistant } from '../../api/adapters';

export default function MeshAssistant({
  isOpen = true,
  onClose,
  runData,
  onSelectBug,
  onExportPatch,
  onShowDiff,
  pendingPrompt,
  onClearPendingPrompt
}) {
  const [messages, setMessages] = useState([
    {
      id: "m1",
      sender: "user",
      text: "Why did the discount test fail?"
    },
    {
      id: "m2",
      sender: "assistant",
      text: "The check at main.py:41 uses >, so an order equal to the threshold is skipped. The test builds exactly that case.",
      citations: [
        { label: "main.py:41", type: "file" },
        { label: "Critic debate", type: "debate" }
      ],
      actions: []
    },
    {
      id: "m3",
      sender: "user",
      text: "Is the fix safe to merge?"
    },
    {
      id: "m4",
      sender: "assistant",
      text: "Yes for this one. The sandbox re-run passed 14 of 14 tests and no other function calls it. The zero-check fix is still unverified.",
      citations: [],
      actions: ["Open PR", "Show diff"]
    }
  ]);
  const [inputText, setInputText] = useState("");
  const [copiedAction, setCopiedAction] = useState(false);

  useEffect(() => {
    if (pendingPrompt && pendingPrompt.trim()) {
      handleSend(pendingPrompt);
      if (onClearPendingPrompt) onClearPendingPrompt();
    }
  }, [pendingPrompt]);

  if (!isOpen) return null;

  const handleSend = (textToSend) => {
    const query = textToSend || inputText;
    if (!query.trim()) return;

    const userMsg = {
      id: `u_${Date.now()}`,
      sender: "user",
      text: query
    };

    const response = queryMeshAssistant(query, runData);
    const botMsg = {
      id: `a_${Date.now() + 1}`,
      sender: "assistant",
      text: response.text,
      citations: response.citations,
      actions: response.actions
    };

    setMessages((prev) => [...prev, userMsg, botMsg]);
    setInputText("");
  };

  const handleAction = (actionName) => {
    if (actionName === "Open PR") {
      onExportPatch && onExportPatch();
    } else if (actionName === "Show diff") {
      onShowDiff && onShowDiff();
    } else if (actionName === "Copy patch") {
      if (runData?.bugs?.[0]?.proposed_fix_diff) {
        navigator.clipboard.writeText(runData.bugs[0].proposed_fix_diff);
        setCopiedAction(true);
        setTimeout(() => setCopiedAction(false), 2000);
      }
    }
  };

  const quickPrompts = [
    "Explain like I'm a beginner",
    "Summarize this run",
    "Draft PR description",
    "What else could break?",
    "Why did the discount test fail?"
  ];

  return (
    <div className="w-80 sm:w-96 bg-white border-l border-[#E2E8F0] shadow-sm flex flex-col h-full z-20 flex-shrink-0 select-text">
      {/* Header */}
      <div className="h-16 px-4 border-b border-[#E2E8F0] flex items-center justify-between bg-white">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-[#EEF2FF] flex items-center justify-center text-[#2457F5] border border-[#2457F5]/20">
            <Bot className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-heading font-extrabold text-[#0F172A] text-xs sm:text-sm">
                Mesh Assistant
              </h3>
              <span className="px-1.5 py-0.2 rounded-full bg-[#E7F8EE] text-[#14753B] text-[10px] font-bold border border-[#A6F4C5]">
                Online
              </span>
            </div>
            <p className="text-[11px] text-[#64748B]">
              Answers from run #{runData?.id ? runData.id.slice(0, 6) : "2841"}
            </p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="text-[#64748B] hover:text-[#0F172A] p-1 rounded-md hover:bg-[#F8FAFC]"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Messages Feed */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3.5 text-xs">
        {messages.map((m) => {
          const isUser = m.sender === "user";
          return (
            <div
              key={m.id}
              className={`flex flex-col ${isUser ? "items-end" : "items-start"}`}
            >
              <div
                className={`max-w-[88%] rounded-xl p-3 leading-relaxed whitespace-pre-wrap ${
                  isUser
                    ? "bg-[#2457F5] text-white font-medium shadow-xs"
                    : "bg-[#F8FAFC] border border-[#E2E8F0] text-[#0F172A]"
                }`}
              >
                {m.text}
              </div>

              {/* Citations */}
              {!isUser && m.citations && m.citations.length > 0 && (
                <div className="flex flex-wrap items-center gap-1.5 mt-1.5">
                  {m.citations.map((c, i) => (
                    <button
                      key={i}
                      onClick={() => {
                        if (c.targetId && onSelectBug && runData?.bugs) {
                          const target = runData.bugs.find((b) => b.id === c.targetId);
                          if (target) onSelectBug(target);
                        }
                      }}
                      className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-[#EEF2FF] text-[#2457F5] border border-[#2457F5]/25 text-[10px] font-mono font-semibold hover:bg-[#E0E7FF] cursor-pointer"
                    >
                      <span>{c.label}</span>
                    </button>
                  ))}
                </div>
              )}

              {/* Action Buttons inside replies */}
              {!isUser && m.actions && m.actions.length > 0 && (
                <div className="flex items-center gap-2 mt-2">
                  {m.actions.map((act, i) => (
                    <button
                      key={i}
                      onClick={() => handleAction(act)}
                      className="px-2.5 py-1 rounded-md bg-[#2457F5] hover:bg-[#1A44D4] text-white text-[11px] font-semibold flex items-center gap-1 transition-colors shadow-xs cursor-pointer"
                    >
                      {act === "Open PR" && <GitPullRequest className="w-3 h-3" />}
                      {act === "Copy patch" && <Copy className="w-3 h-3" />}
                      <span>{act}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Quick Prompts Bar */}
      <div className="px-3 py-2 border-t border-[#E2E8F0] bg-[#FAFBFD]">
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 text-[11px] no-scrollbar">
          {quickPrompts.map((qp, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(qp)}
              className="whitespace-nowrap px-2.5 py-1 rounded-md bg-white hover:bg-[#F1F5F9] border border-[#E2E8F0] text-[#64748B] hover:text-[#0F172A] transition-colors flex-shrink-0 cursor-pointer"
            >
              {qp}
            </button>
          ))}
        </div>
      </div>

      {/* Input Form */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        className="p-3 border-t border-[#E2E8F0] bg-white flex items-center gap-2"
      >
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Ask about this run..."
          className="flex-1 h-9 px-3 text-xs bg-[#F8FAFC] border border-[#E2E8F0] rounded-lg text-[#0F172A] placeholder-[#94A3B8] focus:outline-none focus:border-[#2457F5]"
        />
        <button
          type="submit"
          className="h-9 px-3.5 rounded-lg bg-[#2457F5] hover:bg-[#1A44D4] text-white font-semibold text-xs flex items-center gap-1 transition-colors cursor-pointer"
        >
          <span>Send</span>
          <Send className="w-3 h-3" />
        </button>
      </form>
    </div>
  );
}
