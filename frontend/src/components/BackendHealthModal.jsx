import React, { useState } from 'react';
import { 
  Activity, 
  CheckCircle2, 
  AlertTriangle, 
  XCircle, 
  RefreshCw, 
  Server, 
  Database, 
  Eye, 
  Cpu, 
  ExternalLink, 
  X,
  Zap,
  Clock
} from 'lucide-react';

export default function BackendHealthModal({
  isOpen,
  onClose,
  backendUrl,
  healthData,
  latency,
  isChecking,
  onRefreshHealth
}) {
  if (!isOpen) return null;

  const isHealthy = healthData?.status === 'healthy';
  const isDegraded = healthData?.status === 'degraded';
  const isOffline = !healthData;

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div 
        className="modal-container"
        style={{ maxWidth: '640px' }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div 
              style={{
                width: '36px',
                height: '36px',
                borderRadius: '10px',
                background: isHealthy ? 'rgba(16, 185, 129, 0.2)' : (isDegraded ? 'rgba(245, 158, 11, 0.2)' : 'rgba(239, 68, 68, 0.2)'),
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                border: `1px solid ${isHealthy ? 'rgba(16, 185, 129, 0.4)' : (isDegraded ? 'rgba(245, 158, 11, 0.4)' : 'rgba(239, 68, 68, 0.4)')}`
              }}
            >
              <Server size={20} color={isHealthy ? '#10b981' : (isDegraded ? '#f59e0b' : '#ef4444')} />
            </div>
            <div>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#f8fafc' }}>
                Backend System Health & Diagnostics
              </h3>
              <p style={{ fontSize: '0.78rem', color: '#94a3b8' }}>
                Real-time API responsiveness, Playwright browser engine, and SQLite telemetry.
              </p>
            </div>
          </div>
          <button className="modal-close-btn" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        {/* Content Body */}
        <div className="modal-body" style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
          
          {/* Status Hero Card */}
          <div style={{
            background: isHealthy 
              ? 'linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(6, 182, 212, 0.08) 100%)'
              : 'linear-gradient(135deg, rgba(239, 68, 68, 0.12) 0%, rgba(245, 158, 11, 0.08) 100%)',
            border: `1px solid ${isHealthy ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
            borderRadius: '14px',
            padding: '16px 20px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
              {isHealthy ? (
                <CheckCircle2 size={32} color="#10b981" />
              ) : isDegraded ? (
                <AlertTriangle size={32} color="#f59e0b" />
              ) : (
                <XCircle size={32} color="#ef4444" />
              )}
              <div>
                <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#ffffff' }}>
                  {isHealthy ? 'FastAPI Backend Operational' : (isDegraded ? 'Service Degraded' : 'Backend Unreachable')}
                </h4>
                <p style={{ fontSize: '0.8rem', color: '#cbd5e1', marginTop: '2px' }}>
                  {backendUrl} {latency !== null && `• Roundtrip Ping: ${latency}ms`}
                </p>
              </div>
            </div>

            <button 
              className="btn btn-secondary" 
              onClick={onRefreshHealth}
              disabled={isChecking}
              style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem', padding: '6px 12px' }}
            >
              <RefreshCw size={13} className={isChecking ? 'spin' : ''} />
              <span>{isChecking ? 'Pinging...' : 'Ping Now'}</span>
            </button>
          </div>

          {/* Subsystem Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            
            {/* Playwright Navigator */}
            <div style={{
              background: 'rgba(255, 255, 255, 0.03)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              borderRadius: '12px',
              padding: '14px'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span style={{ fontSize: '0.76rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>
                  Browser Engine
                </span>
                <span style={{ 
                  fontSize: '0.72rem', 
                  padding: '2px 8px', 
                  borderRadius: '9999px',
                  background: 'rgba(16, 185, 129, 0.15)',
                  color: '#34d399',
                  fontWeight: 600
                }}>
                  {healthData?.playwright || 'Ready'}
                </span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Cpu size={16} color="#06b6d4" />
                <span style={{ fontSize: '0.88rem', fontWeight: 700, color: '#f8fafc' }}>
                  Chromium Headless (Playwright)
                </span>
              </div>
              <p style={{ fontSize: '0.74rem', color: '#64748b', marginTop: '4px' }}>
                Full device viewport emulation, screenshot pipeline & DOM geometry.
              </p>
            </div>

            {/* Vision Intelligence */}
            <div style={{
              background: 'rgba(255, 255, 255, 0.03)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              borderRadius: '12px',
              padding: '14px'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span style={{ fontSize: '0.76rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>
                  Vision Intelligence
                </span>
                <span style={{ 
                  fontSize: '0.72rem', 
                  padding: '2px 8px', 
                  borderRadius: '9999px',
                  background: 'rgba(99, 102, 241, 0.15)',
                  color: '#818cf8',
                  fontWeight: 600,
                  textTransform: 'capitalize'
                }}>
                  {healthData?.vision_engine || 'Active'}
                </span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Eye size={16} color="#a855f7" />
                <span style={{ fontSize: '0.88rem', fontWeight: 700, color: '#f8fafc' }}>
                  {healthData?.vlm_provider === 'openai' ? 'OpenAI GPT-4o Vision' : (healthData?.vlm_provider === 'gemini' ? 'Google Gemini 1.5 Pro' : 'Autonomous Spatial VLM')}
                </span>
              </div>
              <p style={{ fontSize: '0.74rem', color: '#64748b', marginTop: '4px' }}>
                Spatial visual anomaly detection, WCAG contrast & AST patch synthesizer.
              </p>
            </div>

            {/* Database & Storage */}
            <div style={{
              background: 'rgba(255, 255, 255, 0.03)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              borderRadius: '12px',
              padding: '14px'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span style={{ fontSize: '0.76rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>
                  Persistence Storage
                </span>
                <span style={{ 
                  fontSize: '0.72rem', 
                  padding: '2px 8px', 
                  borderRadius: '9999px',
                  background: 'rgba(16, 185, 129, 0.15)',
                  color: '#34d399',
                  fontWeight: 600
                }}>
                  {healthData?.database?.status || 'Connected'}
                </span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Database size={16} color="#10b981" />
                <span style={{ fontSize: '0.88rem', fontWeight: 700, color: '#f8fafc' }}>
                  SQLite Registry ({healthData?.database?.total_runs ?? 0} runs)
                </span>
              </div>
              <p style={{ fontSize: '0.74rem', color: '#64748b', marginTop: '4px' }}>
                ACID audit runs, visual diff metadata & verified PR branches.
              </p>
            </div>

            {/* Response Latency */}
            <div style={{
              background: 'rgba(255, 255, 255, 0.03)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              borderRadius: '12px',
              padding: '14px'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span style={{ fontSize: '0.76rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>
                  Network Latency
                </span>
                <span style={{ 
                  fontSize: '0.72rem', 
                  padding: '2px 8px', 
                  borderRadius: '9999px',
                  background: latency !== null && latency < 50 ? 'rgba(16, 185, 129, 0.15)' : 'rgba(245, 158, 11, 0.15)',
                  color: latency !== null && latency < 50 ? '#34d399' : '#f59e0b',
                  fontWeight: 600
                }}>
                  {latency !== null ? `${latency} ms` : 'Measuring...'}
                </span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Zap size={16} color="#f59e0b" />
                <span style={{ fontSize: '0.88rem', fontWeight: 700, color: '#f8fafc' }}>
                  Local Host HTTP/1.1
                </span>
              </div>
              <p style={{ fontSize: '0.74rem', color: '#64748b', marginTop: '4px' }}>
                Direct loopback socket at 127.0.0.1:8000 with CORS authorization.
              </p>
            </div>

          </div>

          {/* Quick Links */}
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center', 
            borderTop: '1px solid rgba(255, 255, 255, 0.08)', 
            paddingTop: '14px' 
          }}>
            <span style={{ fontSize: '0.78rem', color: '#94a3b8', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Clock size={13} />
              <span>Server Time: {healthData?.server_time ? new Date(healthData.server_time).toLocaleTimeString() : 'N/A'}</span>
            </span>

            <div style={{ display: 'flex', gap: '10px' }}>
              <a 
                href={`${backendUrl}/docs`} 
                target="_blank" 
                rel="noreferrer"
                className="btn btn-secondary"
                style={{ fontSize: '0.78rem', padding: '6px 12px', display: 'inline-flex', alignItems: 'center', gap: '5px' }}
              >
                <span>Interactive Swagger API Docs</span>
                <ExternalLink size={12} />
              </a>
              <button 
                className="btn btn-secondary" 
                onClick={onClose}
                style={{ fontSize: '0.78rem', padding: '6px 12px' }}
              >
                Close
              </button>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}

