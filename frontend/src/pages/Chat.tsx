/**
 * Chat page - main chat interface with state management and API integration.
 *
 * Features:
 * - Manages chat state (messages, conversation ID, loading, errors)
 * - Sends messages to backend API
 * - Updates UI with assistant responses
 * - Handles errors gracefully
 * - Persists conversation across page sessions (localStorage)
 * - Loads conversation history on mount
 * - Allows switching between conversations
 */

import React, { useState, useEffect } from 'react';
import { ChatInterface } from '../components/ChatInterface';
import {
  sendChatMessage,
  ChatResponse,
  getConversations,
  getConversationMessages,
  Conversation,
} from '../services/api';
import { logout } from '../services/auth';
import './Chat.css';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  tool_calls?: any[] | null;
  tool_results?: any[] | null;
  timestamp: string;
}

export const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  // Show sidebar by default on desktop (window width > 1024px)
  const [showSidebar, setShowSidebar] = useState(
    typeof window !== 'undefined' && window.innerWidth > 1024
  );

  // Load conversation list on mount
  useEffect(() => {
    loadConversations();
  }, []);

  // Load conversation from localStorage on mount
  useEffect(() => {
    const savedConversationId = localStorage.getItem('current_conversation_id');
    const savedMessages = localStorage.getItem('current_conversation_messages');

    if (savedConversationId && savedMessages) {
      setConversationId(savedConversationId);
      try {
        setMessages(JSON.parse(savedMessages));
      } catch (e) {
        console.error('Failed to load saved messages:', e);
      }
    }
  }, []);

  // Save conversation to localStorage when it changes
  useEffect(() => {
    if (conversationId && messages.length > 0) {
      localStorage.setItem('current_conversation_id', conversationId);
      localStorage.setItem('current_conversation_messages', JSON.stringify(messages));
    }
  }, [conversationId, messages]);

  const loadConversations = async () => {
    try {
      const convs = await getConversations();
      setConversations(convs);
    } catch (err: any) {
      console.error('Failed to load conversations:', err);
    }
  };

  const handleSwitchConversation = async (convId: string) => {
    try {
      setIsLoading(true);
      setError(null);

      // Fetch full message history for this conversation
      const msgs = await getConversationMessages(convId);

      setConversationId(convId);
      setMessages(msgs);
      setShowSidebar(false);

      // Save to localStorage
      localStorage.setItem('current_conversation_id', convId);
      localStorage.setItem('current_conversation_messages', JSON.stringify(msgs));
    } catch (err: any) {
      console.error('Failed to switch conversation:', err);
      setError(err.message || 'Failed to load conversation');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (messageText: string) => {
    // Clear any previous errors
    setError(null);

    // Create temporary user message
    const tempUserMessage: Message = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content: messageText,
      timestamp: new Date().toISOString(),
    };

    // Add user message to UI immediately
    setMessages((prev) => [...prev, tempUserMessage]);
    setIsLoading(true);

    try {
      // Send message to backend
      const response: ChatResponse = await sendChatMessage(
        messageText,
        conversationId || undefined
      );

      // Update conversation ID if this is a new conversation
      if (!conversationId) {
        setConversationId(response.conversation_id);
        // Reload conversations list to include the new one
        loadConversations();
      }

      // Update temp user message with real ID
      setMessages((prev) => {
        const updatedMessages = prev.map((msg) =>
          msg.id === tempUserMessage.id
            ? { ...msg, id: `user-${Date.now()}` }
            : msg
        );

        // Add assistant response
        const assistantMessage: Message = {
          id: `assistant-${Date.now()}`,
          role: 'assistant',
          content: response.message,
          tool_calls: response.tool_calls,
          tool_results: response.tool_results,
          timestamp: response.timestamp,
        };

        return [...updatedMessages, assistantMessage];
      });
    } catch (err: any) {
      console.error('Failed to send message:', err);
      setError(err.message || 'Failed to send message. Please try again.');

      // Remove temporary user message on error
      setMessages((prev) => prev.filter((msg) => msg.id !== tempUserMessage.id));
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewConversation = () => {
    setMessages([]);
    setConversationId(null);
    setError(null);
    localStorage.removeItem('current_conversation_id');
    localStorage.removeItem('current_conversation_messages');
  };

  const handleLogout = () => {
    logout();
    window.location.reload();
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="chat-page">
      <div className="chat-header">
        <div className="header-left">
          <button
            onClick={() => setShowSidebar(!showSidebar)}
            className="sidebar-toggle"
            title="Toggle conversation history"
          >
            ☰
          </button>
          <h1>Todo AI Chatbot</h1>
        </div>
        <div className="header-right">
          <button
            onClick={handleNewConversation}
            className="new-conversation-btn"
            disabled={isLoading}
          >
            New Conversation
          </button>
          <button
            onClick={handleLogout}
            className="logout-btn"
            title="Logout"
          >
            Logout
          </button>
        </div>
      </div>

      <div className="chat-container">
        {/* Sidebar overlay for mobile */}
        <div
          className={`sidebar-overlay ${showSidebar ? 'show' : ''}`}
          onClick={() => setShowSidebar(false)}
        />

        <div className={`conversations-sidebar ${showSidebar ? 'open' : ''}`}>
          <h3>Conversations</h3>
          <div className="conversations-list">
            {conversations.length === 0 ? (
              <p className="no-conversations">No previous conversations</p>
            ) : (
              conversations.map((conv) => (
                <div
                  key={conv.id}
                  className={`conversation-item ${
                    conv.id === conversationId ? 'active' : ''
                  }`}
                  onClick={() => handleSwitchConversation(conv.id)}
                >
                  <div className="conversation-title">
                    {conv.title || `Conversation ${conv.id.substring(0, 8)}...`}
                  </div>
                  <div className="conversation-meta">
                    {formatDate(conv.updated_at)}
                    {(conv as any).message_count && (
                      <span> · {(conv as any).message_count} messages</span>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="chat-main">
          <ChatInterface
            messages={messages}
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
            error={error}
            conversationId={conversationId}
          />
        </div>
      </div>
    </div>
  );
};

export default Chat;
