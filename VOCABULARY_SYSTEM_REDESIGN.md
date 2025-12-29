# 🔧 Vocabulary System Redesign

## Problems Identified

### 1. AI Model
- ✅ **Confirmed**: Using **Mistral 7B** via Ollama
- Location: `/backend/app/config.py` line 29: `OLLAMA_MODEL: str = "mistral:7b"`
- Also has faster model: `OLLAMA_MODEL_FAST: str = "llama3.2:3b"`

### 2. Progress Not Updating
**Root Cause**: Vocabulary completion tracking was added, but:
- Vocab page expects `activity_id` parameter from learning path
- Learning path expects `vocab_sets` collection with proper structure
- Current vocab system uses `seed_words` collection (flat word list)
- **Mismatch**: Activities point to vocab_sets that don't exist

### 3. Poor UX in "Today" Tab
- Shows only 1 random word
- No next/prev navigation
- Users can't learn multiple words in one session
- Unclear how to complete the activity

### 4. No Completion Criteria
- Users don't know: "How many words = complete?"
- No progress indicator within vocabulary activity
- Completion is based on review submission, but unclear requirements

### 5. Limited Word Database
**Current State**:
- `seed_words.csv`: ~5 words (A1, A2, B1)
- `word_bank_large.json`: ~57 words
  - A1: ~20 words (35%)
  - A2: ~13 words (23%)
  - B1: ~12 words (21%)
  - B2: ~12 words (21%)
  - C1-C2: 0 words (0%)

**Required Distribution** (for 1000+ words):
- A1-A2: 60% (600 words) - Most frequent
- B1-B2: 30% (300 words) - Moderate
- C1-C2: 10% (100 words) - Advanced

## Solution Design

### Architecture

```
Learning Path
    ↓
Location (Das Café)
    ↓
Vocabulary Set (Das Café Vocabulary)
    ↓
Words Collection (10-15 words)
    ↓
User learns → Reviews → Completes
```

### Data Model

#### VocabularySet Collection
```javascript
{
  _id: ObjectId,
  location_id: ObjectId,
  chapter_id: ObjectId,
  title: "Das Café Vocabulary",
  description: "Essential vocabulary for das café",
  level: "A1",
  words: [
    {
      word: "der Kaffee",
      translation: "coffee",
      example: "Ich trinke Kaffee.",
      audio_url: null
    },
    // 10-15 words per set
  ],
  total_words: 12,
  completion_criteria: {
    min_words_learned: 10,  // Learn 10 out of 12
    min_reviews: 1          // Complete 1 review session
  },
  xp_reward: 50,
  estimated_minutes: 10
}
```

#### User Progress Tracking
```javascript
{
  user_id: "user123",
  vocab_set_progress: {
    "vocab_set_id_1": {
      words_learned: 10,
      reviews_completed: 1,
      last_review: ISODate,
      is_completed: true
    }
  }
}
```

### UX Improvements

#### Today Tab Redesign
```
┌─────────────────────────────────────┐
│ Vocab Coach - Today's Words         │
├─────────────────────────────────────┤
│                                     │
│  Word 1 of 10                       │
│                                     │
│  ┌───────────────────────────────┐ │
│  │  der Kaffee                   │ │
│  │  coffee                       │ │
│  │                               │ │
│  │  Ich trinke Kaffee.          │ │
│  │  I drink coffee.             │ │
│  └───────────────────────────────┘ │
│                                     │
│  [Listen] [Save] [← Prev] [Next →] │
│                                     │
│  Progress: ████████░░ 8/10         │
│                                     │
└─────────────────────────────────────┘
```

#### Learning Path Integration
```
User clicks "Das Café Vocabulary"
    ↓
Redirects to: /vocab?activity_id=VOCAB_SET_ID&mode=learning_path
    ↓
Shows words from that specific vocabulary set
    ↓
User learns words (next/prev navigation)
    ↓
After learning 10/12 words, shows "Start Review" button
    ↓
User completes review
    ↓
Calls completeActivity API
    ↓
Progress bar updates ✅
```

## Implementation Plan

### Phase 1: Database Structure
1. Create `vocab_sets` collection
2. Migrate existing words to structured sets
3. Create location-specific vocabulary sets
4. Expand word database (A1-C2)

### Phase 2: Backend API
1. Add vocab set endpoints
2. Update completion tracking
3. Add progress calculation
4. Link vocab sets to locations

### Phase 3: Frontend UX
1. Redesign "Today" tab with navigation
2. Add learning path mode
3. Show progress indicators
4. Implement completion flow

### Phase 4: Content
1. Generate 1000+ words across all levels
2. Organize by themes/locations
3. Add audio URLs (future)
4. Create review algorithms

## Completion Criteria

### For Users
- **Learn**: View and save 10 out of 12 words in a set
- **Review**: Complete 1 review session with those words
- **Result**: Activity marked complete, +50 XP

### Clear Indicators
- "Words Learned: 8/10" progress bar
- "Ready for Review" button appears at 10/10
- "Complete Review to finish" message
- Checkmark on learning path after completion

## Benefits

✅ **Clear Progress**: Users see exactly how many words to learn
✅ **Better UX**: Next/prev navigation for learning multiple words
✅ **Proper Integration**: Vocabulary sets linked to locations
✅ **Scalable**: Easy to add more words and sets
✅ **Motivating**: Clear completion criteria and rewards
