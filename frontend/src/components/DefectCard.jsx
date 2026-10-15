import React from 'react';
import { AlertTriangle, ShieldAlert, CheckCircle, Crosshair } from 'lucide-react';

export default function DefectCard({ defects = [], confidenceScore }) {
  if (!defects || defects.length === 0) {
    return (
      <div className="dash-card">
        <div className="dash-card-header">
          <div className="card-title-group">
            <CheckCircle size={18} color="#10b981" />
            <h2>Visual Defect Diagnostics</h2>
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', color: '#10b981', padding: '14px 0' }}>
          <CheckCircle size={20} />
          <span style={{ fontSize: '0.88rem', fontWeight: 600 }}>
            Zero layout anomalies detected. Viewport complies with responsive standards.
          </span>
        </div>
      </div>
    );
  }

  return (
    <div className="dash-card">
      <div className="dash-card-header">
        <div className="card-title-group">
          <ShieldAlert size={18} color="#ef4444" />
          <h2>Visual Defect Diagnostics</h2>
        </div>
        <span style={{ fontSize: '0.78rem', color: '#f87171', fontWeight: 700 }}>
          {defects.length} Anomaly Detected
        </span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
        {defects.map((d, i) => (
          <div key={i} className="defect-pill">
            <div className="defect-header-row">
              <span className="severity-tag">{d.severity || 'HIGH'}</span>
              <span style={{ fontSize: '0.76rem', color: '#94a3b8', fontFamily: 'monospace' }}>
                {d.element || '.checkout-action-btn'}
              </span>
            </div>

            <p className="defect-desc">{d.description}</p>

            <div className="defect-metrics">
              <span><strong>Type:</strong> {d.type}</span>
              {d.overflow_pixels && (
                <span><strong>Overflow:</strong> +{d.overflow_pixels}px</span>
              )}
              {confidenceScore && (
                <span><strong>Confidence:</strong> {(confidenceScore * 100).toFixed(0)}%</span>
              )}
            </div>

            {d.proposed_fix && (
              <div style={{ marginTop: '8px', background: 'rgba(0,0,0,0.3)', padding: '8px 12px', borderRadius: '6px' }}>
                <span style={{ fontSize: '0.72rem', color: '#818cf8', fontWeight: 700 }}>PROPOSED CSS RULES:</span>
                <pre style={{ fontSize: '0.75rem', color: '#cbd5e1', marginTop: '4px' }}>{d.proposed_fix}</pre>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
