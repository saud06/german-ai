'use client';

import { useState } from 'react';
import RequireAuth from '@/components/RequireAuth';

interface ModelTest {
  model: string;
  status: 'idle' | 'testing' | 'success' | 'error';
  response?: string;
  error?: string;
  responseTime?: number;
}

export default function TestAIPage() {
  const [models, setModels] = useState<ModelTest[]>([
    { model: 'mistral:7b', status: 'idle' },
    { model: 'llama3.2:1b', status: 'idle' },
  ]);
  const [testPrompt, setTestPrompt] = useState('Wie geht es dir?');
  const [testingAll, setTestingAll] = useState(false);

  const testModel = async (modelName: string) => {
    setModels(prev => prev.map(m => 
      m.model === modelName ? { ...m, status: 'testing' as const, response: undefined, error: undefined } : m
    ));

    const startTime = Date.now();
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/v1/ai/test-model', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          model: modelName,
          prompt: testPrompt
        })
      });

      const responseTime = Date.now() - startTime;

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(errorData.detail || 'Failed to test model');
      }

      const data = await response.json();
      setModels(prev => prev.map(m => 
        m.model === modelName ? { 
          ...m, 
          status: 'success' as const, 
          response: data.response,
          responseTime 
        } : m
      ));
    } catch (error: any) {
      setModels(prev => prev.map(m => 
        m.model === modelName ? { 
          ...m, 
          status: 'error' as const, 
          error: error.message 
        } : m
      ));
    }
  };

  const testAllModels = async () => {
    setTestingAll(true);
    for (const model of models) {
      await testModel(model.model);
    }
    setTestingAll(false);
  };

  const getStatusColor = (status: ModelTest['status']) => {
    switch (status) {
      case 'idle': return 'text-gray-500';
      case 'testing': return 'text-blue-500';
      case 'success': return 'text-green-500';
      case 'error': return 'text-red-500';
    }
  };

  const getStatusIcon = (status: ModelTest['status']) => {
    switch (status) {
      case 'idle': return '⚪';
      case 'testing': return '🔄';
      case 'success': return '✅';
      case 'error': return '❌';
    }
  };

  return (
    <>
      <RequireAuth />
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 py-8">
        <div className="max-w-6xl mx-auto px-4">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold mb-2 dark:text-white">🤖 Test AI Models</h1>
            <p className="text-gray-600 dark:text-gray-300">
              Test different AI models to verify they're working correctly
            </p>
          </div>

          {/* Test Prompt */}
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 shadow-sm mb-6">
            <h2 className="text-xl font-semibold mb-4 dark:text-white">Test Prompt</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Enter a prompt to test (German recommended)
                </label>
                <input
                  type="text"
                  value={testPrompt}
                  onChange={(e) => setTestPrompt(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500"
                  placeholder="Wie geht es dir?"
                />
              </div>
              <button
                onClick={testAllModels}
                disabled={testingAll || !testPrompt}
                className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {testingAll ? 'Testing All Models...' : 'Test All Models'}
              </button>
            </div>
          </div>

          {/* Models Grid */}
          <div className="grid md:grid-cols-2 gap-6">
            {models.map((model) => (
              <div
                key={model.model}
                className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 shadow-sm"
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{getStatusIcon(model.status)}</span>
                    <div>
                      <h3 className="text-lg font-bold dark:text-white">{model.model}</h3>
                      <p className={`text-sm ${getStatusColor(model.status)}`}>
                        {model.status === 'idle' && 'Ready to test'}
                        {model.status === 'testing' && 'Testing...'}
                        {model.status === 'success' && `Success (${model.responseTime}ms)`}
                        {model.status === 'error' && 'Failed'}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => testModel(model.model)}
                    disabled={model.status === 'testing' || !testPrompt}
                    className="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
                  >
                    Test
                  </button>
                </div>

                {model.response && (
                  <div className="mt-4 p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                    <p className="text-sm font-medium text-green-800 dark:text-green-300 mb-2">Response:</p>
                    <p className="text-sm text-green-700 dark:text-green-400">{model.response}</p>
                  </div>
                )}

                {model.error && (
                  <div className="mt-4 p-4 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
                    <p className="text-sm font-medium text-red-800 dark:text-red-300 mb-2">Error:</p>
                    <p className="text-sm text-red-700 dark:text-red-400">{model.error}</p>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Info Section */}
          <div className="mt-6 bg-gradient-to-r from-indigo-50 to-purple-50 dark:from-indigo-900/20 dark:to-purple-900/20 rounded-lg border border-indigo-200 dark:border-indigo-800 p-6">
            <h3 className="text-lg font-semibold mb-3 dark:text-white">ℹ️ About AI Models</h3>
            <div className="space-y-2 text-sm dark:text-gray-300">
              <p>• <strong>Mistral 7B:</strong> Larger model with better German language understanding and more natural responses</p>
              <p>• <strong>Llama 3.2 1B:</strong> Smaller, faster model optimized for quick responses</p>
              <p>• Both models run locally via Ollama on GPU for fast inference</p>
              <p>• Response times vary based on prompt complexity and model size</p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
