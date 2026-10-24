import React, { useState, useEffect } from 'react';
import {
  fetchModelArchitecture,
  fetchModelEmbeddings,
  probeReidQuery,
  fetchTrafficOdMatrix
} from '../services/api';

export default function ModelVisualizer({ vehiclesA = [], vehiclesB = [] }) {
  const [activeTab, setActiveTab] = useState('architecture'); // 'architecture', 'embeddings', 'matrix', 'probe', 'traffic_od'
  const [archData, setArchData] = useState(null);
  const [embedData, setEmbedData] = useState(null);
  const [odData, setOdData] = useState(null);
  const [loading, setLoading] = useState(true);

  // Probe Query State
  const [selectedProbeId, setSelectedProbeId] = useState('');
  const [probeResult, setProbeResult] = useState(null);
  const [isProbing, setIsProbing] = useState(false);

  // Selected vehicle for embedding vector inspector
  const [selectedInspectVehicle, setSelectedInspectVehicle] = useState(null);

  useEffect(() => {
    loadAllModelData();
  }, []);

  const loadAllModelData = async () => {
    setLoading(true);
    try {
      const [arch, emb, od] = await Promise.all([
        fetchModelArchitecture(),
        fetchModelEmbeddings(),
        fetchTrafficOdMatrix()
      ]);
      setArchData(arch);
      setEmbedData(emb);
      setOdData(od);

      if (emb?.vehicles_a?.length > 0) {
        setSelectedInspectVehicle(emb.vehicles_a[0]);
        setSelectedProbeId(emb.vehicles_a[0].track_id);
        runProbe(emb.vehicles_a[0].track_id);
      }
    } catch (err) {
      console.error('Error loading model visualizer data:', err);
    } finally {
      setLoading(false);
    }
  };

  const runProbe = async (probeId) => {
    if (!probeId) return;
    setIsProbing(true);
    try {
      const res = await probeReidQuery(probeId);
      setProbeResult(res);
    } catch (err) {
      console.error('Probe query failed:', err);
    } finally {
      setIsProbing(false);
    }
  };

  return (
    <div className="eng-panel mb-4">
      {/* Panel Header */}
      <div className="eng-panel-header">
        <div className="eng-panel-title">
          <svg className="w-4 h-4 text-blue-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polygon points="12 2 2 7 12 12 22 7 12 2" />
            <polyline points="2 17 12 22 22 17" />
            <polyline points="2 12 12 17 22 12" />
          </svg>
          AI Re-ID Model Inspection &amp; Latent Embedding Explorer
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800">
            Neural Multi-Camera Re-ID Engine
          </span>
        </div>

        {/* View Switcher Tabs */}
        <div className="flex flex-wrap items-center gap-1.5 text-xs">
          <button
            onClick={() => setActiveTab('architecture')}
            className={`btn btn-sm ${activeTab === 'architecture' ? 'btn-primary' : ''}`}
          >
            1. Model Architecture
          </button>
          <button
            onClick={() => setActiveTab('embeddings')}
            className={`btn btn-sm ${activeTab === 'embeddings' ? 'btn-primary' : ''}`}
          >
            2. 64-Dim Latent Embeddings
          </button>
          <button
            onClick={() => setActiveTab('matrix')}
            className={`btn btn-sm ${activeTab === 'matrix' ? 'btn-primary' : ''}`}
          >
            3. Cross-Camera Cosine Matrix
          </button>
          <button
            onClick={() => setActiveTab('probe')}
            className={`btn btn-sm ${activeTab === 'probe' ? 'btn-primary' : ''}`}
          >
            4. Interactive Re-ID Probe
          </button>
          <button
            onClick={() => setActiveTab('traffic_od')}
            className={`btn btn-sm ${activeTab === 'traffic_od' ? 'btn-primary' : ''}`}
          >
            5. Indian Mixed Traffic OD Flow
          </button>
        </div>
      </div>

      <div className="eng-panel-body">
        {loading ? (
          <div className="p-8 text-center text-slate-400">
            <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
            Loading Neural Model Weights &amp; Feature Projections...
          </div>
        ) : (
          <>
            {/* TAB 1: MODEL ARCHITECTURE */}
            {activeTab === 'architecture' && archData && (
              <div className="space-y-4">
                {/* Visual Pipeline Block Diagram */}
                <div className="bg-[var(--bg-main)] p-4 rounded border border-[var(--border-color)]">
                  <div className="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider mb-3 flex items-center justify-between">
                    <span>Neural Pipeline Flowchart: Vehicle Re-Identification Without License Plates</span>
                    <span className="text-[10px] font-mono text-emerald-400">ResNet-50-IBN-a + Part-based PCB + Spatio-Temporal Layer</span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-5 gap-2.5 text-center text-xs">
                    {/* Stage 1 */}
                    <div className="bg-[var(--bg-surface)] p-3 rounded border border-[var(--border-color)] flex flex-col justify-between">
                      <div className="text-[10px] font-mono text-blue-400 font-bold mb-1">STAGE 1</div>
                      <div className="font-bold text-[var(--text-main)] text-xs">Input Tensor</div>
                      <div className="text-[11px] text-[var(--text-dim)] my-1 font-mono">128 &times; 128 &times; 3</div>
                      <div className="text-[10px] text-[var(--text-muted)]">MOG2 Bounding Box crop normalized to standard aspect</div>
                    </div>

                    {/* Stage 2 */}
                    <div className="bg-[var(--bg-surface)] p-3 rounded border border-[var(--border-color)] flex flex-col justify-between">
                      <div className="text-[10px] font-mono text-cyan-400 font-bold mb-1">STAGE 2</div>
                      <div className="font-bold text-[var(--text-main)] text-xs">CNN Backbone</div>
                      <div className="text-[11px] text-[var(--text-dim)] my-1 font-mono">ResNet-50-IBN-a</div>
                      <div className="text-[10px] text-[var(--text-muted)]">Instance-Batch Norm filters out cross-camera lighting shifts</div>
                    </div>

                    {/* Stage 3 */}
                    <div className="bg-[var(--bg-surface)] p-3 rounded border border-[var(--border-color)] flex flex-col justify-between">
                      <div className="text-[10px] font-mono text-emerald-400 font-bold mb-1">STAGE 3</div>
                      <div className="font-bold text-[var(--text-main)] text-xs">Part-Based Pooling</div>
                      <div className="text-[11px] text-[var(--text-dim)] my-1 font-mono">3 Spatial Stripes</div>
                      <div className="text-[10px] text-[var(--text-muted)]">Top 30% (Roof), Mid 45% (Body), Bot 25% (Chassis)</div>
                    </div>

                    {/* Stage 4 */}
                    <div className="bg-[var(--bg-surface)] p-3 rounded border border-[var(--border-color)] flex flex-col justify-between">
                      <div className="text-[10px] font-mono text-purple-400 font-bold mb-1">STAGE 4</div>
                      <div className="font-bold text-[var(--text-main)] text-xs">Latent Embedding</div>
                      <div className="text-[11px] text-[var(--text-dim)] my-1 font-mono">64-dim L2 Vector</div>
                      <div className="text-[10px] text-[var(--text-muted)]">Unit hypersphere projection with Triplet Margin Loss</div>
                    </div>

                    {/* Stage 5 */}
                    <div className="bg-[var(--bg-surface)] p-3 rounded border border-blue-800/60 bg-blue-950/20 flex flex-col justify-between">
                      <div className="text-[10px] font-mono text-blue-300 font-bold mb-1">STAGE 5</div>
                      <div className="font-bold text-[var(--text-main)] text-xs">Physics Gating</div>
                      <div className="text-[11px] text-[var(--text-dim)] my-1 font-mono">P(Δt | 850m, v)</div>
                      <div className="text-[10px] text-[var(--text-muted)]">Prunes impossible speeds (&lt;15 or &gt;90 km/h) &amp; reverse time</div>
                    </div>
                  </div>
                </div>

                {/* Technical Specifications Table */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-[var(--bg-surface)] p-3.5 rounded border border-[var(--border-color)]">
                    <h4 className="text-xs font-bold text-[var(--text-main)] uppercase mb-2">Backbone &amp; Metric Space</h4>
                    <table className="eng-table">
                      <tbody>
                        <tr>
                          <td className="text-[var(--text-muted)] font-mono text-[11px]">Backbone Architecture</td>
                          <td className="text-[var(--text-main)] font-mono">{archData.backbone?.name}</td>
                        </tr>
                        <tr>
                          <td className="text-[var(--text-muted)] font-mono text-[11px]">Instance-Batch Norm</td>
                          <td className="text-[var(--text-dim)]">{archData.backbone?.purpose}</td>
                        </tr>
                        <tr>
                          <td className="text-[var(--text-muted)] font-mono text-[11px]">Feature Metric</td>
                          <td className="text-[var(--text-main)] font-mono">{archData.embedding_head?.metric}</td>
                        </tr>
                        <tr>
                          <td className="text-[var(--text-muted)] font-mono text-[11px]">Loss Objective</td>
                          <td className="text-[var(--text-dim)] text-[11px]">{archData.embedding_head?.loss_function}</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>

                  <div className="bg-[var(--bg-surface)] p-3.5 rounded border border-[var(--border-color)]">
                    <h4 className="text-xs font-bold text-[var(--text-main)] uppercase mb-2">Spatial Partitioning Weights (PCB)</h4>
                    <table className="eng-table">
                      <thead>
                        <tr>
                          <th>Stripe Region</th>
                          <th>Height %</th>
                          <th>Vector Dim</th>
                          <th>Weight</th>
                        </tr>
                      </thead>
                      <tbody>
                        {archData.spatial_partitioning?.slices?.map((s, idx) => (
                          <tr key={idx}>
                            <td className="text-[var(--text-main)] font-medium">{s.name}</td>
                            <td className="font-mono text-[var(--text-muted)]">{s.height_pct}</td>
                            <td className="font-mono text-[var(--text-muted)]">{s.dim} dims</td>
                            <td className="font-mono text-emerald-400 font-bold">{Math.round(s.weight * 100)}%</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}

            {/* TAB 2: 64-DIMENSIONAL EMBEDDING INSPECTOR */}
            {activeTab === 'embeddings' && embedData && (
              <div className="space-y-4">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="text-xs text-[var(--text-muted)]">
                    Select a detected vehicle to inspect its raw 64-dimensional L2-normalized feature embedding:
                  </div>
                  <div className="flex flex-wrap items-center gap-1.5">
                    {embedData.vehicles_a?.map((v) => (
                      <button
                        key={v.track_id}
                        onClick={() => setSelectedInspectVehicle(v)}
                        className={`btn btn-sm font-mono text-[11px] ${
                          selectedInspectVehicle?.track_id === v.track_id ? 'btn-primary' : ''
                        }`}
                      >
                        {v.track_id} ({v.vehicle_type.split(' ')[0]})
                      </button>
                    ))}
                  </div>
                </div>

                {selectedInspectVehicle && (
                  <div className="bg-[var(--bg-main)] p-4 rounded border border-[var(--border-color)]">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4 pb-3 border-b border-[var(--border-color)]">
                      <div className="flex items-center gap-3">
                        {selectedInspectVehicle.crop_b64 && (
                          <img
                            src={selectedInspectVehicle.crop_b64}
                            alt={selectedInspectVehicle.track_id}
                            className="w-14 h-14 object-cover rounded border border-[var(--border-light)] bg-black"
                          />
                        )}
                        <div>
                          <div className="text-sm font-mono font-bold text-[var(--text-main)] flex items-center gap-2">
                            <span>{selectedInspectVehicle.track_id}</span>
                            <span className="badge badge-neutral text-[10px]">{selectedInspectVehicle.camera_id}</span>
                          </div>
                          <div className="text-xs text-[var(--text-muted)]">{selectedInspectVehicle.vehicle_type}</div>
                          <div className="flex items-center gap-1.5 mt-0.5 text-[11px] text-[var(--text-dim)]">
                            <span
                              className="w-2.5 h-2.5 rounded-full border border-black"
                              style={{ backgroundColor: selectedInspectVehicle.dominant_hex }}
                            ></span>
                            <span>{selectedInspectVehicle.dominant_color}</span>
                          </div>
                        </div>
                      </div>

                      <div className="text-right font-mono text-[11px] text-[var(--text-muted)]">
                        <div>Vector Norm: <strong className="text-emerald-400">1.0000 (Unit Hypersphere)</strong></div>
                        <div>Total Dimensions: <strong className="text-[var(--text-main)]">64 Floats</strong></div>
                      </div>
                    </div>

                    {/* Embedding Dimension Heatmap Bar Strip */}
                    <div className="mb-4">
                      <div className="text-[11px] font-semibold text-[var(--text-muted)] uppercase tracking-wider mb-2 flex items-center justify-between">
                        <span>Latent Feature Channel Activation Levels (64 Dims)</span>
                        <span className="text-[10px] font-mono text-[var(--text-dim)]">Color: Blue (Low) &rarr; Cyan &rarr; Emerald (High)</span>
                      </div>

                      <div className="grid grid-cols-16 sm:grid-cols-32 gap-1 p-2 bg-[var(--bg-surface)] rounded border border-[var(--border-color)]">
                        {selectedInspectVehicle.embedding_64d?.map((val, idx) => {
                          const absVal = Math.min(1.0, Math.abs(val) * 3.5);
                          return (
                            <div
                              key={idx}
                              title={`Dim [${idx}]: ${val}`}
                              className="h-7 rounded-sm flex items-center justify-center font-mono text-[8px] text-white/80 cursor-help"
                              style={{
                                backgroundColor: `rgb(${Math.round(20 + absVal * 40)}, ${Math.round(40 + absVal * 180)}, ${Math.round(180 - absVal * 80)})`
                              }}
                            >
                              {idx}
                            </div>
                          );
                        })}
                      </div>
                    </div>

                    {/* Raw Floating-Point Numerical Dump */}
                    <div>
                      <div className="text-[11px] font-semibold text-[var(--text-muted)] uppercase tracking-wider mb-1">
                        Numerical Latent Vector Array:
                      </div>
                      <div className="bg-[var(--bg-surface)] p-2.5 rounded border border-[var(--border-color)] font-mono text-[10px] text-[var(--text-main)] max-h-36 overflow-y-auto leading-relaxed">
                        [{selectedInspectVehicle.embedding_64d?.map((v, i) => (
                          <span key={i} className="inline-block mr-2 text-[var(--text-muted)]">
                            <span className="text-[var(--text-dim)]">[{i}]</span>{v.toFixed(4)}
                          </span>
                        ))}]
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* TAB 3: CROSS-CAMERA COSINE SIMILARITY MATRIX */}
            {activeTab === 'matrix' && embedData && (
              <div className="space-y-4">
                <div className="text-xs text-[var(--text-muted)]">
                  Pairwise Cosine Similarity Matrix between all <strong>Camera A Vehicles (Rows)</strong> and <strong>Camera B Vehicles (Columns)</strong>:
                </div>

                <div className="overflow-x-auto border border-[var(--border-color)] rounded bg-[var(--bg-main)]">
                  <table className="w-full text-xs text-center border-collapse">
                    <thead>
                      <tr className="bg-[var(--bg-surface)] border-b border-[var(--border-color)]">
                        <th className="p-2.5 text-left font-mono text-[var(--text-muted)] border-r border-[var(--border-color)]">
                          Camera A \ Camera B
                        </th>
                        {embedData.vehicles_b?.map((b) => (
                          <th key={b.track_id} className="p-2 font-mono text-cyan-300 min-w-[70px]">
                            {b.crop_b64 && (
                              <img src={b.crop_b64} alt={b.track_id} className="w-7 h-7 mx-auto rounded object-cover mb-1 border border-[var(--border-light)]" />
                            )}
                            <div>{b.track_id}</div>
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {embedData.vehicles_a?.map((a, rowIdx) => (
                        <tr key={a.track_id} className="border-b border-[var(--border-color)]">
                          <td className="p-2.5 text-left font-mono text-blue-300 bg-[var(--bg-surface)] border-r border-[var(--border-color)] flex items-center gap-2">
                            {a.crop_b64 && (
                              <img src={a.crop_b64} alt={a.track_id} className="w-7 h-7 rounded object-cover border border-[var(--border-light)]" />
                            )}
                            <div>
                              <div className="font-bold">{a.track_id}</div>
                              <div className="text-[10px] text-[var(--text-dim)]">{a.vehicle_type.split(' ')[0]}</div>
                            </div>
                          </td>

                          {embedData.similarity_matrix?.[rowIdx]?.map((simScore, colIdx) => {
                            const isStrong = simScore >= 0.85;
                            const isModerate = simScore >= 0.70 && simScore < 0.85;
                            return (
                              <td
                                key={colIdx}
                                className={`p-2 font-mono font-bold text-xs ${
                                  isStrong
                                    ? 'bg-emerald-950/70 text-emerald-300 border border-emerald-800'
                                    : isModerate
                                    ? 'bg-blue-950/40 text-blue-300'
                                    : 'text-[var(--text-dim)]'
                                }`}
                              >
                                {simScore.toFixed(3)}
                              </td>
                            );
                          })}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                <div className="text-[11px] text-[var(--text-muted)] flex items-center gap-4">
                  <span className="flex items-center gap-1.5">
                    <span className="w-3 h-3 rounded bg-emerald-950 border border-emerald-800"></span>
                    <span>High Similarity (&ge; 0.850) - Strong Re-ID Match Candidate</span>
                  </span>
                  <span className="flex items-center gap-1.5">
                    <span className="w-3 h-3 rounded bg-blue-950 border border-blue-800"></span>
                    <span>Moderate (&ge; 0.700)</span>
                  </span>
                  <span className="flex items-center gap-1.5">
                    <span className="w-3 h-3 rounded bg-[var(--bg-main)] border border-[var(--border-color)]"></span>
                    <span>Low / Distractor (&lt; 0.700)</span>
                  </span>
                </div>
              </div>
            )}

            {/* TAB 4: INTERACTIVE RE-ID PROBE QUERY */}
            {activeTab === 'probe' && embedData && (
              <div className="space-y-4">
                <div className="bg-[var(--bg-main)] p-3 rounded border border-[var(--border-color)] flex flex-wrap items-center gap-3">
                  <label className="text-xs font-semibold text-[var(--text-muted)]">
                    Select Probe Vehicle from Camera A:
                  </label>
                  <select
                    value={selectedProbeId}
                    onChange={(e) => {
                      setSelectedProbeId(e.target.value);
                      runProbe(e.target.value);
                    }}
                    className="bg-[var(--bg-surface)] border border-[var(--border-color)] text-[var(--text-main)] rounded px-2.5 py-1 text-xs font-mono"
                  >
                    {embedData.vehicles_a?.map((v) => (
                      <option key={v.track_id} value={v.track_id}>
                        {v.track_id} - {v.vehicle_type} ({v.dominant_color})
                      </option>
                    ))}
                  </select>

                  <button
                    onClick={() => runProbe(selectedProbeId)}
                    disabled={isProbing}
                    className="btn btn-sm btn-primary"
                  >
                    {isProbing ? 'Querying Re-ID Gallery...' : 'Run Query Probe'}
                  </button>
                </div>

                {probeResult && (
                  <div className="space-y-3">
                    <div className="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider flex items-center justify-between">
                      <span>Query Probe Results: Top Retrieved Matches across Downstream Gallery (Camera B)</span>
                      <span className="font-mono text-emerald-400 text-[11px]">
                        Rank-1 Match Confidence: {probeResult.rank_1_match ? `${Math.round(probeResult.rank_1_match.overall_confidence * 100)}%` : '--'}
                      </span>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                      {probeResult.ranked_candidates?.slice(0, 3).map((cand, idx) => (
                        <div
                          key={cand.match_id}
                          className={`p-3 rounded border ${
                            idx === 0
                              ? 'bg-[var(--bg-surface-active)] border-emerald-600 ring-1 ring-emerald-600'
                              : 'bg-[var(--bg-surface)] border-[var(--border-color)]'
                          }`}
                        >
                          <div className="flex items-center justify-between mb-2">
                            <span className={`text-xs font-mono font-bold ${idx === 0 ? 'text-emerald-400' : 'text-[var(--text-dim)]'}`}>
                              RANK-{cand.rank} {idx === 0 && '★ BEST MATCH'}
                            </span>
                            <span className="text-xs font-mono font-bold text-[var(--text-main)]">
                              {Math.round(cand.overall_confidence * 100)}% Conf
                            </span>
                          </div>

                          <div className="flex items-center gap-3">
                            {cand.target_crop_b64 && (
                              <img
                                src={cand.target_crop_b64}
                                alt={cand.target_track_id}
                                className="w-14 h-14 object-cover rounded border border-[var(--border-light)] bg-black"
                              />
                            )}
                            <div className="text-xs space-y-1">
                              <div className="font-mono font-bold text-[var(--text-main)]">{cand.target_track_id}</div>
                              <div className="text-[var(--text-muted)]">{cand.target_type}</div>
                              <div className="text-[11px] text-[var(--text-dim)]">{cand.target_color}</div>
                            </div>
                          </div>

                          <div className="mt-2.5 pt-2 border-t border-[var(--border-color)] text-[10px] font-mono text-[var(--text-dim)] space-y-0.5">
                            <div>Visual Sim: <strong className="text-[var(--text-main)]">{Math.round(cand.visual_similarity * 100)}%</strong></div>
                            <div>Physics Gating: <strong className="text-emerald-400">{cand.transit_time_sec}s ({cand.speed_kmh} km/h)</strong></div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* TAB 5: INDIAN MIXED TRAFFIC & OD FLOW */}
            {activeTab === 'traffic_od' && odData && (
              <div className="space-y-4">
                <div className="bg-[var(--bg-main)] p-3.5 rounded border border-[var(--border-color)]">
                  <h4 className="text-xs font-bold text-[var(--text-main)] uppercase mb-2">
                    Origin-Destination (OD) Corridor Flow &amp; Indian Traffic Modal Split
                  </h4>
                  <p className="text-xs text-[var(--text-muted)] mb-3">
                    Municipal traffic planning using non-plate Re-ID to construct origin-destination matrices across Indian urban arterials:
                  </p>

                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-4">
                    {Object.entries(odData.modal_split_counts || {}).map(([category, count]) => (
                      <div key={category} className="p-2.5 bg-[var(--bg-surface)] rounded border border-[var(--border-color)]">
                        <div className="text-[10px] text-[var(--text-dim)] uppercase">{category}</div>
                        <div className="text-lg font-bold font-mono text-[var(--text-main)] mt-0.5">{count} Vehicles</div>
                        <div className="text-[10px] font-mono text-blue-400">
                          {odData.modal_split_percentages?.[category] || 0}% modal split
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 p-3 bg-[var(--bg-surface)] rounded border border-[var(--border-color)] text-center">
                    <div>
                      <div className="text-[10px] text-[var(--text-dim)] uppercase">Estimated Hourly Volume</div>
                      <div className="text-base font-mono font-bold text-emerald-400">{odData.hourly_flow_rate_vph} Veh/Hr</div>
                    </div>
                    <div>
                      <div className="text-[10px] text-[var(--text-dim)] uppercase">Mean Corridor Transit</div>
                      <div className="text-base font-mono font-bold text-blue-400">{odData.mean_travel_time_sec}s</div>
                    </div>
                    <div>
                      <div className="text-[10px] text-[var(--text-dim)] uppercase">Corridor Congestion Status</div>
                      <div className="text-base font-mono font-bold text-[var(--text-main)]">{odData.congestion_status}</div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
