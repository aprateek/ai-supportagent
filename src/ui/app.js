// Phase 12: Chat UI JavaScript
const API_URL = "http://localhost:8000";
let sessionId = `session-${Date.now()}`;

const messagesDiv = document.getElementById("chat-messages");
const inputField = document.getElementById("message-input");
const sendBtn = document.getElementById("send-btn");

sendBtn.addEventListener("click", sendMessage);
inputField.addEventListener("keypress", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

async function sendMessage() {
    const message = inputField.value.trim();
    if (!message) return;

    // Add user message
    addMessageToUI("user", message);
    inputField.value = "";

    // Send to API
    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                session_id: sessionId,
                message: message,
            }),
        });

        if (!response.ok) throw new Error("API error");

        const data = await response.json();
        addMessageToUI("assistant", data.agent_response);
    } catch (error) {
        addMessageToUI("error", `Error: ${error.message}`);
    }
}

function addMessageToUI(role, text) {
    const msgDiv = document.createElement("div");
    msgDiv.className = `message message-${role}`;
    msgDiv.innerHTML = `<p>${escapeHtml(text)}</p>`;
    messagesDiv.appendChild(msgDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}
