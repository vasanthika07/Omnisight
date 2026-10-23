import React, { useState } from 'react';
import { GitPullRequest, Code2, Copy, Check } from 'lucide-react';

export default function PatchViewer({ patch, onOpenPRModal, canOpenPR = true, prNumber, prUrl }) {
  const [copied, setCopied] = useState(false);

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

  const handleCopy = () => {
    navigator.clipboard.writeText(patch.unified_diff);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

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

        <div style={{ display: 'flex', gap: '8px' }}>
          <button 
            className="btn btn-secondary" 
            onClick={handleCopy}
            style={{ padding: '6px 12px', fontSize: '0.78rem' }}
          >
            {copied ? <Check size={14} color="#10b981" /> : <Copy size={14} />}
            <span>{copied ? 'Copied!' : 'Copy Diff'}</span>
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
