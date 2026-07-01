class BoardSocket {
  constructor(url) {
    this.url = url;
    this.socket = null;
    this.handlers = {};
  }

  connect() {
    this.socket = new WebSocket(this.url);

    this.socket.onopen = () => this.emit("open");
    this.socket.onclose = () => this.emit("close");
    this.socket.onerror = () => this.emit("error", { message: "WebSocket error" });
    this.socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.emit(data.type, data);
    };
  }

  on(eventName, callback) {
    if (!this.handlers[eventName]) {
      this.handlers[eventName] = [];
    }
    this.handlers[eventName].push(callback);
  }

  emit(eventName, data = {}) {
    const callbacks = this.handlers[eventName] || [];
    callbacks.forEach((callback) => callback(data));
  }

  send(payload) {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      return;
    }
    this.socket.send(JSON.stringify(payload));
  }
}
