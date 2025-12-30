'use client';

import { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface Message {
  role: 'user' | 'assistant';
  text: string;
  audio?: string;
  timestamp: Date;
}

export default function VoiceChatClient() {
  const router = useRouter();
  
  const [messages, setMessages] = useState<Message[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [voiceStatus, setVoiceStatus] = useState<any>(null);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    checkVoiceStatus();
  }, []);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const checkVoiceStatus = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';
      const response = await fetch(`${apiUrl}/voice/status`);
      const data = await response.json();
      setVoiceStatus(data);
      
      if (!data.voice_features_enabled) {
        setError('Voice features are not enabled on the server. Please ensure Whisper and Piper services are running.');
      }
    } catch (err) {
      setError('Failed to check voice service status. Please ensure the backend is running.');
    }
  };

  const startRecording = async () => {
    try {
      setError(null);
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        // Use the actual MIME type from MediaRecorder, not force WAV
        const mimeType = mediaRecorder.mimeType || 'audio/webm';
        const audioBlob = new Blob(audioChunksRef.current, { type: mimeType });
        await processAudio(audioBlob);
        
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      setError('Failed to access microphone. Please grant permission.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const processAudio = async (audioBlob: Blob) => {
    setIsProcessing(true);
    setError(null);

    try {
      // Convert audio to base64
      const reader = new FileReader();
      reader.readAsDataURL(audioBlob);
      
      reader.onloadend = async () => {
        const base64Audio = reader.result as string;
        const base64Data = base64Audio.split(',')[1];

        // Send to voice conversation endpoint
        const token = localStorage.getItem('token');
        const apiUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';
        const response = await fetch(`${apiUrl}/voice/conversation`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            audio_base64: base64Data,
            context: 'general',
            conversation_history: messages.slice(-6).map((m: Message) => ({
              role: m.role,
              content: m.text
            })),
            use_fast_model: true
          })
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Voice conversation failed');
        }

        const data = await response.json();

        // Add user message
        setMessages((prev: Message[]) => [...prev, {
          role: 'user',
          text: data.transcribed_text,
          timestamp: new Date()
        }]);

        // Add AI response
        setMessages((prev: Message[]) => [...prev, {
          role: 'assistant',
          text: data.ai_response_text,
          audio: data.ai_response_audio,
          timestamp: new Date()
        }]);

        // Play AI response audio
        if (data.ai_response_audio) {
          playAudio(data.ai_response_audio);
        }
      };
    } catch (err: any) {
      setError(err.message || 'Failed to process audio');
    } finally {
      setIsProcessing(false);
    }
  };

  const playAudio = (base64Audio: string) => {
    try {
      const audioBlob = base64ToBlob(base64Audio, 'audio/wav');
      const audioUrl = URL.createObjectURL(audioBlob);
      
      if (audioRef.current) {
        audioRef.current.src = audioUrl;
        audioRef.current.play();
        setIsPlaying(true);
        
        audioRef.current.onended = () => {
          setIsPlaying(false);
          URL.revokeObjectURL(audioUrl);
        };
      }
    } catch (err) {
    }
  };

  const base64ToBlob = (base64: string, mimeType: string): Blob => {
    const byteCharacters = atob(base64);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    return new Blob([byteArray], { type: mimeType });
  };

  const replayMessage = (message: Message) => {
    if (message.audio) {
      playAudio(message.audio);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-pink-50 dark:from-gray-900 dark:via-gray-800 dark:to-purple-900">
      <div className="max-w-5xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => router.push('/dashboard')}
            className="mb-4 text-purple-600 dark:text-purple-400 hover:text-purple-800 dark:hover:text-purple-300 flex items-center font-medium transition-colors"
          >
            ← Back to Dashboard
          </button>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-2">
            🎤 Voice Conversation
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-400">
            Practice German with AI voice chat - Speak naturally and get instant responses
          </p>
        </div>


        {/* Error Display */}
        {error && (
          <div className="bg-red-100 dark:bg-red-900 border-2 border-red-300 dark:border-red-700 text-red-700 dark:text-red-200 px-6 py-4 rounded-2xl mb-6 shadow-lg">
            <div className="flex items-start gap-3">
              <span className="text-2xl">⚠️</span>
              <div>
                <p className="font-bold text-lg mb-1">Error</p>
                <p className="text-sm">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Messages Card */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6 mb-6 min-h-[450px] max-h-[550px] overflow-y-auto">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full py-20">
              <div className="text-8xl mb-6 animate-pulse">💬</div>
              <p className="text-xl font-semibold text-gray-400 dark:text-gray-500 mb-2">No messages yet</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">Click the microphone button below to start your conversation</p>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map((message: Message, index: number) => (
                <div
                  key={index}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} animate-fadeIn`}
                >
                  <div
                    className={`max-w-[75%] rounded-2xl p-4 shadow-md ${
                      message.role === 'user'
                        ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white'
                        : 'bg-gradient-to-r from-gray-100 to-gray-200 dark:from-gray-700 dark:to-gray-600 text-gray-800 dark:text-white'
                    }`}
                  >
                    {message.role === 'assistant' && (
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-2xl">🤖</span>
                        <span className="text-xs font-semibold opacity-70">AI Assistant</span>
                      </div>
                    )}
                    {message.role === 'user' && (
                      <div className="flex items-center gap-2 mb-2 justify-end">
                        <span className="text-xs font-semibold opacity-90">You</span>
                        <span className="text-2xl">👤</span>
                      </div>
                    )}
                    <p className="whitespace-pre-wrap text-base leading-relaxed">{message.text}</p>
                    <div className={`flex items-center justify-between mt-3 pt-2 border-t ${
                      message.role === 'user' 
                        ? 'border-purple-400' 
                        : 'border-gray-300 dark:border-gray-500'
                    }`}>
                      <span className="text-xs opacity-70">{message.timestamp.toLocaleTimeString()}</span>
                      {message.audio && (
                        <button
                          onClick={() => replayMessage(message)}
                          className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${
                            message.role === 'user'
                              ? 'bg-purple-600 hover:bg-purple-700 text-white'
                              : 'bg-gray-300 dark:bg-gray-600 hover:bg-gray-400 dark:hover:bg-gray-500 text-gray-800 dark:text-white'
                          } disabled:opacity-50 disabled:cursor-not-allowed`}
                          disabled={isPlaying}
                        >
                          🔊 Replay
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Recording Controls Card */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
          <div className="flex flex-col items-center space-y-6">
            {/* Status Messages */}
            {isProcessing && (
              <div className="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-gray-700 dark:to-gray-600 rounded-xl p-6 w-full text-center border-2 border-purple-200 dark:border-purple-700">
                <div className="flex flex-col items-center justify-center gap-3">
                  <div className="animate-spin rounded-full h-12 w-12 border-4 border-purple-200 border-t-purple-600"></div>
                  <p className="text-lg font-bold text-purple-700 dark:text-purple-300">🤖 AI is thinking...</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Transcribing and generating response</p>
                </div>
              </div>
            )}

            {isPlaying && (
              <div className="bg-gradient-to-r from-green-50 to-emerald-50 dark:from-gray-700 dark:to-gray-600 rounded-xl p-4 w-full text-center">
                <p className="text-sm font-semibold text-green-700 dark:text-green-300 flex items-center justify-center gap-2">
                  <span className="text-xl animate-pulse">🔊</span>
                  Playing AI response...
                </p>
              </div>
            )}

            {/* Record Button */}
            <div className="relative">
              {isRecording && (
                <div className="absolute inset-0 rounded-full bg-red-500 animate-ping opacity-75"></div>
              )}
              <button
                onClick={isRecording ? stopRecording : startRecording}
                disabled={isProcessing || isPlaying}
                className={`relative w-28 h-28 rounded-full flex items-center justify-center text-5xl transition-all transform hover:scale-110 shadow-2xl ${
                  isRecording
                    ? 'bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 animate-pulse'
                    : 'bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600'
                } text-white disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100`}
              >
                {isRecording ? '⏹️' : '🎤'}
              </button>
            </div>

            <div className="text-center">
              <p className={`text-lg font-bold ${
                isRecording 
                  ? 'text-red-600 dark:text-red-400' 
                  : 'text-gray-700 dark:text-gray-300'
              }`}>
                {isRecording
                  ? '🔴 Recording... Click to stop'
                  : '⚪ Click to start recording'}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                {isRecording ? 'Speak clearly in German' : 'Press and hold to speak'}
              </p>
            </div>

            {/* Instructions */}
            <div className="w-full mt-4 bg-gradient-to-r from-purple-50 to-pink-50 dark:from-gray-700 dark:to-gray-600 rounded-xl p-6 border-2 border-purple-200 dark:border-purple-700">
              <div className="flex items-center gap-2 mb-4">
                <span className="text-2xl">💡</span>
                <p className="font-bold text-lg text-gray-800 dark:text-white">How to use:</p>
              </div>
              <ol className="space-y-3 text-sm text-gray-700 dark:text-gray-300">
                <li className="flex items-start gap-3">
                  <span className="flex-shrink-0 w-6 h-6 bg-purple-500 text-white rounded-full flex items-center justify-center text-xs font-bold">1</span>
                  <span>Click the microphone button to start recording</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="flex-shrink-0 w-6 h-6 bg-purple-500 text-white rounded-full flex items-center justify-center text-xs font-bold">2</span>
                  <span>Speak in German (or English to practice)</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="flex-shrink-0 w-6 h-6 bg-purple-500 text-white rounded-full flex items-center justify-center text-xs font-bold">3</span>
                  <span>Click again to stop and send your message</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="flex-shrink-0 w-6 h-6 bg-purple-500 text-white rounded-full flex items-center justify-center text-xs font-bold">4</span>
                  <span>The AI will transcribe, respond, and speak back to you</span>
                </li>
              </ol>
            </div>
          </div>
        </div>

        {/* Hidden audio element for playback */}
        <audio ref={audioRef} className="hidden" />
      </div>
    </div>
  );
}
