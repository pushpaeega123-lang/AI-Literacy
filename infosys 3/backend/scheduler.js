const cron = require('node-cron');
const db = require('./db');
const { generatePrompt } = require('./generate');

async function generateForAllUsersOnce() {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) throw new Error('OPENAI_API_KEY not set');

  db.all(`SELECT id, name, age, level FROM users`, async (err, rows) => {
    if (err) {
      console.error('Failed to query users', err);
      return;
    }

    const users = rows || [];
    for (const user of users) {
      try {
        const age = user.age || '';
        const level = user.level || 'beginner';
        const language = 'English';
        const { prompt, expected } = await generatePrompt({ age, level, language });
        const today = new Date().toISOString().slice(0, 10);
        db.run(
          `INSERT INTO assessments (user_id, prompt_text, expected_text, scheduled_date, status, language) VALUES (?, ?, ?, ?, ?, ?)`,
          [user.id, prompt, expected, today, 'scheduled', language],
          function (err) {
            if (err) console.error('Failed to insert scheduled assessment', err);
            else console.log('Scheduled assessment for user', user.id);
          }
        );
        await new Promise((r) => setTimeout(r, 250));
      } catch (err) {
        console.error('Error generating for user', user.id, err);
      }
    }
  });
}

function startScheduler() {
  // Schedule daily at 00:05 server time
  cron.schedule('5 0 * * *', () => {
    console.log('Running scheduled daily assessment generation');
    generateForAllUsersOnce().catch(err => console.error('generateForAllUsersOnce failed', err));
  }, {
    timezone: 'UTC'
  });

  // Also run once at startup (non-blocking)
  setTimeout(() => {
    console.log('Running initial daily generation check at startup');
    generateForAllUsersOnce().catch(err => console.error('generateForAllUsersOnce failed', err));
  }, 2000);
}

module.exports = { startScheduler };