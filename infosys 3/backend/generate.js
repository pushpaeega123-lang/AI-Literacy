const fetch = require('node-fetch');

async function generatePrompt({ age, level, language = 'English' } = {}) {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) throw new Error('OPENAI_API_KEY not set in environment');

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
    throw new Error(`OpenAI generate error: ${resp.status} ${txt}`);
  }

  const data = await resp.json();
  const content = data.choices && data.choices[0] && data.choices[0].message && data.choices[0].message.content;
  if (!content) throw new Error('No content from OpenAI');

  try {
    const parsed = JSON.parse(content);
    return { prompt: parsed.prompt || '', expected: parsed.expected || '' };
  } catch (e) {
    const m = content.match(/\{[\s\S]*\}/);
    if (m) {
      try {
        const parsed2 = JSON.parse(m[0]);
        return { prompt: parsed2.prompt || '', expected: parsed2.expected || '' };
      } catch (e2) {
        // fall through
      }
    }
    // Fallback: return raw text as prompt
    return { prompt: content.trim(), expected: '' };
  }
}

module.exports = { generatePrompt };