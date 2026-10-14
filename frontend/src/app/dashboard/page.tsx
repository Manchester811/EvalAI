import DashboardHero from '@/components/dashboard/DashboardHero';
import EvaluationResultPreview from '@/components/dashboard/EvaluationResultPreview';
import RecentEvaluationsTable from '@/components/dashboard/RecentEvaluationsTable';
import UploadPanel from '@/components/dashboard/UploadPanel';
import { ClipboardCheck, Clock3, Gauge, TrendingUp } from 'lucide-react';

const metrics = [
  { label: 'Total Evaluations', value: '248', detail: 'All exams', icon: ClipboardCheck, tone: 'blue' },
  { label: 'Pending Review', value: '12', detail: 'Awaiting approval', icon: Clock3, tone: 'amber' },
  { label: 'Average Score', value: '78.6%', detail: 'Across subjects', icon: Gauge, tone: 'violet' },
  { label: 'Completed This Week', value: '36', detail: 'Last 7 days', icon: TrendingUp, tone: 'green' },
];

export default function DashboardPage() {
  return (
    <div>
      <DashboardHero />
      <section className="metrics-grid" aria-label="Evaluation summary">
        {metrics.map(({ label, value, detail, icon: Icon, tone }) => (
          <article className="metric-card" key={label}>
            <div className={`metric-icon metric-icon-${tone}`}><Icon size={16} aria-hidden="true" /></div>
            <div className="metric-copy">
              <span className="metric-label">{label}</span>
              <strong className="metric-value">{value}</strong>
              <span className="metric-detail">{detail}</span>
            </div>
          </article>
        ))}
      </section>
      <div className="dashboard-grid">
        <div className="dashboard-left">
          <UploadPanel />
          <RecentEvaluationsTable />
        </div>
        <EvaluationResultPreview />
      </div>
    </div>
  );
}
