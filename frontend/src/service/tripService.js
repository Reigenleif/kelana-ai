import api from './api';

export const tripService = {
  async getTrips() {
    const response = await api.get('/trips');
    return response.data;
  },

  async getTrip(tripId) {
    const response = await api.get(`/trips/${tripId}`);
    return response.data;
  },

  async createTrip(tripData) {
    const response = await api.post('/trips', tripData);
    return response.data;
  },

  async updateTrip(tripId, tripData) {
    const response = await api.put(`/trips/${tripId}`, tripData);
    return response.data;
  },

  async deleteTrip(tripId) {
    const response = await api.delete(`/trips/${tripId}`);
    return response.data;
  },

  async generateRecommendation(tripId, forceRefresh = false) {
    const response = await api.post(`/trips/${tripId}/generate${forceRefresh ? '?force_refresh=true' : ''}`);
    return response.data;
  },

  async getStaticRecommendations() {
    const response = await api.get('/recommendations');
    return response.data;
  },

  async getTransportations() {
    const response = await api.get('/transportations');
    return response.data;
  },
};

export default tripService;
