import React, { StrictMode, Component } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  componentDidCatch(error, errorInfo) {
    console.error("SentinelMesh UI caught render error:", error, errorInfo);
  }
  render() {
    if (this.state.hasError) {
      return (
        <div className="flex h-screen w-screen items-center justify-center bg-[#F8FAFC] p-6 text-center font-sans">
          <div className="max-w-md p-6 bg-white border border-[#E2E8F0] rounded-xl shadow-lg space-y-3">
            <h2 className="text-base font-bold text-[#DC2626]">SentinelMesh Dashboard Error</h2>
            <p className="text-xs text-[#64748B]">An unexpected rendering error occurred.</p>
            <pre className="p-3 bg-[#F1F5F9] rounded text-[11px] font-mono text-left overflow-x-auto text-[#0F172A]">
              {this.state.error?.message || "Unknown error"}
            </pre>
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-[#2457F5] hover:bg-[#1A44D4] text-white text-xs font-semibold rounded-lg cursor-pointer"
            >
              Reload Dashboard
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </StrictMode>,
)
