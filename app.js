// Minimal AI chat client using the host-provided websim chat API.
// Keeps a short conversation history and streams short responses where possible.

const messagesEl = document.getElementById('messages');
const form = document.getElementById('inputForm');
const input = document.getElementById('input');
const clearBtn = document.getElementById('clear');

let conversationHistory = []; // store last messages (user + assistant) sent to API

function appendMessage(text, cls) {
  const wrap = document.createElement('div');
  wrap.className = 'msg ' + cls;

  // If AI message, detect fenced code blocks and render them with copy button
  if (cls.includes('ai') && typeof text === 'string' && /```/.test(text)) {
    // Split into parts: text and code blocks
    // Keep fence language if provided (e.g. ```js)
    const parts = text.split(/(```[\s\S]*?```)/g);
    parts.forEach(part => {
      if (!part) return;
      if (part.startsWith('```')) {
        // strip fences
        const code = part.replace(/^```[\w-]*\n?/, '').replace(/```$/, '');
        const codeWrap = document.createElement('div');
        codeWrap.className = 'code-wrap';
        const pre = document.createElement('pre');
        pre.textContent = code;
        codeWrap.appendChild(pre);

        const copyBtn = document.createElement('button');
        copyBtn.className = 'copy-btn';
        copyBtn.type = 'button';
        copyBtn.textContent = 'Copy';
        copyBtn.addEventListener('click', async () => {
          try {
            await navigator.clipboard.writeText(code);
            copyBtn.textContent = 'Copied';
            setTimeout(() => (copyBtn.textContent = 'Copy'), 1500);
          } catch (e) {
            copyBtn.textContent = 'Error';
            setTimeout(() => (copyBtn.textContent = 'Copy'), 1500);
          }
        });
        codeWrap.appendChild(copyBtn);
        wrap.appendChild(codeWrap);
      } else {
        // plain text (may contain newlines)
        const p = document.createElement('div');
        p.textContent = part;
        wrap.appendChild(p);
      }
    });
  } else {
    wrap.textContent = text;
  }

  messagesEl.appendChild(wrap);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

// limit to last N entries we send to the API
function trimmedHistory() {
  return conversationHistory.slice(-10);
}

async function sendToModel(userText) {
  // Optimistic UI
  appendMessage(userText, 'user');

  // push to local history
  conversationHistory.push({ role: 'user', content: userText });

  appendMessage('...', 'ai');
  const placeholder = messagesEl.querySelector('.msg.ai:last-child');

  try {
    // Use the global websim object (available in the execution environment).
    // Only send the last 10 messages to keep payload small.
    const completion = await websim.chat.completions.create({
      messages: [
        {
          role: 'system',
          content: 'You are a concise helpful assistant. Keep replies short.'
        },
        ...trimmedHistory()
      ],
      // keep responses short and fast
      max_tokens: 180,
    });

    const aiText = completion.content?.trim() || 'No response.';
    // replace placeholder by removing it and appending parsed message
    placeholder.remove();
    appendMessage(aiText, 'ai');

    conversationHistory.push({ role: 'assistant', content: aiText });
    messagesEl.scrollTop = messagesEl.scrollHeight;
  } catch (err) {
    placeholder.textContent = 'Error: could not reach the AI.';
    console.error(err);
  }
}

form.addEventListener('submit', (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  input.value = '';
  sendToModel(text);
});

clearBtn.addEventListener('click', () => {
  messagesEl.innerHTML = '';
  conversationHistory = [];
});

// make textarea resize to content height (small helper)
function fitTextarea(t) {
  t.style.height = 'auto';
  t.style.height = (t.scrollHeight) + 'px';
}
input.addEventListener('input', (e) => fitTextarea(e.target));
fitTextarea(input);

// Setup persistent storage using host-provided WebsimSocket
const room = new WebsimSocket();
const convoListEl = document.getElementById('convoList');
const saveBtn = document.getElementById('saveConv');
const newBtn = document.getElementById('newConv');

// Render list of saved conversations
async function refreshConversations() {
  convoListEl.innerHTML = '';
  try {
    // get all conversation records (newest first)
    const convos = room.collection('conversation').getList() || [];
    // show newest -> oldest
    convos.reverse().forEach(c => {
      const row = document.createElement('div');
      row.className = 'convo-row';
      const title = document.createElement('div');
      title.className = 'convo-title';
      title.textContent = c.title || `Conversation ${c.created_at.slice(0,10)}`;
      row.appendChild(title);

      const actions = document.createElement('div');
      actions.className = 'convo-actions';
      const load = document.createElement('button');
      load.type = 'button';
      load.textContent = 'Load';
      load.addEventListener('click', () => loadConversation(c));
      actions.appendChild(load);

      const del = document.createElement('button');
      del.type = 'button';
      del.textContent = 'Delete';
      del.addEventListener('click', async () => {
        try {
          await room.collection('conversation').delete(c.id);
          refreshConversations();
        } catch (err) {
          console.error('Delete failed', err);
        }
      });
      actions.appendChild(del);

      row.appendChild(actions);
      convoListEl.appendChild(row);
    });
  } catch (err) {
    console.error('Failed to load conversations', err);
  }
}

// Save current conversation as a record
saveBtn.addEventListener('click', async () => {
  try {
    const title = prompt('Save conversation as (title):') || '';
    const payload = {
      title,
      messages: conversationHistory.slice(), // copy of messages
    };
    await room.collection('conversation').create(payload);
    refreshConversations();
  } catch (err) {
    console.error('Save failed', err);
    alert('Could not save conversation.');
  }
});

// New conversation (clear UI and history)
newBtn.addEventListener('click', () => {
  if (!confirm('Start a new conversation? This clears the current chat window.')) return;
  messagesEl.innerHTML = '';
  conversationHistory = [];
});

// Subscribe to conversation list changes to keep UI in sync
room.collection('conversation').subscribe(() => {
  refreshConversations();
});

// initial load of saved conversations
refreshConversations();

// start with a greeting from AI
(async function init() {
  appendMessage('Hello — I am an AI assistant. Ask me anything.', 'ai');
  conversationHistory.push({ role: 'assistant', content: 'Hello — I am an AI assistant. Ask me anything.' });
})();