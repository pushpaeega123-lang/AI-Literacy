// ==========================================
// AI Literacy Coach - Mascot Lumi
// static/js/mascot.js
// ==========================================

const MASCOT_ACC_COINS = {
  "crown": 50,
  "glasses": 30,
  "hat": 40
};

// Check unlocked accessories from session/local storage
function getUnlockedAccessories() {
  try {
    return JSON.parse(localStorage.getItem("lumi_unlocked_accessories") || '["default"]');
  } catch (e) {
    return ["default"];
  }
}

function getActiveAccessory() {
  return localStorage.getItem("lumi_active_accessory") || "default";
}

function unlockAccessory(item, cost, userCoins, onSuccess, onFailure) {
  const unlocked = getUnlockedAccessories();
  if (unlocked.includes(item)) {
    onFailure("Already unlocked!");
    return;
  }
  if (userCoins < cost) {
    onFailure("Not enough coins!");
    return;
  }
  
  // Save
  unlocked.push(item);
  localStorage.setItem("lumi_unlocked_accessories", JSON.stringify(unlocked));
  localStorage.setItem("lumi_active_accessory", item);
  
  onSuccess();
}

function getMascotSVG(state = "normal") {
  const activeAcc = getActiveAccessory();
  
  // Eye paths depending on state
  let eyeLeft = `<ellipse cx="85" cy="95" rx="8" ry="12" fill="#00f0ff" filter="drop-shadow(0 0 4px #00f0ff)" />`;
  let eyeRight = `<ellipse cx="115" cy="95" rx="8" ry="12" fill="#00f0ff" filter="drop-shadow(0 0 4px #00f0ff)" />`;
  let mouth = `<path d="M 92 110 Q 100 116 108 110" stroke="#00f0ff" stroke-width="3" fill="none" stroke-linecap="round" filter="drop-shadow(0 0 3px #00f0ff)" />`;
  let expressionClass = "lumi-normal";
  let accessoriesSVG = "";
  
  // Custom accessories
  if (activeAcc === "crown") {
    accessoriesSVG = `
      <!-- Gold Crown -->
      <path d="M 82 45 L 87 25 L 100 37 L 113 25 L 118 45 Z" fill="#ffd700" stroke="#b8860b" stroke-width="2" />
      <circle cx="82" cy="45" r="2.5" fill="#ff0000" />
      <circle cx="87" cy="25" r="2.5" fill="#0000ff" />
      <circle cx="100" cy="37" r="2.5" fill="#00ff00" />
      <circle cx="113" cy="25" r="2.5" fill="#0000ff" />
      <circle cx="118" cy="45" r="2.5" fill="#ff0000" />
    `;
  } else if (activeAcc === "glasses") {
    accessoriesSVG = `
      <!-- Cool Sunglasses -->
      <rect x="73" y="87" width="23" height="16" rx="4" fill="#111111" opacity="0.9" stroke="#ff007f" stroke-width="2" />
      <rect x="104" y="87" width="23" height="16" rx="4" fill="#111111" opacity="0.9" stroke="#ff007f" stroke-width="2" />
      <line x1="96" y1="92" x2="104" y2="92" stroke="#ff007f" stroke-width="3.5" />
    `;
  } else if (activeAcc === "hat") {
    accessoriesSVG = `
      <!-- Red Wizard Hat -->
      <path d="M 72 52 L 100 12 L 128 52 Z" fill="#dc2626" />
      <ellipse cx="100" cy="52" rx="32" ry="6" fill="#991b1b" />
      <circle cx="100" cy="12" r="5" fill="#fbbf24" filter="drop-shadow(0 0 4px #fbbf24)" />
    `;
  } else if (activeAcc === "party_hat") {
    accessoriesSVG = `
      <!-- Pink Party Cone Hat -->
      <path d="M 80 50 L 100 10 L 120 50 Z" fill="#ec4899" stroke="#db2777" stroke-width="2" />
      <circle cx="95" cy="40" r="3" fill="#fbbf24" />
      <circle cx="105" cy="30" r="3" fill="#60a5fa" />
      <circle cx="100" cy="45" r="3" fill="#34d399" />
      <circle cx="100" cy="10" r="6" fill="#fbbf24" filter="drop-shadow(0 0 3px #fbbf24)" />
    `;
  }

  // Adjust SVG nodes based on expression state
  switch(state) {
    case "wave":
      expressionClass = "lumi-wave";
      mouth = `<path d="M 90 108 Q 100 118 110 108" stroke="#00f0ff" stroke-width="4" fill="none" stroke-linecap="round" filter="drop-shadow(0 0 3px #00f0ff)" />`;
      break;
    case "happy":
    case "celebrate":
      expressionClass = "lumi-jump";
      // Happy arch eyes
      eyeLeft = `<path d="M 77 98 Q 85 86 93 98" stroke="#00f0ff" stroke-width="4" fill="none" stroke-linecap="round" filter="drop-shadow(0 0 3px #00f0ff)" />`;
      eyeRight = `<path d="M 107 98 Q 115 86 123 98" stroke="#00f0ff" stroke-width="4" fill="none" stroke-linecap="round" filter="drop-shadow(0 0 3px #00f0ff)" />`;
      mouth = `<path d="M 88 106 Q 100 122 112 106" stroke="#00f0ff" stroke-width="4" fill="#00f0ff" stroke-linecap="round" filter="drop-shadow(0 0 3px #00f0ff)" />`;
      break;
    case "sad":
      expressionClass = "lumi-sad";
      // Worried downward eyes
      eyeLeft = `<path d="M 77 92 Q 85 102 93 92" stroke="#00f0ff" stroke-width="4" fill="none" stroke-linecap="round" filter="drop-shadow(0 0 3px #00f0ff)" />`;
      eyeRight = `<path d="M 107 92 Q 115 102 123 92" stroke="#00f0ff" stroke-width="4" fill="none" stroke-linecap="round" filter="drop-shadow(0 0 3px #00f0ff)" />`;
      mouth = `<path d="M 92 114 Q 100 106 108 114" stroke="#00f0ff" stroke-width="3" fill="none" stroke-linecap="round" filter="drop-shadow(0 0 2px #00f0ff)" />`;
      break;
    case "sleep":
      expressionClass = "lumi-sleep";
      eyeLeft = `<line x1="77" y1="95" x2="93" y2="95" stroke="#00f0ff" stroke-width="4" stroke-linecap="round" filter="drop-shadow(0 0 2px #00f0ff)" />`;
      eyeRight = `<line x1="107" y1="95" x2="123" y2="95" stroke="#00f0ff" stroke-width="4" stroke-linecap="round" filter="drop-shadow(0 0 2px #00f0ff)" />`;
      mouth = `<circle cx="100" cy="110" r="3.5" fill="#00f0ff" filter="drop-shadow(0 0 2px #00f0ff)" />`;
      break;
    case "think":
      expressionClass = "lumi-think";
      eyeLeft = `<circle cx="85" cy="90" r="6" fill="#00f0ff" filter="drop-shadow(0 0 3px #00f0ff)" />`;
      eyeRight = `<circle cx="115" cy="90" r="6" fill="#00f0ff" filter="drop-shadow(0 0 3px #00f0ff)" />`;
      mouth = `<line x1="90" y1="112" x2="110" y2="112" stroke="#00f0ff" stroke-width="3" stroke-linecap="round" filter="drop-shadow(0 0 2px #00f0ff)" />`;
      break;
    case "dance":
      expressionClass = "lumi-dance";
      mouth = `<path d="M 90 107 Q 100 120 110 107" stroke="#00f0ff" stroke-width="4" fill="none" stroke-linecap="round" filter="drop-shadow(0 0 3px #00f0ff)" />`;
      break;
    case "fly":
      expressionClass = "lumi-fly";
      mouth = `<path d="M 92 108 Q 100 115 108 108" stroke="#00f0ff" stroke-width="3" fill="none" stroke-linecap="round" filter="drop-shadow(0 0 2px #00f0ff)" />`;
      break;
    case "clap":
      expressionClass = "lumi-clap";
      mouth = `<path d="M 90 107 Q 100 118 110 107" stroke="#00f0ff" stroke-width="4" fill="none" stroke-linecap="round" filter="drop-shadow(0 0 3px #00f0ff)" />`;
      break;
  }

  // Waving arm path modifiers
  let leftArm = `<path d="M 55 140 Q 30 160 25 180" stroke="#cbd5e1" stroke-width="12" fill="none" stroke-linecap="round" class="lumi-l-arm" />`;
  let rightArm = `<path d="M 145 140 Q 170 160 175 180" stroke="#cbd5e1" stroke-width="12" fill="none" stroke-linecap="round" class="lumi-r-arm" />`;
  
  if (state === "wave") {
    leftArm = `<path d="M 55 140 Q 25 100 35 70" stroke="#cbd5e1" stroke-width="12" fill="none" stroke-linecap="round" class="lumi-waving-arm" />`;
  } else if (state === "think") {
    leftArm = `<path d="M 55 140 Q 75 125 85 110" stroke="#cbd5e1" stroke-width="12" fill="none" stroke-linecap="round" class="lumi-thinking-arm" />`;
  } else if (state === "celebrate" || state === "happy") {
    leftArm = `<path d="M 55 140 Q 30 100 45 75" stroke="#cbd5e1" stroke-width="12" fill="none" stroke-linecap="round" class="lumi-happy-l-arm" />`;
    rightArm = `<path d="M 145 140 Q 170 100 155 75" stroke="#cbd5e1" stroke-width="12" fill="none" stroke-linecap="round" class="lumi-happy-r-arm" />`;
  }

  // Thruster jet flame for fly state
  let jetFlame = "";
  if (state === "fly") {
    jetFlame = `
      <path d="M 90 195 L 100 225 L 110 195 Z" fill="#ff7f00" class="lumi-flame" />
      <path d="M 95 195 L 100 215 L 105 195 Z" fill="#ffef00" class="lumi-flame-inner" />
    `;
  }

  // Original Cute 3D Robot SVG representation of Lumi (Not an Owl)
  return `
    <svg viewBox="0 0 200 240" class="lumi-mascot-svg ${expressionClass}" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <!-- 3D Gradients -->
        <radialGradient id="bodyGrad" cx="35%" cy="35%" r="65%">
          <stop offset="0%" stop-color="#ffffff" />
          <stop offset="60%" stop-color="#e2e8f0" />
          <stop offset="100%" stop-color="#cbd5e1" />
        </radialGradient>
        <linearGradient id="screenGrad" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#0f172a" />
          <stop offset="100%" stop-color="#020617" />
        </linearGradient>
        <radialGradient id="earGrad" cx="35%" cy="35%" r="65%">
          <stop offset="0%" stop-color="#38bdf8" />
          <stop offset="100%" stop-color="#0284c7" />
        </radialGradient>
        
        <!-- Drop Shadows -->
        <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
          <feDropShadow dx="0" dy="10" stdDeviation="8" flood-opacity="0.18" />
        </filter>
      </defs>

      <!-- Jet Thruster Flame -->
      ${jetFlame}

      <!-- Ears / Side Knobs -->
      <rect x="40" y="75" width="14" height="24" rx="6" fill="url(#earGrad)" />
      <rect x="146" y="75" width="14" height="24" rx="6" fill="url(#earGrad)" />

      <!-- Limbs / Arms -->
      ${leftArm}
      ${rightArm}

      <!-- Body / Torso -->
      <rect x="58" y="122" width="84" height="72" rx="28" fill="url(#bodyGrad)" filter="url(#shadow)" />
      <!-- Power Core / Heart Symbol -->
      <circle cx="100" cy="155" r="15" fill="#1e293b" />
      <circle cx="100" cy="155" r="10" fill="#00f0ff" class="lumi-core-glow" filter="drop-shadow(0 0 6px #00f0ff)" />

      <!-- Head -->
      <rect x="50" y="48" width="100" height="82" rx="38" fill="url(#bodyGrad)" filter="url(#shadow)" />
      <!-- Face Screen -->
      <rect x="62" y="60" width="76" height="58" rx="22" fill="url(#screenGrad)" />

      <!-- Blushing Cheeks (Adds friendliness) -->
      <circle cx="72" cy="108" r="5" fill="#f43f5e" opacity="0.4" />
      <circle cx="128" cy="108" r="5" fill="#f43f5e" opacity="0.4" />

      <!-- Expressions (Eyes + Mouth) -->
      <g class="lumi-face">
        ${eyeLeft}
        ${eyeRight}
        ${mouth}
      </g>

      <!-- Head Antenna -->
      <line x1="100" y1="48" x2="100" y2="23" stroke="#cbd5e1" stroke-width="6" stroke-linecap="round" />
      <circle cx="100" cy="20" r="9" fill="#38bdf8" class="lumi-antenna-glow" filter="drop-shadow(0 0 6px #38bdf8)" />

      <!-- Custom Accessories -->
      ${accessoriesSVG}
    </svg>
  `;
}

