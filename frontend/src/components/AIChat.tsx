"use client"
import { useState, useRef, useEffect } from 'react';
import api from '@/lib/api';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface AIChatProps {
  context?: string;
  scenario?: string;
}

export default function AIChat({ context = "general conversation", scenario }: AIChatProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [aiAvailable, setAiAvailable] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    checkAIStatus();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const checkAIStatus = async () => {
    try {
      const response = await api.get('/ai/status');
      setAiAvailable(response.data.ollama_available && response.data.features.conversation);
    } catch (error) {
      console.error('Failed to check AI status:', error);
      setAiAvailable(false);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      // Prepare conversation history
      const history = messages.slice(-6).map(msg => ({
        role: msg.role,
        content: msg.content
      }));

      const response = await api.post('/ai/chat', {
        message: input,
        context,
        scenario,
        conversation_history: history
      });

      const aiMessage: Message = {
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error: any) {
      console.error('Chat error:', error);
      
      const errorMessage: Message = {
        role: 'assistant',
        content: error.response?.data?.detail || 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  if (!aiAvailable) {
    return (
      <div className="rounded-xl border bg-white dark:bg-zinc-900 p-8 text-center">
        <div className="text-6xl mb-4">🤖</div>
        <h3 className="text-xl font-semibold mb-2">AI Chat Not Available</h3>
        <p className="text-gray-600 dark:text-gray-400 mb-4">
          The AI conversation feature is currently disabled or Ollama is not running.
        </p>
        <div className="text-sm text-gray-500 space-y-1">
          <p>To enable AI chat:</p>
          <ol className="list-decimal list-inside space-y-1 mt-2">
            <li>Ensure Ollama container is running</li>
            <li>Pull the model: <code className="bg-gray-100 dark:bg-zinc-800 px-2 py-1 rounded">docker exec german_ollama ollama pull mistral:7b</code></li>
            <li>Set <code className="bg-gray-100 dark:bg-zinc-800 px-2 py-1 rounded">ENABLE_AI_CONVERSATION=true</code> in .env</li>
            <li>Restart the backend</li>
          </ol>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-[600px] rounded-xl border bg-white dark:bg-zinc-900 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b dark:border-zinc-800">
        <div>
          <h3 className="font-semibold">AI German Tutor</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            {context} {scenario && `• ${scenario}`}
          </p>
        </div>
        <button
          onClick={clearChat}
          className="px-3 py-1 text-sm text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-200 transition"
        >
          Clear
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 mt-8">
            <div className="text-4xl mb-2">💬</div>
            <p>Start a conversation in German!</p>
            <p className="text-sm mt-2">Try: &quot;Hallo! Wie geht es dir?&quot;</p>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-lg p-3 ${
                  msg.role === 'user'
                    ? 'bg-indigo-600 text-white'
                    : 'bg-gray-100 dark:bg-zinc-800 text-gray-900 dark:text-gray-100'
                }`}
              >
                <p className="whitespace-pre-wrap">{msg.content}</p>
                <span className="text-xs opacity-70 mt-1 block">
                  {msg.timestamp.toLocaleTimeString()}
                </span>
              </div>
            </div>
          ))
        )}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 dark:bg-zinc-800 rounded-lg p-3">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t dark:border-zinc-800">
        <div className="flex gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message in German..."
            className="flex-1 px-4 py-2 border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:bg-zinc-800 dark:border-zinc-700"
            rows={2}
            disabled={loading}
          />
          <button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition self-end"
          >
            {loading ? '...' : 'Send'}
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-2">
          Press Enter to send, Shift+Enter for new line
        </p>
      </div>
    </div>
  );
}
