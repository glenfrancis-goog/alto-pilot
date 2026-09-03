let currentSessionId = "session-" + Math.random().toString(36).substring(2, 9);
const employeeId = "EMP-62";

async function sendMessage(promptText, confirmedAction = null, userOverride = false) {
  const container = document.getElementById("messagesContainer");
  const cardSlot = document.getElementById("cardSlot");

  // Clear card slot
  cardSlot.innerHTML = "";

  // Render User Message if manual prompt
  if (promptText && !confirmedAction) {
    appendMessage("user", "👤", promptText);
  }

  // Loading skeleton
  const loadingEl = appendMessage("assistant", "🤖", "<em>Analyzing request through Google Cloud Model Armor...</em>");

  try {
    const payload = {
      prompt: promptText || "Confirm Action",
      session_id: currentSessionId,
      user_id: employeeId,
      confirmed_action: confirmedAction,
      user_override: userOverride
    };

    const res = await fetch("/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-User-Context": employeeId
      },
      body: JSON.stringify(payload)
    });

    const rawText = await res.text();
    let data;
    try {
      data = JSON.parse(rawText);
    } catch (e) {
      data = { response: rawText || "Server returned non-JSON response" };
    }
    loadingEl.remove();

    if (!res.ok) {
      appendMessage("assistant", "⚠️", `<strong>Error (${data.error_code || res.status}):</strong> ${data.response || data.detail || "Request failed"}`);
      return;
    }

    appendMessage("assistant", "🤖", formatMarkdown(data.response));

    // Render Action Cards if returned
    if (data.card) {
      renderCard(data.card);
    }
  } catch (err) {
    loadingEl.remove();
    appendMessage("assistant", "⚠️", `Connection error: ${err.message}. Please check backend server status.`);
  }
}

function appendMessage(role, avatar, contentHtml) {
  const container = document.getElementById("messagesContainer");
  const msg = document.createElement("div");
  msg.className = `message ${role}`;
  msg.innerHTML = `
    <div class="msg-avatar">${avatar}</div>
    <div class="msg-body">${contentHtml}</div>
  `;
  container.appendChild(msg);
  container.scrollTop = container.scrollHeight;
  return msg;
}

function formatMarkdown(text) {
  if (!text) return "";
  let html = text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/\n\n/g, '<br><br>')
    .replace(/\n\* /g, '<br>• ');
  return html;
}

function renderCard(card) {
  const slot = document.getElementById("cardSlot");
  const cardEl = document.createElement("div");

  if (card.card_type === "PREFLIGHT_CONFIRMATION") {
    cardEl.className = "action-card";
    cardEl.innerHTML = `
      <div class="card-title">⚠️ Action Confirmation Required</div>
      <p>${card.message}</p>
      <div class="card-buttons">
        <button class="card-btn primary" onclick='handleCardAction(${JSON.stringify(card)})'>Confirm & Submit</button>
        <button class="card-btn secondary" onclick='document.getElementById("cardSlot").innerHTML=""'>Cancel</button>
      </div>
    `;
  } else if (card.card_type === "DUPLICATE_DISAMBIGUATION") {
    cardEl.className = "action-card";
    const conflictId = card.conflict_ticket_id;
    cardEl.innerHTML = `
      <div class="card-title">📋 Duplicate Incident Detected</div>
      <p>${card.message}</p>
      <div class="card-buttons">
        <button class="card-btn primary" onclick="handleDuplicateAction('ADD_COMMENT', '${conflictId}')">Add Note to Ticket (${conflictId})</button>
        <button class="card-btn secondary" onclick="handleDuplicateAction('OVERRIDE', '${conflictId}')">File as Separate New Ticket</button>
      </div>
    `;
  } else if (card.card_type === "CONSENT_WITHDRAWAL") {
    cardEl.className = "action-card danger";
    cardEl.innerHTML = `
      <div class="card-title">🛡️ GDPR Right-to-be-Forgotten Data Purge</div>
      <p>${card.message}</p>
      <div class="card-buttons">
        <button class="card-btn danger" onclick='handleCardAction(${JSON.stringify(card)})'>${card.button_label}</button>
        <button class="card-btn secondary" onclick='document.getElementById("cardSlot").innerHTML=""'>Cancel</button>
      </div>
    `;
  }

  slot.appendChild(cardEl);
}

function handleCardAction(card) {
  document.getElementById("cardSlot").innerHTML = "";
  sendMessage("", { action: card.action, parameters: card.parameters });
}

function handleDuplicateAction(choice, ticketId) {
  document.getElementById("cardSlot").innerHTML = "";
  if (choice === "ADD_COMMENT") {
    sendMessage(`Please add a comment to ${ticketId} requesting expedited review.`);
  } else {
    // User override
    sendMessage("Proceed with filing this as a separate new ticket.", null, true);
  }
}

function sendQuickPrompt(promptText) {
  document.getElementById("userInput").value = promptText;
  sendMessage(promptText);
  document.getElementById("userInput").value = "";
}

function handleFormSubmit(e) {
  e.preventDefault();
  const input = document.getElementById("userInput");
  const text = input.value.trim();
  if (text) {
    sendMessage(text);
    input.value = "";
  }
}