// Pre-fetch voices into browser cache on startup
if ('speechSynthesis' in window) {
  window.speechSynthesis.getVoices();
  if (window.speechSynthesis.onvoiceschanged !== undefined) {
    window.speechSynthesis.onvoiceschanged = () => {
      window.speechSynthesis.getVoices();
    };
  }
}

// Speak message aloud using Hybrid Audio Engine (Browser SpeechSynthesis + Cloud Audio Stream fallback)
let currentHtmlAudio = null;

function speakMessage(text, lang = "English") {
  if (!text) return;
  console.log(`[AI TUTOR TTS LOG] speakMessage called -> lang='${lang}', text='${text.substring(0, 35)}...'`);
  
  // Save last spoken parameters for Replay function
  window.lastSpokenText = text;
  window.lastSpokenLang = lang;

  speakTextWithCallback(text, lang);
}

// Renders the mascot inside a container element with message bubble
function renderMascot(containerId, state = "normal", message = "", voiceLang = "English") {
  const container = document.getElementById(containerId);
  if (!container) return;
  
  const bubbleHTML = message ? `
    <div class="lumi-bubble-container">
      <div class="lumi-bubble">
        <p class="mb-0 text-dark fw-medium">${message}</p>
        <button type="button" class="btn btn-sm btn-outline-primary rounded-circle p-1 ms-2 speak-bubble-btn" onclick="speakMessage('${message.replace(/["'`]/g, "")}', '${voiceLang}')" title="Listen">
          <i class="bi bi-volume-up-fill"></i>
        </button>
      </div>
      <div class="lumi-bubble-arrow"></div>
    </div>
  ` : "";

  container.className = "lumi-mascot-wrapper d-flex align-items-center gap-3 flex-wrap";
  container.innerHTML = `
    <div class="lumi-svg-container" style="width: 130px; height: 160px; flex-shrink: 0;">
      ${getMascotSVG(state)}
    </div>
    ${bubbleHTML}
  `;
  
  // Automatically speak the guide bubble prompts when rendering only if autoplay is ON
  if (message && localStorage.getItem('voice_tutor_autoplay') === 'true' && localStorage.getItem('voice_tutor_muted') !== 'true') {
    setTimeout(() => {
      speakMessage(message, voiceLang);
    }, 500);
  }
}

// Play feedback based on correct/incorrect response
function playMascotFeedback(containerId, isCorrect, correctMsg = "Great job! Keep it up! ⭐", incorrectMsg = "Oops! Let's try it again together. You can do it!", voiceLang = "English") {
  const state = isCorrect ? "celebrate" : "sad";
  const msg = isCorrect ? correctMsg : incorrectMsg;
  
  renderMascot(containerId, state, msg, voiceLang);
  
  // Play synthesized audio chimes offline
  playSynthesizedSound(isCorrect ? "success" : "error");
  
  // Revert to normal/wave after 4 seconds
  setTimeout(() => {
    renderMascot(containerId, "wave", "", voiceLang);
  }, 4000);
}

function playSynthesizedSound(type) {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.connect(gain);
    gain.connect(ctx.destination);
    
    if (type === 'success') {
      const now = ctx.currentTime;
      osc.type = 'triangle';
      const freqs = [523.25, 659.25, 783.99, 1046.50];
      freqs.forEach((f, idx) => {
        osc.frequency.setValueAtTime(f, now + idx * 0.1);
      });
      gain.gain.setValueAtTime(0.12, now);
      gain.gain.exponentialRampToValueAtTime(0.01, now + 0.5);
      osc.start(now);
      osc.stop(now + 0.5);
    } else if (type === 'clapping') {
      const bufferSize = ctx.sampleRate * 1.2;
      const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
      const data = buffer.getChannelData(0);
      for (let i = 0; i < bufferSize; i++) {
        data[i] = Math.random() * 2 - 1;
      }
      const noise = ctx.createBufferSource();
      noise.buffer = buffer;
      const filter = ctx.createBiquadFilter();
      filter.type = 'bandpass';
      filter.frequency.value = 1000;
      const noiseGain = ctx.createGain();
      noiseGain.gain.setValueAtTime(0.12, ctx.currentTime);
      for (let t = 0; t < 1.2; t += 0.08) {
        noiseGain.gain.setValueAtTime(0.15, ctx.currentTime + t);
        noiseGain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + t + 0.06);
      }
      noise.connect(filter);
      filter.connect(noiseGain);
      noiseGain.connect(ctx.destination);
      noise.start();
      noise.stop(ctx.currentTime + 1.2);
    } else if (type === 'error') {
      const now = ctx.currentTime;
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(196.00, now);
      osc.frequency.linearRampToValueAtTime(130.81, now + 0.4);
      gain.gain.setValueAtTime(0.08, now);
      gain.gain.exponentialRampToValueAtTime(0.01, now + 0.4);
      osc.start(now);
      osc.stop(now + 0.4);
    }
  } catch (e) {
    console.warn("Web Audio API Synthesizer blocked or unsupported:", e);
  }
}

const MASCOT_MOTIVATION = {
  "English": {
    "welcome": "Hello! I am Lumi. Let's study together today! Choose a lesson to start.",
    "correct": [
      "Excellent! You did it! ⭐⭐⭐⭐⭐",
      "Spectacular! Your pronunciation is perfect!",
      "Superb! Keep up this amazing momentum!"
    ],
    "incorrect": [
      "Don't worry, mistakes help us learn! Try again.",
      "Close try! Practice makes perfect. Let's do it again.",
      "Almost there! Keep practicing and you will get it!"
    ],
    "tips": [
      "Tip: Try breaking long words into syllables to pronounce them easily!",
      "Tip: Practice speaking slow and clear for better accuracy.",
      "Tip: Read regional texts daily to build confidence!"
    ]
  },
  "Telugu": {
    "welcome": "నమస్కారం! నేను లూమి. ఈ రోజు మనం కలిసి చదువుకుందాం! ప్రారంభించడానికి ఒక పాఠాన్ని ఎంచుకోండి.",
    "correct": [
      "అద్భుతం! మీరు సాధించారు! ⭐⭐⭐⭐⭐",
      "చాలా బాగుంది! మీ ఉచ్చారణ చాలా బాగుంది!",
      "సూపర్! ఇదే ఉత్సాహంతో ముందుకు సాగండి!"
    ],
    "incorrect": [
      "చింతించకండి, తప్పుల నుంచే నేర్చుకుంటాం! మరోసారి ప్రయత్నించండి.",
      "చాలా దగ్గరగా వచ్చారు! మళ్లీ ప్రయత్నిద్దాం.",
      "ప్రнятనిస్తూనే ఉండండి! మీరు తప్పక సాధిస్తారు!"
    ],
    "tips": [
      "చిట్కా: పెద్ద పదాలను చిన్న చిన్న భాగాలుగా విడగొట్టి పలకండి!",
      "చిట్కా: మెరుగైన ఫలితాల కోసం స్పష్టంగా, నెమ్మదిగా మాట్లాడండి.",
      "చిట్కా: ప్రతిరోజూ తెలుగు కథలు చదవడం ప్రాక్టీस చేయండి!"
    ]
  },
  "Hindi": {
    "welcome": "नमस्ते! मैं लूमी हूँ। आइए आज साथ मिलकर पढ़ते हैं! शुरू करने के लिए कोई पाठ चुनें।",
    "correct": [
      "अद्भुत! आपने कर दिखाया! ⭐⭐⭐⭐⭐",
      "बहुत बढ़िया! आपका उच्चारण बिल्कुल सही है!",
      "शानदार! इसी तरह आगे बढ़ते रहें!"
    ],
    "incorrect": [
      "चिंता न करें, गलतियों से ही हम सीखते हैं! फिर से प्रयास करें।",
      "बहुत करीब! अभ्यास से सब आसान हो जाता है। आइए फिर से करें।",
      "आप कर सकते हैं! निरंतर अभ्यास जारी रखें!"
    ],
    "tips": [
      "सुझाव: लंबे शब्दों को आसान बनाने के लिए उन्हें छोटे भागों में तोड़ें!",
      "सुझाव: बेहतर उच्चारण के लिए स्पष्ट और धीमे स्वर में बोलें।",
      "सुझाव: शब्दों को दोहराकर अभ्यास करना सबसे अच्छा तरीका है।"
    ]
  },
  "Tamil": {
    "welcome": "வணக்கம்! நான் லூமி. இன்று நாம் சேர்ந்து படிப்போம்! ஒரு பாடத்தைத் தேர்ந்தெடுங்கள்.",
    "correct": [
      "அருமை! நீங்கள் சாதித்துவிட்டீர்கள்! ⭐⭐⭐⭐⭐",
      "மிக நன்று! உங்கள் உச்சரிப்பு மிகத் துல்லியமாக உள்ளது!",
      "அற்புதமான முயற்சி! தொடர்ந்து முன்னேறுங்கள்!"
    ],
    "incorrect": [
      "கவலைப்படாதீர்கள், தவறுகளில் இருந்தே நாம் கற்றுக்கொள்கிறோம்! மீண்டும் முயலுங்கள்.",
      "மிக நெருங்கிவிட்டீர்கள்! தொடர்ந்து பயிற்சி செய்யுங்கள்.",
      "முயற்சியை கைவிடாதீர்கள்! உங்களால் முடியும்!"
    ],
    "tips": [
      "உதவிக்குறிப்பு: கடினமான சொற்களை எழுத்துக்கூட்டி உச்சரிக்க முயலுங்கள்!",
      "உதவிக்குறிப்பு: உச்சரிப்பை மேம்படுத்த மெதுவாகவும் தெளிவாகவும் பேசுங்கள்."
    ]
  },
  "Kannada": {
    "welcome": "ನಮಸ್ಕಾರ! ನಾನು ಲೂಮಿ. ಇಂದು ನಾವು ಒಟ್ಟಿಗೆ ಕಲಿಯೋಣ! ಪ್ರಾರಂಭಿಸಲು ಪಾಠವನ್ನು ಆರಿಸಿ.",
    "correct": [
      "ಅದ್ಭುತ! ನೀವು ಸಾಧಿಸಿದ್ದೀರಿ! ⭐⭐⭐⭐⭐",
      "ಉತ್ತಮ! ನಿಮ್ಮ ಉಚ್ಚಾರಣೆ ಅತ್ಯುತ್ತಮವಾಗಿದೆ!",
      "ಶಹಬಾಸ್! ಇದೇ ರೀತಿ ಮುಂದುವರಿಯಿರಿ!"
    ],
    "incorrect": [
      "ಚಿಂತಿಸಬೇಡಿ, ತಪ್ಪುಗಳಿಂದಲೇ ಕಲಿಯುತ್ತೇವೆ! ಮತ್ತೊम्मे प्रयत्नಿಸಿ.",
      "ತುಂಬಾ ಹತ್ತಿರ ಬಂದಿದ್ದೀರಿ! ನಿರಂತರ ಅಭ್ಯಾಸ ಯಶಸ್ಸು ನೀಡುತ್ತದೆ.",
      "ನಿಮ್ಮಿಂದ ಸಾಧ್ಯ! ಸತತವಾಗಿ ಪ್ರಯತ್ನಿಸುತ್ತಿರಿ!"
    ],
    "tips": [
      "ಸಲಹೆ: ದೀರ್ಘ ಪದಗಳನ್ನು ಉಚ್ಚರಿಸಲು ಭಾಗಗಳಾಗಿ ವಿಂಗಡಿಸಿ!",
      "ಸಲಹೆ: ನಿಖರವಾದ ಉಚ್ಚಾರಣೆಗಾಗಿ ಸ್ಪಷ್ಟವಾಗಿ ಮತ್ತು ಸಾವಧಾನವಾಗಿ ಮಾತನಾಡಿ."
    ]
  },
  "Marathi": {
    "welcome": "नमस्कार! मी लूमी आहे. आज आपण एकत्र अभ्यास करूया! धडा निवडा.",
    "correct": [
      "उत्कृष्ट! तुम्ही करून दाखवले! ⭐⭐⭐⭐⭐",
      "खूपच छान! तुमचे उच्चारण अतिशय अचूक आहे!",
      "अफाट कामगिरी! अशीच प्रगती करत राहा!"
    ],
    "incorrect": [
      "काळजी करू नका, चुकांमधूनच आपण शिकतो! पुन्हा प्रयत्न करा.",
      "खूप जवळ! सरावाने सर्व काही सोपे होते. पुन्हा प्रयत्न करूया.",
      "प्रयत्न सोडता कामा नये! तुम्ही नक्कीच जिंकणार!"
    ],
    "tips": [
      "टीप: लांब शब्द उच्चारण्यासाठी त्यांचे तुकडे करा!",
      "टीप: अचूकतेसाठी स्पष्ट आणि सावकाश बोलण्याचा सराव करा."
    ]
  }
};

function triggerMascotPhrase(containerId, category, lang = "English", learnerName = "Learner", lastCompleted = "", nextTopic = "") {
  const langMap = MASCOT_MOTIVATION[lang] || MASCOT_MOTIVATION["English"];
  let phrase = "";
  let state = "normal";
  
  if (category === "welcome") {
    const prev = lastCompleted || (lang === "Telugu" ? "రంగులు" : lang === "Hindi" ? "रंग" : "Colors");
    const next = nextTopic || (lang === "Telugu" ? "ఆకారాలు" : lang === "Hindi" ? "आकृतियाँ" : "Shapes");

    if (lang === "Telugu") {
      phrase = `నమస్కారం ${learnerName}! తిరిగి వచ్చినందుకు స్వాగతం. నిన్న మీరు ${prev} పూర్తి చేశారు. ఈరోజు మనం ${next} నేర్చుకుందాం!`;
    } else if (lang === "Hindi") {
      phrase = `नमस्ते ${learnerName}! आपका फिर से स्वागत है। कल आपने ${prev} पूरा किया था। आज हम ${next} सीखेंगे!`;
    } else if (lang === "Tamil") {
      phrase = `வணக்கம் ${learnerName}! மீண்டும் வரவேற்கிறோம். நேற்று நீங்கள் ${prev} முடித்தீர்கள். இன்று நாம் ${next} கற்போம்!`;
    } else if (lang === "Kannada") {
      phrase = `ನಮಸ್ಕಾರ ${learnerName}! ಮತ್ತೆ ಸ್ವಾಗತ. ನಿನ್ನೆ ನೀವು ${prev} ಪೂರ್ಣಗೊಳಿಸಿದ್ದೀರಿ. ಇಂದು ನಾವು ${next} ಕಲಿಯೋಣ!`;
    } else if (lang === "Marathi") {
      phrase = `नमस्कार ${learnerName}! पुन्हा स्वागत आहे. काल तुम्ही ${prev} पूर्ण केले. आज आपण ${next} शिकूया!`;
    } else {
      phrase = `Welcome back ${learnerName}! Yesterday you completed ${prev}. Today we'll learn ${next}.`;
    }
    state = "wave";
  } else if (category === "assessment_post") {
    const rec = nextTopic || (lang === "Telugu" ? "సంఖ్యల లెక్కింపు (Number Counting)" : "Number Counting");
    if (lang === "Telugu") {
      phrase = `మీరు చాలా బాగా చేశారు! తదుపరి పాఠానికి వెళ్లేముందు ${rec} అభ్యాసం చేయమని నేను సిఫార్సు చేస్తున్నాను.`;
    } else if (lang === "Hindi") {
      phrase = `आपने बहुत अच्छा किया! अगले पाठ पर जाने से पहले मैं ${rec} का अभ्यास करने की सलाह देता हूँ।`;
    } else if (lang === "Tamil") {
      phrase = `நீங்கள் சிறப்பாகச் செய்தீர்கள்! அடுத்த பாடத்திற்குச் செல்வதற்கு முன் ${rec} பயிற்சி செய்ய பரிந்துரைக்கிறேன்.`;
    } else if (lang === "Kannada") {
      phrase = `ನೀವು ಉತ್ತಮವಾಗಿ ಮಾಡಿದ್ದೀರಿ! ಮುಂದಿನ ಪಾಠಕ್ಕೆ ಹೋಗುವ ಮೊದಲು ${rec} ಅಭ್ಯಾಸ ಮಾಡಲು ಶಿಫಾರಸು ಮಾಡುತ್ತೇನೆ.`;
    } else if (lang === "Marathi") {
      phrase = `तुम्ही उत्तम काम केले! पुढील पाठावर जाण्यापूर्वी ${rec} चा सराव करण्याची मी शिफारस करतो.`;
    } else {
      phrase = `You did great! I recommend practicing ${rec} before moving to the next lesson.`;
    }
    state = "celebrate";
  } else if (category === "correct") {
    const list = langMap["correct"];
    phrase = list[Math.floor(Math.random() * list.length)];
    state = "celebrate";
  } else if (category === "incorrect") {
    const list = langMap["incorrect"];
    phrase = list[Math.floor(Math.random() * list.length)];
    state = "sad";
  } else if (category === "tips") {
    const list = langMap["tips"];
    phrase = list[Math.floor(Math.random() * list.length)];
    state = "think";
  }
  
  renderMascot(containerId, state, phrase, lang);
}


