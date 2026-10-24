import React, { useState } from 'react';

export default function DualCameraView({
  cameraA,
  cameraB,
  selectedTrackA,
  selectedTrackB,
  onSelectTrackA,
  onSelectTrackB,
  onInspectVehicle
}) {
  // displayMode can be 'both', 'video', or 'photo'
  const [displayMode, setDisplayMode] = useState('both');
  const vehiclesA = cameraA?.vehicles || [];
  const vehiclesB = cameraB?.vehicles || [];

  return (
    <div className="eng-panel mb-4">
      {/* Panel Top Header Bar */}
      <div className="eng-panel-header flex-wrap gap-2">
        <div className="eng-panel-title">
          <svg className="w-4 h-4 text-cyan-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
            <rect x="2" y="3" width="20" height="14" rx="2" ry="2" />
            <line x1="8" y1="21" x2="16" y2="21" />
            <line x1="12" y1="17" x2="12" y2="21" />
          </svg>
          Non-Overlapping Dual Camera Corridor Observation
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[var(--bg-surface)] text-cyan-300 border border-[var(--border-color)] font-semibold">
            Corridor Baseline: 850m
          </span>
        </div>

        {/* 3-Way Mode Switcher: Photo + Video Dono / Live Video / Photo */}
        <div className="flex items-center gap-1.5 bg-[var(--bg-main)] p-1 rounded-lg border border-[var(--border-color)]">
          <button
            onClick={() => setDisplayMode('both')}
            className={`px-3 py-1 text-xs font-mono font-bold rounded transition-all flex items-center gap-1.5 ${
              displayMode === 'both'
                ? 'bg-blue-600 text-white shadow-md ring-1 ring-blue-400'
                : 'text-slate-400 hover:text-white hover:bg-[var(--bg-surface)]'
            }`}
            title="Display both Live 30 FPS Video Stream AND Photo Snapshot side-by-side"
          >
            <span>⚡ Photo + Video (Both)</span>
          </button>

          <button
            onClick={() => setDisplayMode('video')}
            className={`px-3 py-1 text-xs font-mono font-bold rounded transition-all flex items-center gap-1.5 ${
              displayMode === 'video'
                ? 'bg-emerald-600 text-white shadow-md ring-1 ring-emerald-400'
                : 'text-slate-400 hover:text-white hover:bg-[var(--bg-surface)]'
            }`}
            title="Display Full-Screen 30 FPS Corridor Video Stream"
          >
            <span className={displayMode === 'video' ? 'live-dot' : ''}></span>
            <span>🎥 Video Feed (30 FPS)</span>
          </button>

          <button
            onClick={() => setDisplayMode('photo')}
            className={`px-3 py-1 text-xs font-mono font-bold rounded transition-all flex items-center gap-1.5 ${
              displayMode === 'photo'
                ? 'bg-cyan-700 text-white shadow-md ring-1 ring-cyan-400'
                : 'text-slate-400 hover:text-white hover:bg-[var(--bg-surface)]'
            }`}
            title="Display High-Resolution Photo Snapshot with Detections"
          >
            <span>📷 Photo Snapshot</span>
          </button>

          {(selectedTrackA || selectedTrackB) && (
            <button
              onClick={() => {
                onSelectTrackA(null);
                onSelectTrackB(null);
              }}
              className="ml-2 btn btn-sm text-[11px] text-amber-300 border-amber-800 bg-amber-950/40"
            >
              Clear Filter ({selectedTrackA || selectedTrackB})
            </button>
          )}
        </div>
      </div>

      {/* Track 05: Smart Cities SC-01 Alignment Sub-Header */}
      <div className="bg-[var(--bg-panel-header)] px-4 py-1.5 border-b border-[var(--border-color)] flex items-center justify-between text-[11px] font-mono flex-wrap gap-2">
        <div className="flex items-center gap-2 text-slate-300">
          <span className="text-cyan-400 font-bold uppercase tracking-wider">Smart City SC-01:</span>
          <span>Non-Overlapping Origin-Destination Re-ID Flow (No Plate OCR)</span>
        </div>
        <div className="flex items-center gap-3 text-[10px]">
          <span className="text-emerald-400 font-semibold">🛵 Mixed Indian Traffic</span>
          <span className="text-slate-600">&bull;</span>
          <span className="text-blue-400 font-semibold">☀️ Multi-Stripe Appearance</span>
          <span className="text-slate-600">&bull;</span>
          <span className="text-purple-400 font-semibold">⏱️ Spatio-Temporal Gating</span>
        </div>
      </div>

      <div className="eng-panel-body">
        {/* Dual Video / Snapshot Displays */}
        <div className="dual-camera-grid mb-4">
          {/* CAMERA A */}
          <div className="border border-[var(--border-color)] rounded-lg bg-[var(--bg-main)] overflow-hidden shadow-xl transition-all">
            {/* Camera Header Bar */}
            <div className="bg-[var(--bg-panel-header)] px-3.5 py-2.5 border-b border-[var(--border-color)] flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="live-dot"></span>
                <span className="font-mono font-bold text-xs text-white tracking-wide">
                  {cameraA?.id || 'CAM-01'}: {cameraA?.name || 'Junction 4th Ave (North Approach)'}
                </span>
              </div>
              <div className="flex items-center gap-2 font-mono text-[10px] text-slate-400">
                <span className="text-blue-400 font-semibold">{vehiclesA.length} Active Tracklets</span>
                <span>&bull;</span>
                <span className="text-emerald-400 font-bold">
                  {displayMode === 'both' ? '⚡ PHOTO + VIDEO ACTIVE' : displayMode === 'video' ? '30.0 FPS LIVE STREAM' : 'HIGH-RES PHOTO SNAPSHOT'}
                </span>
              </div>
            </div>

            {/* Viewport Area: Switches according to displayMode */}
            {displayMode === 'both' ? (
              /* SPLIT SCREEN: Live 30 FPS Video + High-Res Photo */
              <div className="grid grid-cols-1 sm:grid-cols-2 bg-black border-b border-[var(--border-color)] divide-y sm:divide-y-0 sm:divide-x divide-[var(--border-color)]">
                {/* Video Column */}
                <div className="relative aspect-video bg-black flex items-center justify-center overflow-hidden">
                  <img
                    src="/api/stream/cam_a"
                    alt="Camera A Live Stream"
                    className="w-full h-full object-contain"
                  />
                  <div className="absolute top-2 left-2 px-1.5 py-0.5 rounded bg-black/85 border border-emerald-500/70 font-mono text-[8px] text-emerald-300 pointer-events-none flex items-center gap-1">
                    <span className="live-dot"></span>
                    <span>LIVE VIDEO &bull; 30 FPS</span>
                  </div>
                  <div className="absolute bottom-2 left-2 px-1.5 py-0.5 rounded bg-black/85 border border-slate-700/60 font-mono text-[8px] text-slate-300 pointer-events-none">
                    CAM-01 // RTSP STREAM
                  </div>
                </div>

                {/* Photo Snapshot Column */}
                <div className="relative aspect-video bg-black flex items-center justify-center overflow-hidden">
                  {cameraA?.frame_b64 ? (
                    <img
                      src={cameraA.frame_b64}
                      alt="Camera A Snapshot"
                      className="w-full h-full object-contain"
                    />
                  ) : (
                    <div className="text-slate-500 text-xs font-mono">Awaiting Photo Snapshot...</div>
                  )}
                  <div className="absolute top-2 left-2 px-1.5 py-0.5 rounded bg-black/85 border border-blue-500/70 font-mono text-[8px] text-blue-300 pointer-events-none flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-blue-400"></span>
                    <span>PHOTO &bull; VEHICLE DETECTIONS</span>
                  </div>
                  <div className="absolute bottom-2 right-2 px-1.5 py-0.5 rounded bg-black/85 border border-slate-700/60 font-mono text-[8px] text-cyan-300 pointer-events-none">
                    BOUNDING BOXES: {vehiclesA.length}
                  </div>
                </div>
              </div>
            ) : (
              /* SINGLE VIEWPORT: either Full Video or Full Photo */
              <div className="cctv-viewport relative aspect-video bg-black flex items-center justify-center">
                {displayMode === 'video' ? (
                  <img
                    src="/api/stream/cam_a"
                    alt="Camera A Live Stream"
                    className="w-full h-full object-contain"
                  />
                ) : cameraA?.frame_b64 ? (
                  <img
                    src={cameraA.frame_b64}
                    alt="Camera A Feed"
                    className="w-full h-full object-contain"
                  />
                ) : (
                  <div className="text-slate-500 text-xs font-mono">Awaiting Camera A Stream...</div>
                )}

                {/* In-Frame HUD Watermarks */}
                <div className="absolute top-2.5 right-2.5 px-2 py-0.5 rounded bg-black/80 border border-slate-700/60 font-mono text-[9px] text-cyan-300 pointer-events-none flex items-center gap-1.5 shadow">
                  <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
                  <span>ENTRY GATEWAY &bull; SENSOR 01</span>
                </div>

                <div className="absolute bottom-2.5 left-2.5 px-2 py-0.5 rounded bg-black/80 border border-slate-700/60 font-mono text-[9px] text-slate-300 pointer-events-none flex items-center gap-1.5 shadow">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                  <span>CAM-01 // INGRESS // 850M UPSTREAM {displayMode === 'video' ? '// RTSP LIVE STREAM' : '// HIGH-RES PHOTO CAPTURE'}</span>
                </div>
              </div>
            )}

            {/* Camera A Tracklet Strip */}
            <div className="p-3 bg-[var(--bg-panel)] border-t border-[var(--border-color)]">
              <div className="text-[11px] font-bold text-slate-300 uppercase tracking-wider mb-2.5 flex items-center justify-between">
                <span>Camera A Detected Vehicle Signatures</span>
                <span className="font-mono text-[10px] text-blue-400">Indian Mixed Fleet</span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-h-[250px] overflow-y-auto pr-1">
                {vehiclesA.map((v) => {
                  const isSelected = selectedTrackA === v.track_id;
                  return (
                    <div
                      key={v.track_id}
                      onClick={() => onSelectTrackA(isSelected ? null : v.track_id)}
                      className={`p-2.5 rounded-md border cursor-pointer transition-all flex items-center gap-3 ${
                        isSelected
                          ? 'bg-[var(--bg-surface-active)] border-blue-500 ring-1 ring-blue-500 shadow-md'
                          : 'bg-[var(--bg-main)] border-[var(--border-color)] hover:border-[var(--border-light)] hover:bg-[var(--bg-surface)]'
                      }`}
                    >
                      {v.crop_b64 ? (
                        <img
                          src={v.crop_b64}
                          alt={v.track_id}
                          className="w-12 h-12 object-cover rounded-md border border-[#334155] bg-black flex-shrink-0 shadow-sm"
                        />
                      ) : (
                        <div className="w-12 h-12 bg-slate-800 rounded-md flex-shrink-0"></div>
                      )}

                      <div className="min-w-0 flex-1">
                        <div className="flex items-center justify-between">
                          <span className="font-mono font-bold text-xs text-white truncate">
                            {v.track_id}
                          </span>
                          <span className="text-[10px] font-mono text-slate-400 bg-slate-900 px-1 py-0.2 rounded">
                            t={v.exit_time}s
                          </span>
                        </div>
                        <div className="text-[11px] text-slate-300 truncate font-semibold mt-0.5">
                          {v.vehicle_type}
                        </div>
                        <div className="flex items-center gap-1.5 mt-1">
                          <span
                            className="w-2.5 h-2.5 rounded-full border border-black/60 inline-block shadow-sm"
                            style={{ backgroundColor: v.dominant_hex }}
                          ></span>
                          <span className="text-[10px] text-slate-400 truncate">
                            {v.dominant_color}
                          </span>
                        </div>
                      </div>

                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onInspectVehicle(v, 'A');
                        }}
                        className="btn btn-sm text-[10px] px-2 py-0.5 shadow-sm"
                        title="Inspect multi-stripe color histogram and geometric aspect ratio"
                      >
                        Inspect
                      </button>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* CAMERA B */}
          <div className="border border-[var(--border-color)] rounded-lg bg-[var(--bg-main)] overflow-hidden shadow-xl transition-all">
            {/* Camera Header Bar */}
            <div className="bg-[var(--bg-panel-header)] px-3.5 py-2.5 border-b border-[var(--border-color)] flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="live-dot"></span>
                <span className="font-mono font-bold text-xs text-white tracking-wide">
                  {cameraB?.id || 'CAM-02'}: {cameraB?.name || 'Junction 5th Ave (South Exit - 850m)'}
                </span>
              </div>
              <div className="flex items-center gap-2 font-mono text-[10px] text-slate-400">
                <span className="text-cyan-400 font-semibold">{vehiclesB.length} Active Tracklets</span>
                <span>&bull;</span>
                <span className="text-emerald-400 font-bold">
                  {displayMode === 'both' ? '⚡ PHOTO + VIDEO ACTIVE' : displayMode === 'video' ? '30.0 FPS LIVE STREAM' : 'HIGH-RES PHOTO SNAPSHOT'}
                </span>
              </div>
            </div>

            {/* Viewport Area: Switches according to displayMode */}
            {displayMode === 'both' ? (
              /* SPLIT SCREEN: Live 30 FPS Video + High-Res Photo */
              <div className="grid grid-cols-1 sm:grid-cols-2 bg-black border-b border-[var(--border-color)] divide-y sm:divide-y-0 sm:divide-x divide-[var(--border-color)]">
                {/* Video Column */}
                <div className="relative aspect-video bg-black flex items-center justify-center overflow-hidden">
                  <img
                    src="/api/stream/cam_b"
                    alt="Camera B Live Stream"
                    className="w-full h-full object-contain"
                  />
                  <div className="absolute top-2 left-2 px-1.5 py-0.5 rounded bg-black/85 border border-emerald-500/70 font-mono text-[8px] text-emerald-300 pointer-events-none flex items-center gap-1">
                    <span className="live-dot"></span>
                    <span>LIVE VIDEO &bull; 30 FPS</span>
                  </div>
                  <div className="absolute bottom-2 left-2 px-1.5 py-0.5 rounded bg-black/85 border border-slate-700/60 font-mono text-[8px] text-slate-300 pointer-events-none">
                    CAM-02 // RTSP STREAM
                  </div>
                </div>

                {/* Photo Snapshot Column */}
                <div className="relative aspect-video bg-black flex items-center justify-center overflow-hidden">
                  {cameraB?.frame_b64 ? (
                    <img
                      src={cameraB.frame_b64}
                      alt="Camera B Snapshot"
                      className="w-full h-full object-contain"
                    />
                  ) : (
                    <div className="text-slate-500 text-xs font-mono">Awaiting Photo Snapshot...</div>
                  )}
                  <div className="absolute top-2 left-2 px-1.5 py-0.5 rounded bg-black/85 border border-cyan-500/70 font-mono text-[8px] text-cyan-300 pointer-events-none flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
                    <span>PHOTO &bull; VEHICLE DETECTIONS</span>
                  </div>
                  <div className="absolute bottom-2 right-2 px-1.5 py-0.5 rounded bg-black/85 border border-slate-700/60 font-mono text-[8px] text-emerald-300 pointer-events-none">
                    BOUNDING BOXES: {vehiclesB.length}
                  </div>
                </div>
              </div>
            ) : (
              /* SINGLE VIEWPORT: either Full Video or Full Photo */
              <div className="cctv-viewport relative aspect-video bg-black flex items-center justify-center">
                {displayMode === 'video' ? (
                  <img
                    src="/api/stream/cam_b"
                    alt="Camera B Live Stream"
                    className="w-full h-full object-contain"
                  />
                ) : cameraB?.frame_b64 ? (
                  <img
                    src={cameraB.frame_b64}
                    alt="Camera B Feed"
                    className="w-full h-full object-contain"
                  />
                ) : (
                  <div className="text-slate-500 text-xs font-mono">Awaiting Camera B Stream...</div>
                )}

                {/* In-Frame HUD Watermarks */}
                <div className="absolute top-2.5 right-2.5 px-2 py-0.5 rounded bg-black/80 border border-slate-700/60 font-mono text-[9px] text-emerald-300 pointer-events-none flex items-center gap-1.5 shadow">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                  <span>RE-ID GALLERY &bull; SENSOR 02</span>
                </div>

                <div className="absolute bottom-2.5 left-2.5 px-2 py-0.5 rounded bg-black/80 border border-slate-700/60 font-mono text-[9px] text-slate-300 pointer-events-none flex items-center gap-1.5 shadow">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                  <span>CAM-02 // EGRESS // +850M DOWNSTREAM {displayMode === 'video' ? '// RTSP LIVE STREAM' : '// HIGH-RES PHOTO CAPTURE'}</span>
                </div>
              </div>
            )}

            {/* Camera B Tracklet Strip */}
            <div className="p-3 bg-[var(--bg-panel)] border-t border-[var(--border-color)]">
              <div className="text-[11px] font-bold text-slate-300 uppercase tracking-wider mb-2.5 flex items-center justify-between">
                <span>Camera B Detected Vehicle Signatures</span>
                <span className="font-mono text-[10px] text-cyan-400">Re-Appearance Gallery</span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-h-[250px] overflow-y-auto pr-1">
                {vehiclesB.map((v) => {
                  const isSelected = selectedTrackB === v.track_id;
                  return (
                    <div
                      key={v.track_id}
                      onClick={() => onSelectTrackB(isSelected ? null : v.track_id)}
                      className={`p-2.5 rounded-md border cursor-pointer transition-all flex items-center gap-3 ${
                        isSelected
                          ? 'bg-[var(--bg-surface-active)] border-cyan-500 ring-1 ring-cyan-500 shadow-md'
                          : 'bg-[var(--bg-main)] border-[var(--border-color)] hover:border-[var(--border-light)] hover:bg-[var(--bg-surface)]'
                      }`}
                    >
                      {v.crop_b64 ? (
                        <img
                          src={v.crop_b64}
                          alt={v.track_id}
                          className="w-12 h-12 object-cover rounded-md border border-[#334155] bg-black flex-shrink-0 shadow-sm"
                        />
                      ) : (
                        <div className="w-12 h-12 bg-slate-800 rounded-md flex-shrink-0"></div>
                      )}

                      <div className="min-w-0 flex-1">
                        <div className="flex items-center justify-between">
                          <span className="font-mono font-bold text-xs text-white truncate">
                            {v.track_id}
                          </span>
                          <span className="text-[10px] font-mono text-slate-400 bg-slate-900 px-1 py-0.2 rounded">
                            t={v.entry_time}s
                          </span>
                        </div>
                        <div className="text-[11px] text-slate-300 truncate font-semibold mt-0.5">
                          {v.vehicle_type}
                        </div>
                        <div className="flex items-center gap-1.5 mt-1">
                          <span
                            className="w-2.5 h-2.5 rounded-full border border-black/60 inline-block shadow-sm"
                            style={{ backgroundColor: v.dominant_hex }}
                          ></span>
                          <span className="text-[10px] text-slate-400 truncate">
                            {v.dominant_color}
                          </span>
                        </div>
                      </div>

                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onInspectVehicle(v, 'B');
                        }}
                        className="btn btn-sm text-[10px] px-2 py-0.5 shadow-sm"
                        title="Inspect multi-stripe color histogram and geometric aspect ratio"
                      >
                        Inspect
                      </button>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
