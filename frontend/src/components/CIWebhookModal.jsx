import React, { useState, useEffect } from 'react';
import { GitPullRequest, GitBranch, GitCommit, X, Play, CheckCircle2, Clock, AlertTriangle, ExternalLink } from 'lucide-react';

export default function CIWebhookModal({ isOpen, onClose, backendUrl = 'http://127.0.0.1:8000', onJobTriggered }) {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [repo, setRepo] = useState('infotact/omnisight-store');
  const [branch, setBranch] = useState('staging');
  const [commitSha, setCommitSha] = useState('c9a4f21');

  const fetchJobs = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${backendUrl}/webhook/jobs`);
      const data = await res.json();
      setJobs(data.jobs || []);
    } catch (e) {
      console.warn('Could not fetch CI jobs:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchJobs();
      const interval = setInterval(fetchJobs, 3000);
      return () => clearInterval(interval);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSimulateWebhook = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const res = await fetch(`${backendUrl}/webhook/build`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          repository: repo,
          branch: branch,
          commit_sha: commitSha || Math.random().toString(16).slice(2, 9),
          environment: 'staging'
        })
      });
      const data = await res.json();
      if (onJobTriggered) onJobTriggered(data);
      fetchJobs();
    } catch (err) {
      alert(`Simulation failed: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-card wide-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <GitBranch size={20} color="#06b6d4" />
            <h2 style={{ fontSize: '1.2rem', fontWeight: 700 }}>
              CI/CD Automation Gateway & Webhook Simulator
            </h2>
          </div>
          <button 
            onClick={onClose} 
            style={{ background: 'transparent', border: 'none', color: '#94a3b8', cursor: 'pointer' }}
          >
            <X size={20} />
          </button>
        </div>

        <div className="modal-body">
          <div className="ci-intro-card">
            <p>
              OmniSight intercepts automated build webhooks from <strong>GitHub Actions</strong>, <strong>GitLab CI</strong>, or <strong>Jenkins</strong>.
              When a developer commits to staging, OmniSight autonomously tests the preview build, detects layout defects, synthesizes fixes, and dispatches a verification PR.
            </p>
          </div>

          <form onSubmit={handleSimulateWebhook} className="ci-trigger-form">
            <div className="form-row-grid">
              <div className="input-group">
                <label>Target Repository</label>
                <input 
                  type="text" 
                  value={repo} 
                  onChange={(e) => setRepo(e.target.value)} 
                  className="modal-input" 
                />
              </div>

              <div className="input-group">
                <label>Branch / Ref</label>
                <input 
                  type="text" 
                  value={branch} 
                  onChange={(e) => setBranch(e.target.value)} 
                  className="modal-input" 
                />
              </div>

              <div className="input-group">
                <label>Commit SHA</label>
                <input 
                  type="text" 
                  value={commitSha} 
                  onChange={(e) => setCommitSha(e.target.value)} 
                  className="modal-input" 
                />
              </div>
            </div>

            <button 
              type="submit" 
              className="btn btn-primary" 
              disabled={submitting}
              style={{ alignSelf: 'flex-start', marginTop: '10px' }}
            >
              <Play size={14} fill="currentColor" />
              <span>{submitting ? 'Triggering Background QA Agent...' : 'Simulate CI Webhook Push'}</span>
            </button>
          </form>

          <div className="ci-jobs-list-section">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
              <h3 style={{ fontSize: '0.92rem', fontWeight: 700, color: '#f8fafc' }}>
                Recent CI/CD Webhook Interceptions ({jobs.length})
              </h3>
              <button 
                type="button" 
                onClick={fetchJobs} 
                className="btn btn-secondary" 
                style={{ fontSize: '0.74rem', padding: '4px 10px' }}
              >
                Refresh
              </button>
            </div>

            <div className="ci-jobs-container">
              {jobs.length === 0 ? (
                <div style={{ padding: '24px', textAlign: 'center', color: '#64748b', fontSize: '0.84rem' }}>
                  No webhook events received yet. Click "Simulate CI Webhook Push" above to dispatch a test trigger.
                </div>
              ) : (
                jobs.map((job) => {
                  const isCompleted = job.status === 'completed';
                  const isRunning = job.status === 'running' || job.status === 'queued';
                  const isFailed = job.status === 'failed';

                  return (
                    <div key={job.job_id} className="ci-job-row">
                      <div className="ci-job-left">
                        {isCompleted ? (
                          <CheckCircle2 size={18} color="#10b981" />
                        ) : isRunning ? (
                          <div className="spinner" style={{ width: '16px', height: '16px', borderWidth: '2px' }}></div>
                        ) : (
                          <AlertTriangle size={18} color="#ef4444" />
                        )}
                        <div className="ci-job-meta">
                          <span className="ci-job-id">{job.job_id}</span>
                          <span className="ci-job-repo">
                            {job.payload?.repository} • <code>{job.payload?.branch}</code> ({job.payload?.commit_sha?.slice(0, 7)})
                          </span>
                        </div>
                      </div>

                      <div className="ci-job-right">
                        <span className={`status-pill ${isCompleted ? 'pill-green' : (isRunning ? 'pill-amber' : 'pill-red')}`}>
                          {job.status.toUpperCase()}
                        </span>
                        {job.result?.id && (
                          <span style={{ fontSize: '0.75rem', color: '#818cf8', fontFamily: 'monospace' }}>
                            Run: {job.result.id.slice(0, 12)}
                          </span>
                        )}
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>
            Close Gateway
          </button>
        </div>
      </div>
    </div>
  );
}
