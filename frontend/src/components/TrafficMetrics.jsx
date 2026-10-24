import React, { useState } from 'react';

export default function TrafficMetrics({ analytics, parameters, onUpdateParams }) {
  const [showConfig, setShowConfig] = useState(false);
  const [distance, setDistance] = useState(parameters?.corridor_distance_meters || 850);
  const [threshold, setThreshold] = useState(parameters?.confidence_threshold || 0.55);

  const handleApplyConfig = (e) => {
    e.preventDefault();
    onUpdateParams({
      corridor_distance_meters: parseFloat(distance),
      confidence_threshold: parseFloat(threshold)
    });
    setShowConfig(false);
  };

  const a = analytics || {};

  return (
    <div className="mb-4">
      {/* Metrics Row */}
      <div className="stats-grid">
        {/* Metric 1: Corridor Speed */}
        <div className="stat-card stat-speed">
          <div className="flex items-center justify-between">
            <span className="stat-label flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-blue-500"></span>
              Corridor Flow Speed
            </span>
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-blue-950/60 text-blue-300 border border-blue-800">
              {a.corridor_distance_meters || 850}m
            </span>
          </div>
          <div className="stat-value text-blue-100">
            {a.avg_speed_kmh ? `${a.avg_speed_kmh}` : '--'}
            <span className="text-sm font-normal text-slate-400 ml-1 font-mono">km/h</span>
          </div>
          <div className="stat-subtext flex items-center justify-between">
            <span>Physical progression velocity</span>
            <span className="font-mono text-[10px] text-blue-400 font-bold">d / Δt</span>
          </div>
        </div>

        {/* Metric 2: Mean Transit Time */}
        <div className="stat-card stat-transit">
          <div className="flex items-center justify-between">
            <span className="stat-label flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
              Mean Transit Window
            </span>
            <span className="text-[10px] font-mono text-cyan-300 bg-cyan-950/60 px-1.5 py-0.5 rounded border border-cyan-800">
              Δt = tB - tA
            </span>
          </div>
          <div className="stat-value text-cyan-100">
            {a.avg_transit_time_sec ? `${a.avg_transit_time_sec}` : '--'}
            <span className="text-sm font-normal text-slate-400 ml-1 font-mono">s</span>
            <span className="text-xs font-normal text-slate-400 ml-2">
              (med {a.median_transit_time_sec || '--'}s)
            </span>
          </div>
          <div className="stat-subtext">
            Non-overlapping blind zone travel duration
          </div>
        </div>

        {/* Metric 3: Re-ID Match Rate */}
        <div className="stat-card stat-match">
          <div className="flex items-center justify-between">
            <span className="stat-label flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
              Re-ID Match Rate
            </span>
            <span className="text-[10px] font-mono text-emerald-300 bg-emerald-950/60 px-1.5 py-0.5 rounded border border-emerald-800">
              {a.total_matches_detected || 0} candidates
            </span>
          </div>
          <div className="stat-value text-emerald-100">
            {a.match_rate_percent !== undefined ? `${a.match_rate_percent}%` : '--'}
          </div>
          <div className="stat-subtext">
            Cam A vehicles re-identified at downstream Cam B
          </div>
        </div>

        {/* Metric 4: Human Review Status */}
        <div className="stat-card stat-review">
          <div className="flex items-center justify-between">
            <span className="stat-label flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-amber-400"></span>
              Verification Ledger
            </span>
            <button
              onClick={() => setShowConfig(!showConfig)}
              className="text-[11px] text-amber-300 hover:text-amber-200 underline font-mono font-semibold"
            >
              {showConfig ? 'Close Controls' : 'Tune Physics'}
            </button>
          </div>
          <div className="stat-value flex items-center gap-2.5 text-base">
            <span className="text-emerald-400 font-mono font-bold">
              ✓ {a.verified_matches || 0} Verified
            </span>
            <span className="text-slate-600 font-mono">/</span>
            <span className="text-red-400 font-mono font-bold">
              ✗ {a.rejected_matches || 0} Rejected
            </span>
          </div>
          <div className="stat-subtext flex items-center justify-between">
            <span>State: <strong className="text-slate-200">{a.congestion_level || 'Free Flow'}</strong></span>
            <span className="text-[10px] text-slate-400 font-mono">{a.traffic_state || 'Nominal Flow'}</span>
          </div>
        </div>
      </div>

      {/* Corridor Physics Tuning Drawer */}
      {showConfig && (
        <form onSubmit={handleApplyConfig} className="bg-[var(--bg-panel)] border border-[var(--border-light)] p-3.5 rounded-md mb-3 flex flex-wrap items-center gap-4 text-xs shadow-md">
          <div className="flex items-center gap-2">
            <label className="text-slate-300 font-medium font-mono">Corridor Distance (m):</label>
            <input
              type="number"
              min="100"
              max="5000"
              step="50"
              value={distance}
              onChange={(e) => setDistance(e.target.value)}
              className="bg-[var(--bg-main)] border border-[var(--border-color)] rounded px-2.5 py-1 text-white font-mono w-24 focus:border-blue-500 focus:outline-none"
            />
          </div>

          <div className="flex items-center gap-2">
            <label className="text-slate-300 font-medium font-mono">Re-ID Confidence Threshold:</label>
            <input
              type="range"
              min="0.30"
              max="0.90"
              step="0.05"
              value={threshold}
              onChange={(e) => setThreshold(e.target.value)}
              className="w-32 cursor-pointer accent-blue-500"
            />
            <span className="font-mono text-cyan-300 font-bold">{Math.round(threshold * 100)}%</span>
          </div>

          <button type="submit" className="btn btn-sm btn-primary">
            Apply Parameters
          </button>
          <button
            type="button"
            onClick={() => setShowConfig(false)}
            className="btn btn-sm"
          >
            Cancel
          </button>
          <span className="text-[11px] text-slate-400 ml-auto">
            * Adjusts the physical speed bounds and cosine appearance cutoff in real-time.
          </span>
        </form>
      )}
    </div>
  );
}
