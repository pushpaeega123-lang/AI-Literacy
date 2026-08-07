const db = require('../db');
const fetch = require('node-fetch');

async function generateForAllUsers() {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) throw new Error('OPENAI_API_KEY not set');

  db.all(`SELECT id, name, age, level FROM users`, async (err, rows) => {
    if (err) {
      console.error('Failed to query users', err);
      process.exit(1);
    }

    const users = rows || [];
    for (const user of users) {
      try {
        const age = user.age || '';
        const level = user.level || 'beginner';
        const language = 'English'; // Could be extended to per-user language

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
          console.error('OpenAI generate error for user', user.id, txt);
          continue;
        }

        const data = await resp.json();
        const content = data.choices && data.choices[0] && data.choices[0].message && data.choices[0].message.content;
        let prompt = '';
        let expected = '';
        if (content) {
          try {
            const parsed = JSON.parse(content);
            prompt = parsed.prompt || '';
            expected = parsed.expected || '';
          } catch (e) {
            const m = content.match(/\{[\s\S]*\}/);
            if (m) {
              try {
                const parsed2 = JSON.parse(m[0]);
                prompt = parsed2.prompt || '';
                expected = parsed2.expected || '';
              } catch (e2) {
                prompt = content.trim();
                expected = '';
              }
            } else {
              prompt = content.trim();
              expected = '';
            }
          }
        }

        const today = new Date().toISOString().slice(0, 10);
        db.run(`INSERT INTO assessments (user_id, prompt_text, expected_text, scheduled_date, status, language) VALUES (?, ?, ?, ?, ?, ?)`,
          [user.id, prompt, expected, today, 'scheduled', language], function (err) {
            if (err) console.error('Failed to insert scheduled assessment', err);
            else console.log('Scheduled assessment for user', user.id);
          });

        // Simple rate limit
        await new Promise(r => setTimeout(r, 500));
      } catch (err) {
        console.error('Error generating for user', user.id, err);
      }
    }

    console.log('Daily generation complete');
    process.exit(0);
  });
}

generateForAllUsers().catch(err => { console.error(err); process.exit(1); });