from pydantic import BaseModel
from typing import List, Optional

class SentenceResult(BaseModel):
    original: str
    corrected: str
    explanation: str
    suggested_variation: str
    source: str  # "ai" | "db" | "ok"
    # Optional rich fields for enhanced Grammar Coach UI
    highlights: Optional[List[dict]] = None  # [{ op: 'ok'|'sub'|'del'|'ins', before?: str, after?: str }]
    tips: Optional[List[str]] = None
    rule_id: Optional[str] = None
    rule_source: Optional[str] = None
    examples: Optional[List[str]] = None
