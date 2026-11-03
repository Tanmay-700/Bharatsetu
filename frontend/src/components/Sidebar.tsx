import React from 'react';
import { MessageSquare, Plus, BookOpen, Languages, Trash2, ShieldCheck } from 'lucide-react';
import { Conversation } from '../types';

interface SidebarProps {
  conversations: Conversation[];
  activeConversationId: string | null;
  onSelectConversation: (id: string) => void;
  onNewConversation: () => void;
  onDeleteConversation: (id: string) => void;
  activeTab: 'chat' | 'documents' | 'translate';
  onSelectTab: (tab: 'chat' | 'documents' | 'translate') => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewConversation,
  onDeleteConversation,
  activeTab,
  onSelectTab,
}) => {
  return (
    <aside className="w-72 bg-slate-900 text-slate-100 flex flex-col h-screen border-r border-slate-800 select-none">
      {/* Brand Header */}
      <div className="p-4 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-brand-600 to-amber-500 flex items-center justify-center font-bold text-white shadow-md">
            BS
          </div>
          <div>
            <h1 className="font-bold text-base tracking-tight text-white flex items-center gap-1.5">
              BharatSetu
            </h1>
            <p className="text-xs text-slate-400 font-medium">Multilingual AI Companion</p>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="p-3 border-b border-slate-800 space-y-1">
        <button
          onClick={() => onSelectTab('chat')}
          className={`w-full flex items-center space-x-2.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
            activeTab === 'chat'
              ? 'bg-slate-800 text-brand-500 font-semibold'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
          }`}
        >
          <MessageSquare className="w-4 h-4" />
          <span>Study & Knowledge Chat</span>
        </button>

        <button
          onClick={() => onSelectTab('documents')}
          className={`w-full flex items-center space-x-2.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
            activeTab === 'documents'
              ? 'bg-slate-800 text-brand-500 font-semibold'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
          }`}
        >
          <BookOpen className="w-4 h-4" />
          <span>Document Vault (20 PDFs)</span>
        </button>

        <button
          onClick={() => onSelectTab('translate')}
          className={`w-full flex items-center space-x-2.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
            activeTab === 'translate'
              ? 'bg-slate-800 text-brand-500 font-semibold'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
          }`}
        >
          <Languages className="w-4 h-4" />
          <span>Passage Translator</span>
        </button>
      </div>

      {/* New Chat Button */}
      <div className="p-3">
        <button
          onClick={onNewConversation}
          className="w-full flex items-center justify-center space-x-2 px-3 py-2.5 bg-brand-600 hover:bg-brand-500 text-white rounded-lg text-sm font-medium transition-colors shadow-sm"
        >
          <Plus className="w-4 h-4" />
          <span>New Conversation</span>
        </button>
      </div>

      {/* Chat History List */}
      <div className="flex-1 overflow-y-auto px-2 py-1 space-y-1">
        <div className="px-3 py-1.5 text-xs font-semibold text-slate-500 uppercase tracking-wider">
          Conversations
        </div>

        {conversations.length === 0 ? (
          <div className="px-3 py-6 text-center text-xs text-slate-500">
            No conversations yet.<br />Click "New Conversation" to start.
          </div>
        ) : (
          conversations.map((convo) => {
            const isActive = convo.id === activeConversationId && activeTab === 'chat';
            return (
              <div
                key={convo.id}
                className={`group flex items-center justify-between px-3 py-2 rounded-lg text-sm transition-colors cursor-pointer ${
                  isActive
                    ? 'bg-slate-800 text-slate-100 font-medium'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
                onClick={() => {
                  onSelectConversation(convo.id);
                  onSelectTab('chat');
                }}
              >
                <div className="truncate flex-1 pr-2">
                  <div className="truncate">{convo.title}</div>
                  <div className="text-[10px] text-slate-500 flex items-center gap-1.5 mt-0.5">
                    <span className="uppercase">{convo.default_language}</span>
                    <span>•</span>
                    <span>{convo.message_count} messages</span>
                  </div>
                </div>

                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteConversation(convo.id);
                  }}
                  className="opacity-0 group-hover:opacity-100 p-1 text-slate-500 hover:text-red-400 transition-opacity"
                  title="Delete conversation"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            );
          })
        )}
      </div>

      {/* Footer Info */}
      <div className="p-3 border-t border-slate-800 bg-slate-950/40 text-xs text-slate-400 flex items-center justify-between">
        <div className="flex items-center space-x-1.5">
          <ShieldCheck className="w-4 h-4 text-brand-500" />
          <span>Zero-Cost Local Stack</span>
        </div>
        <span className="text-[10px] bg-slate-800 text-slate-300 px-1.5 py-0.5 rounded font-mono">
          bge-m3
        </span>
      </div>
    </aside>
  );
};
