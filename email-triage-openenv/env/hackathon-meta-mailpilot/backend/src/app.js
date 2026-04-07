import cors from 'cors';
import express from 'express';
import helmet from 'helmet';
import morgan from 'morgan';

import emailRoutes from './routes/emailRoutes.js';
import insightRoutes from './routes/insightRoutes.js';
import { errorHandler } from './middleware/errorHandler.js';
import { notFound } from './middleware/notFound.js';
import { env } from './config/env.js';

export const app = express();

app.use(helmet());
app.use(cors({ origin: env.frontendUrl }));
app.use(express.json({ limit: '1mb' }));
app.use(morgan('dev'));

app.get('/api/health', (_req, res) => {
  res.json({ status: 'ok', service: 'mailpilot-api' });
});

app.use('/api/emails', emailRoutes);
app.use('/api/insights', insightRoutes);

app.use(notFound);
app.use(errorHandler);
