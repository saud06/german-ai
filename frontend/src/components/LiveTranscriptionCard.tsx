"use client"
import React, { useEffect, useRef, useState } from 'react'

interface LiveTranscriptionCardProps {
  expected: string
  isRecording: boolean
  onTranscriptUpdate?: (transcript: string, score: number) => void
}

interface WordResult {
  word: string
  confidence: number
  isFinal: boolean
  timestamp: number
}

// Simple word-level similarity calculation
function calculateWordScore(expectedWord: string, spokenWord: string): number {
  const exp = expectedWord.toLowerCase().trim()
  const spoken = spokenWord.toLowerCase().trim()
  
  if (exp === spoken) return 100
  if (exp.includes(spoken) || spoken.includes(exp)) return 75
  
  // Simple character-based similarity
  const maxLen = Math.max(exp.length, spoken.length)
  if (maxLen === 0) return 100
  
  let matches = 0
  const minLen = Math.min(exp.length, spoken.length)
  for (let i = 0; i < minLen; i++) {
    if (exp[i] === spoken[i]) matches++
  }
  
  return Math.round((matches / maxLen) * 100)
}

function calculateOverallScore(expected: string[], spoken: string[]): number {
  if (expected.length === 0 && spoken.length === 0) return 100
  if (expected.length === 0) return 0
  
  let totalScore = 0
  const maxLength = Math.max(expected.length, spoken.length)
  
  for (let i = 0; i < maxLength; i++) {
    const expectedWord = expected[i] || ''
    const spokenWord = spoken[i] || ''
    totalScore += calculateWordScore(expectedWord, spokenWord)
  }
  
  return Math.round(totalScore / maxLength)
}

