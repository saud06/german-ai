"""
Grammar checking using Gemma 2 model
Clean implementation without rule-based dependencies
"""
import ollama
import json
from typing import Optional
from .typing_utils import SentenceResult
from ..config import get_settings

def _tokenize_words(s: str) -> list[str]:
    import re as _re
    return [_t for _t in _re.findall(r"[\wäöüÄÖÜß]+", s or "", flags=_re.UNICODE)]

def _align_words(a: str, b: str) -> list[dict]:
    """Word-level Levenshtein with ops for UI highlights"""
    A = _tokenize_words(a.lower())
    B = _tokenize_words(b.lower())
    m, n = len(A), len(B)
    dp = [[0]*(n+1) for _ in range(m+1)]
    for i in range(m+1): dp[i][0] = i
    for j in range(n+1): dp[0][j] = j
    for i in range(1,m+1):
        for j in range(1,n+1):
            cost = 0 if A[i-1]==B[j-1] else 1
            dp[i][j] = min(dp[i-1][j]+1, dp[i][j-1]+1, dp[i-1][j-1]+cost)
    i,j=m,n
    out=[]
    while i>0 or j>0:
        if i>0 and j>0 and dp[i][j]==dp[i-1][j-1]+(0 if A[i-1]==B[j-1] else 1):
            op = 'ok' if A[i-1]==B[j-1] else 'sub'
            out.append({'op': op, 'before': A[i-1], 'after': B[j-1]})
            i-=1; j-=1
        elif i>0 and dp[i][j]==dp[i-1][j]+1:
            out.append({'op':'del','before':A[i-1]})
            i-=1
        else:
            out.append({'op':'ins','after':B[j-1]})
            j-=1
    out.reverse()
    return out

async def check_grammar_with_gemma(sentence: str) -> SentenceResult:
    """
    Check German grammar using Gemma 2 model
    Returns SentenceResult with corrections and explanations
    """
    settings = get_settings()
    
    print(f"[GEMMA GRAMMAR] Checking: '{sentence}'")
    
    try:
        # Use Gemma 2 for German grammar checking
        client = ollama.AsyncClient(host=settings.OLLAMA_HOST)
        model = settings.OLLAMA_MODEL_GRAMMAR
        
        print(f"[GEMMA GRAMMAR] Host: {settings.OLLAMA_HOST}, Model: {model}")
        
        # Test connection and list models
        try:
            models_list = await client.list()
            available_models = [m['name'] for m in models_list.get('models', [])]
            print(f"[GEMMA GRAMMAR] Available models: {available_models}")
        except Exception as e:
            print(f"[GEMMA GRAMMAR] Failed to list models: {e}")
        
        prompt = f"""Analyze this German sentence for grammar errors:

"{sentence}"

Check for:
1. Subject-verb agreement (singular/plural)
2. Article gender (der/die/das)
3. Case endings (Nominativ/Akkusativ/Dativ/Genitiv)
4. Verb conjugation
5. Adjective endings

Return ONLY valid JSON:
{{
  "is_correct": false,
  "corrected": "corrected German sentence",
  "explanation": "what was wrong",
  "suggested_variation": "alternative phrasing",
  "tips": ["grammar tip"]
}}

CRITICAL:
- DO NOT translate to English - keep all text in GERMAN
- If perfect: is_correct=true, corrected=same as original
- If errors: is_correct=false, corrected=fixed German sentence
- Preserve capitalization exactly
- Return corrected GERMAN sentence, not English translation

JSON:"""
        
        response = await client.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.0}
        )
        
        content = response.get('message', {}).get('content', '').strip()
        print(f"[GEMMA GRAMMAR] Response: {content[:200]}")
        
        # Parse JSON response
        data = None
        
        # Try direct JSON parse
        try:
            data = json.loads(content)
        except:
            pass
        
        # Try extracting from markdown code blocks
        if not data:
            try:
                if '```json' in content:
                    json_str = content.split('```json')[1].split('```')[0].strip()
                    data = json.loads(json_str)
                elif '```' in content:
                    json_str = content.split('```')[1].split('```')[0].strip()
                    data = json.loads(json_str)
            except:
                pass
        
        # Try finding JSON object in text
        if not data:
            try:
                s = content.find('{')
                e = content.rfind('}')
                if s != -1 and e != -1 and e > s:
                    json_str = content[s:e+1]
                    json_str = json_str.replace('\n', ' ').replace('\r', '')
                    data = json.loads(json_str)
            except:
                pass
        
        if not data:
            raise RuntimeError(f"Could not parse Gemma response: {content[:200]}")
        
        # Extract and validate data
        is_correct = bool(data.get('is_correct', False))
        corrected = str(data.get('corrected') or sentence).strip()
        explanation = str(data.get('explanation') or "Grammar check completed").strip()
        suggested_variation = str(data.get('suggested_variation') or corrected).strip()
        tips = [str(t).strip() for t in (data.get('tips') or []) if isinstance(t, (str, int, float))][:3]
        
        # Validate: if corrected differs from original, mark as incorrect
        if corrected.lower().strip() != sentence.lower().strip():
            is_correct = False
        
        # Validate: if AI says correct but made changes, override
        if is_correct and corrected != sentence:
            is_correct = False
        
        highlights = _align_words(sentence, corrected)
        result_source = "ok" if is_correct else "ai_gemma2"
        
        print(f"[GEMMA GRAMMAR] Result: is_correct={is_correct}, corrected='{corrected}'")
        
        return SentenceResult(
            original=sentence,
            corrected=corrected,
            explanation=explanation,
            suggested_variation=suggested_variation,
            source=result_source,
            highlights=highlights,
            tips=tips or None,
            rule_source="gemma2_9b",
        )
        
    except Exception as e:
        print(f"[GEMMA GRAMMAR] Error: {e}")
        # Return original sentence if grammar check fails
        return SentenceResult(
            original=sentence,
            corrected=sentence,
            explanation=f"Grammar check unavailable: {str(e)}",
            suggested_variation=sentence,
            source="error",
            highlights=[],
            tips=None,
            rule_source="error",
        )
