const express = require('express');
const router = express.Router();
const db = require('../db');
const { authMiddleware } = require('../auth');
const { nanoid } = require('nanoid');

// POST /api/files  { name, contentBase64 }
router.post('/', authMiddleware, (req, res) => {
  const { name, contentBase64 } = req.body;
  if (!name || !contentBase64) return res.status(400).json({ error: 'name and contentBase64 required' });
  db.read();
  const id = nanoid();
  const now = Date.now();
  const file = { id, name, contentBase64, versions: [{ ver:1, contentBase64, uploadedAt: now }], uploadedBy: req.user.id, createdAt: now };
  db.data.files.push(file);
  db.data.audit.push({ id: nanoid(), action: 'UPLOAD_FILE', by: req.user.id, target: id, at: now });
  db.write();
  res.json({ id, name, uploadedBy: req.user.id, createdAt: now });
});

// GET /api/files
router.get('/', authMiddleware, (req, res) => {
  db.read();
  res.json(db.data.files.map(f => ({ id: f.id, name: f.name, uploadedBy: f.uploadedBy, createdAt: f.createdAt, versions: f.versions.length })));
});

// GET /api/files/:id
router.get('/:id', authMiddleware, (req, res) => {
  const id = req.params.id;
  db.read();
  const file = db.data.files.find(f => f.id === id);
  if (!file) return res.status(404).json({ error: 'Not found' });
  res.json(file);
});

module.exports = router;
