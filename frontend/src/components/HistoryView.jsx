import React, { useState } from 'react';
import { 
  History, 
  Search, 
  Globe, 
  ShoppingCart, 
  Smartphone, 
  Tablet, 
  Monitor, 
  Layers, 
  CheckCircle2, 
  AlertTriangle, 
  ShieldCheck, 
  ArrowRight, 
  ExternalLink,
  Calendar,
  Filter
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function HistoryView({
  history,
  setCurrentRun,
  backendUrl,
  onOpenReportModal
}) {
  const [filterType, setFilterType] = useState('all'); // all, external, staging
  const [searchTerm, setSearchTerm] = useState('');
  const navigate = useNavigate();

  const filteredRuns = history.filter((run) => {
    const isExt = run.is_external || (run.target_url && !run.target_url.includes('test-app'));
    if (filterType === 'external' && !isExt) return false;
    if (filterType === 'staging' && isExt) return false;

    if (searchTerm.trim()) {
      const q = searchTerm.toLowerCase();
      const matchUrl = run.target_url ? run.target_url.toLowerCase().includes(q) : false;
      const matchTitle = run.page_title ? run.page_title.toLowerCase().includes(q) : false;
      const matchId = run.id ? run.id.toLowerCase().includes(q) : false;
      const matchViewport = run.viewport ? run.viewport.toLowerCase().includes(q) : false;
      return matchUrl || matchTitle || matchId || matchViewport;
    }
    return true;
  });

  const handleSelectRun = (run) => {
    setCurrentRun(run);
    const isExt = run.is_external || (run.target_url && !run.target_url.includes('test-app'));
    if (isExt) {
      navigate('/external');
    } else {
      navigate('/');
    }
  };

  const getViewportIcon = (vp) => {
    switch (vp?.toLowerCase()) {
      case 'mobile':
        return <Smartphone size={13} />;
      case 'tablet':
        return <Tablet size={13} />;
      case 'desktop':
        return <Monitor size={13} />;
      default:
        return <Layers size={13} />;
    }
  };

  return (
    <div className="history-page">
      <div className="history-header">
        <div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <History size={22} color="#818cf8" />
            <span>Audit History & Verification Records</span>
          </h2>
          <p style={{ fontSize: '0.84rem', color: '#94a3b8', marginTop: '4px' }}>
            Chronological log of autonomous multimodal UI audits, self-healing cycles, and visual diff artifacts.
          </p>
        </div>

        {/* Search Bar */}
        <div className="history-search-bar">
          <Search size={16} color="#94a3b8" />
          <input
            type="text"
            placeholder="Search by URL, domain, or run ID..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          {searchTerm && (
            <button
              onClick={() => setSearchTerm('')}
              style={{ background: 'transparent', border: 'none', color: '#94a3b8', cursor: 'pointer' }}
            >
              ×
            </button>
          )}
        </div>
      </div>

      {/* Filter Tabs */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
        <span style={{ fontSize: '0.78rem', fontWeight: 700, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          Filter Source:
        </span>
        <button
          className={`chip-btn ${filterType === 'all' ? 'active' : ''}`}
          onClick={() => setFilterType('all')}
        >
          <span>All Audits ({history.length})</span>
        </button>
        <button
          className={`chip-btn ${filterType === 'external' ? 'active' : ''}`}
          onClick={() => setFilterType('external')}
        >
          <Globe size={13} />
          <span>External Websites ({history.filter(r => r.is_external || (r.target_url && !r.target_url.includes('test-app'))).length})</span>
        </button>
        <button
          className={`chip-btn ${filterType === 'staging' ? 'active' : ''}`}
          onClick={() => setFilterType('staging')}
        >
          <ShoppingCart size={13} />
          <span>Staging Store ({history.filter(r => !r.is_external && (!r.target_url || r.target_url.includes('test-app'))).length})</span>
        </button>
      </div>

      {/* Cards Grid */}
      {filteredRuns.length === 0 ? (
        <div style={{
          textAlign: 'center',
          padding: '48px 24px',
          background: 'rgba(16, 23, 38, 0.4)',
          borderRadius: '16px',
          border: '1px dashed rgba(255, 255, 255, 0.1)'
        }}>
          <History size={36} color="#64748b" style={{ margin: '0 auto 12px' }} />
          <h3 style={{ fontSize: '1rem', color: '#f8fafc', marginBottom: '6px' }}>No audit runs found</h3>
          <p style={{ fontSize: '0.84rem', color: '#94a3b8' }}>
            {searchTerm ? `No records matching "${searchTerm}". Try a different keyword.` : 'Launch an audit to start recording compliance history.'}
          </p>
        </div>
      ) : (
        <div className="history-grid">
          {filteredRuns.map((run) => {
            const isExt = run.is_external || (run.target_url && !run.target_url.includes('test-app'));
            const isPassed = run.verification_passed;
            const defectCount = run.defects_found || 0;

            return (
              <div 
                key={run.id} 
                className="history-card"
                onClick={() => handleSelectRun(run)}
                title="Click to view full inspection details"
              >
                <div className="history-card-header">
                  <div>
                    <span 
                      style={{ 
                        display: 'inline-flex', 
                        alignItems: 'center', 
                        gap: '5px', 
                        fontSize: '0.7rem', 
                        fontWeight: 700, 
                        padding: '3px 8px', 
                        borderRadius: '9999px',
                        marginBottom: '6px',
                        background: isExt ? 'rgba(6, 182, 212, 0.14)' : 'rgba(99, 102, 241, 0.14)',
                        border: `1px solid ${isExt ? 'rgba(6, 182, 212, 0.3)' : 'rgba(99, 102, 241, 0.3)'}`,
                        color: isExt ? '#38bdf8' : '#a5b4fc',
                        textTransform: 'uppercase'
                      }}
                    >
                      {isExt ? <Globe size={11} /> : <ShoppingCart size={11} />}
                      <span>{isExt ? 'External Source' : 'Staging Store'}</span>
                    </span>
                    <h4 className="history-card-title">{run.page_title || run.target_url || 'Target Application'}</h4>
                    <p className="history-card-url">{run.target_url || 'http://127.0.0.1:8000/test-app/index.html'}</p>
                  </div>

                  <span
                    className="status-badge"
                    style={{
                      padding: '4px 8px',
                      fontSize: '0.72rem',
                      background: isPassed ? 'rgba(16, 185, 129, 0.12)' : 'rgba(239, 68, 68, 0.12)',
                      borderColor: isPassed ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)',
                      color: isPassed ? '#34d399' : '#f87171'
                    }}
                  >
                    {isPassed ? <CheckCircle2 size={12} /> : <AlertTriangle size={12} />}
                    <span>{isPassed ? 'Compliant' : 'Defect Found'}</span>
                  </span>
                </div>

                {/* Metrics Grid */}
                <div className="history-card-stats">
                  <div className="history-stat-item">
                    <span>Viewport</span>
                    <strong style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                      {getViewportIcon(run.viewport)}
                      <span>{run.viewport}</span>
                    </strong>
                  </div>
                  <div className="history-stat-item">
                    <span>Defects</span>
                    <strong style={{ color: defectCount > 0 ? '#f59e0b' : '#34d399' }}>
                      {defectCount} detected
                    </strong>
                  </div>
                  <div className="history-stat-item">
                    <span>Engine</span>
                    <strong style={{ textTransform: 'capitalize' }}>
                      {run.engine_used?.includes('openai') ? 'GPT-4o' : (run.engine_used?.includes('gemini') ? 'Gemini' : 'Built-in')}
                    </strong>
                  </div>
                </div>

                {/* Card Footer */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.75rem', color: '#94a3b8' }}>
                  <span>ID: <code style={{ color: '#cbd5e1' }}>{run.id}</code></span>
                  <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', color: '#818cf8', fontWeight: 600 }}>
                    Inspect Run <ArrowRight size={13} />
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
