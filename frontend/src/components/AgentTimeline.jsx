import React from 'react';
import { Activity, CheckCircle2, AlertCircle, Clock, ArrowRight } from 'lucide-react';

export default function AgentTimeline({ timeline = [], isRunning }) {
  if (!timeline || timeline.length === 0) {
    return (
      <div className="dash-card">
        <div className="dash-card-header">
          <div className="card-title-group">
            <Activity size={18} color="#06b6d4" />
            <h2>Agentic Orchestrator (Plan → Execute → Evaluate)</h2>
          </div>
        </div>
        <div className="empty-state" style={{ padding: '24px 12px' }}>
          <Clock size={32} />
          <p>Agent loop idle. Trigger an audit to view live execution steps.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dash-card">
      <div className="dash-card-header">
        <div className="card-title-group">
          <Activity size={18} color="#06b6d4" />
          <h2>Agentic Orchestrator (Plan → Execute → Evaluate)</h2>
        </div>
        <span style={{ fontSize: '0.78rem', color: '#94a3b8' }}>
          {timeline.length} Step{timeline.length === 1 ? '' : 's'}
        </span>
      </div>

      <div className="timeline-list">
        {timeline.map((step, idx) => {
          const isSuccess = step.status === 'success' || step.status === 'completed';
          const isWarn = step.status === 'warning';
          
          return (
            <div 
              key={idx} 
              className={`timeline-item ${isSuccess ? 'success' : ''} ${isRunning && idx === timeline.length - 1 ? 'active' : ''}`}
            >
              <div className="timeline-icon">
                {isSuccess ? (
                  <CheckCircle2 size={16} color="#10b981" />
                ) : isWarn ? (
                  <AlertCircle size={16} color="#f59e0b" />
                ) : (
                  <Activity size={16} color="#818cf8" />
                )}
              </div>
              <div className="timeline-content">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span className="timeline-step-title">{step.step.replace('_', ' ')}</span>
                  <span style={{ fontSize: '0.7rem', color: '#64748b' }}>
                    Step {idx + 1}
                  </span>
                </div>
                <p className="timeline-step-msg">{step.message}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