// ==========================================
// Phase 4: Lumi Interactive Teacher Engine
// ==========================================
const TEACHER_INTRO_TEMPLATES = {
    "English": {
        "intro": (topic) => `Hello! Today we're learning ${topic}. First let's watch a fun video, then we'll play a small game together!`,
        "post": (topic) => `Great job watching the video! Can you answer the small question below?`
    },
    "Telugu": {
        "intro": (topic) => `నమస్కారం! ఈరోజు మనం ${topic} నేర్చుకుంటున్నాం. ముందుగా సరదా వీడియో చూద్దాం, ఆపై చిన్న ఆట ఆడుకుందాం!`,
        "post": (topic) => `చాలా బాగుంది! ఇప్పుడు కింద ఉన్న చిన్న ప్రశ్నకు సమాధానం చెప్పగలరా?`
    },
    "Hindi": {
        "intro": (topic) => `नमस्ते! आज हम ${topic} सीख रहे हैं। पहले एक मजेदार वीडियो देखते हैं, फिर साथ में एक छोटा खेल खेलेंगे!`,
        "post": (topic) => `बहुत बढ़िया! क्या आप नीचे दिए गए प्रश्न का उत्तर दे सकते हैं?`
    },
    "Tamil": {
        "intro": (topic) => `வணக்கம்! இன்று நாம் ${topic} கற்கப்போகிறோம். முதலில் ஒரு வேடிக்கையான வீடியோவைப் பார்ப்போம்!`,
        "post": (topic) => `மிக நன்று! கீழே உள்ள கேள்விக்கு பதிலளிக்க முடியுமா?`
    },
    "Kannada": {
        "intro": (topic) => `ನಮಸ್ಕಾರ! ಇಂದು ನಾವು ${topic} ಕಲಿಯುತ್ತಿದ್ದೇವೆ. ಮೊದಲು ಒಂದು ಮೋಜಿನ ವಿಡಿಯೋ ನೋಡೋಣ!`,
        "post": (topic) => `ಅದ್ಭುತ! ಕೆಳಗಿನ ಸಣ್ಣ ಪ್ರಶ್ನೆಗೆ ಉತ್ತರಿಸಬಹುದೇ?`
    },
    "Marathi": {
        "intro": (topic) => `नमस्कार! आज आपण ${topic} शिकत आहोत. आधी एक छान व्हिडिओ पाहूया!`,
        "post": (topic) => `खूप छान! खालील प्रश्नाचे उत्तर देऊ शकता का?`
    }
};

