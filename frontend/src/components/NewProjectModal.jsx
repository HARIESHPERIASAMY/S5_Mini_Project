import React, { useState } from 'react';
import { X, Upload, Sparkles, Loader2, FileCode } from 'lucide-react';

export default function NewProjectModal({ isOpen, onClose, onSubmitSnippet, onUploadZip, onLaunchDemo }) {
  const [activeTab, setActiveTab] = useState("snippet");
  const [projectName, setProjectName] = useState("Custom Analysis Project");
  const [codeSnippet, setCodeSnippet] = useState(`def process_discount(price: float, discount: float) -> float:
    # Example snippet with division by zero risk
    factor = price / discount
    return price - (price * discount)

def get_item(items: list, index: int):
    # Boundary error
    if index <= len(items):
        return items[index]
    return None
`);
  const [zipFile, setZipFile] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      if (activeTab === "snippet") {
        await onSubmitSnippet(projectName, codeSnippet);
      } else if (activeTab === "zip" && zipFile) {
        await onUploadZip(projectName, zipFile);
      }
      onClose();
    } catch (err) {
      alert("Submission error: " + err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-xs">
      <div className="card-surface bg-white rounded-2xl w-full max-w-xl p-6 border border-[#E3E8F0] shadow-xl">
        {/* Modal Header */}
        <div className="flex items-center justify-between pb-3 border-b border-[#E3E8F0]">
          <div className="flex items-center gap-2">
            <FileCode className="w-5 h-5 text-[#2563EB]" />
            <h3 className="text-base font-heading font-bold text-[#0F172A]">
              Analyze Repository or Code Snippet
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-[#F1F5F9] text-[#5B6577] hover:text-[#0F172A] transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex items-center gap-2 mt-4 border-b border-[#E3E8F0] pb-2 text-xs font-mono">
          <button
            type="button"
            onClick={() => setActiveTab("snippet")}
            className={`px-3 py-1.5 rounded-lg transition-colors font-semibold ${
              activeTab === "snippet"
                ? "bg-[#EAF1FF] text-[#1D4ED8] border border-[#B2CCFF]"
                : "text-[#5B6577] hover:text-[#0F172A]"
            }`}
          >
            Paste Code Snippet
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("zip")}
            className={`px-3 py-1.5 rounded-lg transition-colors font-semibold ${
              activeTab === "zip"
                ? "bg-[#EAF1FF] text-[#1D4ED8] border border-[#B2CCFF]"
                : "text-[#5B6577] hover:text-[#0F172A]"
            }`}
          >
            Upload Project (.zip)
          </button>
          <button
            type="button"
            onClick={() => {
              onLaunchDemo();
              onClose();
            }}
            className="ml-auto flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#E7F8EE] text-[#14753B] border border-[#A6F4C5] hover:bg-[#D3F5E1] transition-colors font-semibold"
          >
            <Sparkles className="w-3.5 h-3.5" />
            Load Pre-Seeded Demo
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="mt-4 space-y-4">
          <div>
            <label className="block text-xs font-mono font-bold text-[#5B6577] mb-1">
              Project Name
            </label>
            <input
              type="text"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              required
              className="w-full bg-[#F8FAFC] border border-[#E3E8F0] rounded-lg px-3 py-2 text-xs font-mono text-[#0F172A] focus:outline-none focus:border-[#2563EB]"
            />
          </div>

          {activeTab === "snippet" ? (
            <div>
              <label className="block text-xs font-mono font-bold text-[#5B6577] mb-1">
                Python Source Snippet
              </label>
              <textarea
                value={codeSnippet}
                onChange={(e) => setCodeSnippet(e.target.value)}
                rows={9}
                required
                className="w-full bg-[#FAFBFD] border border-[#E3E8F0] rounded-lg p-3 text-xs font-mono text-[#0F172A] focus:outline-none focus:border-[#2563EB]"
              />
            </div>
          ) : (
            <div>
              <label className="block text-xs font-mono font-bold text-[#5B6577] mb-1">
                Zip Archive (.zip containing Python project)
              </label>
              <div className="border-2 border-dashed border-[#CBD5E1] rounded-xl p-8 text-center flex flex-col items-center justify-center bg-[#F8FAFC]">
                <Upload className="w-8 h-8 text-[#8E9BAE] mb-2" />
                <input
                  type="file"
                  accept=".zip"
                  onChange={(e) => setZipFile(e.target.files?.[0] || null)}
                  required
                  className="text-xs font-mono text-[#5B6577]"
                />
              </div>
            </div>
          )}

          {/* Footer Actions */}
          <div className="flex items-center justify-end gap-3 pt-3 border-t border-[#E3E8F0]">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-lg bg-[#F1F5F9] text-[#5B6577] text-xs font-mono hover:bg-[#E2E8F0] font-semibold"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="flex items-center gap-2 px-5 py-2 rounded-lg bg-[#2563EB] hover:bg-[#1D4ED8] text-white text-xs font-mono font-bold shadow-xs cursor-pointer"
            >
              {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
              <span>{submitting ? "Initializing Agents..." : "Start Swarm Analysis"}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
