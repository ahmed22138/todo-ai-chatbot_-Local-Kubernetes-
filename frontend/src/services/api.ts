/**
 * API client service for Todo AI Chatbot frontend.
 *
 * Handles communication with the backend API, including:
 * - Authentication header management
 * - Chat message posting
 * - Conversation management
 * - Error handling
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

export interface ChatMessage {
  message: string;
  conversation_id?: string;
}

export interface ToolCall {
  id: string;
  type: string;
  function: {
    name: string;
    arguments: Record<string, any>;
  };
}

export interface ToolResult {
  tool_call_id: string;
  tool_name: string;
  result: {
    success: boolean;
    message?: string;
    [key: string]: any;
  };
}

export interface ChatResponse {
  conversation_id: string;
  message: string;
  tool_calls?: ToolCall[] | null;
  tool_results?: ToolResult[] | null;
  timestamp: string;
}

export interface Conversation {
  id: string;
  title?: string;
  created_at: string;
  updated_at: string;
}

export interface ApiError {
  error: string;
  message: string;
}

/**
 * Get authentication token from localStorage or session.
 *
 * @returns {string | null} JWT token or null if not authenticated.
 */
function getAuthToken(): string | null {
  // Better Auth stores token in localStorage
  return localStorage.getItem('auth_token');
}

/**
 * Send a chat message to the backend API.
 *
 * @param {string} message - User's message.
 * @param {string} [conversationId] - Optional conversation ID to continue existing conversation.
 * @returns {Promise<ChatResponse>} - Assistant's response with tool call metadata.
 * @throws {Error} - If request fails or authentication is missing.
 */
export async function sendChatMessage(
  message: string,
  conversationId?: string
): Promise<ChatResponse> {
  const token = getAuthToken();

  if (!token) {
    throw new Error('Not authenticated. Please log in.');
  }

  const requestBody: ChatMessage = {
    message,
  };

  if (conversationId) {
    requestBody.conversation_id = conversationId;
  }

  const response = await fetch(`${API_BASE_URL}/api/chat/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(requestBody),
  });

  if (!response.ok) {
    const errorData: ApiError = await response.json().catch(() => ({
      error: 'Request failed',
      message: `Request failed with status ${response.status}`,
    }));

    throw new Error(errorData.message || 'Failed to send message');
  }

  const data: ChatResponse = await response.json();
  return data;
}

/**
 * Fetch all conversations for the current user.
 *
 * @returns {Promise<Conversation[]>} - List of conversations.
 * @throws {Error} - If request fails or authentication is missing.
 */
export async function getConversations(): Promise<Conversation[]> {
  const token = getAuthToken();

  if (!token) {
    throw new Error('Not authenticated. Please log in.');
  }

  const response = await fetch(`${API_BASE_URL}/api/conversations/`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch conversations');
  }

  const data = await response.json();
  return data.conversations || [];
}

/**
 * Fetch all messages in a conversation.
 *
 * @param {string} conversationId - ID of the conversation.
 * @returns {Promise<any[]>} - List of messages.
 * @throws {Error} - If request fails or authentication is missing.
 */
export async function getConversationMessages(conversationId: string): Promise<any[]> {
  const token = getAuthToken();

  if (!token) {
    throw new Error('Not authenticated. Please log in.');
  }

  const response = await fetch(
    `${API_BASE_URL}/api/conversations/${conversationId}/messages`,
    {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    }
  );

  if (!response.ok) {
    throw new Error('Failed to fetch conversation messages');
  }

  const data = await response.json();
  return data.messages || [];
}

/**
 * Check API health status.
 *
 * @returns {Promise<any>} - Health check response.
 */
export async function checkHealth(): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/health`, {
    method: 'GET',
  });

  if (!response.ok) {
    throw new Error('Health check failed');
  }

  return await response.json();
}
