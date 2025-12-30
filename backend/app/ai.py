from __future__ import annotations
from typing import List, Optional, Dict, Any
import json

from .config import settings


async def generate_questions(track: Optional[str], size: int, level: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Generate quiz questions with multiple types: MCQ, fill-in-blank, translation, sentence-building, listening, reading, speaking.
    Uses Mistral 7B locally first, falls back to OpenAI if configured.
    """
    
    # Try Mistral 7B first (local, free, fast)
    try:
        from .ollama_client import ollama_client
        
        if ollama_client.is_available:
            # Define question type distribution
            question_types = [
                {"type": "mcq", "description": "Multiple choice with 4 options"},
                {"type": "fill_blank", "description": "Fill in the blank with correct word"},
                {"type": "translation", "description": "Translate English to German"},
                {"type": "sentence_order", "description": "Arrange words in correct order"},
                {"type": "listening", "description": "Listen to German audio and answer"},
                {"type": "reading", "description": "Read a short passage and answer comprehension questions"},
                {"type": "speaking", "description": "Speak a German phrase or sentence"}
            ]
            
            system_prompt = f"""You are an expert German language teacher creating engaging, dynamic quiz questions.

Level: {level or 'intermediate'}
Topic: {track or 'mixed grammar'}
Number of questions: {size}

Create a diverse mix of question types:
1. MCQ (Multiple Choice): Test grammar, vocabulary, or comprehension
2. Fill-in-blank: Complete sentences with correct word/form
3. Translation: Translate simple English phrases to German
4. Sentence order: Arrange scrambled German words correctly
5. Listening: Provide German text to be spoken, ask comprehension question
6. Reading: Short German passage (2-3 sentences) with comprehension question
7. Speaking: Prompt user to speak a German phrase/sentence

Return ONLY a JSON array:
[
  {{
    "id": "q1",
    "type": "mcq",
    "question": "Welcher Artikel ist richtig? ___ Buch ist interessant.",
    "options": ["Der", "Die", "Das", "Den"],
    "answer": "Das",
    "explanation": "'Buch' is neuter, so it uses 'das'",
    "skills": ["articles"]
  }},
  {{
    "id": "q2",
    "type": "fill_blank",
    "sentence": "Ich ___ nach Berlin.",
    "blank_position": 1,
    "answer": "gehe",
    "hint": "verb 'gehen' in present tense",
    "explanation": "First person singular of 'gehen' is 'gehe'",
    "skills": ["verbs"]
  }},
  {{
    "id": "q3",
    "type": "translation",
    "english": "The cat is black",
    "answer": "Die Katze ist schwarz",
    "acceptable_answers": ["Die Katze ist schwarz", "die katze ist schwarz"],
    "explanation": "'Katze' is feminine, uses 'die'",
    "skills": ["vocabulary", "articles"]
  }},
  {{
    "id": "q4",
    "type": "sentence_order",
    "scrambled_words": ["gehe", "Ich", "Schule", "zur"],
    "answer": "Ich gehe zur Schule",
    "explanation": "Subject-Verb-Object word order",
    "skills": ["word_order"]
  }},
  {{
    "id": "q5",
    "type": "listening",
    "audio_text": "Guten Morgen! Wie geht es dir?",
    "question": "What greeting did you hear?",
    "options": ["Good morning", "Good evening", "Good night", "Good afternoon"],
    "answer": "Good morning",
    "explanation": "'Guten Morgen' means 'Good morning'",
    "skills": ["listening", "vocabulary"]
  }},
  {{
    "id": "q6",
    "type": "reading",
    "passage": "Maria wohnt in Berlin. Sie ist Lehrerin. Jeden Tag geht sie zur Schule.",
    "question": "What is Maria's profession?",
    "options": ["Doctor", "Teacher", "Student", "Engineer"],
    "answer": "Teacher",
    "explanation": "'Lehrerin' means teacher (female)",
    "skills": ["reading", "vocabulary"]
  }},
  {{
    "id": "q7",
    "type": "speaking",
    "prompt": "Say: 'Ich lerne Deutsch'",
    "expected_text": "Ich lerne Deutsch",
    "explanation": "This means 'I am learning German'",
    "skills": ["speaking", "pronunciation"]
  }}
]

Rules:
- Mix ALL question types for variety and engagement
- Use real German words and natural sentences
- Level-appropriate vocabulary and grammar
- Clear, unambiguous correct answers
- Helpful explanations
- For listening: provide German text to be converted to speech
- For reading: 2-3 sentence passages with comprehension questions
- For speaking: simple phrases appropriate for the level
- Return ONLY valid JSON array"""

            user_prompt = f"Generate {size} engaging German quiz questions for {level or 'intermediate'} level. Topic: {track or 'mixed grammar'}. Mix different question types for variety."
            
            response = await ollama_client.chat(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8,
                max_tokens=2000
            )
            
            content = response.get('message', {}).get('content', '[]')
            
            # Extract JSON array with robust parsing
            items = []
            try:
                # Method 1: Direct parse
                items = json.loads(content)
            except Exception:
                try:
                    # Method 2: Extract from markdown code blocks
                    if '```json' in content:
                        json_str = content.split('```json')[1].split('```')[0].strip()
                        items = json.loads(json_str)
                    elif '```' in content:
                        json_str = content.split('```')[1].split('```')[0].strip()
                        items = json.loads(json_str)
                    else:
                        # Method 3: Find JSON array boundaries
                        start = content.find('[')
                        end = content.rfind(']')
                        if start != -1 and end != -1 and end > start:
                            json_str = content[start:end+1]
                            # Clean up common issues
                            json_str = json_str.replace('\n', ' ').replace('\r', '')
                            # Remove trailing commas before closing brackets
                            json_str = json_str.replace(',]', ']').replace(', ]', ']')
                            items = json.loads(json_str)
                        else:
                            raise ValueError("No JSON array found in response")
                except Exception as e:
                    import logging
                    logging.getLogger(__name__).error(f"JSON parsing failed: {e}. Content: {content[:200]}")
                    items = []
            
            # Validate and normalize all question types
            out: List[Dict[str, Any]] = []
            for i, q in enumerate(items if isinstance(items, list) else []):
                if not isinstance(q, dict):
                    continue
                    
                qtype = q.get("type")
                qid = str(q.get("id") or f"ai_{track or 'mixed'}_{i}")
                skills = q.get("skills") or ([track] if track else [])
                explanation = q.get("explanation") or ""
                
                # Validate based on question type
                if qtype == "mcq":
                    opts = q.get("options") or []
                    ans = q.get("answer")
                    if isinstance(opts, list) and len(opts) >= 3 and ans:
                        out.append({
                            "id": qid,
                            "type": "mcq",
                            "question": q.get("question") or "",
                            "options": opts,
                            "answer": ans,
                            "explanation": explanation,
                            "skills": skills,
                        })
                        
                elif qtype == "fill_blank":
                    sentence = q.get("sentence")
                    ans = q.get("answer")
                    if sentence and ans:
                        out.append({
                            "id": qid,
                            "type": "fill_blank",
                            "sentence": sentence,
                            "answer": ans,
                            "hint": q.get("hint") or "",
                            "explanation": explanation,
                            "skills": skills,
                        })
                        
                elif qtype == "translation":
                    english = q.get("english")
                    ans = q.get("answer")
                    if english and ans:
                        acceptable = q.get("acceptable_answers") or [ans]
                        out.append({
                            "id": qid,
                            "type": "translation",
                            "english": english,
                            "answer": ans,
                            "acceptable_answers": acceptable,
                            "explanation": explanation,
                            "skills": skills,
                        })
                        
                elif qtype == "sentence_order":
                    words = q.get("scrambled_words")
                    ans = q.get("answer")
                    if isinstance(words, list) and len(words) >= 3 and ans:
                        out.append({
                            "id": qid,
                            "type": "sentence_order",
                            "scrambled_words": words,
                            "answer": ans,
                            "explanation": explanation,
                            "skills": skills,
                        })
                
                elif qtype == "listening":
                    audio_text = q.get("audio_text")
                    question = q.get("question")
                    opts = q.get("options") or []
                    ans = q.get("answer")
                    if audio_text and question and isinstance(opts, list) and len(opts) >= 3 and ans:
                        out.append({
                            "id": qid,
                            "type": "listening",
                            "audio_text": audio_text,
                            "question": question,
                            "options": opts,
                            "answer": ans,
                            "explanation": explanation,
                            "skills": skills,
                        })
                
                elif qtype == "reading":
                    passage = q.get("passage")
                    question = q.get("question")
                    opts = q.get("options") or []
                    ans = q.get("answer")
                    if passage and question and isinstance(opts, list) and len(opts) >= 3 and ans:
                        out.append({
                            "id": qid,
                            "type": "reading",
                            "passage": passage,
                            "question": question,
                            "options": opts,
                            "answer": ans,
                            "explanation": explanation,
                            "skills": skills,
                        })
                
                elif qtype == "speaking":
                    prompt = q.get("prompt")
                    expected = q.get("expected_text")
                    if prompt and expected:
                        out.append({
                            "id": qid,
                            "type": "speaking",
                            "prompt": prompt,
                            "expected_text": expected,
                            "answer": expected,  # Add answer field for validation
                            "explanation": explanation,
                            "skills": skills,
                        })
                
                if len(out) >= size:
                    break
            
            if out:
                return out
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Mistral quiz generation failed: {e}")
    
    # Fallback to OpenAI if configured
    if not settings.OPENAI_API_KEY:
        return []

    try:
        # Lazy import so the package is optional
        try:
            from openai import OpenAI
        except Exception:
            # If SDK is not installed, skip generation gracefully
            return []

        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        system = (
            "You are a German language quiz generator. "
            "Generate multiple-choice questions with exactly one correct answer. "
            "Return only valid JSON in the specified schema."
        )
        user = {
            "instruction": "Generate German quiz questions.",
            "track": track or "mixed",
            "level": level or "A2",
            "size": max(1, int(size)),
            "schema": {
                "id": "string-unique",
                "type": "mcq",
                "question": "text",
                "options": ["A", "B", "C"],
                "answer": "one of options",
                "skills": ["articles" | "pluralization" | "cases" | "nouns" | "prepositions"],
            },
        }
        prompt = f"System:\n{system}\nUser:\n{json.dumps(user)}"

        # Use responses API if available; otherwise fallback to chat.completions
        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": json.dumps(user)},
                ],
                temperature=0.7,
            )
            content = resp.choices[0].message.content or "[]"
        except Exception:
            return []

        # Extract JSON array from content
        try:
            parsed = json.loads(content)
            if isinstance(parsed, dict) and "questions" in parsed:
                items = parsed["questions"]
            elif isinstance(parsed, list):
                items = parsed
            else:
                return []
        except Exception:
            # Try to find JSON block heuristically
            start = content.find("[")
            end = content.rfind("]")
            if start != -1 and end != -1 and end > start:
                try:
                    items = json.loads(content[start : end + 1])
                except Exception:
                    return []
            else:
                return []

        # Validate and normalize
        out: List[Dict[str, Any]] = []
        for i, q in enumerate(items):
            if not isinstance(q, dict):
                continue
            if q.get("type") != "mcq":
                continue
            opts = q.get("options") or []
            ans = q.get("answer")
            if not (isinstance(opts, list) and len(opts) >= 3 and ans in opts):
                continue
            qid = str(q.get("id") or f"ai_{track or 'mixed'}_{i}")
            skills = q.get("skills") or ([track] if track else [])
            out.append({
                "id": qid,
                "type": "mcq",
                "question": q.get("question") or q.get("sentence") or "",
                "options": opts,
                "answer": ans,
                "skills": skills,
            })
            if len(out) >= size:
                break
        return out
    except Exception:
        return []
