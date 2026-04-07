import { connectDb } from '../config/db.js';
import { Email } from '../models/Email.js';

const sampleEmails = [
  {
    sender: 'finops@northwind.ai',
    subject: 'Invoice mismatch for March billing',
    body: 'We were charged for 40 seats but only 27 are active. Please issue refund quickly.',
    priority: 'high',
    category: 'billing',
    sentiment: 'negative',
    urgencyScore: 84
  },
  {
    sender: 'cto@rapidcart.io',
    subject: 'Production outage when syncing webhook',
    body: 'Our checkout integration is down and customer orders are failing right now.',
    priority: 'critical',
    category: 'technical',
    sentiment: 'negative',
    urgencyScore: 98
  },
  {
    sender: 'hello@orbitstudio.com',
    subject: 'Need pricing for enterprise rollout',
    body: 'Can we schedule a demo this week and discuss enterprise pricing tiers?',
    priority: 'medium',
    category: 'sales',
    sentiment: 'neutral',
    urgencyScore: 62
  }
];

async function seed() {
  await connectDb();
  await Email.deleteMany({});
  await Email.insertMany(sampleEmails);
  console.log('Seeded sample emails');
  process.exit(0);
}

seed().catch((error) => {
  console.error(error);
  process.exit(1);
});
