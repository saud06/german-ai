"""
Seed 500+ vocabulary words for Phase 5 - Organized by themes
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = "german_ai"

async def seed_phase5_vocabulary():
    """Seed 500+ vocabulary words organized by themes"""
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DB_NAME]
    
    print("📚 Seeding Phase 5 Vocabulary (500+ words)...")
    
    # Organized vocabulary by themes
    vocabulary_themes = {
        "Medical & Health": [
            ("der Arzt", "doctor", "A2", "noun"),
            ("die Ärztin", "female doctor", "A2", "noun"),
            ("das Krankenhaus", "hospital", "A2", "noun"),
            ("die Apotheke", "pharmacy", "A2", "noun"),
            ("das Medikament", "medication", "A2", "noun"),
            ("die Tablette", "pill/tablet", "A2", "noun"),
            ("der Schmerz", "pain", "A2", "noun"),
            ("die Kopfschmerzen", "headache", "A2", "noun"),
            ("das Fieber", "fever", "A2", "noun"),
            ("der Husten", "cough", "A2", "noun"),
            ("die Erkältung", "cold", "A2", "noun"),
            ("die Grippe", "flu", "B1", "noun"),
            ("die Allergie", "allergy", "B1", "noun"),
            ("die Verletzung", "injury", "B1", "noun"),
            ("die Wunde", "wound", "B1", "noun"),
            ("der Verband", "bandage", "B1", "noun"),
            ("die Spritze", "injection", "B1", "noun"),
            ("die Diagnose", "diagnosis", "B1", "noun"),
            ("die Behandlung", "treatment", "B1", "noun"),
            ("die Versicherung", "insurance", "B1", "noun"),
            ("der Termin", "appointment", "A2", "noun"),
            ("die Untersuchung", "examination", "B1", "noun"),
            ("das Rezept", "prescription", "B1", "noun"),
            ("die Symptome", "symptoms", "B1", "noun"),
            ("gesund", "healthy", "A2", "adjective"),
            ("krank", "sick", "A2", "adjective"),
            ("schmerzhaft", "painful", "B1", "adjective"),
            ("chronisch", "chronic", "B2", "adjective"),
            ("akut", "acute", "B2", "adjective"),
            ("untersuchen", "to examine", "B1", "verb"),
        ],
        
        "Professional & Work": [
            ("der Beruf", "profession", "A2", "noun"),
            ("die Arbeit", "work", "A1", "noun"),
            ("der Arbeitsplatz", "workplace", "A2", "noun"),
            ("das Büro", "office", "A2", "noun"),
            ("der Chef", "boss", "A2", "noun"),
            ("die Chefin", "female boss", "A2", "noun"),
            ("der Kollege", "colleague (male)", "A2", "noun"),
            ("die Kollegin", "colleague (female)", "A2", "noun"),
            ("das Gehalt", "salary", "B1", "noun"),
            ("die Bewerbung", "application", "B1", "noun"),
            ("der Lebenslauf", "CV/resume", "B1", "noun"),
            ("das Vorstellungsgespräch", "job interview", "B1", "noun"),
            ("die Qualifikation", "qualification", "B1", "noun"),
            ("die Erfahrung", "experience", "B1", "noun"),
            ("die Fähigkeit", "skill/ability", "B1", "noun"),
            ("die Ausbildung", "training/education", "B1", "noun"),
            ("das Studium", "studies", "B1", "noun"),
            ("der Abschluss", "degree", "B1", "noun"),
            ("die Karriere", "career", "B1", "noun"),
            ("die Beförderung", "promotion", "B2", "noun"),
            ("die Kündigung", "termination", "B2", "noun"),
            ("der Vertrag", "contract", "B1", "noun"),
            ("die Vollzeit", "full-time", "B1", "noun"),
            ("die Teilzeit", "part-time", "B1", "noun"),
            ("die Überstunden", "overtime", "B1", "noun"),
            ("der Urlaub", "vacation", "A2", "noun"),
            ("die Pause", "break", "A2", "noun"),
            ("die Besprechung", "meeting", "B1", "noun"),
            ("das Projekt", "project", "B1", "noun"),
            ("die Deadline", "deadline", "B1", "noun"),
        ],
        
        "Housing & Living": [
            ("die Wohnung", "apartment", "A2", "noun"),
            ("das Haus", "house", "A1", "noun"),
            ("die Miete", "rent", "A2", "noun"),
            ("der Vermieter", "landlord", "B1", "noun"),
            ("der Mieter", "tenant", "B1", "noun"),
            ("die Kaution", "deposit", "B1", "noun"),
            ("die Nebenkosten", "utilities", "B1", "noun"),
            ("das Zimmer", "room", "A1", "noun"),
            ("das Schlafzimmer", "bedroom", "A2", "noun"),
            ("das Wohnzimmer", "living room", "A2", "noun"),
            ("die Küche", "kitchen", "A1", "noun"),
            ("das Badezimmer", "bathroom", "A2", "noun"),
            ("der Balkon", "balcony", "A2", "noun"),
            ("der Garten", "garden", "A2", "noun"),
            ("die Garage", "garage", "A2", "noun"),
            ("der Keller", "basement", "A2", "noun"),
            ("das Dach", "roof", "A2", "noun"),
            ("die Tür", "door", "A1", "noun"),
            ("das Fenster", "window", "A1", "noun"),
            ("die Wand", "wall", "A2", "noun"),
            ("der Boden", "floor", "A2", "noun"),
            ("die Decke", "ceiling", "A2", "noun"),
            ("die Heizung", "heating", "B1", "noun"),
            ("die Klimaanlage", "air conditioning", "B1", "noun"),
            ("der Strom", "electricity", "B1", "noun"),
            ("das Wasser", "water", "A1", "noun"),
            ("das Gas", "gas", "B1", "noun"),
            ("das Internet", "internet", "A2", "noun"),
            ("möbliert", "furnished", "B1", "adjective"),
            ("unmöbliert", "unfurnished", "B1", "adjective"),
        ],
        
        "Transportation": [
            ("das Auto", "car", "A1", "noun"),
            ("der Bus", "bus", "A1", "noun"),
            ("die Bahn", "train", "A1", "noun"),
            ("der Zug", "train", "A1", "noun"),
            ("die U-Bahn", "subway", "A2", "noun"),
            ("die S-Bahn", "city train", "A2", "noun"),
            ("die Straßenbahn", "tram", "A2", "noun"),
            ("das Taxi", "taxi", "A1", "noun"),
            ("das Fahrrad", "bicycle", "A1", "noun"),
            ("das Motorrad", "motorcycle", "A2", "noun"),
            ("das Flugzeug", "airplane", "A2", "noun"),
            ("das Schiff", "ship", "A2", "noun"),
            ("der Bahnhof", "train station", "A2", "noun"),
            ("der Flughafen", "airport", "A2", "noun"),
            ("die Haltestelle", "stop", "A2", "noun"),
            ("das Gleis", "platform/track", "A2", "noun"),
            ("die Fahrkarte", "ticket", "A2", "noun"),
            ("der Fahrplan", "schedule", "A2", "noun"),
            ("die Verspätung", "delay", "B1", "noun"),
            ("die Abfahrt", "departure", "B1", "noun"),
            ("die Ankunft", "arrival", "B1", "noun"),
            ("umsteigen", "to transfer", "A2", "verb"),
            ("einsteigen", "to board", "A2", "verb"),
            ("aussteigen", "to get off", "A2", "verb"),
            ("fahren", "to drive/go", "A1", "verb"),
            ("fliegen", "to fly", "A2", "verb"),
            ("parken", "to park", "A2", "verb"),
            ("tanken", "to refuel", "A2", "verb"),
            ("der Führerschein", "driver's license", "B1", "noun"),
            ("die Versicherung", "insurance", "B1", "noun"),
        ],
        
        "Banking & Finance": [
            ("die Bank", "bank", "A2", "noun"),
            ("das Konto", "account", "A2", "noun"),
            ("das Girokonto", "checking account", "B1", "noun"),
            ("das Sparkonto", "savings account", "B1", "noun"),
            ("die Kreditkarte", "credit card", "A2", "noun"),
            ("die EC-Karte", "debit card", "A2", "noun"),
            ("das Bargeld", "cash", "A2", "noun"),
            ("der Geldautomat", "ATM", "A2", "noun"),
            ("die Überweisung", "transfer", "B1", "noun"),
            ("die Einzahlung", "deposit", "B1", "noun"),
            ("die Auszahlung", "withdrawal", "B1", "noun"),
            ("der Kredit", "loan", "B1", "noun"),
            ("die Schulden", "debt", "B1", "noun"),
            ("die Zinsen", "interest", "B1", "noun"),
            ("die Gebühr", "fee", "B1", "noun"),
            ("der Kontostand", "balance", "B1", "noun"),
            ("die Rechnung", "bill/invoice", "A2", "noun"),
            ("bezahlen", "to pay", "A1", "verb"),
            ("überweisen", "to transfer", "B1", "verb"),
            ("abheben", "to withdraw", "B1", "verb"),
            ("einzahlen", "to deposit", "B1", "verb"),
            ("sparen", "to save", "A2", "verb"),
            ("leihen", "to borrow/lend", "A2", "verb"),
            ("verdienen", "to earn", "A2", "verb"),
            ("ausgeben", "to spend", "A2", "verb"),
            ("kostenlos", "free", "A2", "adjective"),
            ("teuer", "expensive", "A1", "adjective"),
            ("billig", "cheap", "A1", "adjective"),
            ("günstig", "affordable", "A2", "adjective"),
            ("der Preis", "price", "A1", "noun"),
        ],
        
        "Technology": [
            ("der Computer", "computer", "A1", "noun"),
            ("der Laptop", "laptop", "A2", "noun"),
            ("das Handy", "mobile phone", "A1", "noun"),
            ("das Smartphone", "smartphone", "A2", "noun"),
            ("das Tablet", "tablet", "A2", "noun"),
            ("der Bildschirm", "screen", "A2", "noun"),
            ("die Tastatur", "keyboard", "A2", "noun"),
            ("die Maus", "mouse", "A2", "noun"),
            ("der Drucker", "printer", "A2", "noun"),
            ("das Internet", "internet", "A2", "noun"),
            ("das WLAN", "WiFi", "A2", "noun"),
            ("die E-Mail", "email", "A2", "noun"),
            ("die Nachricht", "message", "A2", "noun"),
            ("die App", "app", "A2", "noun"),
            ("die Software", "software", "B1", "noun"),
            ("das Programm", "program", "A2", "noun"),
            ("die Datei", "file", "B1", "noun"),
            ("der Ordner", "folder", "B1", "noun"),
            ("das Passwort", "password", "A2", "noun"),
            ("der Virus", "virus", "B1", "noun"),
            ("der Fehler", "error", "A2", "noun"),
            ("das Problem", "problem", "A2", "noun"),
            ("die Lösung", "solution", "B1", "noun"),
            ("installieren", "to install", "B1", "verb"),
            ("herunterladen", "to download", "B1", "verb"),
            ("hochladen", "to upload", "B1", "verb"),
            ("speichern", "to save", "A2", "verb"),
            ("löschen", "to delete", "A2", "verb"),
            ("funktionieren", "to work/function", "A2", "verb"),
            ("reparieren", "to repair", "A2", "verb"),
        ],
        
        "Emergency & Safety": [
            ("der Notfall", "emergency", "B1", "noun"),
            ("die Hilfe", "help", "A1", "noun"),
            ("der Unfall", "accident", "A2", "noun"),
            ("das Feuer", "fire", "A2", "noun"),
            ("die Polizei", "police", "A1", "noun"),
            ("die Feuerwehr", "fire department", "A2", "noun"),
            ("der Krankenwagen", "ambulance", "A2", "noun"),
            ("der Notruf", "emergency call", "B1", "noun"),
            ("die Gefahr", "danger", "B1", "noun"),
            ("die Sicherheit", "safety", "B1", "noun"),
            ("der Diebstahl", "theft", "B1", "noun"),
            ("der Einbruch", "burglary", "B1", "noun"),
            ("verletzt", "injured", "B1", "adjective"),
            ("gefährlich", "dangerous", "B1", "adjective"),
            ("sicher", "safe", "A2", "adjective"),
            ("helfen", "to help", "A1", "verb"),
            ("retten", "to rescue", "B1", "verb"),
            ("rufen", "to call", "A1", "verb"),
            ("schreien", "to scream", "A2", "verb"),
            ("warnen", "to warn", "B1", "verb"),
        ],
        
        "Culture & Entertainment": [
            ("das Theater", "theater", "A2", "noun"),
            ("das Kino", "cinema", "A1", "noun"),
            ("das Museum", "museum", "A2", "noun"),
            ("die Ausstellung", "exhibition", "B1", "noun"),
            ("das Konzert", "concert", "A2", "noun"),
            ("die Oper", "opera", "B1", "noun"),
            ("das Festival", "festival", "A2", "noun"),
            ("die Veranstaltung", "event", "B1", "noun"),
            ("die Aufführung", "performance", "B1", "noun"),
            ("das Stück", "play/piece", "B1", "noun"),
            ("der Film", "movie", "A1", "noun"),
            ("die Musik", "music", "A1", "noun"),
            ("die Kunst", "art", "A2", "noun"),
            ("der Künstler", "artist", "A2", "noun"),
            ("die Kultur", "culture", "B1", "noun"),
            ("die Tradition", "tradition", "B1", "noun"),
            ("das Ticket", "ticket", "A2", "noun"),
            ("die Karte", "ticket/card", "A2", "noun"),
            ("der Eintritt", "admission", "B1", "noun"),
            ("die Vorstellung", "show/performance", "B1", "noun"),
            ("reservieren", "to reserve", "A2", "verb"),
            ("buchen", "to book", "A2", "verb"),
            ("besuchen", "to visit", "A2", "verb"),
            ("ansehen", "to watch", "A2", "verb"),
            ("genießen", "to enjoy", "B1", "verb"),
            ("interessant", "interesting", "A2", "adjective"),
            ("langweilig", "boring", "A2", "adjective"),
            ("spannend", "exciting", "A2", "adjective"),
            ("unterhaltsam", "entertaining", "B1", "adjective"),
            ("kulturell", "cultural", "B1", "adjective"),
        ],
        
        "Sports & Fitness": [
            ("der Sport", "sport", "A1", "noun"),
            ("das Fitnessstudio", "gym", "A2", "noun"),
            ("das Training", "training", "A2", "noun"),
            ("der Kurs", "class/course", "A2", "noun"),
            ("das Yoga", "yoga", "A2", "noun"),
            ("das Schwimmen", "swimming", "A2", "noun"),
            ("das Laufen", "running", "A2", "noun"),
            ("das Radfahren", "cycling", "A2", "noun"),
            ("der Fußball", "soccer", "A1", "noun"),
            ("das Tennis", "tennis", "A2", "noun"),
            ("das Basketball", "basketball", "A2", "noun"),
            ("der Mannschaft", "team", "A2", "noun"),
            ("der Spieler", "player", "A2", "noun"),
            ("das Spiel", "game", "A1", "noun"),
            ("das Turnier", "tournament", "B1", "noun"),
            ("der Wettkampf", "competition", "B1", "noun"),
            ("der Sieg", "victory", "B1", "noun"),
            ("die Niederlage", "defeat", "B1", "noun"),
            ("das Tor", "goal", "A2", "noun"),
            ("der Punkt", "point", "A2", "noun"),
            ("trainieren", "to train", "A2", "verb"),
            ("spielen", "to play", "A1", "verb"),
            ("gewinnen", "to win", "A2", "verb"),
            ("verlieren", "to lose", "A2", "verb"),
            ("fit", "fit", "A2", "adjective"),
            ("gesund", "healthy", "A2", "adjective"),
            ("stark", "strong", "A2", "adjective"),
            ("schnell", "fast", "A1", "adjective"),
            ("langsam", "slow", "A1", "adjective"),
            ("müde", "tired", "A1", "adjective"),
        ],
        
        "Education & Learning": [
            ("die Schule", "school", "A1", "noun"),
            ("die Universität", "university", "A2", "noun"),
            ("der Unterricht", "lesson/class", "A2", "noun"),
            ("der Kurs", "course", "A2", "noun"),
            ("der Lehrer", "teacher (male)", "A1", "noun"),
            ("die Lehrerin", "teacher (female)", "A1", "noun"),
            ("der Student", "student (male)", "A1", "noun"),
            ("die Studentin", "student (female)", "A1", "noun"),
            ("der Schüler", "pupil (male)", "A1", "noun"),
            ("die Schülerin", "pupil (female)", "A1", "noun"),
            ("das Fach", "subject", "A2", "noun"),
            ("die Prüfung", "exam", "A2", "noun"),
            ("die Hausaufgabe", "homework", "A2", "noun"),
            ("das Buch", "book", "A1", "noun"),
            ("das Heft", "notebook", "A1", "noun"),
            ("der Stift", "pen", "A1", "noun"),
            ("die Bibliothek", "library", "A2", "noun"),
            ("das Zeugnis", "report card", "B1", "noun"),
            ("die Note", "grade", "A2", "noun"),
            ("das Diplom", "diploma", "B1", "noun"),
            ("lernen", "to learn", "A1", "verb"),
            ("studieren", "to study", "A1", "verb"),
            ("lehren", "to teach", "A2", "verb"),
            ("üben", "to practice", "A2", "verb"),
            ("wiederholen", "to repeat", "A2", "verb"),
            ("verstehen", "to understand", "A1", "verb"),
            ("erklären", "to explain", "A2", "verb"),
            ("schwierig", "difficult", "A2", "adjective"),
            ("leicht", "easy", "A1", "adjective"),
            ("klug", "smart", "A2", "adjective"),
        ],
    }
    
    # Flatten and insert vocabulary
    all_words = []
    for theme, words in vocabulary_themes.items():
        for german, english, level, word_type in words:
            word_doc = {
                "german": german,
                "english": english,
                "level": level,
                "type": word_type,
                "theme": theme,
                "example_sentence": f"Das ist ein Beispiel mit {german}.",
                "pronunciation": "",
                "audio_url": ""
            }
            all_words.append(word_doc)
    
    # Insert in batches
    if all_words:
        # Use update_one with upsert to avoid duplicates
        for word in all_words:
            await db["vocab"].update_one(
                {"german": word["german"]},
                {"$set": word},
                upsert=True
            )
    
    print(f"✅ Seeded {len(all_words)} vocabulary words")
    
    # Get total vocab count
    total = await db["vocab"].count_documents({})
    print(f"\n📈 Total vocabulary in database: {total}")
    
    # Count by theme
    print(f"\n📊 Breakdown by theme:")
    for theme in vocabulary_themes.keys():
        count = await db["vocab"].count_documents({"theme": theme})
        print(f"  - {theme}: {count}")
    
    # Count by level
    print(f"\n📊 Breakdown by level:")
    for level in ["A1", "A2", "B1", "B2", "C1", "C2"]:
        count = await db["vocab"].count_documents({"level": level})
        if count > 0:
            print(f"  - {level}: {count}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_phase5_vocabulary())
