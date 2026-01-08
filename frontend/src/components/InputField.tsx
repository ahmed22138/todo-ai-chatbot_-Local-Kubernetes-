/**
 * InputField component - handles user message input.
 *
 * Features:
 * - Text input for messages
 * - Send button
 * - Enter key submission (Shift+Enter for new line)
 * - Disabled state during message sending
 * - Auto-clear after send
 */

import React, { useState, KeyboardEvent } from 'react';
import {
  MessageInput,
} from '@chatscope/chat-ui-kit-react';

interface InputFieldProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export const InputField: React.FC<InputFieldProps> = ({
  onSendMessage,
  disabled = false,
  placeholder = 'Type your message...',
}) => {
  const [message, setMessage] = useState('');

  const handleSend = () => {
    const trimmedMessage = message.trim();
    if (trimmedMessage && !disabled) {
      onSendMessage(trimmedMessage);
      setMessage('');
    }
  };

  const handleKeyPress = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    // Send on Enter, but allow Shift+Enter for new lines
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="input-field-container">
      <MessageInput
        placeholder={placeholder}
        value={message}
        onChange={(val) => setMessage(val)}
        onSend={handleSend}
        disabled={disabled}
        attachButton={false}
        sendButton={true}
        onKeyPress={handleKeyPress as any}
      />
    </div>
  );
};

export default InputField;
