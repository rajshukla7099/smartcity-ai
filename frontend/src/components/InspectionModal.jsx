import React from 'react';

export default function InspectionModal({ match, vehicle, cameraSide, onClose }) {
  if (!match && !vehicle) return null;

  // Mode 1: Inspected from match candidate (pair comparison)
  // Mode 2: Inspected from single vehicle tracklet
  const isMatchMode = !!match;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="flex items-center gap-2">
            <svg className="w-4 h-4 text-blue-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="11" cy="11" r="8" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
            <h3 className="text-sm font-bold uppercase tracking-wider text-white">
              {isMatchMode
                ? `Vehicle Re-ID Feature Inspection: ${match.match_id}`
                : `Single Vehicle Appearance Profile: ${vehicle.track_id} (Camera ${cameraSide})`}
            </h3>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white font-mono text-sm">
            ✕
          </button>
        </div>

        <div className="modal-body space-y-4">
          {isMatchMode ? (
            <>
              {/* Paired Vehicle Crops Comparison */}
              <div className="grid grid-cols-2 gap-4 bg-[var(--bg-main)] p-3 rounded border border-[var(--border-color)]">
                {/* Camera A Side */}
                <div>
                  <div className="text-xs font-mono font-bold text-blue-400 mb-1.5 flex items-center justify-between">
                    <span>Camera A (Upstream Entry)</span>
                    <span className="text-[var(--text-main)]">{match.cam_a_track_id}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    {match.crop_a_b64 && (
                      <img
                        src={match.crop_a_b64}
                        alt="Cam A"
                        className="w-20 h-20 object-cover rounded border border-[var(--border-light)] bg-black"
                      />
                    )}
                    <div className="text-xs space-y-1">
                      <div>Type: <strong className="text-[var(--text-main)]">{match.vehicle_type_a}</strong></div>
                      <div className="flex items-center gap-1.5">
                        <span>Color:</span>
                        <span
                          className="w-3 h-3 rounded-full border border-black/50"
                          style={{ backgroundColor: match.hex_a }}
                        ></span>
                        <span className="text-[var(--text-muted)]">{match.color_a}</span>
                      </div>
                      <div>Aspect Ratio (W/H): <strong className="text-[var(--text-main)] font-mono">{match.aspect_ratio_a}</strong></div>
                      <div>Exit Time: <strong className="text-[var(--text-main)] font-mono">t = {match.cam_a_exit_time}s</strong></div>
                    </div>
                  </div>
                </div>

                {/* Camera B Side */}
                <div>
                  <div className="text-xs font-mono font-bold text-cyan-400 mb-1.5 flex items-center justify-between">
                    <span>Camera B (Downstream Exit)</span>
                    <span className="text-[var(--text-main)]">{match.cam_b_track_id}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    {match.crop_b_b64 && (
                      <img
                        src={match.crop_b_b64}
                        alt="Cam B"
                        className="w-20 h-20 object-cover rounded border border-[var(--border-light)] bg-black"
                      />
                    )}
                    <div className="text-xs space-y-1">
                      <div>Type: <strong className="text-[var(--text-main)]">{match.vehicle_type_b}</strong></div>
                      <div className="flex items-center gap-1.5">
                        <span>Color:</span>
                        <span
                          className="w-3 h-3 rounded-full border border-black/50"
                          style={{ backgroundColor: match.hex_b }}
                        ></span>
                        <span className="text-[var(--text-muted)]">{match.color_b}</span>
                      </div>
                      <div>Aspect Ratio (W/H): <strong className="text-[var(--text-main)] font-mono">{match.aspect_ratio_b}</strong></div>
                      <div>Entry Time: <strong className="text-[var(--text-main)] font-mono">t = {match.cam_b_entry_time}s</strong></div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Multi-Stripe Appearance Partition Breakdown */}
              <div className="bg-[var(--bg-surface)] border border-[var(--border-color)] p-3 rounded">
                <h4 className="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider mb-2 flex items-center justify-between">
                  <span>3-Tier Spatial Appearance Feature Partition</span>
                  <span className="text-[10px] text-[var(--text-dim)] font-mono">HSV Normalized Histograms</span>
                </h4>
                <div className="space-y-2 text-xs">
                  {/* Top Stripe */}
                  <div className="p-2 bg-[var(--bg-main)] rounded border border-[var(--border-color)] flex items-center justify-between">
                    <div>
                      <strong className="text-blue-300">Stripe 1: Roof &amp; Cabin (Top 30% y-axis)</strong>
                      <div className="text-[11px] text-[var(--text-muted)]">Captures roof paint, roof rails, sun-roof, and windshield tint.</div>
                    </div>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[var(--bg-surface-active)] text-[var(--text-muted)]">
                      Weight: 20%
                    </span>
                  </div>

                  {/* Mid Stripe */}
                  <div className="p-2 bg-[var(--bg-main)] rounded border border-[var(--border-color)] flex items-center justify-between">
                    <div>
                      <strong className="text-emerald-300">Stripe 2: Body Panels &amp; Hood (Mid 45% y-axis)</strong>
                      <div className="text-[11px] text-[var(--text-muted)]">Primary vehicle body paint hue, door panels, and side profile.</div>
                    </div>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950/60 text-emerald-300 border border-emerald-800">
                      Weight: 45% (Highest)
                    </span>
                  </div>

                  {/* Bottom Stripe */}
                  <div className="p-2 bg-[var(--bg-main)] rounded border border-[var(--border-color)] flex items-center justify-between">
                    <div>
                      <strong className="text-amber-300">Stripe 3: Chassis, Bumpers &amp; Wheels (Bot 25% y-axis)</strong>
                      <div className="text-[11px] text-[var(--text-muted)]">Lower bumper contour, tire wheel arches, and road shadow profile.</div>
                    </div>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[var(--bg-surface-active)] text-[var(--text-muted)]">
                      Weight: 15%
                    </span>
                  </div>
                </div>
              </div>

              {/* Spatio-Temporal Physics Calculation */}
              <div className="bg-[var(--bg-surface)] border border-[var(--border-color)] p-3 rounded">
                <h4 className="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider mb-2">
                  Corridor Spatio-Temporal Velocity Verification
                </h4>
                <div className="grid grid-cols-3 gap-3 text-center bg-[var(--bg-main)] p-2.5 rounded border border-[var(--border-color)]">
                  <div>
                    <div className="text-[10px] text-[var(--text-muted)] uppercase">Corridor Distance (d)</div>
                    <div className="font-mono text-sm font-bold text-[var(--text-main)]">{match.distance_meters} m</div>
                  </div>
                  <div>
                    <div className="text-[10px] text-[var(--text-muted)] uppercase">Elapsed Time (Δt)</div>
                    <div className="font-mono text-sm font-bold text-blue-400">{match.transit_time_sec} s</div>
                  </div>
                  <div>
                    <div className="text-[10px] text-[var(--text-muted)] uppercase">Estimated Velocity (v)</div>
                    <div className="font-mono text-sm font-bold text-emerald-400">{match.estimated_speed_kmh} km/h</div>
                  </div>
                </div>
                <div className="text-[11px] text-[var(--text-muted)] mt-2 font-mono">
                  Physics Check: {match.estimated_speed_kmh >= 15 && match.estimated_speed_kmh <= 90
                    ? `✓ Plausible corridor velocity within allowable highway limits [15 km/h, 90 km/h].`
                    : `⚠ Velocity is outside nominal free-flow speed envelope.`}
                </div>
              </div>
            </>
          ) : (
            // Single Vehicle Inspector Mode
            <div className="space-y-3">
              <div className="flex items-center gap-4 bg-[var(--bg-main)] p-3 rounded border border-[var(--border-color)]">
                {vehicle.crop_b64 && (
                  <img
                    src={vehicle.crop_b64}
                    alt={vehicle.track_id}
                    className="w-24 h-24 object-cover rounded border border-[var(--border-light)] bg-black"
                  />
                )}
                <div className="text-xs space-y-1">
                  <div>Track ID: <strong className="text-[var(--text-main)] font-mono text-sm">{vehicle.track_id}</strong></div>
                  <div>Camera ID: <strong className="text-[var(--text-main)]">{vehicle.camera_id}</strong></div>
                  <div>Class: <strong className="text-[var(--text-main)]">{vehicle.vehicle_type}</strong></div>
                  <div className="flex items-center gap-1.5">
                    <span>Dominant Color:</span>
                    <span
                      className="w-3 h-3 rounded-full border border-black/50"
                      style={{ backgroundColor: vehicle.dominant_hex }}
                    ></span>
                    <span className="text-[var(--text-muted)]">{vehicle.dominant_color} ({vehicle.dominant_hex})</span>
                  </div>
                  <div>Aspect Ratio (W/H): <strong className="text-[var(--text-main)] font-mono">{vehicle.aspect_ratio}</strong></div>
                  <div>Presence Window: <strong className="text-[var(--text-main)] font-mono">t = {vehicle.entry_time}s &rarr; {vehicle.exit_time}s</strong></div>
                </div>
              </div>
              <div className="text-xs text-[var(--text-muted)] p-2 bg-[var(--bg-surface)] rounded border border-[var(--border-color)]">
                Non-overlapping surveillance Re-ID correlates this appearance feature vector with vehicle ingress timestamps in downstream sensors.
              </div>
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button onClick={onClose} className="btn btn-sm btn-primary">
            Close Inspector
          </button>
        </div>
      </div>
    </div>
  );
}
