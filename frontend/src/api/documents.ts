import { apiClient } from './client';
import { DocumentItem } from '../types';

export const documentsApi = {
  list: async (): Promise<DocumentItem[]> => {
    const res = await apiClient.get('/documents');
    return res.data;
  },

  listDomains: async (): Promise<string[]> => {
    const res = await apiClient.get('/documents/domains');
    return res.data;
  },

  upload: async (
    file: File,
    domain: string,
    documentType: string = 'Policy',
    language: string = 'en'
  ): Promise<DocumentItem> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('domain', domain);
    formData.append('document_type', documentType);
    formData.append('language', language);

    const res = await apiClient.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return res.data;
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/documents/${id}`);
  },

  getStatus: async (id: string): Promise<any> => {
    const res = await apiClient.get(`/documents/${id}/status`);
    return res.data;
  },
};
