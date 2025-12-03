const express = require('express');
const router = express.Router();
const db = require('../db');
const { authMiddleware } = require('../auth');
const { nanoid } = require('nanoid');

// GET /api/messages?taskId=...
router.get('/', authMiddleware, (req, res) => {
  const { taskId } = req.query;
  db.read();
  const msgs = taskId ? db.data.messages.filter(m => m.taskId === taskId) : db.data.messages;
  res.json(msgs);
});

// POST /api/messages { taskId, text }
router.post('/', authMiddleware, (req, res) => {
  const { taskId, text } = req.body;
  if (!taskId || !text) return res.status(400).json({ error: 'taskId and text required' });
  db.read();
  const id = nanoid();
  const now = Date.now();
  const msg = { id, taskId, text, userId: req.user.id, createdAt: now };
  db.data.messages.push(msg);
  db.data.audit.push({ id: nanoid(), action: 'CREATE_MESSAGE', by: req.user.id, target: id, at: now });
  db.write();
  res.json(msg);
});

module.exports = router;
