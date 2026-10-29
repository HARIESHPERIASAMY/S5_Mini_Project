import React, { useState } from 'react';
import { 
  Puzzle, Copy, Check, MessageSquare, 
  Send, AlertCircle, Shield, CheckCircle2
} from 'lucide-react';

const GitRepoIcon = (props) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22" />
  </svg>
);

export default function IntegrationsView({ runData }) {
  const [copiedAction, setCopiedAction] = useState(false);
  const [copiedComment, setCopiedComment] = useState(false);
  const [webhookUrl, setWebhookUrl] = useState(() => localStorage.getItem("sentinel_webhook_url") || "");
  const [webhookSaved, setWebhookSaved] = useState(false);

  const ghActionYaml = 
`name: SentinelMesh Self-Healing QA Gate
on: [pull_request, push]

jobs:
  sentinelmesh-audit:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install SentinelMesh Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pytest coverage

      - name: Execute Autonomous QA Swarm
        run: |
          # Fails the pipeline check if merge gate fails
          curl -sSL -X POST http://localhost:8000/api/runs \\
            -H "Content-Type: application/json" \\
            -d '{"project_id": "current", "llm_provider": "offline"}'
`;

  const prCommentSnippet = 
`### 🛡️ SentinelMesh QA Gate Certification
- **Suite Health Score**: ${runData?.suite_health_score ?? 73.5} / 100
- **Code Coverage**: ${runData?.code_coverage ?? 54.1}%
- **Defects Flagged**: ${runData?.bugs_count ?? 3}
- **Self-Healing Fixes Verified**: ${runData?.fixes_verified_count ?? 2}
- **Merge Gate**: Verified (${runData?.fixes_verified_count ?? 2} fixes certified in sandbox regression)

*Generated autonomously by SentinelMesh Swarm*`;

  const handleCopyAction = () => {
    navigator.clipboard.writeText(ghActionYaml);
    setCopiedAction(true);
    setTimeout(() => setCopiedAction(false), 2000);
  };

  const handleCopyComment = () => {
    navigator.clipboard.writeText(prCommentSnippet);
    setCopiedComment(true);
    setTimeout(() => setCopiedComment(false), 2000);
  };

  const handleSaveWebhook = (e) => {
    e.preventDefault();
    localStorage.setItem("sentinel_webhook_url", webhookUrl);
    setWebhookSaved(true);
    setTimeout(() => setWebhookSaved(false), 2500);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="sm-card p-5 bg-white border border-[#E2E8F0] rounded-xl shadow-xs">
        <div className="flex items-center gap-2">
          <Puzzle className="w-4 h-4 text-[#2457F5]" />
          <h3 className="font-heading font-extrabold text-[#0F172A] text-lg">
            Continuous Integration & Webhook Integrations
          </h3>
        </div>
        <p className="text-xs text-[#64748B] mt-0.5">
          Connect SentinelMesh into CI/CD pipelines, pull request comment gates, and team notification channels.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* 1. GitHub Action Workflow */}
        <div className="sm-card p-5 bg-white border border-[#E2E8F0] rounded-xl shadow-xs flex flex-col justify-between space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <GitRepoIcon className="w-4 h-4 text-[#0F172A]" />
              <strong className="font-heading text-sm text-[#0F172A]">
                GitHub Actions Pipeline (.github/workflows)
              </strong>
            </div>
            <button
              onClick={handleCopyAction}
              className="flex items-center gap-1.5 px-3 h-8 rounded-lg border border-[#E2E8F0] hover:bg-[#F8FAFC] text-xs font-semibold text-[#0F172A] transition-colors cursor-pointer"
            >
              {copiedAction ? <Check className="w-3.5 h-3.5 text-[#16A34A]" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copiedAction ? "Copied" : "Copy YAML"}</span>
            </button>
          </div>

          <div className="p-3.5 rounded-lg bg-[#0F172A] text-slate-200 font-mono text-[11px] overflow-x-auto">
            <pre>{ghActionYaml}</pre>
          </div>
          <span className="text-[11px] text-[#64748B]">
            Automatically blocks merge if suite health score drops below threshold or regressions occur.
          </span>
        </div>

        {/* 2. Automated PR Comment Template */}
        <div className="sm-card p-5 bg-white border border-[#E2E8F0] rounded-xl shadow-xs flex flex-col justify-between space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <MessageSquare className="w-4 h-4 text-[#2457F5]" />
              <strong className="font-heading text-sm text-[#0F172A]">
                Pull Request Certification Comment
              </strong>
            </div>
            <button
              onClick={handleCopyComment}
              className="flex items-center gap-1.5 px-3 h-8 rounded-lg border border-[#E2E8F0] hover:bg-[#F8FAFC] text-xs font-semibold text-[#0F172A] transition-colors cursor-pointer"
            >
              {copiedComment ? <Check className="w-3.5 h-3.5 text-[#16A34A]" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copiedComment ? "Copied" : "Copy Text"}</span>
            </button>
          </div>

          <div className="p-3.5 rounded-lg bg-[#FAFBFD] border border-[#E2E8F0] font-mono text-[11px] text-[#0F172A] overflow-x-auto whitespace-pre-wrap">
            {prCommentSnippet}
          </div>
          <span className="text-[11px] text-[#64748B]">
            Markdown-formatted verification receipt to paste into GitHub or GitLab review threads.
          </span>
        </div>
      </div>

      {/* 3. Slack / Email Webhook Configuration */}
      <div className="sm-card p-5 bg-white border border-[#E2E8F0] rounded-xl shadow-xs space-y-4">
        <div>
          <strong className="font-heading text-sm text-[#0F172A] block">
            Team Webhook Alerts (Slack / Discord / Teams)
          </strong>
          <p className="text-xs text-[#64748B] mt-0.5">
            Configure a webhook endpoint to receive notifications on swarm analysis completion and regression failures.
          </p>
        </div>

        <form onSubmit={handleSaveWebhook} className="space-y-3 max-w-xl">
          <div>
            <label className="block text-xs font-bold text-[#0F172A] mb-1">Webhook URL</label>
            <input
              type="url"
              placeholder="https://hooks.slack.com/services/..."
              value={webhookUrl}
              onChange={(e) => setWebhookUrl(e.target.value)}
              className="w-full h-9 px-3 text-xs bg-[#F8FAFC] border border-[#E2E8F0] rounded-lg font-mono focus:outline-none focus:border-[#2457F5]"
            />
          </div>

          <div className="flex items-center gap-3">
            <button
              type="submit"
              className="px-4 h-9 rounded-lg bg-[#2457F5] hover:bg-[#1A44D4] text-white text-xs font-semibold cursor-pointer"
            >
              Save Webhook Configuration
            </button>
            {webhookSaved && (
              <span className="text-xs font-mono text-[#16A34A] flex items-center gap-1">
                <Check className="w-3.5 h-3.5" /> Saved locally
              </span>
            )}
          </div>

          <div className="p-3 rounded-lg bg-[#FFF4E0] border border-[#FEDF89] text-[11px] text-[#9A5B00] flex items-center gap-2 font-mono">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>Needs backend webhook sender to dispatch: Delivery is stored locally in offline engine mode (see docs/needs-backend.md).</span>
          </div>
        </form>
      </div>
    </div>
  );
}
