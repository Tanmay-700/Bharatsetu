import React, { useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import { User, Sparkles, Copy, Check, Compass } from 'lucide-react';
import { Message, SourceCitation } from '../../types';
import { CitationCard } from './CitationCard';
import { formatMathContent } from '../../utils/mathFormatter';

interface ChatThreadProps {
  messages: Message[];
  isStreaming: boolean;
  streamingAnswer: string;
  streamingMetadata: {
    rewritten_query?: string;
    routed_domains?: string[];
    sources?: SourceCitation[];
  } | null;
  onTranslateCitation: (text: string) => void;
}

export const ChatThread: React.FC<ChatThreadProps> = ({
  messages,
  isStreaming,
  streamingAnswer,
  streamingMetadata,
  onTranslateCitation,
}) => {
  const bottomRef = useRef<HTMLDivElement>(null);
  const [copiedId, setCopiedId] = React.useState<string | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingAnswer]);

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="flex-1 overflow-y-auto px-4 py-6 space-y-6 max-w-4xl mx-auto w-full">
      {messages.length === 0 && !isStreaming && (
        <div className="text-center py-16 px-4">
          <div className="w-14 h-14 rounded-2xl bg-brand-50 border border-brand-200 text-brand-600 flex items-center justify-center mx-auto mb-4 shadow-sm">
            <Sparkles className="w-7 h-7" />
          </div>
          <h3 className="text-lg font-semibold text-slate-800">
            Welcome to BharatSetu
          </h3>
          <p className="text-sm text-slate-500 max-w-md mx-auto mt-1 leading-relaxed">
            Ask any question in your preferred language (Hindi, Tamil, Gujarati, Odia, etc.).
            BharatSetu retrieves cross-lingual evidence from indexed policies and textbooks.
          </p>

          <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-lg mx-auto text-left text-xs text-slate-600">
            <div className="p-3 bg-white border border-slate-200 rounded-xl shadow-xs">
              <span className="font-semibold text-slate-800 block mb-0.5">🏢 Company Policy Question</span>
              "मातृत्व अवकाश (Maternity Leave) की क्या शर्तें हैं?"
            </div>
            <div className="p-3 bg-white border border-slate-200 rounded-xl shadow-xs">
              <span className="font-semibold text-slate-800 block mb-0.5">⚡ Educational Science Question</span>
              "மின்னோட்டம் என்றால் என்ன? அதன் SI அலகு என்ன?"
            </div>
          </div>
        </div>
      )}

      {/* Render Historical Messages */}
      {messages.map((msg) => {
        const isUser = msg.role === 'user';
        return (
          <div
            key={msg.id}
            className={`flex items-start space-x-3 ${isUser ? 'justify-end' : 'justify-start'}`}
          >
            {!isUser && (
              <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-brand-600 to-emerald-500 flex items-center justify-center text-white flex-shrink-0 shadow-sm mt-0.5">
                <Sparkles className="w-4 h-4" />
              </div>
            )}

            <div className={`max-w-[85%] space-y-2 ${isUser ? 'items-end' : 'items-start'}`}>
              {/* Message Bubble */}
              <div
                className={`p-4 rounded-2xl text-sm leading-relaxed shadow-xs ${
                  isUser
                    ? 'bg-slate-900 text-white rounded-br-xs font-normal'
                    : 'bg-white border border-slate-200 text-slate-800 rounded-bl-xs'
                }`}
              >
                {/* Query rewrite tag if multi-turn */}
                {!isUser && msg.rewritten_question && msg.rewritten_question !== msg.original_question && (
                  <div className="mb-2.5 pb-2 border-b border-slate-100 flex items-center gap-1.5 text-xs text-brand-700 bg-brand-50/60 px-2 py-1 rounded">
                    <Compass className="w-3.5 h-3.5 flex-shrink-0 text-brand-600" />
                    <span>Resolved reference: <strong>{msg.rewritten_question}</strong></span>
                  </div>
                )}

                {isUser ? (
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                ) : (
                  <div className="prose prose-sm max-w-none prose-slate prose-p:leading-relaxed prose-pre:bg-slate-900 prose-pre:text-slate-100">
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm, remarkMath]}
                      rehypePlugins={[[rehypeKatex, { output: 'html' }]]}
                    >
                      {formatMathContent(msg.content)}
                    </ReactMarkdown>
                  </div>
                )}
              </div>

              {/* Citations Footer for Assistant */}
              {!isUser && msg.sources && msg.sources.length > 0 && (
                <div className="pt-2">
                  <div className="text-xs font-semibold text-slate-500 mb-2 flex items-center gap-1">
                    <span>📚 Verified Citations ({msg.sources.length}):</span>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {msg.sources.map((citation, idx) => (
                      <CitationCard
                        key={idx}
                        citation={citation}
                        index={idx + 1}
                        onTranslate={onTranslateCitation}
                      />
                    ))}
                  </div>
                </div>
              )}

              {/* Action buttons (Copy) */}
              {!isUser && (
                <div className="flex items-center space-x-2 text-xs text-slate-400 pl-1">
                  <button
                    onClick={() => handleCopy(msg.id, msg.content)}
                    className="hover:text-slate-600 flex items-center gap-1 transition-colors"
                  >
                    {copiedId === msg.id ? (
                      <>
                        <Check className="w-3.5 h-3.5 text-brand-600" />
                        <span className="text-brand-600">Copied</span>
                      </>
                    ) : (
                      <>
                        <Copy className="w-3.5 h-3.5" />
                        <span>Copy Answer</span>
                      </>
                    )}
                  </button>
                </div>
              )}
            </div>

            {isUser && (
              <div className="w-8 h-8 rounded-lg bg-slate-200 flex items-center justify-center text-slate-700 flex-shrink-0 mt-0.5">
                <User className="w-4 h-4" />
              </div>
            )}
          </div>
        );
      })}

      {/* Live Streaming Bubble */}
      {isStreaming && (
        <div className="flex items-start space-x-3 justify-start">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-brand-600 to-emerald-500 flex items-center justify-center text-white flex-shrink-0 shadow-sm animate-pulse">
            <Sparkles className="w-4 h-4" />
          </div>

          <div className="max-w-[85%] space-y-2">
            <div className="p-4 rounded-2xl text-sm leading-relaxed bg-white border border-brand-200 shadow-xs text-slate-800 rounded-bl-xs">
              {streamingMetadata?.rewritten_query && (
                <div className="mb-2 pb-2 border-b border-slate-100 flex items-center gap-1.5 text-xs text-brand-700 bg-brand-50 px-2 py-1 rounded">
                  <Compass className="w-3.5 h-3.5 flex-shrink-0 text-brand-600" />
                  <span>Jev routing domain: <strong>{streamingMetadata.routed_domains?.join(', ')}</strong></span>
                </div>
              )}

              {streamingAnswer ? (
                <div className="prose prose-sm max-w-none prose-slate">
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm, remarkMath]}
                    rehypePlugins={[[rehypeKatex, { output: 'html' }]]}
                  >
                    {formatMathContent(streamingAnswer)}
                  </ReactMarkdown>
                </div>
              ) : (
                <div className="flex items-center space-x-2 text-slate-500 text-xs py-1">
                  <div className="w-2 h-2 rounded-full bg-brand-500 animate-ping" />
                  <span>Searching multilingual vectors & synthesizing answer...</span>
                </div>
              )}
            </div>

            {/* Live Streaming Citations */}
            {streamingMetadata?.sources && streamingMetadata.sources.length > 0 && (
              <div className="pt-2">
                <div className="text-xs font-semibold text-slate-500 mb-2">
                  <span>📚 Retrieved Evidence Sources ({streamingMetadata.sources.length}):</span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {streamingMetadata.sources.map((citation, idx) => (
                    <CitationCard
                      key={idx}
                      citation={citation}
                      index={idx + 1}
                      onTranslate={onTranslateCitation}
                    />
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
};
