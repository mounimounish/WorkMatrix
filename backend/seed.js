// backend/seed.js
const db = require('./db');
const bcrypt = require('bcryptjs');
const { nanoid } = require('nanoid');

function seed() {
  db.read();
  const now = Date.now();

  const exists = (email) => db.data.users.find(u => u.email === email);
  const users = [
    { email: 'mounishm@rljit.in', fullName: 'mouni', role: 'ADMIN', password: 'MOUNI' },
    { email: 'manager@local', fullName: 'Manager User', role: 'MANAGER', password: 'Manager@123' },
    { email: 'employee@local', fullName: 'Employee User', role: 'EMPLOYEE', password: 'Employee@123' }
  ];

  users.forEach(u => {
    if (!exists(u.email)) {
      const id = nanoid();
      const hash = bcrypt.hashSync(u.password, 8);
      db.data.users.push({ id, email: u.email, password: hash, fullName: u.fullName, role: u.role, createdAt: now });
    }
  });

  // sample tasks
  const admin = db.data.users.find(x => x.email === 'mounishm@rljit.in');
  const manager = db.data.users.find(x => x.email === 'manager@local');
  const employee = db.data.users.find(x => x.email === 'employee@local');

  if (db.data.tasks.length === 0) {
    db.data.tasks.push({
      id: nanoid(),
      title: 'Initial setup',
      description: 'Create repo & CI',
      assigneeId: employee.id,
      status: 'TODO',
      priority: 3,
      dueDate: null,
      createdBy: manager.id,
      createdAt: now,
      updatedAt: now
    });
    db.data.tasks.push({
      id: nanoid(),
      title: 'Design schema',
      description: 'Define tables',
      assigneeId: manager.id,
      status: 'IN_PROGRESS',
      priority: 2,
      dueDate: null,
      createdBy: admin.id,
      createdAt: now,
      updatedAt: now
    });
  }

  db.write();
  console.log('Seeded users and tasks.');
}

seed();
