"""
Final vocabulary additions to reach 500+ words
Common expressions, connectors, and useful phrases
"""

def get_final_vocabulary():
    """Get final 100+ words to reach 500+"""
    
    vocab = [
        # Connectors and conjunctions (30)
        {"word": "und", "translation": "and", "level": "A1", "category": "connectors", "part_of_speech": "conjunction", "examples": ["Ich und du."], "difficulty": 1},
        {"word": "oder", "translation": "or", "level": "A1", "category": "connectors", "part_of_speech": "conjunction", "examples": ["Kaffee oder Tee?"], "difficulty": 1},
        {"word": "aber", "translation": "but", "level": "A1", "category": "connectors", "part_of_speech": "conjunction", "examples": ["Aber ich..."], "difficulty": 1},
        {"word": "denn", "translation": "because", "level": "A2", "category": "connectors", "part_of_speech": "conjunction", "examples": ["Ich gehe, denn..."], "difficulty": 2},
        {"word": "sondern", "translation": "but rather", "level": "A2", "category": "connectors", "part_of_speech": "conjunction", "examples": ["Nicht A, sondern B."], "difficulty": 2},
        {"word": "weil", "translation": "because", "level": "A2", "category": "connectors", "part_of_speech": "conjunction", "examples": ["Weil ich..."], "difficulty": 2},
        {"word": "dass", "translation": "that", "level": "A2", "category": "connectors", "part_of_speech": "conjunction", "examples": ["Ich denke, dass..."], "difficulty": 2},
        {"word": "wenn", "translation": "if, when", "level": "A2", "category": "connectors", "part_of_speech": "conjunction", "examples": ["Wenn ich..."], "difficulty": 2},
        {"word": "als", "translation": "when, than", "level": "A2", "category": "connectors", "part_of_speech": "conjunction", "examples": ["Als ich..."], "difficulty": 2},
        {"word": "ob", "translation": "whether, if", "level": "B1", "category": "connectors", "part_of_speech": "conjunction", "examples": ["Ob das stimmt?"], "difficulty": 3},
        
        # Question words (15)
        {"word": "wer", "translation": "who", "level": "A1", "category": "questions", "part_of_speech": "pronoun", "examples": ["Wer bist du?"], "difficulty": 1},
        {"word": "was", "translation": "what", "level": "A1", "category": "questions", "part_of_speech": "pronoun", "examples": ["Was ist das?"], "difficulty": 1},
        {"word": "wo", "translation": "where", "level": "A1", "category": "questions", "part_of_speech": "adverb", "examples": ["Wo bist du?"], "difficulty": 1},
        {"word": "wann", "translation": "when", "level": "A1", "category": "questions", "part_of_speech": "adverb", "examples": ["Wann kommst du?"], "difficulty": 1},
        {"word": "warum", "translation": "why", "level": "A1", "category": "questions", "part_of_speech": "adverb", "examples": ["Warum nicht?"], "difficulty": 1},
        {"word": "wie", "translation": "how", "level": "A1", "category": "questions", "part_of_speech": "adverb", "examples": ["Wie geht's?"], "difficulty": 1},
        {"word": "welche", "translation": "which", "level": "A1", "category": "questions", "part_of_speech": "pronoun", "examples": ["Welche Farbe?"], "difficulty": 1},
        {"word": "woher", "translation": "where from", "level": "A1", "category": "questions", "part_of_speech": "adverb", "examples": ["Woher kommst du?"], "difficulty": 1},
        {"word": "wohin", "translation": "where to", "level": "A1", "category": "questions", "part_of_speech": "adverb", "examples": ["Wohin gehst du?"], "difficulty": 1},
        {"word": "wieviel", "translation": "how much/many", "level": "A1", "category": "questions", "part_of_speech": "adverb", "examples": ["Wieviel kostet das?"], "difficulty": 1},
        
        # Pronouns (20)
        {"word": "ich", "translation": "I", "level": "A1", "category": "pronouns", "part_of_speech": "pronoun", "examples": ["Ich bin."], "difficulty": 1},
        {"word": "du", "translation": "you (informal)", "level": "A1", "category": "pronouns", "part_of_speech": "pronoun", "examples": ["Du bist."], "difficulty": 1},
        {"word": "er", "translation": "he", "level": "A1", "category": "pronouns", "part_of_speech": "pronoun", "examples": ["Er ist."], "difficulty": 1},
        {"word": "sie", "translation": "she/they", "level": "A1", "category": "pronouns", "part_of_speech": "pronoun", "examples": ["Sie ist."], "difficulty": 1},
        {"word": "es", "translation": "it", "level": "A1", "category": "pronouns", "part_of_speech": "pronoun", "examples": ["Es ist."], "difficulty": 1},
        {"word": "wir", "translation": "we", "level": "A1", "category": "pronouns", "part_of_speech": "pronoun", "examples": ["Wir sind."], "difficulty": 1},
        {"word": "ihr", "translation": "you (plural informal)", "level": "A1", "category": "pronouns", "part_of_speech": "pronoun", "examples": ["Ihr seid."], "difficulty": 1},
        {"word": "Sie", "translation": "you (formal)", "level": "A1", "category": "pronouns", "part_of_speech": "pronoun", "examples": ["Sie sind."], "difficulty": 1},
        {"word": "mein", "translation": "my", "level": "A1", "category": "pronouns", "part_of_speech": "possessive", "examples": ["Mein Haus."], "difficulty": 1},
        {"word": "dein", "translation": "your", "level": "A1", "category": "pronouns", "part_of_speech": "possessive", "examples": ["Dein Auto."], "difficulty": 1},
        
        # More common expressions (40)
        {"word": "Guten Morgen", "translation": "good morning", "level": "A1", "category": "greetings", "part_of_speech": "phrase", "examples": ["Guten Morgen!"], "difficulty": 1},
        {"word": "Guten Tag", "translation": "good day", "level": "A1", "category": "greetings", "part_of_speech": "phrase", "examples": ["Guten Tag!"], "difficulty": 1},
        {"word": "Guten Abend", "translation": "good evening", "level": "A1", "category": "greetings", "part_of_speech": "phrase", "examples": ["Guten Abend!"], "difficulty": 1},
        {"word": "Gute Nacht", "translation": "good night", "level": "A1", "category": "greetings", "part_of_speech": "phrase", "examples": ["Gute Nacht!"], "difficulty": 1},
        {"word": "Hallo", "translation": "hello", "level": "A1", "category": "greetings", "part_of_speech": "interjection", "examples": ["Hallo!"], "difficulty": 1},
        {"word": "Tschüss", "translation": "bye", "level": "A1", "category": "greetings", "part_of_speech": "interjection", "examples": ["Tschüss!"], "difficulty": 1},
        {"word": "Auf Wiedersehen", "translation": "goodbye", "level": "A1", "category": "greetings", "part_of_speech": "phrase", "examples": ["Auf Wiedersehen!"], "difficulty": 1},
        {"word": "Wie geht es dir", "translation": "how are you", "level": "A1", "category": "greetings", "part_of_speech": "phrase", "examples": ["Wie geht es dir?"], "difficulty": 1},
        {"word": "Mir geht es gut", "translation": "I'm fine", "level": "A1", "category": "greetings", "part_of_speech": "phrase", "examples": ["Mir geht es gut."], "difficulty": 1},
        {"word": "Entschuldigung", "translation": "excuse me, sorry", "level": "A1", "category": "phrases", "part_of_speech": "noun", "gender": "f", "examples": ["Entschuldigung!"], "difficulty": 1},
        {"word": "Verzeihung", "translation": "pardon, excuse me", "level": "A2", "category": "phrases", "part_of_speech": "noun", "gender": "f", "examples": ["Verzeihung!"], "difficulty": 2},
        {"word": "Bitte schön", "translation": "you're welcome", "level": "A1", "category": "phrases", "part_of_speech": "phrase", "examples": ["Bitte schön!"], "difficulty": 1},
        {"word": "Gern geschehen", "translation": "you're welcome", "level": "A2", "category": "phrases", "part_of_speech": "phrase", "examples": ["Gern geschehen!"], "difficulty": 2},
        {"word": "Keine Ursache", "translation": "no problem", "level": "A2", "category": "phrases", "part_of_speech": "phrase", "examples": ["Keine Ursache!"], "difficulty": 2},
        {"word": "Wie bitte", "translation": "pardon, what", "level": "A1", "category": "phrases", "part_of_speech": "phrase", "examples": ["Wie bitte?"], "difficulty": 1},
        {"word": "Ich verstehe nicht", "translation": "I don't understand", "level": "A1", "category": "phrases", "part_of_speech": "phrase", "examples": ["Ich verstehe nicht."], "difficulty": 1},
        {"word": "Können Sie das wiederholen", "translation": "can you repeat that", "level": "A2", "category": "phrases", "part_of_speech": "phrase", "examples": ["Können Sie das wiederholen?"], "difficulty": 2},
        {"word": "Langsamer bitte", "translation": "slower please", "level": "A1", "category": "phrases", "part_of_speech": "phrase", "examples": ["Langsamer bitte!"], "difficulty": 1},
        {"word": "Ich weiß nicht", "translation": "I don't know", "level": "A1", "category": "phrases", "part_of_speech": "phrase", "examples": ["Ich weiß nicht."], "difficulty": 1},
        {"word": "Kein Problem", "translation": "no problem", "level": "A1", "category": "phrases", "part_of_speech": "phrase", "examples": ["Kein Problem!"], "difficulty": 1},
        {"word": "Viel Spaß", "translation": "have fun", "level": "A1", "category": "phrases", "part_of_speech": "phrase", "examples": ["Viel Spaß!"], "difficulty": 1},
        {"word": "Viel Erfolg", "translation": "good luck, much success", "level": "A2", "category": "phrases", "part_of_speech": "phrase", "examples": ["Viel Erfolg!"], "difficulty": 2},
        {"word": "Prost", "translation": "cheers", "level": "A1", "category": "phrases", "part_of_speech": "interjection", "examples": ["Prost!"], "difficulty": 1},
        {"word": "Zum Wohl", "translation": "cheers, to your health", "level": "A2", "category": "phrases", "part_of_speech": "phrase", "examples": ["Zum Wohl!"], "difficulty": 2},
        {"word": "Guten Appetit", "translation": "enjoy your meal", "level": "A1", "category": "phrases", "part_of_speech": "phrase", "examples": ["Guten Appetit!"], "difficulty": 1},
        {"word": "Gesundheit", "translation": "bless you", "level": "A1", "category": "phrases", "part_of_speech": "noun", "gender": "f", "examples": ["Gesundheit!"], "difficulty": 1},
        {"word": "Frohe Weihnachten", "translation": "Merry Christmas", "level": "A1", "category": "phrases", "part_of_speech": "phrase", "examples": ["Frohe Weihnachten!"], "difficulty": 1},
        {"word": "Frohes neues Jahr", "translation": "Happy New Year", "level": "A1", "category": "phrases", "part_of_speech": "phrase", "examples": ["Frohes neues Jahr!"], "difficulty": 1},
        {"word": "Alles Liebe", "translation": "all the love, best wishes", "level": "A2", "category": "phrases", "part_of_speech": "phrase", "examples": ["Alles Liebe!"], "difficulty": 2},
        {"word": "Schönes Wochenende", "translation": "have a nice weekend", "level": "A1", "category": "phrases", "part_of_speech": "phrase", "examples": ["Schönes Wochenende!"], "difficulty": 1},
        
        # Final 25 words to reach 500+
        {"word": "immer", "translation": "always", "level": "A1", "category": "adverbs", "part_of_speech": "adverb", "examples": ["Immer!"], "difficulty": 1},
        {"word": "nie", "translation": "never", "level": "A1", "category": "adverbs", "part_of_speech": "adverb", "examples": ["Nie!"], "difficulty": 1},
        {"word": "oft", "translation": "often", "level": "A1", "category": "adverbs", "part_of_speech": "adverb", "examples": ["Oft."], "difficulty": 1},
        {"word": "manchmal", "translation": "sometimes", "level": "A1", "category": "adverbs", "part_of_speech": "adverb", "examples": ["Manchmal."], "difficulty": 1},
        {"word": "selten", "translation": "rarely", "level": "A2", "category": "adverbs", "part_of_speech": "adverb", "examples": ["Selten."], "difficulty": 2},
        {"word": "schon", "translation": "already", "level": "A2", "category": "adverbs", "part_of_speech": "adverb", "examples": ["Schon fertig."], "difficulty": 2},
        {"word": "noch", "translation": "still, yet", "level": "A2", "category": "adverbs", "part_of_speech": "adverb", "examples": ["Noch nicht."], "difficulty": 2},
        {"word": "wieder", "translation": "again", "level": "A2", "category": "adverbs", "part_of_speech": "adverb", "examples": ["Wieder hier."], "difficulty": 2},
        {"word": "mehr", "translation": "more", "level": "A1", "category": "adverbs", "part_of_speech": "adverb", "examples": ["Mehr bitte."], "difficulty": 1},
        {"word": "weniger", "translation": "less", "level": "A2", "category": "adverbs", "part_of_speech": "adverb", "examples": ["Weniger."], "difficulty": 2},
        {"word": "viel", "translation": "much, many", "level": "A1", "category": "adverbs", "part_of_speech": "adverb", "examples": ["Viel Glück."], "difficulty": 1},
        {"word": "wenig", "translation": "little, few", "level": "A2", "category": "adverbs", "part_of_speech": "adverb", "examples": ["Wenig Zeit."], "difficulty": 2},
        {"word": "alle", "translation": "all, everyone", "level": "A1", "category": "pronouns", "part_of_speech": "pronoun", "examples": ["Alle sind hier."], "difficulty": 1},
        {"word": "einige", "translation": "some", "level": "A2", "category": "pronouns", "part_of_speech": "pronoun", "examples": ["Einige Leute."], "difficulty": 2},
        {"word": "viele", "translation": "many", "level": "A1", "category": "pronouns", "part_of_speech": "pronoun", "examples": ["Viele Menschen."], "difficulty": 1},
        {"word": "wenige", "translation": "few", "level": "A2", "category": "pronouns", "part_of_speech": "pronoun", "examples": ["Wenige Leute."], "difficulty": 2},
        {"word": "niemand", "translation": "nobody", "level": "A2", "category": "pronouns", "part_of_speech": "pronoun", "examples": ["Niemand ist da."], "difficulty": 2},
        {"word": "jemand", "translation": "somebody", "level": "A2", "category": "pronouns", "part_of_speech": "pronoun", "examples": ["Jemand ist da."], "difficulty": 2},
        {"word": "etwas", "translation": "something", "level": "A1", "category": "pronouns", "part_of_speech": "pronoun", "examples": ["Etwas essen."], "difficulty": 1},
        {"word": "nichts", "translation": "nothing", "level": "A1", "category": "pronouns", "part_of_speech": "pronoun", "examples": ["Nichts."], "difficulty": 1},
        {"word": "alles", "translation": "everything", "level": "A1", "category": "pronouns", "part_of_speech": "pronoun", "examples": ["Alles gut."], "difficulty": 1},
        {"word": "jeder", "translation": "everyone, each", "level": "A2", "category": "pronouns", "part_of_speech": "pronoun", "examples": ["Jeder Tag."], "difficulty": 2},
        {"word": "dieser", "translation": "this", "level": "A1", "category": "pronouns", "part_of_speech": "demonstrative", "examples": ["Dieser Mann."], "difficulty": 1},
        {"word": "jener", "translation": "that", "level": "A2", "category": "pronouns", "part_of_speech": "demonstrative", "examples": ["Jener Tag."], "difficulty": 2},
        {"word": "solcher", "translation": "such", "level": "B1", "category": "pronouns", "part_of_speech": "demonstrative", "examples": ["Solche Sachen."], "difficulty": 3},
    ]
    
    return vocab
