"use client"
import React, { useEffect, useState } from 'react'
import RequireAuth from '@/components/RequireAuth'
import api from '@/lib/api'
import { useAuth } from '@/store/auth'
import { useSearchParams } from 'next/navigation'
import * as learningPathApi from '@/lib/learningPathApi'
import { useJourney } from '@/contexts/JourneyContext'

interface QuizQuestion {
  id: string
  type: 'mcq' | 'fill_blank' | 'translation' | 'sentence_order' | 'listening' | 'reading' | 'speaking'
  question?: string
  sentence?: string
  english?: string
  options?: string[]
  scrambled_words?: string[]
  audio_text?: string  // For listening questions
  passage?: string  // For reading questions
  prompt?: string  // For speaking questions
  expected_text?: string  // For speaking questions
  answer: string
  acceptable_answers?: string[]
  hint?: string
  explanation?: string
  skills?: string[]
}

interface QuizConfig {
  topic?: string
  level: string
  size: number
  question_types?: string[]
}

interface QuestionResult {
  question_id: string
  correct: boolean
  user_answer: string
  correct_answer: string
  explanation: string
}

type QuizStage = 'setup' | 'loading' | 'quiz' | 'results'

export default function QuizPage() {
  const { userId } = useAuth()
  const { activeJourney } = useJourney()
  const searchParams = useSearchParams()
  const activityId = searchParams.get('activity_id')
  
  // State management
  const [mounted, setMounted] = useState(false)
  const [stage, setStage] = useState<QuizStage>('setup')
  const [quizId, setQuizId] = useState<string>('')
  const [questions, setQuestions] = useState<QuizQuestion[]>([])
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [userAnswers, setUserAnswers] = useState<Map<string, string>>(new Map())
  const [currentAnswer, setCurrentAnswer] = useState<string>('')
  const [results, setResults] = useState<QuestionResult[]>([])
  const [score, setScore] = useState(0)
  const [percentage, setPercentage] = useState(0)
  const [strengths, setStrengths] = useState<string[]>([])
  const [weaknesses, setWeaknesses] = useState<string[]>([])
  const [showFeedback, setShowFeedback] = useState(false)
  const [isCorrect, setIsCorrect] = useState(false)
  const [startTime, setStartTime] = useState<number>(0)
  const [isRecording, setIsRecording] = useState(false)
  
  // Quiz configuration
  const [config, setConfig] = useState<QuizConfig>({
    topic: 'mixed',
    level: 'intermediate',
    size: 10
  })
  
  // Available options
  const [topics, setTopics] = useState<any[]>([])
  const [levels, setLevels] = useState<any[]>([])
  const [questionTypes, setQuestionTypes] = useState<any[]>([])
  const [contentMappings, setContentMappings] = useState<Record<string, any>>({})

  useEffect(() => {
    setMounted(true)
    loadTopics()
    
    // Restore quiz state from localStorage on mount
    const savedState = localStorage.getItem('quizState')
    if (savedState) {
      try {
        const state = JSON.parse(savedState)
        if (state.stage && state.stage !== 'setup' && state.quizId) {
          setStage(state.stage)
          setQuizId(state.quizId)
          setQuestions(state.questions || [])
          setCurrentQuestionIndex(state.currentQuestionIndex || 0)
          setUserAnswers(new Map(state.userAnswers || []))
          setConfig(state.config || config)
          if (state.results) setResults(state.results)
          if (state.score !== undefined) setScore(state.score)
          if (state.percentage !== undefined) setPercentage(state.percentage)
          if (state.strengths) setStrengths(state.strengths)
          if (state.weaknesses) setWeaknesses(state.weaknesses)
        }
      } catch (e) {
      }
    }
  }, [])
  
  // Save quiz state to localStorage whenever it changes
  useEffect(() => {
    if (mounted && stage !== 'setup') {
      const state = {
        stage,
        quizId,
        questions,
        currentQuestionIndex,
        userAnswers: Array.from(userAnswers.entries()),
        config,
        results,
        score,
        percentage,
        strengths,
        weaknesses
      }
      localStorage.setItem('quizState', JSON.stringify(state))
    }
  }, [mounted, stage, quizId, questions, currentQuestionIndex, userAnswers, config, results, score, percentage, strengths, weaknesses])
  
  const loadTopics = async () => {
    try {
      const r = await api.get('/quiz-v2/topics')
      let topicsList = r.data.topics || []
      
      // Sort topics by journey priority if active journey exists
      if (activeJourney && contentMappings) {
        topicsList = topicsList.sort((a: any, b: any) => {
          const aPriority = contentMappings[a.value]?.priority_by_purpose?.[activeJourney.type] || 5
          const bPriority = contentMappings[b.value]?.priority_by_purpose?.[activeJourney.type] || 5
          return bPriority - aPriority
        })
      }
      
      setTopics(topicsList)
      setLevels(r.data.levels || [])
      setQuestionTypes(r.data.question_types || [])
      
      // Load content mappings for quiz filtering
      loadContentMappings()
    } catch (e) {
    }
  }

  const loadContentMappings = async () => {
    try {
      const token = localStorage.getItem('token')
      if (!token) return

      const response = await fetch('http://localhost:8000/api/v1/journeys/content-mappings?content_type=quiz', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        const mappingsMap: Record<string, any> = {}
        data.mappings?.forEach((m: any) => {
          mappingsMap[m.content_id] = m
        })
        setContentMappings(mappingsMap)
      }
    } catch (err) {
      console.error('Failed to fetch quiz content mappings:', err)
    }
  }

  const startQuiz = async () => {
    setStage('loading')
    setCurrentQuestionIndex(0)
    setUserAnswers(new Map())
    setCurrentAnswer('')
    setStartTime(Date.now())
    
    try {
      const r = await api.post('/quiz-v2/start', config)
      setQuizId(r.data.quiz_id)
      setQuestions(r.data.questions || [])
      setStage('quiz')
    } catch (e) {
      setStage('setup')
      alert('Failed to start quiz. Please try again.')
    }
  }

  const handleAnswer = (answer: string) => {
    setCurrentAnswer(answer)
  }
  
  const submitAnswer = () => {
    if (!currentAnswer.trim()) return
    
    const newAnswers = new Map(userAnswers)
    newAnswers.set(questions[currentQuestionIndex].id, currentAnswer)
    setUserAnswers(newAnswers)
    
    // Check if answer is correct for immediate feedback
    const currentQ = questions[currentQuestionIndex]
    let correct = false
    if (currentQ.type === 'translation' && currentQ.acceptable_answers) {
      correct = currentQ.acceptable_answers.some(acc => 
        currentAnswer.toLowerCase().trim() === acc.toLowerCase().trim()
      )
    } else {
      correct = currentAnswer.trim() === currentQ.answer.trim()
    }
    
    setIsCorrect(correct)
    setShowFeedback(true)
  }
  
  const nextQuestion = () => {
    setShowFeedback(false)
    setCurrentAnswer('')
    
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1)
    } else {
      submitQuiz()
    }
  }
  
  const submitQuiz = async () => {
    setStage('loading')
    
    try {
      const answers = Array.from(userAnswers.entries()).map(([question_id, user_answer]) => ({
        question_id,
        user_answer,
        time_spent: 0
      }))
      
      const r = await api.post('/quiz-v2/submit', {
        quiz_id: quizId,
        answers
      })
      
      setResults(r.data.results || [])
      setScore(r.data.score)
      setPercentage(r.data.percentage)
      setStrengths(r.data.strengths || [])
      setWeaknesses(r.data.weaknesses || [])
      setStage('results')
      
      // Mark activity as complete
      if (activityId && r.data.score) {
        try {
          const xp = Math.round(r.data.percentage)
          await learningPathApi.completeActivity(activityId, 'quiz', xp)
        } catch (error) {
        }
      }
    } catch (e) {
      setStage('quiz')
      alert('Failed to submit quiz. Please try again.')
    }
  }
  
  const restartQuiz = () => {
    localStorage.removeItem('quizState')
    setStage('setup')
    setQuizId('')
    setQuestions([])
    setCurrentQuestionIndex(0)
    setUserAnswers(new Map())
    setCurrentAnswer('')
    setResults([])
    setShowFeedback(false)
  }

  if (!mounted) return null
  
  const currentQuestion = questions[currentQuestionIndex]
  // Progress should be based on answered questions, not current question
  const answeredCount = userAnswers.size
  const progress = questions.length > 0 ? (answeredCount / questions.length) * 100 : 0

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-indigo-900">
      <RequireAuth />
      
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent mb-2">
            🎯 German Quiz Challenge
          </h1>
          <p className="text-gray-600 dark:text-gray-400">Test your German skills with AI-powered questions</p>
        </div>

        {/* Setup Stage */}
        {stage === 'setup' && (
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Configure Your Quiz</h2>
            
            {/* Topic Selection */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Choose Topic</label>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {topics.map(topic => (
                  <button
                    key={topic.id}
                    onClick={() => setConfig({...config, topic: topic.id})}
                    className={`p-4 rounded-xl border-2 transition-all ${
                      config.topic === topic.id
                        ? 'border-indigo-600 bg-indigo-50 dark:bg-indigo-900 dark:border-indigo-400'
                        : 'border-gray-200 dark:border-gray-700 hover:border-indigo-300 dark:hover:border-indigo-600'
                    }`}
                  >
                    <div className="text-2xl mb-1">{topic.icon}</div>
                    <div className="text-sm font-medium text-gray-900 dark:text-white">{topic.name}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Level Selection */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Difficulty Level</label>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {levels.map(level => (
                  <button
                    key={level.id}
                    onClick={() => setConfig({...config, level: level.id})}
                    className={`p-4 rounded-xl border-2 transition-all ${
                      config.level === level.id
                        ? 'border-green-600 bg-green-50 dark:bg-green-900 dark:border-green-400'
                        : 'border-gray-200 dark:border-gray-700 hover:border-green-300 dark:hover:border-green-600'
                    }`}
                  >
                    <div className="text-lg font-bold text-gray-900 dark:text-white capitalize">{level.name}</div>
                    <div className="text-xs text-gray-600 dark:text-gray-400">{level.description}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Number of Questions */}
            <div className="mb-8">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                Number of Questions: <span className="text-indigo-600 font-bold">{config.size}</span>
              </label>
              <input
                type="range"
                min="5"
                max="20"
                value={config.size}
                onChange={(e) => setConfig({...config, size: parseInt(e.target.value)})}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>5 (Quick)</span>
                <span>20 (Challenge)</span>
              </div>
            </div>

            {/* Start Button */}
            <button
              onClick={startQuiz}
              className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-bold py-4 px-6 rounded-xl hover:from-indigo-700 hover:to-purple-700 transform hover:scale-105 transition-all shadow-lg"
            >
              🚀 Start Quiz
            </button>
          </div>
        )}

        {/* Loading Stage */}
        {stage === 'loading' && (
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-12 text-center">
            <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-indigo-600 mx-auto mb-4"></div>
            <p className="text-lg text-gray-600 dark:text-gray-400">Generating your quiz with AI...</p>
          </div>
        )}

        {/* Quiz Stage */}
        {stage === 'quiz' && currentQuestion && (
          <div className="space-y-6">
            {/* Back Button and Progress Bar */}
            <div className="flex items-center gap-4">
              <button
                onClick={restartQuiz}
                className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-all font-medium"
              >
                ← Back to Setup
              </button>
              <div className="flex-1 bg-white dark:bg-gray-800 rounded-xl shadow-lg p-4">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Question {currentQuestionIndex + 1} of {questions.length}
                  </span>
                  <span className="text-sm font-bold text-indigo-600">{Math.round(progress)}%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
                  <div
                    className="bg-gradient-to-r from-indigo-600 to-purple-600 h-3 rounded-full transition-all duration-500"
                    style={{ width: `${progress}%` }}
                  ></div>
                </div>
              </div>
            </div>

            {/* Question Card */}
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
              {/* Question Type Badge */}
              <div className="flex items-center gap-2 mb-4">
                <span className="px-3 py-1 bg-indigo-100 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-300 rounded-full text-xs font-medium">
                  {currentQuestion.type === 'mcq' && '☑️ Multiple Choice'}
                  {currentQuestion.type === 'fill_blank' && '✍️ Fill in the Blank'}
                  {currentQuestion.type === 'translation' && '🌐 Translation'}
                  {currentQuestion.type === 'sentence_order' && '🧩 Sentence Building'}
                  {currentQuestion.type === 'listening' && '🎧 Listening'}
                  {currentQuestion.type === 'reading' && '📖 Reading Comprehension'}
                  {currentQuestion.type === 'speaking' && '🎤 Speaking'}
                </span>
                {currentQuestion.skills && currentQuestion.skills.length > 0 && (
                  <span className="px-3 py-1 bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300 rounded-full text-xs font-medium">
                    {currentQuestion.skills[0].charAt(0).toUpperCase() + currentQuestion.skills[0].slice(1).replace(/_/g, ' ')}
                  </span>
                )}
                {config.level && (
                  <span className="px-3 py-1 bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 rounded-full text-xs font-medium">
                    {activeJourney?.type === 'student' && activeJourney?.level 
                      ? activeJourney.level.toUpperCase() 
                      : config.level.charAt(0).toUpperCase() + config.level.slice(1)}
                  </span>
                )}
              </div>

              {/* Question Content */}
              <div className="mb-6">
                {currentQuestion.type === 'mcq' && (
                  <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
                    {currentQuestion.question}
                  </h3>
                )}
                {currentQuestion.type === 'fill_blank' && (
                  <>
                    <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                      {currentQuestion.sentence}
                    </h3>
                    {currentQuestion.hint && (
                      <p className="text-sm text-gray-500 dark:text-gray-400 italic">💡 Hint: {currentQuestion.hint}</p>
                    )}
                  </>
                )}
                {currentQuestion.type === 'translation' && (
                  <>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">Translate to German:</p>
                    <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
                      {currentQuestion.english}
                    </h3>
                  </>
                )}
                {currentQuestion.type === 'sentence_order' && (
                  <>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">Arrange these words in the correct order:</p>
                    <div className="flex flex-wrap gap-2 mb-4">
                      {currentQuestion.scrambled_words?.map((word, i) => (
                        <span key={i} className="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg font-medium">
                          {word}
                        </span>
                      ))}
                    </div>
                  </>
                )}
                {currentQuestion.type === 'listening' && (
                  <>
                    <div className="bg-indigo-50 dark:bg-indigo-900/30 rounded-xl p-6 mb-4">
                      <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">🎧 Listen to the audio:</p>
                      <button
                        onClick={() => {
                          const utterance = new SpeechSynthesisUtterance(currentQuestion.audio_text)
                          utterance.lang = 'de-DE'
                          utterance.rate = 0.85
                          window.speechSynthesis.speak(utterance)
                        }}
                        className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-4 px-6 rounded-xl transition-all flex items-center justify-center gap-2"
                      >
                        🔊 Play Audio
                      </button>
                    </div>
                    <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
                      {currentQuestion.question}
                    </h3>
                  </>
                )}
                {currentQuestion.type === 'reading' && (
                  <>
                    <div className="bg-purple-50 dark:bg-purple-900/30 rounded-xl p-6 mb-4">
                      <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">📖 Read the passage:</p>
                      <p className="text-lg text-gray-900 dark:text-white leading-relaxed">
                        {currentQuestion.passage}
                      </p>
                    </div>
                    <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
                      {currentQuestion.question}
                    </h3>
                  </>
                )}
                {currentQuestion.type === 'speaking' && (
                  <>
                    <div className="bg-green-50 dark:bg-green-900/30 rounded-xl p-6 mb-4">
                      <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">🎤 Speaking Practice:</p>
                      <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
                        {currentQuestion.prompt}
                      </h3>
                    </div>
                    <p className="text-sm text-gray-500 dark:text-gray-400 italic mb-4">
                      💡 Type what you would say, or use the microphone button to record
                    </p>
                  </>
                )}
              </div>

              {/* Answer Input */}
              {!showFeedback && (
                <div className="space-y-4">
                  {currentQuestion.type === 'mcq' && currentQuestion.options && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {currentQuestion.options.map((option, i) => (
                        <button
                          key={i}
                          onClick={() => handleAnswer(option)}
                          className={`p-4 rounded-xl border-2 text-left transition-all ${
                            currentAnswer === option
                              ? 'border-indigo-600 bg-indigo-50 dark:bg-indigo-900 dark:border-indigo-400'
                              : 'border-gray-200 dark:border-gray-700 hover:border-indigo-300 dark:hover:border-indigo-600'
                          }`}
                        >
                          <span className="font-medium text-gray-900 dark:text-white">{option}</span>
                        </button>
                      ))}
                    </div>
                  )}
                  
                  {(currentQuestion.type === 'listening' || currentQuestion.type === 'reading') && currentQuestion.options && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {currentQuestion.options.map((option, i) => (
                        <button
                          key={i}
                          onClick={() => handleAnswer(option)}
                          className={`p-4 rounded-xl border-2 text-left transition-all ${
                            currentAnswer === option
                              ? 'border-indigo-600 bg-indigo-50 dark:bg-indigo-900 dark:border-indigo-400'
                              : 'border-gray-200 dark:border-gray-700 hover:border-indigo-300 dark:hover:border-indigo-600'
                          }`}
                        >
                          <span className="font-medium text-gray-900 dark:text-white">{option}</span>
                        </button>
                      ))}
                    </div>
                  )}
                  
                  {(currentQuestion.type === 'fill_blank' || currentQuestion.type === 'translation' || currentQuestion.type === 'sentence_order') && (
                    <input
                      type="text"
                      value={currentAnswer}
                      onChange={(e) => handleAnswer(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && submitAnswer()}
                      placeholder="Type your answer here..."
                      className="w-full px-4 py-3 border-2 border-gray-300 dark:border-gray-600 rounded-xl focus:border-indigo-600 focus:ring-2 focus:ring-indigo-200 dark:bg-gray-700 dark:text-white text-lg"
                      autoFocus
                    />
                  )}
                  
                  {currentQuestion.type === 'speaking' && (
                    <div className="space-y-3">
                      <div className="flex gap-3">
                        <input
                          type="text"
                          value={currentAnswer}
                          onChange={(e) => handleAnswer(e.target.value)}
                          onKeyPress={(e) => e.key === 'Enter' && submitAnswer()}
                          placeholder="Type your answer here..."
                          className="flex-1 px-4 py-3 border-2 border-gray-300 dark:border-gray-600 rounded-xl focus:border-indigo-600 focus:ring-2 focus:ring-indigo-200 dark:bg-gray-700 dark:text-white text-lg"
                          autoFocus
                        />
                        <button
                          onClick={() => {
                            if (isRecording) {
                              setIsRecording(false)
                              return
                            }
                            
                            setIsRecording(true)
                            const recognition = new (window as any).webkitSpeechRecognition()
                            recognition.lang = 'de-DE'
                            recognition.continuous = false
                            recognition.interimResults = false
                            
                            recognition.onresult = (event: any) => {
                              const transcript = event.results[0][0].transcript
                              handleAnswer(transcript)
                              setIsRecording(false)
                            }
                            
                            recognition.onerror = () => {
                              setIsRecording(false)
                            }
                            
                            recognition.onend = () => {
                              setIsRecording(false)
                            }
                            
                            recognition.start()
                          }}
                          className={`px-6 py-3 rounded-xl font-bold transition-all flex items-center gap-2 ${
                            isRecording 
                              ? 'bg-red-600 hover:bg-red-700 text-white animate-pulse' 
                              : 'bg-green-600 hover:bg-green-700 text-white'
                          }`}
                        >
                          {isRecording ? '⏹️ Stop' : '🎤 Record'}
                        </button>
                      </div>
                      <p className="text-xs text-gray-500 dark:text-gray-400 italic">
                        💡 Click the microphone to record your voice, or type your answer
                      </p>
                    </div>
                  )}

                  <button
                    onClick={submitAnswer}
                    disabled={!currentAnswer.trim()}
                    className="w-full bg-indigo-600 text-white font-bold py-3 px-6 rounded-xl hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-all"
                  >
                    Check Answer
                  </button>
                </div>
              )}

              {/* Feedback */}
              {showFeedback && (
                <div className={`p-6 rounded-xl ${
                  isCorrect 
                    ? 'bg-green-50 dark:bg-green-900 border-2 border-green-500' 
                    : 'bg-red-50 dark:bg-red-900 border-2 border-red-500'
                }`}>
                  <div className="flex items-center gap-3 mb-3">
                    <div className="text-3xl">{isCorrect ? '✅' : '❌'}</div>
                    <div>
                      <h4 className="text-xl font-bold text-gray-900 dark:text-white">
                        {isCorrect ? 'Correct!' : 'Not quite right'}
                      </h4>
                      {!isCorrect && (
                        <p className="text-sm text-gray-700 dark:text-gray-300">
                          Correct answer: <span className="font-bold">{currentQuestion.answer}</span>
                        </p>
                      )}
                    </div>
                  </div>
                  {currentQuestion.explanation && (
                    <p className="text-gray-700 dark:text-gray-300 mb-4">
                      💡 {currentQuestion.explanation}
                    </p>
                  )}
                  <button
                    onClick={nextQuestion}
                    className="w-full bg-indigo-600 text-white font-bold py-3 px-6 rounded-xl hover:bg-indigo-700 transition-all"
                  >
                    {currentQuestionIndex < questions.length - 1 ? 'Next Question →' : 'See Results 🎉'}
                  </button>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Results Stage */}
        {stage === 'results' && (
          <div className="space-y-6">
            {/* Score Card */}
            <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl shadow-xl p-8 text-white text-center">
              <div className="text-6xl mb-4">🎉</div>
              <h2 className="text-3xl font-bold mb-2">Quiz Complete!</h2>
              <div className="text-6xl font-bold mb-2">{percentage}%</div>
              <p className="text-xl mb-4">{score} out of {questions.length} correct</p>
              <div className="flex justify-center gap-4">
                <div className="bg-white bg-opacity-20 rounded-lg px-4 py-2">
                  <div className="text-sm opacity-80">Time</div>
                  <div className="font-bold">{Math.round((Date.now() - startTime) / 1000)}s</div>
                </div>
                <div className="bg-white bg-opacity-20 rounded-lg px-4 py-2">
                  <div className="text-sm opacity-80">Accuracy</div>
                  <div className="font-bold">{percentage}%</div>
                </div>
              </div>
            </div>

            {/* Strengths & Weaknesses */}
            <div className="grid md:grid-cols-2 gap-6">
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                <h3 className="text-lg font-bold text-green-600 dark:text-green-400 mb-3">💪 Strengths</h3>
                <div className="space-y-2">
                  {strengths.map((s, i) => (
                    <div key={i} className="px-3 py-2 bg-green-50 dark:bg-green-900 text-green-700 dark:text-green-300 rounded-lg">
                      {s.charAt(0).toUpperCase() + s.slice(1).replace(/_/g, ' ')}
                    </div>
                  ))}
                </div>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                <h3 className="text-lg font-bold text-orange-600 dark:text-orange-400 mb-3">📚 Areas to Improve</h3>
                <div className="space-y-2">
                  {weaknesses.map((w, i) => (
                    <div key={i} className="px-3 py-2 bg-orange-50 dark:bg-orange-900 text-orange-700 dark:text-orange-300 rounded-lg">
                      {w.charAt(0).toUpperCase() + w.slice(1).replace(/_/g, ' ')}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Detailed Results */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">📊 Detailed Results</h3>
              <div className="space-y-3">
                {results.map((result, i) => (
                  <div key={i} className={`p-4 rounded-lg border-2 ${
                    result.correct 
                      ? 'border-green-200 bg-green-50 dark:bg-green-900 dark:border-green-700' 
                      : 'border-red-200 bg-red-50 dark:bg-red-900 dark:border-red-700'
                  }`}>
                    <div className="flex items-start gap-3">
                      <div className="text-2xl">{result.correct ? '✅' : '❌'}</div>
                      <div className="flex-1">
                        <p className="font-medium text-gray-900 dark:text-white mb-1">Question {i + 1}</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          Your answer: <span className="font-medium">{result.user_answer || '(no answer)'}</span>
                        </p>
                        {!result.correct && (
                          <p className="text-sm text-gray-600 dark:text-gray-400">
                            Correct answer: <span className="font-medium text-green-600 dark:text-green-400">{result.correct_answer}</span>
                          </p>
                        )}
                        {result.explanation && (
                          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1 italic">
                            💡 {result.explanation}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex justify-center">
              <button
                onClick={restartQuiz}
                className="bg-indigo-600 text-white font-bold py-3 px-8 rounded-xl hover:bg-indigo-700 transition-all"
              >
                📝 New Quiz
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
