import { Email } from '../models/Email.js';

export async function getDashboardInsights(_req, res, next) {
  try {
    const [total, open, resolved, critical, avgUrgency] = await Promise.all([
      Email.countDocuments(),
      Email.countDocuments({ status: { $in: ['new', 'in_progress'] } }),
      Email.countDocuments({ status: 'resolved' }),
      Email.countDocuments({ priority: 'critical', status: { $ne: 'resolved' } }),
      Email.aggregate([{ $group: { _id: null, avg: { $avg: '$urgencyScore' } } }])
    ]);

    const byCategory = await Email.aggregate([
      { $group: { _id: '$category', count: { $sum: 1 } } },
      { $sort: { count: -1 } }
    ]);

    res.json({
      kpis: {
        total,
        open,
        resolved,
        critical,
        avgUrgency: Number(avgUrgency[0]?.avg || 0).toFixed(1)
      },
      byCategory
    });
  } catch (error) {
    next(error);
  }
}

export async function runFocusSprint(req, res, next) {
  try {
    const rawMinutes = req.body?.minutes ?? 15;
    const rawQueueSize = req.body?.queueSize ?? 6;
    const minutes = Number(rawMinutes);
    const queueSize = Number(rawQueueSize);

    if (!Number.isFinite(minutes) || minutes < 5 || minutes > 120) {
      res.status(400);
      throw new Error('minutes must be a number between 5 and 120');
    }
    if (!Number.isFinite(queueSize) || queueSize < 1 || queueSize > 50) {
      res.status(400);
      throw new Error('queueSize must be a number between 1 and 50');
    }

    const focusSessionId = `sprint_${Date.now()}`;

    const queue = await Email.find({ status: { $in: ['new', 'in_progress'] } })
      .sort({ urgencyScore: -1, createdAt: 1 })
      .limit(queueSize);

    await Email.updateMany(
      { _id: { $in: queue.map((item) => item._id) } },
      { $set: { focusSessionId } }
    );

    const projectedImpact = queue.reduce((acc, item) => {
      const multiplier = item.priority === 'critical' ? 3 : item.priority === 'high' ? 2 : 1;
      return acc + Math.round(item.urgencyScore * multiplier / 10);
    }, 0);

    res.json({
      focusSessionId,
      durationMinutes: minutes,
      queue,
      projectedImpact,
      coachTip: 'Resolve critical and negative-sentiment emails first to maximize trust retention.'
    });
  } catch (error) {
    next(error);
  }
}
