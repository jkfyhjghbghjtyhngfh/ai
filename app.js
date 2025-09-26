/* ...existing code... */
/* Main client-side simulated ChatGPT-5 demo. No server calls. */

const chatEl = document.getElementById('chat');
const form = document.getElementById('composer');
const input = document.getElementById('input');
const personaSel = document.getElementById('persona');
const clearBtn = document.getElementById('clear');
const ttsBtn = document.getElementById('tts');

let lastAssistantText = '';

function appendMessage(role, text, options = {}) {
  const msg = document.createElement('div');
  msg.className = 'message';
  const avatar = document.createElement('div');
  avatar.className = 'avatar';
  avatar.textContent = role === 'user' ? 'U' : 'A';
  const bubble = document.createElement('div');
  bubble.className = 'bubble ' + (role === 'user' ? 'user' : 'assistant');
  bubble.textContent = text;
  msg.appendChild(avatar);
  msg.appendChild(bubble);
  chatEl.appendChild(msg);
  chatEl.scrollTop = chatEl.scrollHeight;
  lastAssistantText = role === 'assistant' ? text : lastAssistantText;
  return bubble;
}

function simulateThinking(duration = 800) {
  const dot = appendMessage('assistant', '…');
  const start = Date.now();
  return new Promise(resolve => {
    const id = setInterval(() => {
      const elapsed = Date.now() - start;
      dot.textContent = '…'.repeat(1 + Math.floor((elapsed % 900) / 300));
    }, 120);
    setTimeout(() => {
      clearInterval(id);
      dot.parentNode.remove();
      resolve();
    }, duration);
  });
}

function generateResponse(prompt, persona) {
  // Lightweight deterministic pseudo-AI: constructs structured, helpful answers.
  const trimmed = prompt.trim();
  const time = new Date().toLocaleTimeString();
  const base = {
    default: `I understand your request. Here's a clear summary and suggestions:\n\n- Summary: ${trimmed.slice(0, 120)}${trimmed.length>120?'…':''}\n- Actionable steps: 1) Clarify requirements. 2) Prototype. 3) Iterate.\n\nIf you'd like, I can expand any step.`,
    concise: `Short answer: ${trimmed.split(/[.?]/)[0] || trimmed}\nIf you want more details, ask.`,
    creative: `Imagine this: ${trimmed} becomes a story, a concept, or a striking idea.\nStart by sketching, iterate boldly, and embrace constraints as sparks.`,
    expert: `Expert analysis (${time}):\n• Context: ${trimmed.slice(0,80)}\n• Recommendations: Provide metrics, run tests, and validate assumptions.\n• Risks: Consider edge cases and failure modes.`
  };
  // Add minor variability based on prompt length
  const variance = trimmed.length % 3;
  const extra = variance === 0 ? "\n\nNote: I can produce examples, code, or step-by-step plans on request." : "";
  return (base[persona] || base.default) + extra;
}

async function handleSubmit(e) {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  appendMessage('user', text);
  input.value = '';
  input.focus();
  await simulateThinking(700 + Math.min(1800, text.length * 8));
  const persona = personaSel.value;
  const response = generateResponse(text, persona);
  // Simulate streaming output
  const bubble = appendMessage('assistant', '');
  let i = 0;
  while (i < response.length) {
    const chunkLen = 8 + Math.floor(Math.random() * 24);
    bubble.textContent += response.slice(i, i + chunkLen);
    i += chunkLen;
    chatEl.scrollTop = chatEl.scrollHeight;
    await new Promise(r => setTimeout(r, 20 + Math.random() * 80));
  }
  lastAssistantText = bubble.textContent;
}

function clearChat() {
  chatEl.innerHTML = '';
  const welcome = document.createElement('div');
  welcome.className = 'welcome';
  welcome.innerHTML = '<strong>Welcome to ChatGPT‑5 (demo)</strong><p>Type a message and press Enter. This demo simulates an advanced assistant locally — no server calls.</p>';
  chatEl.appendChild(welcome);
}

form.addEventListener('submit', handleSubmit);
clearBtn.addEventListener('click', clearChat);

// Enter sends, Shift+Enter newline
input.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    form.requestSubmit();
  }
});

// TTS: speak last assistant message
ttsBtn.addEventListener('click', () => {
  if (!lastAssistantText) return;
  if (!('speechSynthesis' in window)) return alert('TTS not supported in this browser.');
  const utter = new SpeechSynthesisUtterance(lastAssistantText);
  utter.lang = 'en-US';
  utter.rate = 1;
  speechSynthesis.cancel();
  speechSynthesis.speak(utter);
});

// small accessibility: focus composer on load
window.addEventListener('load', () => input.focus());

/* ...existing code... */

