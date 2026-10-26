import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import MetricsBar from './components/MetricsBar';
import StagingView from './components/StagingView';
import ExternalScannerView from './components/ExternalScannerView';
import HistoryView from './components/HistoryView';
import PRModal from './components/PRModal';
import CIWebhookModal from './components/CIWebhookModal';
import ExportReportModal from './components/ExportReportModal';
import { Sparkles } from 'lucide-react';

const BACKEND_URL = 'http://127.0.0.1:8000';

export default function App() {
  const [viewport, setViewport] = useState('mobile');
  const [targetUrl, setTargetUrl] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const [engineInfo, setEngineInfo] = useState('');
  const [selectedEngine, setSelectedEngine] = useState('builtin');
  const [currentRun, setCurrentRun] = useState(null);
  const [history, setHistory] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [stagingHealth, setStagingHealth] = useState('Compliant');
  
  // Modals
  const [isPRModalOpen, setIsPRModalOpen] = useState(false);
  const [isCIModalOpen, setIsCIModalOpen] = useState(false);
  const [isReportModalOpen, setIsReportModalOpen] = useState(false);
  const [bannerNotice, setBannerNotice] = useState(null);

  const fetchAnalytics = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/analytics`);
      const data = await res.json();
      setAnalytics(data);
    } catch (e) {
      console.warn('Could not fetch analytics:', e);
    }
  };

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

  // Load system info, analytics, and history on mount
  useEffect(() => {
    fetch(`${BACKEND_URL}/`)
      .then((res) => res.json())
      .then((data) => {
        setEngineInfo(`VLM: ${data.vlm_provider_configured.toUpperCase()}`);
      })
      .catch(() => setEngineInfo('VLM: Autonomous Spatial Engine'));

    fetchHistory();
    fetchAnalytics();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const showBanner = (msg) => {
    setBannerNotice(msg);
    setTimeout(() => setBannerNotice(null), 4500);
  };

  const handleTriggerAudit = async () => {
    setIsRunning(true);
    setBannerNotice(`OmniSight QA Agent Dispatched: Navigating & Inspecting ${viewport === 'matrix' ? 'All Viewports' : viewport}...`);
    try {
      const endpoint = viewport === 'matrix' ? `${BACKEND_URL}/api/audit-matrix` : `${BACKEND_URL}/api/audit`;
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          viewport,
          target_url: targetUrl || null,
          max_retries: 2,
          engine: selectedEngine
        })
      });
      const data = await res.json();
      setCurrentRun(data);
      setStagingHealth(data.verification_passed ? 'Compliant' : 'Anomaly Detected');
      fetchHistory();
      fetchAnalytics();
      showBanner(`Audit Complete: ${data.verification_passed ? 'Self-Healing Verified Successfully!' : 'Action Required'}`);
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
      setStagingHealth('Anomaly Active');
      showBanner(data.message || 'Reset to intentional 520px bug state.');
    } catch (e) {
      alert('Reset failed: ' + e.message);
    }
  };

  const handleInjectChaosBug = async (scenarioId) => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/inject-bug`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario: scenarioId })
      });
      const data = await res.json();
      setStagingHealth(`${scenarioId.toUpperCase()} Injected`);
      showBanner(data.message || `Chaos Anomaly '${scenarioId}' Injected.`);
    } catch (e) {
      alert('Inject failed: ' + e.message);
    }
  };

  const handleResetClean = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/reset-clean`, { method: 'POST' });
      const data = await res.json();
      setStagingHealth('Compliant (Clean)');
      showBanner(data.message || 'Reset stylesheet to 100% compliant clean state.');
    } catch (e) {
      alert('Clean reset failed: ' + e.message);
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
    if (data.success) {
      setCurrentRun(prev => prev ? { ...prev, pr_number: data.pr_number, pr_url: data.pr_url } : prev);
      showBanner(`PR #${data.pr_number || 42} created: ${data.message || 'Pull request prepared successfully.'}`);
    }
    fetchHistory();
    fetchAnalytics();
    return data;
  };

  return (
    <div className="dashboard-layout">
      <Navbar 
        onResetBug={handleResetBug}
        onTriggerAudit={handleTriggerAudit}
        isRunning={isRunning}
        engineInfo={engineInfo}
        onOpenCIModal={() => setIsCIModalOpen(true)}
        onOpenReportModal={() => setIsReportModalOpen(true)}
        hasRunData={Boolean(currentRun)}
        historyCount={history.length}
      />

      <MetricsBar 
        analytics={analytics} 
        stagingStatus={stagingHealth} 
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
        <Routes>
          <Route 
            path="/" 
            element={
              <StagingView 
                viewport={viewport}
                setViewport={setViewport}
                targetUrl={targetUrl}
                setTargetUrl={setTargetUrl}
                isRunning={isRunning}
                onTriggerAudit={handleTriggerAudit}
                onResetBug={handleResetBug}
                onInjectChaosBug={handleInjectChaosBug}
                onResetClean={handleResetClean}
                selectedEngine={selectedEngine}
                setSelectedEngine={setSelectedEngine}
                currentRun={currentRun}
                backendUrl={BACKEND_URL}
                onOpenPRModal={() => setIsPRModalOpen(true)}
              />
            } 
          />
          <Route 
            path="/staging" 
            element={<Navigate to="/" replace />} 
          />
          <Route 
            path="/external" 
            element={
              <ExternalScannerView 
                backendUrl={BACKEND_URL}
                currentRun={currentRun}
                setCurrentRun={setCurrentRun}
                isRunning={isRunning}
                setIsRunning={setIsRunning}
                fetchHistory={fetchHistory}
                fetchAnalytics={fetchAnalytics}
                showBanner={showBanner}
                onOpenPRModal={() => setIsPRModalOpen(true)}
              />
            } 
          />
          <Route 
            path="/history" 
            element={
              <HistoryView 
                history={history}
                setCurrentRun={setCurrentRun}
                backendUrl={BACKEND_URL}
                onOpenReportModal={() => setIsReportModalOpen(true)}
              />
            } 
          />
          <Route 
            path="*" 
            element={<Navigate to="/" replace />} 
          />
        </Routes>
      </main>

      {/* GitHub PR Modal */}
      <PRModal 
        key={currentRun?.id || 'none'}
        isOpen={isPRModalOpen}
        onClose={() => setIsPRModalOpen(false)}
        runData={currentRun}
        onConfirmPR={handleConfirmPR}
      />

      {/* CI/CD Gateway Simulator Modal */}
      <CIWebhookModal 
        isOpen={isCIModalOpen}
        onClose={() => setIsCIModalOpen(false)}
        backendUrl={BACKEND_URL}
        onJobTriggered={(job) => {
          showBanner(`CI/CD Webhook Triggered: Job ${job.job_id}`);
          fetchHistory();
          fetchAnalytics();
        }}
      />

      {/* Executive QA Report Modal */}
      <ExportReportModal 
        isOpen={isReportModalOpen}
        onClose={() => setIsReportModalOpen(false)}
        runData={currentRun}
        backendUrl={BACKEND_URL}
      />
    </div>
  );
}
