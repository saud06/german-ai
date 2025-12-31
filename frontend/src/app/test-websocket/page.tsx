'use client';

import { useState, useEffect, useRef } from 'react';
import RequireAuth from '@/components/RequireAuth';

interface Message {
  id: number;
  type: 'sent' | 'received' | 'system';
  content: string;
  timestamp: Date;
}

export default function TestWebSocketPage() {
  const [connected, setConnected] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [connectionStatus, setConnectionStatus] = useState<'disconnected' | 'connecting' | 'connected' | 'error'>('disconnected');
  const wsRef = useRef<WebSocket | null>(null);
  const messageIdRef = useRef(0);

  const addMessage = (type: Message['type'], content: string) => {
    setMessages(prev => [...prev, {
      id: messageIdRef.current++,
      type,
      content,
      timestamp: new Date()
    }]);
  };

  const connect = () => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      addMessage('system', 'Already connected');
      return;
    }

    setConnectionStatus('connecting');
    addMessage('system', 'Connecting to WebSocket server...');

    try {
      const token = localStorage.getItem('token');
      const ws = new WebSocket(`ws://localhost:8000/api/v1/ws/test?token=${token}`);

      ws.onopen = () => {
        setConnected(true);
        setConnectionStatus('connected');
        addMessage('system', '✅ Connected to WebSocket server');
      };

      ws.onmessage = (event) => {
        addMessage('received', event.data);
      };

      ws.onerror = (error) => {
        setConnectionStatus('error');
        addMessage('system', `❌ WebSocket error: ${error}`);
      };

      ws.onclose = () => {
        setConnected(false);
        setConnectionStatus('disconnected');
        addMessage('system', '🔌 Disconnected from WebSocket server');
      };

      wsRef.current = ws;
    } catch (error: any) {
      setConnectionStatus('error');
      addMessage('system', `❌ Failed to connect: ${error.message}`);
    }
  };

  const disconnect = () => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  };

  const sendMessage = () => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      addMessage('system', '❌ Not connected to server');
      return;
    }

    if (!inputMessage.trim()) {
      return;
    }

    wsRef.current.send(inputMessage);
    addMessage('sent', inputMessage);
    setInputMessage('');
  };

  const clearMessages = () => {
    setMessages([]);
    messageIdRef.current = 0;
  };

  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const getStatusColor = () => {
    switch (connectionStatus) {
      case 'disconnected': return 'text-gray-500';
      case 'connecting': return 'text-yellow-500';
      case 'connected': return 'text-green-500';
      case 'error': return 'text-red-500';
    }
  };

  const getStatusIcon = () => {
    switch (connectionStatus) {
      case 'disconnected': return '⚪';
      case 'connecting': return '🔄';
      case 'connected': return '🟢';
      case 'error': return '🔴';
    }
  };

  return (
    <>
      <RequireAuth />
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 py-8">
        <div className="max-w-6xl mx-auto px-4">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold mb-2 dark:text-white">🔌 Test WebSocket</h1>
            <p className="text-gray-600 dark:text-gray-300">
              Test real-time WebSocket connections for live features
            </p>
          </div>

          {/* Connection Status */}
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 shadow-sm mb-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="text-2xl">{getStatusIcon()}</span>
                <div>
                  <h3 className="text-lg font-bold dark:text-white">Connection Status</h3>
                  <p className={`text-sm ${getStatusColor()}`}>
                    {connectionStatus === 'disconnected' && 'Not connected'}
                    {connectionStatus === 'connecting' && 'Connecting...'}
                    {connectionStatus === 'connected' && 'Connected'}
                    {connectionStatus === 'error' && 'Connection error'}
                  </p>
                </div>
              </div>
              <div className="flex gap-2">
                {!connected ? (
                  <button
                    onClick={connect}
                    disabled={connectionStatus === 'connecting'}
                    className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {connectionStatus === 'connecting' ? 'Connecting...' : 'Connect'}
                  </button>
                ) : (
                  <button
                    onClick={disconnect}
                    className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                  >
                    Disconnect
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Message Input */}
          {connected && (
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 shadow-sm mb-6">
              <h3 className="text-lg font-semibold mb-4 dark:text-white">Send Message</h3>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                  placeholder="Type a message..."
                  className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500"
                />
                <button
                  onClick={sendMessage}
                  disabled={!inputMessage.trim()}
                  className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Send
                </button>
              </div>
            </div>
          )}

          {/* Messages */}
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm">
            <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold dark:text-white">Messages ({messages.length})</h3>
              <button
                onClick={clearMessages}
                className="px-3 py-1 text-sm bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white rounded hover:bg-gray-200 dark:hover:bg-gray-600"
              >
                Clear
              </button>
            </div>
            <div className="p-4 space-y-3 max-h-96 overflow-y-auto">
              {messages.length === 0 ? (
                <p className="text-center text-gray-500 dark:text-gray-400 py-8">
                  No messages yet. Connect to start testing.
                </p>
              ) : (
                messages.map((msg) => (
                  <div
                    key={msg.id}
                    className={`p-3 rounded-lg ${
                      msg.type === 'sent'
                        ? 'bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-200 dark:border-indigo-800 ml-8'
                        : msg.type === 'received'
                        ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 mr-8'
                        : 'bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1">
                        <p className={`text-xs font-medium mb-1 ${
                          msg.type === 'sent'
                            ? 'text-indigo-700 dark:text-indigo-300'
                            : msg.type === 'received'
                            ? 'text-green-700 dark:text-green-300'
                            : 'text-gray-700 dark:text-gray-300'
                        }`}>
                          {msg.type === 'sent' ? '📤 Sent' : msg.type === 'received' ? '📥 Received' : 'ℹ️ System'}
                        </p>
                        <p className="text-sm dark:text-gray-200">{msg.content}</p>
                      </div>
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        {msg.timestamp.toLocaleTimeString()}
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Info Section */}
          <div className="mt-6 bg-gradient-to-r from-indigo-50 to-purple-50 dark:from-indigo-900/20 dark:to-purple-900/20 rounded-lg border border-indigo-200 dark:border-indigo-800 p-6">
            <h3 className="text-lg font-semibold mb-3 dark:text-white">ℹ️ About WebSocket Testing</h3>
            <div className="space-y-2 text-sm dark:text-gray-300">
              <p>• <strong>Real-time Communication:</strong> WebSockets enable bidirectional communication between client and server</p>
              <p>• <strong>Use Cases:</strong> Live chat, real-time notifications, collaborative features, live leaderboards</p>
              <p>• <strong>Connection:</strong> Connects to <code className="px-1 py-0.5 bg-gray-200 dark:bg-gray-700 rounded">ws://localhost:8000/api/v1/ws/test</code></p>
              <p>• <strong>Authentication:</strong> Uses JWT token from localStorage for secure connections</p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
