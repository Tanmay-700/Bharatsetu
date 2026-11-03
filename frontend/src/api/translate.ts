import { apiClient } from './client';

export interface TranslationResult {
  original_text: string;
  translated_text: string;
  source_language: string;
  target_language: string;
}

export const translateApi = {
  translate: async (
    text: string,
    targetLanguage: string,
    sourceLanguage: string = 'auto'
  ): Promise<TranslationResult> => {
    const res = await apiClient.post('/translate', {
      text,
      target_language: targetLanguage,
      source_language: sourceLanguage,
    });
    return res.data;
  },
};
