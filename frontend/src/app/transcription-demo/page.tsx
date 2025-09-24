"use client"
import React, { useState } from 'react'

export default function TranscriptionDemo() {
  const [isRecording, setIsRecording] = useState(false)
  const [step, setStep] = useState(0)

  const demoSteps = [
    {
      title: "Initial State",
      expected: ["Ich", "gehe", "zur", "Schule"],
      spoken: [],
      description: "User hasn't started speaking yet"
    },
    {
      title: "First Word (Interim)",
      expected: ["Ich", "gehe", "zur", "Schule"],
      spoken: [{ word: "Ich", status: "correct", isFinal: false }],
      description: "User says 'Ich' - still processing (interim result)"
    },
    {
      title: "First Word (Final)",
      expected: ["Ich", "gehe", "zur", "Schule"],
      spoken: [{ word: "Ich", status: "correct", isFinal: true }],
      description: "First word confirmed as correct"
    },
    {
      title: "Second Word Added",
      expected: ["Ich", "gehe", "zur", "Schule"],
      spoken: [
        { word: "Ich", status: "correct", isFinal: true },
        { word: "gehe", status: "correct", isFinal: false }
      ],
      description: "User continues with 'gehe'"
    },
    {
      title: "Pronunciation Issue",
      expected: ["Ich", "gehe", "zur", "Schule"],
      spoken: [
        { word: "Ich", status: "correct", isFinal: true },
        { word: "gehe", status: "correct", isFinal: true },
        { word: "zu", status: "similar", isFinal: false }
      ],
      description: "User says 'zu' instead of 'zur' - similar but not exact"
    },
    {
      title: "Complete with Extra Word",
      expected: ["Ich", "gehe", "zur", "Schule"],
      spoken: [
        { word: "Ich", status: "correct", isFinal: true },
        { word: "gehe", status: "correct", isFinal: true },
        { word: "zu", status: "similar", isFinal: true },
        { word: "Schule", status: "correct", isFinal: true },
        { word: "heute", status: "extra", isFinal: true }
      ],
      description: "Complete sentence with extra word 'heute'"
    }
  ]

  const currentStep = demoSteps[step]

  const getWordColor = (status: string, isFinal: boolean) => {
    const opacity = isFinal ? '' : ' opacity-70 animate-pulse'
    switch (status) {
      case 'correct': return `bg-green-100 text-green-800 border-green-200${opacity}`
      case 'similar': return `bg-yellow-100 text-yellow-800 border-yellow-200${opacity}`
      case 'incorrect': return `bg-red-100 text-red-800 border-red-200${opacity}`
      case 'extra': return `bg-blue-100 text-blue-800 border-blue-200${opacity}`
      default: return `bg-gray-100 text-gray-600 border-gray-200${opacity}`
    }
  }

  const nextStep = () => {
    setStep((prev) => (prev + 1) % demoSteps.length)
  }

  const prevStep = () => {
    setStep((prev) => (prev - 1 + demoSteps.length) % demoSteps.length)
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="text-center space-y-2">
        <h1 className="text-2xl font-bold">Live Transcription Demo</h1>
        <p className="text-gray-600">See how word-by-word transcription should look</p>
      </div>

      {/* Demo Controls */}
      <div className="flex items-center justify-center gap-4">
        <button 
          onClick={prevStep}
          className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
        >
          ← Previous
        </button>
        <span className="font-medium">
          Step {step + 1} of {demoSteps.length}: {currentStep.title}
        </span>
        <button 
          onClick={nextStep}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Next →
        </button>
      </div>

      {/* Live Transcription Card Demo */}
      <div className="rounded-lg border-2 border-blue-200 bg-blue-50 p-4 space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-blue-900">🎤 Live Transcription</h3>
          <div className="flex items-center gap-2">
            {currentStep.spoken.length > 0 && (
              <div className="flex items-center gap-1">
                <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                <span className="text-xs text-red-600 font-medium">Recording</span>
              </div>
            )}
          </div>
        </div>

        {/* Expected sentence */}
        <div className="space-y-1">
          <div className="text-xs font-medium text-gray-600">Expected:</div>
          <div className="flex flex-wrap gap-1">
            {currentStep.expected.map((word, index) => (
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
            {currentStep.spoken.length > 0 ? (
              currentStep.spoken.map((wordResult, index) => {
                const colorClass = getWordColor(wordResult.status, wordResult.isFinal)
                
                return (
                  <span
                    key={index}
                    className={`px-2 py-1 text-sm border rounded transition-all duration-200 ${colorClass}`}
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
                Start recording to see live transcription
              </span>
            )}
          </div>
        </div>

        {/* Real-time feedback */}
        {currentStep.spoken.length > 0 && (
          <div className="text-xs text-gray-600 bg-white rounded p-2 border">
            <div className="flex items-center justify-between">
              <span>Progress: {currentStep.spoken.filter(w => w.isFinal).length}/{currentStep.expected.length} words</span>
              <span>
                Accuracy: {Math.round((currentStep.spoken.filter(w => w.status === 'correct').length / Math.max(currentStep.expected.length, currentStep.spoken.length)) * 100)}%
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
            <span className="flex items-center gap-1">
              <div className="w-3 h-3 bg-gray-100 border border-gray-200 rounded opacity-70"></div>
              Processing...
            </span>
          </div>
        </div>
      </div>

      {/* Step Description */}
      <div className="bg-white rounded-lg border p-4">
        <h4 className="font-semibold mb-2">What's happening:</h4>
        <p className="text-gray-700">{currentStep.description}</p>
      </div>

      {/* Instructions */}
      <div className="bg-yellow-50 rounded-lg border border-yellow-200 p-4">
        <h4 className="font-semibold text-yellow-800 mb-2">How it works in real usage:</h4>
        <ul className="text-sm text-yellow-700 space-y-1">
          <li>• Words appear in real-time as you speak</li>
          <li>• Colors change based on pronunciation accuracy</li>
          <li>• Interim results show with dots (...) and are slightly faded</li>
          <li>• Final results are solid and confirmed</li>
          <li>• Progress and accuracy update live</li>
        </ul>
      </div>
    </div>
  )
}
