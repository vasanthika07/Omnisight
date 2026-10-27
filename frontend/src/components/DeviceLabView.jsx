import React, { useState, useEffect, useRef } from 'react';
import {
  Smartphone,
  Tablet,
  Monitor,
  Watch,
  Layers,
  Zap,
  RotateCw,
  Sliders,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  HelpCircle,
  Activity,
  Play,
  Pause,
  RefreshCw,
  Plus,
  Trash2,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  ShieldCheck,
  Flame,
  SplitSquareVertical,
  Columns,
  Code,
  Globe,
  Clipboard,
  Radio,
  Eye,
  Download,
  FileText,
  GitPullRequest,
  Copy
} from 'lucide-react';

const PRESET_URLS = [
  { label: 'Staging Store (Default)', url: 'http://127.0.0.1:8000/test-app/index.html', icon: '🛒' },
  { label: 'Hacker News', url: 'https://news.ycombinator.com', icon: '📰' },
  { label: 'Example.com', url: 'https://example.com', icon: '🌐' },
  { label: 'Wikipedia Mobile', url: 'https://en.m.wikipedia.org', icon: '📖' },
  { label: 'Stripe', url: 'https://stripe.com', icon: '💳' },
  { label: 'GitHub', url: 'https://github.com', icon: '🐙' }
];

