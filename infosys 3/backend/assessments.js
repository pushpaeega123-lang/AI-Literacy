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

async function transcribeWithOpenAI(filePath) {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) throw new Error('OPENAI_API_KEY not set in environment');

  const form = new FormData();
  form.append('model', 'whisper-1');
  form.append('file', fs.createReadStream(filePath));

  const res = await fetch('https://api.openai.com/v1/audio/transcriptions', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${apiKey}`
    },
    body: form
  });

  if (!res.ok) {
    const txt = await res.text();
    throw new Error(`OpenAI transcription error: ${res.status} ${txt}`);
  }
  const data = await res.json();
  // API returns { text: 'transcript...' }
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
      const apiKey = process.env.OPENAI_API_KEY;
      if (!apiKey) throw new Error('OPENAI_API_KEY not set in environment');
      const formT = new FormData();
      formT.append('model', 'whisper-1');
      formT.append('file', fs.createReadStream(audioPath));

      const respT = await fetch('https://api.openai.com/v1/audio/transcriptions', {
        method: 'POST',
        headers: { Authorization: `Bearer ${apiKey}` },
        body: formT
      });

      if (!respT.ok) {
        const txt = await respT.text();
        throw new Error(`OpenAI transcription error: ${respT.status} ${txt}`);
      }
      const dataT = await respT.json();
      transcript = dataT.text || '';
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

    // Update DB with results
    db.run(
      `UPDATE assessments SET transcript = ?, score = ?, status = ? WHERE audio_path = ?`,
      [transcript, score, 'done', audioPath],
      function (err) {
        if (err) console.error('DB update error', err);
      }
    );

    res.json({ transcript, score, status: 'done' });
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

module.exports = router;
