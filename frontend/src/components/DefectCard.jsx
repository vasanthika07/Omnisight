import React from 'react';
import { ShieldAlert, CheckCircle, Sparkles } from 'lucide-react';

export default function DefectCard({ 
  defects = [], 
  confidenceScore, 
  croppedArtifact, 
  backendUrl = 'http://127.0.0.1:8000',
  engineUsed 
}) {
  if (!defects || defects.length === 0) {
    return (
      <div className="dash-card">
        <div className="dash-card-header">
          <div className="card-title-group">
            <CheckCircle size={18} color="#10b981" />
            <h2>Visual Defect Diagnostics</h2>
          </div>
          {engineUsed && (
            <span style={{ fontSize: '0.74rem', color: '#94a3b8' }}>
              Engine: {engineUsed.replace(/_/g, ' ')}
            </span>
          )}
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
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {engineUsed && (
            <span style={{ 
              fontSize: '0.72rem', 
              color: '#818cf8', 
              background: 'rgba(99, 102, 241, 0.12)', 
              padding: '2px 8px', 
              borderRadius: '9999px',
              border: '1px solid rgba(99, 102, 241, 0.25)' 
            }}>
              {engineUsed.includes('gemini') ? 'Gemini 1.5' : (engineUsed.includes('openai') ? 'GPT-4o' : 'Autonomous Spatial')}
            </span>
          )}
          <span style={{ fontSize: '0.78rem', color: '#f87171', fontWeight: 700 }}>
            {defects.length} Anomaly Detected
          </span>
        </div>
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

            {/* Token-Optimized Cropped Component Artifact */}
            {croppedArtifact && (
              <div style={{
                marginTop: '10px',
                background: 'rgba(168, 85, 247, 0.08)',
                border: '1px solid rgba(168, 85, 247, 0.25)',
                borderRadius: '8px',
                padding: '10px',
                display: 'flex',
                flexDirection: 'column',
                gap: '8px'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <Sparkles size={14} color="#a855f7" />
                    <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#c084fc' }}>
                      Token-Optimized ROI Crop
                    </span>
                  </div>
                  <span style={{ 
                    fontSize: '0.68rem', 
                    color: '#34d399', 
                    background: 'rgba(16, 185, 129, 0.15)', 
                    padding: '1px 6px', 
                    borderRadius: '4px',
                    fontWeight: 700
                  }}>
                    -80% VLM Tokens
                  </span>
                </div>
                <div style={{ 
                  borderRadius: '6px', 
                  overflow: 'hidden', 
                  border: '1px solid rgba(255,255,255,0.08)',
                  background: '#090d16',
                  display: 'flex',
                  justifyContent: 'center',
                  padding: '4px'
                }}>
                  <img 
                    src={`${backendUrl}/screenshots/${croppedArtifact}`} 
                    alt="Cropped Anomaly ROI" 
                    style={{ maxHeight: '110px', width: 'auto', objectFit: 'contain' }}
                  />
                </div>
              </div>
            )}

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
