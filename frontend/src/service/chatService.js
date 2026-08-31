import api from './api';

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
};

export default chatService;
