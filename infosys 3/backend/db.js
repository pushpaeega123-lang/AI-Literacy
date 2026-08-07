const path = require('path');
const sqlite3 = require('sqlite3').verbose();
const dbPath = path.join(__dirname, 'migrations', 'assessments.db');

const db = new sqlite3.Database(dbPath);

// Create table if not exists
db.serialize(() => {
  db.run(`
    CREATE TABLE IF NOT EXISTS assessments (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id TEXT,
      prompt_id TEXT,
      prompt_text TEXT,
      expected_text TEXT,
      audio_path TEXT,
      transcript TEXT,
      score REAL,
      report_json TEXT,
      scheduled_date DATE,
      language TEXT,
      status TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);

  // Ensure language column exists for older DBs
  db.get("PRAGMA table_info(assessments)", (err, row) => {
    // If PRAGMA fails or table doesn't exist yet, skip; the CREATE TABLE above handles initial creation
    if (err) return;
    db.all("PRAGMA table_info(assessments)", (err2, cols) => {
      if (err2) return;
      const names = (cols || []).map(c => c.name);
      if (!names.includes('language')) {
        db.run(`ALTER TABLE assessments ADD COLUMN language TEXT`);
      }
    });
  });
});

module.exports = db;
