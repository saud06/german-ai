# Learning Purpose Wrapper – Specification

This document defines the **learning purpose wrapper** for the AI German learning platform.  
It describes the four initial user journeys (Student, Traveler, Professional, Hobby), how the wrapper influences the user experience, and an implementation roadmap **without backend code**.

---

## 1. Concept Overview

The **learning purpose wrapper** is a layer around the existing app that:

- Asks each new user for their **primary purpose** of learning German.
- Optionally allows **secondary purposes**.
- Uses this information to:
  - Adapt onboarding.
  - Prioritize and filter content.
  - Change UI wording, milestones, and dashboards.
  - Drive recommendations and notifications.
- Allows the user to **change** their purpose later.

Initial purposes:

1. Student (exam / structured learning)
2. Traveler (travel & culture)
3. Professional (work & career)
4. Hobby (personal interest / fun)

The goal is to make the app feel **relevant and tailored** from the first session.

---

## 2. User Experience Flow

### 2.1. Onboarding Flow

**Trigger:** First-time sign-up or first app open (if logged in via SSO or similar).

**Steps:**

1. **Intro Screen**  
   - Short explanation:  
     > “To personalize your learning experience, what is your main goal with German?”

2. **Primary Purpose Selection**  
   - Present four large, visually distinct options (cards or tiles):
     - **Student** – “Prepare for exams or structured levels (A1–C1).”
     - **Traveler** – “Travel, culture, and real-life conversations.”
     - **Professional** – “Use German at work or for your career.”
     - **Hobby** – “Learn for fun, media, and personal interest.”
   - User must pick **one** primary purpose to proceed.

3. **Secondary Purpose (Optional)**  
   - Show smaller checkboxes or tags with the same four options (excluding the already selected primary).
   - Label:  
     > “Any other reasons you’re interested in German? (optional)”
   - User may select zero or more.

4. **Level / Experience (Optional or Use Existing Flow)**  
   - Keep existing mechanism for level selection (A1–C1, beginner–advanced, etc.).
   - This can be:
     - Self-assessment, or
     - Quick placement quiz (if already implemented).

5. **Confirmation Screen**  
   - Short summary:
     - “You chose: **Traveler** as your main goal.”
     - “Based on this, we’ll focus on real-life travel scenarios, culture, and survival phrases.”
   - CTA: “Start your tailored journey.”

6. **Routing to Relevant Home/Dashboard**  
   - User is taken to a **purpose-specific dashboard** (detailed in section 3).

---

### 2.2. Existing User Handling

For existing users (before wrapper is introduced):

- Show an **in-app prompt** once after update:
  - “We’ve added personalized journeys. What is your main goal with German?”
- Let them set primary and secondary purposes.
- Default behavior if they skip:
  - Use a neutral/default experience (e.g., Student or Hobby), but keep asking them occasionally in a non-intrusive way.
- Add a “Change learning goal” option in **Settings → Learning Profile**.

---

## 3. Purpose-Specific Journeys

Each purpose defines:

- Tone and wording of the UI (microcopy).
- Recommended content types and order.
- Types of scenarios highlighted.
- Milestones and progress indicators.
- Optional paid/advanced features to emphasize (without implementing payment logic here).

Below: each journey’s intent and how the wrapper tailors the experience.

---

### 3.1. Student Journey

**Use Case:**  
Users preparing for exams (Goethe, TestDaF, TELC, etc.) or wanting structured level-based progress (A1–C1).

**High-Level Experience:**

- Emphasis on **structure**, **levels**, and **exam-readiness**.
- Curriculum-like progression: A1 → A2 → B1 → B2 → C1.
- Strong focus on grammar, vocabulary, reading, writing, and listening skills.
- Regular mock tests and progress checks (where app supports them).

#### 3.1.1. Dashboard Layout

- **Title / Hero area**  
  - “Your Exam & Level Journey”
- **Primary CTA**  
  - “Continue your A2 path” or “Start your A1 journey.”
- **Sections:**
  - “Core Lessons” (curriculum-style modules).
  - “Exam Practice” (mock tests, exam-style questions).
  - “Grammar Boosters” (short drills).
  - “Writing & Speaking Practice” (if available).
  - “Progress to Next Level” (visual progress bar).

#### 3.1.2. Content Priorities

- Prioritize:
  - Lessons with **level tags** (A1–C1).
  - Structured grammar content.
  - Exam-style exercises (MCQs, fill-in-the-blank, writing prompts).
- Show travel/professional scenarios only as **supporting examples**, not the main focus.

#### 3.1.3. Milestones & Feedback

- Examples:
  - “Complete A1 core lessons.”
  - “Score 70%+ on A2 mock test.”
  - “Write a 150-word essay on [topic].”
