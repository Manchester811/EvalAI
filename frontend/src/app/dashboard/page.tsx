import DashboardHero from '@/components/dashboard/DashboardHero';
import EvaluationResultPreview from '@/components/dashboard/EvaluationResultPreview';
import RecentEvaluationsTable from '@/components/dashboard/RecentEvaluationsTable';
import UploadPanel from '@/components/dashboard/UploadPanel';
import { useEffect, useState } from 'react';
import { ClipboardCheck, Clock3, Gauge, TrendingUp } from 'lucide-react';

export default function DashboardPage() {
  const [analytics, setAnalytics] = useState<any>(null);
  const [analyticsError, setAnalyticsError] = useState("");

  useEffect(() => {
    const base = process.env.NEXT_PUBLIC_API_URL;
    fetch(`${base}/api/v1/analytics/overview`)
      .then((r) => (r.ok ? r.json() : Promise.reject(`Analytics ${r.status}`)))
      .then(setAnalytics)
      .catch((e) => setAnalyticsError(e.message ?? String(e)));
  }, []);

  const metrics = [
    { label: 'Total Evaluations', value: analytics?.summary_cards?.total_evaluations?.toString() ?? '—', detail: 'From backend', icon: ClipboardCheck, tone: 'blue' },
    { label: 'Pending Review', value: analytics?.summary_cards?.pending_reviews?.toString() ?? '—', detail: 'Needs review', icon: Clock3, tone: 'amber' },
    { label: 'Average Score', value: analytics?.summary_cards?.avg_score != null ? `${analytics.summary_cards.avg_score}%` : '—', detail: 'Across subjects', icon: Gauge, tone: 'violet' },
    { label: 'Completed This Week', value: analytics?.summary_cards?.completions_week?.toString() ?? '—', detail: 'Last 7 days', icon: TrendingUp, tone: 'green' },
  ];

  if (analyticsError) {
    return (
      <div>
        <DashboardHero />
        <p role="alert" style={{ color: '#E5484D', padding: 12, background: '#FFF0F0', borderRadius: 8 }}>Analytics: {analyticsError} (check backend is running at {process.env.NEXT_PUBLIC_API_URL}). Demo fixtures removed per requirement.</p>
      </div>
    );
  }

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
