'use client';

import { Check, FileText, Maximize2, Minus, Plus, Sparkles, Target, Lightbulb } from 'lucide-react';
import { useRef, useState, type KeyboardEvent } from 'react';

type ResultTab = 'feedback' | 'text' | 'scheme';

const marks = [
  { label: 'Q1 (a)', score: '8 / 10', percentage: 80 },
  { label: 'Q1 (b)', score: '7 / 10', percentage: 70 },
  { label: 'Q2 (a)', score: '9 / 10', percentage: 90 },
  { label: 'Q2 (b)', score: '6 / 10', percentage: 60, warning: true },
  { label: 'Q3', score: '8 / 10', percentage: 80 },
  { label: 'Q4 (a)', score: '9 / 10', percentage: 90 },
  { label: 'Q4 (b)', score: '8 / 10', percentage: 80 },
  { label: 'Q5 (a)', score: '9 / 10', percentage: 90 },
  { label: 'Q5 (b)', score: '9 / 10', percentage: 90 },
  { label: 'Q6', score: '9 / 10', percentage: 90 },
];

const feedback = [
  { title: 'Strengths', icon: Check, className: 'feedback-strength', items: ['Clear and structured explanation', 'Correct definition of data structures', 'Good examples provided', 'Accurate explanation of time complexity'] },
  { title: 'Areas for Improvement', icon: Target, className: 'feedback-improve', items: ['Could include more examples', 'Missing edge cases in analysis', 'Explanation can be more concise'] },
  { title: 'Suggestions', icon: Lightbulb, className: 'feedback-suggest', items: ['Add diagrams where applicable', 'Use key technical terms', 'Improve handwriting clarity'] },
];

