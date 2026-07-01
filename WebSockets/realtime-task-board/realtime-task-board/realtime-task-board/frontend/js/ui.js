const state = {
  username: "",
  tasks: new Map(),
};

const columns = ["todo", "in_progress", "done"];

function showBoard() {
  document.getElementById("login").classList.add("hidden");
  document.getElementById("boardApp").classList.remove("hidden");
}

function setConnectionStatus(message) {
  document.getElementById("connectionStatus").textContent = message;
}

function renderUsers(users = []) {
  const usersList = document.getElementById("usersList");
  usersList.innerHTML = "";
  users.forEach((user) => {
    const item = document.createElement("li");
    item.textContent = user;
    usersList.appendChild(item);
  });
}

function renderBoard() {
  columns.forEach((column) => {
    document.getElementById(column).innerHTML = "";
  });

  [...state.tasks.values()].forEach((task) => {
    const columnElement = document.getElementById(task.column);
    columnElement.appendChild(createTaskCard(task));
  });
}

function createTaskCard(task) {
  const card = document.createElement("article");
  card.className = "task-card";
  card.draggable = true;
  card.dataset.taskId = task.id;

  const title = document.createElement("strong");
  title.textContent = task.title;

  const createdBy = document.createElement("small");
  createdBy.textContent = `Created by ${task.created_by}`;

  const actions = document.createElement("div");
  actions.className = "task-actions";

  const editButton = document.createElement("button");
  editButton.textContent = "Edit";
  editButton.addEventListener("click", () => editTask(task));

  const deleteButton = document.createElement("button");
  deleteButton.textContent = "Delete";
  deleteButton.addEventListener("click", () => deleteTask(task.id));

  actions.append(editButton, deleteButton);
  card.append(title, createdBy, actions);

  card.addEventListener("dragstart", (event) => {
    event.dataTransfer.setData("text/plain", String(task.id));
  });

  return card;
}

function addActivity(message) {
  if (!message) return;
  const log = document.getElementById("activityLog");
  const item = document.createElement("li");
  item.textContent = message;
  log.prepend(item);
}

function showTyping(message) {
  const indicator = document.getElementById("typingIndicator");
  indicator.textContent = message || "";
  window.clearTimeout(showTyping.timeoutId);
  showTyping.timeoutId = window.setTimeout(() => {
    indicator.textContent = "";
  }, 1600);
}