- Progress messages:
  - “You’re on track for your planned exam date.”
  - “You’ve improved your grammar accuracy by X% in the last 2 weeks.”

---

### 3.2. Traveler Journey

**Use Case:**  
Users learning German for trips, short stays, or cultural experiences.

**High-Level Experience:**

- Focus on **speaking**, **listening**, and **survival phrases**.
- Real-world scenarios: airports, restaurants, hotels, public transport, emergencies.
- Lots of cultural tips and “do/don’t” guidance.
- Less emphasis on deep grammar; more on being understood and feeling confident.

#### 3.2.1. Dashboard Layout

- **Title / Hero area**  
  - “Get Ready for Your Trip”
- **Primary CTA**  
  - “Practice a real travel scenario.”
- **Sections:**
  - “Essential Phrases for Your Trip.”
  - “Real-Life Scenarios” (airport, hotel, restaurant, etc.).
  - “Culture & Etiquette.”
  - “Pronunciation & Listening Practice.”
  - “Travel Readiness Meter” (visual indicator).

#### 3.2.2. Content Priorities

- Prioritize:
  - Scenario-based speaking practice.
  - Short lessons (5–15 minutes).
  - Dialogues and role-plays.
  - Cultural/lifestyle snippets.
- Deprioritize:
  - Long grammar explanations.
  - Exam-style questions (only as optional extras).

#### 3.2.3. Milestones & Feedback

- Examples:
  - “Order at a restaurant without English.”
  - “Ask for and understand directions.”
  - “Check into a hotel confidently.”
- Feedback messages:
  - “You’re 80% ready for everyday conversations on your trip.”
  - “Your pronunciation is improving steadily—great for real interactions.”

---

### 3.3. Professional Journey

**Use Case:**  
Users needing German for work, career growth, or professional relocation.

**High-Level Experience:**

- Focus on **formal communication**, **professional vocabulary**, and **workplace culture**.
- Email writing, meetings, presentations, interviews.
- Optionally industry-specific content (tech, finance, healthcare) – even if only partially available.

#### 3.3.1. Dashboard Layout

- **Title / Hero area**  
  - “Business & Career German”
- **Primary CTA**  
  - “Continue your workplace communication path.”
- **Sections:**
  - “Core Business German Lessons.”
  - “Email & Message Writing.”
  - “Meetings & Presentations.”
  - “Job Interviews & Networking.”
  - “Professional Culture & Norms.”

#### 3.3.2. Content Priorities

- Prioritize:
  - Formal/semiformal language usage.
  - Scenario-based professional dialogs (meetings, stand-ups, reviews, negotiation).
  - Writing exercises (emails, reports) if supported by app.
  - Level-aware content (e.g., B1+ for some business content).
- Treat travel/hobby content as optional extras.

#### 3.3.3. Milestones & Feedback

- Examples:
  - “Introduce yourself in a professional setting.”
  - “Write a clear professional email.”
  - “Lead a short meeting in German.”
- Feedback messages:
  - “Your vocabulary is expanding in [business domain].”
  - “You’re getting more comfortable with formal phrases.”

---

### 3.4. Hobby Journey

**Use Case:**  
Users learning for fun, curiosity, or personal interest (media, music, friends, etc.).

**High-Level Experience:**

- Emphasis on **enjoyment**, **interests**, and **low pressure**.
- Content-centered: songs, movies, series, news, YouTube-style material (where available).
- Gentle introduction to grammar through context rather than theory-first.

#### 3.4.1. Dashboard Layout

- **Title / Hero area**  
  - “Enjoy Learning German Your Way”
- **Primary CTA**  
  - “Pick something fun to explore today.”
- **Sections:**
  - “Learn Through Media” (songs, clips, articles).
  - “Topics You Like” (sports, politics, tech, art, etc.).
  - “Light Practice” (short quizzes, vocab games).
  - “Casual Conversations & Phrases.”

#### 3.4.2. Content Priorities

- Prioritize:
  - Content tagged with specific interests/topics.
  - Short, fun lessons and games.
  - Real-world media (where the app supports it).
- Provide grammar as:
  - “Did you notice this pattern?” style, not heavy explanations (unless user opts in).

#### 3.4.3. Milestones & Feedback

- Examples:
  - “Watch a short video and understand X% without subtitles.”
  - “Learn 50 words related to your favorite topic.”
  - “Chat casually about your hobbies in German.”
- Feedback messages:
  - “You’ve spent X hours enjoying German content.”
  - “You’re expanding your vocabulary in your favorite topics.”

---

## 4. Cross-Journey Rules

These rules apply across all four journeys to keep the product coherent.

### 4.1. Shared Features

Regardless of purpose, all users should still have access to:

