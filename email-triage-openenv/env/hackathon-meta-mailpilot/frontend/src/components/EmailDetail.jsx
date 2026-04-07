export default function EmailDetail({ email, onTriage, onResolve, triaging }) {
  if (!email) {
    return (
      <section className="panel detail-panel empty">
        <p>Select an email to inspect details and run AI triage.</p>
      </section>
    );
  }

  return (
    <section className="panel detail-panel animate-rise" style={{ '--delay': '120ms' }}>
      <div className="panel-head">
        <h2>{email.subject}</h2>
      </div>

      <div className="meta-grid">
        <span>{email.sender}</span>
        <span className={`priority priority-${email.priority}`}>{email.priority}</span>
        <span>{email.category || 'other'}</span>
        <span>Urgency: {Math.round(email.urgencyScore || 0)}</span>
      </div>

      <p className="mail-body">{email.body}</p>

      <div className="ai-block">
        <h3>AI Summary</h3>
        <p>{email.aiSummary || 'No summary generated yet.'}</p>
      </div>

      <div className="ai-block">
        <h3>Suggested Reply</h3>
        <p>{email.aiSuggestedReply || 'Run AI triage to generate a response draft.'}</p>
      </div>

      <div className="actions">
        <button type="button" onClick={() => onTriage(email._id)} disabled={triaging}>
          {triaging ? 'Analyzing...' : 'Run AI Triage'}
        </button>
        <button type="button" className="ghost" onClick={() => onResolve(email._id)}>
          Mark Resolved
        </button>
      </div>
    </section>
  );
}
