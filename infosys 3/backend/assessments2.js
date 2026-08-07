const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const FormData = require('form-data');
const fetch = require('node-fetch');
const db = require('./db');

const router = express.Router();

const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, path.join(__dirname, 'uploads'));
  },
  filename: function (req, file, cb) {
    const ts = Date.now();
    const safe = file.originalname.replace(/[^a-z0-9\.\-\_]/gi, '_');
    cb(null, `${ts}-${safe}`);
  }
});

const upload = multer({ storage });

// Simple Levenshtein distance for scoring
function levenshtein(a, b) {
  if (!a) return b ? b.length : 0;
  if (!b) return a.length;
  const matrix = [];
  for (let i = 0; i <= b.length; i++) {
    matrix[i] = [i];
  }
  for (let j = 0; j <= a.length; j++) {
    matrix[0][j] = j;
  }
  for (let i = 1; i <= b.length; i++) {
    for (let j = 1; j <= a.length; j++) {
      if (b.charAt(i - 1) === a.charAt(j - 1)) {
        matrix[i][j] = matrix[i - 1][j - 1];
      } else {
        matrix[i][j] = Math.min(
          matrix[i - 1][j - 1] + 1, // substitution
          matrix[i][j - 1] + 1,     // insertion
          matrix[i - 1][j] + 1      // deletion
        );
      }
    }
  }
  return matrix[b.length][a.length];
}

function similarityScore(a, b) {
  const aa = (a || '').toLowerCase().trim();
  const bb = (b || '').toLowerCase().trim();
  if (!aa && !bb) return 1.0;
  const dist = levenshtein(aa, bb);
  const maxLen = Math.max(aa.length, bb.length);
  if (maxLen === 0) return 1.0;
  return Math.max(0, (1 - dist / maxLen));
}

async function transcribeWithOpenAI(filePath, language = null) {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) throw new Error('OPENAI_API_KEY not set in environment');

  const form = new FormData();
  form.append('model', 'whisper-1');
  form.append('file', fs.createReadStream(filePath));
  if (language) form.append('language', language);

  const res = await fetch('https://api.openai.com/v1/audio/transcriptions', {
    method: 'POST',
    headers: { Authorization: `Bearer ${apiKey}` },
    body: form
  });

  if (!res.ok) {
    const txt = await res.text();
    throw new Error(`OpenAI transcription error: ${res.status} ${txt}`);
  }
  const data = await res.json();
  return data.text || '';
}

