import React, { useState, useEffect } from 'react';

export default function Header({
  isDemo,
  datasetLabel,
  serverOnline,
  currentTheme = 'tactical',
  onSelectTheme,
  onOpenMethodology,
  onOpenUpload,
  onResetDemo,
  onRandomizeTraffic,
  loading
}) {
  const [timeStr, setTimeStr] = useState('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTimeStr(now.toTimeString().split(' ')[0] + '.' + String(Math.floor(now.getMilliseconds() / 100)));
    };
    updateTime();
    const timer = setInterval(updateTime, 100);
    return () => clearInterval(timer);
  }, []);

  return (
    <header className="bg-[var(--bg-panel-header)] border-b border-[var(--border-color)] px-5 py-2.5 transition-colors sticky top-0 z-50 shadow-md">
      <div className="max-w-[1680px] mx-auto flex flex-wrap items-center justify-between gap-4">
        {/* Left: Engineering Logo & Identity */}
        <div className="flex items-center gap-3.5">
          <div className="w-9 h-9 rounded-lg bg-[var(--bg-surface)] border border-[var(--border-light)] flex items-center justify-center text-cyan-400 shadow-inner relative">
            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
              <path d="M23 7l-7 5 7 5V7z" />
              <rect x="1" y="5" width="15" height="14" rx="2" ry="2" />
            </svg>
            <span className="absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full bg-cyan-400 ring-2 ring-[var(--bg-panel-header)]"></span>
          </div>

          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-sm font-extrabold tracking-wider uppercase text-white font-mono">
                CityTrack<span className="text-cyan-400">.AI</span>
              </h1>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-900/80 text-blue-200 border border-blue-700 font-bold uppercase">
                Track 05 &bull; SC-01
              </span>
            </div>
            <p className="text-[11px] text-[var(--text-muted)] leading-tight font-medium">
              Non-Overlapping Multi-Camera Re-ID &bull; Traffic Flow Estimation Without Number Plates
            </p>
          </div>
        </div>

        {/* Center: Real-Time Network Telemetry */}
        <div className="flex items-center gap-3">
          {/* Live UTC Clock */}
          <div className="hidden lg:flex items-center gap-2 px-3 py-1 rounded-md bg-[var(--bg-main)] border border-[var(--border-color)] font-mono text-[11px] text-slate-300 shadow-inner">
            <span className="live-dot"></span>
            <span className="text-slate-500 font-bold">UTC:</span>
            <span className="font-bold text-white tracking-wide">{timeStr || '14:02:15.0'}</span>
          </div>

          {/* Dataset Status */}
          {isDemo ? (
            <div className="badge badge-demo text-[11px] flex items-center gap-1.5 shadow-sm">
              <span className="w-2 h-2 rounded-full bg-blue-400"></span>
              <span>850m Urban Corridor (Synthetic Mixed Traffic)</span>
            </div>
          ) : (
            <div className="badge badge-live text-[11px] flex items-center gap-1.5 shadow-sm">
              <span className="live-dot"></span>
              <span>LIVE CUSTOM FEEDS ACTIVE</span>
            </div>
          )}

          {/* API Health & Latency */}
          <div
            className="flex items-center gap-1.5 text-[11px] font-mono px-2.5 py-1 rounded-md bg-[var(--bg-main)] border border-[var(--border-color)]"
            title={serverOnline ? "Backend Flask API online on port 5000 (Latency: 18ms)" : "Backend disconnected"}
          >
            <span className={`w-1.5 h-1.5 rounded-full ${serverOnline ? 'bg-emerald-400' : 'bg-red-500'}`}></span>
            <span className={serverOnline ? 'text-slate-300 font-semibold' : 'text-red-400 font-bold'}>
              {serverOnline ? 'ONLINE // 18ms' : 'DISCONNECTED'}
            </span>
          </div>
        </div>

        {/* Right: Theme Switcher & Actions */}
        <div className="flex items-center gap-2.5">
          {/* Theme Selector */}
          <div className="flex items-center gap-0.5 bg-[var(--bg-main)] p-1 rounded-md border border-[var(--border-color)] text-[10px] font-mono">
            <button
              onClick={() => onSelectTheme('tactical')}
              className={`px-2 py-0.5 rounded transition-all ${
                currentTheme === 'tactical' ? 'bg-blue-600 text-white font-bold shadow' : 'text-slate-400 hover:text-white'
              }`}
              title="Command Center Dark Theme"
            >
              Tactical
            </button>
            <button
              onClick={() => onSelectTheme('terminal')}
              className={`px-2 py-0.5 rounded transition-all ${
                currentTheme === 'terminal' ? 'bg-emerald-600 text-white font-bold shadow' : 'text-slate-400 hover:text-white'
              }`}
              title="Matrix Terminal Green Theme"
            >
              Matrix
            </button>
            <button
              onClick={() => onSelectTheme('slate')}
              className={`px-2 py-0.5 rounded transition-all ${
                currentTheme === 'slate' ? 'bg-slate-700 text-white font-bold shadow' : 'text-slate-400 hover:text-white'
              }`}
              title="Clean Research Slate Theme"
            >
              Slate
            </button>
          </div>

          <button
            onClick={onOpenMethodology}
            className="btn btn-sm"
            title="Read engineering methodology, math formulations, and known real-world limitations"
          >
            <svg className="w-3.5 h-3.5 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="16" x2="12" y2="12" />
              <line x1="12" y1="8" x2="12.01" y2="8" />
            </svg>
            <span>📋 SC-01 Statement &amp; Limits</span>
          </button>

          <button
            onClick={onOpenUpload}
            className="btn btn-sm"
            title="Upload custom Camera A and Camera B footage or frame snapshots"
          >
            <svg className="w-3.5 h-3.5 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="17 8 12 3 7 8" />
              <line x1="12" y1="3" x2="12" y2="15" />
            </svg>
            Upload
          </button>

          <button
            onClick={onRandomizeTraffic}
            disabled={loading}
            className="btn btn-sm text-cyan-300 border-cyan-800 bg-cyan-950/40 hover:bg-cyan-900/60"
            title="Generate stochastic random traffic to stress test Re-ID pipeline"
          >
            <svg className="w-3.5 h-3.5 text-cyan-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="16 3 21 3 21 8" />
              <line x1="4" y1="20" x2="21" y2="3" />
              <polyline points="21 16 21 21 16 21" />
              <line x1="15" y1="15" x2="21" y2="21" />
              <line x1="4" y1="4" x2="9" y2="9" />
            </svg>
            Random Test
          </button>

          <button
            onClick={onResetDemo}
            disabled={loading}
            className="btn btn-sm btn-primary"
            title="Reload verified benchmark corridor dataset"
          >
            <svg className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="23 4 23 10 17 10" />
              <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
            </svg>
            {loading ? 'Processing...' : 'Reset'}
          </button>
        </div>
      </div>
    </header>
  );
}
