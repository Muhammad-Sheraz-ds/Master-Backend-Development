const socketUrl = "ws://localhost:8000/ws";
const boardSocket = new BoardSocket(socketUrl);

const usernameInput = document.getElementById("usernameInput");
const joinButton = document.getElementById("joinButton");
const taskForm = document.getElementById("taskForm");
const taskTitleInput = document.getElementById("taskTitleInput");
const taskColumnInput = document.getElementById("taskColumnInput");

boardSocket.on("open", () => setConnectionStatus("Connected"));
boardSocket.on("close", () => setConnectionStatus("Disconnected"));
boardSocket.on("error", (event) => addActivity(event.message));

boardSocket.on("board_state", (event) => {
  state.tasks = new Map(event.tasks.map((task) => [task.id, task]));
  renderUsers(event.users);
  renderBoard();
});

boardSocket.on("user_joined", (event) => {
  renderUsers(event.users);
  addActivity(event.message);
});

boardSocket.on("user_left", (event) => {
  renderUsers(event.users);
  addActivity(event.message);
});

boardSocket.on("task_created", (event) => {
  state.tasks.set(event.task.id, event.task);
  renderBoard();
  addActivity(event.message);
});

boardSocket.on("task_updated", (event) => {
  state.tasks.set(event.task.id, event.task);
  renderBoard();
  addActivity(event.message);
});

boardSocket.on("task_moved", (event) => {
  state.tasks.set(event.task.id, event.task);
  renderBoard();
  addActivity(event.message);
});

boardSocket.on("task_deleted", (event) => {
  state.tasks.delete(event.task_id);
  renderBoard();
  addActivity(event.message);
});

boardSocket.on("typing", (event) => {
  if (event.username !== state.username) {
    showTyping(event.message);
  }
});

joinButton.addEventListener("click", () => {
  const username = usernameInput.value.trim();
  if (!username) return;

  state.username = username;
  showBoard();
  boardSocket.send({ type: "join", username });
});

usernameInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    joinButton.click();
  }
});

taskForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const title = taskTitleInput.value.trim();
  if (!title) return;

  boardSocket.send({
    type: "create_task",
    username: state.username,
    title,
    column: taskColumnInput.value,
  });
  taskTitleInput.value = "";
});

function editTask(task) {
  boardSocket.send({ type: "typing", username: state.username, task_id: task.id });
  const title = window.prompt("Edit task title", task.title);
  if (!title || !title.trim()) return;

  boardSocket.send({
    type: "update_task",
    username: state.username,
    task_id: task.id,
    title: title.trim(),
  });
}

function deleteTask(taskId) {
  boardSocket.send({
    type: "delete_task",
    username: state.username,
    task_id: taskId,
  });
}

document.querySelectorAll(".column").forEach((column) => {
  column.addEventListener("dragover", (event) => {
    event.preventDefault();
    column.classList.add("drag-over");
  });

  column.addEventListener("dragleave", () => {
    column.classList.remove("drag-over");
  });

  column.addEventListener("drop", (event) => {
    event.preventDefault();
    column.classList.remove("drag-over");
    const taskId = Number(event.dataTransfer.getData("text/plain"));
    const targetColumn = column.dataset.column;

    boardSocket.send({
      type: "move_task",
      username: state.username,
      task_id: taskId,
      column: targetColumn,
    });
  });
});

boardSocket.connect();
