import React from 'react';
import { Eye, RefreshCw, Play, GitBranch, FileText } from 'lucide-react';

export default function Navbar({ 
  onResetBug, 
  onTriggerAudit, 
  isRunning, 
  engineInfo, 
  onOpenCIModal, 
  onOpenReportModal,
  hasRunData 
}) {
  return (
    <header className="top-nav">
      <div className="nav-brand">
        <div className="brand-icon-box">
          <Eye size={24} color="#ffffff" />
        </div>
        <div className="brand-titles">
          <h1>OmniSight</h1>
          <span className="tagline">Multimodal UI Self-Healing & Autonomous RPA QA</span>
        </div>
      </div>

      <div className="nav-controls">
        <div className="status-badge">
          <span className="pulse-dot"></span>
          <span>{engineInfo || 'VLM Engine: Active'}</span>
        </div>

        <button 
          className="btn btn-secondary nav-action-btn"
          onClick={onOpenCIModal}
          title="CI/CD Gateway & Automated Webhook Simulator"
        >
          <GitBranch size={15} color="#06b6d4" />
          <span>CI/CD Gateway</span>
        </button>

        {hasRunData && (
          <button 
            className="btn btn-secondary nav-action-btn"
            onClick={onOpenReportModal}
            title="Export Executive Visual QA Report"
          >
            <FileText size={15} color="#a855f7" />
            <span>Export Report</span>
          </button>
        )}

        <button 
          className="btn btn-secondary" 
          onClick={onResetBug}
          disabled={isRunning}
          title="Reset the checkout page back to intentional bug for testing"
        >
          <RefreshCw size={15} className={isRunning ? 'spin' : ''} />
          <span>Reset Bug</span>
        </button>

        <button 
          className="btn btn-primary" 
          onClick={onTriggerAudit}
          disabled={isRunning}
        >
          {isRunning ? (
            <>
              <div className="spinner"></div>
              <span>Self-Healing In Progress...</span>
            </>
          ) : (
            <>
              <Play size={15} fill="currentColor" />
              <span>Run Autonomous Audit</span>
            </>
          )}
        </button>
      </div>
    </header>
  );
}
