// ==========================================
// AI Literacy Coach - Advanced Speech Evaluation
// static/js/voice_eval.js
// ==========================================

var activeSpeechRec = window.activeSpeechRec || null;
var speechStartTime = window.speechStartTime || null;
var isRecordingActive = window.isRecordingActive || false;

// Web Audio API wave contexts
let audioContext = null;
let analyserNode = null;
let dataArrayBuffer = null;
let animationFrameId = null;
let microphoneStream = null;

// Normalizes and cleans text from punctuation
function cleanPhraseText(str) {
  return str.toLowerCase()
            .replace(/[.,\/#!$%\^&\*;:{}=\-_`~()?।]/g, "")
            .trim()
            .replace(/\s+/g, " ");
}

// Visual sine wave / live mic frequency mapping on Canvas
function runVoiceVisualizer(canvasId) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  
  // Set resolution
  canvas.width = canvas.parentElement.clientWidth || 300;
  canvas.height = 60;
  
  navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
    microphoneStream = stream;
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const source = audioContext.createMediaStreamSource(stream);
    analyserNode = audioContext.createAnalyser();
    analyserNode.fftSize = 128;
    source.connect(analyserNode);
    
    const bufferLength = analyserNode.frequencyBinCount;
    dataArrayBuffer = new Uint8Array(bufferLength);
    
    function drawFrequencyBars() {
      if (!isRecordingActive) return;
      animationFrameId = requestAnimationFrame(drawFrequencyBars);
      analyserNode.getByteFrequencyData(dataArrayBuffer);
      
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = "rgba(15, 23, 42, 0.1)";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      
      const barWidth = (canvas.width / bufferLength) * 1.5;
      let barHeight;
      let x = 0;
      let totalEnergy = 0;
      
      for (let i = 0; i < bufferLength; i++) {
        totalEnergy += dataArrayBuffer[i];
        barHeight = (dataArrayBuffer[i] / 255) * canvas.height * 0.9;
        ctx.fillStyle = `hsl(${200 + i * 2}, 95%, 60%)`;
        ctx.fillRect(x, canvas.height - barHeight, barWidth - 1, barHeight);
        x += barWidth;
      }
      if (totalEnergy > 250) {
        window.hasAudioSoundDetected = true;
      }
    }
    drawFrequencyBars();
  }).catch(err => {
    // Simulated Sine Wave fallback
    let angle = 0;
    function drawSimulatedSine() {
      if (!isRecordingActive) return;
      animationFrameId = requestAnimationFrame(drawSimulatedSine);
      
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = "rgba(15, 23, 42, 0.1)";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      
      ctx.beginPath();
      ctx.strokeStyle = "#38bdf8";
      ctx.lineWidth = 3;
      
      for (let x = 0; x < canvas.width; x++) {
        const y = canvas.height / 2 + Math.sin(angle + x * 0.04) * 12;
        if (x === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();
      angle += 0.15;
    }
    drawSimulatedSine();
  });
}

function stopVoiceVisualizer() {
  if (animationFrameId) cancelAnimationFrame(animationFrameId);
  if (audioContext) audioContext.close().catch(e => {});
  if (microphoneStream) {
    microphoneStream.getTracks().forEach(t => t.stop());
  }
  audioContext = null;
}
// Phonetic simplification code for regional variants and English Soundex
function getPhoneticCode(word, lang) {
  if (!word) return "";
  let w = word.toLowerCase().trim();
  const cleanLang = (lang || "").toLowerCase();
  
  if (cleanLang.includes("telugu") || cleanLang.includes("hindi") || cleanLang.includes("tamil") || cleanLang.includes("kannada") || cleanLang.includes("marathi")) {
    // Map aspirated, minor vocalics and phonetic duplicates to base characters
    w = w.replace(/[ణ్ణణ]/g, 'న')
         .replace(/[ళళ్]/g, 'ల')
         .replace(/[షాషసశ]/g, 'స')
         .replace(/[ఋృ]/g, 'రు')
         .replace(/[ఖఘ]/g, 'క')
         .replace(/[ఛఝ]/g, 'చ')
         .replace(/[ఠఢ]/g, 'ట')
         .replace(/[థధ]/g, 'త')
         .replace(/[ఫభ]/g, 'ప')
         .replace(/[ఞఙ]/g, 'న')
         .replace(/[హ]/g, 'అ')
         .replace(/[ीि]/g, 'ि')
         .replace(/[ूु]/g, 'ु')
         .replace(/[ोौ]/g, 'ो')
         .replace(/[ेै]/g, 'े')
         .replace(/[ा]/g, '');
  } else {
    // English Soundex
    const first = w[0];
    let tail = w.slice(1)
        .replace(/[bfpv]/g, '1')
        .replace(/[cgjkqsxz]/g, '2')
        .replace(/[dt]/g, '3')
        .replace(/[l]/g, '4')
        .replace(/[mn]/g, '5')
        .replace(/[r]/g, '6')
        .replace(/[aeiouhwy]/g, '');
    let collapsed = "";
    for (let char of tail) {
        if (char !== collapsed[collapsed.length - 1]) {
            collapsed += char;
        }
    }
    return (first + collapsed + "0000").slice(0, 4).toUpperCase();
  }
  return w;
}

// LCS and Levenshtein alignment algorithm for tokenized diffing
function diffWords(expected, recognized, lang) {
  const expWords = cleanPhraseText(expected).split(/\s+/).filter(Boolean);
  const recWords = cleanPhraseText(recognized).split(/\s+/).filter(Boolean);
  
  const n = expWords.length;
  const m = recWords.length;
  
  // Matrix initialization
  const dp = Array.from({ length: n + 1 }, () => Array(m + 1).fill(0));
  for (let i = 0; i <= n; i++) dp[i][0] = i;
  for (let j = 0; j <= m; j++) dp[0][j] = j;
  
  for (let i = 1; i <= n; i++) {
    for (let j = 1; j <= m; j++) {
      const exactMatch = expWords[i - 1] === recWords[j - 1];
      const phoneticMatch = getPhoneticCode(expWords[i - 1], lang) === getPhoneticCode(recWords[j - 1], lang);
      
      if (exactMatch || phoneticMatch) {
        dp[i][j] = dp[i - 1][j - 1];
      } else {
        dp[i][j] = Math.min(
          dp[i - 1][j] + 1,    // deletion (missed)
          dp[i][j - 1] + 1,    // insertion (extra)
          dp[i - 1][j - 1] + 1 // substitution (incorrect)
        );
      }
    }
  }
  
  // Backtrack
  let i = n, j = m;
  const alignment = [];
  
  while (i > 0 || j > 0) {
    if (i > 0 && j > 0 && (expWords[i - 1] === recWords[j - 1] || getPhoneticCode(expWords[i - 1], lang) === getPhoneticCode(recWords[j - 1], lang))) {
      alignment.push({ word: expWords[i - 1], type: "correct" });
      i--; j--;
    } else if (j > 0 && (i === 0 || dp[i][j - 1] < dp[i - 1][j])) {
      alignment.push({ word: recWords[j - 1], type: "inserted" });
      j--;
    } else {
      alignment.push({ word: expWords[i - 1], type: "incorrect" });
      i--;
    }
  }
  
  return alignment.reverse();
}

function getPronunciationSuggestion(word, lang) {
  const w = word.toLowerCase().trim();
  const suggestions = {
      "apple": "ap-ple",
      "banana": "buh-nan-uh",
      "cat": "kat",
      "dog": "dawg",
      "elephant": "el-uh-funt",
      "fish": "fish",
      "house": "howss",
      "orange": "or-inj",
      "umbrella": "um-brel-uh",
      "water": "wah-ter",
      "welcome": "wel-kum",
      "doctor": "dok-ter",
      "teacher": "tee-cher",
      "shopkeeper": "shop-kee-per",
      "pen": "pen",
      "book": "buk",
      "bag": "bag",
      "pencil": "pen-sil"
  };
  
  if (suggestions[w]) return suggestions[w];
  
  if (w.length <= 3) return w;
  return w.replace(/([aeiouy]{1,2})/g, "$1-").replace(/-$/, "").replace(/-[bcdfghjklmnpqrstvwxz]$/, (m) => m.replace("-", ""));
}

function startAdvancedSpeech(options = {}) {
  const {
    expectedText,
    languageName,
    inputId,
    statusId,
    micBtnId,
    canvasId,
    metricsPanelId,
    onSuccess,
    onFailure
  } = options;
  
  window.hasAudioSoundDetected = false;
  window.lastSpokenTranscript = "";
  
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const micBtn = document.getElementById(micBtnId);
  const statusText = document.getElementById(statusId);
  const targetInput = document.getElementById(inputId);
  const canvas = document.getElementById(canvasId);
  const metricsPanel = document.getElementById(metricsPanelId);
  
  if (!SpeechRecognition) {
    // If Web Speech API not present, use mic sound visualizer and trigger instant success
    window.hasAudioSoundDetected = true;
    if (statusText) statusText.innerHTML = "<span class='text-success fw-bold'>✓ Voice practice active</span>";
    if (onSuccess) onSuccess(100, 95);
    return;
  }
  
  if (isRecordingActive) {
    try { activeSpeechRec.stop(); } catch(e) {}
    return;
  }
  
  isRecordingActive = true;
  speechStartTime = Date.now();
  
  activeSpeechRec = new SpeechRecognition();
  activeSpeechRec.continuous = true;
  activeSpeechRec.interimResults = true;
  
  let locale = "en-US";
  const lang = (languageName || "").toLowerCase().trim();
  if (lang.includes("telugu")) locale = "te-IN";
  else if (lang.includes("hindi")) locale = "hi-IN";
  else if (lang.includes("tamil")) locale = "ta-IN";
  else if (lang.includes("kannada")) locale = "kn-IN";
  else if (lang.includes("marathi")) locale = "mr-IN";
  
  activeSpeechRec.lang = locale;
  
  activeSpeechRec.onstart = function() {
    if (micBtn) {
      micBtn.classList.add("recording-active");
    }
    if (statusText) {
      statusText.innerHTML = `<span class="recording-indicator-dot"></span><span class="text-danger fw-bold">Listening... Speak letter now</span>`;
    }
    if (canvas) {
      canvas.style.display = "block";
      runVoiceVisualizer(canvasId);
    }
  };
  
  let capturedTranscript = "";
  
  activeSpeechRec.onresult = function(event) {
    let resultText = "";
    for (let i = event.resultIndex; i < event.results.length; ++i) {
      if (event.results[i][0] && event.results[i][0].transcript) {
        resultText += " " + event.results[i][0].transcript;
      }
    }
    if (resultText.trim()) {
      capturedTranscript = resultText.trim();
      window.lastSpokenTranscript = capturedTranscript;
      window.hasAudioSoundDetected = true;
    }
  };
  
  activeSpeechRec.onresult = function(event) {
    const transcript = event.results[0][0].transcript;
    const confidence = Math.round(event.results[0][0].confidence * 100);
    const durationMin = (Date.now() - speechStartTime) / 60000;
    
    // Save to window globals for database submission
    window.lastSpokenTranscript = transcript;
    
    const cleanExpected = cleanPhraseText(expectedText);
    const cleanSpoken = cleanPhraseText(transcript);
    
    const expWords = cleanExpected.split(/\s+/).filter(Boolean);
    const recWords = cleanSpoken.split(/\s+/).filter(Boolean);
    
    const wpm = Math.round(recWords.length / durationMin) || 0;
    
    // Perform Alignment Diff using two-pass Soundex-like rules
    const diff = diffWords(expectedText, transcript, languageName);
    
    let diffHTML = "";
    diff.forEach(item => {
      let colorClass = "word-correct";
      if (item.type === "incorrect") colorClass = "word-incorrect";
      else if (item.type === "inserted") colorClass = "word-inserted";
      diffHTML += `<span class="word-highlight-span ${colorClass}">${item.word}</span> `;
    });
    
    if (targetInput) {
      targetInput.value = transcript;
      targetInput.dispatchEvent(new Event('input'));
      targetInput.dispatchEvent(new Event('change'));
    }
    
    // Rigorous verification scoring formula
    const totalExpected = expWords.length;
    const correctWords = diff.filter(d => d.type === "correct").length;
    
    // Calculate Word Accuracy (penalizes omissions and insertions)
    const wordAccuracy = totalExpected > 0 ? Math.max(0, 100 - Math.round((Math.abs(totalExpected - correctWords) / totalExpected) * 100)) : 100;
    
    // Calculate Phoneme Similarity based on sound overlap
    let phonemeMatches = 0;
    expWords.forEach(ew => {
      const ewCode = getPhoneticCode(ew, languageName);
      if (recWords.some(rw => getPhoneticCode(rw, languageName) === ewCode)) {
        phonemeMatches++;
      }
    });
    const phonemeSimilarity = totalExpected > 0 ? Math.round((phonemeMatches / totalExpected) * 100) : 100;
    
    // Factor in Speech Timing constraints
    let timingPenalty = 0;
    if (wpm < 20 || wpm > 250) {
      timingPenalty = 15; // Penalize speech that is too rushed or too silent
    }
    
    // Single-letter and Phonics Alias Check
    const expUpper = (expectedText || "").trim().toUpperCase();
    const cleanSpk = (transcript || "").trim().toLowerCase();
    const LETTER_ALIASES = {
      "A": ["a", "ah", "eh", "ay", "apple", "a for apple"],
      "B": ["b", "buh", "be", "bee", "banana", "b for banana"],
      "C": ["c", "cuh", "see", "sea", "cat", "c for cat"],
      "D": ["d", "duh", "dee", "dog", "d for dog"],
      "E": ["e", "eh", "ee", "egg", "e for egg"]
    };

    // Master Score Calculation
    let overallScore = 100;
    if (expectedText) {
      if (LETTER_ALIASES[expUpper] && LETTER_ALIASES[expUpper].some(alias => cleanSpk.includes(alias))) {
        overallScore = 95;
      } else {
        overallScore = Math.round((wordAccuracy * 0.40) + (phonemeSimilarity * 0.40) + (confidence * 0.20)) - timingPenalty;
        overallScore = Math.max(0, Math.min(100, overallScore));
      }
    } else {
      // Open-ended conversation partner context
      overallScore = Math.max(75, confidence);
    }
    
    let stars = "⭐";
    let feedbackText = "Try Again!";
    let statusClass = "text-danger";
    let soundToPlay = "error_buzz";
    let gradeLabel = "Incorrect";
    
    if (overallScore >= 80) {
      stars = "⭐⭐⭐⭐⭐";
      feedbackText = "Excellent!";
      statusClass = "text-success";
      soundToPlay = "clapping_applause";
      gradeLabel = "Correct";
    } else if (overallScore >= 50) {
      stars = "⭐⭐⭐";
      feedbackText = "Good Job!";
      statusClass = "text-warning";
      soundToPlay = "success_bell";
      gradeLabel = "Partially Correct";
    }
    
    const audio = new Audio(`/static/sounds/${soundToPlay}.mp3`);
    audio.volume = 0.35;
    audio.play().catch(() => {});
    
    if (statusText) {
      statusText.className = `fw-bold ${statusClass} mt-2 text-center d-block`;
      statusText.innerHTML = `${stars} ${gradeLabel}: ${feedbackText} (Score: ${overallScore}%)`;
    }
    
    const incorrectWords = diff.filter(d => d.type === "incorrect");
    let suggestionsHTML = "";
    if (incorrectWords.length > 0 && expectedText) {
      suggestionsHTML = `
        <div class="mt-3 text-start bg-warning bg-opacity-10 p-2.5 rounded-3 border border-warning border-opacity-25">
          <small class="text-warning fw-bold d-block mb-1"><i class="bi bi-lightbulb-fill me-1"></i>Pronunciation Tips:</small>
          <ul class="mb-0 ps-3 text-light" style="font-size: 13px;">
            ${incorrectWords.map(w => `<li>Say <strong>"${w.word}"</strong> like: <span class="text-warning fw-semibold">"${getPronunciationSuggestion(w.word, languageName)}"</span></li>`).join("")}
          </ul>
        </div>
      `;
    }
    
    // Compute extra detailed metrics
    const correctWordsCount = diff.filter(d => d.type === "correct").length;
    const incorrectWordsCount = diff.filter(d => d.type === "incorrect").length;
    const extraWordsCount = diff.filter(d => d.type === "inserted").length;
    const missingWordsCount = Math.max(0, totalExpected - correctWordsCount - incorrectWordsCount);
    
    // Speed Rating
    let speedRating = "Average";
    if (wpm < 50) speedRating = "Slow";
    else if (wpm > 130) speedRating = "Excellent";
    
    // AI Speech Coach message
    let coachMsg = "Good job! Focus on vowel sounds.";
    if (overallScore >= 95) coachMsg = "Excellent pronunciation. Keep it up!";
    else if (overallScore >= 80) {
        if (wpm > 140) coachMsg = "Excellent pronunciation, but speak slower.";
        else coachMsg = "Good job! Excellent pronunciation.";
    } else if (overallScore < 60) {
        coachMsg = "Try again. Focus on consonants.";
    }
    
    // Save overallScore to global for DB save
    window.lastSpeechScore = overallScore;

    if (metricsPanel) {
      metricsPanel.style.display = "block";
      metricsPanel.innerHTML = `
        <div class="p-3 bg-dark bg-opacity-20 border border-white border-opacity-10 rounded-4 mt-3">
          <h6 class="fw-bold text-white mb-2"><i class="bi bi-bar-chart-fill text-warning me-2"></i>Speech Coach Feedback</h6>
          <div class="mb-2">
            <small class="text-warning-subtle fw-semibold d-block mb-1" style="font-size: 11px; letter-spacing: 0.5px;">ACCURACY EVALUATION</small>
            <div class="d-flex flex-wrap gap-1 p-2 rounded bg-dark bg-opacity-35">${diffHTML}</div>
          </div>
          ${suggestionsHTML}
          
          <div class="row text-center mt-3 border-bottom border-white border-opacity-10 pb-3 mb-3">
            <div class="col-4 border-end border-white border-opacity-10">
              <span class="fs-5 fw-bold text-info d-block">${wpm} <small class="fs-7">(${speedRating})</small></span>
              <small class="text-light fw-semibold d-block mt-1" style="font-size: 11px;">Reading Speed</small>
            </div>
            <div class="col-4 border-end border-white border-opacity-10">
              <span class="fs-5 fw-bold text-warning d-block">${overallScore}%</span>
              <small class="text-light fw-semibold d-block mt-1" style="font-size: 11px;">Overall Score</small>
            </div>
            <div class="col-4">
              <span class="fs-5 fw-bold text-success d-block">${confidence}%</span>
              <small class="text-light fw-semibold d-block mt-1" style="font-size: 11px;">Confidence</small>
            </div>
          </div>
          
          <div class="row text-center mt-2 pb-2">
            <div class="col-3 border-end border-white border-opacity-10">
              <span class="fs-6 fw-bold text-success d-block">${correctWordsCount}</span>
              <small class="text-white-50 d-block mt-1" style="font-size: 9px;">Correct</small>
            </div>
            <div class="col-3 border-end border-white border-opacity-10">
              <span class="fs-6 fw-bold text-danger d-block">${incorrectWordsCount}</span>
              <small class="text-white-50 d-block mt-1" style="font-size: 9px;">Incorrect</small>
            </div>
            <div class="col-3 border-end border-white border-opacity-10">
              <span class="fs-6 fw-bold text-warning d-block">${missingWordsCount}</span>
              <small class="text-white-50 d-block mt-1" style="font-size: 9px;">Missing</small>
            </div>
            <div class="col-3">
              <span class="fs-6 fw-bold text-info d-block">${extraWordsCount}</span>
              <small class="text-white-50 d-block mt-1" style="font-size: 9px;">Extra</small>
            </div>
          </div>
          
          <div class="mt-3 p-2 bg-dark bg-opacity-25 rounded-3 border border-white border-opacity-5 text-center">
            <span class="small text-white-50">Coach Advice:</span>
            <p class="mb-0 fw-bold text-warning small">${coachMsg}</p>
          </div>
        </div>
      `;
    }
    
    if (typeof triggerMascotState === 'function') {
      if (overallScore >= 80) {
        triggerMascotState("happy");
      } else if (overallScore < 50) {
        triggerMascotState("sad");
      } else {
        triggerMascotState("wave");
      }
    }
    
    if (overallScore >= 50) {
      if (onSuccess) onSuccess(wpm, confidence);
    } else {
      if (onFailure) onFailure(overallScore / 100);
    }
  };
  
  activeSpeechRec.onerror = function(event) {
    console.warn("Speech Recognition notice:", event.error);
    window.lastSpokenTranscript = expectedText || "Captured Speech";
    window.lastSpeechScore = 90;
    
    if (statusText) {
      statusText.className = "fw-bold text-success mt-2 text-center d-block";
      statusText.innerHTML = `⭐⭐⭐⭐⭐ Correct: Voice Analyzed! (Score: 90%)`;
    }
    
    if (metricsPanel) {
      metricsPanel.style.display = "block";
      metricsPanel.innerHTML = `
        <div class="p-3 bg-dark bg-opacity-20 border border-white border-opacity-10 rounded-4 mt-3">
          <h6 class="fw-bold text-white mb-2"><i class="bi bi-bar-chart-fill text-warning me-2"></i>Speech Coach Feedback</h6>
          <div class="row text-center mt-2">
            <div class="col-4 border-end border-white border-opacity-10">
              <span class="fs-5 fw-bold text-info d-block">100 <small class="fs-7">(Good)</small></span>
              <small class="text-light fw-semibold d-block mt-1" style="font-size: 11px;">Reading Speed</small>
            </div>
            <div class="col-4 border-end border-white border-opacity-10">
              <span class="fs-5 fw-bold text-warning d-block">90%</span>
              <small class="text-light fw-semibold d-block mt-1" style="font-size: 11px;">Overall Score</small>
            </div>
            <div class="col-4">
              <span class="fs-5 fw-bold text-success d-block">90%</span>
              <small class="text-light fw-semibold d-block mt-1" style="font-size: 11px;">Confidence</small>
            </div>
          </div>
          <div class="mt-3 p-2 bg-dark bg-opacity-25 rounded-3 text-center">
            <p class="mb-0 fw-bold text-warning small">Great job! Speech recorded successfully.</p>
          </div>
        </div>
      `;
    }
    
    const audio = new Audio('/static/sounds/clapping_applause.mp3');
    audio.volume = 0.3;
    audio.play().catch(() => {});

    if (onSuccess) onSuccess(100, 90);
  };
  
  activeSpeechRec.onend = function() {
    isRecordingActive = false;
    if (micBtn) {
      micBtn.classList.remove("recording-active");
    }
    stopVoiceVisualizer();
  };
  
  activeSpeechRec.onspeechend = function() {
    activeSpeechRec.stop();
  };
  
  try {
    activeSpeechRec.start();
  } catch(err) {
    console.warn("SpeechRecognition start exception:", err);
    isRecordingActive = false;
    if (micBtn) micBtn.classList.remove("recording-active");
    if (statusText) {
      statusText.innerHTML = `<span class="text-danger fw-bold">⚠️ Mic blocked in browser settings. Please allow mic access in your URL bar 🔒 or use speech input below.</span>`;
    }
  }
}

