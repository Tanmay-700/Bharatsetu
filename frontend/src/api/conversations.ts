import { apiClient } from './client';
import { Conversation } from '../types';

export const conversationsApi = {
  list: async (): Promise<Conversation[]> => {
    const res = await apiClient.get('/conversations');
    return res.data;
  },

  get: async (id: string): Promise<Conversation> => {
    const res = await apiClient.get(`/conversations/${id}`);
    return res.data;
  },

  create: async (default_language: string = 'hi', title: string = 'New Conversation'): Promise<Conversation> => {
    const res = await apiClient.post('/conversations', { default_language, title });
    return res.data;
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/conversations/${id}`);
  }
};
