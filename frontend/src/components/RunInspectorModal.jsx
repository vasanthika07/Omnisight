import React, { useState } from 'react';
import {
  X,
  ShieldCheck,
  AlertTriangle,
  FileText,
  Copy,
  Check,
  ExternalLink,
  Layers,
  Sparkles,
  Zap,
  Globe,
  ShoppingCart,
  Download,
  Flame,
  CheckCircle2,
  XCircle,
  HelpCircle,
  ChevronDown,
  ChevronUp,
  Cpu,
  Eye,
  Sliders,
  Calendar,
  Code
} from 'lucide-react';
import PerformanceLevelBreakdown from './PerformanceLevelBreakdown';

export default function RunInspectorModal({
  isOpen,
  onClose,
  runData,
  backendUrl,
  onOpenReportModal
}) {
  const [activeTab, setActiveTab] = useState('edge_radar'); // 'edge_radar', 'levels', 'visual_diff', 'patch'
  const [copiedPatch, setCopiedPatch] = useState(false);
  const [copiedId, setCopiedId] = useState(false);
  const [expandedChecks, setExpandedChecks] = useState({});

  if (!isOpen || !runData) return null;

  const isExt = runData.is_external || (runData.target_url && !runData.target_url.includes('test-app'));
  const isPassed = runData.verification_passed;
  const grade = runData.grade || (runData.compliance_score >= 90 ? 'A+' : runData.compliance_score >= 80 ? 'B' : 'F');
  const score = runData.compliance_score !== undefined ? runData.compliance_score : (isPassed ? 100 : 65);

  const checklist = runData.checklist && runData.checklist.length > 0 ? runData.checklist : [];
  const defects = runData.defects || [];
  const patch = runData.patch;

  const handleCopyId = () => {
    navigator.clipboard.writeText(runData.id);
    setCopiedId(true);
    setTimeout(() => setCopiedId(false), 2000);
  };

  const handleCopyPatch = () => {
    if (!patch) return;
    const textToCopy = patch.repaired_css || patch.unified_diff || '';
    navigator.clipboard.writeText(textToCopy);
    setCopiedPatch(true);
    setTimeout(() => setCopiedPatch(false), 2000);
  };

  const handleDownloadJSON = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(runData, null, 2));
    const dlAnchorElem = document.createElement('a');
    dlAnchorElem.setAttribute("href", dataStr);
    dlAnchorElem.setAttribute("download", `omnisight-audit-${runData.id}.json`);
    dlAnchorElem.click();
  };

  const getStatusBadge = (status) => {
    switch (status?.toUpperCase()) {
      case 'PASS':
        return (
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', color: '#34d399', background: 'rgba(16, 185, 129, 0.15)', padding: '2px 8px', borderRadius: '9999px', fontSize: '0.72rem', fontWeight: 700 }}>
            <CheckCircle2 size={12} />
            PASS
          </span>
        );
      case 'REMEDIATED':
        return (
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', color: '#38bdf8', background: 'rgba(56, 189, 248, 0.15)', padding: '2px 8px', borderRadius: '9999px', fontSize: '0.72rem', fontWeight: 700 }}>
            <Sparkles size={12} />
            REMEDIATED
          </span>
        );
      case 'WARNING':
        return (
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', color: '#fbbf24', background: 'rgba(251, 191, 36, 0.15)', padding: '2px 8px', borderRadius: '9999px', fontSize: '0.72rem', fontWeight: 700 }}>
            <AlertTriangle size={12} />
            WARN
          </span>
        );
      case 'FAILED':
        return (
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', color: '#f87171', background: 'rgba(248, 113, 113, 0.15)', padding: '2px 8px', borderRadius: '9999px', fontSize: '0.72rem', fontWeight: 700 }}>
            <XCircle size={12} />
            FAIL
          </span>
        );
      default:
        return (
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', color: '#94a3b8', background: 'rgba(148, 163, 184, 0.15)', padding: '2px 8px', borderRadius: '9999px', fontSize: '0.72rem', fontWeight: 700 }}>
            <HelpCircle size={12} />
            {status || 'EVAL'}
          </span>
        );
    }
  };

  const getGradeColor = (g) => {
    switch (g) {
      case 'A+': return { text: '#34d399', bg: 'rgba(16, 185, 129, 0.15)', border: 'rgba(16, 185, 129, 0.35)' };
      case 'A': return { text: '#38bdf8', bg: 'rgba(56, 189, 248, 0.15)', border: 'rgba(56, 189, 248, 0.35)' };
      case 'B': return { text: '#a78bfa', bg: 'rgba(167, 139, 250, 0.15)', border: 'rgba(167, 139, 250, 0.35)' };
      case 'C': return { text: '#fbbf24', bg: 'rgba(251, 191, 36, 0.15)', border: 'rgba(251, 191, 36, 0.35)' };
      default: return { text: '#f87171', bg: 'rgba(248, 113, 113, 0.15)', border: 'rgba(248, 113, 113, 0.35)' };
    }
  };

  const gradeStyle = getGradeColor(grade);

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div 
        className="modal-container"
        style={{ maxWidth: '960px', maxHeight: '90vh', display: 'flex', flexDirection: 'column' }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="modal-header" style={{ padding: '16px 24px', borderBottom: '1px solid rgba(255, 255, 255, 0.08)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
            <div 
              style={{
                width: '46px',
                height: '46px',
                borderRadius: '12px',
                background: gradeStyle.bg,
                border: `1px solid ${gradeStyle.border}`,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              <span style={{ fontSize: '1.15rem', fontWeight: 900, color: gradeStyle.text, lineHeight: 1 }}>
                {grade}
              </span>
              <span style={{ fontSize: '0.62rem', fontWeight: 700, color: '#94a3b8' }}>
                {score}%
              </span>
            </div>

            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                <span style={{
                  fontSize: '0.7rem',
                  fontWeight: 700,
                  textTransform: 'uppercase',
                  padding: '2px 8px',
                  borderRadius: '9999px',
                  background: isExt ? 'rgba(6, 182, 212, 0.15)' : 'rgba(99, 102, 241, 0.15)',
                  color: isExt ? '#38bdf8' : '#a5b4fc',
                  border: `1px solid ${isExt ? 'rgba(6, 182, 212, 0.3)' : 'rgba(99, 102, 241, 0.3)'}`,
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '4px'
                }}>
                  {isExt ? <Globe size={11} /> : <ShoppingCart size={11} />}
                  <span>{isExt ? 'External Target' : 'Staging Store'}</span>
                </span>
                <span style={{ fontSize: '0.78rem', color: '#94a3b8' }}>
                  Viewport: <strong style={{ color: '#f8fafc' }}>{runData.viewport || 'mobile'}</strong>
                </span>
                <span style={{ fontSize: '0.78rem', color: '#64748b' }}>•</span>
                <span style={{ fontSize: '0.78rem', color: '#94a3b8' }}>
                  {runData.created_at ? new Date(runData.created_at).toLocaleString() : 'Recent'}
                </span>
              </div>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#f8fafc', marginTop: '2px' }}>
                {runData.page_title || runData.target_url || 'Target Application Audit'}
              </h3>
              <p style={{ fontSize: '0.78rem', color: '#94a3b8', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span>{runData.target_url}</span>
                {runData.target_url && (
                  <a href={runData.target_url} target="_blank" rel="noreferrer" style={{ color: '#818cf8', display: 'inline-flex' }}>
                    <ExternalLink size={12} />
                  </a>
                )}
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <a 
              href={`${backendUrl}/api/reports/${runData.id}?format=html`}
              target="_blank"
              rel="noreferrer"
              className="btn btn-secondary"
              style={{ fontSize: '0.78rem', padding: '6px 12px', display: 'inline-flex', alignItems: 'center', gap: '5px' }}
              title="Open print-ready Executive Visual QA Report"
            >
              <FileText size={13} color="#a855f7" />
              <span>Executive Report</span>
              <ExternalLink size={11} />
            </a>

            <button
              className="btn btn-secondary"
              onClick={handleDownloadJSON}
              style={{ fontSize: '0.78rem', padding: '6px 12px', display: 'inline-flex', alignItems: 'center', gap: '5px' }}
              title="Download raw JSON inspection record"
            >
              <Download size={13} />
              <span>JSON</span>
            </button>

            <button className="modal-close-btn" onClick={onClose}>
              <X size={18} />
            </button>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div style={{
          display: 'flex',
          gap: '8px',
          padding: '10px 24px',
          background: 'rgba(255, 255, 255, 0.02)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.06)'
        }}>
          <button
            className={`chip-btn ${activeTab === 'edge_radar' ? 'active' : ''}`}
            onClick={() => setActiveTab('edge_radar')}
          >
            <ShieldCheck size={14} />
            <span>16-Point Edge Radar ({checklist.length})</span>
          </button>
          <button
            className={`chip-btn ${activeTab === 'levels' ? 'active' : ''}`}
            onClick={() => setActiveTab('levels')}
          >
            <Sliders size={14} />
            <span>5-Level Evaluation Breakdown</span>
          </button>
          <button
            className={`chip-btn ${activeTab === 'visual_diff' ? 'active' : ''}`}
            onClick={() => setActiveTab('visual_diff')}
          >
            <Eye size={14} />
            <span>Visual Diff & Screenshots</span>
          </button>
          {patch && (
            <button
              className={`chip-btn ${activeTab === 'patch' ? 'active' : ''}`}
              onClick={() => setActiveTab('patch')}
            >
              <Code size={14} />
              <span>Self-Healing CSS Patch</span>
            </button>
          )}
        </div>

        {/* Modal Scrollable Body */}
        <div className="modal-body" style={{ padding: '20px 24px', overflowY: 'auto', flex: 1 }}>

          {/* TAB 1: 16-POINT EDGE RADAR */}
          {activeTab === 'edge_radar' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#f8fafc' }}>
                    16-Point Autonomous Visual QA Checklist
                  </h4>
                  <p style={{ fontSize: '0.78rem', color: '#94a3b8' }}>
                    WCAG accessibility, responsive viewport blowout, and RPA interaction verification.
                  </p>
                </div>
                <div style={{ display: 'flex', gap: '8px', fontSize: '0.75rem' }}>
                  <span style={{ color: '#34d399', fontWeight: 600 }}>
                    {checklist.filter(c => c.status === 'PASS' || c.status === 'REMEDIATED').length} Passed
                  </span>
                  <span style={{ color: '#64748b' }}>•</span>
                  <span style={{ color: '#f87171', fontWeight: 600 }}>
                    {checklist.filter(c => c.status === 'FAILED' || c.status === 'WARNING').length} Flaws
                  </span>
                </div>
              </div>

              {checklist.length === 0 ? (
                <div style={{ padding: '30px', textAlign: 'center', background: 'rgba(255, 255, 255, 0.02)', borderRadius: '12px' }}>
                  <ShieldCheck size={32} color="#10b981" style={{ margin: '0 auto 8px' }} />
                  <p style={{ color: '#94a3b8', fontSize: '0.85rem' }}>
                    All standard visual checks completed with no anomalous geometry.
                  </p>
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {checklist.map((item) => {
                    const isExpanded = expandedChecks[item.id];
                    return (
                      <div 
                        key={item.id}
                        style={{
                          background: 'rgba(255, 255, 255, 0.03)',
                          border: '1px solid rgba(255, 255, 255, 0.06)',
                          borderRadius: '10px',
                          overflow: 'hidden'
                        }}
                      >
                        <div 
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between',
                            padding: '10px 14px',
                            cursor: 'pointer'
                          }}
                          onClick={() => setExpandedChecks(prev => ({ ...prev, [item.id]: !prev[item.id] }))}
                        >
                          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                            {getStatusBadge(item.status)}
                            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#f8fafc' }}>
                              {item.name}
                            </span>
                            {item.category && (
                              <span style={{ fontSize: '0.7rem', color: '#64748b', background: 'rgba(255, 255, 255, 0.05)', padding: '1px 6px', borderRadius: '4px' }}>
                                {item.category}
                              </span>
                            )}
                          </div>

                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <span style={{ fontSize: '0.72rem', color: '#94a3b8' }}>
                              Weight: {item.weight}%
                            </span>
                            {isExpanded ? <ChevronUp size={14} color="#94a3b8" /> : <ChevronDown size={14} color="#94a3b8" />}
                          </div>
                        </div>

                        {isExpanded && (
                          <div style={{ padding: '10px 14px 14px', borderTop: '1px solid rgba(255, 255, 255, 0.04)', background: 'rgba(0, 0, 0, 0.15)' }}>
                            <p style={{ fontSize: '0.8rem', color: '#cbd5e1', marginBottom: '6px' }}>
                              {item.explanation || 'Evaluated for responsive UI standard adherence.'}
                            </p>
                            {item.remediation && (
                              <div style={{ fontSize: '0.76rem', color: '#38bdf8', background: 'rgba(56, 189, 248, 0.08)', padding: '6px 10px', borderRadius: '6px', borderLeft: '3px solid #38bdf8' }}>
                                <strong>Remediation:</strong> {item.remediation}
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}

          {/* TAB 2: 5-LEVEL BREAKDOWN */}
          {activeTab === 'levels' && (
            <div>
              <PerformanceLevelBreakdown 
                runData={runData}
                targetUrl={runData.target_url}
                title="Evaluation Tier Breakdown & Remediations"
              />
            </div>
          )}

          {/* TAB 3: VISUAL DIFF & SCREENSHOTS */}
          {activeTab === 'visual_diff' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
                
                {/* Before Screenshot */}
                <div style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '12px', padding: '12px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <span style={{ fontSize: '0.78rem', fontWeight: 700, color: '#f87171' }}>
                      BASELINE / BEFORE
                    </span>
                    <span style={{ fontSize: '0.7rem', color: '#94a3b8' }}>
                      {defects.length} defect(s) detected
                    </span>
                  </div>
                  {runData.before_screenshot ? (
                    <img 
                      src={`${backendUrl}/screenshots/${runData.before_screenshot}`} 
                      alt="Before Audit"
                      style={{ width: '100%', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.1)', objectFit: 'contain', maxHeight: '380px', background: '#000' }}
                    />
                  ) : (
                    <div style={{ height: '200px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#64748b' }}>
                      No baseline screenshot
                    </div>
                  )}
                </div>

                {/* After Screenshot */}
                <div style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '12px', padding: '12px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <span style={{ fontSize: '0.78rem', fontWeight: 700, color: '#34d399' }}>
                      HEALED / AFTER
                    </span>
                    <span style={{ fontSize: '0.7rem', color: '#34d399' }}>
                      {isPassed ? 'Verified Healed' : 'Under Review'}
                    </span>
                  </div>
                  {runData.after_screenshot ? (
                    <img 
                      src={`${backendUrl}/screenshots/${runData.after_screenshot}`} 
                      alt="After Audit"
                      style={{ width: '100%', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.1)', objectFit: 'contain', maxHeight: '380px', background: '#000' }}
                    />
                  ) : (
                    <div style={{ height: '200px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#64748b' }}>
                      Clean baseline (no healing required)
                    </div>
                  )}
                </div>

                {/* Pixel Diff Heatmap */}
                {runData.diff_screenshot && (
                  <div style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '12px', padding: '12px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                      <span style={{ fontSize: '0.78rem', fontWeight: 700, color: '#ec4899' }}>
                        PIXEL DIFF HEATMAP
                      </span>
                      <span style={{ fontSize: '0.7rem', color: '#a855f7' }}>
                        Structural shift overlay
                      </span>
                    </div>
                    <img 
                      src={`${backendUrl}/screenshots/${runData.diff_screenshot}`} 
                      alt="Diff Heatmap"
                      style={{ width: '100%', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.1)', objectFit: 'contain', maxHeight: '380px', background: '#000' }}
                    />
                  </div>
                )}

              </div>
            </div>
          )}

          {/* TAB 4: SYNTHESIZED CSS PATCH */}
          {activeTab === 'patch' && patch && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#f8fafc' }}>
                    Autonomous Git Unified Diff & CSS Mutation
                  </h4>
                  <p style={{ fontSize: '0.78rem', color: '#94a3b8' }}>
                    Applied to <code style={{ color: '#cbd5e1' }}>{patch.file_path || 'styles.css'}</code>
                  </p>
                </div>
                <button
                  className="btn btn-secondary"
                  onClick={handleCopyPatch}
                  style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem', padding: '6px 12px' }}
                >
                  {copiedPatch ? <Check size={14} color="#10b981" /> : <Copy size={14} />}
                  <span>{copiedPatch ? 'Copied to Clipboard' : 'Copy Patch'}</span>
                </button>
              </div>

              {patch.unified_diff && (
                <div style={{
                  background: '#090d16',
                  borderRadius: '10px',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  padding: '14px',
                  fontFamily: 'JetBrains Mono, monospace',
                  fontSize: '0.8rem',
                  overflowX: 'auto',
                  lineHeight: 1.6
                }}>
                  <pre style={{ margin: 0, color: '#94a3b8' }}>
                    {patch.unified_diff.split('\n').map((line, idx) => {
                      let color = '#94a3b8';
                      let bg = 'transparent';
                      if (line.startsWith('+')) {
                        color = '#34d399';
                        bg = 'rgba(16, 185, 129, 0.1)';
                      } else if (line.startsWith('-')) {
                        color = '#f87171';
                        bg = 'rgba(239, 68, 68, 0.1)';
                      } else if (line.startsWith('@@')) {
                        color = '#818cf8';
                      }
                      return (
                        <div key={idx} style={{ color, backgroundColor: bg, padding: '0 4px', borderRadius: '2px' }}>
                          {line}
                        </div>
                      );
                    })}
                  </pre>
                </div>
              )}
            </div>
          )}

        </div>

        {/* Footer */}
        <div className="modal-footer" style={{ padding: '12px 24px', borderTop: '1px solid rgba(255, 255, 255, 0.08)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.78rem', color: '#94a3b8' }}>
            <span>Run ID:</span>
            <code style={{ color: '#cbd5e1' }}>{runData.id}</code>
            <button 
              onClick={handleCopyId}
              style={{ background: 'transparent', border: 'none', color: '#818cf8', cursor: 'pointer', padding: '2px' }}
              title="Copy Run ID"
            >
              {copiedId ? <Check size={12} color="#10b981" /> : <Copy size={12} />}
            </button>
          </div>

          <button className="btn btn-primary" onClick={onClose}>
            Done
          </button>
        </div>
      </div>
    </div>
  );
}

