/**
 * MessageList component - displays conversation history.
 *
 * Features:
 * - Displays all messages in chronological order
 * - Shows tool call results as badges
 * - Auto-scrolls to latest message
 * - Differentiates user and assistant messages
 */

import React, { useEffect, useRef } from 'react';
import {
  MessageList as ChatKitMessageList,
  Message as ChatKitMessage,
  TypingIndicator,
} from '@chatscope/chat-ui-kit-react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  tool_calls?: any[] | null;
  tool_results?: any[] | null;
  timestamp: string;
}

interface MessageListProps {
  messages: Message[];
  isTyping?: boolean;
}

export const MessageList: React.FC<MessageListProps> = ({
  messages,
  isTyping = false,
}) => {
  const messageListRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (messageListRef.current) {
      messageListRef.current.scrollTop = messageListRef.current.scrollHeight;
    }
  }, [messages]);

  const renderToolCalls = (toolResults?: any[] | null) => {
    if (!toolResults || toolResults.length === 0) {
      return null;
    }

    return (
      <div className="tool-results">
        {toolResults.map((result, index) => (
          <span
            key={index}
            className={`tool-badge ${result.result.success ? 'success' : 'error'}`}
          >
            {result.tool_name}: {result.result.message || 'Executed'}
          </span>
        ))}
      </div>
    );
  };

  return (
    <div ref={messageListRef} className="message-list-container">
      <ChatKitMessageList
        typingIndicator={
          isTyping ? <TypingIndicator content="Assistant is thinking..." /> : undefined
        }
      >
        {messages.map((msg) => (
          <ChatKitMessage
            key={msg.id}
            model={{
              message: msg.content,
              sender: msg.role === 'user' ? 'You' : 'Assistant',
              direction: msg.role === 'user' ? 'outgoing' : 'incoming',
              position: 'single',
            }}
          >
            {msg.role === 'assistant' && msg.tool_results && (
              <ChatKitMessage.Footer>
                {renderToolCalls(msg.tool_results)}
              </ChatKitMessage.Footer>
            )}
          </ChatKitMessage>
        ))}
      </ChatKitMessageList>
    </div>
  );
};

export default MessageList;
