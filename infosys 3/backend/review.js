const express = require('express');
const db = require('./db');
const router = express.Router();

// GET /api/review/queue
// Returns assessments that are done and not yet reviewer-reviewed (status != 'reviewed')
router.get('/queue', (req, res) => {
  db.all(`SELECT id, user_id, prompt_text, expected_text, audio_path, transcript, score, report_json, status, scheduled_date, created_at FROM assessments WHERE status != 'reviewed' ORDER BY created_at DESC LIMIT 200`, [], (err, rows) => {
    if (err) return res.status(500).json({ error: 'DB error', details: err.message });
    const items = (rows || []).map(r => {
      let report = null; try { report = r.report_json ? JSON.parse(r.report_json) : null; } catch(e) { report = null; }
      return {
        id: r.id,
        user_id: r.user_id,
        prompt: r.prompt_text,
        expected: r.expected_text,
        audio_path: r.audio_path,
        transcript: r.transcript,
        score: r.score,
        report,
        status: r.status,
        scheduled_date: r.scheduled_date,
        created_at: r.created_at
      };
    });
    res.json(items);
  });
});

module.exports = router;