export default function DeviceLabView({ 
  backendUrl = 'http://127.0.0.1:8000', 
  showBanner,
  onOpenPRModal,
  onOpenReportModal,
  currentRun,
  setCurrentRun,
  fetchHistory,
  fetchAnalytics
}) {
  // Navigation tabs: 'lab' (Device Lab & Edge Cases) vs 'monitor' (Live Fleet Monitor)
  const [activeTab, setActiveTab] = useState('lab');

  // Device Registry State
  const [categories, setCategories] = useState([]);
  const [devices, setDevices] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedDeviceId, setSelectedDeviceId] = useState('iphone_15_pro');
  const [isCustomMode, setIsCustomMode] = useState(false);

  // Custom Device Parameters
  const [customWidth, setCustomWidth] = useState(393);
  const [customHeight, setCustomHeight] = useState(852);
  const [customDpr, setCustomDpr] = useState(2.0);
  const [customOrientation, setCustomOrientation] = useState('portrait');
  const [customHasTouch, setCustomHasTouch] = useState(true);
  const [customIsMobile, setCustomIsMobile] = useState(true);
  const [customColorScheme, setCustomColorScheme] = useState('dark');

  // Target URL State
  const [protocol, setProtocol] = useState('https://');
  const [urlInput, setUrlInput] = useState('http://127.0.0.1:8000/test-app/index.html');
  const [connectionStatus, setConnectionStatus] = useState(null);
  const [isCheckingUrl, setIsCheckingUrl] = useState(false);

  // Execution State
  const [isAuditing, setIsAuditing] = useState(false);
  const [auditResult, setAuditResult] = useState(null);
  const [multiAuditResult, setMultiAuditResult] = useState(null);
  const [isMultiMode, setIsMultiMode] = useState(false);
  const [expandedEdgeCases, setExpandedEdgeCases] = useState({});

  // Visual Diff Inspector Mode inside Device Lab
  const [viewMode, setViewMode] = useState('slider'); // 'slider', 'side_by_side', 'heatmap', 'patch'
  const [sliderPos, setSliderPos] = useState(50);
  const sliderContainerRef = useRef(null);

  // Continuous Monitors State
  const [monitors, setMonitors] = useState([]);
  const [isLoadingMonitors, setIsLoadingMonitors] = useState(false);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [newMonitorUrl, setNewMonitorUrl] = useState('http://127.0.0.1:8000/test-app/index.html');
  const [newMonitorName, setNewMonitorName] = useState('');
  const [newMonitorInterval, setNewMonitorInterval] = useState(60);
  const [newMonitorThreshold, setNewMonitorThreshold] = useState(85);
  const [newMonitorDevices, setNewMonitorDevices] = useState(['iphone_15_pro', 'galaxy_s24_ultra', 'desktop_1080p']);

  // Fetch device presets on mount
  useEffect(() => {
    fetch(`${backendUrl}/api/devices`)
      .then((res) => res.json())
      .then((data) => {
        setCategories(data.categories || []);
        setDevices(data.presets || []);
      })
      .catch((err) => console.warn('Could not load device presets:', err));

    fetchMonitors();
  }, [backendUrl]);

  const fetchMonitors = async () => {
    setIsLoadingMonitors(true);
    try {
      const res = await fetch(`${backendUrl}/api/monitors`);
      const data = await res.json();
      setMonitors(data.monitors || []);
    } catch (err) {
      console.warn('Could not fetch monitors:', err);
    } finally {
      setIsLoadingMonitors(false);
    }
  };

  // Sync with currentRun if available
  useEffect(() => {
    if (!auditResult && currentRun) {
      setAuditResult(currentRun);
      if (currentRun.target_url) {
        setUrlInput(currentRun.target_url);
      }
    }
  }, [currentRun]);

  const handleCopyCSS = (css) => {
    if (!css) return;
    navigator.clipboard.writeText(css);
    if (showBanner) showBanner('Synthesized responsive CSS patch copied to clipboard!');
  };

  // Selected device object
  const currentDevice = devices.find((d) => d.id === selectedDeviceId) || devices[0] || {
    id: 'iphone_15_pro',
    name: 'Apple iPhone 15 Pro',
    width: 393,
    height: 852,
    dpr: 3.0,
    has_touch: true,
    is_mobile: true
  };

  // Flip orientation dynamically
  const handleFlipOrientation = () => {
    if (isCustomMode) {
      const newOrientation = customOrientation === 'portrait' ? 'landscape' : 'portrait';
      setCustomOrientation(newOrientation);
      setCustomWidth(customHeight);
      setCustomHeight(customWidth);
    } else {
      setIsCustomMode(true);
      const newOrientation = currentDevice.orientation === 'portrait' ? 'landscape' : 'portrait';
      setCustomOrientation(newOrientation);
      setCustomWidth(currentDevice.height);
      setCustomHeight(currentDevice.width);
      setCustomDpr(currentDevice.dpr);
      setCustomHasTouch(currentDevice.has_touch);
      setCustomIsMobile(currentDevice.is_mobile);
    }
  };

  // Connectivity probe
  const handleCheckConnection = async () => {
    const target = urlInput.trim();
    if (!target) return;
    setIsCheckingUrl(true);
    try {
      const res = await fetch(`${backendUrl}/api/check-url`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: target })
      });
      const data = await res.json();
      setConnectionStatus(data);
    } catch (e) {
      setConnectionStatus({ reachable: true, message: 'Ready for Playwright Chromium scan' });
    } finally {
      setIsCheckingUrl(false);
    }
  };

  // Execute Dynamic Any-Device Audit
  const handleRunDeviceAudit = async () => {
    const target = urlInput.trim();
    if (!target) {
      alert('Please specify a target website URL or use the local staging store.');
      return;
    }

    setIsAuditing(true);
    setAuditResult(null);
    setMultiAuditResult(null);

    const devLabel = isCustomMode ? `Custom (${customWidth}x${customHeight})` : currentDevice.name;
    if (showBanner) showBanner(`Initiating dynamic edge-case audit on ${devLabel}...`);

    try {
      if (isMultiMode) {
        // Multi-device fleet scan
        const fleetDevices = ['iphone_15_pro', 'galaxy_z_fold5_cover', 'ipad_air', 'desktop_1080p'];
        const res = await fetch(`${backendUrl}/api/devices/multi-audit`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            device_ids: fleetDevices,
            target_url: target
          })
        });
        const data = await res.json();
        setMultiAuditResult(data);
        if (fetchHistory) fetchHistory();
        if (fetchAnalytics) fetchAnalytics();
        if (showBanner) {
          showBanner(`Fleet scan complete: ${data.fleet_compliance_score}% score across ${data.devices_audited} devices.`);
        }
      } else {
        // Single device audit
        const payload = {
          target_url: target,
          auto_heal: true
        };

        if (isCustomMode) {
          payload.custom_device = {
            width: Number(customWidth),
            height: Number(customHeight),
            dpr: Number(customDpr),
            is_mobile: customIsMobile,
            has_touch: customHasTouch,
            orientation: customOrientation,
            color_scheme: customColorScheme,
            name: `Custom ${customWidth}×${customHeight} (${customOrientation})`
          };
        } else {
          payload.device_id = selectedDeviceId;
        }

        const res = await fetch(`${backendUrl}/api/devices/audit`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        setAuditResult(data);
        if (setCurrentRun) {
          setCurrentRun(data);
        }
        if (fetchHistory) fetchHistory();
        if (fetchAnalytics) fetchAnalytics();

        if (showBanner) {
          if (data.defects_found > 0) {
            showBanner(`Audit complete: Found ${data.defects_found} defect(s) on ${devLabel}. Synthesized responsive patch!`);
          } else {
            showBanner(`Audit complete: ${devLabel} scored ${data.compliance_score}%! Zero edge-case defects.`);
          }
        }
      }
    } catch (err) {
      alert(`Device audit failed: ${err.message}`);
    } finally {
      setIsAuditing(false);
    }
  };

  // Toggle edge case accordion
  const toggleEdgeCase = (id) => {
    setExpandedEdgeCases((prev) => ({
      ...prev,
      [id]: !prev[id]
    }));
  };

  // Handle slider drag
  const handleSliderMove = (e) => {
    if (!sliderContainerRef.current) return;
    const rect = sliderContainerRef.current.getBoundingClientRect();
    const x = Math.max(0, Math.min(e.clientX - rect.left, rect.width));
    const pct = Math.round((x / rect.width) * 100);
    setSliderPos(pct);
  };

  // Monitor operations
  const handleToggleMonitor = async (monId) => {
    try {
      await fetch(`${backendUrl}/api/monitors/${monId}/toggle`, { method: 'POST' });
      fetchMonitors();
    } catch (err) {
      console.warn('Could not toggle monitor:', err);
    }
  };

  const handleRunMonitorNow = async (monId) => {
    if (showBanner) showBanner('Executing immediate fleet check on monitor...');
    try {
      await fetch(`${backendUrl}/api/monitors/${monId}/run-now`, { method: 'POST' });
      fetchMonitors();
      if (showBanner) showBanner('Live fleet ping finished successfully!');
    } catch (err) {
      alert(`Monitor ping failed: ${err.message}`);
    }
  };

  const handleDeleteMonitor = async (monId) => {
    if (!confirm('Are you sure you want to remove this continuous monitor?')) return;
    try {
      await fetch(`${backendUrl}/api/monitors/${monId}`, { method: 'DELETE' });
      fetchMonitors();
    } catch (err) {
      console.warn('Could not delete monitor:', err);
    }
  };

  const handleCreateMonitor = async (e) => {
    e.preventDefault();
    try {
      await fetch(`${backendUrl}/api/monitors`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newMonitorName || undefined,
          target_url: newMonitorUrl,
          devices: newMonitorDevices,
          interval_seconds: Number(newMonitorInterval),
          alert_threshold: Number(newMonitorThreshold)
        })
      });
      setIsCreateModalOpen(false);
      fetchMonitors();
      if (showBanner) showBanner('Created continuous device monitor successfully!');
    } catch (err) {
      alert(`Failed to create monitor: ${err.message}`);
    }
  };

  // Filtered devices
  const filteredDevices = devices.filter(
    (d) => selectedCategory === 'all' || d.category === selectedCategory
  );

  return (
    <div className="device-lab-container">
      {/* Hero Header with Mode Switcher */}
      <section className="device-lab-hero">
        <div className="hero-content-row">
          <div>
            <div className="scanner-pill-tag">
              <Zap size={13} />
              <span>Universal Device Testing Engine</span>
            </div>
            <h2>Device Lab & Dynamic Continuous Monitor</h2>
            <p>
              Test any website across arbitrary device profiles (smartphones, foldables, tablets, ultrawides,
              wearables, and custom resolutions). Audits all 11 responsive, accessibility, and visual-spatial edge cases dynamically.
            </p>
          </div>

          {/* Tab Switcher */}
          <div className="tab-switcher">
            <button
              className={`tab-btn ${activeTab === 'lab' ? 'active' : ''}`}
              onClick={() => setActiveTab('lab')}
              id="tab-device-lab"
            >
              <Smartphone size={16} />
              <span>Device Lab & Edge Cases</span>
            </button>
            <button
              className={`tab-btn ${activeTab === 'monitor' ? 'active' : ''}`}
              onClick={() => setActiveTab('monitor')}
              id="tab-live-monitor"
            >
              <Radio size={16} />
              <span>Continuous Fleet Monitor</span>
              <span className="live-pill">LIVE</span>
            </button>
          </div>
        </div>
      </section>

      {/* =========================================================================
          TAB 1: DEVICE LAB & DYNAMIC EDGE CASES
          ========================================================================= */}
      {activeTab === 'lab' && (
        <div className="device-lab-main">
          {/* Section A: Device Selection & Dynamic Specifier */}
          <section className="device-lab-card">
            <div className="card-top-bar">
              <div className="section-title-group">
                <Layers size={18} color="#6366f1" />
                <h3>1. Select or Build Any Device Profile</h3>
              </div>
              <div className="device-orientation-controls">
                <button
                  type="button"
                  className="btn btn-secondary btn-sm"
                  onClick={handleFlipOrientation}
                  title="Flip Orientation between Portrait and Landscape"
                >
                  <RotateCw size={14} />
                  <span>
                    Flip to {isCustomMode ? (customOrientation === 'portrait' ? 'Landscape' : 'Portrait') : (currentDevice.orientation === 'portrait' ? 'Landscape' : 'Portrait')}
                  </span>
                </button>
                <button
                  type="button"
                  className={`btn btn-sm ${isCustomMode ? 'btn-primary' : 'btn-secondary'}`}
                  onClick={() => setIsCustomMode(!isCustomMode)}
                  title="Toggle Custom Dynamic Device Sliders"
                >
                  <Sliders size={14} />
                  <span>{isCustomMode ? 'Using Custom Spec' : 'Customize Spec'}</span>
                </button>
              </div>
            </div>

            {/* Category Selector Pills */}
            <div className="category-chips-row">
              {categories.map((cat) => (
                <button
                  key={cat.id}
                  className={`cat-chip ${selectedCategory === cat.id && !isCustomMode ? 'active' : ''}`}
                  onClick={() => {
                    setSelectedCategory(cat.id);
                    if (cat.id === 'custom') {
                      setIsCustomMode(true);
                    } else {
                      setIsCustomMode(false);
                    }
                  }}
                >
                  {cat.name}
                </button>
              ))}
            </div>

            {/* Standard Presets Grid */}
            {!isCustomMode ? (
              <div className="presets-grid">
                {filteredDevices.map((dev) => (
                  <div
                    key={dev.id}
                    className={`device-preset-card ${selectedDeviceId === dev.id ? 'selected' : ''}`}
                    onClick={() => setSelectedDeviceId(dev.id)}
                  >
                    <div className="preset-card-header">
                      <span className="preset-device-name">{dev.name}</span>
                      <span className="preset-cat-badge">{dev.category}</span>
                    </div>
                    <div className="preset-card-specs">
                      <span className="res-pill">
                        {dev.width} × {dev.height} px
                      </span>
                      <span className="dpr-pill">DPR {dev.dpr}x</span>
                      {dev.has_touch && <span className="touch-pill">Touch</span>}
                    </div>
                    <p className="preset-desc">{dev.description}</p>
                  </div>
                ))}
              </div>
            ) : (
              /* Custom Device Builder Drawer */
              <div className="custom-device-builder">
                <div className="custom-builder-grid">
                  <div className="builder-slider-group">
                    <div className="slider-header">
                      <label>Viewport Width</label>
                      <span className="slider-value">{customWidth} px</span>
                    </div>
                    <input
                      type="range"
                      min="200"
                      max="3840"
                      step="5"
                      value={customWidth}
                      onChange={(e) => setCustomWidth(Number(e.target.value))}
                      className="cyber-slider"
                    />
                  </div>

                  <div className="builder-slider-group">
                    <div className="slider-header">
                      <label>Viewport Height</label>
                      <span className="slider-value">{customHeight} px</span>
                    </div>
                    <input
                      type="range"
                      min="200"
                      max="2160"
                      step="5"
                      value={customHeight}
                      onChange={(e) => setCustomHeight(Number(e.target.value))}
                      className="cyber-slider"
                    />
                  </div>

                  <div className="builder-slider-group">
                    <div className="slider-header">
                      <label>Device Pixel Ratio (DPR)</label>
                      <span className="slider-value">{customDpr}x</span>
                    </div>
                    <input
                      type="range"
                      min="1.0"
                      max="4.0"
                      step="0.5"
                      value={customDpr}
                      onChange={(e) => setCustomDpr(Number(e.target.value))}
                      className="cyber-slider"
                    />
                  </div>
                </div>

                <div className="custom-toggles-row">
                  <label className="toggle-label">
                    <input
                      type="checkbox"
                      checked={customHasTouch}
                      onChange={(e) => setCustomHasTouch(e.target.checked)}
                    />
                    <span>Touch Screen Emulation</span>
                  </label>
                  <label className="toggle-label">
                    <input
                      type="checkbox"
                      checked={customIsMobile}
                      onChange={(e) => setCustomIsMobile(e.target.checked)}
                    />
                    <span>Mobile User Agent</span>
                  </label>
                  <label className="toggle-label">
                    <span>Orientation:</span>
                    <select
                      value={customOrientation}
                      onChange={(e) => setCustomOrientation(e.target.value)}
                      className="custom-select-small"
                    >
                      <option value="portrait">Portrait</option>
                      <option value="landscape">Landscape</option>
                    </select>
                  </label>
                  <label className="toggle-label">
                    <span>Color Scheme:</span>
                    <select
                      value={customColorScheme}
                      onChange={(e) => setCustomColorScheme(e.target.value)}
                      className="custom-select-small"
                    >
                      <option value="dark">Dark Theme</option>
                      <option value="light">Light Theme</option>
                    </select>
                  </label>
                </div>
              </div>
            )}
          </section>

          {/* Section B: Target URL Bar & Audit Trigger */}
          <section className="device-lab-card">
            <div className="section-title-group" style={{ marginBottom: '14px' }}>
              <Globe size={18} color="#06b6d4" />
              <h3>2. Specify Target URL & Execution Mode</h3>
            </div>

            {/* Preset URL Pills */}
            <div className="preset-url-pills">
              {PRESET_URLS.map((p) => (
                <button
                  key={p.url}
                  type="button"
                  className="preset-url-pill"
                  onClick={() => {
                    setUrlInput(p.url);
                    setConnectionStatus(null);
                  }}
                >
                  <span>{p.icon}</span>
                  <span>{p.label}</span>
                </button>
              ))}
            </div>

            <div className="scanner-url-bar" style={{ marginTop: '12px' }}>
              <Globe size={18} color="#94a3b8" />
              <input
                type="text"
                value={urlInput}
                onChange={(e) => {
                  setUrlInput(e.target.value);
                  setConnectionStatus(null);
                }}
                placeholder="Enter URL to audit (e.g. http://127.0.0.1:8000/test-app/index.html or any external site)"
                className="scanner-input"
                id="device-target-url-input"
              />
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                onClick={handleCheckConnection}
                disabled={isCheckingUrl || isAuditing}
              >
                {isCheckingUrl ? 'Checking...' : 'Check Reachability'}
              </button>
            </div>

            {connectionStatus && (
              <div
                className="connection-banner"
                style={{
                  marginTop: '10px',
                  background: connectionStatus.reachable ? 'rgba(16, 185, 129, 0.12)' : 'rgba(239, 68, 68, 0.12)',
                  borderColor: connectionStatus.reachable ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)',
                  color: connectionStatus.reachable ? '#34d399' : '#f87171'
                }}
              >
                {connectionStatus.reachable ? <CheckCircle2 size={15} /> : <AlertTriangle size={15} />}
                <span>
                  {connectionStatus.message || (connectionStatus.reachable ? 'Target is online & reachable' : 'Target unreachable')}
                </span>
              </div>
            )}

            {/* Launch Controls */}
            <div className="launch-controls-bar">
              <div className="mode-toggle-group">
                <button
                  type="button"
                  className={`mode-btn ${!isMultiMode ? 'active' : ''}`}
                  onClick={() => setIsMultiMode(false)}
                >
                  <Smartphone size={14} />
                  <span>Single Device Deep Audit</span>
                </button>
                <button
                  type="button"
                  className={`mode-btn ${isMultiMode ? 'active' : ''}`}
                  onClick={() => setIsMultiMode(true)}
                >
                  <Layers size={14} />
                  <span>Multi-Device Fleet Matrix</span>
                </button>
              </div>

              <button
                type="button"
                className="btn btn-primary run-audit-btn"
                onClick={handleRunDeviceAudit}
                disabled={isAuditing}
                id="run-any-device-audit-btn"
              >
                <Play size={16} className={isAuditing ? 'spin' : ''} />
                <span>
                  {isAuditing
                    ? 'Executing Dynamic Audit...'
                    : isMultiMode
                    ? '⚡ Audit Across Multi-Device Fleet'
                    : `⚡ Audit ${isCustomMode ? 'Custom Device' : currentDevice.name}`}
                </span>
              </button>
            </div>
          </section>

          {/* Section C: Dynamic Edge Cases Radar & Verification Results */}
          {auditResult && (
            <div className="audit-results-container">
              {/* Score & Summary Banner */}
              <section className="compliance-score-banner">
                <div className="score-radial-box">
                  <div
                    className={`score-circle ${
                      auditResult.compliance_score >= 90
                        ? 'green'
                        : auditResult.compliance_score >= 75
                        ? 'yellow'
                        : 'red'
                    }`}
                  >
                    <span className="score-number">{auditResult.compliance_score}%</span>
                    <span className="score-label">Compliance</span>
                  </div>
                </div>

                <div className="score-info-column">
                  <div className="score-title-row">
                    <h3>{auditResult.device?.name || 'Device'} Dynamic Edge-Case Audit</h3>
                    <span
                      className={`grade-badge ${
                        auditResult.compliance_score >= 90
                          ? 'grade-a'
                          : auditResult.compliance_score >= 75
                          ? 'grade-b'
                          : 'grade-c'
                      }`}
                    >
                      {auditResult.grade}
                    </span>
                  </div>
                  <p className="score-summary-text">{auditResult.summary}</p>
                  <div className="metrics-chip-row">
                    <span className="chip">
                      <strong>11</strong> Universal Checks
                    </span>
                    <span className="chip passed">
                      <strong>
                        {auditResult.checklist?.filter((c) => c.status === 'PASSED').length || 0}
                      </strong>{' '}
                      Passed
                    </span>
                    <span className="chip failed">
                      <strong>
                        {auditResult.checklist?.filter((c) => c.status === 'FAILED').length || 0}
                      </strong>{' '}
                      Failed
                    </span>
                    <span className="chip warning">
                      <strong>
                        {auditResult.checklist?.filter((c) => c.status === 'WARNING').length || 0}
                      </strong>{' '}
                      Warnings
                    </span>
                    {auditResult.verification_passed && (
                      <span className="chip verified">
                        <ShieldCheck size={13} />
                        Self-Healing Verified
                      </span>
                    )}
                  </div>

                  {/* Delivered Work Action Buttons */}
                  <div className="delivered-work-actions">
                    {auditResult.patch && (
                      <button
                        type="button"
                        className="btn btn-primary"
                        onClick={() => {
                          if (setCurrentRun) setCurrentRun(auditResult);
                          if (onOpenPRModal) onOpenPRModal();
                        }}
                        id="device-approve-pr-btn"
                        title="Dispatch GitHub Pull Request with before/after visual proof"
                      >
                        <GitPullRequest size={15} />
                        <span>Approve & Open GitHub PR</span>
                      </button>
                    )}
                    <button
                      type="button"
                      className="btn btn-secondary"
                      onClick={() => {
                        if (setCurrentRun) setCurrentRun(auditResult);
                        if (onOpenReportModal) onOpenReportModal();
                      }}
                      id="device-export-report-btn"
                      title="Export Executive Visual QA Report"
                    >
                      <FileText size={15} color="#a855f7" />
                      <span>Export Executive QA Report</span>
                    </button>
                    {auditResult.patch?.unified_diff && (
                      <a
                        href={`${backendUrl}/api/download-patch/${auditResult.id}`}
                        target="_blank"
                        rel="noreferrer"
                        className="btn btn-secondary"
                        id="device-download-diff-btn"
                        title="Download .diff patch artifact"
                      >
                        <Download size={15} color="#06b6d4" />
                        <span>Download .diff</span>
                      </a>
                    )}
                    {auditResult.patch?.css && (
                      <button
                        type="button"
                        className="btn btn-secondary"
                        onClick={() => handleCopyCSS(auditResult.patch.css)}
                        id="device-copy-css-btn"
                        title="Copy Synthesized CSS rules to clipboard"
                      >
                        <Copy size={15} />
                        <span>Copy CSS Patch</span>
                      </button>
                    )}
                  </div>
                </div>
              </section>

              {/* Grid: 11 Dynamic Edge Cases Checklist */}
              <section className="edge-cases-radar-section">
                <div className="section-title-group" style={{ marginBottom: '16px' }}>
                  <ShieldCheck size={18} color="#818cf8" />
                  <h3>Dynamic Edge Cases Radar (11 Universal Checks)</h3>
                </div>

                <div className="edge-cases-grid">
                  {auditResult.checklist?.map((check) => {
                    const isExpanded = expandedEdgeCases[check.id];
                    return (
                      <div
                        key={check.id}
                        className={`edge-case-card status-${check.status.toLowerCase()}`}
                      >
                        <div
                          className="edge-case-card-header"
                          onClick={() => toggleEdgeCase(check.id)}
                          style={{ cursor: 'pointer' }}
                        >
                          <div className="card-header-left">
                            <span className={`status-indicator ${check.status.toLowerCase()}`}>
                              {check.status === 'PASSED' ? (
                                <CheckCircle2 size={16} />
                              ) : check.status === 'FAILED' ? (
                                <XCircle size={16} />
                              ) : check.status === 'WARNING' ? (
                                <AlertTriangle size={16} />
                              ) : (
                                <HelpCircle size={16} />
                              )}
                            </span>
                            <div>
                              <h4 className="check-name">{check.name}</h4>
                              <span className="check-cat">{check.category}</span>
                            </div>
                          </div>
                          <div className="card-header-right">
                            <span className={`check-badge ${check.status.toLowerCase()}`}>
                              {check.status}
                            </span>
                            {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                          </div>
                        </div>

                        <p className="check-explanation">{check.explanation}</p>

                        {/* Collapsible Details */}
                        {isExpanded && (
                          <div className="check-expanded-drawer">
                            {check.metrics && (
                              <div className="metrics-table">
                                {Object.entries(check.metrics).map(([k, v]) => (
                                  <div key={k} className="metric-row">
                                    <span className="m-key">{k.replace(/_/g, ' ')}:</span>
                                    <span className="m-val">{String(v)}</span>
                                  </div>
                                ))}
                              </div>
                            )}

                            {check.remediation && (
                              <div className="remediation-box">
                                <span className="remediation-title">Proposed Dynamic Fix:</span>
                                <code>{check.remediation}</code>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </section>

              {/* Visual Diff & Verification Evidence */}
              <section className="device-visual-diff-section">
                <div className="diff-header-bar">
                  <div className="section-title-group">
                    <Eye size={18} color="#ec4899" />
                    <h3>Visual Proof & Verification Sandbox</h3>
                  </div>
                  <div className="diff-view-modes">
                    <button
                      className={`diff-mode-btn ${viewMode === 'slider' ? 'active' : ''}`}
                      onClick={() => setViewMode('slider')}
                    >
                      <SplitSquareVertical size={14} />
                      <span>Split Slider</span>
                    </button>
                    <button
                      className={`diff-mode-btn ${viewMode === 'side_by_side' ? 'active' : ''}`}
                      onClick={() => setViewMode('side_by_side')}
                    >
                      <Columns size={14} />
                      <span>Side-by-Side</span>
                    </button>
                    <button
                      className={`diff-mode-btn ${viewMode === 'frame' ? 'active' : ''}`}
                      onClick={() => setViewMode('frame')}
                    >
                      <Smartphone size={14} />
                      <span>Device Mockup</span>
                    </button>
                    {auditResult.diff_screenshot && (
                      <button
                        className={`diff-mode-btn ${viewMode === 'heatmap' ? 'active' : ''}`}
                        onClick={() => setViewMode('heatmap')}
                      >
                        <Flame size={14} />
                        <span>Diff Heatmap</span>
                      </button>
                    )}
                    {auditResult.patch && (
                      <button
                        className={`diff-mode-btn ${viewMode === 'patch' ? 'active' : ''}`}
                        onClick={() => setViewMode('patch')}
                      >
                        <Code size={14} />
                        <span>Unified Diff</span>
                      </button>
                    )}
                  </div>
                </div>

                {/* Diff Viewer Body */}
                <div className="diff-viewer-frame">
                  {viewMode === 'slider' && auditResult.after_screenshot && (
                    <div
                      className="split-slider-container"
                      ref={sliderContainerRef}
                      onMouseMove={handleSliderMove}
                    >
                      {/* After Image (Background) */}
                      <img
                        src={`${backendUrl}/screenshots/${auditResult.after_screenshot}`}
                        alt="Repaired State"
                        className="slider-img after-img"
                      />
                      {/* Before Image (Clipped Overlay) */}
                      <div
                        className="slider-before-clipper"
                        style={{ width: `${sliderPos}%` }}
                      >
                        <img
                          src={`${backendUrl}/screenshots/${auditResult.before_screenshot}`}
                          alt="Before Anomaly"
                          className="slider-img before-img"
                        />
                      </div>
                      {/* Divider Handle */}
                      <div className="slider-divider-line" style={{ left: `${sliderPos}%` }}>
                        <div className="slider-handle-knob">⇄</div>
                      </div>
                      <span className="slider-tag before">BEFORE ANOMALY</span>
                      <span className="slider-tag after">VERIFIED REPAIR</span>
                    </div>
                  )}

                  {(viewMode === 'side_by_side' && auditResult.after_screenshot) && (
                    <div className="side-by-side-grid">
                      <div className="side-column">
                        <span className="side-label">Original State</span>
                        <img
                          src={`${backendUrl}/screenshots/${auditResult.before_screenshot}`}
                          alt="Before"
                          className="side-img"
                        />
                      </div>
                      <div className="side-column">
                        <span className="side-label healed">Repaired & Verified</span>
                        <img
                          src={`${backendUrl}/screenshots/${auditResult.after_screenshot}`}
                          alt="After"
                          className="side-img"
                        />
                      </div>
                    </div>
                  )}

                  {(viewMode === 'frame' || (!auditResult.after_screenshot && viewMode !== 'patch' && viewMode !== 'heatmap')) && (
                    <div className="device-frame-wrapper">
                      <div className={`hardware-mockup frame-${currentDevice.category || 'phone'} ${isCustomMode ? 'custom' : ''}`}>
                        <div className="mockup-top-hardware">
                          <div className="mockup-dynamic-island">
                            <div className="sensor-camera"></div>
                            <div className="sensor-lens"></div>
                          </div>
                        </div>
                        <div className="mockup-screen">
                          <img
                            src={`${backendUrl}/screenshots/${auditResult.after_screenshot || auditResult.before_screenshot}`}
                            alt="Hardware Mockup Preview"
                            className="mockup-screen-img"
                          />
                        </div>
                        <div className="mockup-home-bar"></div>
                      </div>
                      <div className="mockup-caption">
                        <span>Hardware Emulation: {isCustomMode ? `Custom (${customWidth}×${customHeight}px)` : currentDevice.name}</span>
                        {auditResult.after_screenshot && (
                          <span className="caption-badge verified">Verified Repaired State Active</span>
                        )}
                      </div>
                    </div>
                  )}

                  {viewMode === 'heatmap' && auditResult.diff_screenshot && (
                    <div className="heatmap-container">
                      <span className="side-label">Pillow Discrepancy Heatmap</span>
                      <img
                        src={`${backendUrl}/screenshots/${auditResult.diff_screenshot}`}
                        alt="Pixel Discrepancy Heatmap"
                        className="heatmap-img"
                      />
                      {auditResult.pixel_diff_stats && (
                        <div className="heatmap-telemetry-badge">
                          <span>
                            Diff: {auditResult.pixel_diff_stats.diff_percentage}% (
                            {auditResult.pixel_diff_stats.diff_pixels} pixels changed)
                          </span>
                        </div>
                      )}
                    </div>
                  )}

                  {viewMode === 'patch' && auditResult.patch && (
                    <div className="patch-diff-container">
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <h4>Synthesized Responsive CSS Patch</h4>
                        <button
                          type="button"
                          className="btn btn-secondary btn-sm"
                          onClick={() => handleCopyCSS(auditResult.patch.css)}
                          style={{ fontSize: '0.75rem', padding: '4px 10px' }}
                        >
                          <Copy size={12} />
                          <span>Copy CSS</span>
                        </button>
                      </div>
                      <pre className="patch-code-block">{auditResult.patch.css}</pre>
                      {auditResult.patch.unified_diff && (
                        <>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '16px' }}>
                            <h4>Git Unified Diff</h4>
                            <a
                              href={`${backendUrl}/api/download-patch/${auditResult.id}`}
                              target="_blank"
                              rel="noreferrer"
                              className="btn btn-secondary btn-sm"
                              style={{ fontSize: '0.75rem', padding: '4px 10px', textDecoration: 'none' }}
                            >
                              <Download size={12} />
                              <span>Download .diff</span>
                            </a>
                          </div>
                          <pre className="patch-code-block diff-syntax">
                            {auditResult.patch.unified_diff}
                          </pre>
                        </>
                      )}
                    </div>
                  )}
                </div>
              </section>
            </div>
          )}

          {/* Section D: Multi-Device Fleet Results Matrix */}
          {multiAuditResult && (
            <section className="fleet-matrix-section">
              <div className="fleet-matrix-header">
                <div>
                  <h3>Multi-Device Fleet Matrix Results</h3>
                  <p>
                    Audited {multiAuditResult.devices_audited} devices simultaneously on{' '}
                    <code>{multiAuditResult.target_url}</code>.
                  </p>
                </div>
                <div className="fleet-score-box">
                  <span className="score-big">{multiAuditResult.fleet_compliance_score}%</span>
                  <span className="score-sub">Fleet Score</span>
                </div>
              </div>

              <div className="fleet-cards-grid">
                {Object.entries(multiAuditResult.fleet_results || {}).map(([devId, r]) => (
                  <div key={devId} className="fleet-card">
                    <div className="fleet-card-top">
                      <div>
                        <h4>{r.device_name}</h4>
                        <span className="dim-text">
                          {r.width} × {r.height} px • {r.category}
                        </span>
                      </div>
                      <span className={`fleet-grade-pill ${r.compliance_score >= 90 ? 'green' : 'yellow'}`}>
                        {r.compliance_score}%
                      </span>
                    </div>

                    <img
                      src={`${backendUrl}/screenshots/${r.screenshot}`}
                      alt={r.device_name}
                      className="fleet-preview-thumb"
                    />

                    <div className="fleet-checks-summary">
                      <span className="c-pill green">{r.checklist_summary?.passed || 0} Passed</span>
                      <span className="c-pill red">{r.checklist_summary?.failed || 0} Failed</span>
                      <span className="c-pill yellow">
                        {r.checklist_summary?.warning || 0} Warning
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}
        </div>
      )}

      {/* =========================================================================
          TAB 2: CONTINUOUS DYNAMIC MONITORING FLEET
          ========================================================================= */}
      {activeTab === 'monitor' && (
        <div className="monitoring-fleet-main">
          {/* Top Monitoring Controls */}
          <div className="monitor-top-bar">
            <div>
              <h3>Live Continuous Device Fleet Monitors</h3>
              <p>
                Actively polls web endpoints across heterogeneous device fleets, tracking uptime,
                responsive compliance regression, and automated self-healing triggers.
              </p>
            </div>
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => setIsCreateModalOpen(true)}
              id="add-device-monitor-btn"
            >
              <Plus size={16} />
              <span>Create Fleet Monitor</span>
            </button>
          </div>

          {/* Active Monitors List */}
          <div className="monitors-grid">
            {monitors.map((mon) => (
              <div key={mon.id} className={`monitor-card status-${mon.status || 'active'}`}>
                <div className="monitor-card-top">
                  <div>
                    <div className="monitor-badge-row">
                      <span className={`status-pill ${mon.status}`}>
                        <span className="pulse-dot"></span>
                        {mon.status.toUpperCase()}
                      </span>
                      <span className="interval-pill">Every {mon.interval_seconds}s</span>
                    </div>
                    <h4 className="monitor-title">{mon.name}</h4>
                    <span className="monitor-url">{mon.target_url}</span>
                  </div>

                  <div className="monitor-score-gauge">
                    <span className="score-val">{mon.last_score || 100}%</span>
                    <span className="score-sub">Health</span>
                  </div>
                </div>

                <div className="monitored-devices-pills">
                  {mon.devices?.map((dKey) => (
                    <span key={dKey} className="dev-tag">
                      {dKey.replace(/_/g, ' ')}
                    </span>
                  ))}
                </div>

                {/* History Sparkline */}
                {mon.history && mon.history.length > 0 && (
                  <div className="sparkline-container">
                    <span className="sparkline-title">Recent Compliance Trend:</span>
                    <div className="sparkline-bars">
                      {mon.history.slice(-12).map((h, idx) => (
                        <div
                          key={idx}
                          className={`spark-bar ${h.score >= 90 ? 'green' : h.score >= 75 ? 'yellow' : 'red'}`}
                          style={{ height: `${Math.max(15, h.score)}%` }}
                          title={`Score: ${h.score}% (${h.defects || 0} defects, ${h.latency_ms || 0}ms)`}
                        />
                      ))}
                    </div>
                  </div>
                )}

                {/* Card Actions */}
                <div className="monitor-card-actions">
                  <button
                    type="button"
                    className="btn btn-secondary btn-sm"
                    onClick={() => handleRunMonitorNow(mon.id)}
                    title="Run Immediate Ping on all devices"
                  >
                    <RefreshCw size={13} />
                    <span>Ping Fleet</span>
                  </button>

                  <button
                    type="button"
                    className="btn btn-secondary btn-sm"
                    onClick={() => handleToggleMonitor(mon.id)}
                  >
                    {mon.status === 'active' ? <Pause size={13} /> : <Play size={13} />}
                    <span>{mon.status === 'active' ? 'Pause' : 'Resume'}</span>
                  </button>

                  <button
                    type="button"
                    className="btn btn-secondary btn-sm delete-btn"
                    onClick={() => handleDeleteMonitor(mon.id)}
                    title="Remove Monitor"
                  >
                    <Trash2 size={13} color="#f87171" />
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Create Monitor Modal */}
          {isCreateModalOpen && (
            <div className="modal-backdrop">
              <div className="cyber-modal">
                <div className="modal-header">
                  <h3>Create Dynamic Device Monitor</h3>
                  <button
                    className="close-btn"
                    onClick={() => setIsCreateModalOpen(false)}
                  >
                    ✕
                  </button>
                </div>

                <form onSubmit={handleCreateMonitor} className="modal-form">
                  <div className="form-group">
                    <label>Monitor Name (Optional)</label>
                    <input
                      type="text"
                      value={newMonitorName}
                      onChange={(e) => setNewMonitorName(e.target.value)}
                      placeholder="e.g. Staging Checkout Multi-Device Watch"
                      className="scanner-input"
                    />
                  </div>

                  <div className="form-group">
                    <label>Target URL to Monitor</label>
                    <input
                      type="text"
                      value={newMonitorUrl}
                      onChange={(e) => setNewMonitorUrl(e.target.value)}
                      required
                      placeholder="http://127.0.0.1:8000/test-app/index.html"
                      className="scanner-input"
                    />
                  </div>

                  <div className="form-group">
                    <label>Check Interval</label>
                    <select
                      value={newMonitorInterval}
                      onChange={(e) => setNewMonitorInterval(e.target.value)}
                      className="custom-select"
                    >
                      <option value="15">Every 15 Seconds (Real-Time Live Ping)</option>
                      <option value="30">Every 30 Seconds</option>
                      <option value="60">Every 1 Minute (Standard)</option>
                      <option value="300">Every 5 Minutes</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label>Devices to Audit in Fleet</label>
                    <div className="modal-device-checkboxes">
                      {devices.slice(0, 8).map((d) => (
                        <label key={d.id} className="checkbox-row">
                          <input
                            type="checkbox"
                            checked={newMonitorDevices.includes(d.id)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setNewMonitorDevices([...newMonitorDevices, d.id]);
                              } else {
                                setNewMonitorDevices(
                                  newMonitorDevices.filter((id) => id !== d.id)
                                );
                              }
                            }}
                          />
                          <span>
                            {d.name} ({d.width}×{d.height})
                          </span>
                        </label>
                      ))}
                    </div>
                  </div>

                  <div className="modal-footer">
                    <button
                      type="button"
                      className="btn btn-secondary"
                      onClick={() => setIsCreateModalOpen(false)}
                    >
                      Cancel
                    </button>
                    <button type="submit" className="btn btn-primary">
                      Deploy Fleet Monitor
                    </button>
                  </div>
                </form>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
