const fs = require('fs');
const path = require('path');
const db = require('../db');

async function seed() {
  const uploadsDir = path.join(__dirname, '..', 'uploads');
  if (!fs.existsSync(uploadsDir)) fs.mkdirSync(uploadsDir, { recursive: true });

  // Create placeholder WAV (1 second of silence) - minimal RIFF header + silence
  const wavPath = path.join(uploadsDir, 'placeholder_silence.wav');
  if (!fs.existsSync(wavPath)) {
    // 1-second 8000Hz 16-bit mono silence
    const header = Buffer.from([
      0x52,0x49,0x46,0x46, // 'RIFF'
    ]);
    // For simplicity, write a tiny valid WAV using node's wav module would be better, but to avoid deps write a small file from base64
    const base64 = 'UklGRigAAABXQVZFZm10IBAAAAABAAEAIlYAAESsAAACABAAZGF0YQAAAAA='; // very small WAV placeholder
    fs.writeFileSync(wavPath, Buffer.from(base64, 'base64'));
    console.log('Created placeholder audio at', wavPath);
  } else {
    console.log('Placeholder audio already exists at', wavPath);
  }

  // Ensure users table exists and insert test user
  db.run(`CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, name TEXT, age TEXT, level TEXT)`);
  const user = { id: 'testuser', name: 'Demo Student', age: '10', level: 'beginner' };
  db.run(`INSERT OR REPLACE INTO users (id, name, age, level) VALUES (?, ?, ?, ?)`, [user.id, user.name, user.age, user.level], function(err) {
    if (err) console.error('Failed to insert user', err);
    else console.log('Inserted/updated user', user.id);
  });

  // Insert a scheduled assessment for today
  const today = new Date().toISOString().slice(0,10);
  db.run(`INSERT INTO assessments (user_id, prompt_text, expected_text, scheduled_date, status, language) VALUES (?, ?, ?, ?, ?, ?)`,
    [user.id, 'Please say: "My favorite hobby is reading books."', 'My favorite hobby is reading books.', today, 'scheduled', 'English'], function(err) {
      if (err) console.error('Failed to insert scheduled assessment', err);
      else console.log('Inserted scheduled assessment for', user.id);
    });

  // Insert a completed assessment with fake transcript and report
  const fakeTranscript = 'my favorite hobby is reading books';
  const similarity = 0.95;
  const fakeReport = {
    pronunciation_score: 4.0,
    fluency_score: 4.2,
    accuracy_score: 4.5,
    overall_score: 92,
    feedback: 'Good pronunciation and fluency. Keep working on intonation.'
  };

  const now = new Date().toISOString();
  db.run(`INSERT INTO assessments (user_id, prompt_text, expected_text, audio_path, transcript, score, report_json, status, scheduled_date, language, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
    [user.id, 'Please say: "My favorite hobby is reading books."', 'My favorite hobby is reading books.', wavPath, fakeTranscript, similarity, JSON.stringify(fakeReport), 'done', today, 'English', now], function(err) {
      if (err) console.error('Failed to insert completed assessment', err);
      else console.log('Inserted completed assessment for', user.id);

      // Print last 10 assessments
      db.all(`SELECT id, user_id, prompt_text, expected_text, transcript, score, report_json, status, scheduled_date, created_at FROM assessments WHERE user_id = ? ORDER BY created_at DESC LIMIT 10`, [user.id], (err2, rows) => {
        if (err2) { console.error('Failed to query assessments', err2); process.exit(1); }
        console.log('Recent assessments for', user.id);
        for (const r of rows) {
          console.log('---');
          console.log('id:', r.id);
          console.log('prompt:', r.prompt_text);
          console.log('expected:', r.expected_text);
          console.log('transcript:', r.transcript);
          console.log('score:', r.score);
          console.log('report_json:', r.report_json);
          console.log('status:', r.status);
          console.log('scheduled_date:', r.scheduled_date);
          console.log('created_at:', r.created_at);
        }
        process.exit(0);
      });
    });
}

seed().catch(err => { console.error(err); process.exit(1); });
