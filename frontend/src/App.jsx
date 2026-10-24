import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import FeatureVehicleDetection from './components/FeatureVehicleDetection';
import FeatureMultiCameraMatching from './components/FeatureMultiCameraMatching';
import FeatureTrafficFlow from './components/FeatureTrafficFlow';
import MethodologyModal from './components/MethodologyModal';
import UploadModal from './components/UploadModal';
import {
  fetchStatus,
  fetchDemoCorridor,
  reviewMatch,
  updateCorridorConfig,
  uploadSurveillancePair,
  randomizeCorridorDataset
} from './services/api';

export default function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [serverOnline, setServerOnline] = useState(false);

  // 3 Core Features: 'detection' | 'matching' | 'traffic_flow'
  const [mainView, setMainView] = useState('detection');

  // Theme state: 'tactical' (default), 'terminal', 'slate'
  const [currentTheme, setCurrentTheme] = useState(() => {
    return localStorage.getItem('citytrack_theme') || 'tactical';
  });

  const handleSelectTheme = (newTheme) => {
    setCurrentTheme(newTheme);
    try {
      localStorage.setItem('citytrack_theme', newTheme);
    } catch (e) {}
  };

  // Modals
  const [showMethodology, setShowMethodology] = useState(false);
  const [showUpload, setShowUpload] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [updatingMatchId, setUpdatingMatchId] = useState(null);

  // Initial load
  useEffect(() => {
    loadCorridorData();
  }, []);

  const loadCorridorData = async () => {
    setLoading(true);
    setError(null);
    try {
      // Check status
      await fetchStatus()
        .then(() => setServerOnline(true))
        .catch(() => setServerOnline(false));

      const res = await fetchDemoCorridor();
      setData(res);
      setServerOnline(true);
    } catch (err) {
      console.error('Error fetching corridor data:', err);
      setError(err.message || 'Failed to connect to CityTrack AI backend API.');
      setServerOnline(false);
    } finally {
      setLoading(false);
    }
  };

  const handleReviewMatch = async (matchId, action) => {
    setUpdatingMatchId(matchId);
    try {
      const res = await reviewMatch(matchId, action);
      if (res.success && data) {
        const updatedMatches = data.matches.map((m) =>
          m.match_id === matchId ? { ...m, status: action } : m
        );
        setData({
          ...data,
          matches: updatedMatches,
          analytics: res.analytics || data.analytics
        });
      }
    } catch (err) {
      alert(`Review action failed: ${err.message}`);
    } finally {
      setUpdatingMatchId(null);
    }
  };

  const handleUploadSubmit = async (fileA, fileB) => {
    setIsUploading(true);
    try {
      const res = await uploadSurveillancePair(fileA, fileB);
      if (res.success) {
        const updated = await fetchDemoCorridor();
        setData(updated);
        setShowUpload(false);
      }
    } catch (err) {
      alert(`Upload analysis error: ${err.message}`);
    } finally {
      setIsUploading(false);
    }
  };

  const handleRandomizeTraffic = async () => {
    setLoading(true);
    try {
      const res = await randomizeCorridorDataset();
      setData(res);
    } catch (err) {
      alert(`Random test failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container" data-theme={currentTheme}>
      {/* Top Header */}
      <Header
        isDemo={data?.is_demo ?? true}
        datasetLabel={data?.dataset_label || ''}
        serverOnline={serverOnline}
        currentTheme={currentTheme}
        onSelectTheme={handleSelectTheme}
        onOpenMethodology={() => setShowMethodology(true)}
        onOpenUpload={() => setShowUpload(true)}
        onResetDemo={loadCorridorData}
        onRandomizeTraffic={handleRandomizeTraffic}
        loading={loading}
      />

      <main className="main-content">
        {/* Error State */}
        {error && (
          <div className="p-3 mb-4 rounded bg-red-950/80 border border-red-800 text-red-200 text-xs flex items-center justify-between">
            <div>
              <strong>Connection Error:</strong> {error}
              <div className="text-[11px] text-red-300 mt-0.5">
                Ensure backend Flask service is running on <code>http://127.0.0.1:5000</code>.
              </div>
            </div>
            <button onClick={loadCorridorData} className="btn btn-sm btn-danger">
              Retry Connection
            </button>
          </div>
        )}

        {/* Loading Indicator */}
        {loading && !data && (
          <div className="border border-[#23334d] rounded-xl p-12 text-center text-slate-400 bg-[#131d31] my-8 shadow-xl">
            <div className="w-9 h-9 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
            <div className="text-sm font-semibold text-slate-200">
              Loading Surveillance Streams &amp; AI Re-ID Pipeline...
            </div>
          </div>
        )}

        {/* Main Content with 3 Core Features */}
        {data && (
          <>
            {/* The 3 Core Feature Switcher Navigation */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-2.5 mb-5 bg-[var(--bg-panel-header)] p-2 rounded-xl border border-[var(--border-color)] shadow-md">
              {/* Feature 1 */}
              <button
                onClick={() => setMainView('detection')}
                className={`flex items-center gap-3 p-3 rounded-lg text-left transition-all ${
                  mainView === 'detection'
                    ? 'bg-blue-600 text-white shadow-lg ring-1 ring-blue-400 font-bold'
                    : 'bg-[var(--bg-main)] text-slate-300 hover:text-white hover:bg-[var(--bg-surface)] border border-[var(--border-color)]'
                }`}
              >
                <span className="text-2xl flex-shrink-0">🚗</span>
                <div>
                  <div className="text-xs font-bold uppercase tracking-wider">1. Vehicle Detection</div>
                  <div className={`text-[11px] leading-tight mt-0.5 ${mainView === 'detection' ? 'text-blue-100' : 'text-slate-400'}`}>
                    Car, bike, bus, truck &amp; auto detection
                  </div>
                </div>
              </button>

              {/* Feature 2 */}
              <button
                onClick={() => setMainView('matching')}
                className={`flex items-center gap-3 p-3 rounded-lg text-left transition-all ${
                  mainView === 'matching'
                    ? 'bg-indigo-600 text-white shadow-lg ring-1 ring-indigo-400 font-bold'
                    : 'bg-[var(--bg-main)] text-slate-300 hover:text-white hover:bg-[var(--bg-surface)] border border-[var(--border-color)]'
                }`}
              >
                <span className="text-2xl flex-shrink-0">🔍</span>
                <div>
                  <div className="text-xs font-bold uppercase tracking-wider">2. Multi-Camera Matching</div>
                  <div className={`text-[11px] leading-tight mt-0.5 ${mainView === 'matching' ? 'text-indigo-100' : 'text-slate-400'}`}>
                    Visual appearance &amp; features comparison
                  </div>
                </div>
              </button>

              {/* Feature 3 */}
              <button
                onClick={() => setMainView('traffic_flow')}
                className={`flex items-center gap-3 p-3 rounded-lg text-left transition-all ${
                  mainView === 'traffic_flow'
                    ? 'bg-emerald-600 text-white shadow-lg ring-1 ring-emerald-400 font-bold'
                    : 'bg-[var(--bg-main)] text-slate-300 hover:text-white hover:bg-[var(--bg-surface)] border border-[var(--border-color)]'
                }`}
              >
                <span className="text-2xl flex-shrink-0">📊</span>
                <div>
                  <div className="text-xs font-bold uppercase tracking-wider">3. Traffic Flow Dashboard</div>
                  <div className={`text-[11px] leading-tight mt-0.5 ${mainView === 'traffic_flow' ? 'text-emerald-100' : 'text-slate-400'}`}>
                    Vehicle volume, camera matches &amp; travel times
                  </div>
                </div>
              </button>
            </div>

            {/* Feature 1 View: Video Detection of car, bike, bus, truck, auto */}
            {mainView === 'detection' && (
              <FeatureVehicleDetection
                cameraA={data.camera_a}
                cameraB={data.camera_b}
                onOpenUpload={() => setShowUpload(true)}
              />
            )}

            {/* Feature 2 View: Multi-Camera Visual Feature Matching */}
            {mainView === 'matching' && (
              <FeatureMultiCameraMatching
                cameraA={data.camera_a}
                cameraB={data.camera_b}
                matches={data.matches}
                onReviewMatch={handleReviewMatch}
                updatingMatchId={updatingMatchId}
              />
            )}

            {/* Feature 3 View: Traffic Flow Dashboard (Volume, Camera Matches, Travel Time) */}
            {mainView === 'traffic_flow' && (
              <FeatureTrafficFlow
                analytics={data.analytics}
                parameters={data.parameters}
                matches={data.matches}
                cameraA={data.camera_a}
                cameraB={data.camera_b}
              />
            )}
          </>
        )}
      </main>

      {/* Clean Modern Footer */}
      <footer className="bg-[var(--bg-panel-header)] border-t border-[var(--border-color)] px-5 py-3 text-[11px] text-[var(--text-dim)] mt-6">
        <div className="max-w-[1680px] mx-auto flex flex-wrap items-center justify-between gap-2">
          <div>
            <strong>CityTrack AI</strong> &mdash; 1. Vehicle Detection &bull; 2. Multi-Camera Matching &bull; 3. Traffic Flow Dashboard
          </div>
          <div className="flex items-center gap-3 text-[var(--text-muted)] font-mono text-[10px]">
            <span>Corridor Baseline: 850m</span>
            <span>&bull;</span>
            <span className="text-emerald-400 font-bold">Zero OCR / No License Plates</span>
          </div>
        </div>
      </footer>

      {/* Modals */}
      {showMethodology && (
        <MethodologyModal onClose={() => setShowMethodology(false)} />
      )}

      {showUpload && (
        <UploadModal
          onUpload={handleUploadSubmit}
          onClose={() => setShowUpload(false)}
          isUploading={isUploading}
        />
      )}
    </div>
  );
}
