'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import ReactMarkdown from 'react-markdown';
import { MessageSquare, Send, Sparkles, Plus, RefreshCw, Compass, Bot, User, ArrowLeft } from 'lucide-react';
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
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
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
  }, [messages, sending]);

  const selectConversation = async (conv) => {
    setActiveConversation(conv);
    try {
      const msgs = await chatService.getMessages(conv.id);
      setMessages(msgs);
    } catch (err) {
      console.error('Error fetching messages:', err);
    }
  };

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

  const handleSendMessage = async (e) => {
    e?.preventDefault();
    if (!messageInput.trim() || !activeConversation || sending) return;

    const textToSend = messageInput.trim();
    setMessageInput('');

    // Optimistic user message append
    const tempUserMsg = {
      id: Date.now(),
      conversation_id: activeConversation.id,
      sender: 'user',
      text: textToSend,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);
    setSending(true);

    try {
      const returnedMsgs = await chatService.sendMessage(activeConversation.id, textToSend);
      // Update with server returned messages
      setMessages((prev) => {
        const withoutTemp = prev.filter((m) => m.id !== tempUserMsg.id);
        return [...withoutTemp, ...returnedMsgs];
      });

      // Update last message in conversation list
      const latestAi = returnedMsgs[returnedMsgs.length - 1];
      setConversations((prev) =>
        prev.map((c) => (c.id === activeConversation.id ? { ...c, last_message: latestAi } : c))
      );
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to send message to AI assistant');
    } finally {
      setSending(false);
    }
  };

  const icebreakers = [
    "Recommend top hidden gems in Kyoto",
    "What is a realistic 5-day budget for Bali?",
    "Plan a weekend getaway itinerary in the Swiss Alps",
  ];

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
            <div>
              <h2 className="font-extrabold text-sm text-white">AI Travel Chat</h2>
              <p className="text-[10px] text-slate-400">Assistant Sessions</p>
            </div>
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
        <div className="px-6 py-3.5 border-b border-slate-800 bg-slate-950/40 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-rose-600 to-red-500 flex items-center justify-center text-white shadow-md shadow-rose-600/30">
              <Bot className="w-5 h-5" />
            </div>
            <div>
              <div className="text-sm font-bold text-white flex items-center gap-2">
                <span>Kelana AI Travel Assistant</span>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-500/20 border border-rose-500/40 text-rose-300">
                  RAG Ready
                </span>
              </div>
              <div className="text-[11px] text-slate-400">
                Powered by AWS Bedrock • Ready to plan your dream trips
              </div>
            </div>
          </div>

          <div className="hidden sm:flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-800/80 border border-slate-700 text-slate-300 text-xs">
            <Sparkles className="w-3.5 h-3.5 text-rose-400" />
            <span>AI Travel Assistant</span>
          </div>
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
                  <span className="text-[10px] text-slate-400 mt-1 px-1">
                    {new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
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

          {sending && (
            <div className="flex items-start gap-3 justify-start">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-rose-600 to-red-500 flex items-center justify-center text-white shrink-0 shadow-sm mt-1">
                <Bot className="w-4 h-4" />
              </div>
              <div className="px-4 py-3 rounded-2xl rounded-bl-none bg-slate-800/90 border border-slate-700/60 flex items-center gap-2 text-xs text-slate-400">
                <span className="inline-block w-2 h-2 rounded-full bg-rose-500 animate-bounce" />
                <span className="inline-block w-2 h-2 rounded-full bg-rose-500 animate-bounce [animation-delay:0.2s]" />
                <span className="inline-block w-2 h-2 rounded-full bg-rose-500 animate-bounce [animation-delay:0.4s]" />
                <span className="ml-1 text-slate-400">Kelana AI is thinking...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Icebreaker Prompts */}
        <div className="px-4 py-2 bg-slate-950/60 border-t border-slate-800 flex items-center gap-2 overflow-x-auto scrollbar-none">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider shrink-0">
            Suggested:
          </span>
          {icebreakers.map((prompt, i) => (
            <button
              key={i}
              type="button"
              onClick={() => setMessageInput(prompt)}
              className="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 hover:border-rose-500/40 text-[11px] text-slate-300 hover:text-white whitespace-nowrap transition-colors"
            >
              {prompt}
            </button>
          ))}
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
