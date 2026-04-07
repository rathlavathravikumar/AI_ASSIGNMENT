import { Router } from 'express';
import {
  createEmail,
  getEmailById,
  getEmails,
  triageEmail,
  updateEmailStatus
} from '../controllers/emailController.js';

const router = Router();

router.get('/', getEmails);
router.get('/:id', getEmailById);
router.post('/', createEmail);
router.patch('/:id/status', updateEmailStatus);
router.post('/:id/triage', triageEmail);

export default router;
