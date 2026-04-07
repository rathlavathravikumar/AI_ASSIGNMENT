import { Email } from '../models/Email.js';
import { triageWithAi } from '../services/aiService.js';

const ALLOWED_STATUSES = ['new', 'in_progress', 'resolved', 'archived'];

export async function getEmails(req, res, next) {
  try {
    const { status, priority, q } = req.query;
    const filter = {};

    if (status) filter.status = status;
    if (priority) filter.priority = priority;
    if (q) filter.$text = { $search: q };

    const emails = await Email.find(filter).sort({ urgencyScore: -1, createdAt: -1 }).limit(200);
    res.json(emails);
  } catch (error) {
    next(error);
  }
}

export async function getEmailById(req, res, next) {
  try {
    const email = await Email.findById(req.params.id);
    if (!email) {
      res.status(404);
      throw new Error('Email not found');
    }
    res.json(email);
  } catch (error) {
    next(error);
  }
}

export async function createEmail(req, res, next) {
  try {
    const payload = req.body;
    if (!payload?.sender || !payload?.subject || !payload?.body) {
      res.status(400);
      throw new Error('sender, subject, and body are required');
    }
    const created = await Email.create(payload);
    res.status(201).json(created);
  } catch (error) {
    next(error);
  }
}

export async function updateEmailStatus(req, res, next) {
  try {
    const { status } = req.body;
    if (!status || !ALLOWED_STATUSES.includes(status)) {
      res.status(400);
      throw new Error(`status must be one of: ${ALLOWED_STATUSES.join(', ')}`);
    }

    const email = await Email.findById(req.params.id);

    if (!email) {
      res.status(404);
      throw new Error('Email not found');
    }

    email.status = status || email.status;
    if (status === 'resolved') email.resolvedAt = new Date();
    await email.save();

    res.json(email);
  } catch (error) {
    next(error);
  }
}

export async function triageEmail(req, res, next) {
  try {
    const email = await Email.findById(req.params.id);
    if (!email) {
      res.status(404);
      throw new Error('Email not found');
    }

    const triage = await triageWithAi(email);

    email.aiSummary = triage.summary;
    email.aiSuggestedReply = triage.suggestedReply;
    email.priority = triage.priority;
    email.category = triage.category;
    email.sentiment = triage.sentiment;
    email.urgencyScore = triage.urgencyScore;
    email.aiConfidence = triage.confidence;
    email.tags = [triage.category, triage.priority, triage.sentiment];

    if (triage.priority === 'critical') {
      email.slaDeadline = new Date(Date.now() + 30 * 60 * 1000);
    } else if (triage.priority === 'high') {
      email.slaDeadline = new Date(Date.now() + 2 * 60 * 60 * 1000);
    }

    await email.save();

    res.json({
      email,
      triageSource: triage.source
    });
  } catch (error) {
    next(error);
  }
}
