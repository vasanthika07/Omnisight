import React from 'react';
import ControlBar from './ControlBar';
import VisualDiffInspector from './VisualDiffInspector';
import AgentTimeline from './AgentTimeline';
import DefectCard from './DefectCard';
import PatchViewer from './PatchViewer';

export default function StagingView({
  viewport,
  setViewport,
  targetUrl,
  setTargetUrl,
  isRunning,
  onTriggerAudit,
  onResetBug,
  onInjectChaosBug,
  onResetClean,
  selectedEngine,
  setSelectedEngine,
  currentRun,
  backendUrl,
  onOpenPRModal
}) {
  return (
    <>
      <ControlBar 
        viewport={viewport}
        setViewport={setViewport}
        targetUrl={targetUrl}
        setTargetUrl={setTargetUrl}
        isRunning={isRunning}
        onTriggerAudit={onTriggerAudit}
        onResetBug={onResetBug}
        onInjectChaosBug={onInjectChaosBug}
        onResetClean={onResetClean}
        selectedEngine={selectedEngine}
        setSelectedEngine={setSelectedEngine}
      />

      <div className="dashboard-grid">
        {/* Left Column: Visual Diff Inspector & Unified Diff */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <VisualDiffInspector 
            runData={currentRun} 
            backendUrl={backendUrl} 
          />

          <PatchViewer 
            patch={currentRun?.patch} 
            prNumber={currentRun?.pr_number}
            prUrl={currentRun?.pr_url}
            runId={currentRun?.id}
            targetUrl={targetUrl || currentRun?.target_url}
            backendUrl={backendUrl}
            onOpenPRModal={onOpenPRModal}
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
            confidenceScore={currentRun?.confidence_score ?? currentRun?.timeline?.find(t => t.step === 'defect_detection')?.details?.confidence}
            croppedArtifact={currentRun?.cropped_defect_token_artifact || currentRun?.crop_screenshot}
            engineUsed={currentRun?.engine_used}
            tokenTelemetry={currentRun?.token_telemetry}
          />
        </div>
      </div>
    </>
  );
}
