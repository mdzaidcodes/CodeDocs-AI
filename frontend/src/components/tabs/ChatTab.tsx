'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import ReactMarkdown from 'react-markdown';
import Swal from 'sweetalert2';
import apiClient from '@/lib/api';
import type { ChatMessage } from '@/types';

interface ChatTabProps {
  projectId: string;
  isEmbeddingsReady?: boolean;
}

/**
 * Chat Tab Component
 * RAG-powered chat assistant for querying documentation
 */
export default function ChatTab({ projectId, isEmbeddingsReady = false }: ChatTabProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  /**
   * Scroll to bottom when messages change
   */
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  /**
   * Handle send message
   */
  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!inputMessage.trim() || isLoading) return;

    // Add user message to chat
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      // Send message to API
      const response = await apiClient.post(`/projects/${projectId}/chat`, {
        message: inputMessage,
      });

      // Add assistant response to chat
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.data.data.message,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error: any) {
      console.error('Chat error:', error);
      
      // Check if it's a message quota exceeded error
      if (error.response?.status === 429 || error.response?.data?.error_code === 'MESSAGE_QUOTA_EXCEEDED') {
        // Remove the user message since it wasn't processed
        setMessages((prev) => prev.slice(0, -1));
        
        // Show quota exceeded alert
        Swal.fire({
          icon: 'warning',
          title: 'Message Quota Exceeded',
          html: error.response?.data?.message || "You&apos;ve reached your daily limit of 5 messages. Your quota will reset tomorrow. Thank you for your understanding!",
          confirmButtonText: 'Understood',
          confirmButtonColor: '#3b82f6',
          background: '#1e293b',
          color: '#fff',
        });
      } else {
        // Add error message to chat for other errors
        const errorMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.',
          timestamp: new Date().toISOString(),
        };

        setMessages((prev) => [...prev, errorMessage]);
      }
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Handle Enter key press
   */
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(e);
    }
  };

  // Show loading state while embeddings are being created
  if (!isEmbeddingsReady) {
    return (
      <div className="flex flex-col items-center justify-center py-24 space-y-6">
        <Loader2 className="h-16 w-16 text-green-400 animate-spin" />
        <div className="text-center space-y-2">
          <p className="text-2xl font-bold text-white">Coming Soon...</p>
          <p className="text-gray-400">Chat assistant is being prepared in the background</p>
          <p className="text-sm text-gray-500">This usually takes 30-60 seconds</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-[calc(100vh-300px)]">
      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto bg-white/5 rounded-lg border border-white/10 p-4 mb-4">
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center">
            <div className="text-center">
              <Bot className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">
                Ask Me Anything
              </h3>
              <p className="text-gray-400 max-w-md">
                I can help you understand your code, explain functions, find specific
                implementations, and answer questions about your documentation.
              </p>
              <div className="mt-6 space-y-2">
                <p className="text-sm text-gray-400">Try asking:</p>
                <div className="flex flex-wrap gap-2 justify-center">
                  <button
                    onClick={() => setInputMessage("What does this project do?")}
                    className="text-sm bg-blue-500/20 text-blue-400 px-3 py-1 rounded-full hover:bg-blue-500/30 transition-colors"
                  >
                    What does this project do?
                  </button>
                  <button
                    onClick={() => setInputMessage("How do I set up this project?")}
                    className="text-sm bg-blue-500/20 text-blue-400 px-3 py-1 rounded-full hover:bg-blue-500/30 transition-colors"
                  >
                    How do I set up this project?
                  </button>
                  <button
                    onClick={() => setInputMessage("What are the main features?")}
                    className="text-sm bg-blue-500/20 text-blue-400 px-3 py-1 rounded-full hover:bg-blue-500/30 transition-colors"
                  >
                    What are the main features?
                  </button>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex items-start space-x-3 ${
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                {message.role === 'assistant' && (
                  <div className="flex-shrink-0 w-8 h-8 bg-blue-500/20 rounded-full flex items-center justify-center">
                    <Bot className="h-5 w-5 text-blue-400" />
                  </div>
                )}
                <div
                  className={`max-w-[80%] rounded-lg p-4 ${
                    message.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-white/10 text-gray-200'
                  }`}
                >
                  {message.role === 'assistant' ? (
                    <div className="text-sm prose prose-invert prose-sm max-w-none">
                      <ReactMarkdown
                        components={{
                          p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                          strong: ({ children }) => <strong className="font-bold text-white">{children}</strong>,
                          em: ({ children }) => <em className="italic">{children}</em>,
                          code: ({ children }) => (
                            <code className="bg-black/30 px-1.5 py-0.5 rounded text-blue-300 font-mono text-xs">
                              {children}
                            </code>
                          ),
                          ul: ({ children }) => <ul className="list-disc list-inside mb-2">{children}</ul>,
                          ol: ({ children }) => <ol className="list-decimal list-inside mb-2">{children}</ol>,
                          li: ({ children }) => <li className="mb-1">{children}</li>,
                        }}
                      >
                        {message.content}
                      </ReactMarkdown>
                    </div>
                  ) : (
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                  )}
                  <p className="text-xs mt-2 opacity-60">
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </p>
                </div>
                {message.role === 'user' && (
                  <div className="flex-shrink-0 w-8 h-8 bg-gray-500/20 rounded-full flex items-center justify-center">
                    <User className="h-5 w-5 text-gray-400" />
                  </div>
                )}
              </div>
            ))}
            {isLoading && (
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 w-8 h-8 bg-blue-500/20 rounded-full flex items-center justify-center">
                  <Bot className="h-5 w-5 text-blue-400" />
                </div>
                <div className="bg-white/10 rounded-lg p-4">
                  <Loader2 className="h-5 w-5 text-blue-400 animate-spin" />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Form */}
      <form onSubmit={handleSendMessage} className="flex space-x-2">
        <Textarea
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question about your code..."
          className="flex-1 min-h-[60px] max-h-[120px] bg-white/10 border-white/20 text-white placeholder:text-gray-400 resize-none"
          disabled={isLoading}
        />
        <Button
          type="submit"
          disabled={!inputMessage.trim() || isLoading}
          className="bg-blue-600 hover:bg-blue-700 px-6"
        >
          {isLoading ? (
            <Loader2 className="h-5 w-5 animate-spin" />
          ) : (
            <Send className="h-5 w-5" />
          )}
        </Button>
      </form>
      <p className="text-xs text-gray-400 mt-2 text-center">
        Press Enter to send, Shift+Enter for new line
      </p>
    </div>
  );
}

