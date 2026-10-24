import React, { useState } from 'react';

export default function UploadModal({ onUpload, onClose, isUploading }) {
  const [fileA, setFileA] = useState(null);
  const [fileB, setFileB] = useState(null);
  const [previewA, setPreviewA] = useState('');
  const [previewB, setPreviewB] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  const isVideo = (file) => file && (file.type?.startsWith('video') || /\.(mp4|avi|mov|mkv|webm)$/i.test(file.name));

  const handleSelectA = (e) => {
    const file = e.target.files[0];
    if (file) {
      setFileA(file);
      setPreviewA(URL.createObjectURL(file));
      setErrorMsg('');
    }
  };

  const handleSelectB = (e) => {
    const file = e.target.files[0];
    if (file) {
      setFileB(file);
      setPreviewB(URL.createObjectURL(file));
      setErrorMsg('');
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!fileA || !fileB) {
      setErrorMsg('Please select both Camera A and Camera B media files (Photos or MP4 Videos).');
      return;
    }
    onUpload(fileA, fileB);
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content max-w-xl" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="flex items-center gap-2">
            <span className="text-base">📸 🎥</span>
            <h3 className="text-sm font-bold uppercase tracking-wider text-white">
              Upload Surveillance Feeds (Photo & Video Supported)
            </h3>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white font-mono text-sm">
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="modal-body space-y-4 text-xs">
            <p className="text-slate-300">
              Provide two media captures from non-overlapping surveillance locations. You can upload <strong>Photos (JPG/PNG)</strong> or <strong>Videos (MP4/AVI)</strong>. The pipeline extracts frames, runs MOG2 background detection, computes 64-dim part-based appearance embeddings, and solves cross-camera re-identification.
            </p>

            {errorMsg && (
              <div className="p-2.5 rounded bg-red-950/80 border border-red-800 text-red-200 text-xs font-mono">
                {errorMsg}
              </div>
            )}

            <div className="grid grid-cols-2 gap-3">
              {/* Camera A Upload */}
              <div className="border border-[var(--border-color)] p-3 rounded bg-[var(--bg-surface)]">
                <div className="flex items-center justify-between mb-1.5">
                  <label className="text-[var(--text-main)] font-bold font-mono">
                    Camera A (Upstream)
                  </label>
                  {fileA && (
                    <span className={`text-[9px] font-mono font-bold px-1.5 py-0.5 rounded ${
                      isVideo(fileA) ? 'bg-purple-900/60 text-purple-300 border border-purple-700' : 'bg-blue-900/60 text-blue-300 border border-blue-700'
                    }`}>
                      {isVideo(fileA) ? '🎥 VIDEO' : '📷 PHOTO'}
                    </span>
                  )}
                </div>
                <input
                  type="file"
                  accept="image/*,video/*,.mp4,.avi,.mov,.mkv,.jpg,.jpeg,.png,.webp"
                  onChange={handleSelectA}
                  className="text-[11px] text-[var(--text-muted)] file:mr-2 file:py-1 file:px-2.5 file:rounded file:border file:border-[var(--border-color)] file:text-[11px] file:bg-[var(--bg-surface-hover)] file:text-[var(--text-main)] hover:file:bg-[var(--accent-primary)] hover:file:text-white cursor-pointer w-full"
                />
                {previewA && (
                  <div className="mt-2 aspect-video bg-black rounded overflow-hidden border border-[var(--border-color)] flex items-center justify-center">
                    {isVideo(fileA) ? (
                      <video src={previewA} controls className="w-full h-full object-contain" />
                    ) : (
                      <img src={previewA} alt="Cam A Preview" className="w-full h-full object-cover" />
                    )}
                  </div>
                )}
              </div>

              {/* Camera B Upload */}
              <div className="border border-[var(--border-color)] p-3 rounded bg-[var(--bg-surface)]">
                <div className="flex items-center justify-between mb-1.5">
                  <label className="text-[var(--text-main)] font-bold font-mono">
                    Camera B (Downstream)
                  </label>
                  {fileB && (
                    <span className={`text-[9px] font-mono font-bold px-1.5 py-0.5 rounded ${
                      isVideo(fileB) ? 'bg-purple-900/60 text-purple-300 border border-purple-700' : 'bg-cyan-900/60 text-cyan-300 border border-cyan-700'
                    }`}>
                      {isVideo(fileB) ? '🎥 VIDEO' : '📷 PHOTO'}
                    </span>
                  )}
                </div>
                <input
                  type="file"
                  accept="image/*,video/*,.mp4,.avi,.mov,.mkv,.jpg,.jpeg,.png,.webp"
                  onChange={handleSelectB}
                  className="text-[11px] text-[var(--text-muted)] file:mr-2 file:py-1 file:px-2.5 file:rounded file:border file:border-[var(--border-color)] file:text-[11px] file:bg-[var(--bg-surface-hover)] file:text-[var(--text-main)] hover:file:bg-[var(--accent-primary)] hover:file:text-white cursor-pointer w-full"
                />
                {previewB && (
                  <div className="mt-2 aspect-video bg-black rounded overflow-hidden border border-[var(--border-color)] flex items-center justify-center">
                    {isVideo(fileB) ? (
                      <video src={previewB} controls className="w-full h-full object-contain" />
                    ) : (
                      <img src={previewB} alt="Cam B Preview" className="w-full h-full object-cover" />
                    )}
                  </div>
                )}
              </div>
            </div>

            <div className="p-2.5 rounded bg-[var(--bg-main)] border border-[var(--border-color)] text-[var(--text-muted)] text-[11px] flex items-center justify-between">
              <div>
                <strong>Supported Media:</strong> Photos (<code className="text-cyan-300">.jpg, .png, .webp</code>) & Videos (<code className="text-purple-300">.mp4, .avi, .mov</code>).
              </div>
              <span className="font-mono text-[10px] text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-800">
                Auto-Frame Extraction
              </span>
            </div>
          </div>

          <div className="modal-footer">
            <button
              type="button"
              onClick={onClose}
              disabled={isUploading}
              className="btn btn-sm"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isUploading}
              className="btn btn-sm btn-primary flex items-center gap-1.5"
            >
              {isUploading ? (
                <>
                  <span className="live-dot"></span>
                  <span>Executing Computer Vision Pipeline...</span>
                </>
              ) : (
                <>
                  <span>⚡</span>
                  <span>Run Photo / Video Re-ID Analysis</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
