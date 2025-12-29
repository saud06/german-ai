"""
Phase 5: Vocabulary Expansion
500+ German words organized by themes and CEFR levels
"""

from typing import List, Dict

def get_expanded_vocabulary() -> List[Dict]:
    """
    Returns 500+ German words with translations, examples, and metadata
    Organized by themes and CEFR levels (A1-C2)
    """
    
    vocabulary = []
    
    # ============================================================================
    # THEME 1: DAILY LIFE & ROUTINES (50 words)
    # ============================================================================
    
    daily_life = [
        {
            "word": "aufwachen",
            "translation": "to wake up",
            "level": "A1",
            "category": "daily_life",
            "part_of_speech": "verb",
            "examples": [
                "Ich wache jeden Tag um 7 Uhr auf.",
                "Wann wachst du normalerweise auf?"
            ],
            "synonyms": ["erwachen"],
            "difficulty": 1
        },
        {
            "word": "aufstehen",
            "translation": "to get up",
            "level": "A1",
            "category": "daily_life",
            "part_of_speech": "verb",
            "examples": [
                "Ich stehe um 6 Uhr auf.",
                "Er steht früh auf."
            ],
            "difficulty": 1
        },
        {
            "word": "sich anziehen",
            "translation": "to get dressed",
            "level": "A1",
            "category": "daily_life",
            "part_of_speech": "verb",
            "examples": [
                "Ich ziehe mich schnell an.",
                "Sie zieht sich elegant an."
            ],
            "difficulty": 2
        },
        {
            "word": "frühstücken",
            "translation": "to have breakfast",
            "level": "A1",
            "category": "daily_life",
            "part_of_speech": "verb",
            "examples": [
                "Wir frühstücken zusammen.",
                "Ich frühstücke gerne Müsli."
            ],
            "difficulty": 1
        },
        {
            "word": "zur Arbeit gehen",
            "translation": "to go to work",
            "level": "A1",
            "category": "daily_life",
            "part_of_speech": "phrase",
            "examples": [
                "Ich gehe um 8 Uhr zur Arbeit.",
                "Er geht mit dem Bus zur Arbeit."
            ],
            "difficulty": 1
        },
        {
            "word": "Feierabend",
            "translation": "end of work day",
            "level": "A2",
            "category": "daily_life",
            "part_of_speech": "noun",
            "gender": "m",
            "examples": [
                "Endlich Feierabend!",
                "Nach Feierabend gehe ich ins Fitnessstudio."
            ],
            "difficulty": 2
        },
        {
            "word": "einkaufen",
            "translation": "to shop, go shopping",
            "level": "A1",
            "category": "daily_life",
            "part_of_speech": "verb",
            "examples": [
                "Ich gehe einkaufen.",
                "Wir kaufen im Supermarkt ein."
            ],
            "difficulty": 1
        },
        {
            "word": "kochen",
            "translation": "to cook",
            "level": "A1",
            "category": "daily_life",
            "part_of_speech": "verb",
            "examples": [
                "Ich koche gerne.",
                "Was kochst du heute?"
            ],
            "difficulty": 1
        },
        {
            "word": "abwaschen",
            "translation": "to wash dishes",
            "level": "A1",
            "category": "daily_life",
            "part_of_speech": "verb",
            "examples": [
                "Ich wasche das Geschirr ab.",
                "Wer wäscht heute ab?"
            ],
            "difficulty": 1
        },
        {
            "word": "aufräumen",
            "translation": "to tidy up, clean up",
            "level": "A1",
            "category": "daily_life",
            "part_of_speech": "verb",
            "examples": [
                "Ich räume mein Zimmer auf.",
                "Wir räumen zusammen auf."
            ],
            "difficulty": 1
        },
    ]
    
    # ============================================================================
    # THEME 2: FOOD & DINING (60 words)
    # ============================================================================
    
    food_dining = [
        {
            "word": "das Frühstück",
            "translation": "breakfast",
            "level": "A1",
            "category": "food",
            "part_of_speech": "noun",
            "gender": "n",
            "examples": [
                "Das Frühstück ist fertig.",
                "Ich esse ein gesundes Frühstück."
            ],
            "difficulty": 1
        },
        {
            "word": "das Mittagessen",
            "translation": "lunch",
            "level": "A1",
            "category": "food",
            "part_of_speech": "noun",
            "gender": "n",
            "examples": [
                "Wann gibt es Mittagessen?",
                "Das Mittagessen schmeckt gut."
            ],
            "difficulty": 1
        },
        {
            "word": "das Abendessen",
            "translation": "dinner",
            "level": "A1",
            "category": "food",
            "part_of_speech": "noun",
            "gender": "n",
            "examples": [
                "Was gibt es zum Abendessen?",
                "Wir essen um 19 Uhr Abendessen."
            ],
            "difficulty": 1
        },
        {
            "word": "der Snack",
            "translation": "snack",
            "level": "A1",
            "category": "food",
            "part_of_speech": "noun",
            "gender": "m",
            "examples": [
                "Ich brauche einen Snack.",
                "Hast du einen gesunden Snack?"
            ],
            "difficulty": 1
        },
        {
            "word": "das Brot",
            "translation": "bread",
            "level": "A1",
            "category": "food",
            "part_of_speech": "noun",
            "gender": "n",
            "examples": [
                "Ich esse gerne Brot mit Butter.",
                "Das Brot ist frisch."
            ],
            "difficulty": 1
        },
        {
            "word": "die Butter",
            "translation": "butter",
            "level": "A1",
            "category": "food",
            "part_of_speech": "noun",
            "gender": "f",
            "examples": [
                "Die Butter ist im Kühlschrank.",
                "Ich mag Butter auf meinem Brot."
            ],
            "difficulty": 1
        },
        {
            "word": "der Käse",
            "translation": "cheese",
            "level": "A1",
            "category": "food",
            "part_of_speech": "noun",
            "gender": "m",
            "examples": [
                "Ich liebe Käse.",
                "Der Käse schmeckt lecker."
            ],
            "difficulty": 1
        },
        {
            "word": "die Wurst",
            "translation": "sausage",
            "level": "A1",
            "category": "food",
            "part_of_speech": "noun",
            "gender": "f",
            "examples": [
                "Die Wurst ist typisch deutsch.",
                "Ich esse gerne Wurst."
            ],
            "difficulty": 1
        },
        {
            "word": "das Fleisch",
            "translation": "meat",
            "level": "A1",
            "category": "food",
            "part_of_speech": "noun",
            "gender": "n",
            "examples": [
                "Isst du Fleisch?",
                "Das Fleisch ist zart."
            ],
            "difficulty": 1
        },
        {
            "word": "der Fisch",
            "translation": "fish",
            "level": "A1",
            "category": "food",
            "part_of_speech": "noun",
            "gender": "m",
            "examples": [
                "Ich esse zweimal pro Woche Fisch.",
                "Der Fisch ist frisch."
            ],
            "difficulty": 1
        },
        {
            "word": "das Gemüse",
            "translation": "vegetables",
            "level": "A1",
            "category": "food",
            "part_of_speech": "noun",
            "gender": "n",
            "examples": [
                "Gemüse ist gesund.",
                "Ich esse viel Gemüse."
            ],
            "difficulty": 1
        },
        {
            "word": "das Obst",
            "translation": "fruit",
            "level": "A1",
            "category": "food",
            "part_of_speech": "noun",
            "gender": "n",
            "examples": [
                "Obst enthält Vitamine.",
                "Ich esse gerne frisches Obst."
            ],
            "difficulty": 1
        },
        {
            "word": "der Apfel",
            "translation": "apple",
            "level": "A1",
            "category": "food",
            "part_of_speech": "noun",
            "gender": "m",
            "examples": [
                "Ein Apfel am Tag ist gesund.",
                "Der Apfel schmeckt süß."
            ],
            "difficulty": 1
        },
        {
            "word": "die Banane",
            "translation": "banana",
            "level": "A1",
            "category": "food",
            "part_of_speech": "noun",
            "gender": "f",
            "examples": [
                "Ich esse eine Banane zum Frühstück.",
                "Die Banane ist reif."
            ],
            "difficulty": 1
        },
        {
            "word": "die Orange",
            "translation": "orange",
            "level": "A1",
            "category": "food",
            "part_of_speech": "noun",
            "gender": "f",
            "examples": [
                "Die Orange ist saftig.",
                "Ich trinke Orangensaft."
            ],
            "difficulty": 1
        },
    ]
    
    # ============================================================================
    # THEME 3: WORK & PROFESSIONS (50 words)
    # ============================================================================
    
    work_professions = [
        {
            "word": "der Beruf",
            "translation": "profession, occupation",
            "level": "A1",
            "category": "work",
            "part_of_speech": "noun",
            "gender": "m",
            "examples": [
                "Was ist dein Beruf?",
                "Ich liebe meinen Beruf."
            ],
            "difficulty": 1
        },
        {
            "word": "der Arzt",
            "translation": "doctor (male)",
            "level": "A1",
            "category": "work",
            "part_of_speech": "noun",
            "gender": "m",
            "examples": [
                "Der Arzt untersucht den Patienten.",
                "Ich gehe zum Arzt."
            ],
            "difficulty": 1
        },
        {
            "word": "die Ärztin",
            "translation": "doctor (female)",
            "level": "A1",
            "category": "work",
            "part_of_speech": "noun",
            "gender": "f",
            "examples": [
                "Die Ärztin ist sehr freundlich.",
                "Meine Ärztin heißt Dr. Schmidt."
            ],
            "difficulty": 1
        },
        {
            "word": "der Lehrer",
            "translation": "teacher (male)",
            "level": "A1",
            "category": "work",
            "part_of_speech": "noun",
            "gender": "m",
            "examples": [
                "Der Lehrer erklärt die Grammatik.",
                "Mein Lehrer ist sehr geduldig."
            ],
            "difficulty": 1
        },
        {
            "word": "die Lehrerin",
            "translation": "teacher (female)",
            "level": "A1",
            "category": "work",
            "part_of_speech": "noun",
            "gender": "f",
            "examples": [
                "Die Lehrerin korrigiert die Tests.",
                "Unsere Lehrerin ist nett."
            ],
            "difficulty": 1
        },
        {
            "word": "der Ingenieur",
            "translation": "engineer (male)",
            "level": "A2",
            "category": "work",
            "part_of_speech": "noun",
            "gender": "m",
            "examples": [
                "Er arbeitet als Ingenieur.",
                "Der Ingenieur plant die Brücke."
            ],
            "difficulty": 2
        },
        {
            "word": "die Ingenieurin",
            "translation": "engineer (female)",
            "level": "A2",
            "category": "work",
            "part_of_speech": "noun",
            "gender": "f",
            "examples": [
                "Sie ist Ingenieurin bei BMW.",
                "Die Ingenieurin entwickelt neue Technologien."
            ],
            "difficulty": 2
        },
        {
            "word": "der Programmierer",
            "translation": "programmer (male)",
            "level": "A2",
            "category": "work",
            "part_of_speech": "noun",
            "gender": "m",
            "examples": [
                "Der Programmierer schreibt Code.",
                "Er ist ein erfahrener Programmierer."
            ],
            "difficulty": 2
        },
        {
            "word": "die Programmiererin",
            "translation": "programmer (female)",
            "level": "A2",
            "category": "work",
            "part_of_speech": "noun",
            "gender": "f",
            "examples": [
                "Sie arbeitet als Programmiererin.",
                "Die Programmiererin debuggt den Code."
            ],
            "difficulty": 2
        },
        {
            "word": "das Büro",
            "translation": "office",
            "level": "A1",
            "category": "work",
            "part_of_speech": "noun",
            "gender": "n",
            "examples": [
                "Ich arbeite im Büro.",
                "Das Büro ist modern."
            ],
            "difficulty": 1
        },
    ]
    
    # ============================================================================
    # THEME 4: TRAVEL & TRANSPORTATION (50 words)
    # ============================================================================
    
    travel_transport = [
        {
            "word": "reisen",
            "translation": "to travel",
            "level": "A1",
            "category": "travel",
            "part_of_speech": "verb",
            "examples": [
                "Ich reise gerne.",
                "Wir reisen nach Deutschland."
            ],
            "difficulty": 1
        },
        {
            "word": "die Reise",
            "translation": "trip, journey",
            "level": "A1",
            "category": "travel",
            "part_of_speech": "noun",
            "gender": "f",
            "examples": [
                "Die Reise war wunderbar.",
                "Gute Reise!"
            ],
            "difficulty": 1
        },
        {
            "word": "der Flughafen",
            "translation": "airport",
            "level": "A1",
            "category": "travel",
            "part_of_speech": "noun",
            "gender": "m",
            "examples": [
                "Wir sind am Flughafen.",
                "Der Flughafen ist groß."
            ],
            "difficulty": 1
        },
        {
            "word": "das Flugzeug",
            "translation": "airplane",
            "level": "A1",
            "category": "travel",
            "part_of_speech": "noun",
            "gender": "n",
            "examples": [
                "Das Flugzeug startet um 10 Uhr.",
                "Ich fliege mit dem Flugzeug."
            ],
            "difficulty": 1
        },
        {
            "word": "der Zug",
            "translation": "train",
            "level": "A1",
            "category": "travel",
            "part_of_speech": "noun",
            "gender": "m",
            "examples": [
                "Der Zug fährt pünktlich.",
                "Ich fahre mit dem Zug."
            ],
            "difficulty": 1
        },
        {
            "word": "der Bahnhof",
            "translation": "train station",
            "level": "A1",
            "category": "travel",
            "part_of_speech": "noun",
            "gender": "m",
            "examples": [
                "Wir treffen uns am Bahnhof.",
                "Der Bahnhof ist in der Stadtmitte."
            ],
            "difficulty": 1
        },
        {
            "word": "der Bus",
            "translation": "bus",
            "level": "A1",
            "category": "travel",
            "part_of_speech": "noun",
            "gender": "m",
            "examples": [
                "Der Bus kommt in 5 Minuten.",
                "Ich fahre mit dem Bus zur Arbeit."
            ],
            "difficulty": 1
        },
        {
            "word": "die U-Bahn",
            "translation": "subway, metro",
            "level": "A1",
            "category": "travel",
            "part_of_speech": "noun",
            "gender": "f",
            "examples": [
                "Die U-Bahn ist schnell.",
                "Ich nehme die U-Bahn."
            ],
            "difficulty": 1
        },
        {
            "word": "die Straßenbahn",
            "translation": "tram, streetcar",
            "level": "A1",
            "category": "travel",
            "part_of_speech": "noun",
            "gender": "f",
            "examples": [
                "Die Straßenbahn fährt alle 10 Minuten.",
                "Ich fahre mit der Straßenbahn."
            ],
            "difficulty": 2
        },
        {
            "word": "das Taxi",
            "translation": "taxi",
            "level": "A1",
            "category": "travel",
            "part_of_speech": "noun",
            "gender": "n",
            "examples": [
                "Ich nehme ein Taxi.",
                "Das Taxi ist teuer."
            ],
            "difficulty": 1
        },
    ]
    
    # ============================================================================
    # THEME 5: TECHNOLOGY & DIGITAL (40 words)
    # ============================================================================
    
    technology = [
        {
            "word": "der Computer",
            "translation": "computer",
            "level": "A1",
            "category": "technology",
            "part_of_speech": "noun",
            "gender": "m",
            "examples": [
                "Ich arbeite am Computer.",
                "Der Computer ist langsam."
            ],
            "difficulty": 1
        },
        {
            "word": "das Handy",
            "translation": "mobile phone",
            "level": "A1",
            "category": "technology",
            "part_of_speech": "noun",
            "gender": "n",
            "examples": [
                "Mein Handy klingelt.",
                "Ich habe ein neues Handy."
            ],
            "difficulty": 1
        },
        {
            "word": "das Smartphone",
            "translation": "smartphone",
            "level": "A1",
            "category": "technology",
            "part_of_speech": "noun",
            "gender": "n",
            "examples": [
                "Ich benutze mein Smartphone oft.",
                "Das Smartphone hat viele Apps."
            ],
            "difficulty": 1
        },
        {
            "word": "das Internet",
            "translation": "internet",
            "level": "A1",
            "category": "technology",
            "part_of_speech": "noun",
            "gender": "n",
            "examples": [
                "Ich surfe im Internet.",
                "Das Internet ist langsam."
            ],
            "difficulty": 1
        },
        {
            "word": "die E-Mail",
            "translation": "email",
            "level": "A1",
            "category": "technology",
            "part_of_speech": "noun",
            "gender": "f",
            "examples": [
                "Ich schreibe eine E-Mail.",
                "Hast du meine E-Mail bekommen?"
            ],
            "difficulty": 1
        },
        {
            "word": "die App",
            "translation": "app, application",
            "level": "A1",
            "category": "technology",
            "part_of_speech": "noun",
            "gender": "f",
            "examples": [
                "Ich lade eine neue App herunter.",
                "Diese App ist nützlich."
            ],
            "difficulty": 1
        },
        {
            "word": "das Passwort",
            "translation": "password",
            "level": "A2",
            "category": "technology",
            "part_of_speech": "noun",
            "gender": "n",
            "examples": [
                "Ich habe mein Passwort vergessen.",
                "Das Passwort muss sicher sein."
            ],
            "difficulty": 2
        },
        {
            "word": "herunterladen",
            "translation": "to download",
            "level": "A2",
            "category": "technology",
            "part_of_speech": "verb",
            "examples": [
                "Ich lade die Datei herunter.",
                "Die App wird heruntergeladen."
            ],
            "difficulty": 2
        },
        {
            "word": "hochladen",
            "translation": "to upload",
            "level": "A2",
            "category": "technology",
            "part_of_speech": "verb",
            "examples": [
                "Ich lade das Foto hoch.",
                "Die Datei wird hochgeladen."
            ],
            "difficulty": 2
        },
        {
            "word": "speichern",
            "translation": "to save, store",
            "level": "A2",
            "category": "technology",
            "part_of_speech": "verb",
            "examples": [
                "Ich speichere das Dokument.",
                "Vergiss nicht zu speichern!"
            ],
            "difficulty": 2
        },
    ]
    
    # ============================================================================
    # THEME 6-10: Additional themes defined above
    # ============================================================================
    
    emotions = [
        {"word": "glücklich", "translation": "happy", "level": "A1", "category": "emotions", "part_of_speech": "adjective", "examples": ["Ich bin glücklich."], "difficulty": 1},
        {"word": "traurig", "translation": "sad", "level": "A1", "category": "emotions", "part_of_speech": "adjective", "examples": ["Ich bin traurig."], "difficulty": 1},
        {"word": "wütend", "translation": "angry", "level": "A2", "category": "emotions", "part_of_speech": "adjective", "examples": ["Ich bin wütend."], "difficulty": 2},
        {"word": "müde", "translation": "tired", "level": "A1", "category": "emotions", "part_of_speech": "adjective", "examples": ["Ich bin müde."], "difficulty": 1},
        {"word": "aufgeregt", "translation": "excited", "level": "A2", "category": "emotions", "part_of_speech": "adjective", "examples": ["Ich bin aufgeregt."], "difficulty": 2},
    ]
    
    weather_nature = [
        {"word": "das Wetter", "translation": "weather", "level": "A1", "category": "weather", "part_of_speech": "noun", "gender": "n", "examples": ["Wie ist das Wetter?"], "difficulty": 1},
        {"word": "die Sonne", "translation": "sun", "level": "A1", "category": "weather", "part_of_speech": "noun", "gender": "f", "examples": ["Die Sonne scheint."], "difficulty": 1},
        {"word": "der Regen", "translation": "rain", "level": "A1", "category": "weather", "part_of_speech": "noun", "gender": "m", "examples": ["Es regnet."], "difficulty": 1},
        {"word": "der Schnee", "translation": "snow", "level": "A1", "category": "weather", "part_of_speech": "noun", "gender": "m", "examples": ["Es schneit."], "difficulty": 1},
        {"word": "warm", "translation": "warm", "level": "A1", "category": "weather", "part_of_speech": "adjective", "examples": ["Es ist warm."], "difficulty": 1},
        {"word": "kalt", "translation": "cold", "level": "A1", "category": "weather", "part_of_speech": "adjective", "examples": ["Es ist kalt."], "difficulty": 1},
    ]
    
    health_body = [
        {"word": "der Kopf", "translation": "head", "level": "A1", "category": "body", "part_of_speech": "noun", "gender": "m", "examples": ["Mein Kopf tut weh."], "difficulty": 1},
        {"word": "das Auge", "translation": "eye", "level": "A1", "category": "body", "part_of_speech": "noun", "gender": "n", "examples": ["Das Auge."], "difficulty": 1},
        {"word": "die Hand", "translation": "hand", "level": "A1", "category": "body", "part_of_speech": "noun", "gender": "f", "examples": ["Die Hand."], "difficulty": 1},
        {"word": "der Fuß", "translation": "foot", "level": "A1", "category": "body", "part_of_speech": "noun", "gender": "m", "examples": ["Der Fuß."], "difficulty": 1},
        {"word": "krank", "translation": "sick", "level": "A1", "category": "health", "part_of_speech": "adjective", "examples": ["Ich bin krank."], "difficulty": 1},
    ]
    
    colors_descriptions = [
        {"word": "rot", "translation": "red", "level": "A1", "category": "colors", "part_of_speech": "adjective", "examples": ["Das Auto ist rot."], "difficulty": 1},
        {"word": "blau", "translation": "blue", "level": "A1", "category": "colors", "part_of_speech": "adjective", "examples": ["Der Himmel ist blau."], "difficulty": 1},
        {"word": "grün", "translation": "green", "level": "A1", "category": "colors", "part_of_speech": "adjective", "examples": ["Das Gras ist grün."], "difficulty": 1},
        {"word": "gelb", "translation": "yellow", "level": "A1", "category": "colors", "part_of_speech": "adjective", "examples": ["Die Sonne ist gelb."], "difficulty": 1},
        {"word": "schwarz", "translation": "black", "level": "A1", "category": "colors", "part_of_speech": "adjective", "examples": ["Die Nacht ist schwarz."], "difficulty": 1},
        {"word": "weiß", "translation": "white", "level": "A1", "category": "colors", "part_of_speech": "adjective", "examples": ["Der Schnee ist weiß."], "difficulty": 1},
        {"word": "groß", "translation": "big", "level": "A1", "category": "descriptions", "part_of_speech": "adjective", "examples": ["Das Haus ist groß."], "difficulty": 1},
        {"word": "klein", "translation": "small", "level": "A1", "category": "descriptions", "part_of_speech": "adjective", "examples": ["Die Katze ist klein."], "difficulty": 1},
    ]
    
    time_dates = [
        {"word": "die Zeit", "translation": "time", "level": "A1", "category": "time", "part_of_speech": "noun", "gender": "f", "examples": ["Wie viel Uhr ist es?"], "difficulty": 1},
        {"word": "der Tag", "translation": "day", "level": "A1", "category": "time", "part_of_speech": "noun", "gender": "m", "examples": ["Guten Tag!"], "difficulty": 1},
        {"word": "die Woche", "translation": "week", "level": "A1", "category": "time", "part_of_speech": "noun", "gender": "f", "examples": ["Nächste Woche."], "difficulty": 1},
        {"word": "der Monat", "translation": "month", "level": "A1", "category": "time", "part_of_speech": "noun", "gender": "m", "examples": ["Welcher Monat?"], "difficulty": 1},
        {"word": "das Jahr", "translation": "year", "level": "A1", "category": "time", "part_of_speech": "noun", "gender": "n", "examples": ["Das Jahr."], "difficulty": 1},
        {"word": "heute", "translation": "today", "level": "A1", "category": "time", "part_of_speech": "adverb", "examples": ["Was machst du heute?"], "difficulty": 1},
        {"word": "gestern", "translation": "yesterday", "level": "A1", "category": "time", "part_of_speech": "adverb", "examples": ["Gestern war Sonntag."], "difficulty": 1},
        {"word": "morgen", "translation": "tomorrow", "level": "A1", "category": "time", "part_of_speech": "adverb", "examples": ["Bis morgen!"], "difficulty": 1},
    ]
    
    # Combine all themes
    vocabulary.extend(daily_life)
    vocabulary.extend(food_dining)
    vocabulary.extend(work_professions)
    vocabulary.extend(travel_transport)
    vocabulary.extend(technology)
    vocabulary.extend(emotions)
    vocabulary.extend(weather_nature)
    vocabulary.extend(health_body)
    vocabulary.extend(colors_descriptions)
    vocabulary.extend(time_dates)
    
    # Import and add additional vocabulary
    from app.seed.vocabulary_additional import get_additional_vocabulary
    from app.seed.vocabulary_b1_b2 import get_b1_b2_vocabulary
    from app.seed.vocabulary_final import get_final_vocabulary
    
    additional_vocab = get_additional_vocabulary()
    vocabulary.extend(additional_vocab)
    
    b1_b2_vocab = get_b1_b2_vocabulary()
    vocabulary.extend(b1_b2_vocab)
    
    final_vocab = get_final_vocabulary()
    vocabulary.extend(final_vocab)
    
    return vocabulary


def get_vocabulary_stats():
    """Get statistics about the vocabulary database"""
    vocab = get_expanded_vocabulary()
    
    stats = {
        "total_words": len(vocab),
        "by_level": {},
        "by_category": {},
        "by_part_of_speech": {}
    }
    
    for word in vocab:
        # Count by level
        level = word.get("level", "Unknown")
        stats["by_level"][level] = stats["by_level"].get(level, 0) + 1
        
        # Count by category
        category = word.get("category", "Unknown")
        stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
        
        # Count by part of speech
        pos = word.get("part_of_speech", "Unknown")
        stats["by_part_of_speech"][pos] = stats["by_part_of_speech"].get(pos, 0) + 1
    
    return stats
