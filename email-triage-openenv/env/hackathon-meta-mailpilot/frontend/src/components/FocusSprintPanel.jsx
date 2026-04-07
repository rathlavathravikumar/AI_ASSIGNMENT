export default function FocusSprintPanel({ sprintData, onRun }) {
  return (
    <section className="panel sprint-panel animate-rise" style={{ '--delay': '170ms' }}>
      <div className="panel-head">
        <h2>Focus Sprint</h2>
        <button type="button" className="small" onClick={() => onRun({ minutes: 15, queueSize: 6 })}>
          Launch 15m Sprint
        </button>
      </div>

      {!sprintData ? (
        <p className="muted">Generate a high-impact queue and prioritize outcomes in a timed run.</p>
      ) : (
        <>
          <p>
            <strong>Projected Impact:</strong> +{sprintData.projectedImpact} trust points
          </p>
          <p className="muted">{sprintData.coachTip}</p>
          <ul className="sprint-list">
            {sprintData.queue.map((email) => (
              <li key={email._id}>
                <span>{email.subject}</span>
                <span>{Math.round(email.urgencyScore || 0)}</span>
              </li>
            ))}
          </ul>
        </>
      )}
    </section>
  );
}
