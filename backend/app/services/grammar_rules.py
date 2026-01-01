"""
Simple rule-based German grammar checker
Catches common errors that AI struggles with
"""
import re
from typing import Optional, Tuple

def check_subject_verb_agreement(sentence: str) -> Optional[Tuple[str, str]]:
    """
    Check for subject-verb agreement errors
    Returns (corrected_sentence, explanation) or None
    """
    # Pattern: singular noun + plural verb
    patterns = [
        # "Das sind [singular noun]" -> should be "Das ist"
        (r'\bDas\s+sind\s+(meine?|deine?|seine?|ihre?|unsere?|eure?)\s+(\w+)\b',
         r'Das ist \1 \2',
         "Changed 'sind' to 'ist' (singular subject 'Das' requires singular verb)"),
        
        # "Der/Die/Das [noun] sind" -> should be "ist"
        (r'\b(Der|Die|Das)\s+(\w+)\s+sind\b', r'\1 \2 ist', 
         "Changed 'sind' to 'ist' (singular subject requires singular verb)"),
        
        # "Was sind der/die/das" -> should be "Was ist"
        (r'\bWas\s+sind\s+(der|die|das)\b', r'Was ist \1',
         "Changed 'sind' to 'ist' (singular question requires singular verb)"),
        
        # "Die [singular noun] sind" -> should be "ist"
        (r'\bDie\s+(Entwicklung|Meinung|Verantwortung|Gelegenheit|Entscheidung)\s+sind\b',
         r'Die \1 ist',
         "Changed 'sind' to 'ist' (singular noun requires singular verb)"),
    ]
    
    for pattern, replacement, explanation in patterns:
        if re.search(pattern, sentence, re.IGNORECASE):
            corrected = re.sub(pattern, replacement, sentence, flags=re.IGNORECASE)
            # Preserve original capitalization of first word
            if sentence[0].isupper() and corrected[0].islower():
                corrected = corrected[0].upper() + corrected[1:]
            return (corrected, explanation)
    
    return None

def check_case_errors(sentence: str) -> Optional[Tuple[str, str]]:
    """
    Check for case errors (Nominativ/Akkusativ/Dativ/Genitiv)
    Returns (corrected_sentence, explanation) or None
    """
    patterns = [
        # "Unter welche/welches/welcher" -> should be "Unter welchen" (dative after unter)
        (r'\bUnter\s+(welche|welches|welcher)\b', r'Unter welchen',
         "Changed to 'welchen' (dative case after 'unter')"),
        
        # "Das ist meinen/meiner" -> should be "meine" (nominative)
        (r'\bist\s+(meinen|meiner)\s+(\w+)\b', r'ist meine \2',
         "Changed to 'meine' (nominative case after 'ist')"),
        
        # "Das ist einen" -> should be "eine/ein" (nominative)
        (r'\bist\s+einen\s+(\w+)\b', r'ist ein \1',
         "Changed 'einen' to 'ein' (nominative case after 'ist')"),
    ]
    
    for pattern, replacement, explanation in patterns:
        if re.search(pattern, sentence, re.IGNORECASE):
            corrected = re.sub(pattern, replacement, sentence, flags=re.IGNORECASE)
            # Preserve capitalization
            if sentence[0].isupper() and corrected[0].islower():
                corrected = corrected[0].upper() + corrected[1:]
            return (corrected, explanation)
    
    return None

def check_verb_conjugation(sentence: str) -> Optional[Tuple[str, str]]:
    """
    Check for verb conjugation errors
    Returns (corrected_sentence, explanation) or None
    """
    patterns = [
        # "Ich haben" -> should be "Ich habe"
        (r'\bIch\s+haben\b', r'Ich habe',
         "Changed 'haben' to 'habe' (first person singular conjugation)"),
        
        # "Ich machen" -> should be "Ich mache"
        (r'\bIch\s+machen\b', r'Ich mache',
         "Changed 'machen' to 'mache' (first person singular conjugation)"),
        
        # "Er/Sie/Es machen" -> should be "macht"
        (r'\b(Er|Sie|Es)\s+machen\b', r'\1 macht',
         "Changed 'machen' to 'macht' (third person singular conjugation)"),
        
        # "Er/Sie/Es haben" -> should be "hat"
        (r'\b(Er|Sie|Es)\s+haben\b', r'\1 hat',
         "Changed 'haben' to 'hat' (third person singular conjugation)"),
    ]
    
    for pattern, replacement, explanation in patterns:
        if re.search(pattern, sentence, re.IGNORECASE):
            corrected = re.sub(pattern, replacement, sentence, flags=re.IGNORECASE)
            return (corrected, explanation)
    
    return None

def check_grammar_rules(sentence: str) -> Optional[Tuple[str, str]]:
    """
    Check sentence against all grammar rules
    Returns (corrected_sentence, explanation) or None if no errors found
    """
    # Try each rule checker
    checkers = [
        check_subject_verb_agreement,
        check_case_errors,
        check_verb_conjugation,
    ]
    
    for checker in checkers:
        result = checker(sentence)
        if result:
            return result
    
    return None
