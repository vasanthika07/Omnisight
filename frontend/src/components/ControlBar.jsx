import React from 'react';
import { Smartphone, Tablet, Monitor, Globe, Cpu, Play, RefreshCw, X, CornerDownLeft } from 'lucide-react';

export default function ControlBar({ 
  viewport, 
  setViewport, 
  targetUrl, 
  setTargetUrl, 
  isRunning, 
  onTriggerAudit, 
  onResetBug 
}) {
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !isRunning && onTriggerAudit) {
      e.preventDefault();
      onTriggerAudit();
    }
  };

  const handleClearUrl = () => {
    setTargetUrl('');
  };

  return (
    <section className="audit-control-bar">
      {/* Viewport selection tabs */}
      <div className="viewport-tabs">
        <button 
          type="button"
          className={`tab-btn ${viewport === 'mobile' ? 'active' : ''}`}
          onClick={() => setViewport('mobile')}
          disabled={isRunning}
          title="Audit on Mobile Viewport (375x812)"
        >
          <Smartphone size={16} />
          <span>Mobile (375x812)</span>
        </button>

        <button 
          type="button"
          className={`tab-btn ${viewport === 'tablet' ? 'active' : ''}`}
          onClick={() => setViewport('tablet')}
          disabled={isRunning}
          title="Audit on Tablet Viewport (768x1024)"
        >
          <Tablet size={16} />
          <span>Tablet (768x1024)</span>
        </button>

        <button 
          type="button"
          className={`tab-btn ${viewport === 'desktop' ? 'active' : ''}`}
          onClick={() => setViewport('desktop')}
          disabled={isRunning}
          title="Audit on Desktop Viewport (1440x900)"
        >
          <Monitor size={16} />
          <span>Desktop (1440x900)</span>
        </button>
      </div>

      {/* Target URL Input with Clear & Enter trigger */}
      <div className="control-bar-input-group">
        <Globe size={18} color="#94a3b8" className="input-prefix-icon" />
        <input 
          type="text" 
          value={targetUrl}
          onChange={(e) => setTargetUrl(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Target Staging URL (defaults to Infotact Demo Checkout)"
          disabled={isRunning}
          className="control-bar-input"
          id="staging-url-input"
        />
        {targetUrl && (
          <button 
            type="button"
            onClick={handleClearUrl}
            disabled={isRunning}
            className="control-bar-clear-btn"
            title="Clear target URL (reverts to demo checkout store)"
          >
            <X size={14} />
          </button>
        )}
        <div className="kbd-shortcut-hint" title="Press Enter to launch audit">
          <CornerDownLeft size={11} />
          <span>Enter</span>
        </div>
      </div>

      {/* Action Buttons: Run Audit & Reset Bug */}
      <div className="control-bar-actions">
        {onResetBug && (
          <button 
            type="button"
            className="btn btn-secondary control-bar-btn"
            onClick={onResetBug}
            disabled={isRunning}
            title="Reset checkout stylesheet to deliberate 520px buggy state"
          >
            <RefreshCw size={14} className={isRunning ? 'spin' : ''} />
            <span>Reset Bug</span>
          </button>
        )}

        <button 
          type="button"
          className="btn btn-primary control-bar-btn-primary"
          onClick={onTriggerAudit}
          disabled={isRunning}
          id="run-audit-btn"
          title="Dispatch OmniSight Autonomous QA Agent for this viewport (or press Enter)"
        >
          {isRunning ? (
            <>
              <div className="spinner" style={{ width: '14px', height: '14px', borderWidth: '2px' }}></div>
              <span>Auditing...</span>
            </>
          ) : (
            <>
              <Play size={14} fill="currentColor" />
              <span>Run Audit</span>
            </>
          )}
        </button>
      </div>

      {/* Mode Tag */}
      <div className="control-bar-mode">
        <Cpu size={16} color="#818cf8" />
        <span>Mode: <strong style={{ color: '#ffffff' }}>Plan → Execute → Evaluate</strong></span>
      </div>
    </section>
  );
}
