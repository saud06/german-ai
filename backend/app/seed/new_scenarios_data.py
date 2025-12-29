"""
New scenarios for Phase 4: Life Simulation Enhancement
10 additional real-world scenarios with branching paths
"""

from app.models.scenario import (
    Scenario, Character, Objective,
    PersonalityTrait, Emotion, DialogueBranch, DecisionPoint
)


def get_new_scenarios():
    """Get 10 new scenario data with enhanced features"""
    
    scenarios = []
    
    # Scenario 11: Doctor Visit (Medical)
    doctor_scenario = Scenario(
        name="Beim Arzt",
        title_en="At the Doctor",
        description="Du fühlst dich nicht gut und gehst zum Arzt. Beschreibe deine Symptome.",
        description_en="You're not feeling well and go to the doctor. Describe your symptoms.",
        difficulty="intermediate",
        category="medical",
        estimated_duration=8,
        icon="🏥",
        tags=["health", "medical", "symptoms"],
        xp_reward=150,
        bonus_xp=75,
        
        characters=[
            Character(
                name="Dr. Schmidt",
                role="doctor",
                personality="professional and caring",
                personality_traits=PersonalityTrait(
                    friendliness=8,
                    formality=9,
                    patience=9,
                    helpfulness=10,
                    chattiness=6
                ),
                emotion=Emotion(current="professional", intensity=7),
                voice_id="de_DE-thorsten-high",
                description="Dr. Schmidt ist eine erfahrene Ärztin mit 15 Jahren Praxis. Sie ist sehr geduldig und erklärt alles genau.",
                greeting="Guten Tag! Setzen Sie sich bitte. Was kann ich heute für Sie tun?",
                remembers_user=True
            )
        ],
        
        objectives=[
            Objective(
                description="Erkläre deine Symptome",
                keywords=["kopfschmerzen", "fieber", "husten", "halsschmerzen", "bauchschmerzen", "schmerzen"],
                required=True,
                hint="Sage 'Ich habe Kopfschmerzen' oder 'Mir tut der Hals weh'",
                xp_reward=60,
                difficulty_level=2
            ),
            Objective(
                description="Beantworte Fragen zur Krankengeschichte",
                keywords=["seit", "tagen", "gestern", "allergien", "medikamente"],
                required=True,
                hint="Sage 'Seit drei Tagen' oder 'Ich nehme keine Medikamente'",
                xp_reward=50,
                difficulty_level=3
            ),
            Objective(
                description="Verstehe die Diagnose",
                keywords=["verstehe", "okay", "danke", "rezept"],
                required=False,
                hint="Sage 'Ich verstehe' oder 'Was soll ich tun?'",
                xp_reward=40,
                difficulty_level=2
            )
        ],
        
        context="Der Benutzer ist beim Arzt und fühlt sich krank. Der Arzt muss die Symptome erfragen, eine Diagnose stellen und Behandlung empfehlen.",
        system_prompt="Du bist Dr. Schmidt, eine professionelle und fürsorgliche Ärztin. Frage nach Symptomen, stelle eine Diagnose und gib Behandlungsempfehlungen. Sei geduldig und erkläre medizinische Begriffe einfach."
    )
    scenarios.append(doctor_scenario)
    
    # Scenario 12: Job Interview (Professional)
    job_interview_scenario = Scenario(
        name="Vorstellungsgespräch",
        title_en="Job Interview",
        description="Du hast ein Vorstellungsgespräch für eine neue Stelle. Überzeuge den Interviewer!",
        description_en="You have a job interview for a new position. Convince the interviewer!",
        difficulty="advanced",
        category="professional",
        estimated_duration=10,
        icon="💼",
        tags=["work", "interview", "career"],
        xp_reward=200,
        bonus_xp=100,
        
        characters=[
            Character(
                name="Frau Müller",
                role="hr_manager",
                personality="professional and evaluative",
                personality_traits=PersonalityTrait(
                    friendliness=6,
                    formality=10,
                    patience=7,
                    helpfulness=5,
                    chattiness=5
                ),
                emotion=Emotion(current="neutral", intensity=5),
                voice_id="de_DE-thorsten-high",
                description="Frau Müller ist die Personalleiterin. Sie ist professionell und achtet auf Details.",
                greeting="Guten Tag! Schön, dass Sie da sind. Erzählen Sie mir etwas über sich.",
                remembers_user=True
            )
        ],
        
        objectives=[
            Objective(
                description="Stelle dich vor",
                keywords=["name", "studiert", "gearbeitet", "erfahrung", "qualifikation"],
                required=True,
                hint="Sage 'Ich heiße... und habe... studiert'",
                xp_reward=70,
                difficulty_level=3
            ),
            Objective(
                description="Beschreibe deine Stärken",
                keywords=["stärken", "gut", "team", "organisiert", "kreativ", "zuverlässig"],
                required=True,
                hint="Sage 'Meine Stärken sind...'",
                xp_reward=70,
                difficulty_level=4
            ),
            Objective(
                description="Stelle eine Frage",
                keywords=["frage", "team", "aufgaben", "arbeitszeiten", "gehalt"],
                required=False,
                hint="Frage 'Wie groß ist das Team?' oder 'Welche Aufgaben gibt es?'",
                xp_reward=60,
                difficulty_level=3
            )
        ],
        
        context="Der Benutzer ist in einem Vorstellungsgespräch. Der Interviewer stellt Fragen zur Erfahrung, Qualifikationen und Motivation.",
        system_prompt="Du bist Frau Müller, eine professionelle Personalleiterin. Stelle typische Interviewfragen, bewerte die Antworten und sei höflich aber kritisch."
    )
    scenarios.append(job_interview_scenario)
    
    # Scenario 13: Making Friends (Social)
    making_friends_scenario = Scenario(
        name="Neue Freunde finden",
        title_en="Making Friends",
        description="Du triffst jemanden in einem Café und möchtest ein Gespräch beginnen.",
        description_en="You meet someone at a café and want to start a conversation.",
        difficulty="beginner",
        category="social",
        estimated_duration=6,
        icon="👋",
        tags=["friends", "social", "conversation"],
        xp_reward=120,
        bonus_xp=60,
        
        characters=[
            Character(
                name="Lisa",
                role="student",
                personality="friendly and outgoing",
                personality_traits=PersonalityTrait(
                    friendliness=10,
                    formality=3,
                    patience=8,
                    helpfulness=9,
                    chattiness=9
                ),
                emotion=Emotion(current="happy", intensity=7),
                voice_id="de_DE-thorsten-high",
                description="Lisa ist eine freundliche Studentin, die gerne neue Leute kennenlernt.",
                greeting="Hallo! Ist hier noch frei?",
                remembers_user=True
            )
        ],
        
        objectives=[
            Objective(
                description="Begrüße die Person",
                keywords=["hallo", "hi", "guten tag", "ja", "klar", "natürlich"],
                required=True,
                hint="Sage 'Hallo!' oder 'Ja, klar!'",
                xp_reward=40,
                difficulty_level=1
            ),
            Objective(
                description="Stelle dich vor",
                keywords=["name", "heiße", "komme aus", "wohne", "studiere", "arbeite"],
                required=True,
                hint="Sage 'Ich heiße... Und du?'",
                xp_reward=50,
                difficulty_level=2
            ),
            Objective(
                description="Finde gemeinsame Interessen",
                keywords=["hobbys", "sport", "musik", "filme", "reisen", "lesen"],
                required=False,
                hint="Frage 'Was sind deine Hobbys?' oder erzähle von deinen",
                xp_reward=60,
                difficulty_level=2
            )
        ],
        
        context="Der Benutzer trifft eine freundliche Person im Café und möchte ein lockeres Gespräch führen.",
        system_prompt="Du bist Lisa, eine freundliche und gesprächige Studentin. Sei offen, stelle Fragen und teile Interessen. Mache das Gespräch natürlich und entspannt."
    )
    scenarios.append(making_friends_scenario)
    
    # Scenario 14: Public Transport (Travel)
    public_transport_scenario = Scenario(
        name="Mit der U-Bahn",
        title_en="Taking the Subway",
        description="Du musst mit der U-Bahn fahren und brauchst Hilfe mit dem Ticket.",
        description_en="You need to take the subway and need help with the ticket.",
        difficulty="beginner",
        category="transport",
        estimated_duration=5,
        icon="🚇",
        tags=["transport", "travel", "tickets"],
        xp_reward=100,
        bonus_xp=50,
        
        characters=[
            Character(
                name="Herr Weber",
                role="ticket_agent",
                personality="helpful but busy",
                personality_traits=PersonalityTrait(
                    friendliness=6,
                    formality=7,
                    patience=5,
                    helpfulness=8,
                    chattiness=4
                ),
                emotion=Emotion(current="neutral", intensity=5),
                voice_id="de_DE-thorsten-high",
                description="Herr Weber arbeitet am Ticketschalter und hilft Fahrgästen.",
                greeting="Ja, bitte? Wie kann ich Ihnen helfen?",
                remembers_user=False
            )
        ],
        
        objectives=[
            Objective(
                description="Sage wohin du fahren möchtest",
                keywords=["hauptbahnhof", "flughafen", "zentrum", "nach", "zum", "zur"],
                required=True,
                hint="Sage 'Ich möchte zum Hauptbahnhof'",
                xp_reward=50,
                difficulty_level=1
            ),
            Objective(
                description="Kaufe ein Ticket",
                keywords=["ticket", "fahrkarte", "einzelfahrt", "tageskarte", "bitte"],
                required=True,
                hint="Sage 'Eine Einzelfahrt, bitte' oder 'Eine Tageskarte'",
                xp_reward=50,
                difficulty_level=2
            )
        ],
        
        context="Der Benutzer ist am U-Bahn-Schalter und braucht ein Ticket.",
        system_prompt="Du bist Herr Weber, ein Ticketverkäufer. Sei hilfsbereit aber effizient. Erkläre die Ticketoptionen und den Preis."
    )
    scenarios.append(public_transport_scenario)
    
    # Scenario 15: Bank Visit (Financial)
    bank_scenario = Scenario(
        name="Bei der Bank",
        title_en="At the Bank",
        description="Du möchtest ein Bankkonto eröffnen.",
        description_en="You want to open a bank account.",
        difficulty="intermediate",
        category="financial",
        estimated_duration=8,
        icon="🏦",
        tags=["bank", "money", "account"],
        xp_reward=150,
        bonus_xp=75,
        
        characters=[
            Character(
                name="Frau Klein",
                role="bank_advisor",
                personality="professional and thorough",
                personality_traits=PersonalityTrait(
                    friendliness=7,
                    formality=9,
                    patience=8,
                    helpfulness=9,
                    chattiness=6
                ),
                emotion=Emotion(current="professional", intensity=6),
                voice_id="de_DE-thorsten-high",
                description="Frau Klein ist Bankberaterin und hilft bei Kontoeröffnungen.",
                greeting="Guten Tag! Wie kann ich Ihnen heute helfen?",
                remembers_user=True
            )
        ],
        
        objectives=[
            Objective(
                description="Erkläre was du möchtest",
                keywords=["konto", "eröffnen", "girokonto", "sparkonto", "möchte"],
                required=True,
                hint="Sage 'Ich möchte ein Konto eröffnen'",
                xp_reward=60,
                difficulty_level=2
            ),
            Objective(
                description="Beantworte Fragen zu deinen Daten",
                keywords=["name", "adresse", "geburtsdatum", "ausweis", "pass"],
                required=True,
                hint="Gib deine persönlichen Informationen",
                xp_reward=60,
                difficulty_level=3
            ),
            Objective(
                description="Verstehe die Konditionen",
                keywords=["gebühren", "zinsen", "karte", "online", "verstehe"],
                required=False,
                hint="Frage nach Gebühren oder Online-Banking",
                xp_reward=50,
                difficulty_level=3
            )
        ],
        
        context="Der Benutzer ist bei der Bank und möchte ein Konto eröffnen.",
        system_prompt="Du bist Frau Klein, eine professionelle Bankberaterin. Erkläre den Prozess der Kontoeröffnung, frage nach notwendigen Dokumenten und erkläre die Konditionen."
    )
    scenarios.append(bank_scenario)
    
    # Scenario 16: Apartment Hunting (Housing)
    apartment_scenario = Scenario(
        name="Wohnungsbesichtigung",
        title_en="Apartment Viewing",
        description="Du besichtigst eine Wohnung und sprichst mit dem Vermieter.",
        description_en="You're viewing an apartment and talking to the landlord.",
        difficulty="intermediate",
        category="housing",
        estimated_duration=7,
        icon="🏠",
        tags=["housing", "apartment", "rent"],
        xp_reward=140,
        bonus_xp=70,
        
        characters=[
            Character(
                name="Herr Braun",
                role="landlord",
                personality="business-like but fair",
                personality_traits=PersonalityTrait(
                    friendliness=6,
                    formality=8,
                    patience=6,
                    helpfulness=7,
                    chattiness=5
                ),
                emotion=Emotion(current="neutral", intensity=5),
                voice_id="de_DE-thorsten-high",
                description="Herr Braun ist Vermieter und zeigt die Wohnung.",
                greeting="Guten Tag! Kommen Sie herein. Das ist die Wohnung.",
                remembers_user=True
            )
        ],
        
        objectives=[
            Objective(
                description="Frage nach der Miete",
                keywords=["miete", "kosten", "preis", "nebenkosten", "kaution"],
                required=True,
                hint="Frage 'Wie hoch ist die Miete?'",
                xp_reward=50,
                difficulty_level=2
            ),
            Objective(
                description="Frage nach Details der Wohnung",
                keywords=["zimmer", "quadratmeter", "küche", "bad", "balkon", "heizung"],
                required=True,
                hint="Frage 'Wie viele Zimmer hat die Wohnung?'",
                xp_reward=60,
                difficulty_level=3
            ),
            Objective(
                description="Zeige Interesse oder lehne ab",
                keywords=["interessiert", "nehme", "überlegen", "danke", "melde mich"],
                required=False,
                hint="Sage 'Ich bin interessiert' oder 'Ich muss es mir überlegen'",
                xp_reward=50,
                difficulty_level=2
            )
        ],
        
        context="Der Benutzer besichtigt eine Wohnung und spricht mit dem Vermieter über Details und Konditionen.",
        system_prompt="Du bist Herr Braun, ein Vermieter. Zeige die Wohnung, beantworte Fragen zu Miete, Größe und Ausstattung. Sei geschäftsmäßig aber fair."
    )
    scenarios.append(apartment_scenario)
    
    # Scenario 17: Emergency Situation
    emergency_scenario = Scenario(
        name="Notfall",
        title_en="Emergency",
        description="Du hast einen Notfall und rufst die Notrufnummer an.",
        description_en="You have an emergency and call the emergency number.",
        difficulty="advanced",
        category="emergency",
        estimated_duration=6,
        icon="🚨",
        tags=["emergency", "help", "urgent"],
        xp_reward=180,
        bonus_xp=90,
        has_time_limit=True,
        time_limit_minutes=5,
        
        characters=[
            Character(
                name="Operator",
                role="emergency_operator",
                personality="calm and efficient",
                personality_traits=PersonalityTrait(
                    friendliness=7,
                    formality=8,
                    patience=9,
                    helpfulness=10,
                    chattiness=3
                ),
                emotion=Emotion(current="calm", intensity=8),
                voice_id="de_DE-thorsten-high",
                description="Notfall-Operator, ruhig und professionell.",
                greeting="Notruf, was ist passiert?",
                remembers_user=False
            )
        ],
        
        objectives=[
            Objective(
                description="Beschreibe den Notfall",
                keywords=["unfall", "verletzt", "feuer", "hilfe", "notfall", "krank"],
                required=True,
                hint="Sage 'Es gab einen Unfall' oder 'Jemand ist verletzt'",
                xp_reward=70,
                difficulty_level=4
            ),
            Objective(
                description="Gib deinen Standort an",
                keywords=["adresse", "straße", "nummer", "bin", "wo"],
                required=True,
                hint="Sage 'Ich bin in der... Straße'",
                xp_reward=70,
                difficulty_level=4
            ),
            Objective(
                description="Beantworte Fragen",
                keywords=["ja", "nein", "person", "atmet", "bewusstsein"],
                required=True,
                hint="Beantworte die Fragen des Operators",
                xp_reward=60,
                difficulty_level=5
            )
        ],
        
        context="Der Benutzer hat einen Notfall und muss schnell und klar kommunizieren.",
        system_prompt="Du bist ein Notfall-Operator. Bleibe ruhig, stelle klare Fragen und sammle wichtige Informationen: Was ist passiert? Wo? Wie viele Personen? Sind sie bei Bewusstsein?"
    )
    scenarios.append(emergency_scenario)
    
    # Scenario 18: Cultural Event
    cultural_event_scenario = Scenario(
        name="Im Museum",
        title_en="At the Museum",
        description="Du besuchst ein Museum und sprichst mit einem Guide.",
        description_en="You visit a museum and talk to a guide.",
        difficulty="intermediate",
        category="culture",
        estimated_duration=7,
        icon="🎨",
        tags=["culture", "museum", "art"],
        xp_reward=130,
        bonus_xp=65,
        
        characters=[
            Character(
                name="Frau Wagner",
                role="museum_guide",
                personality="enthusiastic and knowledgeable",
                personality_traits=PersonalityTrait(
                    friendliness=9,
                    formality=6,
                    patience=8,
                    helpfulness=10,
                    chattiness=8
                ),
                emotion=Emotion(current="enthusiastic", intensity=8),
                voice_id="de_DE-thorsten-high",
                description="Frau Wagner ist Museumsführerin und liebt Kunst.",
                greeting="Willkommen! Interessieren Sie sich für eine Führung?",
                remembers_user=True
            )
        ],
        
        objectives=[
            Objective(
                description="Frage nach einer Führung",
                keywords=["führung", "tour", "ausstellung", "zeigen", "erklären"],
                required=True,
                hint="Frage 'Gibt es eine Führung?'",
                xp_reward=50,
                difficulty_level=2
            ),
            Objective(
                description="Stelle Fragen zur Ausstellung",
                keywords=["künstler", "wann", "warum", "bedeutung", "stil"],
                required=True,
                hint="Frage 'Wer ist der Künstler?' oder 'Was bedeutet das?'",
                xp_reward=60,
                difficulty_level=3
            ),
            Objective(
                description="Bedanke dich",
                keywords=["danke", "interessant", "toll", "schön"],
                required=False,
                hint="Sage 'Vielen Dank!' oder 'Das war sehr interessant'",
                xp_reward=40,
                difficulty_level=1
            )
        ],
        
        context="Der Benutzer ist im Museum und möchte mehr über die Ausstellung erfahren.",
        system_prompt="Du bist Frau Wagner, eine begeisterte Museumsführerin. Erkläre die Kunstwerke mit Enthusiasmus, beantworte Fragen und teile interessante Fakten."
    )
    scenarios.append(cultural_event_scenario)
    
    # Scenario 19: Sports/Fitness
    fitness_scenario = Scenario(
        name="Im Fitnessstudio",
        title_en="At the Gym",
        description="Du möchtest dich im Fitnessstudio anmelden.",
        description_en="You want to sign up at the gym.",
        difficulty="beginner",
        category="sports",
        estimated_duration=6,
        icon="💪",
        tags=["sports", "fitness", "health"],
        xp_reward=110,
        bonus_xp=55,
        
        characters=[
            Character(
                name="Tom",
                role="fitness_trainer",
                personality="energetic and motivating",
                personality_traits=PersonalityTrait(
                    friendliness=10,
                    formality=4,
                    patience=7,
                    helpfulness=9,
                    chattiness=8
                ),
                emotion=Emotion(current="energetic", intensity=9),
                voice_id="de_DE-thorsten-high",
                description="Tom ist Fitnesstrainer und sehr motivierend.",
                greeting="Hey! Willkommen im Gym! Wie kann ich dir helfen?",
                remembers_user=True
            )
        ],
        
        objectives=[
            Objective(
                description="Sage was du möchtest",
                keywords=["anmelden", "mitglied", "trainieren", "fitness", "sport"],
                required=True,
                hint="Sage 'Ich möchte mich anmelden'",
                xp_reward=40,
                difficulty_level=1
            ),
            Objective(
                description="Frage nach Preisen und Angeboten",
                keywords=["preis", "kosten", "monat", "jahr", "probetraining"],
                required=True,
                hint="Frage 'Was kostet die Mitgliedschaft?'",
                xp_reward=50,
                difficulty_level=2
            ),
            Objective(
                description="Frage nach Kursen oder Training",
                keywords=["kurse", "yoga", "spinning", "training", "plan"],
                required=False,
                hint="Frage 'Welche Kurse gibt es?'",
                xp_reward=50,
                difficulty_level=2
            )
        ],
        
        context="Der Benutzer ist im Fitnessstudio und möchte Mitglied werden.",
        system_prompt="Du bist Tom, ein energischer Fitnesstrainer. Sei motivierend und freundlich. Erkläre die Mitgliedschaftsoptionen und Kurse."
    )
    scenarios.append(fitness_scenario)
    
    # Scenario 20: Technology Support
    tech_support_scenario = Scenario(
        name="Computer-Hilfe",
        title_en="Computer Help",
        description="Dein Computer hat ein Problem und du rufst den Support an.",
        description_en="Your computer has a problem and you call support.",
        difficulty="intermediate",
        category="technology",
        estimated_duration=8,
        icon="💻",
        tags=["technology", "computer", "support"],
        xp_reward=140,
        bonus_xp=70,
        
        characters=[
            Character(
                name="Herr Fischer",
                role="tech_support",
                personality="patient and technical",
                personality_traits=PersonalityTrait(
                    friendliness=7,
                    formality=6,
                    patience=10,
                    helpfulness=10,
                    chattiness=6
                ),
                emotion=Emotion(current="helpful", intensity=7),
                voice_id="de_DE-thorsten-high",
                description="Herr Fischer ist IT-Support-Mitarbeiter und sehr geduldig.",
                greeting="Technischer Support, Fischer. Was ist das Problem?",
                remembers_user=False
            )
        ],
        
        objectives=[
            Objective(
                description="Beschreibe das Problem",
                keywords=["funktioniert nicht", "fehler", "langsam", "internet", "bildschirm", "programm"],
                required=True,
                hint="Sage 'Mein Computer ist sehr langsam' oder 'Das Internet funktioniert nicht'",
                xp_reward=60,
                difficulty_level=3
            ),
            Objective(
                description="Folge den Anweisungen",
                keywords=["okay", "gemacht", "ja", "nein", "versuche", "sehe"],
                required=True,
                hint="Folge den Schritten: 'Okay, ich habe es gemacht'",
                xp_reward=60,
                difficulty_level=3
            ),
            Objective(
                description="Bestätige die Lösung",
                keywords=["funktioniert", "geht", "danke", "problem gelöst"],
                required=False,
                hint="Sage 'Ja, es funktioniert jetzt!' oder 'Danke für die Hilfe'",
                xp_reward=50,
                difficulty_level=2
            )
        ],
        
        context="Der Benutzer hat ein technisches Problem und braucht Hilfe vom Support.",
        system_prompt="Du bist Herr Fischer, ein geduldiger IT-Support-Mitarbeiter. Stelle Diagnosefragen, gib klare Anweisungen und helfe Schritt für Schritt."
    )
    scenarios.append(tech_support_scenario)
    
    return scenarios
