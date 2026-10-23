import React from 'react';
import { Eye, RefreshCw, Play } from 'lucide-react';

export default function Navbar({ onResetBug, onTriggerAudit, isRunning, engineInfo }) {
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
          className="btn btn-secondary" 
          onClick={onResetBug}
          disabled={isRunning}
          title="Reset the checkout page back to intentional bug for testing"
        >
          <RefreshCw size={16} className={isRunning ? 'spin' : ''} />
          <span>Reset Staging Bug</span>
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
              <Play size={16} fill="currentColor" />
              <span>Run Autonomous Audit</span>
            </>
          )}
        </button>
      </div>
    </header>
  );
}
