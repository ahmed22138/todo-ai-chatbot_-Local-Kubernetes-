/**
 * Modern ChatInterface component - beautiful chat UI with smooth interactions.
 */

import React, { useRef, useEffect, useState } from 'react';
import './ChatInterface.css';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  tool_calls?: any[] | null;
  tool_results?: any[] | null;
  timestamp: string;
}

interface ChatInterfaceProps {
  messages: Message[];
  onSendMessage: (message: string) => void;
  isLoading?: boolean;
  error?: string | null;
  conversationId?: string | null;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  messages,
  onSendMessage,
  isLoading = false,
  error = null,
}) => {
  const [inputText, setInputText] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [inputText]);

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!inputText.trim() || isLoading) return;

    onSendMessage(inputText.trim());
    setInputText('');

    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  const suggestions = [
    "Add a task to buy groceries",
    "Show me all my tasks",
    "Mark my first task as complete",
    "Delete completed tasks"
  ];

  return (
    <div className="chat-interface">
      <div className="messages-container">
        {messages.length === 0 && !isLoading && (
          <div className="empty-state">
            <div className="empty-state-icon">💬</div>
            <h3>Start a conversation</h3>
            <p>Ask me anything about your tasks! I can help you add, view, complete, update, or delete tasks using natural language.</p>
            <div className="suggestion-chips">
              {suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  className="suggestion-chip"
                  onClick={() => {
                    setInputText(suggestion);
                    textareaRef.current?.focus();
                  }}
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((message) => (
          <div key={message.id} className={`message ${message.role}`}>
            <div className="message-wrapper">
              <div className="message-avatar">
                {message.role === 'user' ? '👤' : '🤖'}
              </div>
              <div className="message-content">
                {message.content}
                {message.tool_results && message.tool_results.length > 0 && (
                  <div className="tool-calls">
                    {message.tool_results.map((result: any, idx: number) => (
                      <div key={idx} className="tool-call-item">
                        <div className="tool-call-name">
                          {result.tool_name || 'Action'}
                        </div>
                        <div className="tool-call-result">
                          {result.result?.message || JSON.stringify(result.result)}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
                <div className="message-timestamp">{formatTime(message.timestamp)}</div>
              </div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="message assistant">
            <div className="message-wrapper">
              <div className="message-avatar">🤖</div>
              <div className="typing-indicator">
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {error && (
        <div className="error-message">
          <span className="error-icon">⚠</span>
          {error}
        </div>
      )}

      <div className="input-area">
        <form onSubmit={handleSubmit} className="input-container">
          <div className="input-wrapper">
            <textarea
              ref={textareaRef}
              className="message-input"
              placeholder="Type your message... (Shift+Enter for new line)"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isLoading}
              rows={1}
            />
            {inputText.length > 0 && (
              <span className="char-count">{inputText.length}/500</span>
            )}
          </div>
          <button
            type="submit"
            className="send-button"
            disabled={!inputText.trim() || isLoading}
          >
            {isLoading ? '⏳' : '➤'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatInterface;
