import React, { useState, useRef } from 'react';
import { Columns, SplitSquareVertical, Flame, Layers } from 'lucide-react';

export default function VisualDiffInspector({ runData, backendUrl = 'http://127.0.0.1:8000' }) {
  const [viewMode, setViewMode] = useState('slider'); // 'slider', 'side', 'heatmap'
  const [sliderPos, setSliderPos] = useState(50);
  const [showBoundingBoxes, setShowBoundingBoxes] = useState(true);
  const containerRef = useRef(null);

  if (!runData || !runData.before_screenshot) {
    return (
      <div className="dash-card">
        <div className="dash-card-header">
          <div className="card-title-group">
            <Layers size={18} color="#6366f1" />
            <h2>Visual Diff & Evidence Inspector</h2>
          </div>
        </div>
        <div className="empty-state">
          <Layers size={40} />
          <p>No active audit run loaded. Click "Run Autonomous Audit" above to begin.</p>
        </div>
      </div>
    );
  }

  const beforeUrl = `${backendUrl}/screenshots/${runData.before_screenshot}`;
  const afterUrl = runData.after_screenshot ? `${backendUrl}/screenshots/${runData.after_screenshot}` : null;
  const diffUrl = runData.diff_screenshot ? `${backendUrl}/screenshots/${runData.diff_screenshot}` : null;

  const handleMouseMove = (e) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const x = Math.max(0, Math.min(e.clientX - rect.left, rect.width));
    const percent = Math.round((x / rect.width) * 100);
    setSliderPos(percent);
  };

  const defectBbox = runData.defects?.[0]?.bounding_box;

  return (
    <div className="dash-card visual-inspector">
      <div className="dash-card-header">
        <div className="card-title-group">
          <Layers size={18} color="#6366f1" />
          <h2>Visual Diff & Evidence Inspector</h2>
          <span style={{ fontSize: '0.78rem', color: '#94a3b8' }}>
            ({runData.viewport.toUpperCase()} • {runData.defects_found === 0 ? 'PASSED (ZERO DEFECTS)' : (runData.verification_passed ? 'HEALED & VERIFIED' : 'UNVERIFIED')})
          </span>
        </div>

        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <div className="view-mode-selector">
            <button 
              className={`view-mode-btn ${viewMode === 'slider' ? 'active' : ''}`}
              onClick={() => setViewMode('slider')}
              disabled={!afterUrl}
              title="Split interactive slider"
            >
              <SplitSquareVertical size={14} style={{ marginRight: '4px' }} />
              Slider
            </button>
            <button 
              className={`view-mode-btn ${viewMode === 'side' ? 'active' : ''}`}
              onClick={() => setViewMode('side')}
              disabled={!afterUrl}
              title="Side by side comparison"
            >
              <Columns size={14} style={{ marginRight: '4px' }} />
              Side by Side
            </button>
            <button 
              className={`view-mode-btn ${viewMode === 'heatmap' ? 'active' : ''}`}
              onClick={() => setViewMode('heatmap')}
              disabled={!diffUrl}
              title="Pixel difference heatmap"
            >
              <Flame size={14} style={{ marginRight: '4px' }} />
              Heatmap
            </button>
          </div>

          <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.76rem', color: '#94a3b8', cursor: 'pointer' }}>
            <input 
              type="checkbox" 
              checked={showBoundingBoxes} 
              onChange={(e) => setShowBoundingBoxes(e.target.checked)} 
            />
            Show Bounding Boxes
          </label>
        </div>
      </div>

      <div className="diff-stage-container">
        {/* SLIDER MODE */}
        {viewMode === 'slider' && afterUrl && (
          <div 
            className="slider-container" 
            ref={containerRef}
            onMouseMove={handleMouseMove}
            onTouchMove={(e) => {
              if (!containerRef.current || !e.touches[0]) return;
              const rect = containerRef.current.getBoundingClientRect();
              const x = Math.max(0, Math.min(e.touches[0].clientX - rect.left, rect.width));
              setSliderPos(Math.round((x / rect.width) * 100));
            }}
          >
            {/* Before image (Background) */}
            <div style={{ position: 'relative' }}>
              <img src={beforeUrl} alt="Before Defect" />
              {showBoundingBoxes && defectBbox && (
                <div 
                  style={{
                    position: 'absolute',
                    left: `${Math.max(0, defectBbox.x)}px`,
                    top: `${Math.max(0, defectBbox.y)}px`,
                    width: `${defectBbox.width}px`,
                    height: `${defectBbox.height}px`,
                    border: '2px solid #ef4444',
                    background: 'rgba(239, 68, 68, 0.2)',
                    borderRadius: '4px',
                    pointerEvents: 'none',
                    boxShadow: '0 0 15px rgba(239, 68, 68, 0.6)'
                  }}
                >
                  <span style={{
                    position: 'absolute',
                    top: '-20px',
                    left: 0,
                    background: '#ef4444',
                    color: '#ffffff',
                    fontSize: '10px',
                    fontWeight: 700,
                    padding: '1px 6px',
                    borderRadius: '3px'
                  }}>
                    DEFECT: {runData.defects?.[0]?.element}
                  </span>
                </div>
              )}
            </div>

            {/* After image (Clipped foreground) */}
            <div 
              className="slider-after-overlay"
              style={{ clipPath: `inset(0 0 0 ${sliderPos}%)` }}
            >
              <img src={afterUrl} alt="After Self-Heal" />
            </div>

            {/* Draggable Divider */}
            <div 
              className="slider-divider-line"
              style={{ left: `${sliderPos}%` }}
            >
              <div className="slider-handle-bubble">
                <span style={{ fontSize: '11px', fontWeight: 800, color: '#090d16' }}>↔</span>
              </div>
            </div>
          </div>
        )}

        {/* SIDE BY SIDE MODE */}
        {viewMode === 'side' && afterUrl && (
          <div className="side-by-side-grid">
            <div className="side-frame">
              <span className="side-label label-before">BEFORE DEFECT</span>
              <img src={beforeUrl} alt="Before Defect" />
            </div>
            <div className="side-frame">
              <span className="side-label label-after">AFTER SELF-HEAL</span>
              <img src={afterUrl} alt="After Self-Heal" />
            </div>
          </div>
        )}

        {/* HEATMAP MODE */}
        {viewMode === 'heatmap' && diffUrl && (
          <div className="heatmap-frame">
            <span style={{ fontSize: '0.8rem', color: '#ec4899', fontWeight: 700 }}>
              PIXEL DISCREPANCY MASK (PIL ENHANCED)
            </span>
            <img src={diffUrl} alt="Discrepancy Heatmap" />
          </div>
        )}

        {!afterUrl && (
          <div className="side-frame" style={{ padding: '20px', width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <span className="side-label label-before">
              {runData.defects_found === 0 ? 'AUDITED VIEWPORT (COMPLIANT)' : 'STAGING VIEWPORT SCREENSHOT'}
            </span>
            <img 
              src={beforeUrl} 
              alt="Viewport Screenshot" 
              style={{ 
                maxWidth: runData.viewport === 'desktop' ? '92%' : (runData.viewport === 'tablet' ? '70%' : '380px'),
                borderRadius: '8px',
                border: '1px solid var(--border-color)',
                boxShadow: '0 8px 24px rgba(0,0,0,0.4)'
              }} 
            />
          </div>
        )}
      </div>
    </div>
  );
}
