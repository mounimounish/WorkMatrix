// backend/server.js
const express = require('express');
const cors = require('cors');
const bodyParser = require('express').json;
const db = require('./db');
const bcrypt = require('bcryptjs');
const { sign } = require('./auth');
const tasksRouter = require('./routes/tasks');
const dashboardRouter = require('./routes/dashboard');
const usersRouter = require('./routes/users');
const filesRouter = require('./routes/files');
const messagesRouter = require('./routes/messages');
const reportsRouter = require('./routes/reports');
const auditRouter = require('./routes/audit');

const app = express();
app.use(cors());
app.use(bodyParser());

// Auth routes: login (using lowdb)
app.post('/api/auth/login', (req, res) => {
  const { email, password } = req.body;
  if (!email || !password) return res.status(400).json({ error: 'email+password required' });
  db.read();
  const user = db.data.users.find(u => u.email === email);
  if (!user) return res.status(401).json({ error: 'Invalid credentials' });
  if (!bcrypt.compareSync(password, user.password)) return res.status(401).json({ error: 'Invalid credentials' });
  const token = sign({ id: user.id, email: user.email, role: user.role });
  res.json({ token, user: { id: user.id, email: user.email, fullName: user.fullName, role: user.role } });
});

app.use('/api/tasks', tasksRouter);
app.use('/api/dashboard', dashboardRouter);
app.use('/api/users', usersRouter);
app.use('/api/files', filesRouter);
app.use('/api/messages', messagesRouter);
app.use('/api/reports', reportsRouter);
app.use('/api/audit', auditRouter);

app.get('/api/me', (req, res) => res.json({ ok: true }));

const port = process.env.PORT || 4000;
app.listen(port, () => console.log(`Backend listening on http://localhost:${port}`));
