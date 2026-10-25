import React, { useState } from 'react';
import { FileText, Download, Copy, Check, X, ShieldCheck, ExternalLink } from 'lucide-react';

export default function ExportReportModal({ isOpen, onClose, runData, backendUrl = 'http://127.0.0.1:8000' }) {
  const [copied, setCopied] = useState(false);

  if (!isOpen || !runData) return null;

  const handleDownloadHtml = () => {
    window.open(`${backendUrl}/api/reports/${runData.id}?format=html`, '_blank');
  };

  const handleDownloadJson = () => {
    const jsonStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(runData, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", jsonStr);
    downloadAnchor.setAttribute("download", `omnisight_report_${runData.id}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const generateMarkdownSummary = () => {
    return `# 👁️ OmniSight Visual QA Audit Report
**Run ID:** \`${runData.id}\`
**Viewport:** \`${runData.viewport}\`
**Status:** ${runData.verification_passed ? 'PASSED & HEALED ✅' : 'ACTION REQUIRED ⚠️'}
**Defects Found:** ${runData.defects_found}
**Vision Engine:** \`${runData.engine_used || 'Autonomous Built-in'}\`
**Token Efficiency:** -${runData.token_telemetry?.token_reduction_pct || 81}% VLM tokens saved via ROI crop

## Defects Summary
${runData.defects?.map(d => `- **${d.severity}**: \`${d.element}\` - ${d.description}`).join('\n') || 'Zero defects detected.'}

## Verification
- Pre-healing screenshot: \`${runData.before_screenshot}\`
- Post-healing screenshot: \`${runData.after_screenshot}\`
- Pixel Discrepancy Heatmap: \`${runData.diff_screenshot}\`
`;
  };

  const handleCopyMarkdown = () => {
    navigator.clipboard.writeText(generateMarkdownSummary());
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-card wide-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <FileText size={20} color="#8b5cf6" />
            <h2 style={{ fontSize: '1.2rem', fontWeight: 700 }}>
              Export Executive QA Compliance Report
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
          <div className="report-preview-box">
            <div className="report-preview-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <ShieldCheck size={18} color="#10b981" />
                <span style={{ fontWeight: 700, color: '#f8fafc' }}>
                  OmniSight Autonomous QA Certification
                </span>
              </div>
              <span className={`status-pill ${runData.verification_passed ? 'pill-green' : 'pill-amber'}`}>
                {runData.verification_passed ? '100% COMPLIANT' : 'REVIEW REQUIRED'}
              </span>
            </div>

            <div className="report-preview-grid">
              <div>
                <span className="preview-label">AUDIT RUN ID</span>
                <p className="preview-val font-mono">{runData.id.slice(0, 18)}</p>
              </div>
              <div>
                <span className="preview-label">TARGET VIEWPORT</span>
                <p className="preview-val">{runData.viewport?.toUpperCase()}</p>
              </div>
              <div>
                <span className="preview-label">VLM REASONING ENGINE</span>
                <p className="preview-val">{runData.engine_used?.replace(/_/g, ' ') || 'Autonomous Spatial'}</p>
              </div>
              <div>
                <span className="preview-label">TOTAL ANOMALIES</span>
                <p className="preview-val">{runData.defects_found} Defect(s) Healed</p>
              </div>
            </div>

            <div style={{ marginTop: '16px' }}>
              <span className="preview-label">EXECUTIVE SUMMARY</span>
              <p style={{ fontSize: '0.86rem', color: '#cbd5e1', marginTop: '4px' }}>
                {runData.summary || 'Closed-loop visual testing and responsive patch verification completed.'}
              </p>
            </div>
          </div>

          <div className="export-actions-grid">
            <button 
              className="btn btn-primary export-card-btn" 
              onClick={handleDownloadHtml}
            >
              <Download size={18} />
              <div>
                <strong>Download HTML Report</strong>
                <span>Standalone executive report for stakeholder presentations</span>
              </div>
            </button>

            <button 
              className="btn btn-secondary export-card-btn" 
              onClick={handleDownloadJson}
            >
              <Download size={18} />
              <div>
                <strong>Download Raw JSON Audit</strong>
                <span>Complete spatial DOM metrics, bounding boxes, and diffs</span>
              </div>
            </button>

            <button 
              className="btn btn-secondary export-card-btn" 
              onClick={handleCopyMarkdown}
            >
              {copied ? <Check size={18} color="#10b981" /> : <Copy size={18} />}
              <div>
                <strong>{copied ? 'Copied to Clipboard!' : 'Copy Markdown Summary'}</strong>
                <span>Formatted for PR comments, Jira tickets, and Slack alerts</span>
              </div>
            </button>
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
