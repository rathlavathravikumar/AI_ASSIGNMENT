const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

async function request(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json'
    },
    ...options
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.message || 'API request failed');
  }

  return response.json();
}

export const api = {
  getEmails: () => request('/emails'),
  getInsights: () => request('/insights/dashboard'),
  triageEmail: (id) => request(`/emails/${id}/triage`, { method: 'POST' }),
  updateStatus: (id, status) => request(`/emails/${id}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ status })
  }),
  runFocusSprint: (payload) => request('/insights/focus-sprint', {
    method: 'POST',
    body: JSON.stringify(payload)
  })
};
