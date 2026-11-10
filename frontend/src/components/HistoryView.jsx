import React, { useState, useEffect } from 'react';
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
  Filter,
  FileText,
  Eye,
  Download,
  Copy,
  Check,
  Award,
  Sliders,
  Sparkles,
  Zap,
  Clock,
  ArrowUpDown
} from 'lucide-react';
import { useNavigate, useParams } from 'react-router-dom';
import RunInspectorModal from './RunInspectorModal';

export default function HistoryView({
  history = [],
  setCurrentRun,
  backendUrl = 'http://127.0.0.1:8000',
  onOpenReportModal
}) {
  const { runId } = useParams();
  const [filterType, setFilterType] = useState('all'); // all, external, staging
  const [gradeFilter, setGradeFilter] = useState('all'); // all, A+, A, B, C, F
  const [statusFilter, setStatusFilter] = useState('all'); // all, compliant, defects
  const [sortBy, setSortBy] = useState('newest'); // newest, oldest, score_desc, defects_desc
  const [searchTerm, setSearchTerm] = useState('');
  
  // Inspection Modal State
  const [inspectedRun, setInspectedRun] = useState(null);
  const [isInspectorOpen, setIsInspectorOpen] = useState(false);
  const [copiedRunId, setCopiedRunId] = useState(null);

  const navigate = useNavigate();

  // If URL has /history/:runId, auto-open that run in inspector
  useEffect(() => {
    if (runId && history.length > 0) {
      const targetRun = history.find((r) => r.id === runId);
      if (targetRun) {
        setInspectedRun(targetRun);
        setIsInspectorOpen(true);
      }
    }
  }, [runId, history]);

  // Filter & Sort Logic
  const filteredRuns = history.filter((run) => {
    const isExt = run.is_external || (run.target_url && !run.target_url.includes('test-app'));
    if (filterType === 'external' && !isExt) return false;
    if (filterType === 'staging' && isExt) return false;

    // Grade Filter
    const runGrade = run.grade || (run.compliance_score >= 90 ? 'A+' : run.compliance_score >= 80 ? 'B' : 'F');
    if (gradeFilter !== 'all' && runGrade !== gradeFilter) return false;

    // Status Filter
    if (statusFilter === 'compliant' && !run.verification_passed) return false;
    if (statusFilter === 'defects' && run.defects_found === 0) return false;

    // Search Term
    if (searchTerm.trim()) {
      const q = searchTerm.toLowerCase();
      const matchUrl = run.target_url ? run.target_url.toLowerCase().includes(q) : false;
      const matchTitle = run.page_title ? run.page_title.toLowerCase().includes(q) : false;
      const matchId = run.id ? run.id.toLowerCase().includes(q) : false;
      const matchViewport = run.viewport ? run.viewport.toLowerCase().includes(q) : false;
      return matchUrl || matchTitle || matchId || matchViewport;
    }
    return true;
  }).sort((a, b) => {
    if (sortBy === 'newest') {
      return new Date(b.created_at || 0) - new Date(a.created_at || 0);
    }
    if (sortBy === 'oldest') {
      return new Date(a.created_at || 0) - new Date(b.created_at || 0);
    }
    if (sortBy === 'score_desc') {
      return (b.compliance_score ?? 100) - (a.compliance_score ?? 100);
    }
    if (sortBy === 'defects_desc') {
      return (b.defects_found ?? 0) - (a.defects_found ?? 0);
    }
    return 0;
  });

  // Calculate Aggregates for Header
  const totalAudits = history.length;
  const compliantCount = history.filter(r => r.verification_passed).length;
  const totalDefects = history.reduce((acc, r) => acc + (r.defects_found || 0), 0);
  const avgScore = totalAudits > 0 
    ? Math.round(history.reduce((acc, r) => acc + (r.compliance_score ?? (r.verification_passed ? 100 : 70)), 0) / totalAudits)
    : 100;
  const avgGrade = avgScore >= 95 ? 'A+' : avgScore >= 90 ? 'A' : avgScore >= 80 ? 'B' : avgScore >= 70 ? 'C' : 'F';

  const handleInspectRun = (run, e) => {
    if (e) e.stopPropagation();
    setInspectedRun(run);
    setIsInspectorOpen(true);
  };

  const handleLoadInWorkspace = (run, e) => {
    if (e) e.stopPropagation();
    setCurrentRun(run);
    const isExt = run.is_external || (run.target_url && !run.target_url.includes('test-app'));
    if (isExt) {
      navigate('/external');
    } else {
      navigate('/');
    }
  };

  const handleDownloadJSON = (run, e) => {
    if (e) e.stopPropagation();
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(run, null, 2));
    const dlAnchorElem = document.createElement('a');
    dlAnchorElem.setAttribute("href", dataStr);
    dlAnchorElem.setAttribute("download", `omnisight-audit-${run.id}.json`);
    dlAnchorElem.click();
  };

  const handleCopyId = (id, e) => {
    if (e) e.stopPropagation();
    navigator.clipboard.writeText(id);
    setCopiedRunId(id);
    setTimeout(() => setCopiedRunId(null), 2000);
  };

  const getViewportIcon = (vp) => {
    switch (vp?.toLowerCase()) {
      case 'mobile':
      case 'iphone 15 pro':
      case 'pixel 8':
        return <Smartphone size={13} />;
      case 'tablet':
      case 'ipad pro 11"':
        return <Tablet size={13} />;
      case 'desktop':
      case 'macbook pro 16"':
      case 'full hd monitor':
        return <Monitor size={13} />;
      default:
        return <Layers size={13} />;
    }
  };

  const getGradeStyle = (g) => {
    switch (g) {
      case 'A+': return { text: '#34d399', bg: 'rgba(16, 185, 129, 0.15)', border: 'rgba(16, 185, 129, 0.35)' };
      case 'A': return { text: '#38bdf8', bg: 'rgba(56, 189, 248, 0.15)', border: 'rgba(56, 189, 248, 0.35)' };
      case 'B': return { text: '#a78bfa', bg: 'rgba(167, 139, 250, 0.15)', border: 'rgba(167, 139, 250, 0.35)' };
      case 'C': return { text: '#fbbf24', bg: 'rgba(251, 191, 36, 0.15)', border: 'rgba(251, 191, 36, 0.35)' };
      default: return { text: '#f87171', bg: 'rgba(248, 113, 113, 0.15)', border: 'rgba(248, 113, 113, 0.35)' };
    }
  };

  return (
    <div className="history-page">
      
      {/* Executive Header Banner */}
      <div className="history-header">
        <div>
          <h2 style={{ fontSize: '1.45rem', fontWeight: 800, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <History size={24} color="#818cf8" />
            <span>Audit History & Verification Registry</span>
          </h2>
          <p style={{ fontSize: '0.85rem', color: '#94a3b8', marginTop: '4px' }}>
            Enterprise audit registry of multimodal UI inspections, self-healing visual diffs, and compliance records.
          </p>
        </div>

        {/* Search Bar */}
        <div className="history-search-bar" style={{ minWidth: '320px' }}>
          <Search size={16} color="#94a3b8" />
          <input
            type="text"
            placeholder="Search by URL, domain, run ID, or device..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          {searchTerm && (
            <button
              onClick={() => setSearchTerm('')}
              style={{ background: 'transparent', border: 'none', color: '#94a3b8', cursor: 'pointer', fontSize: '1.1rem' }}
            >
              ×
            </button>
          )}
        </div>
      </div>

      {/* Stakeholder Executive Summary Bar */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '14px',
        background: 'rgba(16, 23, 38, 0.6)',
        border: '1px solid rgba(255, 255, 255, 0.08)',
        borderRadius: '16px',
        padding: '16px 20px',
        backdropFilter: 'blur(10px)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ width: '38px', height: '38px', borderRadius: '10px', background: 'rgba(99, 102, 241, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <History size={20} color="#818cf8" />
          </div>
          <div>
            <span style={{ fontSize: '0.72rem', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 600 }}>Audits Logged</span>
            <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#f8fafc' }}>{totalAudits} Runs</div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ width: '38px', height: '38px', borderRadius: '10px', background: 'rgba(16, 185, 129, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Award size={20} color="#10b981" />
          </div>
          <div>
            <span style={{ fontSize: '0.72rem', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 600 }}>Fleet Quality</span>
            <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#34d399' }}>Grade {avgGrade} ({avgScore}%)</div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ width: '38px', height: '38px', borderRadius: '10px', background: 'rgba(245, 158, 11, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Sparkles size={20} color="#f59e0b" />
          </div>
          <div>
            <span style={{ fontSize: '0.72rem', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 600 }}>Defects Healed</span>
            <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#f8fafc' }}>{totalDefects} Remediated</div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ width: '38px', height: '38px', borderRadius: '10px', background: 'rgba(6, 182, 212, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Clock size={20} color="#06b6d4" />
          </div>
          <div>
            <span style={{ fontSize: '0.72rem', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 600 }}>Effort Saved</span>
            <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#38bdf8' }}>~{(totalAudits * 4.5).toFixed(0)} Eng Hours</div>
          </div>
        </div>
      </div>

      {/* Filter and Sorting Controls Strip */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
        
        {/* Source & Status Filters */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Source:
          </span>
          <button
            className={`chip-btn ${filterType === 'all' ? 'active' : ''}`}
            onClick={() => setFilterType('all')}
          >
            <span>All ({history.length})</span>
          </button>
          <button
            className={`chip-btn ${filterType === 'external' ? 'active' : ''}`}
            onClick={() => setFilterType('external')}
          >
            <Globe size={13} />
            <span>External ({history.filter(r => r.is_external || (r.target_url && !r.target_url.includes('test-app'))).length})</span>
          </button>
          <button
            className={`chip-btn ${filterType === 'staging' ? 'active' : ''}`}
            onClick={() => setFilterType('staging')}
          >
            <ShoppingCart size={13} />
            <span>Staging ({history.filter(r => !r.is_external && (!r.target_url || r.target_url.includes('test-app'))).length})</span>
          </button>

          <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em', marginLeft: '12px' }}>
            Grade:
          </span>
          {['all', 'A+', 'A', 'B', 'C', 'F'].map(g => (
            <button
              key={g}
              className={`chip-btn ${gradeFilter === g ? 'active' : ''}`}
              onClick={() => setGradeFilter(g)}
              style={{ minWidth: '32px', textAlign: 'center' }}
            >
              <span>{g === 'all' ? 'All' : g}</span>
            </button>
          ))}
        </div>

        {/* Sort Selector */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <ArrowUpDown size={14} color="#94a3b8" />
          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#94a3b8' }}>Sort:</span>
          <select 
            value={sortBy} 
            onChange={(e) => setSortBy(e.target.value)}
            style={{
              background: 'rgba(255, 255, 255, 0.05)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '8px',
              padding: '6px 12px',
              color: '#f8fafc',
              fontSize: '0.78rem',
              cursor: 'pointer'
            }}
          >
            <option value="newest" style={{ background: '#0f172a' }}>Newest First</option>
            <option value="oldest" style={{ background: '#0f172a' }}>Oldest First</option>
            <option value="score_desc" style={{ background: '#0f172a' }}>Highest Score</option>
            <option value="defects_desc" style={{ background: '#0f172a' }}>Most Defects</option>
          </select>
        </div>

      </div>

      {/* Cards Grid */}
      {filteredRuns.length === 0 ? (
        <div style={{
          textAlign: 'center',
          padding: '60px 24px',
          background: 'rgba(16, 23, 38, 0.4)',
          borderRadius: '16px',
          border: '1px dashed rgba(255, 255, 255, 0.1)'
        }}>
          <History size={42} color="#64748b" style={{ margin: '0 auto 12px' }} />
          <h3 style={{ fontSize: '1.05rem', color: '#f8fafc', marginBottom: '6px' }}>No audit runs found</h3>
          <p style={{ fontSize: '0.84rem', color: '#94a3b8' }}>
            {searchTerm ? `No records matching "${searchTerm}". Try another keyword or reset filters.` : 'Launch an audit to start recording compliance history.'}
          </p>
        </div>
      ) : (
        <div className="history-grid">
          {filteredRuns.map((run) => {
            const isExt = run.is_external || (run.target_url && !run.target_url.includes('test-app'));
            const isPassed = run.verification_passed;
            const defectCount = run.defects_found || 0;
            const runGrade = run.grade || (run.compliance_score >= 90 ? 'A+' : run.compliance_score >= 80 ? 'B' : 'F');
            const runScore = run.compliance_score !== undefined ? run.compliance_score : (isPassed ? 100 : 70);
            const gradeStyle = getGradeStyle(runGrade);
            const weakAreas = run.weak_areas || [];
            const levels = run.performance_levels || [];

            return (
              <div 
                key={run.id} 
                className="history-card"
                onClick={(e) => handleInspectRun(run, e)}
                title="Click to inspect 16-point checklist, performance levels, and visual diffs"
                style={{ cursor: 'pointer' }}
              >
                {/* Header */}
                <div className="history-card-header" style={{ alignItems: 'flex-start' }}>
                  <div style={{ display: 'flex', gap: '12px', flex: 1, minWidth: 0 }}>
                    {/* Grade Badge */}
                    <div 
                      style={{
                        width: '42px',
                        height: '42px',
                        borderRadius: '10px',
                        background: gradeStyle.bg,
                        border: `1px solid ${gradeStyle.border}`,
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'center',
                        flexShrink: 0
                      }}
                    >
                      <span style={{ fontSize: '1.05rem', fontWeight: 900, color: gradeStyle.text, lineHeight: 1 }}>
                        {runGrade}
                      </span>
                      <span style={{ fontSize: '0.6rem', fontWeight: 700, color: '#94a3b8' }}>
                        {runScore}%
                      </span>
                    </div>

                    <div style={{ minWidth: 0, flex: 1 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px', flexWrap: 'wrap' }}>
                        <span 
                          style={{ 
                            display: 'inline-flex', 
                            alignItems: 'center', 
                            gap: '4px', 
                            fontSize: '0.68rem', 
                            fontWeight: 700, 
                            padding: '2px 7px', 
                            borderRadius: '9999px',
                            background: isExt ? 'rgba(6, 182, 212, 0.14)' : 'rgba(99, 102, 241, 0.14)',
                            border: `1px solid ${isExt ? 'rgba(6, 182, 212, 0.3)' : 'rgba(99, 102, 241, 0.3)'}`,
                            color: isExt ? '#38bdf8' : '#a5b4fc',
                            textTransform: 'uppercase'
                          }}
                        >
                          {isExt ? <Globe size={10} /> : <ShoppingCart size={10} />}
                          <span>{isExt ? 'External' : 'Staging'}</span>
                        </span>

                        <span style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '4px',
                          fontSize: '0.68rem',
                          fontWeight: 600,
                          padding: '2px 6px',
                          borderRadius: '4px',
                          background: 'rgba(255, 255, 255, 0.05)',
                          color: '#cbd5e1'
                        }}>
                          {getViewportIcon(run.viewport)}
                          <span>{run.viewport}</span>
                        </span>
                      </div>

                      <h4 className="history-card-title" style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {run.page_title || run.target_url || 'Target Application'}
                      </h4>
                      <p className="history-card-url" style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {run.target_url || 'http://127.0.0.1:8000/test-app/index.html'}
                      </p>
                    </div>
                  </div>

                  <span
                    className="status-badge"
                    style={{
                      padding: '4px 8px',
                      fontSize: '0.72rem',
                      background: isPassed ? 'rgba(16, 185, 129, 0.12)' : 'rgba(239, 68, 68, 0.12)',
                      borderColor: isPassed ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)',
                      color: isPassed ? '#34d399' : '#f87171',
                      flexShrink: 0
                    }}
                  >
                    {isPassed ? <CheckCircle2 size={12} /> : <AlertTriangle size={12} />}
                    <span>{isPassed ? 'Compliant' : 'Defect Found'}</span>
                  </span>
                </div>

                {/* Performance Levels Mini Preview */}
                {levels.length > 0 && (
                  <div style={{ marginTop: '10px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.68rem', color: '#94a3b8' }}>
                      <span>5-Level Evaluation</span>
                      <span>{levels.filter(l => l.status === 'PASS').length}/5 Passed</span>
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '4px', height: '6px' }}>
                      {levels.map((lvl) => {
                        const isLvlPass = lvl.status === 'PASS';
                        const isLvlWarn = lvl.status === 'WARN';
                        const barColor = isLvlPass ? '#10b981' : (isLvlWarn ? '#f59e0b' : '#ef4444');
                        return (
                          <div 
                            key={lvl.level}
                            title={`${lvl.name}: ${lvl.score}% (${lvl.status})`}
                            style={{ 
                              height: '100%', 
                              background: barColor, 
                              borderRadius: '2px',
                              opacity: 0.85
                            }}
                          />
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* Weak Areas or Clean State Tag */}
                <div style={{ marginTop: '10px' }}>
                  {weakAreas.length > 0 ? (
                    <div style={{ 
                      fontSize: '0.72rem', 
                      color: '#f59e0b', 
                      background: 'rgba(245, 158, 11, 0.08)', 
                      padding: '4px 8px', 
                      borderRadius: '6px',
                      border: '1px solid rgba(245, 158, 11, 0.2)',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '5px'
                    }}>
                      <AlertTriangle size={11} />
                      <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        Weak Area: {weakAreas[0].name}
                      </span>
                    </div>
                  ) : (
                    <div style={{ 
                      fontSize: '0.72rem', 
                      color: '#34d399', 
                      background: 'rgba(16, 185, 129, 0.08)', 
                      padding: '4px 8px', 
                      borderRadius: '6px',
                      border: '1px solid rgba(16, 185, 129, 0.2)',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '5px'
                    }}>
                      <ShieldCheck size={11} />
                      <span>All 16 Dynamic Edge Cases Verified</span>
                    </div>
                  )}
                </div>

                {/* Metrics Stats Row */}
                <div className="history-card-stats" style={{ marginTop: '10px' }}>
                  <div className="history-stat-item">
                    <span>Defects</span>
                    <strong style={{ color: defectCount > 0 ? '#f59e0b' : '#34d399' }}>
                      {defectCount} detected
                    </strong>
                  </div>
                  <div className="history-stat-item">
                    <span>Engine</span>
                    <strong style={{ textTransform: 'capitalize' }}>
                      {run.engine_used?.includes('openai') ? 'GPT-4o' : (run.engine_used?.includes('gemini') ? 'Gemini' : 'Built-in VLM')}
                    </strong>
                  </div>
                  <div className="history-stat-item">
                    <span>Date</span>
                    <strong style={{ fontSize: '0.72rem', color: '#cbd5e1' }}>
                      {run.created_at ? new Date(run.created_at).toLocaleDateString() : 'Recent'}
                    </strong>
                  </div>
                </div>

                {/* Action Buttons Bar */}
                <div 
                  style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'space-between', 
                    borderTop: '1px solid rgba(255, 255, 255, 0.06)', 
                    paddingTop: '10px',
                    marginTop: '12px' 
                  }}
                  onClick={(e) => e.stopPropagation()}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <code style={{ fontSize: '0.7rem', color: '#94a3b8' }}>
                      {run.id.slice(0, 10)}...
                    </code>
                    <button
                      onClick={(e) => handleCopyId(run.id, e)}
                      style={{ background: 'transparent', border: 'none', color: '#818cf8', cursor: 'pointer', padding: '2px' }}
                      title="Copy Run ID"
                    >
                      {copiedRunId === run.id ? <Check size={11} color="#10b981" /> : <Copy size={11} />}
                    </button>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <a
                      href={`${backendUrl}/api/reports/${run.id}?format=html`}
                      target="_blank"
                      rel="noreferrer"
                      className="btn btn-secondary"
                      style={{ padding: '4px 8px', fontSize: '0.72rem', display: 'inline-flex', alignItems: 'center', gap: '4px' }}
                      title="View printable executive HTML report"
                    >
                      <FileText size={11} color="#a855f7" />
                      <span>Report</span>
                    </a>

                    <button
                      className="btn btn-secondary"
                      onClick={(e) => handleDownloadJSON(run, e)}
                      style={{ padding: '4px 8px', fontSize: '0.72rem', display: 'inline-flex', alignItems: 'center', gap: '4px' }}
                      title="Download raw JSON inspection record"
                    >
                      <Download size={11} />
                      <span>JSON</span>
                    </button>

                    <button
                      className="btn btn-primary"
                      onClick={(e) => handleInspectRun(run, e)}
                      style={{ padding: '4px 10px', fontSize: '0.72rem', display: 'inline-flex', alignItems: 'center', gap: '4px' }}
                      title="Inspect full details, 16-point checklist, and screenshots"
                    >
                      <Eye size={11} />
                      <span>Inspect</span>
                    </button>
                  </div>
                </div>

              </div>
            );
          })}
        </div>
      )}

      {/* Comprehensive Run Inspector Modal */}
      <RunInspectorModal
        isOpen={isInspectorOpen}
        onClose={() => setIsInspectorOpen(false)}
        runData={inspectedRun}
        backendUrl={backendUrl}
        onOpenReportModal={onOpenReportModal}
      />

    </div>
  );
}
