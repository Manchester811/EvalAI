import { BrainCircuit, Download, MessageSquareText, ScanText } from 'lucide-react';

const features = [
  { label: 'Handwriting Recognition', icon: ScanText },
  { label: 'AI-Powered Evaluation', icon: BrainCircuit },
  { label: 'Detailed Feedback', icon: MessageSquareText },
  { label: 'Export Results', icon: Download },
];

export default function DashboardHero() {
  return (
    <section className="hero" aria-labelledby="dashboard-title">
      <div className="hero-copy">
        <h1 id="dashboard-title">Evaluate Answer Sheets <span className="gradient-text">with AI</span></h1>
        <p className="hero-description">Upload answer sheets, get accurate, consistent, and unbiased evaluation with detailed feedback in seconds.</p>
      </div>
      <div className="hero-visual" role="group" aria-label="EvalAI capabilities">
        <div className="notebook" role="img" aria-label="Handwritten answer sheet preview">
          <span className="notebook-corner" aria-hidden="true" />
        </div>
        <div className="feature-list">
          {features.map(({ label, icon: Icon }) => (
            <div className="feature-item" key={label}>
              <Icon size={15} aria-hidden="true" />
              <span>{label}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
