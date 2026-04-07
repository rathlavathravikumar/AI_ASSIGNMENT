import { Router } from 'express';
import { getDashboardInsights, runFocusSprint } from '../controllers/insightController.js';

const router = Router();

router.get('/dashboard', getDashboardInsights);
router.post('/focus-sprint', runFocusSprint);

export default router;
