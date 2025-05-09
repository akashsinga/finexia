// src/services/websocket.service.js
export class WebSocketService {
  constructor(url, callbacks = {}) {
    this.url = url;
    this.connection = null;
    this.connected = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.connectionTimeout = null;
    this.reconnectTimeout = null;

    // Callbacks
    this.onOpen = callbacks.onOpen || (() => { });
    this.onMessage = callbacks.onMessage || (() => { });
    this.onClose = callbacks.onClose || (() => { });
    this.onError = callbacks.onError || (() => { });
  }

  connect() {
    this.close();

    try {
      this.connection = new WebSocket(this.url);
      this.connection.onopen = this.handleOpen.bind(this);
      this.connection.onmessage = this.handleMessage.bind(this);
      this.connection.onclose = this.handleClose.bind(this);
      this.connection.onerror = this.handleError.bind(this);

      this.connectionTimeout = setTimeout(() => {
        if (this.connection && this.connection.readyState !== WebSocket.OPEN) {
          this.connection.close();
          this.connected = false;
          this.onClose({ code: 4000, reason: 'Connection timeout' });
        }
      }, 5000);
    } catch (error) {
      console.error('WebSocket initialization error:', error);
      this.onError(error);
    }
  }

  handleOpen(event) {
    this.connected = true;
    this.reconnectAttempts = 0;

    if (this.connectionTimeout) {
      clearTimeout(this.connectionTimeout);
      this.connectionTimeout = null;
    }

    this.onOpen(event);
  }

  handleMessage(event) {
    let data;
    try {
      data = JSON.parse(event.data);
    } catch (e) {
      console.error('Error parsing WebSocket message:', e);
      data = event.data;
    }

    this.onMessage({ data, originalEvent: event });
  }

  handleClose(event) {
    this.connected = false;

    if (event.code === 1000 || event.code === 1001) {
      this.onClose(event);
      return;
    }

    this.attemptReconnect();
    this.onClose(event);
  }

  handleError(error) {
    this.connected = false;
    this.attemptReconnect();
    this.onError(error);
  }

  attemptReconnect() {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
    }

    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      return;
    }

    this.reconnectAttempts++;
    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts - 1), 16000);

    this.reconnectTimeout = setTimeout(() => {
      if (!this.connected) {
        this.connect();
      }
    }, delay);
  }

  close() {
    if (this.connection) {
      this.connection.onclose = null;
      this.connection.close();
      this.connection = null;
      this.connected = false;
    }

    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }

    if (this.connectionTimeout) {
      clearTimeout(this.connectionTimeout);
      this.connectionTimeout = null;
    }
  }

  isConnected() {
    return this.connected;
  }

  sendMessage(message) {
    if (this.connection && this.connected) {
      const messageStr = typeof message === 'string' ? message : JSON.stringify(message);
      this.connection.send(messageStr);
      return true;
    }
    return false;
  }
}