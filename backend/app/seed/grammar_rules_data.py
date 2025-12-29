"""
German Grammar Rules Data
Comprehensive grammar rules for A1-B2 levels
"""

from app.models.grammar_rule import GrammarRule, GrammarExample, GrammarExercise


def get_grammar_rules():
    """Get comprehensive German grammar rules"""
    
    rules = []
    
    # ============================================================================
    # ARTICLES & CASES
    # ============================================================================
    
    # Rule 1: Definite Articles (der, die, das)
    rules.append(GrammarRule(
        title="Definite Articles (der, die, das)",
        title_de="Bestimmte Artikel",
        category="articles",
        level="A1",
        difficulty=1,
        description="German has three genders: masculine (der), feminine (die), and neuter (das). The gender must be learned with each noun.",
        description_de="Deutsch hat drei Geschlechter: maskulin (der), feminin (die) und neutral (das).",
        usage=[
            "Use 'der' for masculine nouns",
            "Use 'die' for feminine nouns and all plurals",
            "Use 'das' for neuter nouns"
        ],
        examples=[
            GrammarExample(german="der Mann", english="the man", highlight="der"),
            GrammarExample(german="die Frau", english="the woman", highlight="die"),
            GrammarExample(german="das Kind", english="the child", highlight="das"),
            GrammarExample(german="die Kinder", english="the children", highlight="die")
        ],
        common_mistakes=[
            {"wrong": "das Frau", "correct": "die Frau", "explanation": "Frau is feminine"},
            {"wrong": "der Kind", "correct": "das Kind", "explanation": "Kind is neuter"}
        ],
        exercises=[
            GrammarExercise(
                type="multiple_choice",
                question="___ Haus ist groß. (The house is big)",
                options=["der", "die", "das"],
                correct_answer="das",
                explanation="Haus is neuter, so we use 'das'",
                difficulty=1
            ),
            GrammarExercise(
                type="multiple_choice",
                question="___ Auto fährt schnell. (The car drives fast)",
                options=["der", "die", "das"],
                correct_answer="das",
                explanation="Auto is neuter",
                difficulty=1
            )
        ],
        tags=["articles", "gender", "beginner", "A1"]
    ))
    
    # Rule 2: Indefinite Articles (ein, eine)
    rules.append(GrammarRule(
        title="Indefinite Articles (ein, eine)",
        title_de="Unbestimmte Artikel",
        category="articles",
        level="A1",
        difficulty=1,
        description="Indefinite articles mean 'a' or 'an'. Use 'ein' for masculine and neuter, 'eine' for feminine.",
        description_de="Unbestimmte Artikel bedeuten 'ein' oder 'eine'.",
        usage=[
            "Use 'ein' for masculine nouns",
            "Use 'eine' for feminine nouns",
            "Use 'ein' for neuter nouns",
            "No plural form (just use the noun without article)"
        ],
        examples=[
            GrammarExample(german="ein Mann", english="a man", highlight="ein"),
            GrammarExample(german="eine Frau", english="a woman", highlight="eine"),
            GrammarExample(german="ein Kind", english="a child", highlight="ein"),
            GrammarExample(german="Kinder", english="children", explanation="No article in plural")
        ],
        common_mistakes=[
            {"wrong": "ein Frau", "correct": "eine Frau", "explanation": "Frau is feminine, use 'eine'"},
            {"wrong": "eine Mann", "correct": "ein Mann", "explanation": "Mann is masculine, use 'ein'"}
        ],
        exercises=[
            GrammarExercise(
                type="multiple_choice",
                question="Ich habe ___ Katze. (I have a cat)",
                options=["ein", "eine", "einen"],
                correct_answer="eine",
                explanation="Katze is feminine",
                difficulty=1
            )
        ],
        tags=["articles", "indefinite", "A1"]
    ))
    
    # Rule 3: Nominative Case
    rules.append(GrammarRule(
        title="Nominative Case",
        title_de="Nominativ",
        category="cases",
        level="A1",
        difficulty=2,
        description="The nominative case is used for the subject of a sentence (who or what is doing the action).",
        description_de="Der Nominativ wird für das Subjekt des Satzes verwendet.",
        usage=[
            "Subject of the sentence",
            "After 'sein' (to be), 'werden' (to become), 'bleiben' (to remain)"
        ],
        examples=[
            GrammarExample(german="Der Mann isst.", english="The man eats.", highlight="Der Mann"),
            GrammarExample(german="Das ist ein Buch.", english="That is a book.", highlight="ein Buch"),
            GrammarExample(german="Sie ist eine Lehrerin.", english="She is a teacher.", highlight="eine Lehrerin")
        ],
        common_mistakes=[
            {"wrong": "Den Mann isst", "correct": "Der Mann isst", "explanation": "Subject needs nominative"}
        ],
        exercises=[
            GrammarExercise(
                type="multiple_choice",
                question="___ Hund bellt. (The dog barks)",
                options=["Der", "Den", "Dem"],
                correct_answer="Der",
                explanation="Subject is in nominative case",
                difficulty=2
            )
        ],
        tags=["cases", "nominative", "A1"]
    ))
    
    # Rule 4: Accusative Case
    rules.append(GrammarRule(
        title="Accusative Case",
        title_de="Akkusativ",
        category="cases",
        level="A1",
        difficulty=2,
        description="The accusative case is used for the direct object (who or what receives the action).",
        description_de="Der Akkusativ wird für das direkte Objekt verwendet.",
        usage=[
            "Direct object of the sentence",
            "After accusative prepositions: durch, für, gegen, ohne, um",
            "With accusative verbs: haben, sehen, essen, trinken, etc."
        ],
        examples=[
            GrammarExample(german="Ich sehe den Mann.", english="I see the man.", highlight="den Mann"),
            GrammarExample(german="Sie hat einen Hund.", english="She has a dog.", highlight="einen Hund"),
            GrammarExample(german="Wir essen das Brot.", english="We eat the bread.", highlight="das Brot")
        ],
        common_mistakes=[
            {"wrong": "Ich sehe der Mann", "correct": "Ich sehe den Mann", "explanation": "Direct object needs accusative"},
            {"wrong": "Sie hat ein Hund", "correct": "Sie hat einen Hund", "explanation": "Masculine accusative changes 'ein' to 'einen'"}
        ],
        exercises=[
            GrammarExercise(
                type="multiple_choice",
                question="Ich kaufe ___ Auto. (I buy a car)",
                options=["der", "den", "das"],
                correct_answer="das",
                explanation="Auto is neuter, accusative same as nominative",
                difficulty=2
            ),
            GrammarExercise(
                type="multiple_choice",
                question="Er liebt ___ Frau. (He loves the woman)",
                options=["der", "die", "den"],
                correct_answer="die",
                explanation="Frau is feminine, accusative same as nominative",
                difficulty=2
            )
        ],
        tags=["cases", "accusative", "A1"]
    ))
    
    # ============================================================================
    # VERBS
    # ============================================================================
    
    # Rule 5: Present Tense Regular Verbs
    rules.append(GrammarRule(
        title="Present Tense - Regular Verbs",
        title_de="Präsens - Regelmäßige Verben",
        category="verbs",
        level="A1",
        difficulty=1,
        description="Regular verbs follow a pattern: remove -en ending and add personal endings.",
        description_de="Regelmäßige Verben folgen einem Muster.",
        usage=[
            "Actions happening now",
            "Habitual actions",
            "General truths"
        ],
        examples=[
            GrammarExample(german="ich lerne", english="I learn", highlight="lerne"),
            GrammarExample(german="du lernst", english="you learn", highlight="lernst"),
            GrammarExample(german="er/sie/es lernt", english="he/she/it learns", highlight="lernt"),
            GrammarExample(german="wir lernen", english="we learn", highlight="lernen"),
            GrammarExample(german="ihr lernt", english="you (plural) learn", highlight="lernt"),
            GrammarExample(german="sie/Sie lernen", english="they/you (formal) learn", highlight="lernen")
        ],
        common_mistakes=[
            {"wrong": "ich lernt", "correct": "ich lerne", "explanation": "First person singular ends in -e"},
            {"wrong": "du lernen", "correct": "du lernst", "explanation": "Second person singular ends in -st"}
        ],
        exercises=[
            GrammarExercise(
                type="fill_blank",
                question="Ich ___ Deutsch. (I learn German) [lernen]",
                correct_answer="lerne",
                explanation="First person singular: lern + e",
                difficulty=1
            ),
            GrammarExercise(
                type="fill_blank",
                question="Du ___ schnell. (You work fast) [arbeiten]",
                correct_answer="arbeitest",
                explanation="Second person singular: arbeit + est (extra e before st)",
                difficulty=2
            )
        ],
        tags=["verbs", "present", "conjugation", "A1"]
    ))
    
    # Rule 6: Separable Verbs
    rules.append(GrammarRule(
        title="Separable Verbs",
        title_de="Trennbare Verben",
        category="verbs",
        level="A2",
        difficulty=3,
        description="Separable verbs have a prefix that separates and moves to the end of the sentence in main clauses.",
        description_de="Trennbare Verben haben ein Präfix, das sich trennt.",
        usage=[
            "Prefix goes to end of main clause",
            "Prefix stays attached in subordinate clauses",
            "Common prefixes: ab-, an-, auf-, aus-, ein-, mit-, vor-, zu-"
        ],
        examples=[
            GrammarExample(german="Ich stehe um 7 Uhr auf.", english="I get up at 7 o'clock.", highlight="auf"),
            GrammarExample(german="Er kommt morgen an.", english="He arrives tomorrow.", highlight="an"),
            GrammarExample(german="Wir kaufen im Supermarkt ein.", english="We shop at the supermarket.", highlight="ein")
        ],
        common_mistakes=[
            {"wrong": "Ich aufstehe um 7 Uhr", "correct": "Ich stehe um 7 Uhr auf", "explanation": "Prefix goes to end"},
            {"wrong": "Er ankommt morgen", "correct": "Er kommt morgen an", "explanation": "Separate the prefix"}
        ],
        exercises=[
            GrammarExercise(
                type="transform",
                question="Transform: aufstehen (ich, 6 Uhr)",
                correct_answer="Ich stehe um 6 Uhr auf.",
                explanation="Prefix 'auf' goes to the end",
                difficulty=3
            )
        ],
        tags=["verbs", "separable", "A2"]
    ))
    
    # Rule 7: Modal Verbs
    rules.append(GrammarRule(
        title="Modal Verbs",
        title_de="Modalverben",
        category="verbs",
        level="A2",
        difficulty=2,
        description="Modal verbs express ability, permission, necessity, or desire. The main verb goes to the end in infinitive form.",
        description_de="Modalverben drücken Fähigkeit, Erlaubnis, Notwendigkeit oder Wunsch aus.",
        usage=[
            "können (can, to be able to)",
            "müssen (must, to have to)",
            "dürfen (may, to be allowed to)",
            "sollen (should, to be supposed to)",
            "wollen (to want to)",
            "mögen (to like)"
        ],
        examples=[
            GrammarExample(german="Ich kann schwimmen.", english="I can swim.", highlight="kann schwimmen"),
            GrammarExample(german="Du musst lernen.", english="You must learn.", highlight="musst lernen"),
            GrammarExample(german="Er will schlafen.", english="He wants to sleep.", highlight="will schlafen")
        ],
        common_mistakes=[
            {"wrong": "Ich kann zu schwimmen", "correct": "Ich kann schwimmen", "explanation": "No 'zu' with modal verbs"},
            {"wrong": "Du musst zu lernen", "correct": "Du musst lernen", "explanation": "Infinitive without 'zu'"}
        ],
        exercises=[
            GrammarExercise(
                type="multiple_choice",
                question="Ich ___ Deutsch sprechen. (I can speak German)",
                options=["kann", "muss", "will"],
                correct_answer="kann",
                explanation="'können' means 'can' or 'to be able to'",
                difficulty=2
            )
        ],
        tags=["verbs", "modal", "A2"]
    ))
    
    # ============================================================================
    # WORD ORDER
    # ============================================================================
    
    # Rule 8: Basic Word Order (SVO)
    rules.append(GrammarRule(
        title="Basic Word Order (Subject-Verb-Object)",
        title_de="Grundlegende Wortstellung",
        category="word_order",
        level="A1",
        difficulty=1,
        description="In German main clauses, the verb is always in the second position. The subject usually comes first.",
        description_de="In deutschen Hauptsätzen steht das Verb immer an zweiter Stelle.",
        usage=[
            "Subject + Verb + Object (most common)",
            "Time + Verb + Subject + Object (also common)",
            "Verb is ALWAYS second"
        ],
        examples=[
            GrammarExample(german="Ich esse einen Apfel.", english="I eat an apple.", highlight="esse"),
            GrammarExample(german="Heute esse ich einen Apfel.", english="Today I eat an apple.", highlight="esse"),
            GrammarExample(german="Der Mann kauft ein Auto.", english="The man buys a car.", highlight="kauft")
        ],
        common_mistakes=[
            {"wrong": "Ich einen Apfel esse", "correct": "Ich esse einen Apfel", "explanation": "Verb must be second"},
            {"wrong": "Heute ich esse", "correct": "Heute esse ich", "explanation": "Verb stays second, subject moves"}
        ],
        exercises=[
            GrammarExercise(
                type="transform",
                question="Reorder: (Ich / ein Buch / lese)",
                correct_answer="Ich lese ein Buch.",
                explanation="Subject + Verb + Object",
                difficulty=1
            )
        ],
        tags=["word_order", "syntax", "A1"]
    ))
    
    # Add more rules...
    # Rule 9: Adjective Endings
    # Rule 10: Dative Case
    # Rule 11: Genitive Case
    # Rule 12: Past Tense (Perfekt)
    # Rule 13: Subordinate Clauses
    # Rule 14: Comparative and Superlative
    # Rule 15: Reflexive Verbs
    
    return rules


def get_grammar_stats():
    """Get statistics about grammar rules"""
    rules = get_grammar_rules()
    
    stats = {
        "total_rules": len(rules),
        "by_level": {},
        "by_category": {}
    }
    
    for rule in rules:
        # Count by level
        level = rule.level
        stats["by_level"][level] = stats["by_level"].get(level, 0) + 1
        
        # Count by category
        category = rule.category
        stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
    
    return stats
