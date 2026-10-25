import React from 'react';
import { ShieldCheck, Zap, Sparkles, Activity, Layers } from 'lucide-react';

export default function MetricsBar({ analytics, stagingStatus = 'Compliant' }) {
  const total = analytics?.total_audits ?? 0;
  const rate = analytics?.healing_success_rate ?? 100;
  const tokensSaved = analytics?.estimated_tokens_saved ?? 0;
  const tokenPct = analytics?.avg_token_reduction_pct ?? 81.3;
  const avgSpeed = analytics?.avg_healing_duration_sec ?? 1.8;

  return (
    <div className="metrics-bar">
      <div className="metric-chip">
        <Activity size={15} color="#818cf8" />
        <span className="metric-label">Audits Executed:</span>
        <strong className="metric-value">{total}</strong>
      </div>

      <div className="metric-chip">
        <ShieldCheck size={15} color="#10b981" />
        <span className="metric-label">Healing Success:</span>
        <strong className="metric-value text-success">{rate}%</strong>
      </div>

      <div className="metric-chip">
        <Zap size={15} color="#f59e0b" />
        <span className="metric-label">Avg Resolution:</span>
        <strong className="metric-value">{avgSpeed}s</strong>
      </div>

      <div className="metric-chip">
        <Sparkles size={15} color="#c084fc" />
        <span className="metric-label">Token Efficiency:</span>
        <strong className="metric-value text-purple">-{tokenPct}% ({tokensSaved.toLocaleString()} tk)</strong>
      </div>

      <div className="metric-chip status-chip">
        <Layers size={14} color="#06b6d4" />
        <span className="metric-label">Staging Health:</span>
        <span className={`status-pill ${stagingStatus.toLowerCase().includes('clean') || stagingStatus.toLowerCase().includes('compliant') ? 'pill-green' : 'pill-amber'}`}>
          {stagingStatus}
        </span>
      </div>
    </div>
  );
}