export default function EvaluationResultPreview() {
  const [activeTab, setActiveTab] = useState<ResultTab>('feedback');
  const [expanded, setExpanded] = useState(false);
  const [zoom, setZoom] = useState(100);
  const [showAllMarks, setShowAllMarks] = useState(false);
  const tabRefs = useRef<Record<ResultTab, HTMLButtonElement | null>>({ feedback: null, text: null, scheme: null });

  const selectTab = (tab: ResultTab) => {
    setActiveTab(tab);
    tabRefs.current[tab]?.focus();
  };

  const handleTabKeyDown = (event: KeyboardEvent<HTMLButtonElement>, currentTab: ResultTab) => {
    const tabOrder: ResultTab[] = ['feedback', 'text', 'scheme'];
    const currentIndex = tabOrder.indexOf(currentTab);
    let nextIndex = currentIndex;

    if (event.key === 'ArrowRight') nextIndex = (currentIndex + 1) % tabOrder.length;
    if (event.key === 'ArrowLeft') nextIndex = (currentIndex - 1 + tabOrder.length) % tabOrder.length;
    if (event.key === 'Home') nextIndex = 0;
    if (event.key === 'End') nextIndex = tabOrder.length - 1;

    if (!['ArrowRight', 'ArrowLeft', 'Home', 'End'].includes(event.key)) return;

    event.preventDefault();
    if (nextIndex !== currentIndex) selectTab(tabOrder[nextIndex]);
  };

  const displayedMarks = showAllMarks ? marks : marks.slice(0, 5);

  return (
    <section className="surface-card result-card" aria-labelledby="result-title">
      <div className="card-heading">
        <div>
          <h2 id="result-title">Evaluation Result</h2>
          <span className="demo-label">Demo preview</span>
        </div>
        <span className="result-status"><Check size={13} aria-hidden="true" /> Completed in 12 seconds</span>
      </div>

      <div className="result-top">
        <div className={`document-preview${expanded ? ' document-preview-expanded' : ''}`}>
          <div className="document-page" role="img" aria-label="Demo preview: illustrative sample handwritten answer content.">
            <div className="document-handwriting" style={{ transform: `scale(${zoom / 100})`, transformOrigin: 'top left' }}>
              <p className="document-sample-note">DEMO SAMPLE — illustrative answer</p>
              <p>Q1 (a)</p>
              <p>Data structures organize and store data so it can be accessed and modified efficiently.</p>
              <p>Examples include arrays, linked lists, stacks, queues, and trees.</p>
              <p>(b) Time complexity helps us analyse the efficiency of an algorithm.</p>
            </div>
          </div>
          <div className="document-toolbar" role="group" aria-label="Document preview controls">
            <button type="button" aria-label="Zoom out" onClick={() => setZoom((value) => Math.max(80, value - 10))} disabled={zoom === 80}><Minus size={14} aria-hidden="true" /></button>
            <button type="button" aria-label="Reset zoom to 100 percent" onClick={() => setZoom(100)}>{zoom}%</button>
            <button type="button" aria-label="Zoom in" onClick={() => setZoom((value) => Math.min(150, value + 10))} disabled={zoom === 150}><Plus size={14} aria-hidden="true" /></button>
            <button type="button" aria-label={expanded ? 'Collapse preview' : 'Expand preview'} aria-pressed={expanded} onClick={() => setExpanded((value) => !value)}><Maximize2 size={14} aria-hidden="true" /></button>
          </div>
        </div>
        <div className="score-summary">
          <div className="score-overview">
            <div>
              <div className="score-number">82<span>/100</span></div>
              <div className="score-label">Overall Score</div>
            </div>
            <div className="score-ring" role="img" aria-label="82 percent overall score"><span aria-hidden="true">82%</span></div>
          </div>
        </div>
      </div>

      <div className="section-marks">
        <h3 className="section-heading">Section-wise Marks</h3>
        <p className="section-marks-summary">Showing {displayedMarks.length} of {marks.length} questions in this demo preview.</p>
        {displayedMarks.map((mark) => (
          <div className={`mark-row${mark.warning ? ' mark-row-warning' : ''}`} key={mark.label}>
            <span>{mark.label}</span>
            <div className="mark-bar" aria-hidden="true"><span style={{ width: `${mark.percentage}%` }} /></div>
            <span className="mark-score">{mark.score}</span>
          </div>
        ))}
        <button className="section-marks-disclosure" type="button" aria-expanded={showAllMarks} onClick={() => setShowAllMarks((value) => !value)}>
          {showAllMarks ? 'Show fewer questions' : 'Show all 10 questions'}
        </button>
      </div>

      <div className="result-tabs" role="tablist" aria-label="Evaluation detail tabs">
        <button id="feedback-tab" ref={(element) => { tabRefs.current.feedback = element; }} className={`result-tab${activeTab === 'feedback' ? ' result-tab-active' : ''}`} type="button" role="tab" aria-selected={activeTab === 'feedback'} aria-controls="feedback-panel" tabIndex={activeTab === 'feedback' ? 0 : -1} onClick={() => selectTab('feedback')} onKeyDown={(event) => handleTabKeyDown(event, 'feedback')}><Sparkles size={14} aria-hidden="true" /> AI Feedback</button>
        <button id="text-tab" ref={(element) => { tabRefs.current.text = element; }} className={`result-tab${activeTab === 'text' ? ' result-tab-active' : ''}`} type="button" role="tab" aria-selected={activeTab === 'text'} aria-controls="text-panel" tabIndex={activeTab === 'text' ? 0 : -1} onClick={() => selectTab('text')} onKeyDown={(event) => handleTabKeyDown(event, 'text')}><FileText size={14} aria-hidden="true" /> Extracted Text</button>
        <button id="scheme-tab" ref={(element) => { tabRefs.current.scheme = element; }} className={`result-tab${activeTab === 'scheme' ? ' result-tab-active' : ''}`} type="button" role="tab" aria-selected={activeTab === 'scheme'} aria-controls="scheme-panel" tabIndex={activeTab === 'scheme' ? 0 : -1} onClick={() => selectTab('scheme')} onKeyDown={(event) => handleTabKeyDown(event, 'scheme')}><Target size={14} aria-hidden="true" /> Demo Marking Scheme</button>
      </div>

      <div className="result-panel">
        <div id="feedback-panel" role="tabpanel" aria-labelledby="feedback-tab" hidden={activeTab !== 'feedback'}>
          <div className="feedback-grid">
            {feedback.map(({ title, icon: Icon, className, items }) => (
              <article className={`feedback-card ${className}`} key={title}>
                <div className="feedback-card-header"><span className="feedback-icon"><Icon size={14} aria-hidden="true" /></span>{title}</div>
                <ul className="feedback-list">{items.map((item) => <li key={item}>{item}</li>)}</ul>
              </article>
            ))}
          </div>
        </div>
        <div id="text-panel" className="result-empty-panel" role="tabpanel" aria-labelledby="text-tab" hidden={activeTab !== 'text'}>
          <strong>Extracted response</strong><br />Data structures are a way of organizing and storing data so that it can be accessed and modified efficiently. Examples include arrays, linked lists, stacks, queues, and trees.
        </div>
        <div id="scheme-panel" className="result-empty-panel" role="tabpanel" aria-labelledby="scheme-tab" hidden={activeTab !== 'scheme'}>
          <strong>Demo marking scheme</strong><br />This sample scheme illustrates how each criterion can be scored against the demo response. It is illustrative only and does not save or persist edits.
        </div>
      </div>
    </section>
  );
}