function renderTeacherMascot(containerId, topic, stage = "intro", lang = "English") {
    const tmpl = TEACHER_INTRO_TEMPLATES[lang] || TEACHER_INTRO_TEMPLATES["English"];
    const text = stage === "intro" ? tmpl.intro(topic) : tmpl.post(topic);
    renderMascot(containerId, "happy", text, lang);
}

function speakTextWithCallback(text, lang = "English", callback) {
    if (localStorage.getItem('voice_tutor_muted') === 'true') {
        if (callback) callback();
        return;
    }
    
    // Stop any existing audio playbacks
    if (window.currentHtmlAudio) {
        try { window.currentHtmlAudio.pause(); } catch(e) {}
        window.currentHtmlAudio = null;
    }
    if (window.speechSynthesis) {
        try { window.speechSynthesis.cancel(); } catch(e) {}
    }

    const langCodes = {
        "English": "en-US",
        "Telugu": "te-IN",
        "Hindi": "hi-IN",
        "Tamil": "ta-IN",
        "Kannada": "kn-IN",
        "Marathi": "mr-IN"
    };
    const code = langCodes[lang] || "en-US";

    if (lang !== "English") {
        // Use high-quality backend TTS audio stream for regional languages to guarantee native accents
        const audioUrl = `/api/tts?text=${encodeURIComponent(text)}&lang=${encodeURIComponent(lang)}`;
        const audio = new Audio(audioUrl);
        window.currentHtmlAudio = audio;
        audio.onended = function() {
            if (callback) callback();
        };
        audio.onerror = function() {
            if (callback) callback();
        };
        audio.play().catch(err => {
            console.warn("Regional TTS stream playback blocked or failed:", err);
            if (callback) callback();
        });
    } else {
        // Use browser native SpeechSynthesis for English
        if (!('speechSynthesis' in window)) {
            if (callback) callback();
            return;
        }
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = code;
        utterance.rate = 0.9;
        
        utterance.onend = function() {
            if (callback) callback();
        };
        utterance.onerror = function() {
            if (callback) callback();
        };
        
        // Find English voice
        const voices = window.speechSynthesis.getVoices() || [];
        const engVoice = voices.find(v => v.lang.toLowerCase().startsWith("en"));
        if (engVoice) utterance.voice = engVoice;
        
        window.speechSynthesis.speak(utterance);
    }
}
