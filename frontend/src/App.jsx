import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import ControlBar from './components/ControlBar';
import VisualDiffInspector from './components/VisualDiffInspector';
import AgentTimeline from './components/AgentTimeline';
import DefectCard from './components/DefectCard';
import PatchViewer from './components/PatchViewer';
import PRModal from './components/PRModal';
import { History, Shield, Sparkles, CheckCircle2 } from 'lucide-react';

const BACKEND_URL = 'http://127.0.0.1:8000';

export default function App() {
  const [viewport, setViewport] = useState('mobile');
  const [targetUrl, setTargetUrl] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const [engineInfo, setEngineInfo] = useState('');
  const [currentRun, setCurrentRun] = useState(null);
  const [history, setHistory] = useState([]);
  const [isPRModalOpen, setIsPRModalOpen] = useState(false);
  const [bannerNotice, setBannerNotice] = useState(null);

  // Load system info and recent history on mount
  useEffect(() => {
    fetch(`${BACKEND_URL}/`)
      .then((res) => res.json())
      .then((data) => {
        setEngineInfo(`VLM: ${data.vlm_provider_configured.toUpperCase()}`);
      })
      .catch(() => setEngineInfo('VLM: Autonomous Spatial Engine'));

    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/history`);
      const data = await res.json();
      setHistory(data.runs || []);
      if (!currentRun && data.runs && data.runs.length > 0) {
        setCurrentRun(data.runs[0]);
      }
    } catch (e) {
      console.warn('Could not fetch history:', e);
    }
  };

  const showBanner = (msg) => {
    setBannerNotice(msg);
    setTimeout(() => setBannerNotice(null), 4000);
  };

  const handleTriggerAudit = async () => {
    setIsRunning(true);
    setBannerNotice('OmniSight Autonomous QA Agent Dispatched: Navigating & Inspecting...');
    try {
      const res = await fetch(`${BACKEND_URL}/api/audit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          viewport,
          target_url: targetUrl || null,
          max_retries: 2
        })
      });
      const data = await res.json();
      setCurrentRun(data);
      fetchHistory();
      showBanner(`Audit Complete: ${data.verification_passed ? 'Self-Healing Verified Successfully!' : 'Audit Finished'}`);
    } catch (err) {
      alert(`Audit failed: ${err.message}`);
    } finally {
      setIsRunning(false);
    }
  };

  const handleResetBug = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/reset-bug`, { method: 'POST' });
      const data = await res.json();
      showBanner(data.message || 'Reset to intentional bug state.');
    } catch (e) {
      alert('Reset failed: ' + e.message);
    }
  };

  const handleConfirmPR = async (runId, customTitle, customNotes) => {
    const res = await fetch(`${BACKEND_URL}/api/approve-pr`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        run_id: runId,
        custom_title: customTitle,
        custom_notes: customNotes
      })
    });
    const data = await res.json();
    fetchHistory();
    return data;
  };

  return (
    <div className="dashboard-layout">
      <Navbar 
        onResetBug={handleResetBug}
        onTriggerAudit={handleTriggerAudit}
        isRunning={isRunning}
        engineInfo={engineInfo}
      />

      {bannerNotice && (
        <div style={{
          background: 'linear-gradient(90deg, #6366f1 0%, #a855f7 100%)',
          color: '#ffffff',
          padding: '8px 24px',
          fontSize: '0.82rem',
          fontWeight: 600,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '8px'
        }}>
          <Sparkles size={16} />
          <span>{bannerNotice}</span>
        </div>
      )}

      <main className="dashboard-main">
        <ControlBar 
          viewport={viewport}
          setViewport={setViewport}
          targetUrl={targetUrl}
          setTargetUrl={setTargetUrl}
          isRunning={isRunning}
        />

        <div className="dashboard-grid">
          {/* Left Column: Visual Diff Inspector & Unified Diff */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <VisualDiffInspector 
              runData={currentRun} 
              backendUrl={BACKEND_URL} 
            />

            <PatchViewer 
              patch={currentRun?.patch} 
              onOpenPRModal={() => setIsPRModalOpen(true)}
              canOpenPR={currentRun?.verification_passed}
            />
          </div>

          {/* Right Column: Timeline, Diagnostics & History */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <AgentTimeline 
              timeline={currentRun?.timeline} 
              isRunning={isRunning} 
            />

            <DefectCard 
              defects={currentRun?.defects} 
              confidenceScore={currentRun?.timeline?.find(t => t.step === 'defect_detection')?.details?.confidence}
            />

            {/* Recent Audit History List */}
            {history.length > 0 && (
              <div className="dash-card">
                <div className="dash-card-header">
                  <div className="card-title-group">
                    <History size={18} color="#94a3b8" />
                    <h2>Audit History ({history.length})</h2>
                  </div>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '240px', overflowY: 'auto' }}>
                  {history.map((h) => (
                    <div 
                      key={h.id}
                      onClick={() => setCurrentRun(h)}
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        padding: '10px 14px',
                        borderRadius: '8px',
                        background: currentRun?.id === h.id ? 'rgba(99, 102, 241, 0.15)' : 'rgba(255,255,255,0.02)',
                        border: currentRun?.id === h.id ? '1px solid rgba(99, 102, 241, 0.4)' : '1px solid var(--border-color)',
                        cursor: 'pointer'
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{
                          width: '8px',
                          height: '8px',
                          borderRadius: '50%',
                          background: h.verification_passed ? '#10b981' : '#f59e0b'
                        }}></span>
                        <span style={{ fontSize: '0.82rem', fontFamily: 'monospace' }}>{h.id.slice(0, 16)}</span>
                      </div>
                      <span style={{ fontSize: '0.74rem', color: '#94a3b8' }}>
                        {h.viewport} • {h.defects_found} defect(s)
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </main>

      <PRModal 
        isOpen={isPRModalOpen}
        onClose={() => setIsPRModalOpen(false)}
        runData={currentRun}
        onConfirmPR={handleConfirmPR}
      />
    </div>
  );
}
