import React, { useState, useRef, useEffect } from 'react';
import { 
  Smartphone, 
  Tablet, 
  Monitor, 
  Layers, 
  Globe, 
  Cpu, 
  Play, 
  RefreshCw, 
  X, 
  CornerDownLeft, 
  FlaskConical, 
  ChevronDown, 
  Sparkles,
  ShieldCheck,
  Check
} from 'lucide-react';

export default function ControlBar({ 
  viewport, 
  setViewport, 
  targetUrl, 
  setTargetUrl, 
  isRunning, 
  onTriggerAudit, 
  onResetBug,
  onInjectChaosBug,
  onResetClean,
  selectedEngine,
  setSelectedEngine
}) {
  const [isChaosOpen, setIsChaosOpen] = useState(false);
  const chaosDropdownRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (chaosDropdownRef.current && !chaosDropdownRef.current.contains(event.target)) {
        setIsChaosOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !isRunning && onTriggerAudit) {
      e.preventDefault();
      onTriggerAudit();
    }
  };

  const handleClearUrl = () => {
    setTargetUrl('');
  };

  const handleSelectScenario = (scenarioId) => {
    setIsChaosOpen(false);
    if (scenarioId === 'clean') {
      if (onResetClean) onResetClean();
    } else {
      if (onInjectChaosBug) onInjectChaosBug(scenarioId);
    }
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
          <Smartphone size={15} />
          <span>Mobile (375px)</span>
        </button>

        <button 
          type="button"
          className={`tab-btn ${viewport === 'tablet' ? 'active' : ''}`}
          onClick={() => setViewport('tablet')}
          disabled={isRunning}
          title="Audit on Tablet Viewport (768x1024)"
        >
          <Tablet size={15} />
          <span>Tablet (768px)</span>
        </button>

        <button 
          type="button"
          className={`tab-btn ${viewport === 'desktop' ? 'active' : ''}`}
          onClick={() => setViewport('desktop')}
          disabled={isRunning}
          title="Audit on Desktop Viewport (1440x900)"
        >
          <Monitor size={15} />
          <span>Desktop (1440px)</span>
        </button>

        <button 
          type="button"
          className={`tab-btn matrix-tab ${viewport === 'matrix' ? 'active' : ''}`}
          onClick={() => setViewport('matrix')}
          disabled={isRunning}
          title="Cross-Device Matrix Audit (Mobile + Tablet + Desktop)"
        >
          <Layers size={15} />
          <span>Matrix (All 3)</span>
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
          placeholder="Target Staging URL (defaults to Infotact Demo Checkout Store)"
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

      {/* Engine Selector */}
      <div className="engine-select-group">
        <Cpu size={14} color="#818cf8" />
        <select 
          value={selectedEngine || 'builtin'} 
          onChange={(e) => setSelectedEngine(e.target.value)}
          disabled={isRunning}
          className="engine-select"
          title="Select VLM Inference Engine"
        >
          <option value="builtin">Autonomous Spatial (Built-in)</option>
          <option value="gemini">Google Gemini 1.5 Flash</option>
          <option value="openai">OpenAI GPT-4o-mini</option>
        </select>
      </div>

      {/* Chaos Testing Studio Dropdown */}
      <div className="chaos-dropdown-container" ref={chaosDropdownRef}>
        <button 
          type="button"
          className="btn btn-secondary chaos-trigger-btn"
          onClick={() => setIsChaosOpen(!isChaosOpen)}
          disabled={isRunning}
          title="Inject realistic visual QA anomalies to test self-healing resilience"
        >
          <FlaskConical size={14} color="#ec4899" />
          <span>Chaos Studio</span>
          <ChevronDown size={13} style={{ transform: isChaosOpen ? 'rotate(180deg)' : 'none', transition: '0.2s' }} />
        </button>

        {isChaosOpen && (
          <div className="chaos-menu">
            <div className="chaos-menu-header">
              <Sparkles size={13} color="#ec4899" />
              <span>QA Anomaly Simulator</span>
            </div>

            <button 
              type="button" 
              className="chaos-item" 
              onClick={() => handleSelectScenario('overflow')}
            >
              <div className="chaos-item-info">
                <strong>⚡ Mobile Viewport Overflow</strong>
                <span>520px fixed button clipping mobile screen</span>
              </div>
            </button>

            <button 
              type="button" 
              className="chaos-item" 
              onClick={() => handleSelectScenario('contrast')}
            >
              <div className="chaos-item-info">
                <strong>👁️ WCAG Low Contrast Violation</strong>
                <span>Dark gray text on dark card (ratio 2.1:1 &lt; 4.5:1)</span>
              </div>
            </button>

            <button 
              type="button" 
              className="chaos-item" 
              onClick={() => handleSelectScenario('touch_target')}
            >
              <div className="chaos-item-info">
                <strong>👆 Sub-Standard Touch Target</strong>
                <span>Checkout CTA reduced to tiny 20px height</span>
              </div>
            </button>

            <button 
              type="button" 
              className="chaos-item" 
              onClick={() => handleSelectScenario('zindex_overlap')}
            >
              <div className="chaos-item-info">
                <strong>🚫 Floating CTA Collision</strong>
                <span>Promotional banner blocking checkout click</span>
              </div>
            </button>

            <div className="chaos-divider"></div>

            <button 
              type="button" 
              className="chaos-item clean-item" 
              onClick={() => handleSelectScenario('clean')}
            >
              <div className="chaos-item-info">
                <strong style={{ color: '#10b981' }}>🛡️ Reset 100% Compliant (Zero Bugs)</strong>
                <span>Audit passes cleanly across all viewports</span>
              </div>
            </button>
          </div>
        )}
      </div>

      {/* Action Buttons: Run Audit & Reset Bug */}
      <div className="control-bar-actions">
        <button 
          type="button"
          className="btn btn-primary control-bar-btn-primary"
          onClick={onTriggerAudit}
          disabled={isRunning}
          id="run-audit-btn"
          title={`Dispatch OmniSight Autonomous QA Agent for ${viewport === 'matrix' ? 'all 3 devices' : viewport}`}
        >
          {isRunning ? (
            <>
              <div className="spinner" style={{ width: '14px', height: '14px', borderWidth: '2px' }}></div>
              <span>Auditing...</span>
            </>
          ) : (
            <>
              <Play size={14} fill="currentColor" />
              <span>{viewport === 'matrix' ? 'Run Matrix Audit' : 'Run Audit'}</span>
            </>
          )}
        </button>
      </div>
    </section>
  );
}
