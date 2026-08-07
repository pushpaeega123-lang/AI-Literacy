// ==========================================
// AI Literacy Coach - Virtual Indian Keyboard
// static/js/keyboard.js
// ==========================================

const REGIONAL_KEYS = {
  "te": {
    "vowels": ["అ", "ఆ", "ఇ", "ఈ", "ఉ", "ఊ", "ఋ", "ఎ", "ఏ", "ఐ", "ఒ", "ఓ", "ఔ", "అం", "అః"],
    "consonants": [
      "క", "ఖ", "గ", "ఘ", "ఙ", 
      "చ", "ఛ", "జ", "ఝ", "ఞ", 
      "ట", "ఠ", "డ", "ఢ", "ణ", 
      "త", "థ", "ద", "ధ", "న", 
      "ప", "ఫ", "బ", "భ", "మ", 
      "య", "ర", "ల", "వ", "శ", "ష", "స", "హ", "ళ", "క్ష", "ఱ"
    ],
    "matras": ["ా", "ి", "ీ", "ు", "ూ", "ృ", "ె", "ే", "ై", "ొ", "ో", "ౌ", "్"]
  },
  "hi": {
    "vowels": ["अ", "आ", "इ", "ई", "उ", "ऊ", "ऋ", "ए", "ऐ", "ओ", "औ", "अं", "अः"],
    "consonants": [
      "क", "ख", "ग", "घ", "ङ", 
      "च", "छ", "ज", "झ", "ञ", 
      "ट", "ठ", "ड", "ढ", "ण", 
      "त", "थ", "द", "ध", "न", 
      "प", "फ", "ब", "भ", "म", 
      "य", "र", "ल", "व", "श", "ष", "स", "ह", "क्ष", "त्र", "ज्ञ"
    ],
    "matras": ["ा", "ि", "ी", "ु", "ू", "ृ", "े", "ै", "ो", "ौ", "ं", "ः", "्"]
  },
  "ta": {
    "vowels": ["அ", "ஆ", "இ", "ஈ", "உ", "ஊ", "எ", "ஏ", "ஐ", "ஒ", "ஓ", "ஔ", "ஃ"],
    "consonants": [
      "க", "ங", "ச", "ஞ", "ட", "ண", 
      "த", "ந", "ப", "ம", "ய", "ர", 
      "ல", "வ", "ழ", "ள", "ற", "ன", 
      "ஜ", "ஷ", "ஸ", "ஹ", "க்ஷ"
    ],
    "matras": ["ா", "ி", "ீ", "ு", "ூ", "ெ", "ே", "ை", "ொ", "ோ", "ௌ", "்"]
  },
  "kn": {
    "vowels": ["ಅ", "ಆ", "ಇ", "ಈ", "ಉ", "ಊ", "ಋ", "ಎ", "ಏ", "ಐ", "ಒ", "ಓ", "ಔ", "ಅಂ", "ಅಃ"],
    "consonants": [
      "ಕ", "ಖ", "ಗ", "ಘ", "ಙ", 
      "ಚ", "ಛ", "ಜ", "ಝ", "ಞ", 
      "ಟ", "ಠ", "ಡ", "ಢ", "ಣ", 
      "ತ", "ಥ", "ದ", "ಧ", "ನ", 
      "ಪ", "ಫ", "ಬ", "ಭ", "ಮ", 
      "ಯ", "ರ", "ಲ", "ವ", "ಶ", "ಷ", "ಸ", "ಹ", "ಳ"
    ],
    "matras": ["ಾ", "ಿ", "ೀ", "ು", "ೂ", "ೃ", "ೆ", "ೇ", "ೈ", "ೊ", "ೋ", "ೌ", "್"]
  },
  "mr": {
    // Marathi shares Devanagari script with Hindi, plus specific letters like ळ
    "vowels": ["अ", "आ", "इ", "ई", "उ", "ऊ", "ऋ", "ए", "ऐ", "ओ", "औ", "अं", "अः"],
    "consonants": [
      "क", "ख", "ग", "घ", "ङ", 
      "च", "छ", "ज", "झ", "ञ", 
      "ट", "ठ", "ड", "ढ", "ण", 
      "त", "थ", "द", "ध", "न", 
      "प", "फ", "ब", "भ", "म", 
      "य", "र", "ल", "व", "श", "ष", "स", "ह", "ळ", "क्ष", "त्र", "ज्ञ"
    ],
    "matras": ["ा", "ि", "ी", "ु", "ू", "ृ", "े", "ै", "ो", "ौ", "ं", "ः", "्"]
  }
};

