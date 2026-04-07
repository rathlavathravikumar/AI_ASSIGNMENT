import { useEffect, useMemo, useState } from 'react';

import Header from './components/Header.jsx';
import KpiGrid from './components/KpiGrid.jsx';
import EmailList from './components/EmailList.jsx';
import EmailDetail from './components/EmailDetail.jsx';
import FocusSprintPanel from './components/FocusSprintPanel.jsx';
import { api } from './api/client.js';

export default function App() {
  const [emails, setEmails] = useState([]);
  const [insights, setInsights] = useState({ kpis: {} });
  const [selectedId, setSelectedId] = useState('');
  const [sprintData, setSprintData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [triaging, setTriaging] = useState(false);
  const [error, setError] = useState('');

  const selectedEmail = useMemo(
    () => emails.find((email) => email._id === selectedId),
    [emails, selectedId]
  );

  async function loadAll() {
    try {
      setLoading(true);
      const [allEmails, dashboard] = await Promise.all([api.getEmails(), api.getInsights()]);
      setEmails(allEmails);
      setInsights(dashboard);
      setSelectedId((prev) => prev || allEmails[0]?._id || '');
      setError('');
    } catch (loadError) {
      setError(loadError.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadAll();
  }, []);

  async function onTriage(id) {
    try {
      setTriaging(true);
      await api.triageEmail(id);
      await loadAll();
    } catch (triageError) {
      setError(triageError.message);
    } finally {
      setTriaging(false);
    }
  }

  async function onResolve(id) {
    try {
      await api.updateStatus(id, 'resolved');
      await loadAll();
    } catch (resolveError) {
      setError(resolveError.message);
    }
  }

  async function onRunSprint(payload) {
    try {
      const response = await api.runFocusSprint(payload);
      setSprintData(response);
      setError('');
    } catch (sprintError) {
      setError(sprintError.message);
    }
  }

  return (
    <main className="page">
      <div className="bg-orb orb-a" />
      <div className="bg-orb orb-b" />
      <Header />
      {error ? <p className="error">{error}</p> : null}
      <KpiGrid kpis={insights.kpis} />

      {loading ? (
        <div className="panel loading-panel animate-rise" style={{ '--delay': '140ms' }}>
          <div className="loading-shimmer" />
          <span>Loading inbox intelligence...</span>
        </div>
      ) : (
        <section className="workspace">
          <EmailList emails={emails} selectedId={selectedId} onSelect={(email) => setSelectedId(email._id)} />
          <EmailDetail
            email={selectedEmail}
            onTriage={onTriage}
            onResolve={onResolve}
            triaging={triaging}
          />
          <FocusSprintPanel sprintData={sprintData} onRun={onRunSprint} />
        </section>
      )}
    </main>
  );
}