// POST /api/assessments
// Expects multipart/form-data with field 'audio' (file), and optional fields: userId, promptId, expected
router.post('/', upload.single('audio'), async (req, res) => {
  try {
    if (!req.file) return res.status(400).json({ error: 'audio file is required (field name: audio)' });

    const userId = req.body.userId || null;
    const promptId = req.body.promptId || null;
    const promptText = req.body.promptText || req.body.prompt_text || null;
    const expected = req.body.expected || null; // optional expected transcript for scoring
    const language = req.body.language || req.body.lang || 'English';
    const audioPath = req.file.path;

    // Insert initial record
    db.run(
      `INSERT INTO assessments (user_id, prompt_id, prompt_text, expected_text, audio_path, language, status) VALUES (?, ?, ?, ?, ?, ?, ?)`,
      [userId, promptId, promptText, expected, audioPath, language, 'processing'],
      function (err) {
        if (err) console.error('DB insert error', err);
      }
    );

    // Transcribe
    let transcript = '';
    try {
      transcript = await transcribeWithOpenAI(audioPath, language);
    } catch (err) {
      console.error('Transcription failed', err);
      // update record as failed
      db.run(`UPDATE assessments SET status = ?, transcript = ? WHERE audio_path = ?`, ['failed', err.message, audioPath]);
      return res.status(500).json({ error: 'Transcription failed', details: err.message });
    }

    // Score
    let score = null;
    if (expected) {
      const sim = similarityScore(transcript, expected); // 0..1
      score = Math.round(sim * 100) / 100; // two decimals
    }

    // LLM-based rubric scoring
    let report = null;
    try {
      const apiKey = process.env.OPENAI_API_KEY;
      if (!apiKey) throw new Error('OPENAI_API_KEY not set');

      const system = `You are an expert language assessment rater. Given a student's transcript and the expected answer, produce a JSON object with the following numeric fields 0-5 for pronunciation_score, fluency_score, accuracy_score and an overall_score 0-100. Also include a short feedback string. Use these instructions: accuracy refers to how well the content of the transcript matches the expected answer (consider paraphrase); fluency refers to flow, pace and use of fillers (fewer fillers -> higher fluency); pronunciation_score is an estimate based on transcript and likely pronunciation issues (if you cannot judge, give a neutral score). Return strictly JSON.`;

      const userMsg = `Transcript: ${transcript}\nExpected: ${expected || ''}\nPrompt: ${promptText || ''}\nLanguage: ${language || 'English'}`;

      const resp = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${process.env.OPENAI_API_KEY}` },
        body: JSON.stringify({
          model: 'gpt-3.5-turbo',
          messages: [
            { role: 'system', content: system },
            { role: 'user', content: userMsg }
          ],
          temperature: 0.0,
          max_tokens: 300
        })
      });

      if (resp.ok) {
        const data = await resp.json();
        const content = data.choices && data.choices[0] && data.choices[0].message && data.choices[0].message.content;
        if (content) {
          try {
            report = JSON.parse(content);
          } catch (e) {
            const m = content.match(/\{[\s\S]*\}/);
            if (m) {
              try { report = JSON.parse(m[0]); } catch (e2) { report = { feedback: content.trim() }; }
            } else {
              report = { feedback: content.trim() };
            }
          }
        }
      } else {
        const txt = await resp.text();
        console.error('LLM rubric error', txt);
      }
    } catch (err) {
      console.error('Rubric scoring failed', err);
    }

    // Update DB with results including report_json
    db.run(
      `UPDATE assessments SET transcript = ?, score = ?, report_json = ?, status = ? WHERE audio_path = ?`,
      [transcript, score, report ? JSON.stringify(report) : null, 'done', audioPath],
      function (err) {
        if (err) console.error('DB update error', err);
      }
    );

    res.json({ transcript, score, status: 'done', report });
  } catch (err) {
    console.error('Unexpected error', err);
    res.status(500).json({ error: 'Unexpected server error', details: err.message });
  }
});

// POST /api/assessments/generate
// Expects JSON { age, level, language }
router.post('/generate', express.json(), async (req, res) => {
  try {
    const apiKey = process.env.OPENAI_API_KEY;
    if (!apiKey) return res.status(500).json({ error: 'OPENAI_API_KEY not configured' });

    const { age, level, language = 'English' } = req.body;
    const system = `You are an assessment item generator for spoken language practice. Produce one short spoken prompt suitable for a student given their age and level. Return only a JSON object with keys: prompt and expected. Keep the prompt short (one or two sentences) and the expected answer 1-2 sentences.`;
    const userMsg = `Generate a spoken assessment prompt for a student. Age: ${age || 'unspecified'}. Level: ${level || 'unspecified'}. Language: ${language}. Respond only with a JSON object like {"prompt":"...","expected":"..."}.`;

    const resp = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${apiKey}` },
      body: JSON.stringify({
        model: 'gpt-3.5-turbo',
        messages: [
          { role: 'system', content: system },
          { role: 'user', content: userMsg }
        ],
        temperature: 0.7,
        max_tokens: 300
      })
    });

    if (!resp.ok) {
      const txt = await resp.text();
      return res.status(500).json({ error: 'OpenAI generate error', details: txt });
    }

    const data = await resp.json();
    const content = data.choices && data.choices[0] && data.choices[0].message && data.choices[0].message.content;
    if (!content) return res.status(500).json({ error: 'No content from OpenAI' });

    // Try to parse JSON from the model's response
    try {
      const parsed = JSON.parse(content);
      return res.json(parsed);
    } catch (e) {
      const m = content.match(/\{[\s\S]*\}/);
      if (m) {
        try {
          const parsed2 = JSON.parse(m[0]);
          return res.json(parsed2);
        } catch (e2) {
          // fall through
        }
      }
      // Fallback: return raw text as prompt
      return res.json({ prompt: content.trim(), expected: '' });
    }
  } catch (err) {
    console.error('Generate endpoint error', err);
    res.status(500).json({ error: 'Unexpected server error', details: err.message });
  }
});

// POST /api/assessments/:id/review
// Body JSON: { reviewed: true, override_score: number (0-100), reviewer_feedback: string }
router.post('/:id/review', express.json(), (req, res) => {
  const id = req.params.id;
  const { reviewed, override_score, reviewer_feedback } = req.body;
  if (!id) return res.status(400).json({ error: 'id required' });

  db.get(`SELECT id, report_json FROM assessments WHERE id = ?`, [id], (err, row) => {
    if (err) return res.status(500).json({ error: 'DB error', details: err.message });
    if (!row) return res.status(404).json({ error: 'Assessment not found' });

    let report = null;
    try { report = row.report_json ? JSON.parse(row.report_json) : {}; } catch (e) { report = {}; }
    if (override_score !== undefined && override_score !== null) {
      report.reviewer_override_score = override_score;
    }
    if (reviewer_feedback) report.reviewer_feedback = reviewer_feedback;
    report.reviewed_at = new Date().toISOString();

    const newStatus = reviewed ? 'reviewed' : 'done';

    db.run(`UPDATE assessments SET report_json = ?, status = ? WHERE id = ?`, [JSON.stringify(report), newStatus, id], function (err2) {
      if (err2) return res.status(500).json({ error: 'DB error', details: err2.message });
      res.json({ id, status: newStatus, report });
    });
  });
});

module.exports = router;
