const express = require('express');
const db = require('./db');
const router = express.Router();

// GET /api/dashboard/:userId
// Returns summary info for the dashboard
router.get('/:userId', (req, res) => {
  const userId = req.params.userId;
  if (!userId) return res.status(400).json({ error: 'userId required' });

  db.get(`SELECT id, name, age, level FROM users WHERE id = ?`, [userId], (err, user) => {
    if (err) return res.status(500).json({ error: 'DB error', details: err.message });

    if (!user) return res.status(404).json({ error: 'User not found' });

    // Recent assessments (latest 10)
    db.all(`SELECT id, prompt_text, expected_text, transcript, score, report_json, status, scheduled_date, created_at FROM assessments WHERE user_id = ? ORDER BY created_at DESC LIMIT 10`, [userId], (err2, rows) => {
      if (err2) return res.status(500).json({ error: 'DB error', details: err2.message });

      const assessments = (rows || []).map(r => {
        let report = null;
        try { report = r.report_json ? JSON.parse(r.report_json) : null; } catch (e) { report = null; }
        return {
          id: r.id,
          prompt: r.prompt_text,
          expected: r.expected_text,
          transcript: r.transcript,
          score: typeof r.score === 'number' ? r.score : null,
          report,
          status: r.status,
          scheduled_date: r.scheduled_date,
          created_at: r.created_at,
          audio_path: r.audio_path
        };
      });

      // Compute summary metrics
      let overallScore = null; // percent 0-100
      let achievementPoints = 0;
      let counted = 0;
      for (const a of assessments) {
        if (a.report && typeof a.report.overall_score === 'number') {
          overallScore = overallScore === null ? a.report.overall_score : (overallScore + a.report.overall_score) / 2;
          achievementPoints += Math.round(a.report.overall_score / 10);
          counted++;
        } else if (typeof a.score === 'number') {
          const sc = Math.round(a.score * 100);
          overallScore = overallScore === null ? sc : (overallScore + sc) / 2;
          achievementPoints += Math.round(sc / 10);
          counted++;
        }
      }
      if (overallScore === null) overallScore = 0; else overallScore = Math.round(overallScore);

      // Progress: ratio of done assessments to total scheduled+done
      db.get(`SELECT COUNT(*) as doneCount FROM assessments WHERE user_id = ? AND status = 'done'`, [userId], (err3, doneRow) => {
        if (err3) return res.status(500).json({ error: 'DB error', details: err3.message });
        db.get(`SELECT COUNT(*) as totalCount FROM assessments WHERE user_id = ? AND (status = 'scheduled' OR status = 'done')`, [userId], (err4, totalRow) => {
          if (err4) return res.status(500).json({ error: 'DB error', details: err4.message });

          const doneCount = (doneRow && doneRow.doneCount) || 0;
          const totalCount = (totalRow && totalRow.totalCount) || 0;
          let progress = 0;
          if (totalCount > 0) progress = Math.round((doneCount / totalCount) * 100);

          // Today's scheduled assessment (if any)
          const today = new Date().toISOString().slice(0, 10);
          db.get(`SELECT id, prompt_text, expected_text, scheduled_date FROM assessments WHERE user_id = ? AND scheduled_date = ? ORDER BY created_at DESC LIMIT 1`, [userId, today], (err5, todayRow) => {
            if (err5) return res.status(500).json({ error: 'DB error', details: err5.message });

            res.json({
              user,
              overallScore,
              currentLevel: user.level || 'Unknown',
              progress,
              achievementPoints,
              todaysAssessment: todayRow || null,
              recentAssessments: assessments
            });
          });
        });
      });
    });
  });
});

module.exports = router;