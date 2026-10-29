import React from 'react';
import { 
  LayoutDashboard, PlayCircle, AlertCircle, Bot, History, 
  FileText, Share2, Settings, ChevronLeft, ChevronRight, Shield
} from 'lucide-react';

export default function Sidebar({
  activeView = "overview",
  onSelectView,
  collapsed = false,
  onToggleCollapse,
  findingsCount = 0,
  runId = "2841",
  isConnected = true
}) {
  const navItems = [
    { id: "overview", label: "Overview", icon: LayoutDashboard },
    { id: "liverun", label: "Live run", icon: PlayCircle },
    { id: "findings", label: "Findings", icon: AlertCircle, badge: findingsCount },
    { id: "agents", label: "Agents", icon: Bot },
    { id: "history", label: "Run history", icon: History },
    { id: "reports", label: "Reports", icon: FileText },
    { id: "integrations", label: "Integrations", icon: Share2 },
    { id: "settings", label: "Settings", icon: Settings },
  ];

  return (
    <aside
      className={`bg-[#0B132B] text-slate-300 flex flex-col transition-all duration-200 border-r border-[#1E2D5A] z-30 select-none ${
        collapsed ? "w-16" : "w-60"
      }`}
    >
      {/* Brand Header */}
      <div className="h-16 px-4 flex items-center justify-between border-b border-[#1E2D5A]/80">
        <div className="flex items-center gap-3 overflow-hidden">
          <div className="w-8 h-8 rounded-lg bg-[#2457F5] flex items-center justify-center text-white flex-shrink-0 shadow-sm shadow-blue-500/30">
            <Shield className="w-4 h-4" />
          </div>
          {!collapsed && (
            <div className="min-w-0">
              <span className="font-heading font-extrabold text-white text-[15px] tracking-tight leading-none block">
                SentinelMesh
              </span>
              <span className="text-[11px] text-slate-400 font-medium leading-none mt-1 block">
                Self-healing QA
              </span>
            </div>
          )}
        </div>

        <button
          onClick={onToggleCollapse}
          title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          className="text-slate-400 hover:text-white p-1 rounded-md hover:bg-[#142042] transition-colors"
        >
          {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>

      {/* Navigation List */}
      <nav className="flex-1 px-2.5 py-4 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeView === item.id;

          return (
            <button
              key={item.id}
              onClick={() => onSelectView(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-[13px] font-medium transition-all ${
                isActive
                  ? "bg-[#2457F5] text-white shadow-xs font-semibold"
                  : "text-slate-300 hover:bg-[#142042] hover:text-white"
              } ${collapsed ? "justify-center px-0" : ""}`}
              title={collapsed ? item.label : undefined}
            >
              <Icon className="w-4 h-4 flex-shrink-0" />
              {!collapsed && (
                <span className="flex-1 text-left truncate">{item.label}</span>
              )}
              {!collapsed && item.badge !== undefined && item.badge > 0 && (
                <span
                  className={`px-1.5 py-0.2 rounded-full text-[10px] font-bold ${
                    isActive
                      ? "bg-white text-[#2457F5]"
                      : "bg-[#FEECEC] text-[#B42318]"
                  }`}
                >
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Footer: Connection & Agents Liveness */}
      <div className="p-3.5 border-t border-[#1E2D5A]/80 text-[11px] font-mono">
        <div className="flex items-center gap-2">
          <span
            className={`w-2 h-2 rounded-full flex-shrink-0 ${
              isConnected ? "bg-[#16A34A]" : "bg-[#DC2626]"
            }`}
          />
          {!collapsed && (
            <span className="text-white font-semibold truncate">
              {isConnected ? "Backend connected" : "Disconnected"}
            </span>
          )}
        </div>
        {!collapsed && (
          <p className="text-slate-400 text-[10px] mt-1 truncate">
            9 agents online · run #{runId ? runId.slice(0, 6) : "idle"}
          </p>
        )}
      </div>
    </aside>
  );
}
