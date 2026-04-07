const labels = [
  { key: 'total', title: 'Total Emails' },
  { key: 'open', title: 'Open Queue' },
  { key: 'resolved', title: 'Resolved' },
  { key: 'critical', title: 'Critical Pending' },
  { key: 'avgUrgency', title: 'Avg Urgency' }
];

export default function KpiGrid({ kpis }) {
  return (
    <section className="kpi-grid">
      {labels.map((item, index) => (
        <article
          className="kpi-card animate-rise"
          key={item.key}
          style={{ '--delay': `${index * 70}ms` }}
        >
          <p>{item.title}</p>
          <h3>{kpis?.[item.key] ?? '-'}</h3>
        </article>
      ))}
    </section>
  );
}
