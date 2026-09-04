'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import ReactMarkdown from 'react-markdown';
import { MessageSquare, Send, Sparkles, Plus, RefreshCw, Compass, Bot, User } from 'lucide-react';
import { chatService, authService } from '@/service';

export default function AIChatPage() {
  const router = useRouter();
  const [currentUser, setCurrentUser] = useState(null);
  const [conversations, setConversations] = useState([]);
  const [activeConversation, setActiveConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [messageInput, setMessageInput] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [streamingText, setStreamingText] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const selectConversation = async (conv) => {
    setActiveConversation(conv);
    setStreamingText('');
    try {
      const msgs = await chatService.getMessages(conv.id);
      setMessages(msgs);
    } catch (err) {
      console.error('Error fetching messages:', err);
    }
  };

  const loadData = async () => {
    setLoading(true);
    try {
      if (!authService.isAuthenticated()) {
        router.push('/login');
        return;
      }
      const user = authService.getCurrentUser() || (await authService.getMe());
      setCurrentUser(user);

      const convs = await chatService.getConversations();
      setConversations(convs);

      if (convs.length > 0) {
        selectConversation(convs[0]);
      }
    } catch (err) {
      if (err.response?.status === 401) {
        router.push('/login');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingText, sending]);

  const handleNewConversation = async () => {
    try {
      const newConv = await chatService.createConversation('Trip Planning Session');
      const updated = await chatService.getConversations();
      setConversations(updated);
      const target = updated.find((c) => c.id === newConv.id) || newConv;
      selectConversation(target);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to create new chat session');
    }
  };

  const formatMessageTime = (dateStr) => {
    if (!dateStr) return '';
    try {
      const date = new Date(dateStr);
      if (isNaN(date.getTime())) return '';
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch {
      return '';
    }
  };

  const handleSendMessage = async (e) => {
    e?.preventDefault();
    if (!messageInput.trim() || !activeConversation || sending) return;

    const textToSend = messageInput.trim();
    setMessageInput('');
    setStreamingText('');

    // Optimistic user message append
    const tempUserId = `temp-${Date.now()}`;
    const tempUserMsg = {
      id: tempUserId,
      conversation_id: activeConversation.id,
      sender: 'user',
      text: textToSend,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);
    setSending(true);

    let accumulatedText = '';

    try {
      await chatService.streamMessage(activeConversation.id, textToSend, {
        onUserMessage: (persistedUserMsg) => {
          setMessages((prev) =>
            prev.map((m) => (m.id === tempUserId ? persistedUserMsg : m))
          );
        },
        onTitle: (inferredTitle) => {
          setActiveConversation((prev) => (prev ? { ...prev, title: inferredTitle } : prev));
          setConversations((prev) =>
            prev.map((c) => (c.id === activeConversation.id ? { ...c, title: inferredTitle } : c))
          );
        },
        onChunk: (chunk) => {
          accumulatedText += chunk;
          setStreamingText(accumulatedText);
        },
        onDone: (savedAiMsg, finalTitle) => {
          setStreamingText('');
          setMessages((prev) => {
            const filtered = prev.filter((m) => m.id !== savedAiMsg.id);
            return [...filtered, savedAiMsg];
          });
          const targetTitle = finalTitle || activeConversation?.title;
          if (targetTitle) {
            setActiveConversation((prev) => (prev ? { ...prev, title: targetTitle } : prev));
            setConversations((prev) =>
              prev.map((c) =>
                c.id === activeConversation.id
                  ? { ...c, title: targetTitle, last_message: savedAiMsg }
                  : c
              )
            );
          }
        },
        onError: (errDetail) => {
          alert(errDetail || 'Error streaming AI response');
        },
      });
    } catch (err) {
      console.error('Error streaming message:', err);
    } finally {
      setSending(false);
      setStreamingText('');
    }
  };

  return (
    <div className="h-[calc(100vh-4rem)] bg-[#090d14] text-slate-100 flex flex-col md:flex-row overflow-hidden max-w-7xl mx-auto md:p-4 md:gap-4">
      {/* Left Sidebar: AI Chat Sessions */}
      <div className="w-full md:w-72 lg:w-80 bg-slate-900/80 border-r md:border border-slate-800 md:rounded-3xl flex flex-col shrink-0 h-1/4 md:h-full overflow-hidden backdrop-blur-xl">
        {/* Sidebar Header */}
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-xl bg-rose-600/15 text-rose-400">
              <Bot className="w-4 h-4" />
            </div>
            <h2 className="font-extrabold text-sm text-white">AI Travel Chat</h2>
          </div>

          <button
            onClick={handleNewConversation}
            className="p-1.5 rounded-xl bg-rose-600/20 hover:bg-rose-600 border border-rose-500/30 text-rose-300 hover:text-white transition-all text-xs flex items-center gap-1 font-semibold"
            title="Start new conversation"
          >
            <Plus className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">New</span>
          </button>
        </div>

        {/* Sessions list */}
        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {loading ? (
            <div className="text-center py-6 text-xs text-slate-500">Loading sessions...</div>
          ) : conversations.length === 0 ? (
            <div className="px-3 py-6 text-center text-xs text-slate-500">
              No sessions yet. Click New to start chatting with Kelana AI!
            </div>
          ) : (
            conversations.map((conv) => {
              const isSelected = activeConversation?.id === conv.id;
              return (
                <button
                  key={conv.id}
                  onClick={() => selectConversation(conv)}
                  className={`w-full p-2.5 rounded-2xl flex items-center gap-3 text-left transition-all ${
                    isSelected
                      ? 'bg-rose-950/40 border border-rose-500/40 text-white'
                      : 'hover:bg-slate-800/50 text-slate-300'
                  }`}
                >
                  <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-rose-600 to-red-500 flex items-center justify-center text-white shrink-0 shadow-sm">
                    <Sparkles className="w-4 h-4" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <span className="text-xs font-bold truncate block text-slate-100">
                      {conv.title || 'Travel Chat'}
                    </span>
                    <p className="text-[11px] text-slate-400 truncate mt-0.5">
                      {conv.last_message ? conv.last_message.text : 'Ask anything...'}
                    </p>
                  </div>
                </button>
              );
            })
          )}
        </div>
      </div>

      {/* Right Main Chat Window */}
      <div className="flex-1 bg-slate-900/80 md:border border-slate-800 md:rounded-3xl flex flex-col h-3/4 md:h-full overflow-hidden backdrop-blur-xl">
        {/* Chat Header */}
        <div className="px-6 py-4 border-b border-slate-800 bg-slate-950/40 flex items-center gap-3">
          <div className="w-9 h-9 rounded-2xl bg-gradient-to-tr from-rose-600 to-red-500 flex items-center justify-center text-white shadow-md shadow-rose-600/30">
            <Bot className="w-4 h-4" />
          </div>
          <h2 className="text-sm font-bold text-white">
            {activeConversation?.title || 'Kelana AI Travel Assistant'}
          </h2>
        </div>

        {/* Messages Stream */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4">
          {messages.map((msg) => {
            const isUser = msg.sender === 'user';
            return (
              <div
                key={msg.id}
                className={`flex items-start gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}
              >
                {!isUser && (
                  <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-rose-600 to-red-500 flex items-center justify-center text-white shrink-0 shadow-sm mt-1">
                    <Bot className="w-4 h-4" />
                  </div>
                )}

                <div className={`max-w-[85%] sm:max-w-xl flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
                  <div
                    className={`px-4 py-3 rounded-2xl text-xs sm:text-sm leading-relaxed shadow-md ${
                      isUser
                        ? 'bg-gradient-to-r from-rose-600 to-red-600 text-white rounded-br-none shadow-rose-600/20'
                        : 'bg-slate-800/90 text-slate-100 rounded-bl-none border border-slate-700/60 markdown-body'
                    }`}
                  >
                    {isUser ? (
                      msg.text
                    ) : (
                      <ReactMarkdown>{msg.text}</ReactMarkdown>
                    )}
                  </div>
                  <span className="text-[10px] text-slate-400 mt-1 px-1.5 font-medium">
                    {formatMessageTime(msg.created_at)}
                  </span>
                </div>

                {isUser && (
                  <div className="w-8 h-8 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300 shrink-0 mt-1">
                    <User className="w-4 h-4" />
                  </div>
                )}
              </div>
            );
          })}

          {/* Streaming chunk preview with cursor */}
          {streamingText && (
            <div className="flex items-start gap-3 justify-start">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-rose-600 to-red-500 flex items-center justify-center text-white shrink-0 shadow-sm mt-1">
                <Bot className="w-4 h-4" />
              </div>
              <div className="max-w-[85%] sm:max-w-xl flex flex-col items-start">
                <div className="px-4 py-3 rounded-2xl rounded-bl-none bg-slate-800/90 border border-slate-700/60 text-xs sm:text-sm leading-relaxed markdown-body shadow-md">
                  <ReactMarkdown>{streamingText}</ReactMarkdown>
                  <span className="inline-block w-1.5 h-3.5 ml-1 bg-rose-500 animate-pulse align-middle" />
                </div>
                <span className="text-[10px] text-rose-400 mt-1 px-1 flex items-center gap-1.5 font-medium">
                  <span className="w-1.5 h-1.5 rounded-full bg-rose-500 animate-ping inline-block" />
                  <span>Streaming live • {formatMessageTime(new Date().toISOString())}</span>
                </span>
              </div>
            </div>
          )}

          {/* Loading indicator spinner when requesting */}
          {sending && !streamingText && (
            <div className="flex items-start gap-3 justify-start">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-rose-600 to-red-500 flex items-center justify-center text-white shrink-0 shadow-sm mt-1">
                <Bot className="w-4 h-4" />
              </div>
              <div className="flex flex-col items-start">
                <div className="px-4 py-3 rounded-2xl rounded-bl-none bg-slate-800/90 border border-slate-700/60 flex items-center gap-1.5 shadow-md">
                  <span className="inline-block w-2 h-2 rounded-full bg-rose-500 animate-bounce" />
                  <span className="inline-block w-2 h-2 rounded-full bg-rose-500 animate-bounce [animation-delay:0.2s]" />
                  <span className="inline-block w-2 h-2 rounded-full bg-rose-500 animate-bounce [animation-delay:0.4s]" />
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <form
          onSubmit={handleSendMessage}
          className="p-3 sm:p-4 border-t border-slate-800 bg-slate-950/80 flex items-center gap-2"
        >
          <input
            type="text"
            placeholder="Ask Kelana AI about destinations, budgets, itineraries..."
            value={messageInput}
            onChange={(e) => setMessageInput(e.target.value)}
            disabled={sending}
            className="flex-1 px-4 py-2.5 bg-slate-900 border border-slate-800 rounded-2xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-rose-500 focus:ring-1 focus:ring-rose-500"
          />
          <button
            type="submit"
            disabled={!messageInput.trim() || sending}
            className="p-2.5 rounded-2xl bg-gradient-to-r from-rose-600 to-red-600 hover:from-rose-500 hover:to-red-500 text-white shadow-lg shadow-rose-600/30 transition-all disabled:opacity-50 hover:scale-105"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
}
