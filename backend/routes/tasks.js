const express = require("express");
const router = express.Router();
const db = require("../db");
const { nanoid } = require("nanoid");
const { authMiddleware, authorize } = require("../auth");

// GET /api/tasks
router.get("/", authMiddleware, (req, res) => {
  db.read();
  // All users can see all tasks (employees see their assigned tasks highlighted)
  const tasks = [...db.data.tasks].sort((a,b)=>b.createdAt - a.createdAt);
  res.json(tasks);
});

// POST /api/tasks (Admin or Manager)
router.post("/", authorize("ADMIN", "MANAGER"), (req, res) => {
  const { title, description, assigneeId, priority, dueDate } = req.body;
  if (!title) return res.status(400).json({ error: "title required" });
  db.read();
  const now = Date.now();
  const id = nanoid();
  const task = {
    id, title, description: description || "", assigneeId: assigneeId || null,
    status: "TODO", priority: priority || 3, dueDate: dueDate ? Date.parse(dueDate) : null,
    createdBy: req.user.id, createdAt: now, updatedAt: now
  };
  db.data.tasks.push(task);
  db.write();
  res.json(task);
});

// PATCH /api/tasks/:id
router.patch("/:id", authMiddleware, (req, res) => {
  const id = req.params.id;
  db.read();
  const idx = db.data.tasks.findIndex(t => t.id === id);
  if (idx === -1) return res.status(404).json({ error: "Not found" });
  const task = db.data.tasks[idx];

  if (req.user.role === "EMPLOYEE") {
    // Employees can update only status (for all tasks they can see)
    if (!req.body.status) return res.status(400).json({ error: "Employee can update only status" });
    task.status = req.body.status;
    task.updatedAt = Date.now();
    db.data.tasks[idx] = task; db.write();
    return res.json(task);
  }

  // Admin/Manager updates
  ["title","description","assigneeId","status","priority","dueDate"].forEach(f => {
    if (req.body[f] !== undefined) {
      task[f] = f === "dueDate" ? (req.body.dueDate ? Date.parse(req.body.dueDate) : null) : req.body[f];
    }
  });
  task.updatedAt = Date.now();
  db.data.tasks[idx] = task; db.write();
  res.json(task);
});

// DELETE (Admin only)
router.delete("/:id", authorize("ADMIN"), (req, res) => {
  const id = req.params.id;
  db.read();
  db.data.tasks = db.data.tasks.filter(t => t.id !== id);
  db.write();
  res.json({ ok: true });
});

module.exports = router;
