// Minimal single-handler chat widget
document.addEventListener('DOMContentLoaded', function () {
  const input = document.getElementById('chat-input');
  const send = document.getElementById('chat-send');
  const messages = document.getElementById('messages');

  if (!input || !send || !messages) return;

  let busy = false;

  function appendMessage(who, text) {
    const el = document.createElement('div');
    el.className = who === 'user' ? 'text-right mb-2' : 'text-left mb-2';
    const bubble = document.createElement('div');
    bubble.className = 'inline-block p-2 rounded ' + (who === 'user' ? 'bg-blue-100' : 'bg-gray-100');
    bubble.textContent = text;
    el.appendChild(bubble);
    messages.appendChild(el);
    messages.scrollTop = messages.scrollHeight;
  }

  function setBusy(state) {
    busy = !!state;
    input.disabled = busy;
    send.disabled = busy;
    if (busy) {
      send.dataset.origText = send.textContent || '';
      send.textContent = 'Enviando...';
      send.classList.add('opacity-60');
    } else {
      if (send.dataset.origText) send.textContent = send.dataset.origText;
      send.classList.remove('opacity-60');
    }
  }

  // Render bot responses in a friendly way. If the answer contains HTML snippets
  // (e.g. a <button> from docs), show a cleaned message and a safe action button
  // that attempts to call a global function if present (no eval).
  function renderBotResponse(data) {
    const answer = (data && data.answer) || '';
    // If looks like HTML or contains a button, convert to a friendly view
    const hasHtml = /<[^>]+>/.test(answer);
    if (hasHtml) {
      // Plain text version (remove tags and collapse whitespace)
      const textOnly = answer.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();

      const wrapper = document.createElement('div');
      wrapper.className = 'text-left mb-2';

      const bubble = document.createElement('div');
      bubble.className = 'inline-block p-2 rounded bg-gray-100';
      bubble.textContent = 'Encontré esto en la documentación y creo que responde tu pregunta: ' + (textOnly || ' (contenido)');
      wrapper.appendChild(bubble);

      // Try to extract a <button ...>label</button> from the HTML
      const btnMatch = answer.match(/<button\b([^>]*)>([\s\S]*?)<\/button>/i);
      if (btnMatch) {
        const attrs = btnMatch[1];
        const label = btnMatch[2].replace(/<[^>]+>/g, '').trim() || 'Acción';
        // Try to find onclick attribute
        const onclickMatch = attrs.match(/onclick\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))/i);
        const onclick = onclickMatch ? (onclickMatch[1] || onclickMatch[2] || onclickMatch[3]) : null;

        const actionBtn = document.createElement('button');
        actionBtn.className = 'btn btn-primary ml-2';
        actionBtn.textContent = label;
        actionBtn.addEventListener('click', function () {
          if (!onclick) {
            appendMessage('bot', 'Acción no disponible automáticamente.');
            return;
          }
          // Attempt to extract function name like myFunc(...) and call it if available
          const fnMatch = onclick.match(/([a-zA-Z_$][0-9a-zA-Z_.$]*)\s*\(/);
          if (fnMatch) {
            const fnName = fnMatch[1];
            const fn = window[fnName];
            if (typeof fn === 'function') {
              try { fn(); }
              catch (err) { appendMessage('bot', 'No se pudo ejecutar la acción: ' + (err && err.message)); }
              return;
            }
          }
          // Fallback: inform user how to proceed
          appendMessage('bot', 'No puedo ejecutar esa acción aquí. Si quieres, puedo escalarlo al administrador.');
        });

        wrapper.appendChild(actionBtn);
      }

      messages.appendChild(wrapper);
      messages.scrollTop = messages.scrollHeight;
      return;
    }

    // Default: plain answer
    appendMessage('bot', answer || 'Sin respuesta');
  }

  async function sendMessage() {
    if (busy) return;
    const text = input.value.trim();
    if (!text) return;

    appendMessage('user', text);
    input.value = '';

    setBusy(true);
    try {
      const res = await fetch('/api/chat/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
      });

      if (!res.ok) {
        appendMessage('bot', 'Error del servidor al procesar la petición.');
        return;
      }

  const data = await res.json().catch(() => ({ answer: 'Respuesta inválida del servidor.' }));
  // Render the bot response in a friendly way
  renderBotResponse(data);

      if (!data.resolved) {
        const actions = document.createElement('div');
        actions.className = 'chat-actions';

        const adaptBtn = document.createElement('button');
        adaptBtn.className = 'btn btn-secondary';
        adaptBtn.textContent = 'Adaptar a mi caso';

        const escBtn = document.createElement('button');
        escBtn.className = 'btn btn-danger';
        escBtn.textContent = 'Escalar al admin';

        const originalMessage = text;
        const snippet = (data.answer && data.answer.substring(0, 200)) || originalMessage;

        adaptBtn.addEventListener('click', async function () {
          if (busy) return;
          adaptBtn.disabled = true;
          adaptBtn.textContent = 'Adaptando...';
          try {
            const r = await fetch('/api/chat/adapt', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ snippet })
            });
            if (r.ok) {
              const jr = await r.json();
              appendMessage('bot', jr.adapted_answer || 'No se pudo adaptar.');
            } else {
              appendMessage('bot', 'Error al adaptar. Intenta más tarde.');
            }
          } catch (e) {
            console.error(e);
            appendMessage('bot', 'Error al adaptar. Intenta más tarde.');
          } finally {
            adaptBtn.disabled = false;
            adaptBtn.textContent = 'Adaptar a mi caso';
          }
        });

        escBtn.addEventListener('click', async function () {
          if (busy) return;
          escBtn.disabled = true;
          escBtn.textContent = 'Escalando...';
          try {
            const r = await fetch('/api/chat/escalate', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ original_message: originalMessage })
            });
            if (r.ok) {
              const jr = await r.json();
              appendMessage('bot', 'He creado un ticket (#' + jr.ticket_id + '). El administrador recibirá un aviso: ' + jr.admin_email);
            } else {
              appendMessage('bot', 'Error al escalar. Intenta más tarde.');
            }
          } catch (e) {
            console.error(e);
            appendMessage('bot', 'Error al escalar. Intenta más tarde.');
          } finally {
            escBtn.disabled = false;
            escBtn.textContent = 'Escalar al admin';
          }
        });

        actions.appendChild(adaptBtn);
        actions.appendChild(escBtn);
        messages.appendChild(actions);
      }
    } catch (e) {
      console.error(e);
      appendMessage('bot', 'Error de red. Intenta de nuevo.');
    } finally {
      setBusy(false);
    }
  }

  send.addEventListener('click', sendMessage);
  input.addEventListener('keyup', function (e) { if (e.key === 'Enter') sendMessage(); });
});
