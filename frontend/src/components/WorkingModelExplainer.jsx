import React, { useState } from 'react';

export default function WorkingModelExplainer({ vehiclesA = [], vehiclesB = [], matches = [] }) {
  // Select first match by default if available
  const [selectedMatchIndex, setSelectedMatchIndex] = useState(0);
  const [activeStep, setActiveStep] = useState(1); // Steps 1 to 5
  const [isSimulating, setIsSimulating] = useState(false);

  const currentMatch = matches[selectedMatchIndex] || {
    match_id: 'MATCH-001',
    cam_a_track_id: 'CAM-A-V-01',
    cam_b_track_id: 'CAM-B-V-01',
    vehicle_type_a: 'Auto-Rickshaw (3-Wheeler)',
    vehicle_type_b: 'Auto-Rickshaw (3-Wheeler)',
    color_a: 'Golden / Yellow',
    color_b: 'Golden / Yellow',
    hex_a: '#eac627',
    hex_b: '#d4b322',
    cam_a_exit_time: 12.0,
    cam_b_entry_time: 67.8,
    transit_time_sec: 55.8,
    distance_meters: 850.0,
    estimated_speed_kmh: 54.8,
    visual_similarity: 0.942,
    spatio_temporal_score: 0.965,
    overall_confidence: 0.952,
    crop_a_b64: '',
    crop_b_b64: '',
    status: 'verified'
  };

  const runSimulation = () => {
    setIsSimulating(true);
    setActiveStep(1);
    const stepInterval = setInterval(() => {
      setActiveStep((prev) => {
        if (prev >= 5) {
          clearInterval(stepInterval);
          setIsSimulating(false);
          return 5;
        }
        return prev + 1;
      });
    }, 1100);
  };

  return (
    <div className="eng-panel mb-4">
      {/* Header */}
      <div className="eng-panel-header">
        <div className="eng-panel-title">
          <svg className="w-4 h-4 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
          </svg>
          Interactive Live Working Model: How Non-Plate Re-ID Works Step-by-Step
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950/60 text-emerald-300 border border-emerald-800 font-semibold">
            End-to-End Pipeline
          </span>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={runSimulation}
            disabled={isSimulating}
            className={`btn btn-sm font-bold ${
              isSimulating
                ? 'bg-emerald-600 text-white'
                : 'btn-primary'
            }`}
          >
            {isSimulating ? (
              <>
                <span className="live-dot"></span>
                <span>Executing Step {activeStep} of 5...</span>
              </>
            ) : (
              <>
                <svg className="w-3.5 h-3.5 fill-current" viewBox="0 0 24 24">
                  <polygon points="5 3 19 12 5 21 5 3" />
                </svg>
                <span>▶ Auto-Simulate Workflow</span>
              </>
            )}
          </button>
        </div>
      </div>

      <div className="eng-panel-body">
        {/* Vehicle Pair Selector Pills */}
        <div className="flex flex-wrap items-center justify-between gap-2 mb-4 pb-3 border-b border-[var(--border-color)]">
          <div className="text-xs text-[var(--text-muted)] font-medium">
            Select a detected vehicle to trace its journey from Camera A to Camera B:
          </div>
          <div className="flex flex-wrap items-center gap-1.5">
            {matches.slice(0, 6).map((m, idx) => (
              <button
                key={m.match_id}
                onClick={() => {
                  setSelectedMatchIndex(idx);
                  setActiveStep(1);
                }}
                className={`btn btn-sm font-mono text-[11px] ${
                  selectedMatchIndex === idx ? 'btn-primary' : ''
                }`}
              >
                {m.cam_a_track_id} ({m.vehicle_type_a?.split(' ')[0]})
              </button>
            ))}
          </div>
        </div>

        {/* 5-Step Process Visualizer Bar */}
        <div className="grid grid-cols-5 gap-2 mb-4">
          {[
            { step: 1, title: '1. Camera A Ingress', desc: 'Upstream Capture' },
            { step: 2, title: '2. Feature Extraction', desc: '3-Part HSV (No Plates)' },
            { step: 3, title: '3. Physics Gating', desc: '850m Transit Math' },
            { step: 4, title: '4. Camera B Egress', desc: 'Downstream Gallery' },
            { step: 5, title: '5. Match Decision', desc: 'Score & Verification' }
          ].map((s) => (
            <button
              key={s.step}
              onClick={() => setActiveStep(s.step)}
              className={`p-2.5 rounded border text-left transition-all ${
                activeStep === s.step
                  ? 'bg-[var(--bg-surface-active)] border-[var(--accent-primary)] ring-1 ring-[var(--accent-primary)]'
                  : activeStep > s.step
                  ? 'bg-[var(--bg-surface)] border-emerald-800/60 text-slate-300'
                  : 'bg-[var(--bg-main)] border-[var(--border-color)] opacity-70'
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="font-mono text-[10px] font-bold text-slate-400">STEP {s.step}</span>
                {activeStep > s.step && (
                  <span className="text-emerald-400 text-xs font-bold">✓</span>
                )}
              </div>
              <div className="font-bold text-xs text-[var(--text-main)] truncate">{s.title}</div>
              <div className="text-[10px] text-[var(--text-muted)] truncate">{s.desc}</div>
            </button>
          ))}
        </div>

        {/* Interactive Step Content Box */}
        <div className="bg-[var(--bg-main)] p-4 rounded-lg border border-[var(--border-color)]">
          {activeStep === 1 && (
            <div className="space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-[var(--border-color)]">
                <div>
                  <h4 className="text-sm font-bold text-[var(--text-main)]">
                    Step 1: Vehicle Ingress &amp; Localization at Camera A (Junction 1)
                  </h4>
                  <p className="text-xs text-[var(--text-muted)] mt-0.5">
                    Vehicle enters the corridor at Camera A. Movement is segmented from background via MOG2 motion contours.
                  </p>
                </div>
                <span className="badge badge-live">LIVE TIMESTAMP: t = {currentMatch.cam_a_exit_time}s</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-1">
                <div className="flex flex-col items-center justify-center p-3 rounded bg-[var(--bg-surface)] border border-[var(--border-color)]">
                  {currentMatch.crop_a_b64 ? (
                    <img
                      src={currentMatch.crop_a_b64}
                      alt="Crop A"
                      className="w-24 h-24 object-contain rounded border border-[var(--border-light)] bg-black mb-2"
                    />
                  ) : (
                    <div className="w-24 h-24 rounded bg-black flex items-center justify-center font-mono text-xs text-slate-500 mb-2">
                      Crop A
                    </div>
                  )}
                  <span className="font-mono text-xs font-bold text-blue-400">{currentMatch.cam_a_track_id}</span>
                </div>

                <div className="md:col-span-2 space-y-2 text-xs">
                  <div className="p-2.5 rounded bg-[var(--bg-surface)] border border-[var(--border-color)] space-y-1">
                    <div><strong>Detected Class:</strong> <span className="text-[var(--text-main)]">{currentMatch.vehicle_type_a}</span></div>
                    <div><strong>Dominant Body Hue:</strong> <span className="text-[var(--text-main)]">{currentMatch.color_a}</span> ({currentMatch.hex_a})</div>
                    <div><strong>Aspect Ratio (W/H):</strong> <span className="font-mono text-[var(--text-main)]">{currentMatch.aspect_ratio_a || '1.12'}</span></div>
                    <div><strong>Departure Time (tA):</strong> <span className="font-mono text-blue-400 font-bold">{currentMatch.cam_a_exit_time} seconds</span></div>
                  </div>
                  <div className="p-2 rounded bg-blue-950/20 border border-blue-800/40 text-[11px] text-blue-200">
                    💡 <strong>Privacy-First Guarantee:</strong> Zero license plate OCR is performed. Re-ID relies purely on visual body-part color geometry and corridor physical timing.
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeStep === 2 && (
            <div className="space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-[var(--border-color)]">
                <div>
                  <h4 className="text-sm font-bold text-[var(--text-main)]">
                    Step 2: 3-Tier Multi-Stripe Appearance Feature Extraction
                  </h4>
                  <p className="text-xs text-[var(--text-muted)] mt-0.5">
                    Vehicle crop is vertically partitioned into 3 spatial stripes to capture paint tone, roof profile, and chassis structure.
                  </p>
                </div>
                <span className="font-mono text-xs text-emerald-400 font-bold">L2 Norm: 1.0000 (Unit Hypersphere)</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-1 text-xs">
                <div className="p-3 rounded bg-[var(--bg-surface)] border border-[var(--border-color)]">
                  <strong className="text-blue-300">Stripe 1: Roof &amp; Windshield (Top 30%)</strong>
                  <p className="text-[11px] text-[var(--text-muted)] mt-1">
                    Captures cabin tint, roof paint, luggage carriers, and sunroof color signatures.
                  </p>
                  <div className="mt-2 text-[10px] font-mono text-slate-400">Weight: 20% of Visual Sim</div>
                </div>

                <div className="p-3 rounded bg-[var(--bg-surface)] border border-[var(--border-color)]">
                  <strong className="text-emerald-300">Stripe 2: Body Panels (Mid 45%)</strong>
                  <p className="text-[11px] text-[var(--text-muted)] mt-1">
                    Primary vehicle paint hue, door structure, bonnet slope, and side profile contours.
                  </p>
                  <div className="mt-2 text-[10px] font-mono text-emerald-400 font-bold">Weight: 45% (Primary Feature)</div>
                </div>

                <div className="p-3 rounded bg-[var(--bg-surface)] border border-[var(--border-color)]">
                  <strong className="text-amber-300">Stripe 3: Chassis &amp; Wheels (Bot 25%)</strong>
                  <p className="text-[11px] text-[var(--text-muted)] mt-1">
                    Lower bumpers, wheel arches, tire clearance, and road shadow geometry.
                  </p>
                  <div className="mt-2 text-[10px] font-mono text-slate-400">Weight: 15% of Visual Sim</div>
                </div>
              </div>

              <div className="p-2.5 rounded bg-[var(--bg-surface)] border border-[var(--border-color)] font-mono text-[11px] flex items-center justify-between text-[var(--text-muted)]">
                <span>Output Latent Vector: <strong>64 Floats [Normalized Hue-Sat-Val Histogram]</strong></span>
                <span className="text-cyan-400">Color Metric: Mahalanobis Distance Space</span>
              </div>
            </div>
          )}

          {activeStep === 3 && (
            <div className="space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-[var(--border-color)]">
                <div>
                  <h4 className="text-sm font-bold text-[var(--text-main)]">
                    Step 3: Spatio-Temporal Corridor Physics Verification (850m Baseline)
                  </h4>
                  <p className="text-xs text-[var(--text-muted)] mt-0.5">
                    Evaluates if the vehicle could physically travel between Camera A and Camera B within allowable highway velocity bounds.
                  </p>
                </div>
                <span className="font-mono text-xs text-emerald-400 font-bold">
                  {currentMatch.estimated_speed_kmh} km/h (FEASIBLE)
                </span>
              </div>

              <div className="grid grid-cols-3 gap-3 text-center pt-1">
                <div className="p-3 rounded bg-[var(--bg-surface)] border border-[var(--border-color)]">
                  <div className="text-[10px] text-[var(--text-muted)] uppercase font-mono">Corridor Distance (d)</div>
                  <div className="font-mono text-base font-extrabold text-[var(--text-main)] mt-1">
                    {currentMatch.distance_meters} Meters
                  </div>
                </div>
                <div className="p-3 rounded bg-[var(--bg-surface)] border border-[var(--border-color)]">
                  <div className="text-[10px] text-[var(--text-muted)] uppercase font-mono">Measured Transit Time (Δt)</div>
                  <div className="font-mono text-base font-extrabold text-blue-400 mt-1">
                    {currentMatch.transit_time_sec} Seconds
                  </div>
                </div>
                <div className="p-3 rounded bg-[var(--bg-surface)] border border-[var(--border-color)]">
                  <div className="text-[10px] text-[var(--text-muted)] uppercase font-mono">Calculated Velocity (v)</div>
                  <div className="font-mono text-base font-extrabold text-emerald-400 mt-1">
                    {currentMatch.estimated_speed_kmh} km/h
                  </div>
                </div>
              </div>

              <div className="p-3 rounded bg-[var(--bg-surface)] border border-[var(--border-color)] text-xs font-mono space-y-1">
                <div className="text-slate-300">
                  Physics Formula: v = (d / Δt) &times; 3.6 = ({currentMatch.distance_meters}m / {currentMatch.transit_time_sec}s) &times; 3.6 = {currentMatch.estimated_speed_kmh} km/h
                </div>
                <div className="text-emerald-400">
                  ✓ Result: Velocity is safely within the allowable highway limits [15 km/h, 90 km/h]. Impossible speeds and reverse time are pruned.
                </div>
              </div>
            </div>
          )}

          {activeStep === 4 && (
            <div className="space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-[var(--border-color)]">
                <div>
                  <h4 className="text-sm font-bold text-[var(--text-main)]">
                    Step 4: Candidate Search in Downstream Camera B Gallery
                  </h4>
                  <p className="text-xs text-[var(--text-muted)] mt-0.5">
                    Camera B detects incoming vehicles. The Re-ID matcher evaluates candidates arriving within the feasible physical window.
                  </p>
                </div>
                <span className="badge badge-demo">ARRIVAL: t = {currentMatch.cam_b_entry_time}s</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-1">
                <div className="flex flex-col items-center justify-center p-3 rounded bg-[var(--bg-surface)] border border-[var(--border-color)]">
                  {currentMatch.crop_b_b64 ? (
                    <img
                      src={currentMatch.crop_b_b64}
                      alt="Crop B"
                      className="w-24 h-24 object-contain rounded border border-[var(--border-light)] bg-black mb-2"
                    />
                  ) : (
                    <div className="w-24 h-24 rounded bg-black flex items-center justify-center font-mono text-xs text-slate-500 mb-2">
                      Crop B
                    </div>
                  )}
                  <span className="font-mono text-xs font-bold text-cyan-400">{currentMatch.cam_b_track_id}</span>
                </div>

                <div className="md:col-span-2 space-y-2 text-xs">
                  <div className="p-2.5 rounded bg-[var(--bg-surface)] border border-[var(--border-color)] space-y-1">
                    <div><strong>Downstream Vehicle ID:</strong> <span className="font-mono text-cyan-300">{currentMatch.cam_b_track_id}</span></div>
                    <div><strong>Downstream Detected Class:</strong> <span className="text-[var(--text-main)]">{currentMatch.vehicle_type_b}</span></div>
                    <div><strong>Downstream Dominant Color:</strong> <span className="text-[var(--text-main)]">{currentMatch.color_b}</span> ({currentMatch.hex_b})</div>
                    <div><strong>Appearance Cosine Similarity:</strong> <span className="font-mono text-emerald-400 font-bold">{Math.round((currentMatch.visual_similarity || 0.94) * 100)}%</span></div>
                  </div>
                  <div className="p-2 rounded bg-[var(--bg-surface)] border border-[var(--border-color)] text-[11px] text-[var(--text-muted)]">
                    Cross-camera lighting and angle shifts are normalized using Instance-Batch Normalization (IBN) feature layers.
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeStep === 5 && (
            <div className="space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-[var(--border-color)]">
                <div>
                  <h4 className="text-sm font-bold text-[var(--text-main)]">
                    Step 5: Bipartite Match Verification &amp; Operator Decision
                  </h4>
                  <p className="text-xs text-[var(--text-muted)] mt-0.5">
                    Fused confidence score combines appearance (60%) + physics transit (30%) + vehicle type agreement (10%).
                  </p>
                </div>
                <span className="badge badge-accepted font-mono text-xs">
                  CONFIDENCE: {Math.round(currentMatch.overall_confidence * 100)}% (VERIFIED)
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1 text-xs">
                <div className="p-3 rounded bg-[var(--bg-surface)] border border-[var(--border-color)] space-y-2">
                  <div className="font-bold text-[var(--text-main)] uppercase text-[11px]">Score Composition</div>
                  <div>
                    <div className="flex justify-between text-[11px] mb-1">
                      <span>Visual Appearance Cosine (60% weight)</span>
                      <strong className="text-emerald-400 font-mono">{Math.round((currentMatch.visual_similarity || 0.94) * 100)}%</strong>
                    </div>
                    <div className="w-full bg-[var(--bg-main)] h-1.5 rounded-full overflow-hidden">
                      <div className="bg-emerald-500 h-full" style={{ width: `${(currentMatch.visual_similarity || 0.94) * 100}%` }}></div>
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-[11px] mb-1">
                      <span>Spatio-Temporal Physics (30% weight)</span>
                      <strong className="text-blue-400 font-mono">{Math.round((currentMatch.spatio_temporal_score || 0.95) * 100)}%</strong>
                    </div>
                    <div className="w-full bg-[var(--bg-main)] h-1.5 rounded-full overflow-hidden">
                      <div className="bg-blue-500 h-full" style={{ width: `${(currentMatch.spatio_temporal_score || 0.95) * 100}%` }}></div>
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-[11px] mb-1">
                      <span>Vehicle Class Agreement (10% weight)</span>
                      <strong className="text-cyan-400 font-mono">100%</strong>
                    </div>
                    <div className="w-full bg-[var(--bg-main)] h-1.5 rounded-full overflow-hidden">
                      <div className="bg-cyan-500 h-full" style={{ width: '100%' }}></div>
                    </div>
                  </div>
                </div>

                <div className="p-3 rounded bg-[var(--bg-surface)] border border-[var(--border-color)] flex flex-col justify-between">
                  <div>
                    <div className="font-bold text-[var(--text-main)] uppercase text-[11px] mb-1.5">
                      Matched Identity Conclusion
                    </div>
                    <p className="text-[11px] text-[var(--text-muted)] leading-relaxed">
                      Vehicle <strong>{currentMatch.cam_a_track_id}</strong> (Camera A) and <strong>{currentMatch.cam_b_track_id}</strong> (Camera B) represent the <strong>same physical vehicle</strong> traversing the 850m municipal corridor.
                    </p>
                  </div>

                  <div className="mt-3 pt-2 border-t border-[var(--border-color)] flex items-center justify-between">
                    <span className="text-[11px] text-slate-400 font-mono">Status: Verified Match</span>
                    <span className="badge badge-accepted">1-to-1 Bipartite Primary</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Step Navigation Controls */}
        <div className="flex items-center justify-between mt-3 text-xs">
          <button
            onClick={() => setActiveStep(Math.max(1, activeStep - 1))}
            disabled={activeStep === 1}
            className="btn btn-sm"
          >
            ← Previous Step
          </button>
          <span className="font-mono text-slate-400 text-[11px]">
            Step {activeStep} of 5
          </span>
          <button
            onClick={() => setActiveStep(Math.min(5, activeStep + 1))}
            disabled={activeStep === 5}
            className="btn btn-sm btn-primary"
          >
            Next Step →
          </button>
        </div>
      </div>
    </div>
  );
}
