import React, { useEffect, useState } from 'react';
import './dashboard.css';

// Requires Bootstrap CSS in the host app
// Usage: <Dashboard apiUrl="http://localhost:4000/api/dashboard" userId="user-local" />
export default function Dashboard({ apiUrl = '/api/dashboard', userId = 'user-local' }) {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  const [playingIndex, setPlayingIndex] = useState(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const res = await fetch(`${apiUrl}/${userId}`);
        const json = await res.json();
        if (!res.ok) throw new Error(json.error || 'Failed to load');
        setData(json);
      } catch (err) {
        setError(err.message || String(err));
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [apiUrl, userId]);

  // Play-all queue implementation for reviewer workflow
  async function handlePlayAll() {
    if (!data || !data.recentAssessments) return;
    for (let i = 0; i < data.recentAssessments.length; i++) {
      const a = data.recentAssessments[i];
      if (!a.audio_path) continue;
      const filename = (a.audio_path || '').split(/[/\\\\]/).pop();
      if (!filename) continue;
      const src = `/uploads/${filename}`;
      setPlayingIndex(i);
      await playAudio(src);
    }
    setPlayingIndex(null);
  }

  function playAudio(src) {
    return new Promise((resolve) => {
      const audio = new Audio(src);
      audio.play().catch(() => resolve());
      audio.onended = () => resolve();
      audio.onerror = () => resolve();
    });
  }

  async function markReviewed(id) {
    const override = prompt('Optional: enter override overall score (0-100) or leave blank');
    const reviewer_feedback = prompt('Optional: enter reviewer feedback');
    const payload = { reviewed: true };
    if (override !== null && override !== '') payload.override_score = Number(override);
    if (reviewer_feedback) payload.reviewer_feedback = reviewer_feedback;

    try {
      const res = await fetch(`/api/assessments/${id}/review`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
      const json = await res.json();
      if (!res.ok) throw new Error(json.error || 'Failed to mark reviewed');
      // refresh data
      const r = await fetch(`${apiUrl}/${userId}`);
      const refreshed = await r.json();
      setData(refreshed);
      alert('Marked reviewed');
    } catch (err) {
      alert('Failed to mark reviewed: ' + err.message);
    }
  }

  if (loading) return <div className="p-4">Loading dashboard...</div>;
  if (error) return <div className="p-4 text-danger">Error: {error}</div>;

  const user = data.user || {};

  return (
    <div className="container mt-4">
      <div className="card mb-4">
        <div className="card-body bg-primary text-white">
          <h3 className="card-title">Welcome, {user.name || user.id}</h3>
          <p className="card-text">AI Personalized Literacy Learning Dashboard</p>
        </div>
      </div>

      <div className="row mb-4">
        <div className="col-md-3 mb-3">
          <div className="card p-3 text-center">
            <h5>{data.overallScore}%</h5>
            <div>Overall Score</div>
          </div>
        </div>
        <div className="col-md-3 mb-3">
          <div className="card p-3 text-center">
            <h5>{data.currentLevel}</h5>
            <div>Current Level</div>
          </div>
        </div>
        <div className="col-md-3 mb-3">
          <div className="card p-3 text-center">
            <h5>{data.progress}%</h5>
            <div>Progress</div>
          </div>
        </div>
        <div className="col-md-3 mb-3">
          <div className="card p-3 text-center">
            <h5>{data.achievementPoints}</h5>
            <div>Achievement Points</div>
          </div>
        </div>
      </div>

      {/* Mentor workflow removed as requested */}

      <div className="row mb-4">
        <div className="col-md-3 mb-3">
          <div className="card text-center p-4" style={{ cursor: 'pointer' }} onClick={() => window.location.href = '/take-assessment'}>
            <div className="mb-2"><i className="bi bi-file-earmark-text" style={{ fontSize: 28 }} /></div>
            <h6>Take Assessment</h6>
          </div>
        </div>
        <div className="col-md-3 mb-3">
          <div className="card text-center p-4" style={{ cursor: 'pointer' }} onClick={() => window.location.href = '/learning'}>
            <div className="mb-2"><i className="bi bi-book" style={{ fontSize: 28 }} /></div>
            <h6>Learning Activities</h6>
          </div>
        </div>
        <div className="col-md-3 mb-3">
          <div className="card text-center p-4" style={{ cursor: 'pointer' }} onClick={() => window.location.href = '/voice-assessment'}>
            <div className="mb-2"><i className="bi bi-mic" style={{ fontSize: 28 }} /></div>
            <h6>Voice Assessment</h6>
          </div>
        </div>
        <div className="col-md-3 mb-3">
          <div className="card text-center p-4" style={{ cursor: 'pointer' }} onClick={() => window.location.href = '/report'}>
            <div className="mb-2"><i className="bi bi-file-earmark-text-fill" style={{ fontSize: 28 }} /></div>
            <h6>Performance Report</h6>
          </div>
        </div>
      </div>

      <div className="card mb-4">
        <div className="card-body">
          <h5>Overall Progress</h5>
          <div className="progress" style={{ height: 20 }}>
            <div className="progress-bar" role="progressbar" style={{ width: `${data.progress}%` }} aria-valuenow={data.progress} aria-valuemin="0" aria-valuemax="100">{data.progress}%</div>
          </div>
        </div>
      </div>

      <div className="card mb-4">
        <div className="card-body">
          <h5>Today's Assessment</h5>
          {data.todaysAssessment ? (
            <div>
              <p><strong>Prompt:</strong> {data.todaysAssessment.prompt_text || data.todaysAssessment.prompt}</p>
              <p><strong>Expected:</strong> {data.todaysAssessment.expected_text || data.todaysAssessment.expected}</p>
              {data.todaysAssessment.audio_path && (() => {
                const filename = (data.todaysAssessment.audio_path || '').split(/[/\\\\]/).pop();
                const src = filename ? `/uploads/${filename}` : null;
                return src ? <div style={{ marginTop: 8 }}><audio controls src={src} /></div> : null;
              })()
              }
              <a className="btn btn-primary" href="/take-assessment">Go to assessment</a>
            </div>
          ) : (
            <p>No assessment scheduled for today.</p>
          )}
        </div>
      </div>

      <div className="card mb-4">
        <div className="card-body">
          <h5>Recent Assessments</h5>
          <div style={{ marginBottom: 8 }}>
            <button className="btn btn-sm btn-outline-primary" onClick={handlePlayAll}>Play all audio</button>
          </div>

          {data.recentAssessments && data.recentAssessments.length > 0 ? (
            <div className="list-group">
              {data.recentAssessments.map((a, idx) => (
                <div key={a.id} className={`list-group-item ${playingIndex === idx ? 'active' : ''}`}>
                  <div className="d-flex justify-content-between">
                    <div>
                      <div><strong>Prompt:</strong> {a.prompt}</div>
                      <div><strong>Transcript:</strong> {a.transcript || '-'} </div>
                      {a.audio_path && (
                        (() => {
                          const filename = (a.audio_path || '').split(/[/\\\\]/).pop();
                          const src = filename ? `/uploads/${filename}` : null;
                          return src ? <div style={{ marginTop: 8 }}><audio controls src={src} /></div> : null;
                        })()
                      )}
                    </div>
                    <div className="text-right">
                      <div><strong>Score:</strong> {a.score !== null ? Math.round(a.score * 100) + '%' : (a.report && a.report.overall_score ? a.report.overall_score + '%' : 'N/A')}</div>
                      <div><small>{a.status}</small></div>
                      <div style={{ marginTop: 8 }}>
                        <button className="btn btn-sm btn-outline-success" onClick={() => markReviewed(a.id)}>Mark reviewed / Override</button>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p>No recent assessments.</p>
          )}
        </div>
      </div>
    </div>
  );
}
