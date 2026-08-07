const express = require('express');
const db = require('./db');
const router = express.Router();

// Create a user (for demo purposes)
// POST /api/users { id, name, age, level }
router.post('/', express.json(), (req, res) => {
  const { id, name, age, level } = req.body;
  if (!id) return res.status(400).json({ error: 'id is required' });
  db.run(
    `CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, name TEXT, age TEXT, level TEXT)`
  );
  db.run(`INSERT OR REPLACE INTO users (id, name, age, level) VALUES (?, ?, ?, ?)`, [id, name || null, age || null, level || null], function (err) {
    if (err) return res.status(500).json({ error: 'DB error', details: err.message });
    res.json({ id, name, age, level });
  });
});

// List users
router.get('/', (req, res) => {
  db.all(`SELECT id, name, age, level FROM users`, [], (err, rows) => {
    if (err) return res.status(500).json({ error: 'DB error', details: err.message });
    res.json(rows || []);
  });
});

module.exports = router;