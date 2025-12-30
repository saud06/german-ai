"use client"
import { useState } from 'react';
import { useWebSocket } from '@/hooks/useWebSocket';

export default function WebSocketTest() {
  const [messages, setMessages] = useState<any[]>([]);
  const [inputMessage, setInputMessage] = useState('');

  const { isConnected, connectionStatus, sendMessage, sendText, ping } = useWebSocket({
    onMessage: (message) => {
      setMessages(prev => [...prev, { direction: 'received', data: message, timestamp: new Date() }]);
    },
    onConnect: () => {
    },
    onDisconnect: () => {
    },
  });

  const handleSendText = () => {
    if (inputMessage.trim()) {
      sendText(inputMessage);
      setMessages(prev => [...prev, { 
        direction: 'sent', 
        data: { type: 'text', content: inputMessage }, 
        timestamp: new Date() 
      }]);
      setInputMessage('');
    }
  };

  const handlePing = () => {
    ping();
    setMessages(prev => [...prev, { 
      direction: 'sent', 
      data: { type: 'ping', timestamp: Date.now() }, 
      timestamp: new Date() 
    }]);
  };

  const handleEcho = () => {
    const echoMessage = { type: 'echo', content: 'Hello from frontend!' };
    sendMessage(echoMessage);
    setMessages(prev => [...prev, { 
      direction: 'sent', 
      data: echoMessage, 
      timestamp: new Date() 
    }]);
  };

  const clearMessages = () => {
    setMessages([]);
  };

  const getStatusColor = () => {
    switch (connectionStatus) {
      case 'connected': return 'bg-green-500';
      case 'connecting': return 'bg-yellow-500';
      case 'error': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="rounded-xl border bg-white dark:bg-zinc-900 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold">WebSocket Test</h2>
          <div className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${getStatusColor()}`}></div>
            <span className="text-sm font-medium capitalize">{connectionStatus}</span>
          </div>
        </div>

        {/* Controls */}
        <div className="space-y-4">
          <div className="flex gap-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendText()}
              placeholder="Type a message..."
              className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:bg-zinc-800 dark:border-zinc-700"
              disabled={!isConnected}
            />
            <button
              onClick={handleSendText}
              disabled={!isConnected || !inputMessage.trim()}
              className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              Send
            </button>
          </div>

          <div className="flex gap-2">
            <button
              onClick={handlePing}
              disabled={!isConnected}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition"
            >
              Ping
            </button>
            <button
              onClick={handleEcho}
              disabled={!isConnected}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 transition"
            >
              Echo Test
            </button>
            <button
              onClick={clearMessages}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition"
            >
              Clear
            </button>
          </div>
        </div>

        {/* Message Log */}
        <div className="mt-6">
          <h3 className="text-lg font-semibold mb-3">Message Log ({messages.length})</h3>
          <div className="space-y-2 max-h-96 overflow-y-auto border rounded-lg p-4 dark:border-zinc-700">
            {messages.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No messages yet. Send a message to test the connection.</p>
            ) : (
              messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`p-3 rounded-lg ${
                    msg.direction === 'sent'
                      ? 'bg-indigo-50 dark:bg-indigo-900/20 ml-8'
                      : 'bg-gray-50 dark:bg-zinc-800 mr-8'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className={`text-xs font-semibold ${
                      msg.direction === 'sent' ? 'text-indigo-600' : 'text-green-600'
                    }`}>
                      {msg.direction === 'sent' ? '→ SENT' : '← RECEIVED'}
                    </span>
                    <span className="text-xs text-gray-500">
                      {msg.timestamp.toLocaleTimeString()}
                    </span>
                  </div>
                  <pre className="text-sm overflow-x-auto">
                    {JSON.stringify(msg.data, null, 2)}
                  </pre>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Info Panel */}
      <div className="rounded-xl border bg-white dark:bg-zinc-900 p-6">
        <h3 className="text-lg font-semibold mb-3">Connection Info</h3>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600 dark:text-gray-400">Status:</span>
            <span className="font-medium">{connectionStatus}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600 dark:text-gray-400">Connected:</span>
            <span className="font-medium">{isConnected ? 'Yes' : 'No'}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600 dark:text-gray-400">Messages:</span>
            <span className="font-medium">{messages.length}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
