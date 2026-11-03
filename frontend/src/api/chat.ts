import { SourceCitation } from '../types';

export interface ChatStreamCallbacks {
  onMetadata?: (meta: {
    rewritten_query: string;
    routed_domains: string[];
    sources: SourceCitation[];
    answer_language: string;
  }) => void;
  onToken?: (token: string) => void;
  onComplete?: () => void;
  onError?: (error: Error) => void;
}

export const chatApi = {
  streamMessage: async (
    conversationId: string,
    question: string,
    answerLanguage: string,
    callbacks: ChatStreamCallbacks,
    signal?: AbortSignal
  ): Promise<void> => {
    try {
      const response = await fetch('/api/v1/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream',
        },
        body: JSON.stringify({
          conversation_id: conversationId,
          question: question,
          answer_language: answerLanguage,
        }),
        signal,
      });

      if (!response.ok) {
        throw new Error(`Chat API error: ${response.status} ${response.statusText}`);
      }

      if (!response.body) {
        throw new Error('ReadableStream not supported on this browser.');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed.startsWith('data:')) {
            const dataStr = trimmed.slice(5).trim();
            if (!dataStr) continue;

            try {
              const parsed = JSON.parse(dataStr);
              if (parsed.type === 'metadata' && callbacks.onMetadata) {
                callbacks.onMetadata({
                  rewritten_query: parsed.rewritten_query,
                  routed_domains: parsed.routed_domains,
                  sources: parsed.sources || [],
                  answer_language: parsed.answer_language,
                });
              } else if (parsed.type === 'token' && callbacks.onToken) {
                callbacks.onToken(parsed.content);
              } else if (parsed.type === 'done' && callbacks.onComplete) {
                callbacks.onComplete();
              }
            } catch (err) {
              console.warn('Failed to parse SSE JSON chunk:', dataStr, err);
            }
          }
        }
      }

      if (callbacks.onComplete) {
        callbacks.onComplete();
      }
    } catch (err: any) {
      if (err.name === 'AbortError' || signal?.aborted) {
        // User aborted the stream intentionally
        if (callbacks.onComplete) {
          callbacks.onComplete();
        }
        return;
      }
      if (callbacks.onError) {
        callbacks.onError(err);
      } else {
        console.error('Stream message error:', err);
      }
    }
  },
};
