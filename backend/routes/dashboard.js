// backend/routes/dashboard.js
const express = require('express');
const router = express.Router();
const db = require('../db');
const { authMiddleware } = require('../auth');

router.get('/summary', authMiddleware, (req, res) => {
  db.read();
  const total = db.data.tasks.length;
  const users = db.data.users.length;
  const statusCounts = {};
  db.data.tasks.forEach(t => {
    statusCounts[t.status] = (statusCounts[t.status] || 0) + 1;
  });
  const byStatus = Object.entries(statusCounts).map(([status,cnt]) => ({ status, cnt }));
  res.json({ totalTasks: total, byStatus, users });
});

module.exports = router;
