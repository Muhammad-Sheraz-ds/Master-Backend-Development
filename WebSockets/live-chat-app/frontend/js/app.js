const joinScreen = document.getElementById("join-screen");
const chatScreen = document.getElementById("chat-screen");
const usernameInput = document.getElementById("username-input");
const joinButton = document.getElementById("join-button");
const statusText = document.getElementById("connection-status");
const usersList = document.getElementById("users-list");
const messages = document.getElementById("messages");
const typingIndicator = document.getElementById("typing-indicator");
const messageForm = document.getElementById("message-form");
const messageInput = document.getElementById("message-input");

let socket = null;
let username = "";
let typingTimer = null;

function connectWebSocket() {
  socket = new WebSocket("ws://localhost:8000/ws");

  socket.onopen = () => {
    statusText.textContent = "Connected";
    socket.send(JSON.stringify({ type: "join", username }));
  };

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    handleServerEvent(data);
  };

  socket.onclose = () => {
    statusText.textContent = "Disconnected";
    addSystemMessage("Disconnected from server");
  };

  socket.onerror = () => {
    statusText.textContent = "Connection error";
    addSystemMessage("Could not connect to server");
  };
}

function handleServerEvent(data) {
  if (data.type === "connected") {
    renderUsers(data.users || []);
  }

  if (data.type === "user_joined") {
    addSystemMessage(data.message, data.time);
    renderUsers(data.users || []);
  }

  if (data.type === "user_left") {
    addSystemMessage(data.message, data.time);
    renderUsers(data.users || []);
  }

  if (data.type === "chat_message") {
    addChatMessage(data.username, data.message, data.time);
    clearTypingIndicator();
  }

  if (data.type === "typing" && data.username !== username) {
    showTypingIndicator(data.message);
  }

  if (data.type === "error") {
    addSystemMessage(data.message);
  }
}

function joinChat() {
  username = usernameInput.value.trim();

  if (!username) {
    alert("Please enter your name");
    return;
  }

  joinScreen.classList.add("hidden");
  chatScreen.classList.remove("hidden");
  connectWebSocket();
}

function sendMessage(event) {
  event.preventDefault();

  const message = messageInput.value.trim();

  if (!message || socket.readyState !== WebSocket.OPEN) {
    return;
  }

  socket.send(
    JSON.stringify({
      type: "chat_message",
      message,
    })
  );

  messageInput.value = "";
}

function sendTypingEvent() {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({ type: "typing" }));
  }
}

function renderUsers(users) {
  usersList.innerHTML = "";

  users.forEach((user) => {
    const li = document.createElement("li");
    li.textContent = user;
    usersList.appendChild(li);
  });
}

function addChatMessage(sender, text, time) {
  const div = document.createElement("div");
  div.className = "message";

  div.innerHTML = `
    <div class="message-header">
      <strong>${escapeHtml(sender)}</strong>
      <span>${time || ""}</span>
    </div>
    <div>${escapeHtml(text)}</div>
  `;

  messages.appendChild(div);
  scrollToBottom();
}

function addSystemMessage(text, time = "") {
  const div = document.createElement("div");
  div.className = "message system";
  div.textContent = time ? `${text} (${time})` : text;
  messages.appendChild(div);
  scrollToBottom();
}

function showTypingIndicator(text) {
  typingIndicator.textContent = text;

  clearTimeout(typingTimer);
  typingTimer = setTimeout(clearTypingIndicator, 1200);
}

function clearTypingIndicator() {
  typingIndicator.textContent = "";
}

function scrollToBottom() {
  messages.scrollTop = messages.scrollHeight;
}

function escapeHtml(value) {
  const div = document.createElement("div");
  div.textContent = value;
  return div.innerHTML;
}

joinButton.addEventListener("click", joinChat);
usernameInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    joinChat();
  }
});
messageForm.addEventListener("submit", sendMessage);
messageInput.addEventListener("input", sendTypingEvent);
