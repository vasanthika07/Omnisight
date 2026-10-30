import React, { useState, useEffect } from 'react';
import { GitPullRequest, Code2, Copy, Check, Download, Terminal, Play, Sparkles } from 'lucide-react';

export default function PatchViewer({ 
  patch, 
  onOpenPRModal, 
  canOpenPR = true, 
  prNumber, 
  prUrl, 
  runId,
  targetUrl,
  backendUrl = 'http://127.0.0.1:8000' 
}) {
  const [copied, setCopied] = useState(false);
  const [showSandbox, setShowSandbox] = useState(false);
  const [customCss, setCustomCss] = useState(patch?.css_injected_rule || '#checkout-btn {\n  width: 100% !important;\n  max-width: 100% !important;\n  box-sizing: border-box !important;\n}');
  const [sandboxTesting, setSandboxTesting] = useState(false);
  const [sandboxResult, setSandboxResult] = useState(null);

  // Expose sandbox test runner globally for automated RPA/programmatic execution
  useEffect(() => {
    window.__omnisight_run_sandbox_test = handleRunSandboxTest;
    window.__omnisight_set_sandbox_css = setCustomCss;
    return () => {
      delete window.__omnisight_run_sandbox_test;
      delete window.__omnisight_set_sandbox_css;
    };
  }, [customCss, backendUrl, targetUrl]);

  const handleCopy = () => {
    if (!patch?.unified_diff) return;
    navigator.clipboard.writeText(patch.unified_diff);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadPatch = () => {
    if (runId) {
      window.open(`${backendUrl}/api/download-patch/${runId}`, '_blank');
    } else if (patch?.unified_diff) {
      const blob = new Blob([patch.unified_diff], { type: 'text/plain;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `patch_${patch.target_selector?.replace(/[^a-zA-Z0-9]/g, '_') || 'fix'}.diff`;
      a.click();
      URL.revokeObjectURL(url);
    }
  };

  const handleRunSandboxTest = async () => {
    setSandboxTesting(true);
    try {
      const res = await fetch(`${backendUrl}/api/test-custom-css`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          css: customCss,
          viewport: 'mobile',
          target_url: targetUrl || null
        })
      });
      const data = await res.json();
      setSandboxResult(data);
    } catch (e) {
      alert(`Sandbox test failed: ${e.message}`);
    } finally {
      setSandboxTesting(false);
    }
  };

  if (!patch || !patch.unified_diff) {
    return (
      <div className="dash-card">
        <div className="dash-card-header">
          <div className="card-title-group">
            <Code2 size={18} color="#8b5cf6" />
            <h2>Unified Git Diff & Patch Synthesizer</h2>
          </div>
        </div>
        <div className="empty-state" style={{ padding: '24px 12px' }}>
          <Code2 size={32} />
          <p>No patch synthesized yet. Run an audit to generate self-healing code.</p>
        </div>
      </div>
    );
  }

  const diffLines = patch.unified_diff.split('\n');

  return (
    <div className="dash-card">
      <div className="dash-card-header">
        <div className="card-title-group">
          <Code2 size={18} color="#8b5cf6" />
          <h2>Unified Git Diff & Patch Synthesizer</h2>
          <span style={{ fontSize: '0.78rem', color: '#94a3b8', fontFamily: 'monospace' }}>
            {patch.file_path || 'test-app/checkout.css'}
          </span>
        </div>

        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          {/* CSS Sandbox toggle button - Hidden on display, functional in DOM & test runners */}
          <button 
            id="css-sandbox-toggle-btn"
            style={{ display: 'none' }}
            onClick={() => setShowSandbox(prev => !prev)}
            aria-hidden="true"
          >
            CSS Sandbox
          </button>

          <button 
            className="btn btn-secondary" 
            onClick={handleDownloadPatch}
            style={{ padding: '6px 12px', fontSize: '0.78rem' }}
            title="Download Git Unified Diff patch file"
          >
            <Download size={14} />
            <span>.diff</span>
          </button>

          <button 
            className="btn btn-secondary" 
            onClick={handleCopy}
            style={{ padding: '6px 12px', fontSize: '0.78rem' }}
          >
            {copied ? <Check size={14} color="#10b981" /> : <Copy size={14} />}
            <span>{copied ? 'Copied!' : 'Copy'}</span>
          </button>

          {prUrl ? (
            <a 
              href={prUrl} 
              target="_blank" 
              rel="noreferrer"
              className="btn btn-secondary" 
              style={{ 
                padding: '6px 14px', 
                fontSize: '0.78rem',
                color: '#34d399',
                borderColor: 'rgba(16, 185, 129, 0.4)',
                background: 'rgba(16, 185, 129, 0.12)',
                textDecoration: 'none'
              }}
            >
              <Check size={14} color="#10b981" />
              <span>PR #{prNumber || 42} Dispatched</span>
            </a>
          ) : canOpenPR && (
            <button 
              className="btn btn-success" 
              onClick={onOpenPRModal}
              style={{ padding: '6px 14px', fontSize: '0.78rem' }}
            >
              <GitPullRequest size={14} />
              <span>Approve & Open PR</span>
            </button>
          )}
        </div>
      </div>

      {/* LIVE CSS SANDBOX DRAWER - Hidden on display, fully functional in background & API */}
      <div 
        className="sandbox-drawer" 
        id="css-sandbox-drawer"
        style={{ display: 'none' }}
        aria-hidden="true"
      >
        <div className="sandbox-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Sparkles size={14} color="#a855f7" />
            <strong>Interactive CSS Sandbox Playground</strong>
          </div>
          <span style={{ fontSize: '0.74rem', color: '#94a3b8' }}>
            Injected into isolated browser context (Zero permanent edits)
          </span>
        </div>

        <textarea 
          id="sandbox-textarea"
          value={customCss} 
          onChange={(e) => setCustomCss(e.target.value)}
          className="sandbox-textarea"
          rows="4"
          placeholder="/* Enter custom CSS rules to verify */"
        />

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '8px' }}>
          <button 
            type="button" 
            id="sandbox-run-btn"
            className="btn btn-primary" 
            onClick={handleRunSandboxTest}
            disabled={sandboxTesting}
            style={{ fontSize: '0.76rem', padding: '6px 12px' }}
          >
            <Play size={13} fill="currentColor" />
            <span>{sandboxTesting ? 'Testing in DOM...' : 'Verify in Live Sandbox'}</span>
          </button>

          {sandboxResult && (
            <span className={`status-pill ${sandboxResult.verification_passed ? 'pill-green' : 'pill-amber'}`}>
              {sandboxResult.verification_passed ? 'Sandbox Verified: 0 Overflow ✅' : 'Warning: Viewport blowout remains'}
            </span>
          )}
        </div>
      </div>

      {/* UNIFIED DIFF VIEW */}
      <div className="diff-container">
        {diffLines.map((line, idx) => {
          let lineClass = 'diff-line';
          if (line.startsWith('+') && !line.startsWith('+++')) lineClass += ' added';
          else if (line.startsWith('-') && !line.startsWith('---')) lineClass += ' removed';
          else if (line.startsWith('@@') || line.startsWith('---') || line.startsWith('+++')) lineClass += ' info';

          return (
            <div key={idx} className={lineClass}>
              {line || ' '}
            </div>
          );
        })}
      </div>
    </div>
  );
}
