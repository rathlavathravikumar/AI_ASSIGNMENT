const criticalWords = ['down', 'outage', 'fraud', 'urgent', 'breach', 'payment failed'];
const positiveWords = ['thanks', 'great', 'appreciate', 'love'];

export function inferPriority(text) {
  const normalized = text.toLowerCase();
  if (criticalWords.some((word) => normalized.includes(word))) return 'critical';
  if (normalized.includes('refund') || normalized.includes('blocked')) return 'high';
  if (normalized.includes('pricing') || normalized.includes('trial')) return 'medium';
  return 'low';
}

export function inferCategory(text) {
  const normalized = text.toLowerCase();
  if (normalized.includes('invoice') || normalized.includes('refund') || normalized.includes('billing')) return 'billing';
  if (normalized.includes('bug') || normalized.includes('error') || normalized.includes('crash')) return 'technical';
  if (normalized.includes('demo') || normalized.includes('quote') || normalized.includes('pricing')) return 'sales';
  if (normalized.includes('collaborat') || normalized.includes('partnership')) return 'partnership';
  if (normalized.includes('feedback') || normalized.includes('suggestion')) return 'feedback';
  return 'other';
}

export function inferSentiment(text) {
  const normalized = text.toLowerCase();
  if (positiveWords.some((word) => normalized.includes(word))) return 'positive';
  if (normalized.includes('angry') || normalized.includes('disappointed') || normalized.includes('frustrat')) return 'negative';
  return 'neutral';
}

export function computeUrgency({ priority, sentiment, createdAt }) {
  const priorityScoreMap = {
    low: 20,
    medium: 50,
    high: 75,
    critical: 95
  };

  const ageHours = Math.max(0, (Date.now() - new Date(createdAt).getTime()) / (1000 * 60 * 60));
  const ageBoost = Math.min(20, ageHours * 1.5);
  const sentimentBoost = sentiment === 'negative' ? 8 : sentiment === 'positive' ? -5 : 0;

  return Math.max(0, Math.min(100, priorityScoreMap[priority] + ageBoost + sentimentBoost));
}
