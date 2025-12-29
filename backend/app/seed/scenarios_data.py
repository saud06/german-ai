"""
Seed data for initial scenarios
"""

from app.models.scenario import Scenario, Character, Objective


def get_initial_scenarios():
    """Get initial scenario data"""
    
    scenarios = []
    
    # Scenario 1: Restaurant
    restaurant_scenario = Scenario(
        name="Im Restaurant",
        title_en="At the Restaurant",
        description="Du bist in einem deutschen Restaurant zum Mittagessen. Bestelle Essen und Getränke.",
        description_en="You're at a German restaurant for lunch. Order food and drinks.",
        difficulty="beginner",
        category="restaurant",
        estimated_duration=5,
        icon="🍽️",
        tags=["food", "dining", "ordering"],
        
        characters=[
            Character(
                name="Hans",
                role="waiter",
                personality="friendly",
                voice_id="de_DE-thorsten-high",
                description="Hans ist ein freundlicher Kellner, der seit 10 Jahren im Restaurant arbeitet. Er hilft gerne neuen Gästen.",
                greeting="Guten Tag! Willkommen in unserem Restaurant. Was möchten Sie trinken?"
            )
        ],
        
        objectives=[
            Objective(
                description="Begrüße den Kellner",
                keywords=["hallo", "guten tag", "grüß gott", "servus"],
                required=True,
                hint="Sage 'Guten Tag' oder 'Hallo'"
            ),
            Objective(
                description="Bestelle ein Getränk",
                keywords=["wasser", "bier", "wein", "cola", "saft", "kaffee", "tee", "möchte", "hätte gern"],
                required=True,
                hint="Sage 'Ich möchte ein Wasser, bitte' oder 'Ein Bier, bitte'"
            ),
            Objective(
                description="Frage nach der Speisekarte",
                keywords=["speisekarte", "karte", "menü", "essen", "haben sie"],
                required=True,
                hint="Frage 'Kann ich die Speisekarte haben?'"
            ),
            Objective(
                description="Bestelle ein Hauptgericht",
                keywords=["schnitzel", "bratwurst", "kartoffeln", "salat", "suppe", "hähnchen", "fisch", "bestellen", "nehme"],
                required=True,
                hint="Sage 'Ich nehme das Schnitzel' oder 'Ich möchte die Bratwurst'"
            ),
            Objective(
                description="Bitte um die Rechnung",
                keywords=["rechnung", "zahlen", "bezahlen", "bitte"],
                required=True,
                hint="Sage 'Die Rechnung, bitte' oder 'Ich möchte zahlen'"
            )
        ],
        
        context="""Dies ist ein typisches deutsches Restaurant. Der Gast kommt zum Mittagessen. 
        Der Kellner ist freundlich und hilfsbereit. Das Restaurant serviert traditionelle deutsche Küche.
        Typische Gerichte: Schnitzel, Bratwurst, Kartoffelsalat, Sauerkraut.""",
        
        system_prompt="""Du bist Hans, ein freundlicher Kellner in einem deutschen Restaurant.
        Hilf dem Gast beim Bestellen. Sei geduldig und freundlich.
        Empfehle Gerichte wenn gefragt. Halte die Konversation natürlich und kurz."""
    )
    scenarios.append(restaurant_scenario)
    
    # Scenario 2: Hotel Check-in
    hotel_scenario = Scenario(
        name="Hotel Check-in",
        title_en="Hotel Check-in",
        description="Du kommst in einem Hotel in Berlin an und möchtest einchecken.",
        description_en="You arrive at a hotel in Berlin and want to check in.",
        difficulty="intermediate",
        category="hotel",
        estimated_duration=8,
        icon="🏨",
        tags=["travel", "accommodation", "booking"],
        
        characters=[
            Character(
                name="Frau Schmidt",
                role="receptionist",
                personality="professional",
                voice_id="de_DE-thorsten-high",
                description="Frau Schmidt ist eine professionelle Rezeptionistin mit 15 Jahren Erfahrung. Sie ist höflich und effizient.",
                greeting="Guten Tag! Willkommen im Hotel Berlin. Wie kann ich Ihnen helfen?"
            )
        ],
        
        objectives=[
            Objective(
                description="Stelle dich vor",
                keywords=["name", "heiße", "bin", "reservierung", "gebucht"],
                required=True,
                hint="Sage 'Mein Name ist...' oder 'Ich habe eine Reservierung'"
            ),
            Objective(
                description="Bestätige deine Reservierung",
                keywords=["reservierung", "zimmer", "gebucht", "nächte", "übernachtung"],
                required=True,
                hint="Sage 'Ich habe ein Zimmer für zwei Nächte gebucht'"
            ),
            Objective(
                description="Frage nach der Frühstückszeit",
                keywords=["frühstück", "breakfast", "morgen", "uhr", "zeit", "wann"],
                required=True,
                hint="Frage 'Wann gibt es Frühstück?'"
            ),
            Objective(
                description="Bitte um den Zimmerschlüssel",
                keywords=["schlüssel", "key", "zimmer", "karte"],
                required=True,
                hint="Sage 'Kann ich den Zimmerschlüssel haben?'"
            ),
            Objective(
                description="Frage nach WLAN",
                keywords=["wlan", "wifi", "internet", "passwort", "code"],
                required=False,
                hint="Frage 'Wie ist das WLAN-Passwort?'"
            )
        ],
        
        context="""Dies ist die Rezeption eines modernen Hotels in Berlin. 
        Der Gast hat online ein Zimmer für 2 Nächte gebucht.
        Das Hotel bietet Frühstück von 7-10 Uhr, kostenloses WLAN, und einen Fitnessraum.
        Die Rezeptionistin ist professionell und hilfsbereit.""",
        
        system_prompt="""Du bist Frau Schmidt, eine professionelle Hotelrezeptionistin.
        Sei höflich und effizient. Beantworte Fragen über das Hotel.
        Frühstück: 7-10 Uhr, WLAN-Passwort: Berlin2024, Check-out: 11 Uhr."""
    )
    scenarios.append(hotel_scenario)
    
    # Scenario 3: Shopping
    shopping_scenario = Scenario(
        name="Im Supermarkt",
        title_en="At the Supermarket",
        description="Du kaufst im Supermarkt ein und brauchst Hilfe beim Finden von Produkten.",
        description_en="You're shopping at a supermarket and need help finding products.",
        difficulty="beginner",
        category="shopping",
        estimated_duration=5,
        icon="🛒",
        tags=["shopping", "groceries", "daily life"],
        
        characters=[
            Character(
                name="Herr Müller",
                role="shop_assistant",
                personality="helpful",
                voice_id="de_DE-thorsten-high",
                description="Herr Müller arbeitet seit 5 Jahren im Supermarkt. Er kennt jeden Gang und hilft gerne.",
                greeting="Guten Tag! Kann ich Ihnen helfen?"
            )
        ],
        
        objectives=[
            Objective(
                description="Begrüße den Verkäufer",
                keywords=["hallo", "guten tag", "tag", "grüß gott"],
                required=True,
                hint="Sage 'Guten Tag'"
            ),
            Objective(
                description="Frage wo etwas ist",
                keywords=["wo", "finde", "ist", "gibt", "haben sie", "milch", "brot", "obst", "gemüse"],
                required=True,
                hint="Frage 'Wo finde ich die Milch?' oder 'Wo ist das Brot?'"
            ),
            Objective(
                description="Frage nach dem Preis",
                keywords=["preis", "kostet", "kosten", "euro", "teuer", "viel"],
                required=True,
                hint="Frage 'Was kostet das?' oder 'Wie viel kostet die Milch?'"
            ),
            Objective(
                description="Bedanke dich",
                keywords=["danke", "dankeschön", "vielen dank"],
                required=True,
                hint="Sage 'Danke' oder 'Vielen Dank'"
            ),
            Objective(
                description="Verabschiede dich",
                keywords=["tschüss", "auf wiedersehen", "schönen tag", "bis bald"],
                required=True,
                hint="Sage 'Auf Wiedersehen' oder 'Tschüss'"
            )
        ],
        
        context="""Dies ist ein typischer deutscher Supermarkt. 
        Der Kunde sucht nach verschiedenen Produkten.
        Der Verkäufer ist hilfsbereit und kennt den Laden gut.
        Typische Produkte: Milch (1,50€), Brot (2,00€), Äpfel (3,00€/kg), Käse (4,50€).""",
        
        system_prompt="""Du bist Herr Müller, ein hilfsbereiter Supermarkt-Mitarbeiter.
        Hilf dem Kunden, Produkte zu finden. Nenne Preise wenn gefragt.
        Sei freundlich und geduldig. Halte Antworten kurz und klar."""
    )
    scenarios.append(shopping_scenario)
    
    # Scenario 4: At the Doctor
    doctor_scenario = Scenario(
        name="Beim Arzt",
        title_en="At the Doctor",
        description="Du fühlst dich krank und gehst zum Arzt. Beschreibe deine Symptome.",
        description_en="You feel sick and go to the doctor. Describe your symptoms.",
        difficulty="intermediate",
        category="health",
        estimated_duration=7,
        icon="🏥",
        tags=["health", "medical", "symptoms"],
        
        characters=[
            Character(
                name="Dr. Weber",
                role="doctor",
                personality="caring",
                voice_id="de_DE-thorsten-high",
                description="Dr. Weber ist eine erfahrene Ärztin mit 20 Jahren Praxis. Sie ist geduldig und verständnisvoll.",
                greeting="Guten Tag! Setzen Sie sich bitte. Was fehlt Ihnen?"
            )
        ],
        
        objectives=[
            Objective(
                description="Begrüße den Arzt",
                keywords=["guten tag", "hallo", "tag"],
                required=True,
                hint="Sage 'Guten Tag, Frau Doktor'"
            ),
            Objective(
                description="Beschreibe deine Symptome",
                keywords=["kopfschmerzen", "fieber", "husten", "schnupfen", "halsschmerzen", "bauchschmerzen", "schmerzen", "krank", "fühle"],
                required=True,
                hint="Sage 'Ich habe Kopfschmerzen' oder 'Mir tut der Hals weh'"
            ),
            Objective(
                description="Sage seit wann du krank bist",
                keywords=["seit", "tagen", "gestern", "heute", "woche", "montag"],
                required=True,
                hint="Sage 'Seit drei Tagen' oder 'Seit gestern'"
            ),
            Objective(
                description="Frage nach Medikamenten",
                keywords=["medikament", "tabletten", "medizin", "nehmen", "helfen", "brauche"],
                required=True,
                hint="Frage 'Was soll ich nehmen?' oder 'Welche Medikamente helfen?'"
            ),
            Objective(
                description="Bedanke dich",
                keywords=["danke", "vielen dank", "dankeschön"],
                required=True,
                hint="Sage 'Vielen Dank, Frau Doktor'"
            )
        ],
        
        context="""Dies ist eine Arztpraxis in Deutschland. Der Patient fühlt sich seit ein paar Tagen krank.
        Die Ärztin ist professionell und einfühlsam. Sie stellt Fragen zu den Symptomen und gibt Ratschläge.
        Typische Behandlungen: Ruhe, viel trinken, Schmerztabletten, bei Bedarf Antibiotika.""",
        
        system_prompt="""Du bist Dr. Weber, eine einfühlsame Ärztin.
        Frage nach Symptomen und seit wann der Patient krank ist.
        Gib medizinische Ratschläge: Ruhe, viel trinken, Ibuprofen bei Schmerzen.
        Sei professionell aber freundlich. Halte Antworten klar und verständlich."""
    )
    scenarios.append(doctor_scenario)
    
    # Scenario 5: At the Train Station
    train_scenario = Scenario(
        name="Am Bahnhof",
        title_en="At the Train Station",
        description="Du möchtest eine Zugfahrkarte kaufen und Informationen über Abfahrtszeiten bekommen.",
        description_en="You want to buy a train ticket and get information about departure times.",
        difficulty="intermediate",
        category="travel",
        estimated_duration=6,
        icon="🚂",
        tags=["travel", "transportation", "tickets"],
        
        characters=[
            Character(
                name="Herr Klein",
                role="ticket_agent",
                personality="efficient",
                voice_id="de_DE-thorsten-high",
                description="Herr Klein arbeitet seit 10 Jahren am Fahrkartenschalter. Er ist schnell und hilfsbereit.",
                greeting="Guten Tag! Wohin möchten Sie fahren?"
            )
        ],
        
        objectives=[
            Objective(
                description="Sage wohin du fahren möchtest",
                keywords=["nach", "münchen", "berlin", "hamburg", "köln", "frankfurt", "fahren", "möchte"],
                required=True,
                hint="Sage 'Ich möchte nach München fahren'"
            ),
            Objective(
                description="Frage nach der Abfahrtszeit",
                keywords=["wann", "abfahrt", "fährt", "uhr", "zeit", "nächste"],
                required=True,
                hint="Frage 'Wann fährt der nächste Zug?'"
            ),
            Objective(
                description="Frage nach dem Preis",
                keywords=["kostet", "preis", "euro", "ticket", "fahrkarte", "viel"],
                required=True,
                hint="Frage 'Was kostet die Fahrkarte?'"
            ),
            Objective(
                description="Kaufe eine Fahrkarte",
                keywords=["kaufen", "möchte", "nehme", "eine", "ticket", "fahrkarte", "bitte"],
                required=True,
                hint="Sage 'Ich möchte eine Fahrkarte kaufen'"
            ),
            Objective(
                description="Frage nach dem Gleis",
                keywords=["gleis", "platform", "wo", "abfahrt", "fährt ab"],
                required=True,
                hint="Frage 'Von welchem Gleis fährt der Zug ab?'"
            )
        ],
        
        context="""Dies ist ein Fahrkartenschalter am Hauptbahnhof.
        Der Kunde möchte eine Fahrkarte für eine Reise kaufen.
        Züge nach München: 10:30, 12:45, 15:20 Uhr. Preis: 89€ (2. Klasse), 129€ (1. Klasse).
        Der Mitarbeiter ist effizient und kennt alle Verbindungen.""",
        
        system_prompt="""Du bist Herr Klein, ein Fahrkartenschalter-Mitarbeiter.
        Beantworte Fragen zu Abfahrtszeiten, Preisen und Gleisen.
        Nächster Zug nach München: 12:45 Uhr, Gleis 7, Preis: 89€.
        Sei freundlich aber effizient. Halte Antworten kurz."""
    )
    scenarios.append(train_scenario)
    
    # Scenario 6: At the Bank
    bank_scenario = Scenario(
        name="In der Bank",
        title_en="At the Bank",
        description="Du möchtest ein Konto eröffnen und Informationen über Bankdienstleistungen bekommen.",
        description_en="You want to open an account and get information about banking services.",
        difficulty="advanced",
        category="finance",
        estimated_duration=10,
        icon="🏦",
        tags=["banking", "finance", "account"],
        
        characters=[
            Character(
                name="Frau Becker",
                role="bank_advisor",
                personality="professional",
                voice_id="de_DE-thorsten-high",
                description="Frau Becker ist Bankberaterin mit 15 Jahren Erfahrung. Sie ist kompetent und vertrauenswürdig.",
                greeting="Guten Tag! Willkommen bei der Deutschen Bank. Wie kann ich Ihnen helfen?"
            )
        ],
        
        objectives=[
            Objective(
                description="Erkläre dein Anliegen",
                keywords=["konto", "eröffnen", "möchte", "brauche", "girokonto", "sparkonto"],
                required=True,
                hint="Sage 'Ich möchte ein Konto eröffnen'"
            ),
            Objective(
                description="Frage nach den Kontogebühren",
                keywords=["gebühren", "kosten", "kostet", "monat", "jahr", "euro"],
                required=True,
                hint="Frage 'Welche Gebühren fallen an?'"
            ),
            Objective(
                description="Frage nach einer EC-Karte",
                keywords=["karte", "ec-karte", "bankkarte", "girocard", "debitkarte"],
                required=True,
                hint="Frage 'Bekomme ich eine EC-Karte?'"
            ),
            Objective(
                description="Frage nach Online-Banking",
                keywords=["online", "banking", "internet", "app", "smartphone"],
                required=True,
                hint="Frage 'Gibt es Online-Banking?'"
            ),
            Objective(
                description="Frage welche Dokumente du brauchst",
                keywords=["dokumente", "brauche", "mitbringen", "ausweis", "pass", "papiere"],
                required=True,
                hint="Frage 'Welche Dokumente brauche ich?'"
            )
        ],
        
        context="""Dies ist eine Bankfiliale in Deutschland.
        Der Kunde möchte ein Girokonto eröffnen.
        Kontogebühren: 0€ bei Gehaltseingang, sonst 4,90€/Monat.
        Inklusive: EC-Karte, Online-Banking, Mobile App.
        Benötigte Dokumente: Personalausweis, Meldebescheinigung.""",
        
        system_prompt="""Du bist Frau Becker, eine professionelle Bankberaterin.
        Erkläre die Konditionen: 0€ Gebühren bei Gehaltseingang, EC-Karte kostenlos, Online-Banking inklusive.
        Dokumente: Personalausweis und Meldebescheinigung.
        Sei professionell und vertrauenswürdig. Erkläre alles klar."""
    )
    scenarios.append(bank_scenario)
    
    # Scenario 7: At the Pharmacy
    pharmacy_scenario = Scenario(
        name="In der Apotheke",
        title_en="At the Pharmacy",
        description="Du brauchst Medikamente und möchtest Beratung von einem Apotheker.",
        description_en="You need medication and want advice from a pharmacist.",
        difficulty="beginner",
        category="health",
        estimated_duration=5,
        icon="💊",
        tags=["health", "pharmacy", "medicine"],
        
        characters=[
            Character(
                name="Frau Hoffmann",
                role="pharmacist",
                personality="caring",
                voice_id="de_DE-thorsten-high",
                description="Frau Hoffmann ist Apothekerin seit 12 Jahren. Sie berät Kunden freundlich und kompetent.",
                greeting="Guten Tag! Was kann ich für Sie tun?"
            )
        ],
        
        objectives=[
            Objective(
                description="Begrüße die Apothekerin",
                keywords=["guten tag", "hallo", "tag"],
                required=True,
                hint="Sage 'Guten Tag'"
            ),
            Objective(
                description="Erkläre dein Problem",
                keywords=["kopfschmerzen", "erkältung", "husten", "schnupfen", "schmerzen", "habe", "brauche"],
                required=True,
                hint="Sage 'Ich habe Kopfschmerzen' oder 'Ich bin erkältet'"
            ),
            Objective(
                description="Frage nach einem Medikament",
                keywords=["medikament", "tabletten", "tropfen", "salbe", "mittel", "empfehlen", "haben sie"],
                required=True,
                hint="Frage 'Was empfehlen Sie?' oder 'Haben Sie etwas gegen Kopfschmerzen?'"
            ),
            Objective(
                description="Frage wie du es einnehmen sollst",
                keywords=["einnehmen", "nehmen", "wie oft", "dosierung", "wann", "mal", "täglich"],
                required=True,
                hint="Frage 'Wie oft soll ich das nehmen?'"
            ),
            Objective(
                description="Bedanke dich",
                keywords=["danke", "vielen dank", "dankeschön"],
                required=True,
                hint="Sage 'Vielen Dank'"
            )
        ],
        
        context="""Dies ist eine Apotheke in Deutschland.
        Der Kunde hat leichte Beschwerden und sucht Rat.
        Die Apothekerin empfiehlt rezeptfreie Medikamente.
        Typische Empfehlungen: Ibuprofen (Schmerzen), Nasenspray (Schnupfen), Hustensaft (Husten).""",
        
        system_prompt="""Du bist Frau Hoffmann, eine freundliche Apothekerin.
        Empfehle passende Medikamente: Ibuprofen 400mg (3x täglich), Nasenspray (2x täglich).
        Erkläre die Einnahme klar und einfach.
        Sei fürsorglich und geduldig."""
    )
    scenarios.append(pharmacy_scenario)
    
    # Scenario 8: At the Post Office
    post_scenario = Scenario(
        name="Bei der Post",
        title_en="At the Post Office",
        description="Du möchtest ein Paket verschicken und Briefmarken kaufen.",
        description_en="You want to send a package and buy stamps.",
        difficulty="beginner",
        category="services",
        estimated_duration=5,
        icon="📮",
        tags=["postal", "shipping", "mail"],
        
        characters=[
            Character(
                name="Herr Wagner",
                role="postal_clerk",
                personality="helpful",
                voice_id="de_DE-thorsten-high",
                description="Herr Wagner arbeitet seit 8 Jahren bei der Post. Er ist geduldig und hilfsbereit.",
                greeting="Guten Tag! Was kann ich für Sie tun?"
            )
        ],
        
        objectives=[
            Objective(
                description="Sage was du möchtest",
                keywords=["paket", "verschicken", "senden", "schicken", "möchte", "brief", "briefmarken"],
                required=True,
                hint="Sage 'Ich möchte ein Paket verschicken'"
            ),
            Objective(
                description="Sage wohin das Paket soll",
                keywords=["nach", "deutschland", "österreich", "schweiz", "ausland", "inland"],
                required=True,
                hint="Sage 'Nach München' oder 'Nach Österreich'"
            ),
            Objective(
                description="Frage nach dem Preis",
                keywords=["kostet", "preis", "euro", "viel", "kosten"],
                required=True,
                hint="Frage 'Was kostet das?'"
            ),
            Objective(
                description="Frage wie lange es dauert",
                keywords=["dauert", "lange", "tage", "wann", "ankommt", "lieferzeit"],
                required=True,
                hint="Frage 'Wie lange dauert das?'"
            ),
            Objective(
                description="Bedanke dich",
                keywords=["danke", "dankeschön", "vielen dank"],
                required=True,
                hint="Sage 'Danke schön'"
            )
        ],
        
        context="""Dies ist eine Postfiliale in Deutschland.
        Der Kunde möchte ein Paket verschicken.
        Preise: Inland 4,99€ (1-2 Tage), Ausland 9,99€ (3-5 Tage).
        Der Mitarbeiter ist hilfsbereit und erklärt alle Optionen.""",
        
        system_prompt="""Du bist Herr Wagner, ein hilfsbereiter Post-Mitarbeiter.
        Erkläre die Versandoptionen: Inland 4,99€ (1-2 Tage), Ausland 9,99€ (3-5 Tage).
        Frage nach Größe und Gewicht des Pakets.
        Sei freundlich und geduldig."""
    )
    scenarios.append(post_scenario)
    
    # Scenario 9: Apartment Viewing
    apartment_scenario = Scenario(
        name="Wohnungsbesichtigung",
        title_en="Apartment Viewing",
        description="Du besichtigst eine Wohnung und stellst Fragen zum Mietvertrag.",
        description_en="You're viewing an apartment and asking questions about the rental contract.",
        difficulty="advanced",
        category="housing",
        estimated_duration=10,
        icon="🏠",
        tags=["housing", "rental", "apartment"],
        
        characters=[
            Character(
                name="Frau Schneider",
                role="landlord",
                personality="professional",
                voice_id="de_DE-thorsten-high",
                description="Frau Schneider vermietet seit 20 Jahren Wohnungen. Sie ist professionell und fair.",
                greeting="Guten Tag! Willkommen! Möchten Sie die Wohnung sehen?"
            )
        ],
        
        objectives=[
            Objective(
                description="Stelle dich vor",
                keywords=["name", "heiße", "bin", "ich"],
                required=True,
                hint="Sage 'Guten Tag, mein Name ist...'"
            ),
            Objective(
                description="Frage nach der Miete",
                keywords=["miete", "kostet", "monat", "kaltmiete", "warmmiete", "euro"],
                required=True,
                hint="Frage 'Wie hoch ist die Miete?'"
            ),
            Objective(
                description="Frage nach den Nebenkosten",
                keywords=["nebenkosten", "strom", "heizung", "wasser", "kosten", "inklusive"],
                required=True,
                hint="Frage 'Was ist in den Nebenkosten enthalten?'"
            ),
            Objective(
                description="Frage nach der Kaution",
                keywords=["kaution", "anzahlung", "sicherheit", "deposit"],
                required=True,
                hint="Frage 'Wie hoch ist die Kaution?'"
            ),
            Objective(
                description="Frage wann du einziehen kannst",
                keywords=["einziehen", "wann", "ab wann", "verfügbar", "frei"],
                required=True,
                hint="Frage 'Ab wann ist die Wohnung frei?'"
            ),
            Objective(
                description="Frage nach Haustieren",
                keywords=["haustiere", "hund", "katze", "erlaubt", "tiere"],
                required=False,
                hint="Frage 'Sind Haustiere erlaubt?'"
            )
        ],
        
        context="""Dies ist eine Wohnungsbesichtigung in Berlin.
        Die Wohnung: 2 Zimmer, 65m², 3. Stock, mit Balkon.
        Kaltmiete: 850€, Nebenkosten: 150€, Kaution: 2 Monatsmieten.
        Verfügbar ab 1. nächsten Monat. Haustiere nach Absprache.
        Die Vermieterin ist professionell und beantwortet alle Fragen.""",
        
        system_prompt="""Du bist Frau Schneider, eine professionelle Vermieterin.
        Wohnungsdetails: 2 Zimmer, 65m², Kaltmiete 850€, Nebenkosten 150€ (Heizung, Wasser, Müll).
        Kaution: 1700€ (2 Monatsmieten), verfügbar ab 1. nächsten Monat.
        Haustiere: nach Absprache möglich.
        Sei professionell und beantworte alle Fragen klar."""
    )
    scenarios.append(apartment_scenario)
    
    # Scenario 10: Job Interview
    interview_scenario = Scenario(
        name="Vorstellungsgespräch",
        title_en="Job Interview",
        description="Du hast ein Vorstellungsgespräch für eine Stelle als Softwareentwickler.",
        description_en="You have a job interview for a position as a software developer.",
        difficulty="advanced",
        category="career",
        estimated_duration=12,
        icon="💼",
        tags=["career", "interview", "professional"],
        
        characters=[
            Character(
                name="Herr Fischer",
                role="hr_manager",
                personality="professional",
                voice_id="de_DE-thorsten-high",
                description="Herr Fischer ist HR-Manager mit 15 Jahren Erfahrung. Er ist professionell aber freundlich.",
                greeting="Guten Tag! Schön, dass Sie da sind. Bitte nehmen Sie Platz. Erzählen Sie mir etwas über sich."
            )
        ],
        
        objectives=[
            Objective(
                description="Stelle dich vor",
                keywords=["name", "heiße", "bin", "komme aus", "studiert", "abschluss"],
                required=True,
                hint="Sage 'Mein Name ist... Ich habe... studiert'"
            ),
            Objective(
                description="Beschreibe deine Erfahrung",
                keywords=["erfahrung", "gearbeitet", "jahre", "firma", "projekt", "entwicklung"],
                required=True,
                hint="Sage 'Ich habe 3 Jahre Erfahrung als...'"
            ),
            Objective(
                description="Erkläre warum du dich bewirbst",
                keywords=["interesse", "interessiert", "möchte", "weil", "firma", "position"],
                required=True,
                hint="Sage 'Ich interessiere mich für diese Position, weil...'"
            ),
            Objective(
                description="Frage nach den Aufgaben",
                keywords=["aufgaben", "tätigkeiten", "machen", "arbeiten", "projekt", "team"],
                required=True,
                hint="Frage 'Was wären meine Aufgaben?'"
            ),
            Objective(
                description="Frage nach dem Gehalt",
                keywords=["gehalt", "verdienen", "bezahlung", "euro", "jahr", "monat"],
                required=True,
                hint="Frage 'Wie ist das Gehalt?'"
            ),
            Objective(
                description="Bedanke dich für das Gespräch",
                keywords=["danke", "vielen dank", "gespräch", "zeit"],
                required=True,
                hint="Sage 'Vielen Dank für das Gespräch'"
            )
        ],
        
        context="""Dies ist ein Vorstellungsgespräch bei einer IT-Firma in München.
        Position: Softwareentwickler (Full-Stack), Team: 8 Personen.
        Aufgaben: Webentwicklung mit React und Node.js, Agile Methoden.
        Gehalt: 55.000-65.000€ pro Jahr (je nach Erfahrung).
        Der HR-Manager ist professionell und möchte den Kandidaten kennenlernen.""",
        
        system_prompt="""Du bist Herr Fischer, ein professioneller HR-Manager.
        Stelle Fragen zur Erfahrung und Motivation des Kandidaten.
        Position: Full-Stack Entwickler, Technologien: React, Node.js, MongoDB.
        Gehalt: 55.000-65.000€/Jahr, 30 Tage Urlaub, flexible Arbeitszeiten.
        Sei professionell aber freundlich. Beantworte Fragen ehrlich."""
    )
    scenarios.append(interview_scenario)
    
    return scenarios
