import React, { useState, useRef } from 'react';

// Usage: include <RecordAssessment apiUrl="http://localhost:4000/api/assessments" />
export default function RecordAssessment({ apiUrl = '/api/assessments' }) {
  const [age, setAge] = useState('');
  const [level, setLevel] = useState('beginner');
  const [language, setLanguage] = useState('English');
  const [generatedPrompt, setGeneratedPrompt] = useState('');
  const [expected, setExpected] = useState('');

  const [recording, setRecording] = useState(false);
  const [audioUrl, setAudioUrl] = useState(null);
  const [transcript, setTranscript] = useState(null);
  const [score, setScore] = useState(null);
  const [status, setStatus] = useState('idle');
  const mediaRecorderRef = useRef(null);
  const recordedChunksRef = useRef([]);

  async function startRecording() {
    setTranscript(null);
    setScore(null);
    recordedChunksRef.current = [];
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mediaRecorder = new MediaRecorder(stream);
    mediaRecorderRef.current = mediaRecorder;
    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) recordedChunksRef.current.push(e.data);
    };
    mediaRecorder.onstop = () => {
      const blob = new Blob(recordedChunksRef.current, { type: 'audio/webm' });
      const url = URL.createObjectURL(blob);
      setAudioUrl(url);
    };
    mediaRecorder.start();
    setRecording(true);
    setStatus('recording');
  }

  function stopRecording() {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setRecording(false);
      setStatus('ready');
    }
  }

  function reset() {
    setAudioUrl(null);
    setTranscript(null);
    setScore(null);
    setStatus('idle');
    setGeneratedPrompt('');
    setExpected('');
    setAge('');
    setLevel('beginner');
  }

  async function submit() {
    if (!audioUrl) return;
    setStatus('uploading');
    setTranscript(null);
    setScore(null);

    const response = await fetch(audioUrl);
    const blob = await response.blob();
    const form = new FormData();
    form.append('audio', blob, 'response.webm');
    form.append('userId', 'user-local');
    form.append('promptId', 'prompt-local');
    if (generatedPrompt) form.append('promptText', generatedPrompt);
    if (expected) form.append('expected', expected);
    if (language) form.append('language', language);

    try {
      const res = await fetch(apiUrl, { method: 'POST', body: form });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Upload failed');
      setTranscript(data.transcript);
      setScore(data.score);
      setStatus('done');
    } catch (err) {
      console.error(err);
      setStatus('error');
    }
  }

  async function generateAssessment() {
    setStatus('generating');
    try {
      const res = await fetch(`${apiUrl}/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ age, level, language })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Generation failed');
      setGeneratedPrompt(data.prompt || '');
      setExpected(data.expected || '');
      setStatus('ready');
    } catch (err) {
      console.error(err);
      setStatus('error');
    }
  }

  return (
    <div>
      <div style={{ marginBottom: 10 }}>
        <label>Age: <input value={age} onChange={(e) => setAge(e.target.value)} placeholder="e.g. 8" /></label>
        <label style={{ marginLeft: 10 }}>
          Level:
          <select value={level} onChange={(e) => setLevel(e.target.value)}>
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>
        </label>
        <label style={{ marginLeft: 10 }}>
          Language:
          <select value={language} onChange={(e) => setLanguage(e.target.value)}>
            <option>English</option>
            <option>Spanish</option>
            <option>French</option>
            <option>German</option>
            <option>Portuguese</option>
            <option>Russian</option>
            <option>Hindi</option>
            <option>Chinese</option>
            <option>Japanese</option>
            <option>Korean</option>
            <option>Arabic</option>
            <option>Other</option>
          </select>
        </label>
        <button onClick={generateAssessment} style={{ marginLeft: 10 }}>Generate Assessment</button>
      </div>

      {generatedPrompt && (
        <div style={{ marginBottom: 10 }}>
          <h4>Generated Prompt</h4>
          <p>{generatedPrompt}</p>
          <h5>Expected Answer</h5>
          <p>{expected}</p>
        </div>
      )}

      <div>
        {!recording && <button onClick={startRecording}>Start</button>}
        {recording && <button onClick={stopRecording}>Stop</button>}
        <button onClick={reset}>Reset</button>
      </div>

      {audioUrl && (
        <div>
          <h4>Preview</h4>
          <audio controls src={audioUrl} />
        </div>
      )}

      <div>
        <button onClick={submit} disabled={!audioUrl || status === 'uploading'}>
          Submit for assessment
        </button>
      </div>

      <div>
        <p>Status: {status}</p>
        {transcript && (
          <div>
            <h4>Transcript</h4>
            <p>{transcript}</p>
          </div>
        )}
        {score !== null && (
          <div>
            <h4>Score</h4>
            <p>{score}</p>
          </div>
        )}
      </div>
    </div>
  );
}
