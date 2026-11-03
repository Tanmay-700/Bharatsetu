import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, Square } from 'lucide-react';
import { SUPPORTED_LANGUAGES } from '../../types';

interface ChatInputProps {
  onSendMessage: (question: string) => void;
  isLoading: boolean;
  selectedLanguage: string;
  onLanguageChange: (lang: string) => void;
  onStop?: () => void;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  isLoading,
  selectedLanguage,
  onLanguageChange,
  onStop,
}) => {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 140)}px`;
    }
  }, [input]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    onSendMessage(input.trim());
    setInput('');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Escape' && isLoading && onStop) {
      e.preventDefault();
      onStop();
      return;
    }
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleQuickPrompt = (promptText: string) => {
    onSendMessage(promptText);
  };

  return (
    <div className="border-t border-slate-200 bg-white p-4 flex-shrink-0 z-10">
      <div className="max-w-4xl mx-auto space-y-2.5">
        {/* Quick Follow-up Suggestions Bar */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs text-slate-500">
          <span className="flex-shrink-0 flex items-center gap-1 font-medium text-slate-400">
            <Sparkles className="w-3 h-3 text-amber-500" />
            Try follow-up:
          </span>
          <button
            onClick={() => handleQuickPrompt("What is its SI unit?")}
            className="flex-shrink-0 px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-full transition-colors"
          >
            "What is its SI unit?"
          </button>
          <button
            onClick={() => handleQuickPrompt("Explain this in simple points")}
            className="flex-shrink-0 px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-full transition-colors"
          >
            "Explain this in simple points"
          </button>
          <button
            onClick={() => handleQuickPrompt("Are there any exceptions to this rule?")}
            className="flex-shrink-0 px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-full transition-colors"
          >
            "Are there any exceptions to this rule?"
          </button>
        </div>

        {/* Input Card */}
        <form
          onSubmit={handleSubmit}
          className="relative flex items-end bg-slate-50 border border-slate-300 rounded-2xl p-2 focus-within:ring-2 focus-within:ring-brand-500 focus-within:border-transparent transition-all shadow-xs"
        >
          <textarea
            ref={textareaRef}
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask anything in English, Hindi, Tamil, Gujarati, etc... (Shift + Enter for new line)"
            className="w-full resize-none bg-transparent px-3 py-1.5 text-sm text-slate-800 placeholder-slate-400 focus:outline-none max-h-36"
            disabled={isLoading}
          />

          <div className="flex items-center space-x-2 pl-2">
            <select
              value={selectedLanguage}
              onChange={(e) => onLanguageChange(e.target.value)}
              className="text-[11px] font-semibold bg-white border border-slate-200 rounded-lg px-2 py-1.5 text-slate-700 hover:bg-slate-100 cursor-pointer focus:outline-none"
              title="Target output language"
            >
              {SUPPORTED_LANGUAGES.map((l) => (
                <option key={l.code} value={l.code}>
                  {l.name}
                </option>
              ))}
            </select>

            {isLoading ? (
              <button
                type="button"
                onClick={onStop}
                className="flex items-center space-x-1.5 px-3 py-1.5 bg-rose-50 text-rose-700 hover:bg-rose-100 border border-rose-200 rounded-xl transition-all shadow-xs text-xs font-semibold cursor-pointer animate-pulse"
                title="Stop generating (Cancel)"
              >
                <Square className="w-3.5 h-3.5 fill-rose-600 text-rose-600" />
                <span className="hidden sm:inline">Stop</span>
              </button>
            ) : (
              <button
                type="submit"
                disabled={!input.trim()}
                className={`p-2 rounded-xl transition-all ${
                  input.trim()
                    ? 'bg-brand-600 text-white hover:bg-brand-500 shadow-sm cursor-pointer'
                    : 'bg-slate-200 text-slate-400 cursor-not-allowed'
                }`}
                title="Send message"
              >
                <Send className="w-4 h-4" />
              </button>
            )}
          </div>
        </form>

        <p className="text-[11px] text-center text-slate-400">
          BharatSetu is grounded in indexed documents. Answers are derived from evidence with zero pre-translation.
        </p>
      </div>
    </div>
  );
};