let activeInputElement = null;
let currentKeyboardLang = "";

function initKeyboardHTML() {
  if (document.getElementById("keyboardOverlayPanel")) return;

  const panel = document.createElement("div");
  panel.id = "keyboardOverlayPanel";
  panel.className = "keyboard-overlay-panel";
  panel.innerHTML = `
    <div class="keyboard-suggestions-bar" id="keyboardSuggestions"></div>
    <div class="keyboard-keys-grid">
      <div class="keyboard-row" id="vowelRow"></div>
      <div class="keyboard-row" id="matraRow"></div>
      <div class="keyboard-row" id="consonantRow1"></div>
      <div class="keyboard-row" id="consonantRow2"></div>
      <div class="keyboard-row" id="consonantRow3"></div>
      <div class="keyboard-row" id="controlRow">
        <button class="keyboard-key key-danger" onclick="handleKeyboardAction('clear')">Clear</button>
        <button class="keyboard-key key-wide" onclick="handleKeyboardAction('space')">Space ⎵</button>
        <button class="keyboard-key key-danger" onclick="handleKeyboardAction('backspace')">⌫ Back</button>
        <button class="keyboard-key key-wide" onclick="hideKeyboard()">Done ✓</button>
      </div>
    </div>
  `;
  document.body.appendChild(panel);
}

function showKeyboard(inputId, languageName, suggestions = []) {
  initKeyboardHTML();
  
  const targetInput = document.getElementById(inputId);
  if (!targetInput) return;

  activeInputElement = targetInput;
  
  // Map long name to code
  let langCode = "";
  const nameClean = languageName.toLowerCase().trim();
  if (nameClean.includes("telugu")) langCode = "te";
  else if (nameClean.includes("hindi")) langCode = "hi";
  else if (nameClean.includes("tamil")) langCode = "ta";
  else if (nameClean.includes("kannada")) langCode = "kn";
  else if (nameClean.includes("marathi")) langCode = "mr";
  
  // English does not trigger regional keyboard
  if (!langCode) {
    hideKeyboard();
    return;
  }
  
  currentKeyboardLang = langCode;
  
  // Render keys
  renderKeyboardKeys(langCode);
  
  // Render suggestions
  const suggContainer = document.getElementById("keyboardSuggestions");
  suggContainer.innerHTML = "";
  suggestions.forEach(word => {
    const chip = document.createElement("div");
    chip.className = "keyboard-suggestion-chip";
    chip.innerText = word;
    chip.onclick = () => {
      activeInputElement.value = word;
      // Trigger input event to update frameworks
      activeInputElement.dispatchEvent(new Event('input'));
    };
    suggContainer.appendChild(chip);
  });
  
  // Display panel
  document.getElementById("keyboardOverlayPanel").style.display = "block";
}

function hideKeyboard() {
  const panel = document.getElementById("keyboardOverlayPanel");
  if (panel) {
    panel.style.display = "none";
  }
  activeInputElement = null;
}