- Core app navigation (Home, Lessons, Scenarios, Profile, Settings).
- Main AI conversation features.
- Base learning content (with different ordering/priorities).
- Progress tracking and history.

The wrapper **changes emphasis and ordering**, not the existence of core features.

---

### 4.2. Journey-Specific UI Copy

The wrapper can modify:

- **Headlines** (e.g., “Your Exam Prep Journey” vs “Get Ready for Your Trip”).
- **Subtitles / helper text** (e.g., “Short, practical lessons to use on your next trip.”).
- **Empty states** (e.g., when no recommendations, show journey-specific suggestions).
- **CTA labels** (“Start Mock Exam” vs “Practice Travel Scenario”).

---

### 4.3. Allowing Purpose Change

In **Settings → Learning Profile**:

- Show current primary purpose and secondary purposes.
- Allow:
  - Changing primary purpose.
  - Adding/removing secondary purposes.
- After change:
  - Show a short “Your journey has been updated” confirmation.
  - Redirect to the updated dashboard.
- Optionally ask:
  - “Why did you change your goal?” (for analytics).

---

## 5. Implementation Plan (High-Level, No Timelines)

This section gives a **sequence of work**, not tied to specific dates.

### 5.1. Design & UX

1. Define final UI texts for:
   - Purpose selection screen.
   - Journey-specific dashboard headings and descriptions.
2. Design wireframes / mockups for:
   - Onboarding screens (purpose selection).
   - Four purpose-specific dashboards.
   - Settings → Learning Profile page.
3. Decide how existing navigation is adapted:
   - Does “Home” change per purpose?
   - Do we show purpose-specific tabs?

### 5.2. Data & Configuration (Conceptual, No Code)

1. Ensure each piece of content can be **tagged by purpose**:
   - Student / Traveler / Professional / Hobby (multiple tags allowed).
2. Optionally ensure content can be:
   - **Level-tagged** (A1–C1).
   - **Topic-tagged** (e.g., food, work, travel, culture).
3. Prepare a mapping document:
   - For each existing key content/scenario, define:
     - Appropriate purposes.
     - Recommended level (if applicable).
   - This can be a simple spreadsheet managed by you and your brother.

### 5.3. Wrapper Logic (Conceptual)

1. When user logs in:
   - Check if they have a **primary purpose** set.
   - If not, show purpose selection flow.
2. On the home/dashboard:
   - Determine current journey from primary purpose.
   - Use journey rules to:
     - Choose which **sections** to show.
     - Decide **ordering** of sections and items.
     - Select **copy** for headings.
3. For content lists (e.g., recommended lessons):
   - Use content tags (purpose + level) to filter and rank.
4. In navigation:
   - Optionally show a small badge or label:
     - “Student Journey” / “Travel Journey” etc.

### 5.4. Settings Integration

1. Add a “Learning Profile” section in user settings:
   - Show current primary and secondary purposes.
   - Simple UI to change them.
2. When updated:
   - Immediately re-calculate home screen layout.
   - Next visit to dashboard uses new journey configuration.

### 5.5. Analytics (Conceptual)

1. Track events keyed by journey:
   - `journey_selected` (student/traveler/professional/hobby).
   - `journey_changed`.
   - `content_started` (with journey + content tags).
   - `content_completed`.
2. For each journey:
   - Monitor:
     - Activation rates (first lesson completed).
     - Retention (returning usage).
     - Content engagement.
3. Use metrics to:
   - Improve each journey.
   - Decide where to add more content.
   - Prioritize new features.

---

## 6. Open Questions for Future Iteration

- Should users be allowed to **follow multiple journeys actively** at once (e.g., Student + Traveler) or keep one as “primary” and others as “secondary only”?
- Should each journey have **its own streaks, badges, and achievements**, or one global system?
- How aggressively should we **suggest changing journeys** if behavior doesn’t match stated goal (e.g., a “student” mostly uses travel scenarios)?
- Eventually: Should we create **journey-specific onboarding mini-tutorials** to explain what each path offers?

---

## 7. Summary

This wrapper:

- Wraps the current app in **four tailored experiences**.
- Does **not** require rewriting core functionalities.
- Reuses existing content and features by **re-ordering and retargeting** them based on user goals.
- Creates a foundation for:
  - Better personalization.
  - Better analytics.
  - Stronger positioning (“German for Students / Travelers / Professionals / Hobbyists”).

Implementation should start with:

1. UX copy & design for selection + dashboards.
2. Content tagging by purpose.
3. Purpose selection onboarding.
4. Journey-specific dashboards and section ordering.
5. Settings integration to change purpose.

Once these are in place, you can refine and expand each journey without changing the overall wrapper concept.
  