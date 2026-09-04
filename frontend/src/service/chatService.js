import api from './api';
import authService from './authService';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const chatService = {
  async getConversations() {
    const response = await api.get('/conversations');
    return response.data;
  },

  async createConversation(title) {
    const response = await api.post('/conversations', {
      title: title || 'Trip Planning Chat',
    });
    return response.data;
  },

  async getMessages(conversationId) {
    const response = await api.get(`/conversations/${conversationId}/messages`);
    return response.data;
  },

  async sendMessage(conversationId, text) {
    const response = await api.post(`/conversations/${conversationId}/messages`, {
      text,
    });
    return response.data;
  },

  async streamMessage(conversationId, text, { onUserMessage, onChunk, onTitle, onDone, onError }) {
    const token = authService.getToken();
    try {
      const response = await fetch(`${BASE_URL}/conversations/${conversationId}/messages/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ text }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to stream response from AI');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // keep remainder

        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed.startsWith('data: ')) {
            try {
              const data = JSON.parse(trimmed.slice(6));
              if (data.type === 'user_message' && onUserMessage) {
                onUserMessage(data.message);
              } else if (data.type === 'chunk' && onChunk) {
                onChunk(data.text);
              } else if (data.type === 'title' && onTitle) {
                onTitle(data.title);
              } else if (data.type === 'done' && onDone) {
                onDone(data.message, data.title);
              } else if (data.type === 'error' && onError) {
                onError(data.detail);
              }
            } catch (e) {
              console.error('SSE JSON parse error:', e);
            }
          }
        }
      }
    } catch (err) {
      if (onError) onError(err.message || 'Stream error');
      throw err;
    }
  },
};

export default chatService;
