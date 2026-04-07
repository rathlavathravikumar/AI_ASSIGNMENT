import mongoose from 'mongoose';

const emailSchema = new mongoose.Schema(
  {
    sender: { type: String, required: true, trim: true },
    subject: { type: String, required: true, trim: true },
    body: { type: String, required: true },
    status: {
      type: String,
      enum: ['new', 'in_progress', 'resolved', 'archived'],
      default: 'new'
    },
    priority: {
      type: String,
      enum: ['low', 'medium', 'high', 'critical'],
      default: 'medium'
    },
    category: {
      type: String,
      enum: ['billing', 'technical', 'sales', 'partnership', 'feedback', 'other'],
      default: 'other'
    },
    sentiment: {
      type: String,
      enum: ['negative', 'neutral', 'positive'],
      default: 'neutral'
    },
    aiSummary: { type: String, default: '' },
    aiSuggestedReply: { type: String, default: '' },
    aiConfidence: { type: Number, default: 0 },
    urgencyScore: { type: Number, default: 50 },
    tags: { type: [String], default: [] },
    slaDeadline: { type: Date },
    focusSessionId: { type: String, default: '' },
    resolvedAt: { type: Date }
  },
  { timestamps: true }
);

emailSchema.index({ status: 1, urgencyScore: -1, createdAt: -1 });
emailSchema.index({ subject: 'text', body: 'text', sender: 'text' });

export const Email = mongoose.model('Email', emailSchema);
