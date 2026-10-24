import React, { useState } from 'react';

export default function MethodologyModal({ onClose }) {
  const [activeSection, setActiveSection] = useState('problem_statement'); // 'problem_statement', 'overview', 'methodology', 'limitations'

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content max-w-3xl" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="flex items-center gap-2">
            <svg className="w-4 h-4 text-blue-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
              <line x1="16" y1="13" x2="8" y2="13" />
              <line x1="16" y1="17" x2="8" y2="17" />
              <polyline points="10 9 9 9 8 9" />
            </svg>
            <h3 className="text-sm font-bold uppercase tracking-wider text-white">
              Track 05 &bull; SC-01 Problem Statement &amp; Methodology
            </h3>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white font-mono text-sm">
            ✕
          </button>
        </div>

        {/* Section Navigation Tabs */}
        <div className="bg-[var(--bg-panel-header)] px-4 py-2 border-b border-[var(--border-color)] flex items-center gap-2 text-xs flex-wrap">
          <button
            onClick={() => setActiveSection('problem_statement')}
            className={`btn btn-sm ${activeSection === 'problem_statement' ? 'bg-indigo-600 text-white font-bold' : ''}`}
          >
            📋 Official SC-01 Statement
          </button>
          <button
            onClick={() => setActiveSection('overview')}
            className={`btn btn-sm ${activeSection === 'overview' ? 'btn-primary' : ''}`}
          >
            1. System Approach
          </button>
          <button
            onClick={() => setActiveSection('methodology')}
            className={`btn btn-sm ${activeSection === 'methodology' ? 'btn-primary' : ''}`}
          >
            2. Multi-Stage Methodology
          </button>
          <button
            onClick={() => setActiveSection('limitations')}
            className={`btn btn-sm ${activeSection === 'limitations' ? 'btn-primary' : ''}`}
          >
            3. Known Limitations
          </button>
        </div>

        <div className="modal-body space-y-4 text-xs leading-relaxed text-[var(--text-muted)] max-h-[70vh] overflow-y-auto">
          {activeSection === 'problem_statement' && (
            <div className="space-y-3.5">
              <div className="bg-[var(--bg-main)] p-4 rounded-lg border border-blue-800/80 shadow-md">
                <div className="flex items-center gap-2 mb-2">
                  <span className="px-2 py-0.5 rounded bg-blue-600 text-white font-mono font-bold text-[10px] uppercase">
                    Track 05 &bull; Smart Cities
                  </span>
                  <span className="px-2 py-0.5 rounded bg-indigo-900 text-indigo-200 border border-indigo-700 font-mono font-bold text-[10px]">
                    SC-01
                  </span>
                </div>
                <h4 className="text-sm font-black text-white mb-2 uppercase tracking-wide">
                  Multi-Camera Vehicle Re-Identification
                </h4>

                <div className="p-3 rounded bg-[var(--bg-surface)] border border-[var(--border-color)] mb-3">
                  <div className="text-[10px] uppercase font-mono text-cyan-400 font-bold mb-1">
                    Problem Statement
                  </div>
                  <p className="text-slate-200 leading-relaxed font-medium">
                    &ldquo;Cities plan roads and public transport using outdated surveys of where journeys begin and end. Using footage from multiple non-overlapping cameras, detect, track and re-identify vehicles across cameras to estimate traffic flows between them, without reading number plates.&rdquo;
                  </p>
                </div>

                <div className="p-3 rounded bg-[var(--bg-surface)] border border-[var(--border-color)] mb-3">
                  <div className="text-[10px] uppercase font-mono text-amber-400 font-bold mb-1">
                    Explanation
                  </div>
                  <p className="text-slate-300 leading-relaxed">
                    &ldquo;Number-plate recognition is prohibited, so vehicles must be matched by visual appearance. Indian traffic is dense and mixed (two-wheelers, autorickshaws, buses, cars), with heavy occlusion and many near-identical vehicles.
                    Cameras differ in viewing angle and lighting. Travel time between cameras helps decide which matches are plausible.&rdquo;
                  </p>
                </div>

                <div className="p-3 rounded bg-[var(--bg-surface)] border border-[var(--border-color)]">
                  <div className="text-[10px] uppercase font-mono text-emerald-400 font-bold mb-2">
                    Key Challenges Addressed
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-start gap-2">
                      <span className="text-emerald-400 font-bold font-mono">✓</span>
                      <div>
                        <strong className="text-white">1. Tracking vehicles in dense, mixed traffic:</strong>
                        <span className="text-slate-300 ml-1">
                          Evaluated on mixed Indian fleet (Two-Wheelers, Auto-Rickshaws, Cars, Commercial Mini-Trucks, SUVs, Buses) with dynamic bounding box scale filtering.
                        </span>
                      </div>
                    </div>

                    <div className="flex items-start gap-2">
                      <span className="text-emerald-400 font-bold font-mono">✓</span>
                      <div>
                        <strong className="text-white">2. Handling appearance changes between cameras:</strong>
                        <span className="text-slate-300 ml-1">
                          Solved using Instance-Batch Normalization (IBN) and 3-part spatial stripe decomposition (Roof / Body / Chassis) in illumination-invariant HSV space.
                        </span>
                      </div>
                    </div>

                    <div className="flex items-start gap-2">
                      <span className="text-emerald-400 font-bold font-mono">✓</span>
                      <div>
                        <strong className="text-white">3. Distinguishing nearly identical vehicles:</strong>
                        <span className="text-slate-300 ml-1">
                          Solved using the corridor Spatio-Temporal Physics Gating layer: <code className="text-cyan-300">v = (d / &Delta;t) * 3.6</code>. Visually identical clones outside the feasible speed envelope are pruned.
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeSection === 'overview' && (
            <div className="space-y-3">
              <div className="bg-[var(--bg-main)] p-3.5 rounded border border-[var(--border-color)]">
                <h4 className="text-sm font-bold text-[var(--text-main)] mb-1">
                  The Problem: Non-Overlapping Surveillance Without License Plates
                </h4>
                <p>
                  In municipal and highway surveillance, cameras are positioned hundreds of meters apart (non-overlapping fields of view), separated by blind zones. Traditional continuous optical tracking fails across disjoint cameras.
                </p>
                <p className="mt-2">
                  While license plate readers (ALPR) exist, they are frequently unusable in realistic conditions:
                </p>
                <ul className="list-disc list-inside mt-1.5 space-y-1 text-[var(--text-dim)]">
                  <li>Standard CCTV resolution is too coarse to resolve small character fonts at a distance.</li>
                  <li>Headlight glare, high-speed motion blur, dirt, and adverse weather obscure plates.</li>
                  <li>Privacy regulations (e.g., GDPR, DPDP Act) increasingly restrict constant plate OCR logging across general citizen movement.</li>
                </ul>
              </div>

              <div className="bg-[var(--bg-surface)] p-3.5 rounded border border-[var(--border-color)]">
                <h4 className="text-sm font-bold text-[var(--text-main)] mb-1">
                  Our Engineering Approach
                </h4>
                <p>
                  CityTrack AI solves cross-camera vehicle association using <strong>privacy-preserving visual appearance signatures</strong> coupled with <strong>spatio-temporal physics constraints</strong>:
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mt-2">
                  <div className="p-2.5 bg-[var(--bg-main)] rounded border border-[var(--border-color)]">
                    <strong className="text-blue-400">1. Appearance Signature</strong>
                    <p className="text-[11px] text-[var(--text-muted)] mt-0.5">
                      Extracts 3-tier vertical spatial color histograms in illumination-invariant HSV color space and geometric aspect ratio.
                    </p>
                  </div>
                  <div className="p-2.5 bg-[var(--bg-main)] rounded border border-[var(--border-color)]">
                    <strong className="text-emerald-400">2. Physics Gating</strong>
                    <p className="text-[11px] text-[var(--text-muted)] mt-0.5">
                      Evaluates physical transit time Δt = tB - tA against corridor distance (d = 850m) and feasible speed limits (15 to 90 km/h).
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeSection === 'methodology' && (
            <div className="space-y-3">
              <div className="bg-[var(--bg-main)] p-3.5 rounded border border-[var(--border-color)]">
                <h4 className="text-sm font-bold text-[var(--text-main)] mb-1">
                  Pipeline Architecture &amp; Mathematical Formulation
                </h4>
                <div className="space-y-3 mt-2">
                  <div>
                    <strong className="text-blue-400">Step 1: Vehicle Detection &amp; Localization</strong>
                    <p className="text-[var(--text-muted)] mt-0.5">
                      Moving vehicles are localized using Gaussian Mixture-based Background Subtraction (MOG2) with morphological closing. Bounding boxes are filtered by aspect ratio bounds (0.5 &le; W/H &le; 3.5) and minimum contour area.
                    </p>
                  </div>

                  <div>
                    <strong className="text-blue-400">Step 2: Single-Camera Tracking (Tracklets)</strong>
                    <p className="text-[var(--text-muted)] mt-0.5">
                      Detections across successive video frames are associated using spatial IoU (Intersection-over-Union &ge; 0.25). Each tracklet records entry timestamp t_entry, exit timestamp t_exit, trajectory vector, and preserves the highest-resolution vehicle crop.
                    </p>
                  </div>

                  <div>
                    <strong className="text-blue-400">Step 3: Multi-Stripe Appearance Feature Extraction</strong>
                    <p className="text-[var(--text-muted)] mt-0.5">
                      To prevent false matches between multi-tone vehicles (e.g. black roof on white car vs white roof on black car), each vehicle crop is segmented into 3 horizontal stripes:
                    </p>
                    <ul className="list-disc list-inside mt-1 text-[var(--text-muted)] pl-2">
                      <li>Top 30% (Roof, Cabin, Glass tint) &bull; Weight: 20%</li>
                      <li>Mid 45% (Main body paint, doors, hood) &bull; Weight: 45%</li>
                      <li>Bottom 25% (Bumpers, tire arches, chassis) &bull; Weight: 15%</li>
                      <li>Global Hue-Sat histogram &bull; Weight: 20%</li>
                    </ul>
                  </div>

                  <div>
                    <strong className="text-blue-400">Step 4: Spatio-Temporal Constraint Filtering</strong>
                    <p className="text-[var(--text-muted)] mt-0.5">
                      For corridor distance d and speed bounds [v_min, v_max]:
                    </p>
                    <p className="font-mono text-[11px] text-[var(--text-main)] mt-1 bg-[var(--bg-surface)] p-2 rounded border border-[var(--border-color)]">
                      Δt = t_B(entry) - t_A(exit) &isin; [d / v_max, d / v_min]
                    </p>
                    <p className="text-[var(--text-muted)] mt-1">
                      Pairs with Δt &le; 0 (chronological impossibility) are automatically pruned. Feasible transit times receive a Gaussian proximity score.
                    </p>
                  </div>

                  <div>
                    <strong className="text-blue-400">Step 5: Bipartite Confidence Scoring &amp; Operator Review</strong>
                    <p className="text-[var(--text-muted)] mt-0.5">
                      Final candidate score is a weighted fusion:
                    </p>
                    <p className="font-mono text-[11px] text-[var(--text-main)] mt-1 bg-[var(--bg-surface)] p-2 rounded border border-[var(--border-color)]">
                      Confidence = 0.60 &times; Sim(Appearance) + 0.30 &times; Score(SpatioTemporal) + 0.10 &times; Match(Type)
                    </p>
                    <p className="text-[var(--text-muted)] mt-1">
                      Candidates are surfaced to the human reviewer for explicit acceptance or rejection, ensuring transparency and accountable traffic governance.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeSection === 'limitations' && (
            <div className="space-y-3">
              <div className="bg-[var(--bg-main)] p-3.5 rounded border border-[var(--border-color)]">
                <h4 className="text-sm font-bold text-[var(--text-main)] mb-1">
                  Documented Engineering Limitations
                </h4>
                <p className="text-[var(--text-muted)]">
                  As an engineering project, we document known physical and computer vision constraints rather than claiming unrealistic 100% automated accuracy:
                </p>

                <div className="space-y-2.5 mt-3">
                  <div className="p-3 bg-[var(--bg-surface)] rounded border border-[var(--border-color)]">
                    <strong className="text-rose-400">1. Illumination &amp; Shadow Disparities</strong>
                    <p className="text-[var(--text-muted)] text-[11px] mt-0.5">
                      Cameras facing different orientations experience different sun angles, tree shadows, and cloud cover. While HSV color space isolates Hue from Value/Intensity, severe shadows or nighttime low-lux conditions degrade color fidelity.
                    </p>
                  </div>

                  <div className="p-3 bg-[var(--bg-surface)] rounded border border-[var(--border-color)]">
                    <strong className="text-rose-400">2. Visually Identical Fleet Vehicles</strong>
                    <p className="text-[var(--text-muted)] text-[11px] mt-0.5">
                      Two white sedans of identical make (e.g. taxi fleets, municipal cars) have near-identical visual embeddings. In dense traffic, visual Re-ID alone cannot separate them without spatio-temporal transit bounds or human operator review.
                    </p>
                  </div>

                  <div className="p-3 bg-[var(--bg-surface)] rounded border border-[var(--border-color)]">
                    <strong className="text-rose-400">3. Lateral Turns &amp; Side Street Diversions</strong>
                    <p className="text-[var(--text-muted)] text-[11px] mt-0.5">
                      Vehicles exiting Camera A may turn into side alleys or parking lots before reaching Camera B. Conversely, vehicles can enter the corridor midway. Our benchmark includes negative control cases (V-06 and V-07) to explicitly handle diverted traffic.
                    </p>
                  </div>

                  <div className="p-3 bg-[var(--bg-surface)] rounded border border-[var(--border-color)]">
                    <strong className="text-rose-400">4. Heavy Occlusion in Multi-Lane Traffic</strong>
                    <p className="text-[var(--text-muted)] text-[11px] mt-0.5">
                      High-profile commercial trucks or buses can temporarily occlude compact cars in adjacent lanes, causing fragmented tracklets or incomplete bounding boxes.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button onClick={onClose} className="btn btn-sm btn-primary">
            Close Reference
          </button>
        </div>
      </div>
    </div>
  );
}
