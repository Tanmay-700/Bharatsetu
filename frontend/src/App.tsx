import React, { useState, useEffect, useRef } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { ChatThread } from './components/Chat/ChatThread';
import { ChatInput } from './components/Chat/ChatInput';
import { DocumentManager } from './components/Documents/DocumentManager';
import { TranslationDrawer } from './components/Translate/TranslationDrawer';
import { conversationsApi } from './api/conversations';
import { chatApi } from './api/chat';
import { Conversation, Message, SourceCitation } from './types';

export const App: React.FC = () => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null);
  const [activeTab, setActiveTab] = useState<'chat' | 'documents' | 'translate'>('chat');
  const [selectedLanguage, setSelectedLanguage] = useState<string>('hi');
  const [translateText, setTranslateText] = useState<string>('');

  // Streaming State
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingAnswer, setStreamingAnswer] = useState('');
  const [streamingMetadata, setStreamingMetadata] = useState<{
    rewritten_query?: string;
    routed_domains?: string[];
    sources?: SourceCitation[];
  } | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Load conversations on mount
  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      const convos = await conversationsApi.list();
      setConversations(convos);
      if (convos.length > 0 && !activeConversationId) {
        selectConversation(convos[0].id);
      } else if (convos.length === 0) {
        handleNewConversation();
      }
    } catch (err) {
      console.error('Failed to load conversations:', err);
    }
  };

  const selectConversation = async (id: string) => {
    setActiveConversationId(id);
    try {
      const full = await conversationsApi.get(id);
      setCurrentConversation(full);
      if (full.default_language) {
        setSelectedLanguage(full.default_language);
      }
    } catch (err) {
      console.error('Failed to get conversation details:', err);
    }
  };

  const handleNewConversation = async () => {
    try {
      const created = await conversationsApi.create(selectedLanguage, 'New Conversation');
      setConversations((prev) => [created, ...prev]);
      setActiveConversationId(created.id);
      setCurrentConversation(created);
      setActiveTab('chat');
    } catch (err) {
      console.error('Failed to create new conversation:', err);
    }
  };

  const handleDeleteConversation = async (id: string) => {
    try {
      await conversationsApi.delete(id);
      const remaining = conversations.filter((c) => c.id !== id);
      setConversations(remaining);
      if (activeConversationId === id) {
        if (remaining.length > 0) {
          selectConversation(remaining[0].id);
        } else {
          handleNewConversation();
        }
      }
    } catch (err) {
      console.error('Failed to delete conversation:', err);
    }
  };

  const handleSendMessage = async (question: string) => {
    if (!activeConversationId) return;

    // Optimistically append user message to local state
    const tempUserMsg: Message = {
      id: `temp_${Date.now()}`,
      conversation_id: activeConversationId,
      role: 'user',
      content: question,
      timestamp: new Date().toISOString(),
    };

    setCurrentConversation((prev) => {
      if (!prev) return null;
      return {
        ...prev,
        messages: [...(prev.messages || []), tempUserMsg],
      };
    });

    setIsStreaming(true);
    setStreamingAnswer('');
    setStreamingMetadata(null);

    let accumulatedAnswer = '';

    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    const controller = new AbortController();
    abortControllerRef.current = controller;

    await chatApi.streamMessage(
      activeConversationId,
      question,
      selectedLanguage,
      {
        onMetadata: (meta) => {
          setStreamingMetadata(meta);
        },
        onToken: (token) => {
          accumulatedAnswer += token;
          setStreamingAnswer(accumulatedAnswer);
        },
        onComplete: async () => {
          setIsStreaming(false);
          abortControllerRef.current = null;
          // Refresh conversation messages from backend to get saved assistant message & citations
          await selectConversation(activeConversationId);
          // Refresh conversation titles in sidebar
          const convos = await conversationsApi.list();
          setConversations(convos);
        },
        onError: (err) => {
          setIsStreaming(false);
          abortControllerRef.current = null;
          console.error('Chat streaming failed:', err);
        },
      },
      controller.signal
    );
  };

  const handleStopStreaming = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsStreaming(false);
  };

  const handleTranslateCitation = (text: string) => {
    setTranslateText(text);
    setActiveTab('translate');
  };

  return (
    <div className="flex h-screen overflow-hidden bg-slate-50">
      {/* Left Sidebar */}
      <Sidebar
        conversations={conversations}
        activeConversationId={activeConversationId}
        onSelectConversation={selectConversation}
        onNewConversation={handleNewConversation}
        onDeleteConversation={handleDeleteConversation}
        activeTab={activeTab}
        onSelectTab={setActiveTab}
      />

      {/* Main Workspace */}
      <div className="flex-1 flex flex-col h-screen overflow-hidden">
        <Header
          title={
            activeTab === 'chat'
              ? currentConversation?.title || 'Knowledge Assistant'
              : activeTab === 'documents'
              ? 'Document Repository'
              : 'Passage Translator'
          }
          selectedLanguage={selectedLanguage}
          onLanguageChange={setSelectedLanguage}
          activeDomain={streamingMetadata?.routed_domains?.[0]}
        />

        {/* View Switcher */}
        {activeTab === 'chat' && (
          <div className="flex-1 flex flex-col overflow-hidden">
            <ChatThread
              messages={currentConversation?.messages || []}
              isStreaming={isStreaming}
              streamingAnswer={streamingAnswer}
              streamingMetadata={streamingMetadata}
              onTranslateCitation={handleTranslateCitation}
            />
            <ChatInput
              onSendMessage={handleSendMessage}
              isLoading={isStreaming}
              selectedLanguage={selectedLanguage}
              onLanguageChange={setSelectedLanguage}
              onStop={handleStopStreaming}
            />
          </div>
        )}

        {activeTab === 'documents' && <DocumentManager />}

        {activeTab === 'translate' && <TranslationDrawer initialText={translateText} />}
      </div>
    </div>
  );
};

export default App;
