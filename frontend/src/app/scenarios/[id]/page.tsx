'use client';

import { useEffect, useState, useRef } from 'react';
import { useRouter, useParams } from 'next/navigation';
import VoiceRecorder from '@/components/VoiceRecorder';

interface Character {
  id: string;
  name: string;
  role: string;
  personality: string;
  description: string;
  greeting: string;
}

interface Objective {
  id: string;
  description: string;
  keywords: string[];
  required: boolean;
  hint: string | null;
  completed: boolean;
}

interface Scenario {
  _id: string;
  name: string;
  title_en: string;
  description: string;
  description_en: string;
  difficulty: string;
  category: string;
  estimated_duration: number;
  icon: string;
  characters: Character[];
  objectives: Objective[];
  context: string;
}

interface Message {
  role: string;
  content: string;
  timestamp: string;
  audio?: string;
}

interface ConversationState {
  _id: string;
  messages: Message[];
  objectives_progress: Array<{
    objective_id: string;
    completed: boolean;
  }>;
  score: number;
  status: string;
  character_id: string;
}

export default function ScenarioDetailPage() {
  const router = useRouter();
  const params = useParams();
  const scenarioId = params.id as string;
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const [scenario, setScenario] = useState<Scenario | null>(null);
  const [conversationState, setConversationState] = useState<ConversationState | null>(null);
  const [loading, setLoading] = useState(true);
  const [starting, setStarting] = useState(false);
  const [sending, setSending] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const formatText = (text: string) => {
    return text.replace(/_/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase());
  };

  useEffect(() => {
    fetchScenario();
    checkConversationState();
  }, [scenarioId]);

  const fetchScenario = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/v1/scenarios/${scenarioId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!response.ok) throw new Error('Failed to fetch scenario');

      const data = await response.json();
      setScenario(data.scenario);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load scenario');
    } finally {
      setLoading(false);
    }
  };

  const checkConversationState = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/v1/scenarios/${scenarioId}/state`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setConversationState(data.state);
      } else if (response.status === 404) {
        setConversationState(null);
      }
    } catch (err) {
      // No active conversation
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  };

  useEffect(() => {
    if (conversationState?.messages && conversationState.status !== 'completed') {
      scrollToBottom();
    }
  }, [conversationState?.messages, conversationState?.status]);

  const startScenario = async () => {
    if (!scenario || !scenario.characters[0]) return;

    setStarting(true);
    setError('');

    try {
      const token = localStorage.getItem('token');
      const characterId = scenario.characters[0].id;
      const response = await fetch(
        `http://localhost:8000/api/v1/scenarios/${scenarioId}/start?character_id=${characterId}`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to start scenario');
      }

      await checkConversationState();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start scenario');
    } finally {
      setStarting(false);
    }
  };

  const sendMessage = async () => {
    if (!message.trim() || sending) return;

    const userMessage = message.trim();
    setSending(true);
    setError('');
    setMessage('');

    try {
      const token = localStorage.getItem('token');
      
      // Add user message immediately
      if (conversationState) {
        setConversationState({
          ...conversationState,
          messages: [...conversationState.messages, {
            role: 'user',
            content: userMessage,
            timestamp: new Date().toISOString()
          }]
        });
      }

      // Stream AI response
      const response = await fetch(
        `http://localhost:8000/api/v1/scenarios/${scenarioId}/message/stream`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ message: userMessage })
        }
      );

      if (!response.ok) throw new Error('Failed to send message');

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let streamedResponse = '';
      let isComplete = false;

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                
                if (data.type === 'token') {
                  streamedResponse += data.content;
                  if (conversationState) {
                    const updatedMessages = [...conversationState.messages];
                    const lastMessage = updatedMessages[updatedMessages.length - 1];
                    
                    if (lastMessage && lastMessage.role === 'character') {
                      lastMessage.content = streamedResponse;
                    } else {
                      updatedMessages.push({
                        role: 'character',
                        content: streamedResponse,
                        timestamp: new Date().toISOString()
                      });
                    }
                    
                    setConversationState({
                      ...conversationState,
                      messages: updatedMessages
                    });
                  }
                } else if (data.type === 'complete') {
                  isComplete = data.conversation_complete || false;
                } else if (data.type === 'error') {
                  throw new Error(data.message);
                }
              } catch (e) {
              }
            }
          }
        }
      }

      // Always refresh conversation state to get updated objectives and completion status
      // Wait for state to update before checking completion
      const stateResponse = await fetch(`http://localhost:8000/api/v1/scenarios/${scenarioId}/state`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (stateResponse.ok) {
        const stateData = await stateResponse.json();
        setConversationState(stateData.state);
        
        // Check if scenario is complete based on fresh state
        if (stateData.state.status === 'completed' || isComplete) {
          setConversationState({
            ...stateData.state,
            status: 'completed'
          });
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message');
      setMessage(userMessage);
    } finally {
      setSending(false);
    }
  };

  const sendVoiceMessage = async (audioBase64: string) => {
    if (sending) return;

    setSending(true);
    setError('');

    try {
      const token = localStorage.getItem('token');
      
      // First, transcribe the audio to show user message immediately
      const transcribeResponse = await fetch(
        `http://localhost:8000/api/v1/scenarios/${scenarioId}/voice-message`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ audio_base64: audioBase64 })
        }
      );

      if (!transcribeResponse.ok) {
        const errorData = await transcribeResponse.json();
        throw new Error(errorData.detail || 'Failed to send voice message');
      }

      const data = await transcribeResponse.json();

      // Refresh conversation state to get both user message and AI response
      // (backend already added both to state)
      await checkConversationState();

      // Play audio response if available
      if (data.character_audio) {
        try {
          const audio = new Audio(`data:audio/wav;base64,${data.character_audio}`);
          audio.play();
        } catch (audioErr) {
        }
      }
      
      // If complete, update status (no alert)
      if (data.conversation_complete && conversationState) {
        setConversationState({
          ...conversationState,
          status: 'completed'
        });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send voice message');
    } finally {
      setSending(false);
    }
  };

  const getObjectiveStatus = (objectiveId: string) => {
    if (!conversationState) return false;
    const progress = conversationState.objectives_progress.find(
      p => p.objective_id === objectiveId
    );
    return progress?.completed || false;
  };

  const getCompletionPercentage = () => {
    if (!scenario || !conversationState) return 0;
    const completed = conversationState.objectives_progress.filter(p => p.completed).length;
    return Math.round((completed / scenario.objectives.length) * 100);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (!scenario) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 dark:text-red-400 text-lg">Scenario not found</p>
          <button
            onClick={() => router.push('/scenarios')}
            className="mt-4 text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300"
          >
            ← Back to Scenarios
          </button>
        </div>
      </div>
    );
  }

  const character = scenario.characters[0];

  // If no conversation started, show scenario details
  if (!conversationState) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
        <div className="max-w-4xl mx-auto px-4 py-8">
          <button
            onClick={() => router.push('/scenarios')}
            className="mb-4 text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300"
          >
            ← Back to Scenarios
          </button>

          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden">
            {/* Header */}
            <div className="bg-gradient-to-r from-indigo-500 to-purple-600 p-8 text-white">
              <div className="text-6xl mb-4">{scenario.icon || '🎭'}</div>
              <h1 className="text-4xl font-bold mb-2">{scenario.name}</h1>
              <p className="text-indigo-100 text-lg">{scenario.title_en}</p>
            </div>

            {/* Body */}
            <div className="p-8">
              {/* Description */}
              <div className="mb-8">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">About this scenario</h2>
                <p className="text-gray-700 dark:text-gray-300 mb-2">{scenario.description}</p>
                <p className="text-gray-600 dark:text-gray-400 italic">{scenario.description_en}</p>
              </div>

              {/* Character */}
              <div className="mb-8">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Character</h2>
                {scenario.characters && scenario.characters.length > 0 && character && (
                  <div className="flex items-start gap-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div className="text-4xl">👤</div>
                    <div className="flex-1">
                      <p className="text-gray-800 dark:text-gray-200 font-medium text-lg">{character.name}</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400 font-medium">{formatText(character.role)}</p>
                      <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">{formatText(character.personality)}</p>
                      {character.description && (
                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-2 italic">{character.description}</p>
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* Learning Objectives */}
              <div className="mb-8">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Learning objectives</h2>
                <div className="space-y-2">
                  {scenario.objectives.map((obj, index) => {
                    const isCompleted = getObjectiveStatus(obj.id);
                    return (
                      <div 
                        key={obj.id} 
                        className={`flex items-start gap-3 p-3 rounded-lg ${
                          isCompleted 
                            ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800' 
                            : 'bg-gray-50 dark:bg-gray-700'
                        }`}
                      >
                        <span className={`flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-sm font-medium ${
                          isCompleted
                            ? 'bg-green-100 dark:bg-green-800 text-green-700 dark:text-green-200'
                            : 'bg-indigo-100 dark:bg-indigo-900 text-indigo-600 dark:text-indigo-300'
                        }`}>
                          {isCompleted ? '✓' : index + 1}
                        </span>
                        <div className="flex-1">
                          <p className={`font-medium ${
                            isCompleted 
                              ? 'text-green-700 dark:text-green-300 line-through' 
                              : 'text-gray-800 dark:text-gray-200'
                          }`}>
                            {obj.description}
                          </p>
                          {obj.hint && !isCompleted && (
                            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">💡 {obj.hint}</p>
                          )}
                        </div>
                        <span className={`text-xs font-medium px-2 py-1 rounded ${
                          isCompleted 
                            ? 'bg-green-100 dark:bg-green-800 text-green-700 dark:text-green-200' 
                            : 'bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300'
                        }`}>
                          {isCompleted ? 'Completed' : 'Required'}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Meta Info */}
              <div className="flex items-center gap-6 mb-8 text-gray-600 dark:text-gray-400">
                <span>📊 Difficulty: <strong>{scenario.difficulty}</strong></span>
                <span>⏱️ Duration: <strong>{scenario.estimated_duration} min</strong></span>
                <span>🎯 Objectives: <strong>{scenario.objectives.length}</strong></span>
                {conversationState && (
                  <span className="text-green-600 dark:text-green-400">
                    ✅ Progress: <strong>{getCompletionPercentage()}%</strong>
                  </span>
                )}
              </div>

              {/* Error */}
              {error && (
                <div className="mb-6 bg-red-100 dark:bg-red-900 border border-red-400 dark:border-red-700 text-red-700 dark:text-red-300 px-4 py-3 rounded">
                  {error}
                </div>
              )}

              {/* Start Button */}
              <button
                onClick={startScenario}
                disabled={starting}
                className="w-full bg-indigo-600 text-white py-4 rounded-lg font-medium text-lg hover:bg-indigo-700 transition disabled:opacity-50"
              >
                {starting ? 'Starting...' : `Start Conversation with ${character.name} →`}
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Conversation view
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Progress Bar - Top */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4 mb-6">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-lg font-bold text-gray-900 dark:text-white">Progress</h3>
            <span className="text-2xl font-bold text-indigo-600 dark:text-indigo-400">{getCompletionPercentage()}%</span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
            <div
              className="bg-indigo-600 h-3 rounded-full transition-all"
              style={{ width: `${getCompletionPercentage()}%` }}
            ></div>
          </div>
          <div className="flex items-center justify-between mt-2 text-sm text-gray-600 dark:text-gray-400">
            <span>Score: <strong className="text-indigo-600 dark:text-indigo-400">{conversationState.score}</strong></span>
            <span>Completed: <strong>{conversationState.objectives_progress.filter(p => p.completed).length}/{scenario.objectives.length}</strong></span>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Sidebar - Objectives */}
          <div className="lg:col-span-1">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-6">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Learning Objectives</h2>
              <div className="space-y-2">
                {scenario.objectives.map((obj) => (
                  <div key={obj.id} className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div className="flex-shrink-0">
                      {getObjectiveStatus(obj.id) ? (
                        <span className="text-green-500 text-xl">✓</span>
                      ) : (
                        <span className="text-gray-400 dark:text-gray-500 text-xl">○</span>
                      )}
                    </div>
                    <div className="flex-1">
                      <p className="text-gray-800 dark:text-gray-200 font-medium flex-1">{obj.description}</p>
                      {obj.hint && !getObjectiveStatus(obj.id) && (
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">💡 {obj.hint}</p>
                      )}
                    </div>
                    {getObjectiveStatus(obj.id) ? (
                      <span className="text-xs bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 px-2 py-1 rounded">✓ Completed</span>
                    ) : obj.required ? (
                      <span className="text-xs bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 px-2 py-1 rounded">Required</span>
                    ) : (
                      <span className="text-xs bg-gray-100 dark:bg-gray-600 text-gray-600 dark:text-gray-300 px-2 py-1 rounded">Optional</span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Conversation Area */}
          <div className="lg:col-span-2">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md flex flex-col" style={{ height: '600px' }}>
              {/* Completion Banner */}
              {conversationState.status === 'completed' && (
                <div className="bg-gradient-to-r from-green-500 to-emerald-600 text-white p-4 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className="text-3xl">🎉</span>
                    <div>
                      <h3 className="font-bold text-lg">Scenario Completed!</h3>
                      <p className="text-sm opacity-90">Great job! You've completed all objectives.</p>
                    </div>
                  </div>
                  <button
                    onClick={() => router.back()}
                    className="bg-white text-green-600 px-4 py-2 rounded-lg font-medium hover:bg-green-50 transition"
                  >
                    ← Back to Scenarios
                  </button>
                </div>
              )}
              
              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {conversationState.messages.map((msg, index) => (
                  <div
                    key={index}
                    className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[80%] rounded-lg p-4 ${
                        msg.role === 'user'
                          ? 'bg-indigo-600 text-white'
                          : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-100'
                      }`}
                    >
                      {msg.role === 'character' && (
                        <p className="text-xs font-medium mb-1 opacity-70">
                          {character.name}
                        </p>
                      )}
                      <p className="text-sm">{msg.content}</p>
                    </div>
                  </div>
                ))}
                {sending && (
                  <div className="flex justify-start">
                    <div className="bg-gray-100 dark:bg-gray-700 rounded-lg p-4 max-w-[80%]">
                      <div className="flex items-center gap-2">
                        <div className="animate-pulse">💭</div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Typing...</p>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Input */}
              <div className="border-t dark:border-gray-700 p-4 bg-gray-50 dark:bg-gray-900">
                {error && (
                  <div className="mb-3 bg-red-100 dark:bg-red-900 border border-red-400 dark:border-red-700 text-red-700 dark:text-red-300 px-3 py-2 rounded text-sm">
                    {error}
                  </div>
                )}
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                    placeholder="Type your message in German..."
                    disabled={sending}
                    className="flex-1 px-4 py-2 border dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400"
                  />
                  <VoiceRecorder
                    onRecordingComplete={sendVoiceMessage}
                    disabled={sending}
                  />
                  <button
                    onClick={sendMessage}
                    disabled={sending || !message.trim()}
                    className="px-6 py-2 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition disabled:opacity-50"
                  >
                    {sending ? '...' : 'Send'}
                  </button>
                </div>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                  💡 Tip: Type or speak your message in German. Complete objectives using the suggested keywords!
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
