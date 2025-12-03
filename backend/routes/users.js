const express = require('express');
const router = express.Router();
const db = require('../db');
const { authorize, authMiddleware } = require('../auth');
const { nanoid } = require('nanoid');

// GET /api/users - admin only
router.get('/', authorize('ADMIN'), (req, res) => {
  db.read();
  res.json(db.data.users.map(u => ({ id: u.id, email: u.email, fullName: u.fullName, role: u.role, createdAt: u.createdAt })));
});

// POST /api/users/signup - public employee self-registration (no auth required)
router.post('/signup', (req, res) => {
  const { email, fullName, password, role } = req.body;
  if (!email || !password) return res.status(400).json({ error: 'email and password required' });
  if (!fullName) return res.status(400).json({ error: 'fullName required' });
  
  db.read();
  if (db.data.users.find(u => u.email === email)) return res.status(409).json({ error: 'User already exists' });
  
  const id = nanoid();
  const bcrypt = require('bcryptjs');
  const hash = bcrypt.hashSync(password, 8);
  const now = Date.now();
  
  // Force role to EMPLOYEE for self-registration
  db.data.users.push({ id, email, fullName, role: 'EMPLOYEE', password: hash, createdAt: now });
  db.write();
  
  // audit
  db.read(); 
  db.data.audit.push({ id: nanoid(), action: 'EMPLOYEE_SIGNUP', by: null, target: id, at: Date.now() }); 
  db.write();
  
  res.status(201).json({ id, email, fullName, role: 'EMPLOYEE', createdAt: now });
});

// POST /api/users - admin create
router.post('/', authorize('ADMIN'), (req, res) => {
  const { email, fullName, role, password } = req.body;
  if (!email || !password || !role) return res.status(400).json({ error: 'email,password,role required' });
  db.read();
  if (db.data.users.find(u => u.email === email)) return res.status(409).json({ error: 'User exists' });
  const id = nanoid();
  const bcrypt = require('bcryptjs');
  const hash = bcrypt.hashSync(password, 8);
  const now = Date.now();
  db.data.users.push({ id, email, fullName: fullName || email, role, password: hash, createdAt: now });
  db.write();
  // audit
  db.read(); db.data.audit.push({ id: nanoid(), action: 'CREATE_USER', by: req.user?.id || null, target: id, at: Date.now() }); db.write();
  res.json({ id, email, fullName, role });
});

// DELETE /api/users/:id - Admins can remove any user (except themselves), Managers can remove EMPLOYEE users
router.delete('/:id', authMiddleware, (req, res) => {
  const id = req.params.id;
  db.read();
  const target = db.data.users.find(u => u.id === id);
  if (!target) return res.status(404).json({ error: 'Not found' });

  const actorRole = req.user.role;
  // Prevent self-deletion
  if (req.user.id === id) return res.status(400).json({ error: 'Cannot delete yourself' });

  if (actorRole === 'ADMIN') {
    // allowed
  } else if (actorRole === 'MANAGER') {
    if (target.role !== 'EMPLOYEE') return res.status(403).json({ error: 'Managers can only remove employees' });
  } else {
    return res.status(403).json({ error: 'Forbidden' });
  }

  db.data.users = db.data.users.filter(u => u.id !== id);
  db.data.audit.push({ id: nanoid(), action: 'DELETE_USER', by: req.user.id, target: id, at: Date.now() });
  db.write();
  res.json({ ok: true });
});

module.exports = router;
