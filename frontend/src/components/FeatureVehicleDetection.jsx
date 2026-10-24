import React, { useState } from 'react';

export default function FeatureVehicleDetection({ cameraA, cameraB, onOpenUpload }) {
  const [selectedCamera, setSelectedCamera] = useState('cam_a'); // 'cam_a' or 'cam_b'
  const [filterClass, setFilterClass] = useState('all');

  const currentCam = selectedCamera === 'cam_a' ? cameraA : cameraB;
  const vehicles = currentCam?.vehicles || [];

  // Vehicle Categories for Indian Traffic
  const categories = [
    { key: 'all', label: 'All Vehicles', icon: '🚦' },
    { key: 'car', label: 'Cars', icon: '🚗' },
    { key: 'bike', label: 'Bikes / Two-Wheelers', icon: '🛵' },
    { key: 'auto', label: 'Auto-Rickshaws', icon: '🛺' },
    { key: 'truck', label: 'Commercial Trucks', icon: '🚚' },
    { key: 'bus', label: 'Buses', icon: '🚌' }
  ];

  const matchesCategory = (v, catKey) => {
    if (catKey === 'all') return true;
    const type = (v.vehicle_type || '').toLowerCase();
    if (catKey === 'car') return type.includes('car') || type.includes('hatchback') || type.includes('sedan') || type.includes('suv');
    if (catKey === 'bike') return type.includes('two-wheeler') || type.includes('bike') || type.includes('scooter');
    if (catKey === 'auto') return type.includes('auto') || type.includes('rickshaw') || type.includes('3-wheeler');
    if (catKey === 'truck') return type.includes('truck') || type.includes('commercial');
    if (catKey === 'bus') return type.includes('bus');
    return true;
  };

  const filteredVehicles = vehicles.filter(v => matchesCategory(v, filterClass));

  // Tally counts across classes
  const counts = {
    car: vehicles.filter(v => matchesCategory(v, 'car')).length,
    bike: vehicles.filter(v => matchesCategory(v, 'bike')).length,
    auto: vehicles.filter(v => matchesCategory(v, 'auto')).length,
    truck: vehicles.filter(v => matchesCategory(v, 'truck')).length,
    bus: vehicles.filter(v => matchesCategory(v, 'bus')).length,
  };

  return (
    <div className="space-y-4">
      {/* Feature Title Banner */}
      <div className="p-4 rounded-xl bg-gradient-to-r from-blue-950 via-slate-900 to-indigo-950 border border-blue-700/60 shadow-lg flex flex-wrap items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 rounded bg-blue-600 text-white font-mono font-bold text-xs uppercase tracking-wider">
              Feature 1
            </span>
            <h2 className="text-base font-bold text-white tracking-wide">
              Vehicle Detection from Video
            </h2>
          </div>
          <p className="text-xs text-slate-300 mt-1">
            Real-time localization and multi-class detection of <strong>Cars, Bikes, Buses, Trucks, and Auto-Rickshaws</strong> using background modeling &amp; spatial contours without license plates.
          </p>
        </div>

        <button
          onClick={onOpenUpload}
          className="btn btn-sm btn-primary flex items-center gap-2 shadow-md"
        >
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="17 8 12 3 7 8" />
            <line x1="12" y1="3" x2="12" y2="15" />
          </svg>
          <span>Upload Custom Video / Photo</span>
        </button>
      </div>

      {/* Real-time Category Count Badges */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
        <div
          onClick={() => setFilterClass(filterClass === 'car' ? 'all' : 'car')}
          className={`p-3 rounded-lg border cursor-pointer transition-all ${
            filterClass === 'car'
              ? 'bg-blue-600/30 border-blue-500 ring-1 ring-blue-400'
              : 'bg-[var(--bg-panel)] border-[var(--border-color)] hover:border-slate-500'
          }`}
        >
          <div className="flex items-center justify-between text-xs text-slate-400 font-mono">
            <span>🚗 Cars / Sedans</span>
            <span className="w-2 h-2 rounded-full bg-blue-400"></span>
          </div>
          <div className="text-2xl font-black text-white font-mono mt-1">{counts.car}</div>
          <div className="text-[10px] text-slate-400 mt-0.5">Hatchback / Sedan / SUV</div>
        </div>

        <div
          onClick={() => setFilterClass(filterClass === 'bike' ? 'all' : 'bike')}
          className={`p-3 rounded-lg border cursor-pointer transition-all ${
            filterClass === 'bike'
              ? 'bg-amber-600/30 border-amber-500 ring-1 ring-amber-400'
              : 'bg-[var(--bg-panel)] border-[var(--border-color)] hover:border-slate-500'
          }`}
        >
          <div className="flex items-center justify-between text-xs text-slate-400 font-mono">
            <span>🛵 Bikes / Scooters</span>
            <span className="w-2 h-2 rounded-full bg-amber-400"></span>
          </div>
          <div className="text-2xl font-black text-white font-mono mt-1">{counts.bike}</div>
          <div className="text-[10px] text-slate-400 mt-0.5">Two-Wheeler Fleet</div>
        </div>

        <div
          onClick={() => setFilterClass(filterClass === 'auto' ? 'all' : 'auto')}
          className={`p-3 rounded-lg border cursor-pointer transition-all ${
            filterClass === 'auto'
              ? 'bg-yellow-600/30 border-yellow-500 ring-1 ring-yellow-400'
              : 'bg-[var(--bg-panel)] border-[var(--border-color)] hover:border-slate-500'
          }`}
        >
          <div className="flex items-center justify-between text-xs text-slate-400 font-mono">
            <span>🛺 Auto-Rickshaws</span>
            <span className="w-2 h-2 rounded-full bg-yellow-400"></span>
          </div>
          <div className="text-2xl font-black text-white font-mono mt-1">{counts.auto}</div>
          <div className="text-[10px] text-slate-400 mt-0.5">3-Wheeler Transit</div>
        </div>

        <div
          onClick={() => setFilterClass(filterClass === 'truck' ? 'all' : 'truck')}
          className={`p-3 rounded-lg border cursor-pointer transition-all ${
            filterClass === 'truck'
              ? 'bg-emerald-600/30 border-emerald-500 ring-1 ring-emerald-400'
              : 'bg-[var(--bg-panel)] border-[var(--border-color)] hover:border-slate-500'
          }`}
        >
          <div className="flex items-center justify-between text-xs text-slate-400 font-mono">
            <span>🚚 Trucks</span>
            <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
          </div>
          <div className="text-2xl font-black text-white font-mono mt-1">{counts.truck}</div>
          <div className="text-[10px] text-slate-400 mt-0.5">Commercial Mini-Truck</div>
        </div>

        <div
          onClick={() => setFilterClass(filterClass === 'bus' ? 'all' : 'bus')}
          className={`p-3 rounded-lg border cursor-pointer transition-all ${
            filterClass === 'bus'
              ? 'bg-purple-600/30 border-purple-500 ring-1 ring-purple-400'
              : 'bg-[var(--bg-panel)] border-[var(--border-color)] hover:border-slate-500'
          }`}
        >
          <div className="flex items-center justify-between text-xs text-slate-400 font-mono">
            <span>🚌 City Buses</span>
            <span className="w-2 h-2 rounded-full bg-purple-400"></span>
          </div>
          <div className="text-2xl font-black text-white font-mono mt-1">{counts.bus}</div>
          <div className="text-[10px] text-slate-400 mt-0.5">Heavy Transit</div>
        </div>
      </div>

      {/* Main Detection Viewport & Detected Crops */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Left: Video Feed with Detection HUD */}
        <div className="lg:col-span-7 bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-xl overflow-hidden shadow-lg">
          {/* Header Controls */}
          <div className="bg-[var(--bg-panel-header)] px-4 py-2.5 border-b border-[var(--border-color)] flex items-center justify-between flex-wrap gap-2">
            <div className="flex items-center gap-2">
              <span className="live-dot"></span>
              <span className="font-mono font-bold text-xs text-white">
                Live Video Detection Stream (30 FPS)
              </span>
            </div>

            {/* Camera Switcher */}
            <div className="flex items-center gap-1 bg-[var(--bg-main)] p-1 rounded-md border border-[var(--border-color)] text-xs font-mono">
              <button
                onClick={() => setSelectedCamera('cam_a')}
                className={`px-2.5 py-1 rounded font-bold transition-all ${
                  selectedCamera === 'cam_a' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'
                }`}
              >
                Camera A (Entry)
              </button>
              <button
                onClick={() => setSelectedCamera('cam_b')}
                className={`px-2.5 py-1 rounded font-bold transition-all ${
                  selectedCamera === 'cam_b' ? 'bg-cyan-600 text-white' : 'text-slate-400 hover:text-white'
                }`}
              >
                Camera B (Exit - 850m)
              </button>
            </div>
          </div>

          {/* Video Stream Area */}
          <div className="relative aspect-video bg-black flex items-center justify-center">
            <img
              src={selectedCamera === 'cam_a' ? '/api/stream/cam_a' : '/api/stream/cam_b'}
              alt="Live Detection Stream"
              className="w-full h-full object-contain"
            />

            {/* In-Video HUD Badges */}
            <div className="absolute top-3 left-3 px-2 py-1 rounded bg-black/80 border border-emerald-500/80 font-mono text-[10px] text-emerald-300 pointer-events-none flex items-center gap-1.5 shadow">
              <span className="live-dot"></span>
              <span>LIVE AI DETECTOR ACTIVE</span>
            </div>

            <div className="absolute bottom-3 left-3 px-2 py-1 rounded bg-black/80 border border-slate-700/80 font-mono text-[10px] text-cyan-300 pointer-events-none shadow">
              {selectedCamera === 'cam_a' ? 'GATEWAY: CAM-01 (4th Ave North)' : 'GATEWAY: CAM-02 (5th Ave South - +850m)'}
            </div>

            <div className="absolute bottom-3 right-3 px-2 py-1 rounded bg-black/80 border border-blue-500/80 font-mono text-[10px] text-white pointer-events-none shadow">
              DETECTED IN FRAME: {vehicles.length} TARGETS
            </div>
          </div>
        </div>

        {/* Right: Detected Vehicle Gallery (Crops & Classified Tags) */}
        <div className="lg:col-span-5 bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-xl overflow-hidden shadow-lg flex flex-col">
          <div className="bg-[var(--bg-panel-header)] px-4 py-2.5 border-b border-[var(--border-color)] flex items-center justify-between">
            <div className="font-mono font-bold text-xs text-white flex items-center gap-2">
              <span>📋</span>
              <span>Detected Vehicles Catalog ({filteredVehicles.length})</span>
            </div>
            {filterClass !== 'all' && (
              <button
                onClick={() => setFilterClass('all')}
                className="text-[10px] text-cyan-300 font-mono underline hover:text-white"
              >
                Clear Filter
              </button>
            )}
          </div>

          <div className="p-3 flex-1 overflow-y-auto max-h-[460px] space-y-2">
            {filteredVehicles.length === 0 ? (
              <div className="text-center py-12 text-slate-500 text-xs font-mono">
                No vehicles detected matching category "{filterClass}".
              </div>
            ) : (
              filteredVehicles.map((v) => (
                <div
                  key={v.track_id}
                  className="p-2.5 rounded-lg bg-[var(--bg-main)] border border-[var(--border-color)] flex items-center gap-3 hover:border-blue-500 transition-all shadow-sm"
                >
                  {/* Vehicle Crop */}
                  {v.crop_b64 ? (
                    <img
                      src={v.crop_b64}
                      alt={v.track_id}
                      className="w-14 h-14 object-cover rounded-md border border-slate-700 bg-black flex-shrink-0"
                    />
                  ) : (
                    <div className="w-14 h-14 bg-slate-800 rounded-md flex-shrink-0"></div>
                  )}

                  <div className="min-w-0 flex-1">
                    <div className="flex items-center justify-between">
                      <span className="font-mono font-bold text-xs text-white">
                        {v.track_id}
                      </span>
                      <span className="text-[10px] font-mono text-cyan-400 bg-cyan-950/80 px-1.5 py-0.5 rounded border border-cyan-800">
                        {v.exit_time !== undefined ? `Exit: ${v.exit_time}s` : `Entry: ${v.entry_time}s`}
                      </span>
                    </div>

                    <div className="text-xs text-slate-200 font-semibold mt-0.5 truncate flex items-center gap-1.5">
                      <span>{v.vehicle_type}</span>
                    </div>

                    <div className="flex items-center gap-3 mt-1 text-[11px] text-slate-400">
                      <span className="flex items-center gap-1">
                        <span
                          className="w-2.5 h-2.5 rounded-full inline-block border border-black/40"
                          style={{ backgroundColor: v.dominant_hex }}
                        ></span>
                        <span>{v.dominant_color}</span>
                      </span>

                      {v.features?.aspect_ratio && (
                        <span className="font-mono text-[10px] text-slate-400">
                          AR: {v.features.aspect_ratio.toFixed(2)}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
