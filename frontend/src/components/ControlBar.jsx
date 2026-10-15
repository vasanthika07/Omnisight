import React from 'react';
import { Smartphone, Tablet, Monitor, Globe, Cpu } from 'lucide-react';

export default function ControlBar({ viewport, setViewport, targetUrl, setTargetUrl, isRunning }) {
  return (
    <section className="audit-control-bar">
      <div className="viewport-tabs">
        <button 
          className={`tab-btn ${viewport === 'mobile' ? 'active' : ''}`}
          onClick={() => setViewport('mobile')}
          disabled={isRunning}
        >
          <Smartphone size={16} />
          <span>Mobile (375x812)</span>
        </button>

        <button 
          className={`tab-btn ${viewport === 'tablet' ? 'active' : ''}`}
          onClick={() => setViewport('tablet')}
          disabled={isRunning}
        >
          <Tablet size={16} />
          <span>Tablet (768x1024)</span>
        </button>

        <button 
          className={`tab-btn ${viewport === 'desktop' ? 'active' : ''}`}
          onClick={() => setViewport('desktop')}
          disabled={isRunning}
        >
          <Monitor size={16} />
          <span>Desktop (1440x900)</span>
        </button>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flex: 1, maxWidth: '480px' }}>
        <Globe size={18} color="#94a3b8" />
        <input 
          type="text" 
          value={targetUrl}
          onChange={(e) => setTargetUrl(e.target.value)}
          placeholder="Target Staging URL (defaults to Infotact Demo Checkout)"
          disabled={isRunning}
          style={{
            flex: 1,
            background: 'rgba(0,0,0,0.3)',
            border: '1px solid rgba(255,255,255,0.1)',
            borderRadius: '8px',
            padding: '8px 12px',
            color: '#f8fafc',
            fontSize: '0.82rem',
            fontFamily: 'inherit'
          }}
        />
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.8rem', color: '#94a3b8' }}>
        <Cpu size={16} color="#818cf8" />
        <span>Mode: <strong style={{ color: '#ffffff' }}>Plan → Execute → Evaluate</strong></span>
      </div>
    </section>
  );
}