export default function LiveTranscriptionCard({ expected, isRecording, onTranscriptUpdate }: LiveTranscriptionCardProps) {
  const [wordResults, setWordResults] = useState<WordResult[]>([])
  const [currentTranscript, setCurrentTranscript] = useState('')
  const [isSupported, setIsSupported] = useState(true)
  const [demoMode, setDemoMode] = useState(false)
  const recognitionRef = useRef<any>(null)
  const demoTimeoutRef = useRef<any>(null)
  
  // Parse expected words
  const expectedWords = expected.toLowerCase().split(/\s+/).filter(w => w.length > 0)

  // Clear results when recording stops
  const clearResults = () => {
    setWordResults([])
    setCurrentTranscript('')
  }


  useEffect(() => {
    if (!isRecording) {
      stopRecognition()
      return
    }

    startRecognition()
    return () => stopRecognition()
  }, [isRecording, expected])

  const startRecognition = () => {
    console.log('Starting speech recognition...')
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    if (!SpeechRecognition) {
      console.error('Speech Recognition not supported in this browser')
      setIsSupported(false)
      return
    }

    try {
      const recognition = new SpeechRecognition()
      recognition.lang = 'de-DE'
      recognition.continuous = true
      recognition.interimResults = true
      recognition.maxAlternatives = 1
      
      console.log('Speech Recognition configured:', {
        lang: recognition.lang,
        continuous: recognition.continuous,
        interimResults: recognition.interimResults
      })

    recognition.onresult = (event: any) => {
      console.log('Speech recognition result:', event) // Debug log
      
      let finalTranscript = ''
      let interimTranscript = ''
      
      // Process all results to separate final and interim
      for (let i = 0; i < event.results.length; i++) {
        const result = event.results[i]
        const transcript = result[0].transcript.trim()
        
        if (transcript) {
          if (result.isFinal) {
            finalTranscript += transcript + ' '
          } else {
            interimTranscript += transcript + ' '
          }
        }
      }

      // Combine final and interim transcripts
      const fullTranscript = (finalTranscript + interimTranscript).trim()
      
      // Process words from the full transcript
      const allWordResults: WordResult[] = []
      if (fullTranscript) {
        const words = fullTranscript.split(/\s+/).filter((w: string) => w.length > 0)
        const finalWordCount = finalTranscript.trim().split(/\s+/).filter(w => w.length > 0).length
        
        words.forEach((word: string, wordIndex: number) => {
          const isFinal = wordIndex < finalWordCount
          allWordResults.push({
            word: word.toLowerCase().replace(/[.,!?]/g, ''), // Clean punctuation
            confidence: 85, // Default confidence
            isFinal: isFinal,
            timestamp: Date.now() + (wordIndex * 200) // Unique timestamp
          })
        })
      }

      console.log('Final transcript:', finalTranscript) // Debug log
      console.log('Interim transcript:', interimTranscript) // Debug log
      console.log('Word results:', allWordResults) // Debug log
      
      setCurrentTranscript(fullTranscript)
      setWordResults(allWordResults)

      // Calculate overall similarity score
      const spokenWords = allWordResults.map(w => w.word)
      const similarity = calculateOverallScore(expectedWords, spokenWords)
      onTranscriptUpdate?.(fullTranscript, similarity)
    }

    recognition.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error)
      if (event.error === 'not-allowed') {
        alert('Please allow microphone access to use speech recognition')
      }
    }

    recognition.onstart = () => {
      console.log('Speech recognition started successfully')
      setIsSupported(true)
    }

    recognition.onend = () => {
      console.log('Speech recognition ended')
      // Don't automatically restart - let user control it
    }

      console.log('Starting speech recognition...')
      recognition.start()
      recognitionRef.current = recognition
      
    } catch (error) {
      console.error('Error starting speech recognition:', error)
      setIsSupported(false)
    }
  }

  const stopRecognition = () => {
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop()
      } catch (e) {
        console.warn('Error stopping recognition:', e)
      }
      recognitionRef.current = null
    }
    
    if (!isRecording) {
      clearResults()
    }
  }

  const calculateOverallScore = (expected: string[], spoken: string[]): number => {
    if (expected.length === 0 && spoken.length === 0) return 100
    if (expected.length === 0) return 0
    
    let totalScore = 0
    const maxLength = Math.max(expected.length, spoken.length)
    
    for (let i = 0; i < maxLength; i++) {
      const expectedWord = expected[i] || ''
      const spokenWord = spoken[i] || ''
      totalScore += calculateWordScore(expectedWord, spokenWord)
    }
    
    return Math.round(totalScore / maxLength)
  }

  const getWordStatus = (wordIndex: number, spokenWord: string) => {
    const expectedWord = expectedWords[wordIndex]
    if (!expectedWord) return 'extra'
    
    const score = calculateWordScore(expectedWord, spokenWord)
    if (score >= 90) return 'correct'
    if (score >= 70) return 'similar'
    return 'incorrect'
  }

  const getWordColor = (status: string, isFinal: boolean) => {
    const opacity = isFinal ? '' : ' opacity-70'
    switch (status) {
      case 'correct': return `bg-green-100 text-green-800 border-green-200${opacity}`
      case 'similar': return `bg-yellow-100 text-yellow-800 border-yellow-200${opacity}`
      case 'incorrect': return `bg-red-100 text-red-800 border-red-200${opacity}`
      case 'extra': return `bg-blue-100 text-blue-800 border-blue-200${opacity}`
      default: return `bg-gray-100 text-gray-600 border-gray-200${opacity}`
    }
  }

  return (
    <div className="rounded-lg border-2 border-blue-200 bg-blue-50 p-4 space-y-3">
      <div className="text-xs text-gray-500 space-x-2">
        <span>Recording: {isRecording ? 'Yes' : 'No'}</span>
        <span>Supported: {isSupported ? 'Yes' : 'No'}</span>
        <span>Words: {wordResults.length}</span>
      </div>

      {/* Expected sentence */}
      <div className="space-y-1">
        <div className="text-xs font-medium text-gray-600">Expected:</div>
        <div className="flex flex-wrap gap-1">
          {expectedWords.map((word, index) => (
            <span
              key={index}
              className="px-2 py-1 text-sm bg-gray-100 text-gray-700 border border-gray-200 rounded"
            >
              {word}
            </span>
          ))}
        </div>
      </div>

      {/* Live transcription */}
      <div className="space-y-1">
        <div className="text-xs font-medium text-gray-600">You're saying:</div>
        <div className="min-h-[2.5rem] flex flex-wrap gap-1 items-start">
          {wordResults.length > 0 ? (
            wordResults.map((wordResult, index) => {
              const status = getWordStatus(index, wordResult.word)
              const colorClass = getWordColor(status, wordResult.isFinal)
              
              return (
                <span
                  key={`${wordResult.timestamp}-${index}`}
                  className={`px-2 py-1 text-sm border rounded transition-all duration-200 ${colorClass}`}
                  title={`Confidence: ${Math.round(wordResult.confidence)}%`}
                >
                  {wordResult.word}
                  {!wordResult.isFinal && (
                    <span className="ml-1 text-xs opacity-60">...</span>
                  )}
                </span>
              )
            })
          ) : (
            <span className="text-gray-400 text-sm italic">
              {isRecording ? 'Listening...' : 'Start recording to see live transcription'}
            </span>
          )}
        </div>
      </div>

      {/* Real-time feedback */}
      {wordResults.length > 0 && (
        <div className="text-xs text-gray-600 bg-white rounded p-2 border">
          <div className="flex items-center justify-between">
            <span>Progress: {wordResults.filter(w => w.isFinal).length}/{expectedWords.length} words</span>
            <span>
              Accuracy: {calculateOverallScore(expectedWords, wordResults.map(w => w.word))}%
            </span>
          </div>
        </div>
      )}

      {/* Legend */}
      <div className="text-xs text-gray-500 border-t pt-2">
        <div className="flex flex-wrap gap-3">
          <span className="flex items-center gap-1">
            <div className="w-3 h-3 bg-green-100 border border-green-200 rounded"></div>
            Correct
          </span>
          <span className="flex items-center gap-1">
            <div className="w-3 h-3 bg-yellow-100 border border-yellow-200 rounded"></div>
            Similar
          </span>
          <span className="flex items-center gap-1">
            <div className="w-3 h-3 bg-red-100 border border-red-200 rounded"></div>
            Incorrect
          </span>
          <span className="flex items-center gap-1">
            <div className="w-3 h-3 bg-blue-100 border border-blue-200 rounded"></div>
            Extra
          </span>
        </div>
      </div>
    </div>
  )
}
