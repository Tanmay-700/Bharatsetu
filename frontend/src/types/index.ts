export interface Language {
  code: string;
  name: string;
  native: string;
}

export const SUPPORTED_LANGUAGES: Language[] = [
  { code: 'hi', name: 'Hindi', native: 'हिन्दी' },
  { code: 'en', name: 'English', native: 'English' },
  { code: 'ta', name: 'Tamil', native: 'தமிழ்' },
  { code: 'gu', name: 'Gujarati', native: 'ગુજરાતી' },
  { code: 'kn', name: 'Kannada', native: 'ಕನ್ನಡ' },
  { code: 'mr', name: 'Marathi', native: 'मराठी' },
  { code: 'pa', name: 'Punjabi', native: 'ਪੰਜਾਬੀ' },
  { code: 'od', name: 'Odia', native: 'ଓଡ଼ିଆ' },
];

export interface SourceCitation {
  chunk_id: string;
  document_name: string;
  domain: string;
  section: string;
  page_number: number;
  score: number;
  content_preview: string;
}

export interface Message {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant';
  content: string;
  original_question?: string;
  rewritten_question?: string;
  answer_language?: string;
  sources?: SourceCitation[];
  timestamp: string;
}

export interface Conversation {
  id: string;
  user_id: string;
  title: string;
  default_language: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  messages?: Message[];
}

export interface DocumentItem {
  id: string;
  filename: string;
  domain: string;
  document_type: string;
  language: string;
  total_pages: number;
  total_chunks: number;
  status: 'processing' | 'completed' | 'failed';
  error_message?: string;
  uploaded_at: string;
}
