(async function(){
  const root = document.getElementById('root');
  const params = new URLSearchParams(location.search);
  const userId = params.get('user') || 'testuser';
  root.innerHTML = '<div class="p-4">Loading dashboard for <strong>'+userId+'</strong>...</div>';

  try {
    const res = await fetch('/api/dashboard/' + encodeURIComponent(userId));
    if (!res.ok) throw new Error('Failed to load dashboard: ' + res.status);
    const data = await res.json();

    // Build HTML similar to the React component
    const user = data.user || {};
    const recent = data.recentAssessments || [];

    const html = [];
    html.push('<div class="card mb-4"><div class="card-body bg-primary text-white"><h3 class="card-title">Welcome, '+(user.name||user.id)+'</h3><p class="card-text">AI Personalized Literacy Learning Dashboard</p></div></div>');

    html.push('<div class="metrics-grid mb-4">');
    html.push('<div class="metric-card"><h5>'+data.overallScore+'%</h5><div>Overall Score</div></div>');
    html.push('<div class="metric-card"><h5>'+data.currentLevel+'</h5><div>Current Level</div></div>');
    html.push('<div class="metric-card"><h5>'+data.progress+'%</h5><div>Progress</div></div>');
    html.push('<div class="metric-card"><h5>'+data.achievementPoints+'</h5><div>Achievement Points</div></div>');
    html.push('</div>');

    // Actions
    html.push('<div class="action-grid mb-4">');
    html.push('<div class="action-tile bg-white" onclick="location.href=\'/take-assessment\'"> <div class="mb-2"><i class="bi bi-file-earmark-text" style="font-size:28px"></i></div><h6>Take Assessment</h6></div>');
    html.push('<div class="action-tile bg-white" onclick="location.href=\'/learning\'"> <div class="mb-2"><i class="bi bi-book" style="font-size:28px"></i></div><h6>Learning Activities</h6></div>');
    html.push('<div class="action-tile bg-white" onclick="location.href=\'/voice-assessment\'"> <div class="mb-2"><i class="bi bi-mic" style="font-size:28px"></i></div><h6>Voice Assessment</h6></div>');
    html.push('<div class="action-tile bg-white" onclick="location.href=\'/report\'"> <div class="mb-2"><i class="bi bi-file-earmark-text-fill" style="font-size:28px"></i></div><h6>Performance Report</h6></div>');
    html.push('</div>');

    // Overall progress
    html.push('<div class="overall-progress-card mb-4"><h5>Overall Progress</h5><div class="progress" style="height:20px"><div class="progress-bar" role="progressbar" style="width:'+data.progress+'%">'+data.progress+'%</div></div></div>');

    // Today's assessment
    html.push('<div class="todays-assessment-card mb-4"><h5>Today\'s Assessment</h5>');
    if (data.todaysAssessment) {
      const t = data.todaysAssessment;
      html.push('<p><strong>Prompt:</strong> '+(t.prompt_text||t.prompt)+'</p>');
      html.push('<p><strong>Expected:</strong> '+(t.expected_text||t.expected)+'</p>');
      if (t.audio_path) {
        const fname = (t.audio_path || '').split(/[/\\\\]/).pop();
        if (fname) html.push('<div style="margin-top:8px"><audio controls src="/uploads/'+encodeURIComponent(fname)+'"></audio></div>');
      }
      html.push('<a class="btn btn-primary" href="/take-assessment">Go to assessment</a>');
    } else {
      html.push('<p>No assessment scheduled for today.</p>');
    }
    html.push('</div>');

    // Recent assessments
    html.push('<div class="recent-assessments-card mb-4"><h5>Recent Assessments</h5>');
    if (recent.length) {
      html.push('<div style="margin-bottom:8px"><button id="playAllBtn" class="btn btn-sm btn-outline-primary">Play all audio</button></div>');
      html.push('<div class="list-group">');
      recent.forEach((a, idx) => {
        const scoreDisplay = (a.report && a.report.overall_score) ? (a.report.overall_score + '%') : (a.score !== null ? Math.round(a.score*100)+'%' : 'N/A');
        html.push('<div class="list-group-item" data-idx="'+idx+'">');
        html.push('<div><div><strong>Prompt:</strong> '+(a.prompt||'')+'</div><div><strong>Transcript:</strong> '+(a.transcript||'-')+'</div>');
        if (a.audio_path) {
          const fname = (a.audio_path || '').split(/[/\\\\]/).pop();
          if (fname) html.push('<div style="margin-top:8px"><audio controls src="/uploads/'+encodeURIComponent(fname)+'"></audio></div>');
        }
        html.push('</div>');
        html.push('<div class="text-end"><div><strong>Score:</strong> '+scoreDisplay+'</div><div><small>'+a.status+'</small></div><div style="margin-top:8px"><button class="btn btn-sm btn-outline-success review-btn" data-id="'+a.id+'">Mark reviewed / Override</button></div></div>');
        html.push('</div>');
      });
      html.push('</div>');

      // small script to wire play all and review buttons
      html.push('<script>document.getElementById("playAllBtn").addEventListener("click", async function(){const items=document.querySelectorAll(".list-group-item");for(const it of items){const audio=it.querySelector("audio"); if(audio){ try{ await audio.play(); await new Promise(r=>audio.onended=r);}catch(e){ /* ignore */ } } }}); Array.from(document.querySelectorAll('.review-btn')).forEach(btn=>{btn.addEventListener('click', async function(){const id=this.dataset.id; const override=prompt('Optional: enter override overall score (0-100) or leave blank'); const feedback=prompt('Optional: enter reviewer feedback'); const payload={reviewed:true}; if(override!==null && override!=='') payload.override_score=Number(override); if(feedback) payload.reviewer_feedback=feedback; try{ const res=await fetch('/api/assessments/'+encodeURIComponent(id)+'/review',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}); if(!res.ok){ const txt=await res.text(); alert('Failed: '+txt); } else { alert('Marked reviewed'); location.reload(); } }catch(e){ alert('Failed: '+e.message); } }); });</script>');
    } else {
      html.push('<p>No recent assessments.</p>');
    }
    html.push('</div>');

    root.innerHTML = html.join('');

    // Add Bootstrap icons if missing
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = 'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css';
    document.head.appendChild(link);

  } catch (err) {
    root.innerHTML = '<div class="alert alert-danger">Error loading dashboard: '+err.message+'</div>';
  }
})();