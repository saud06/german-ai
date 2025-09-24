# Live Transcription Card - Visual Example

## How it should look when working:

### 1. Initial State (Not Recording)
```
┌─────────────────────────────────────────────────────────────┐
│ 🎤 Live Transcription                                       │
├─────────────────────────────────────────────────────────────┤
│ Expected:                                                   │
│ [Ich] [gehe] [zur] [Schule]                                │
│                                                             │
│ You're saying:                                              │
│ Start recording to see live transcription                   │
└─────────────────────────────────────────────────────────────┘
```

### 2. While Recording - Word by Word Appearance
```
┌─────────────────────────────────────────────────────────────┐
│ 🎤 Live Transcription                    🔴 Recording       │
├─────────────────────────────────────────────────────────────┤
│ Expected:                                                   │
│ [Ich] [gehe] [zur] [Schule]                                │
│                                                             │
│ You're saying:                                              │
│ [Ich...] (interim - gray with dots)                        │
└─────────────────────────────────────────────────────────────┘
```

### 3. As More Words Are Spoken
```
┌─────────────────────────────────────────────────────────────┐
│ 🎤 Live Transcription                    🔴 Recording       │
├─────────────────────────────────────────────────────────────┤
│ Expected:                                                   │
│ [Ich] [gehe] [zur] [Schule]                                │
│                                                             │
│ You're saying:                                              │
│ [Ich] [gehe...] [zu...]                                    │
│  ✓     ✓        ⚠️                                         │
│ Green  Green   Yellow (similar to "zur")                   │
└─────────────────────────────────────────────────────────────┘
```

### 4. Complete Sentence with Feedback
```
┌─────────────────────────────────────────────────────────────┐
│ 🎤 Live Transcription                    🔴 Recording       │
├─────────────────────────────────────────────────────────────┤
│ Expected:                                                   │
│ [Ich] [gehe] [zur] [Schule]                                │
│                                                             │
│ You're saying:                                              │
│ [Ich] [gehe] [zu] [Schule] [heute]                         │
│  ✓     ✓      ⚠️    ✓       +                             │
│                                                             │
│ Progress: 4/4 words | Accuracy: 85%                        │
│                                                             │
│ Legend: ✓ Correct ⚠️ Similar ❌ Incorrect + Extra          │
└─────────────────────────────────────────────────────────────┘
```

## Color Coding:
- 🟢 Green: Perfect match (90%+ similarity)
- 🟡 Yellow: Close match (70-89% similarity) 
- 🔴 Red: Poor match (<70% similarity)
- 🔵 Blue: Extra words not in expected sentence
- ⚪ Gray with dots: Interim results (still processing)
