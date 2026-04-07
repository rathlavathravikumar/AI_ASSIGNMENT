import OpenAI from 'openai';
import { env } from '../config/env.js';
import { computeUrgency, inferCategory, inferPriority, inferSentiment } from './scoringService.js';

const client = env.openAiApiKey ? new OpenAI({ apiKey: env.openAiApiKey }) : null;

function fallbackTriage(email) {
  const text = `${email.subject}\n${email.body}`;
  const priority = inferPriority(text);
  const category = inferCategory(text);
  const sentiment = inferSentiment(text);
  const urgencyScore = computeUrgency({ priority, sentiment, createdAt: email.createdAt || new Date() });

  return {
    summary: `${email.subject} from ${email.sender}. Main request: ${category}.`,
    suggestedReply: 'Thanks for reaching out. We have prioritized your request and a specialist will follow up shortly.',
    priority,
    category,
    sentiment,
    urgencyScore,
    confidence: 0.62,
    source: 'heuristic'
  };
}

export async function triageWithAi(email) {
  if (!client) return fallbackTriage(email);

  const prompt = `You are an email triage assistant for a startup support desk.\nReturn JSON with keys: summary, suggestedReply, priority(low|medium|high|critical), category(billing|technical|sales|partnership|feedback|other), sentiment(negative|neutral|positive), confidence(0-1).\n\nSender: ${email.sender}\nSubject: ${email.subject}\nBody: ${email.body}`;

  try {
    const response = await client.responses.create({
      model: env.openAiModel,
      input: prompt,
      temperature: 0.2
    });

    const raw = response.output_text || '{}';
    const parsed = JSON.parse(raw);
    const urgencyScore = computeUrgency({
      priority: parsed.priority || 'medium',
      sentiment: parsed.sentiment || 'neutral',
      createdAt: email.createdAt || new Date()
    });

    return {
      summary: parsed.summary,
      suggestedReply: parsed.suggestedReply,
      priority: parsed.priority,
      category: parsed.category,
      sentiment: parsed.sentiment,
      urgencyScore,
      confidence: Number(parsed.confidence || 0.8),
      source: 'openai'
    };
  } catch (error) {
    console.warn('AI triage failed, using fallback:', error.message);
    return fallbackTriage(email);
  }
}
