'use client';

import { useState, useEffect, useRef } from 'react';
import AIChat from '@/components/AIChat';

interface AIStatus {
  ollama_available: boolean;
  ollama_host: string;
  ollama_model: string;
  features: {
    conversation: boolean;
    voice: boolean;
    simulation: boolean;
  };
}

interface ServiceStatus {
  whisper: boolean;
  piper: boolean;
  ollama: boolean;
}

interface GPUMetrics {
  available: boolean;
  name?: string;
  memory_used_mb?: number;
  memory_total_mb?: number;
  memory_percent?: number;
  utilization_percent?: number;
  temperature?: number;
}

interface SystemMetrics {
  cpu_percent: number;
  memory_percent: number;
  memory_used_gb: number;
  memory_total_gb: number;
  memory_available_gb: number;
  disk_percent: number;
  uptime_seconds: number;
  gpu?: GPUMetrics;
}

export default function TestAIPage() {
  const [aiStatus, setAiStatus] = useState<AIStatus | null>(null);
  const [serviceStatus, setServiceStatus] = useState<ServiceStatus>({
    whisper: false,
    piper: false,
    ollama: false
  });
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [isRecording, setIsRecording] = useState(false);
  const [voiceResponse, setVoiceResponse] = useState<string>('');
  const [isProcessing, setIsProcessing] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const [showVoiceTest, setShowVoiceTest] = useState(false);

  useEffect(() => {
    fetchStatus();
    fetchSystemMetrics();
    // Refresh status every 10 seconds
    const statusInterval = setInterval(fetchStatus, 10000);
    // Refresh metrics every 2 seconds for live monitoring
    const metricsInterval = setInterval(fetchSystemMetrics, 2000);
    return () => {
      clearInterval(statusInterval);
      clearInterval(metricsInterval);
    };
  }, []);

  const fetchStatus = async () => {
    try {
      // Fetch AI status
      const aiRes = await fetch('http://localhost:8000/api/v1/ai/status');
      if (aiRes.ok) {
        const data = await aiRes.json();
        setAiStatus(data);
        setServiceStatus(prev => ({ ...prev, ollama: data.ollama_available }));
      }

      // Fetch voice status
      const voiceRes = await fetch('http://localhost:8000/api/v1/voice/status');
      if (voiceRes.ok) {
        const data = await voiceRes.json();
        setServiceStatus(prev => ({
          ...prev,
          whisper: data.whisper_available || false,
          piper: data.piper_available || false
        }));
      }
    } catch (error) {
      console.error('Failed to fetch status:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchSystemMetrics = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/analytics/metrics');
      if (res.ok) {
        const data = await res.json();
        setSystemMetrics({
          cpu_percent: data.system?.cpu_percent || 0,
          memory_percent: data.system?.memory_percent || 0,
          memory_used_gb: data.system?.memory_used_gb || 0,
          memory_total_gb: data.system?.memory_total_gb || 0,
          memory_available_gb: data.system?.memory_available_gb || 0,
          disk_percent: data.system?.disk_percent || 0,
          uptime_seconds: data.system?.uptime_seconds || 0,
          gpu: data.system?.gpu
        });
      }
    } catch (error) {
      console.error('Failed to fetch system metrics:', error);
    }
  };

  const startRecording = async () => {
    try {
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
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        await sendVoiceMessage(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Failed to start recording:', error);
      alert('Failed to access microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const sendVoiceMessage = async (audioBlob: Blob) => {
    setIsProcessing(true);
    setVoiceResponse('');

    try {
      const reader = new FileReader();
      reader.readAsDataURL(audioBlob);
      reader.onloadend = async () => {
        const base64Audio = reader.result as string;
        const base64Data = base64Audio.split(',')[1];

        const token = localStorage.getItem('token');
        const response = await fetch('http://localhost:8000/api/v1/voice/conversation', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({ audio_base64: base64Data })
        });

        if (response.ok) {
          const data = await response.json();
          setVoiceResponse(`Transcribed: "${data.transcribed_text}"\n\nAI Response: "${data.ai_response_text}"`);
          
          // Play audio response if available
          if (data.ai_response_audio) {
            const audio = new Audio(`data:audio/wav;base64,${data.ai_response_audio}`);
            audio.play();
          }
        } else {
          const error = await response.json();
          setVoiceResponse(`Error: ${error.detail || 'Voice conversation failed'}`);
        }
      };
    } catch (error) {
      console.error('Voice message error:', error);
      setVoiceResponse('Error: Failed to process voice message');
    } finally {
      setIsProcessing(false);
    }
  };

  const getStatusColor = (status: boolean) => {
    return status ? 'bg-green-500' : 'bg-red-500';
  };

  const getStatusText = (status: boolean) => {
    return status ? 'Available' : 'Unavailable';
  };

  const getMetricColor = (percent: number) => {
    if (percent < 50) return 'bg-green-500';
    if (percent < 80) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const formatUptime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-zinc-950 py-8">
      <div className="max-w-6xl mx-auto px-4">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold mb-2">🤖 AI Model Testing</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Test AI models and monitor service status
          </p>
        </div>

        {/* Service Status Grid */}
        <div className="grid md:grid-cols-3 gap-4 mb-6">
          {/* Ollama Status */}
          <div className="bg-white dark:bg-zinc-900 rounded-lg border p-4">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-semibold">Ollama (AI)</h3>
              <span className={`h-3 w-3 rounded-full ${getStatusColor(serviceStatus.ollama)}`}></span>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
              {getStatusText(serviceStatus.ollama)}
            </p>
            {aiStatus && (
              <div className="text-xs space-y-1">
                <p><strong>Host:</strong> {aiStatus.ollama_host}</p>
                <p><strong>Model:</strong> {aiStatus.ollama_model}</p>
                <div className="mt-2">
                  <p className="font-semibold mb-1">Features:</p>
                  <div className="space-y-0.5">
                    <p>• Conversation: {aiStatus.features.conversation ? '✅' : '❌'}</p>
                    <p>• Voice: {aiStatus.features.voice ? '✅' : '❌'}</p>
                    <p>• Simulation: {aiStatus.features.simulation ? '✅' : '❌'}</p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Whisper Status */}
          <div className="bg-white dark:bg-zinc-900 rounded-lg border p-4">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-semibold">Whisper (STT)</h3>
              <span className={`h-3 w-3 rounded-full ${getStatusColor(serviceStatus.whisper)}`}></span>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
              {getStatusText(serviceStatus.whisper)}
            </p>
            <div className="text-xs space-y-1">
              <p><strong>Service:</strong> Speech-to-Text</p>
              <p><strong>Port:</strong> 9000</p>
              <p><strong>Language:</strong> German (de)</p>
            </div>
          </div>

          {/* Piper Status */}
          <div className="bg-white dark:bg-zinc-900 rounded-lg border p-4">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-semibold">Piper (TTS)</h3>
              <span className={`h-3 w-3 rounded-full ${getStatusColor(serviceStatus.piper)}`}></span>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
              {getStatusText(serviceStatus.piper)}
            </p>
            <div className="text-xs space-y-1">
              <p><strong>Service:</strong> Text-to-Speech</p>
              <p><strong>Port:</strong> 10200</p>
              <p><strong>Voice:</strong> de_DE-thorsten-high</p>
            </div>
          </div>
        </div>

        {/* System Info */}
        <div className="bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 rounded-lg border p-4 mb-6">
          <h3 className="font-semibold mb-2">ℹ️ System Information</h3>
          <div className="text-sm space-y-1 text-gray-700 dark:text-gray-300">
            <p>• <strong>Backend:</strong> FastAPI running on http://localhost:8000</p>
            <p>• <strong>Frontend:</strong> Next.js running on http://localhost:3000</p>
            <p>• <strong>Database:</strong> MongoDB on localhost:27017</p>
            <p>• <strong>Cache:</strong> Redis on localhost:6379</p>
            <p>• <strong>Auto-refresh:</strong> Status updates every 10 seconds</p>
          </div>
        </div>

        {/* Live System Metrics */}
        {systemMetrics && (
          <div className="bg-white dark:bg-zinc-900 rounded-lg border p-6 mb-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-bold">📊 Live System Metrics</h2>
              <span className="text-xs text-gray-500 dark:text-gray-400">Updates every 2s</span>
            </div>
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* CPU */}
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-semibold">CPU Usage</span>
                  <span className="text-sm font-mono">{systemMetrics.cpu_percent.toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
                  <div
                    className={`h-3 rounded-full transition-all duration-500 ${getMetricColor(systemMetrics.cpu_percent)}`}
                    style={{ width: `${Math.min(systemMetrics.cpu_percent, 100)}%` }}
                  ></div>
                </div>
              </div>

              {/* System RAM */}
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-semibold">System RAM</span>
                  <span className="text-sm font-mono">{systemMetrics.memory_percent.toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
                  <div
                    className={`h-3 rounded-full transition-all duration-500 ${getMetricColor(systemMetrics.memory_percent)}`}
                    style={{ width: `${Math.min(systemMetrics.memory_percent, 100)}%` }}
                  ></div>
                </div>
                <div className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                  {systemMetrics.memory_used_gb.toFixed(1)}GB / {systemMetrics.memory_total_gb.toFixed(1)}GB
                  <br />
                  <span className="text-green-600 dark:text-green-400">
                    {systemMetrics.memory_available_gb.toFixed(1)}GB available
                  </span>
                </div>
              </div>

              {/* Disk */}
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-semibold">Disk Usage</span>
                  <span className="text-sm font-mono">{systemMetrics.disk_percent.toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
                  <div
                    className={`h-3 rounded-full transition-all duration-500 ${getMetricColor(systemMetrics.disk_percent)}`}
                    style={{ width: `${Math.min(systemMetrics.disk_percent, 100)}%` }}
                  ></div>
                </div>
              </div>

              {/* Uptime */}
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-semibold">System Uptime</span>
                  <span className="text-sm font-mono">{formatUptime(systemMetrics.uptime_seconds)}</span>
                </div>
                <div className="flex items-center justify-center h-3">
                  <span className="text-xs text-gray-500 dark:text-gray-400">Since last boot</span>
                </div>
              </div>
            </div>

            {/* GPU Metrics */}
            {systemMetrics.gpu && systemMetrics.gpu.available && (
              <div className="mt-6 pt-6 border-t">
                <h3 className="text-lg font-bold mb-4">🎮 GPU Metrics (AI Model)</h3>
                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
                  {/* GPU Name */}
                  <div className="md:col-span-2">
                    <div className="text-sm font-semibold mb-2">GPU Device</div>
                    <div className="text-sm text-gray-700 dark:text-gray-300">
                      {systemMetrics.gpu.name || 'Unknown GPU'}
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      Used for Ollama AI inference
                    </div>
                  </div>

                  {/* GPU Memory */}
                  {systemMetrics.gpu.memory_total_mb && (
                    <div>
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-sm font-semibold">GPU Memory</span>
                        {systemMetrics.gpu.memory_percent && (
                          <span className="text-sm font-mono">{systemMetrics.gpu.memory_percent.toFixed(1)}%</span>
                        )}
                      </div>
                      {systemMetrics.gpu.memory_percent ? (
                        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
                          <div
                            className={`h-3 rounded-full transition-all duration-500 ${getMetricColor(systemMetrics.gpu.memory_percent)}`}
                            style={{ width: `${Math.min(systemMetrics.gpu.memory_percent, 100)}%` }}
                          ></div>
                        </div>
                      ) : (
                        <div className="text-xs text-gray-500">Monitoring not available</div>
                      )}
                      <div className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                        {systemMetrics.gpu.memory_used_mb ? 
                          `${(systemMetrics.gpu.memory_used_mb / 1024).toFixed(1)}GB / ` : ''}
                        {(systemMetrics.gpu.memory_total_mb / 1024).toFixed(1)}GB VRAM
                      </div>
                    </div>
                  )}

                  {/* GPU Utilization */}
                  {systemMetrics.gpu.utilization_percent !== undefined && systemMetrics.gpu.utilization_percent !== null && (
                    <div>
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-sm font-semibold">GPU Usage</span>
                        <span className="text-sm font-mono">{systemMetrics.gpu.utilization_percent.toFixed(1)}%</span>
                      </div>
                      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
                        <div
                          className={`h-3 rounded-full transition-all duration-500 ${getMetricColor(systemMetrics.gpu.utilization_percent)}`}
                          style={{ width: `${Math.min(systemMetrics.gpu.utilization_percent, 100)}%` }}
                        ></div>
                      </div>
                      <div className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                        Compute utilization
                      </div>
                    </div>
                  )}
                </div>

                {!systemMetrics.gpu.memory_percent && !systemMetrics.gpu.utilization_percent && (
                  <div className="mt-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3">
                    <p className="text-xs text-gray-700 dark:text-gray-300">
                      ℹ️ <strong>Note:</strong> Real-time GPU monitoring is limited on macOS. GPU info shows device details only.
                      For detailed GPU metrics, use Activity Monitor or third-party tools.
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* Memory Usage Explanation */}
            <div className="mt-6 pt-6 border-t">
              <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                <h4 className="text-sm font-semibold mb-2">💡 About High Memory Usage</h4>
                <p className="text-xs text-gray-700 dark:text-gray-300 leading-relaxed">
                  <strong>macOS Memory Management:</strong> macOS uses available RAM for file caching to improve performance.
                  High memory usage (70%+) is normal and doesn't mean you're running out of memory.
                  The system automatically frees cached memory when apps need it.
                  <br /><br />
                  <strong>What matters:</strong> "Available" memory (shown in green above). As long as you have several GB available,
                  your system is healthy. Only worry if available memory drops below 1-2GB.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* AI Chat Testing */}
        <div className="mb-6">
          <h2 className="text-2xl font-bold mb-4">💬 Test AI Conversation (Text)</h2>
          <AIChat context="general conversation" />
        </div>

        {/* Voice Testing */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold">🎤 Test Voice Conversation</h2>
            <button
              onClick={() => setShowVoiceTest(!showVoiceTest)}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 text-sm"
            >
              {showVoiceTest ? 'Hide' : 'Show'} Voice Test
            </button>
          </div>

          {showVoiceTest && (
            <div className="bg-white dark:bg-zinc-900 rounded-lg border p-6">
              {!serviceStatus.whisper || !serviceStatus.piper ? (
                <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
                  <p className="text-sm">
                    ⚠️ Voice services not available. Please ensure Whisper (STT) and Piper (TTS) are running.
                  </p>
                  <p className="text-xs mt-2 text-gray-600 dark:text-gray-400">
                    Run: <code className="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">docker-compose up -d whisper piper</code>
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="flex items-center justify-center">
                    <button
                      onClick={isRecording ? stopRecording : startRecording}
                      disabled={isProcessing}
                      className={`w-24 h-24 rounded-full flex items-center justify-center text-white text-3xl transition-all ${
                        isRecording
                          ? 'bg-red-500 hover:bg-red-600 animate-pulse'
                          : isProcessing
                          ? 'bg-gray-400 cursor-not-allowed'
                          : 'bg-indigo-600 hover:bg-indigo-700'
                      }`}
                    >
                      {isProcessing ? '⏳' : isRecording ? '⏹️' : '🎤'}
                    </button>
                  </div>

                  <div className="text-center text-sm text-gray-600 dark:text-gray-400">
                    {isProcessing
                      ? 'Processing your voice message...'
                      : isRecording
                      ? 'Recording... Click to stop'
                      : 'Click microphone to start recording'}
                  </div>

                  {voiceResponse && (
                    <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
                      <h3 className="font-semibold mb-2">Response:</h3>
                      <pre className="text-sm whitespace-pre-wrap">{voiceResponse}</pre>
                    </div>
                  )}

                  <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3">
                    <p className="text-xs text-gray-700 dark:text-gray-300">
                      💡 <strong>Tip:</strong> Speak in German for best results. Try: "Hallo! Wie geht es dir?"
                    </p>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Tips */}
        <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800 p-4">
          <h3 className="font-semibold mb-2">💡 Testing Tips</h3>
          <ul className="text-sm space-y-1 text-gray-700 dark:text-gray-300">
            <li>• <strong>Green status:</strong> Service is running and available</li>
            <li>• <strong>Red status:</strong> Service is unavailable or not configured</li>
            <li>• <strong>Test conversation:</strong> Try "Hallo! Wie geht es dir?"</li>
            <li>• <strong>Check features:</strong> Ensure required features are enabled in backend .env</li>
            <li>• <strong>Troubleshooting:</strong> If services are down, check Docker containers</li>
          </ul>
        </div>

        {/* Admin Actions */}
        <div className="mt-6 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800 p-4">
          <h3 className="font-semibold mb-2">⚙️ Quick Actions</h3>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={fetchStatus}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm"
            >
              Refresh Status
            </button>
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 text-sm"
            >
              API Docs
            </a>
            <a
              href="http://localhost:8000/api/v1/analytics/health"
              target="_blank"
              rel="noopener noreferrer"
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm"
            >
              Health Check
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