function renderKeyboardKeys(langCode) {
  const dataset = REGIONAL_KEYS[langCode];
  if (!dataset) return;
  
  const vowelRow = document.getElementById("vowelRow");
  const matraRow = document.getElementById("matraRow");
  const cons1 = document.getElementById("consonantRow1");
  const cons2 = document.getElementById("consonantRow2");
  const cons3 = document.getElementById("consonantRow3");
  
  vowelRow.innerHTML = "";
  matraRow.innerHTML = "";
  cons1.innerHTML = "";
  cons2.innerHTML = "";
  cons3.innerHTML = "";
  
  // Vowels row
  dataset.vowels.forEach(v => {
    vowelRow.appendChild(createKeyButton(v));
  });
  
  // Matras row
  dataset.matras.forEach(m => {
    matraRow.appendChild(createKeyButton(m));
  });
  
  // Consonants rows divided logically
  const totalCons = dataset.consonants.length;
  const chunk = Math.ceil(totalCons / 3);
  
  for(let i=0; i<totalCons; i++) {
    const btn = createKeyButton(dataset.consonants[i]);
    if (i < chunk) {
      cons1.appendChild(btn);
    } else if (i < chunk * 2) {
      cons2.appendChild(btn);
    } else {
      cons3.appendChild(btn);
    }
  }
}

function createKeyButton(char) {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "keyboard-key";
  btn.innerText = char;
  btn.onclick = (e) => {
    e.preventDefault();
    if (activeInputElement) {
      // Get selection cursor position for inserting char
      const startPos = activeInputElement.selectionStart;
      const endPos = activeInputElement.selectionEnd;
      const val = activeInputElement.value;
      
      activeInputElement.value = val.substring(0, startPos) + char + val.substring(endPos);
      
      // Put cursor back after the inserted char
      activeInputElement.selectionStart = activeInputElement.selectionEnd = startPos + char.length;
      activeInputElement.focus();
      
      // Trigger event
      activeInputElement.dispatchEvent(new Event('input'));
    }
  };
  return btn;
}

function handleKeyboardAction(action) {
  if (!activeInputElement) return;
  
  const startPos = activeInputElement.selectionStart;
  const endPos = activeInputElement.selectionEnd;
  const val = activeInputElement.value;
  
  if (action === "clear") {
    activeInputElement.value = "";
  } else if (action === "space") {
    activeInputElement.value = val.substring(0, startPos) + " " + val.substring(endPos);
    activeInputElement.selectionStart = activeInputElement.selectionEnd = startPos + 1;
  } else if (action === "backspace") {
    if (startPos > 0 || endPos > startPos) {
      const deleteLen = (endPos > startPos) ? 0 : 1;
      const newCursor = Math.max(0, startPos - deleteLen);
      activeInputElement.value = val.substring(0, startPos - deleteLen) + val.substring(endPos);
      activeInputElement.selectionStart = activeInputElement.selectionEnd = newCursor;
    }
  }
  
  activeInputElement.focus();
  activeInputElement.dispatchEvent(new Event('input'));
}

// Auto-attach virtual keyboard to eligible inputs on focus
document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll("input[type='text']:not([readonly]), textarea").forEach(input => {
        input.addEventListener("focus", function() {
            const currentLang = window.currentLanguage || "English";
            
            let suggestions = [];
            if (currentLang === "Telugu") {
                suggestions = ["అమ్మ", "ఆవు", "ఇల్లు", "ఈగ", "ఉడుత", "నమస్కారం"];
            } else if (currentLang === "Hindi") {
                suggestions = ["आम", "इमली", "नमस्ते", "कमल", "घर", "बंदर"];
            } else if (currentLang === "Tamil") {
                suggestions = ["அம்மா", "ஆடு", "இலை", "வணக்கம்", "படம்", "மரம்"];
            } else if (currentLang === "Kannada") {
                suggestions = ["ಅಮ್ಮ", "ಆನೆ", "ಇಲಿ", "ನಮಸ್ಕಾರ", "ಕಮಲ", "ಮರ"];
            } else if (currentLang === "Marathi") {
                suggestions = ["आमचा", "इमारत", "नमस्कार", "कमळ", "घर", "बंदर"];
            }
            
            if (currentLang !== "English") {
                showKeyboard(input.id || (input.id = "kbd_input_" + Math.random().toString(36).substr(2, 9)), currentLang, suggestions);
            }
        });
    });
});

