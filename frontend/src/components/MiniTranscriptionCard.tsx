"use client"
import React, { useEffect, useRef, useState } from 'react'

interface MiniTranscriptionCardProps {
  expected: string
  isRecording: boolean
  onTranscriptUpdate?: (transcript: string, score: number) => void
}

interface WordResult {
  word: string
  confidence: number
  isFinal: boolean
}

function calculateWordScore(expectedWord: string, spokenWord: string): number {
  const exp = expectedWord.toLowerCase().trim()
  const spoken = spokenWord.toLowerCase().trim()
  
  if (exp === spoken) return 100
  if (exp.includes(spoken) || spoken.includes(exp)) return 75
  
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

export default function MiniTranscriptionCard({ expected, isRecording, onTranscriptUpdate }: MiniTranscriptionCardProps) {
  const [wordResults, setWordResults] = useState<WordResult[]>([])
  const [isSupported, setIsSupported] = useState(true)
  const recognitionRef = useRef<any>(null)
  const expectedWords = expected.toLowerCase().split(/\s+/).filter(w => w.length > 0)

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
      setWordResults([])
    }
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
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    if (!SpeechRecognition) {
      setIsSupported(false)
      startDemoMode()
      return
    }

    try {
      const recognition = new SpeechRecognition()
      recognition.lang = 'de-DE'
      recognition.continuous = true
      recognition.interimResults = true
      recognition.maxAlternatives = 1

      recognition.onresult = (event: any) => {
        let finalTranscript = ''
        let interimTranscript = ''
        const allWordResults: WordResult[] = []

        // Process all results to get complete transcript
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
        if (fullTranscript) {
          const words = fullTranscript.split(/\s+/).filter((w: string) => w.length > 0)
          words.forEach((word: string, wordIndex: number) => {
            // Determine if this word is final (from final transcript)
            const finalWordCount = finalTranscript.trim().split(/\s+/).filter(w => w.length > 0).length
            const isFinal = wordIndex < finalWordCount
            
            allWordResults.push({
              word: word.toLowerCase().replace(/[.,!?]/g, ''),
              confidence: 85, // Default confidence
              isFinal: isFinal
            })
          })
        }

        setWordResults(allWordResults)

        // Calculate overall similarity score
        const spokenWords = allWordResults.map(w => w.word)
        const similarity = calculateOverallScore(expectedWords, spokenWords)
        onTranscriptUpdate?.(fullTranscript, similarity)
      }

      recognition.onerror = (event: any) => {
        console.warn('Speech recognition error:', event.error)
      }

      recognition.start()
      recognitionRef.current = recognition
    } catch (error) {
      console.error('Error starting speech recognition:', error)
      setIsSupported(false)
      startDemoMode()
    }
  }

  // Demo mode for testing when Speech API is not available
  const startDemoMode = () => {
    if (!isRecording) return
    
    const demoWords = ['guten', 'morgen']
    let wordIndex = 0
    
    const addDemoWord = () => {
      if (wordIndex < demoWords.length && isRecording) {
        const newResults: WordResult[] = []
        
        // Add all words up to current index
        for (let i = 0; i <= wordIndex; i++) {
          newResults.push({
            word: demoWords[i],
            confidence: 85 + Math.random() * 10,
            isFinal: i < wordIndex
          })
        }
        
        setWordResults(newResults)
        
        const spokenWords = newResults.map(w => w.word)
        const similarity = calculateOverallScore(expectedWords, spokenWords)
        onTranscriptUpdate?.(demoWords.slice(0, wordIndex + 1).join(' '), similarity)
        
        wordIndex++
        if (wordIndex <= demoWords.length) {
          setTimeout(addDemoWord, 1500)
        }
      }
    }
    
    // Start demo after 1 second
    setTimeout(addDemoWord, 1000)
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
    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6 mb-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white">🎯 Word-by-Word Analysis</h3>
          <span className="px-3 py-1 bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 rounded-full text-xs font-medium">
            Live Recognition
          </span>
        </div>
        <button 
          onClick={startDemoMode}
          disabled={!isRecording}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-all text-sm disabled:opacity-50 disabled:cursor-not-allowed"
        >
          🎬 Test with Demo
        </button>
      </div>
      
      <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
        Watch your words appear in real-time with color-coded accuracy feedback
      </p>
      
      {/* Live transcription words */}
      {isRecording ? (
        <div className="bg-gray-50 dark:bg-gray-700 rounded-xl p-6 min-h-[120px]">
          <div className="flex flex-wrap gap-2 mb-4">
            {wordResults.length > 0 ? (
              wordResults.map((wordResult, index) => {
                const status = getWordStatus(index, wordResult.word)
                const colorClass = getWordColor(status, wordResult.isFinal)
                
                return (
                  <span
                    key={index}
                    className={`px-3 py-2 text-sm font-medium border-2 rounded-lg ${colorClass} transition-all duration-300 transform hover:scale-105`}
                  >
                    {wordResult.word}
                    {!wordResult.isFinal && (
                      <span className="ml-1 opacity-60 animate-pulse">...</span>
                    )}
                  </span>
                )
              })
            ) : (
              <div className="w-full text-center py-8">
                <span className="text-gray-400 dark:text-gray-500 text-base italic">
                  {isSupported ? '🎤 Listening for your voice...' : '🎬 Click "Start Demo" above to see how it works'}
                </span>
              </div>
            )}
          </div>
          
          {/* Legend */}
          {wordResults.length > 0 && (
            <div className="flex flex-wrap gap-4 pt-4 border-t border-gray-200 dark:border-gray-600">
              <div className="flex items-center gap-2">
                <span className="w-4 h-4 rounded bg-green-500"></span>
                <span className="text-xs font-medium text-gray-700 dark:text-gray-300">Correct</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-4 h-4 rounded bg-yellow-500"></span>
                <span className="text-xs font-medium text-gray-700 dark:text-gray-300">Similar</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-4 h-4 rounded bg-red-500"></span>
                <span className="text-xs font-medium text-gray-700 dark:text-gray-300">Incorrect</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-4 h-4 rounded bg-blue-500"></span>
                <span className="text-xs font-medium text-gray-700 dark:text-gray-300">Extra Word</span>
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="bg-gray-50 dark:bg-gray-700 rounded-xl p-6 text-center">
          <p className="text-gray-500 dark:text-gray-400 text-base">
            ⏸️ Click <strong>"Start Recording"</strong> to begin speech recognition
          </p>
        </div>
      )}
    </div>
  )
}
