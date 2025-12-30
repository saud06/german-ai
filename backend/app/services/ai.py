from .typing_utils import SentenceResult
from ..config import get_settings
import re

# AI-first; if AI unavailable, use DB-backed rules. If neither applies, raise for router to 503.

def _tokenize_words(s: str) -> list[str]:
    import re as _re
    return [_t for _t in _re.findall(r"[\wäöüÄÖÜß]+", s or "", flags=_re.UNICODE)]

def _align_words(a: str, b: str) -> list[dict]:
    # word-level Levenshtein with ops for UI highlights
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

async def grammar_check(db, sentence: str) -> SentenceResult:
    settings = get_settings()
    
    # Try Ollama (Mistral 7B) first - local, fast, free
    try:
        from ..ollama_client import ollama_client
        import json
        
        if ollama_client.is_available:
            prompt = f"""Analyze this German sentence for grammar errors:

"{sentence}"

Return ONLY valid JSON with NO extra text:
{{
  "is_correct": true,
  "corrected": "corrected German sentence here",
  "explanation": "what was wrong",
  "suggested_variation": "alternative German phrasing",
  "tips": ["one tip"]
}}

Rules:
- Keep ALL text in GERMAN (do not translate to English)
- If sentence is correct: is_correct=true, corrected=same as original, explanation="Perfect! No errors."
- If sentence has errors: is_correct=false, corrected=fixed German sentence, explanation=brief error description
- Check: articles (der/die/das, zum/zur), verb conjugation, case endings, word order
- Return ONLY the JSON object

JSON:"""
            
            response = await ollama_client.chat(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                keep_alive="5m"
            )
            
            content = response.get('message', {}).get('content', '').strip()
            
            # Extract JSON from response - try multiple methods
            data = None
            
            # Method 1: Direct JSON parse
            try:
                data = json.loads(content)
            except:
                pass
            
            # Method 2: Extract from markdown code blocks
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
            
            # Method 3: Find JSON object in text
            if not data:
                try:
                    s = content.find('{')
                    e = content.rfind('}')
                    if s != -1 and e != -1 and e > s:
                        json_str = content[s:e+1]
                        # Clean up common issues
                        json_str = json_str.replace('\n', ' ').replace('\r', '')
                        data = json.loads(json_str)
                except:
                    pass
            
            # Method 4: Try to parse line by line for key-value pairs
            if not data:
                try:
                    # Build JSON from text response
                    data = {
                        "is_correct": "correct" not in content.lower() and "error" not in content.lower() and "wrong" not in content.lower(),
                        "corrected": sentence,
                        "explanation": content[:200] if content else "Could not parse AI response",
                        "suggested_variation": sentence,
                        "tips": ["Review German grammar rules"]
                    }
                except:
                    raise RuntimeError(f"AI did not return valid JSON. Response: {content[:200]}")
            
            is_correct = bool(data.get('is_correct', False))
            corrected = str(data.get('corrected') or sentence).strip()
            
            # Clean explanation - remove any JSON artifacts
            explanation_raw = str(data.get('explanation') or "AI grammar check completed").strip()
            # If explanation contains JSON, it means parsing failed - extract just the text
            if explanation_raw.startswith('{') or '"is_correct"' in explanation_raw:
                # Mistral returned malformed JSON - provide a clean fallback
                if corrected.lower() != sentence.lower():
                    explanation = "Grammar error detected and corrected"
                else:
                    explanation = "Perfect! No errors detected."
            else:
                explanation = explanation_raw
            
            suggested_variation = str(data.get('suggested_variation') or corrected).strip()
            # Clean suggested_variation too
            if suggested_variation.startswith('{') or '"is_correct"' in suggested_variation:
                suggested_variation = corrected
            
            tips = [str(t).strip() for t in (data.get('tips') or []) if isinstance(t, (str, int, float))][:3]
            # Clean tips
            tips = [t for t in tips if not t.startswith('{') and '"is_correct"' not in t]
            
            # If corrected differs from original, it's not correct
            if corrected.lower().strip() != sentence.lower().strip():
                is_correct = False
            
            highlights = _align_words(sentence, corrected)
            result_source = "ok" if is_correct else "ai_mistral"
            
            return SentenceResult(
                original=sentence,
                corrected=corrected,
                explanation=explanation,
                suggested_variation=suggested_variation,
                source=result_source,
                highlights=highlights,
                tips=tips or None,
                rule_source="mistral_7b",
            )
    except Exception as e:
        # Log but continue to fallback
        import logging
        logging.getLogger(__name__).warning(f"Ollama grammar check failed: {e}")
    
    # Fallback to OpenAI if configured
    if settings.OPENAI_API_KEY:
        try:
            try:
                from openai import OpenAI
            except Exception:
                raise RuntimeError("openai package not installed in backend env")
            client = OpenAI(api_key=settings.OPENAI_API_KEY)

            system = (
                "You are a German grammar checker. Return strict JSON only with keys: "
                "corrected (string), explanation (string), suggested_variation (string), "
                "tips (array of strings), highlights (array of {op:'ok'|'sub'|'del'|'ins', before?:string, after?:string})."
            )
            user = {
                "instruction": "Fix grammar and explain briefly.",
                "language": "German",
                "sentence": sentence,
                "schema": {
                    "corrected": "string",
                    "explanation": "string",
                    "suggested_variation": "string",
                    "tips": ["string"],
                    "highlights": [{"op": "ok|sub|del|ins", "before": "string?", "after": "string?"}],
                },
            }
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": __import__('json').dumps(user)},
                ],
                temperature=0.2,
            )
            content = resp.choices[0].message.content or "{}"
            import json
            try:
                data = json.loads(content)
            except Exception:
                # try bracket extraction
                s = content.find('{'); e = content.rfind('}')
                if s != -1 and e != -1 and e > s:
                    data = json.loads(content[s:e+1])
                else:
                    raise RuntimeError("AI did not return valid JSON")

            corrected = str(data.get('corrected') or sentence)
            explanation = str(data.get('explanation') or "AI grammar suggestions")
            suggested_variation = str(data.get('suggested_variation') or corrected)
            tips = [str(t) for t in (data.get('tips') or []) if isinstance(t, (str, int, float))][:5]
            highlights = data.get('highlights')
            if not isinstance(highlights, list) or not highlights:
                highlights = _align_words(sentence, corrected)

            return SentenceResult(
                original=sentence,
                corrected=corrected,
                explanation=explanation,
                suggested_variation=suggested_variation,
                source="ai",
                highlights=highlights,
                tips=tips or None,
                rule_source="ai",
            )
        except Exception:
            # On AI failure, fall through to DB rules
            pass

    # DB-backed rules: scan rules and apply the first highest-priority match
    # Supported schemas (backward-compatible):
    #  - { pattern, replacement, explanation?, suggestion?, ci?, word_boundary?, priority? }
    #  - { regex, flags?, replacement, explanation?, suggestion?, priority? }
    rules = db["grammar_rules"]
    all_rules = []
    async for rr in (
        rules
        .find({"$or": [{"pattern": {"$exists": True}}, {"regex": {"$exists": True}}]}, {
            "_id": 1, "pattern": 1, "replacement": 1, "explanation": 1, "suggestion": 1, "regex": 1, "flags": 1,
            "priority": 1, "ci": 1, "word_boundary": 1,
        })
        .sort([("priority", -1)])
        .limit(1000)
    ):
        all_rules.append(rr)

    current = sentence
    explanations: list[str] = []
    tips_acc: list[str] = []
    last_suggestion: str | None = None
    applied: list[str] = []

    def apply_one(text: str) -> tuple[str, bool, dict | None]:
        # returns (new_text, changed, rule)
        for rule in all_rules:
            if str(rule.get("_id")) in applied:
                continue
            replacement = rule.get("replacement", "")
            explanation = rule.get("explanation", "Applied DB grammar rule.")
            suggestion = rule.get("suggestion")
            rx = rule.get("regex")
            if isinstance(rx, str) and rx:
                flags_str = (rule.get("flags") or "") if isinstance(rule.get("flags"), str) else ""
                flags = 0
                if "i" in flags_str: flags |= re.IGNORECASE
                if "m" in flags_str: flags |= re.MULTILINE
                if "s" in flags_str: flags |= re.DOTALL
                try:
                    pattern = re.compile(rx, flags)
                    if pattern.search(text):
                        new_text = pattern.sub(replacement or rx, text, count=1)
                        return new_text, new_text != text, {"rule": rule, "explanation": explanation, "suggestion": suggestion, "source": "db.regex"}
                except re.error:
                    continue
            pat = rule.get("pattern")
            if isinstance(pat, str) and pat:
                if bool(rule.get("ci")):
                    idx = text.lower().find(pat.lower())
                    if idx != -1:
                        new_text = text[:idx] + (replacement or pat) + text[idx+len(pat):]
                        return new_text, True, {"rule": rule, "explanation": explanation, "suggestion": suggestion, "source": "db.literal.ci"}
                elif bool(rule.get("word_boundary")):
                    try:
                        wb_rx = re.compile(rf"\\b{re.escape(pat)}\\b")
                        if wb_rx.search(text):
                            new_text = wb_rx.sub(replacement or pat, text, count=1)
                            return new_text, True, {"rule": rule, "explanation": explanation, "suggestion": suggestion, "source": "db.literal.wb"}
                    except re.error:
                        pass
                else:
                    if pat in text:
                        new_text = text.replace(pat, replacement or pat, 1)
                        return new_text, True, {"rule": rule, "explanation": explanation, "suggestion": suggestion, "source": "db.literal"}
        return text, False, None

    MAX_STEPS = 3
    for _ in range(MAX_STEPS):
        new_text, changed, meta = apply_one(current)
        if not changed or not meta:
            break
        current = new_text
        r = meta["rule"]
        applied.append(str(r.get("_id")))
        explanations.append(str(meta.get("explanation") or "Applied DB rule"))
        if meta.get("suggestion"):
            last_suggestion = meta["suggestion"]
        tips_acc.append("Review basic conjugation and article agreement.")

    if current != sentence:
        highlights = _align_words(sentence, current)
        explanation_full = " • ".join(explanations) if explanations else "Applied DB grammar corrections."
        return SentenceResult(
            original=sentence,
            corrected=current,
            explanation=explanation_full,
            suggested_variation=last_suggestion or current,
            source="db",
            highlights=highlights,
            tips=tips_acc or None,
            rule_id=",".join(applied) if applied else None,
            rule_source="db.multi",
        )

    # No AI and no applicable DB rule
    raise ValueError("No grammar service available")
