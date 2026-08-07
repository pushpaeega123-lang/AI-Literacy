(async function(){
  const root = document.getElementById('queue');
  async function load() {
    root.innerHTML = 'Loading...';
    try {
      const res = await fetch('/api/review/queue');
      if (!res.ok) throw new Error('Failed to load queue');
      const items = await res.json();
      if (!items.length) { root.innerHTML = '<p>No items in the review queue.</p>'; return; }
      const container = document.createElement('div');
      container.className = 'list-group';
      items.forEach(it => {
        const el = document.createElement('div');
        el.className = 'list-group-item d-flex justify-content-between align-items-start';
        el.innerHTML = `<div><div><strong>User:</strong> ${it.user_id || ''}</div><div><strong>Prompt:</strong> ${it.prompt || ''}</div><div><strong>Transcript:</strong> ${it.transcript || '-'}</div></div>`;
        const right = document.createElement('div');
        right.style.textAlign = 'right';
        const score = document.createElement('div'); score.innerHTML = `<strong>Score:</strong> ${it.report && it.report.overall_score ? it.report.overall_score+'%' : (it.score ? Math.round(it.score*100)+'%' : 'N/A')}`;
        const btns = document.createElement('div'); btns.style.marginTop='8px';
        const audioBtn = document.createElement('button'); audioBtn.className='btn btn-sm btn-outline-primary me-2'; audioBtn.textContent='Play';
        if (it.audio_path) {
          const fname = (it.audio_path||'').split(/[/\\\\]/).pop();
          const src = fname ? '/uploads/'+encodeURIComponent(fname) : null;
          audioBtn.addEventListener('click', () => { const a = new Audio(src); a.play().catch(()=>{}); });
        } else { audioBtn.disabled=true; }
        const reviewBtn = document.createElement('button'); reviewBtn.className='btn btn-sm btn-outline-success'; reviewBtn.textContent='Review';
        reviewBtn.addEventListener('click', () => openModal(it));
        btns.appendChild(audioBtn); btns.appendChild(reviewBtn);
        right.appendChild(score); right.appendChild(btns);
        el.appendChild(right);
        container.appendChild(el);
      });
      root.innerHTML = '';
      root.appendChild(container);
    } catch (e) {
      root.innerHTML = '<div class="alert alert-danger">Failed to load queue: '+e.message+'</div>';
    }
  }

  let activeItem = null;
  const modalEl = document.getElementById('reviewModal');
  const bsModal = new bootstrap.Modal(modalEl);
  document.getElementById('modal-save').addEventListener('click', async () => {
    if (!activeItem) return;
    const override = document.getElementById('modal-override').value;
    const feedback = document.getElementById('modal-feedback').value;
    const payload = { reviewed: true };
    if (override !== '') payload.override_score = Number(override);
    if (feedback) payload.reviewer_feedback = feedback;
    try {
      const res = await fetch('/api/assessments/'+encodeURIComponent(activeItem.id)+'/review', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) });
      if (!res.ok) { const txt = await res.text(); alert('Failed: '+txt); return; }
      bsModal.hide();
      load();
    } catch (e) { alert('Failed: '+e.message); }
  });

  function openModal(item) {
    activeItem = item;
    document.getElementById('modal-body-content').innerHTML = `<div><strong>User:</strong> ${item.user_id||''}</div><div><strong>Prompt:</strong> ${item.prompt||''}</div><div><strong>Transcript:</strong> ${item.transcript||''}</div>` + (item.audio_path ? `<div style="margin-top:8px"><audio controls src="/uploads/${encodeURIComponent((item.audio_path||'').split(/[/\\\\]/).pop())}"></audio></div>` : '');
    document.getElementById('modal-override').value='';
    document.getElementById('modal-feedback').value='';
    bsModal.show();
  }

  load();
})();