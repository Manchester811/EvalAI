import Link from 'next/link';
import { ArrowUpRight, CheckCircle2, Clock3, Eye } from 'lucide-react';

const rows = [
  { id: 101, student: 'Aarav Sharma', subject: 'Data Structures', exam: 'Mid Term', date: 'Oct 09, 2026', score: '78/100', status: 'Completed', initials: 'AS', tone: 'blue' },
  { id: 102, student: 'Diya Patel', subject: 'Database Systems', exam: 'CAT 1', date: 'Oct 09, 2026', score: '92/100', status: 'Completed', initials: 'DP', tone: 'pink' },
  { id: 103, student: 'Rohan Mehta', subject: 'Operating Systems', exam: 'Mid Term', date: 'Oct 08, 2026', score: '65/100', status: 'Pending Review', initials: 'RM', tone: 'amber' },
  { id: 104, student: 'Ishita Verma', subject: 'Computer Networks', exam: 'Quiz 2', date: 'Oct 08, 2026', score: '88/100', status: 'Completed', initials: 'IV', tone: 'violet' },
  { id: 105, student: 'Karan Singh', subject: 'Machine Learning', exam: 'Assignment', date: 'Oct 07, 2026', score: '71/100', status: 'Completed', initials: 'KS', tone: 'green' },
];

export default function RecentEvaluationsTable() {
  return (
    <section className="surface-card recent-card" aria-labelledby="recent-evaluations-title">
      <div className="card-heading">
        <div>
          <h2 id="recent-evaluations-title">Recent Evaluations</h2>
        </div>
        <Link className="text-link" href="/results">View all <ArrowUpRight size={14} aria-hidden="true" /></Link>
      </div>
      <div className="table-scroll">
        <table className="evaluations-table">
          <caption className="sr-only">Recent evaluations by student, subject, exam, score, and review status</caption>
          <thead>
            <tr>
              <th scope="col">Student</th>
              <th scope="col">Subject</th>
              <th scope="col">Exam</th>
              <th scope="col">Date</th>
              <th scope="col">Score</th>
              <th scope="col">Status</th>
              <th scope="col"><span className="sr-only">Actions</span></th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => {
              const isPending = row.status === 'Pending Review';
              return (
                <tr key={row.id}>
                  <td className="student-cell"><span className={`student-avatar student-avatar-${row.tone}`} aria-hidden="true">{row.initials}</span>{row.student}</td>
                  <td>{row.subject}</td>
                  <td>{row.exam}</td>
                  <td>{row.date}</td>
                  <td className="score-cell">{row.score}</td>
                  <td><span className={`status-badge ${isPending ? 'status-pending' : 'status-completed'}`}>{isPending ? <Clock3 size={11} aria-hidden="true" /> : <CheckCircle2 size={11} aria-hidden="true" />}{row.status}</span></td>
                  <td><Link className="table-action" href={`/evaluations/${row.id}`} aria-label={`View evaluation for ${row.student}`}><Eye size={17} aria-hidden="true" /></Link></td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}
