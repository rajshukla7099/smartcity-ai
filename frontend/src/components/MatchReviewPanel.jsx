import React, { useState } from 'react';

export default function MatchReviewPanel({
  matches = [],
  selectedTrackA,
  selectedTrackB,
  onReviewMatch,
  onInspectMatch,
  updatingMatchId
}) {
  const [filter, setFilter] = useState('primary'); // 'all', 'primary', 'pending', 'accepted', 'rejected'
  const [searchQuery, setSearchQuery] = useState('');

  // Apply track selection filter if user clicked a specific vehicle in DualCameraView
  let filtered = matches;
  if (selectedTrackA) {
    filtered = filtered.filter((m) => m.cam_a_track_id === selectedTrackA);
  }
  if (selectedTrackB) {
    filtered = filtered.filter((m) => m.cam_b_track_id === selectedTrackB);
  }

  // Apply tab filter
  if (filter === 'primary') {
    filtered = filtered.filter((m) => m.is_primary_candidate);
  } else if (filter === 'pending') {
    filtered = filtered.filter((m) => m.status === 'pending');
  } else if (filter === 'accepted') {
    filtered = filtered.filter((m) => m.status === 'accepted');
  } else if (filter === 'rejected') {
    filtered = filtered.filter((m) => m.status === 'rejected');
  } else if (filter === 'flagged') {
    filtered = filtered.filter((m) => m.status === 'flagged');
  }

  // Apply text search
  if (searchQuery.trim()) {
    const q = searchQuery.toLowerCase();
    filtered = filtered.filter(
      (m) =>
        m.match_id.toLowerCase().includes(q) ||
        m.cam_a_track_id.toLowerCase().includes(q) ||
        m.cam_b_track_id.toLowerCase().includes(q) ||
        m.color_a.toLowerCase().includes(q) ||
        m.vehicle_type_a.toLowerCase().includes(q)
    );
  }

  const counts = {
    all: matches.length,
    primary: matches.filter((m) => m.is_primary_candidate).length,
    pending: matches.filter((m) => m.status === 'pending').length,
    accepted: matches.filter((m) => m.status === 'accepted').length,
    rejected: matches.filter((m) => m.status === 'rejected').length,
    flagged: matches.filter((m) => m.status === 'flagged').length
  };

  return (
    <div className="eng-panel">
      {/* Panel Top Header Bar */}
      <div className="eng-panel-header">
        <div className="eng-panel-title">
          <svg className="w-4 h-4 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
            <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
            <circle cx="9" cy="7" r="4" />
            <polyline points="16 11 18 13 22 9" />
          </svg>
          Cross-Camera Re-Identification Verification Console
          <span className="text-xs font-normal text-slate-400 font-mono">
            ({filtered.length} candidates active)
          </span>
        </div>

        {/* Filter Navigation Tabs */}
        <div className="flex flex-wrap items-center gap-1.5 text-xs">
          <button
            onClick={() => setFilter('primary')}
            className={`btn btn-sm ${filter === 'primary' ? 'btn-primary' : ''}`}
          >
            1-to-1 Best Matches ({counts.primary})
          </button>
          <button
            onClick={() => setFilter('all')}
            className={`btn btn-sm ${filter === 'all' ? 'btn-primary' : ''}`}
          >
            All Candidates ({counts.all})
          </button>
          <button
            onClick={() => setFilter('pending')}
            className={`btn btn-sm ${filter === 'pending' ? 'btn-primary' : ''}`}
          >
            Pending ({counts.pending})
          </button>
          <button
            onClick={() => setFilter('accepted')}
            className={`btn btn-sm ${filter === 'accepted' ? 'btn-primary' : ''}`}
          >
            Verified ({counts.accepted})
          </button>
          <button
            onClick={() => setFilter('rejected')}
            className={`btn btn-sm ${filter === 'rejected' ? 'btn-primary' : ''}`}
          >
            Rejected ({counts.rejected})
          </button>
        </div>
      </div>

      <div className="eng-panel-body">
        {/* Search & Active Filter Indicators */}
        <div className="flex flex-wrap items-center justify-between mb-3.5 gap-3">
          <div className="text-[11px] text-slate-400 flex items-center gap-2">
            <span className="font-semibold text-slate-300">Quick Filter:</span>
            <input
              type="text"
              placeholder="Search by Track ID, Type, Color..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-[var(--bg-main)] border border-[var(--border-color)] rounded-md px-3 py-1 text-xs text-white w-60 font-mono placeholder:text-slate-600 focus:outline-none focus:border-blue-500 shadow-inner"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="text-[10px] text-slate-400 hover:text-white underline font-mono"
              >
                Clear
              </button>
            )}
          </div>

          <div className="text-[11px] text-slate-400 font-mono flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
            <span>Corridor Gating: Baseline = 850m &bull; Non-Plate Spatial Appearance Embeddings</span>
          </div>
        </div>

        {/* Empty State */}
        {filtered.length === 0 ? (
          <div className="border border-dashed border-[var(--border-color)] rounded-lg p-10 text-center text-slate-400 bg-[var(--bg-main)]">
            <svg className="w-10 h-10 mx-auto text-slate-600 mb-2.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <circle cx="11" cy="11" r="8" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
            <div className="text-sm font-semibold text-slate-300">No match candidates match current filter criteria</div>
            <div className="text-xs text-slate-500 mt-1">
              {selectedTrackA || selectedTrackB
                ? "The selected vehicle has no candidates meeting the threshold in this category."
                : "Try selecting 'All Candidates' tab or tuning Re-ID Confidence Threshold."}
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            {filtered.map((match) => {
              const isUpdating = updatingMatchId === match.match_id;
              const confPct = Math.round(match.overall_confidence * 100);
              const visPct = Math.round(match.visual_similarity * 100);
              const stPct = Math.round(match.spatio_temporal_score * 100);

              let statusBadge = (
                <span className="badge badge-pending">Pending Operator Review</span>
              );
              if (match.status === 'accepted') {
                statusBadge = <span className="badge badge-accepted">✓ Verified Ground Match</span>;
              } else if (match.status === 'rejected') {
                statusBadge = <span className="badge badge-rejected">✗ Rejected Pairing</span>;
              } else if (match.status === 'flagged') {
                statusBadge = <span className="badge badge-flagged">⚑ Flagged for Secondary Review</span>;
              }

              return (
                <div
                  key={match.match_id}
                  className={`border rounded-lg p-3.5 transition-all shadow-sm ${
                    match.status === 'accepted'
                      ? 'bg-[var(--bg-surface)] border-emerald-600/70 ring-1 ring-emerald-500/30'
                      : match.status === 'rejected'
                      ? 'bg-[var(--bg-main)] border-red-900/50 opacity-60'
                      : 'bg-[var(--bg-surface)] border-[var(--border-color)] hover:border-[var(--border-light)]'
                  }`}
                >
                  <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                    {/* Left: Paired Visual Vehicle Crops */}
                    <div className="flex items-center gap-3.5">
                      {/* Camera A Crop */}
                      <div className="flex items-center gap-2.5 bg-[var(--bg-main)] p-2 rounded-md border border-[var(--border-color)] shadow-inner">
                        {match.crop_a_b64 ? (
                          <img
                            src={match.crop_a_b64}
                            alt={match.cam_a_track_id}
                            className="w-14 h-14 object-cover rounded border border-[#334155] bg-black shadow"
                          />
                        ) : (
                          <div className="w-14 h-14 bg-slate-800 rounded"></div>
                        )}
                        <div>
                          <div className="text-[10px] text-blue-400 font-mono font-bold">CAM-01 (ENTRY)</div>
                          <div className="font-mono text-xs font-extrabold text-white">{match.cam_a_track_id}</div>
                          <div className="text-[10px] text-slate-400 font-mono">exit: t={match.cam_a_exit_time}s</div>
                        </div>
                      </div>

                      {/* Transit Physics Bridge */}
                      <div className="flex flex-col items-center justify-center px-1">
                        <div className="text-[10px] font-mono text-slate-400 font-semibold">
                          {match.transit_time_sec}s transit
                        </div>
                        <div className="w-20 h-0.5 bg-slate-600 my-1 relative">
                          <span className="absolute -top-1.5 right-0 text-[11px] text-cyan-400 font-bold">&rarr;</span>
                        </div>
                        <div className="text-[11px] font-mono text-emerald-400 font-bold">
                          {match.estimated_speed_kmh} km/h
                        </div>
                      </div>

                      {/* Camera B Crop */}
                      <div className="flex items-center gap-2.5 bg-[var(--bg-main)] p-2 rounded-md border border-[var(--border-color)] shadow-inner">
                        {match.crop_b_b64 ? (
                          <img
                            src={match.crop_b_b64}
                            alt={match.cam_b_track_id}
                            className="w-14 h-14 object-cover rounded border border-[#334155] bg-black shadow"
                          />
                        ) : (
                          <div className="w-14 h-14 bg-slate-800 rounded"></div>
                        )}
                        <div>
                          <div className="text-[10px] text-cyan-400 font-mono font-bold">CAM-02 (EXIT)</div>
                          <div className="font-mono text-xs font-extrabold text-white">{match.cam_b_track_id}</div>
                          <div className="text-[10px] text-slate-400 font-mono">entry: t={match.cam_b_entry_time}s</div>
                        </div>
                      </div>
                    </div>

                    {/* Middle: Feature Similarity & Engineering Explanation */}
                    <div className="flex-1 lg:px-4 border-t lg:border-t-0 lg:border-l lg:border-r border-[var(--border-color)] pt-2.5 lg:pt-0">
                      <div className="flex flex-wrap items-center gap-2 mb-1.5">
                        <span className="font-mono text-xs text-white font-bold">{match.match_id}</span>
                        {statusBadge}
                        {match.is_primary_candidate && (
                          <span className="text-[10px] px-2 py-0.5 rounded bg-blue-900/60 text-blue-300 border border-blue-700 font-mono font-bold">
                            ★ Primary 1-to-1 Pairing
                          </span>
                        )}
                      </div>

                      <p className="text-[11px] text-slate-300 leading-tight mb-2.5 font-medium">
                        {match.explanation}
                      </p>

                      {/* Visual Meters */}
                      <div className="grid grid-cols-3 gap-3 text-[10px] font-mono">
                        <div>
                          <div className="flex justify-between text-slate-400 mb-0.5">
                            <span>Visual Sim:</span>
                            <span className="text-white font-bold">{visPct}%</span>
                          </div>
                          <div className="w-full bg-slate-800 h-1 rounded overflow-hidden">
                            <div className="bg-blue-500 h-full rounded" style={{ width: `${visPct}%` }}></div>
                          </div>
                        </div>

                        <div>
                          <div className="flex justify-between text-slate-400 mb-0.5">
                            <span>Physics Score:</span>
                            <span className="text-white font-bold">{stPct}%</span>
                          </div>
                          <div className="w-full bg-slate-800 h-1 rounded overflow-hidden">
                            <div className="bg-cyan-500 h-full rounded" style={{ width: `${stPct}%` }}></div>
                          </div>
                        </div>

                        <div>
                          <div className="flex justify-between text-slate-400 mb-0.5">
                            <span>Confidence:</span>
                            <span className={confPct >= 80 ? 'text-emerald-400 font-bold' : 'text-blue-300 font-bold'}>
                              {confPct}%
                            </span>
                          </div>
                          <div className="w-full bg-slate-800 h-1 rounded overflow-hidden">
                            <div
                              className={`h-full rounded ${confPct >= 80 ? 'bg-emerald-500' : 'bg-blue-500'}`}
                              style={{ width: `${confPct}%` }}
                            ></div>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Right: Human Review Decision Controls */}
                    <div className="flex flex-wrap items-center gap-2 justify-end">
                      <button
                        onClick={() => onInspectMatch(match)}
                        className="btn btn-sm shadow-sm"
                        title="Compare spatial stripe color histograms and geometric features"
                      >
                        Inspect
                      </button>

                      <button
                        onClick={() => onReviewMatch(match.match_id, 'accepted')}
                        disabled={isUpdating || match.status === 'accepted'}
                        className="btn btn-sm btn-success shadow-sm"
                        title="Accept this pairing as the verified physical vehicle"
                      >
                        Verify Match
                      </button>

                      <button
                        onClick={() => onReviewMatch(match.match_id, 'rejected')}
                        disabled={isUpdating || match.status === 'rejected'}
                        className="btn btn-sm btn-danger shadow-sm"
                        title="Reject this match as false correlation or distractor"
                      >
                        Reject
                      </button>

                      <button
                        onClick={() => onReviewMatch(match.match_id, 'flagged')}
                        disabled={isUpdating || match.status === 'flagged'}
                        className="btn btn-sm btn-warning shadow-sm"
                        title="Flag for secondary engineering review"
                      >
                        Flag
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
