function priorityClass(priority) {
  return `priority priority-${priority || 'medium'}`;
}

export default function EmailList({ emails, selectedId, onSelect }) {
  return (
    <section className="panel list-panel">
      <div className="panel-head">
        <h2>Inbox Queue</h2>
      </div>
      <div className="email-list">
        {emails.map((email, index) => (
          <button
            key={email._id}
            type="button"
            className={`email-row animate-rise ${selectedId === email._id ? 'active' : ''}`}
            style={{ '--delay': `${index * 45}ms` }}
            onClick={() => onSelect(email)}
          >
            <div>
              <p className="email-subject">{email.subject}</p>
              <p className="email-meta">{email.sender}</p>
            </div>
            <div className="row-right">
              <span className={priorityClass(email.priority)}>{email.priority}</span>
              <span className="urgency">{Math.round(email.urgencyScore || 0)}</span>
            </div>
          </button>
        ))}
      </div>
    </section>
  );
}
