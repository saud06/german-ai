from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from ..security import auth_dep
from ..config import settings
from typing import List, Optional
import random
import logging

router = APIRouter(prefix="/paragraph")
logger = logging.getLogger(__name__)

class ParagraphResponse(BaseModel):
    title: str
    sentences: List[str]

# Sample paragraph templates with placeholders
PARAGRAPH_TEMPLATES = [
    {
        "title": "Ein Tag im Park",
        "sentences": [
            "Heute ist das Wetter schön.",
            "Die Sonne scheint hell am Himmel.",
            "Vögel zwitschern in den Bäumen.",
            "Kinder spielen auf dem Spielplatz.",
            "Ein Hund läuft hinter einem Ball her.",
            "Ältere Leute sitzen auf Bänken.",
            "Ein Eiswagen steht am Wegesrand.",
            "Die Blumen blühen in allen Farben.",
            "Ein leichter Wind weht durch die Bäume.",
            "Es ist ein perfekter Tag im Park."
        ]
    },
    {
        "title": "Beim Einkaufen",
        "sentences": [
            "Ich gehe heute Nachmittag einkaufen.",
            "Zuerst brauche ich Brot und Brötchen.",
            "Dann kaufe ich etwas Obst und Gemüse.",
            "Die Äpfel sehen heute besonders frisch aus.",
            "Ich nehme auch Milch und Eier mit.",
            "An der Kasse ist eine lange Schlange.",
            "Die Kassiererin ist sehr freundlich.",
            "Ich bezahle mit meiner Karte.",
            "Draußen regnet es plötzlich.",
            "Zum Glück habe ich einen Regenschirm dabei."
        ]
    },
    {
        "title": "Mein Wochenende",
        "sentences": [
            "Am Wochenende habe ich viel vor.",
            "Freitagabend gehe ich mit Freunden aus.",
            "Wir essen in einem italienischen Restaurant.",
            "Am Samstag mache ich Sport im Park.",
            "Danach besuche ich meine Großeltern.",
            "Am Sonntag schlafe ich lange aus.",
            "Ich frühstücke gemütlich mit der Familie.",
            "Nachmittags lese ich ein interessantes Buch.",
            "Abends schaue ich mir einen Film an.",
            "So ein entspanntes Wochenende tut gut!"
        ]
    }
]

@router.get("/generate", response_model=ParagraphResponse)
async def generate_paragraph(
    topic: Optional[str] = None,
    level: Optional[str] = None,
    _: str = Depends(auth_dep)
):
    """
    Generate a paragraph with multiple sentences on a given topic and level.
    If no topic is provided, a random one is selected.
    """
    try:
        if settings.OPENAI_API_KEY:
            # Use AI to generate a paragraph if API key is available
            try:
                from openai import OpenAI
                client = OpenAI(api_key=settings.OPENAI_API_KEY)
                
                prompt = f"Generate a short paragraph in German with 10 simple sentences about {topic or 'a random everyday topic'}. "
                prompt += f"The language level should be {level or 'A2'} German. "
                prompt += "Return the response as a JSON object with 'title' and 'sentences' (an array of exactly 10 sentences)."
                
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    response_format={ "type": "json_object" }
                )
                
                # Parse the response
                content = response.choices[0].message.content
                if not content:
                    raise ValueError("No content in AI response")
                    
                import json
                result = json.loads(content)
                
                # Validate the response structure
                if not all(key in result for key in ["title", "sentences"]):
                    raise ValueError("Invalid response format from AI")
                    
                # Ensure we have exactly 10 sentences
                sentences = result["sentences"][:10]
                while len(sentences) < 10:
                    sentences.append("")
                
                return {
                    "title": result["title"],
                    "sentences": sentences[:10]
                }
                
            except Exception as e:
                logger.warning(f"AI paragraph generation failed: {e}", exc_info=True)
                # Fall through to template-based generation
        
        # Fallback to template-based generation
        template = random.choice(PARAGRAPH_TEMPLATES)
        return template
        
    except Exception as e:
        logger.error(f"Error generating paragraph: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate paragraph")
