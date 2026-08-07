// ==========================================
// AI Literacy Coach - Tracing Canvas Checker
// static/js/tracing.js
// ==========================================

function initDrawingCanvas(canvasId) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  
  canvas.width = canvas.offsetWidth || 300;
  canvas.height = canvas.offsetHeight || 200;
  
  const ctx = canvas.getContext('2d');
  ctx.strokeStyle = '#2563eb';
  ctx.lineWidth = 12;
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';
  
  let drawing = false;
  
  function getPos(e) {
    const rect = canvas.getBoundingClientRect();
    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    const clientY = e.touches ? e.touches[0].clientY : e.clientY;
    return {
      x: clientX - rect.left,
      y: clientY - rect.top
    };
  }
  
  canvas.addEventListener('mousedown', (e) => {
    drawing = true;
    const pos = getPos(e);
    ctx.beginPath();
    ctx.moveTo(pos.x, pos.y);
  });
  
  canvas.addEventListener('mousemove', (e) => {
    if (!drawing) return;
    const pos = getPos(e);
    ctx.lineTo(pos.x, pos.y);
    ctx.stroke();
  });
  
  canvas.addEventListener('mouseup', () => { drawing = false; });
  canvas.addEventListener('mouseleave', () => { drawing = false; });
  
  // Touch support
  canvas.addEventListener('touchstart', (e) => {
    e.preventDefault();
    drawing = true;
    const pos = getPos(e);
    ctx.beginPath();
    ctx.moveTo(pos.x, pos.y);
  });
  
  canvas.addEventListener('touchmove', (e) => {
    e.preventDefault();
    if (!drawing) return;
    const pos = getPos(e);
    ctx.lineTo(pos.x, pos.y);
    ctx.stroke();
  });
  
  canvas.addEventListener('touchend', () => { drawing = false; });
}

function clearCanvas(canvasId) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);
}

function checkDrawing(canvasId, targetText, name) {
  const score = evaluateDrawingScore(canvasId, targetText);
  const feedbackContainer = document.getElementById(`feedback_${name}`);
  const inputElement = document.getElementById(`input_${name}`);
  
  fetch('/api/trace/verify', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ score: score })
  })
  .then(res => res.json())
  .then(data => {
    if (data.status === 'success') {
      if (inputElement) {
        inputElement.value = score >= 50 ? "Pass" : "";
        inputElement.dispatchEvent(new Event('change'));
      }
      
      let badgeClass = "bg-warning";
      if (score >= 80) badgeClass = "bg-success";
      else if (score < 50) badgeClass = "bg-danger";
      
      if (feedbackContainer) {
        feedbackContainer.innerHTML = `
          <div class="mt-2 p-2 rounded ${badgeClass} text-white fw-bold">
             ${data.stars} ${data.feedback} (Match: ${score}%)
          </div>
        `;
      }
      
      // Play synthesized audio chimes offline
      if (typeof playSynthesizedSound === 'function') {
        playSynthesizedSound(score >= 50 ? "success" : "error");
      }
      
      // Hook completion btn if inside lesson task
      const completeBtn = document.getElementById("completeBtn");
      if (completeBtn) {
        if (score >= 50) {
          if (typeof enableCompletion === 'function') enableCompletion();
        } else {
          if (typeof disableCompletion === 'function') disableCompletion("Try again to complete.");
        }
      }
    }
  });
}

function evaluateDrawingScore(canvasId, targetText) {
  const canvas = document.getElementById(canvasId);
  const ctx = canvas.getContext('2d');
  
  const tempCanvas = document.createElement('canvas');
  tempCanvas.width = canvas.width;
  tempCanvas.height = canvas.height;
  const tempCtx = tempCanvas.getContext('2d');
  
  // Render guides (normal weight instead of bold to match drawing line width)
  tempCtx.fillStyle = '#000000';
  tempCtx.font = '80px Poppins, "Noto Sans Telugu", "Noto Sans Devanagari", sans-serif';
  tempCtx.textAlign = 'center';
  tempCtx.textBaseline = 'middle';
  tempCtx.fillText(targetText, tempCanvas.width / 2, tempCanvas.height / 2);
  
  const userImg = ctx.getImageData(0, 0, canvas.width, canvas.height);
  const maskImg = tempCtx.getImageData(0, 0, tempCanvas.width, tempCanvas.height);
  
  let hits = 0;
  let misses = 0;
  let maskTotal = 0;
  
  for (let i = 0; i < maskImg.data.length; i += 4) {
    const maskAlpha = maskImg.data[i + 3];
    const userAlpha = userImg.data[i + 3];
    
    if (maskAlpha > 15) {
      maskTotal++;
      if (userAlpha > 15) {
        hits++;
      }
    } else {
      if (userAlpha > 15) {
        misses++;
      }
    }
  }
  
  if (maskTotal === 0) return 0;
  
  // Calculate raw hit percentage
  let rawScore = (hits / maskTotal) * 100;
  
  // Minor penalty for drawing outside target template
  let penalty = 0;
  if (misses > hits) {
    penalty = Math.round((misses / maskTotal) * 15);
  }
  
  // Generous scaling mapping to make score output natural and high when tracing matches
  let score = 0;
  if (rawScore >= 45) {
    score = 92 + Math.min(8, Math.round((rawScore - 45) * 0.4));
  } else if (rawScore >= 25) {
    score = 75 + Math.round((rawScore - 25) * (17 / 20));
  } else if (rawScore >= 10) {
    score = 50 + Math.round((rawScore - 10) * (25 / 15));
  } else {
    score = Math.round(rawScore * 5);
  }
  
  score = Math.max(0, score - penalty);
  return Math.min(100, Math.max(0, score));
}
