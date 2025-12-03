// backend/db.js — tiny, reliable JSON file DB (no lowdb)
const fs = require('fs');
const path = require('path');

const dataDir = path.join(__dirname, 'data');
if (!fs.existsSync(dataDir)) fs.mkdirSync(dataDir);

const dbPath = path.join(dataDir, 'db.json');

function initFile() {
  if (!fs.existsSync(dbPath)) {
    const initial = { users: [], tasks: [] };
    fs.writeFileSync(dbPath, JSON.stringify(initial, null, 2), 'utf8');
  }
}

const db = {
  data: null,
  read() {
    initFile();
    const raw = fs.readFileSync(dbPath, 'utf8') || '{}';
    try {
      this.data = JSON.parse(raw);
    } catch (e) {
      // If file is corrupted, reset it
      this.data = { users: [], tasks: [] };
      this.write();
    }
    // ensure defaults
    this.data.users = this.data.users || [];
    this.data.tasks = this.data.tasks || [];
    this.data.files = this.data.files || [];
    this.data.messages = this.data.messages || [];
    this.data.audit = this.data.audit || [];
    return this.data;
  },
  write() {
    if (this.data === null) this.data = { users: [], tasks: [] };
    fs.writeFileSync(dbPath, JSON.stringify(this.data, null, 2), 'utf8');
  }
};

// initialize now so other modules can use immediately
db.read();

module.exports = db;
