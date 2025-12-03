const express = require('express');
const router = express.Router();
const db = require('../db');
const { authorize } = require('../auth');

// GET /api/audit - admin only
router.get('/', authorize('ADMIN'), (req, res) => {
  db.read();
  res.json(db.data.audit || []);
});

module.exports = router;
