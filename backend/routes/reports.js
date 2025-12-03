const express = require('express');
const router = express.Router();
const db = require('../db');
const { authMiddleware } = require('../auth');
const { nanoid } = require('nanoid');

// Simple tasks report: /api/reports/tasks returns JSON summary or CSV when ?format=csv
router.get('/tasks', authMiddleware, (req, res) => {
  const { format } = req.query;
  db.read();
  const rows = db.data.tasks.map(t => ({ id: t.id, title: t.title, status: t.status, assigneeId: t.assigneeId, createdAt: t.createdAt }));
  if (format === 'csv') {
    const header = 'id,title,status,assigneeId,createdAt\n';
    const csv = header + rows.map(r => `${r.id},"${(r.title||'').replace(/"/g,'""')}",${r.status},${r.assigneeId||''},${r.createdAt}`).join('\n');
    res.setHeader('Content-Type', 'text/csv');
    res.send(csv);
    return;
  }
  res.json({ total: rows.length, rows });
});

module.exports = router;
