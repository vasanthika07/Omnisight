import React from 'react';
import { Eye, RefreshCw, Play, GitBranch, FileText, Globe, ShoppingCart, History, Smartphone } from 'lucide-react';
import { NavLink } from 'react-router-dom';

export default function Navbar({ 
  onResetBug, 
  onTriggerAudit, 
  isRunning, 
  engineInfo, 
  onOpenCIModal, 
  onOpenReportModal,
  hasRunData,
  historyCount
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

      {/* Navigation Routes */}
      <nav className="nav-routes" aria-label="Main Navigation">
        <NavLink 
          to="/" 
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          id="nav-link-devices"
          title="Universal Any-Device Testing & Dynamic Continuous Monitor"
          end
        >
          <Smartphone size={15} />
          <span>Any-Device Lab & Monitor</span>
          <span className="nav-link-badge live">Universal</span>
        </NavLink>

        <NavLink 
          to="/external" 
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          id="nav-link-external"
          title="Universal Scanner: Take any website from external sources to audit"
        >
          <Globe size={15} />
          <span>External Scanner</span>
          <span className="nav-link-badge live">Live</span>
        </NavLink>

        <NavLink 
          to="/staging" 
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          id="nav-link-staging"
          title="Internal Staging Demo Store & Chaos Anomaly Studio"
        >
          <ShoppingCart size={15} />
          <span>Staging Store</span>
        </NavLink>

        <NavLink 
          to="/history" 
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          id="nav-link-history"
          title="View all past audit runs and verification records"
        >
          <History size={15} />
          <span>History</span>
          {typeof historyCount === 'number' && historyCount > 0 && (
            <span className="nav-link-badge">{historyCount}</span>
          )}
        </NavLink>
      </nav>

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
