import React, { useState } from 'react';
import { X, Code, Upload, Sparkles, Loader2 } from 'lucide-react';

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
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-fade-in">
      <div className="glass-panel-glow rounded-2xl w-full max-w-xl p-6 border border-mesh-border shadow-2xl">
        <div className="flex items-center justify-between pb-3 border-b border-mesh-border">
          <div className="flex items-center gap-2">
            <Code className="w-5 h-5 text-cyan-400" />
            <h2 className="text-base font-bold text-white font-mono">
              Analyze New Repository or Code Snippet
            </h2>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex items-center gap-2 mt-4 border-b border-slate-800 pb-2 text-xs font-mono">
          <button
            onClick={() => setActiveTab("snippet")}
            className={`px-3 py-1.5 rounded-lg transition-colors ${activeTab === "snippet" ? "bg-cyan-950 text-cyan-300 border border-cyan-800" : "text-slate-400 hover:text-white"}`}
          >
            Paste Code Snippet
          </button>
          <button
            onClick={() => setActiveTab("zip")}
            className={`px-3 py-1.5 rounded-lg transition-colors ${activeTab === "zip" ? "bg-cyan-950 text-cyan-300 border border-cyan-800" : "text-slate-400 hover:text-white"}`}
          >
            Upload Project (.zip)
          </button>
          <button
            onClick={() => {
              onLaunchDemo();
              onClose();
            }}
            className="ml-auto flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-950 text-indigo-300 border border-indigo-800 hover:bg-indigo-900 transition-colors"
          >
            <Sparkles className="w-3.5 h-3.5" />
            Load Pre-Seeded Demo
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="mt-4 space-y-4">
          <div>
            <label className="block text-xs font-mono text-slate-400 mb-1">Project Name</label>
            <input
              type="text"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              required
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs font-mono text-white focus:outline-none focus:border-cyan-500"
            />
          </div>

          {activeTab === "snippet" ? (
            <div>
              <label className="block text-xs font-mono text-slate-400 mb-1">Python Source Snippet</label>
              <textarea
                value={codeSnippet}
                onChange={(e) => setCodeSnippet(e.target.value)}
                rows={10}
                required
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs font-mono text-cyan-300 focus:outline-none focus:border-cyan-500"
              />
            </div>
          ) : (
            <div>
              <label className="block text-xs font-mono text-slate-400 mb-1">Zip Archive</label>
              <div className="border-2 border-dashed border-slate-700 rounded-xl p-8 text-center flex flex-col items-center justify-center">
                <Upload className="w-8 h-8 text-slate-500 mb-2" />
                <input
                  type="file"
                  accept=".zip"
                  onChange={(e) => setZipFile(e.target.files?.[0] || null)}
                  required
                  className="text-xs font-mono text-slate-400"
                />
              </div>
            </div>
          )}

          <div className="flex items-center justify-end gap-3 pt-3 border-t border-mesh-border">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-lg bg-slate-800 text-slate-300 text-xs font-mono hover:bg-slate-700"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="flex items-center gap-2 px-5 py-2 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 text-white text-xs font-mono font-bold hover:from-cyan-400 hover:to-blue-500 shadow-lg shadow-cyan-500/20"
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
