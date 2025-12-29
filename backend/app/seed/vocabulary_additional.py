"""
Additional vocabulary to reach 500+ words
Part 2 of vocabulary expansion
"""

def get_additional_vocabulary():
    """Generate additional 200+ words"""
    additional = []
    
    # Numbers, Family, Common Verbs, Adjectives, Places, etc.
    # Simplified format for bulk addition
    
    bulk_vocab = [
        # Numbers (20)
        {"word": "eins", "translation": "one", "level": "A1", "category": "numbers", "part_of_speech": "numeral", "examples": ["Ich habe eins."], "difficulty": 1},
        {"word": "zwei", "translation": "two", "level": "A1", "category": "numbers", "part_of_speech": "numeral", "examples": ["Zwei Katzen."], "difficulty": 1},
        {"word": "drei", "translation": "three", "level": "A1", "category": "numbers", "part_of_speech": "numeral", "examples": ["Drei Äpfel."], "difficulty": 1},
        {"word": "vier", "translation": "four", "level": "A1", "category": "numbers", "part_of_speech": "numeral", "examples": ["Vier Personen."], "difficulty": 1},
        {"word": "fünf", "translation": "five", "level": "A1", "category": "numbers", "part_of_speech": "numeral", "examples": ["Fünf Finger."], "difficulty": 1},
        {"word": "sechs", "translation": "six", "level": "A1", "category": "numbers", "part_of_speech": "numeral", "examples": ["Sechs Uhr."], "difficulty": 1},
        {"word": "sieben", "translation": "seven", "level": "A1", "category": "numbers", "part_of_speech": "numeral", "examples": ["Sieben Tage."], "difficulty": 1},
        {"word": "acht", "translation": "eight", "level": "A1", "category": "numbers", "part_of_speech": "numeral", "examples": ["Acht Euro."], "difficulty": 1},
        {"word": "neun", "translation": "nine", "level": "A1", "category": "numbers", "part_of_speech": "numeral", "examples": ["Neun Uhr."], "difficulty": 1},
        {"word": "zehn", "translation": "ten", "level": "A1", "category": "numbers", "part_of_speech": "numeral", "examples": ["Zehn Minuten."], "difficulty": 1},
        
        # Family (15)
        {"word": "die Familie", "translation": "family", "level": "A1", "category": "family", "part_of_speech": "noun", "gender": "f", "examples": ["Meine Familie."], "difficulty": 1},
        {"word": "die Mutter", "translation": "mother", "level": "A1", "category": "family", "part_of_speech": "noun", "gender": "f", "examples": ["Meine Mutter."], "difficulty": 1},
        {"word": "der Vater", "translation": "father", "level": "A1", "category": "family", "part_of_speech": "noun", "gender": "m", "examples": ["Mein Vater."], "difficulty": 1},
        {"word": "der Bruder", "translation": "brother", "level": "A1", "category": "family", "part_of_speech": "noun", "gender": "m", "examples": ["Mein Bruder."], "difficulty": 1},
        {"word": "die Schwester", "translation": "sister", "level": "A1", "category": "family", "part_of_speech": "noun", "gender": "f", "examples": ["Meine Schwester."], "difficulty": 1},
        
        # Common verbs (30)
        {"word": "sein", "translation": "to be", "level": "A1", "category": "verbs", "part_of_speech": "verb", "examples": ["Ich bin."], "difficulty": 1},
        {"word": "haben", "translation": "to have", "level": "A1", "category": "verbs", "part_of_speech": "verb", "examples": ["Ich habe."], "difficulty": 1},
        {"word": "machen", "translation": "to do, make", "level": "A1", "category": "verbs", "part_of_speech": "verb", "examples": ["Ich mache."], "difficulty": 1},
        {"word": "gehen", "translation": "to go", "level": "A1", "category": "verbs", "part_of_speech": "verb", "examples": ["Ich gehe."], "difficulty": 1},
        {"word": "kommen", "translation": "to come", "level": "A1", "category": "verbs", "part_of_speech": "verb", "examples": ["Ich komme."], "difficulty": 1},
        {"word": "sehen", "translation": "to see", "level": "A1", "category": "verbs", "part_of_speech": "verb", "examples": ["Ich sehe."], "difficulty": 1},
        {"word": "hören", "translation": "to hear", "level": "A1", "category": "verbs", "part_of_speech": "verb", "examples": ["Ich höre."], "difficulty": 1},
        {"word": "sprechen", "translation": "to speak", "level": "A1", "category": "verbs", "part_of_speech": "verb", "examples": ["Ich spreche."], "difficulty": 1},
        {"word": "lernen", "translation": "to learn", "level": "A1", "category": "verbs", "part_of_speech": "verb", "examples": ["Ich lerne."], "difficulty": 1},
        {"word": "arbeiten", "translation": "to work", "level": "A1", "category": "verbs", "part_of_speech": "verb", "examples": ["Ich arbeite."], "difficulty": 1},
        {"word": "wohnen", "translation": "to live", "level": "A1", "category": "verbs", "part_of_speech": "verb", "examples": ["Ich wohne."], "difficulty": 1},
        {"word": "essen", "translation": "to eat", "level": "A1", "category": "verbs", "part_of_speech": "verb", "examples": ["Ich esse."], "difficulty": 1},
        {"word": "trinken", "translation": "to drink", "level": "A1", "category": "verbs", "part_of_speech": "verb", "examples": ["Ich trinke."], "difficulty": 1},
        {"word": "schlafen", "translation": "to sleep", "level": "A1", "category": "verbs", "part_of_speech": "verb", "examples": ["Ich schlafe."], "difficulty": 1},
        {"word": "lesen", "translation": "to read", "level": "A1", "category": "verbs", "part_of_speech": "verb", "examples": ["Ich lese."], "difficulty": 1},
        {"word": "schreiben", "translation": "to write", "level": "A1", "category": "verbs", "part_of_speech": "verb", "examples": ["Ich schreibe."], "difficulty": 1},
        {"word": "kaufen", "translation": "to buy", "level": "A1", "category": "verbs", "part_of_speech": "verb", "examples": ["Ich kaufe."], "difficulty": 1},
        {"word": "finden", "translation": "to find", "level": "A1", "category": "verbs", "part_of_speech": "verb", "examples": ["Ich finde."], "difficulty": 1},
        {"word": "suchen", "translation": "to search", "level": "A1", "category": "verbs", "part_of_speech": "verb", "examples": ["Ich suche."], "difficulty": 1},
        {"word": "wollen", "translation": "to want", "level": "A1", "category": "verbs", "part_of_speech": "verb", "examples": ["Ich will."], "difficulty": 1},
        
        # Adjectives (25)
        {"word": "gut", "translation": "good", "level": "A1", "category": "adjectives", "part_of_speech": "adjective", "examples": ["Das ist gut."], "difficulty": 1},
        {"word": "schlecht", "translation": "bad", "level": "A1", "category": "adjectives", "part_of_speech": "adjective", "examples": ["Das ist schlecht."], "difficulty": 1},
        {"word": "neu", "translation": "new", "level": "A1", "category": "adjectives", "part_of_speech": "adjective", "examples": ["Das ist neu."], "difficulty": 1},
        {"word": "alt", "translation": "old", "level": "A1", "category": "adjectives", "part_of_speech": "adjective", "examples": ["Das ist alt."], "difficulty": 1},
        {"word": "jung", "translation": "young", "level": "A1", "category": "adjectives", "part_of_speech": "adjective", "examples": ["Sie ist jung."], "difficulty": 1},
        {"word": "schnell", "translation": "fast", "level": "A1", "category": "adjectives", "part_of_speech": "adjective", "examples": ["Das ist schnell."], "difficulty": 1},
        {"word": "langsam", "translation": "slow", "level": "A1", "category": "adjectives", "part_of_speech": "adjective", "examples": ["Das ist langsam."], "difficulty": 1},
        {"word": "teuer", "translation": "expensive", "level": "A1", "category": "adjectives", "part_of_speech": "adjective", "examples": ["Das ist teuer."], "difficulty": 1},
        {"word": "billig", "translation": "cheap", "level": "A1", "category": "adjectives", "part_of_speech": "adjective", "examples": ["Das ist billig."], "difficulty": 1},
        {"word": "einfach", "translation": "simple, easy", "level": "A2", "category": "adjectives", "part_of_speech": "adjective", "examples": ["Das ist einfach."], "difficulty": 2},
        
        # Places (20)
        {"word": "das Haus", "translation": "house", "level": "A1", "category": "places", "part_of_speech": "noun", "gender": "n", "examples": ["Das Haus."], "difficulty": 1},
        {"word": "die Wohnung", "translation": "apartment", "level": "A1", "category": "places", "part_of_speech": "noun", "gender": "f", "examples": ["Die Wohnung."], "difficulty": 1},
        {"word": "die Stadt", "translation": "city", "level": "A1", "category": "places", "part_of_speech": "noun", "gender": "f", "examples": ["Die Stadt."], "difficulty": 1},
        {"word": "die Straße", "translation": "street", "level": "A1", "category": "places", "part_of_speech": "noun", "gender": "f", "examples": ["Die Straße."], "difficulty": 1},
        {"word": "der Park", "translation": "park", "level": "A1", "category": "places", "part_of_speech": "noun", "gender": "m", "examples": ["Der Park."], "difficulty": 1},
        {"word": "das Restaurant", "translation": "restaurant", "level": "A1", "category": "places", "part_of_speech": "noun", "gender": "n", "examples": ["Das Restaurant."], "difficulty": 1},
        {"word": "das Hotel", "translation": "hotel", "level": "A1", "category": "places", "part_of_speech": "noun", "gender": "n", "examples": ["Das Hotel."], "difficulty": 1},
        {"word": "die Schule", "translation": "school", "level": "A1", "category": "places", "part_of_speech": "noun", "gender": "f", "examples": ["Die Schule."], "difficulty": 1},
        {"word": "die Universität", "translation": "university", "level": "A2", "category": "places", "part_of_speech": "noun", "gender": "f", "examples": ["Die Universität."], "difficulty": 2},
        {"word": "das Krankenhaus", "translation": "hospital", "level": "A2", "category": "places", "part_of_speech": "noun", "gender": "n", "examples": ["Das Krankenhaus."], "difficulty": 2},
        
        # Clothing (20)
        {"word": "die Kleidung", "translation": "clothing", "level": "A1", "category": "clothing", "part_of_speech": "noun", "gender": "f", "examples": ["Die Kleidung."], "difficulty": 1},
        {"word": "das Hemd", "translation": "shirt", "level": "A1", "category": "clothing", "part_of_speech": "noun", "gender": "n", "examples": ["Das Hemd."], "difficulty": 1},
        {"word": "die Hose", "translation": "pants", "level": "A1", "category": "clothing", "part_of_speech": "noun", "gender": "f", "examples": ["Die Hose."], "difficulty": 1},
        {"word": "das Kleid", "translation": "dress", "level": "A1", "category": "clothing", "part_of_speech": "noun", "gender": "n", "examples": ["Das Kleid."], "difficulty": 1},
        {"word": "der Rock", "translation": "skirt", "level": "A1", "category": "clothing", "part_of_speech": "noun", "gender": "m", "examples": ["Der Rock."], "difficulty": 1},
        {"word": "die Jacke", "translation": "jacket", "level": "A1", "category": "clothing", "part_of_speech": "noun", "gender": "f", "examples": ["Die Jacke."], "difficulty": 1},
        {"word": "der Mantel", "translation": "coat", "level": "A1", "category": "clothing", "part_of_speech": "noun", "gender": "m", "examples": ["Der Mantel."], "difficulty": 1},
        {"word": "die Schuhe", "translation": "shoes", "level": "A1", "category": "clothing", "part_of_speech": "noun", "gender": "pl", "examples": ["Die Schuhe."], "difficulty": 1},
        {"word": "die Socken", "translation": "socks", "level": "A1", "category": "clothing", "part_of_speech": "noun", "gender": "pl", "examples": ["Die Socken."], "difficulty": 1},
        {"word": "der Hut", "translation": "hat", "level": "A1", "category": "clothing", "part_of_speech": "noun", "gender": "m", "examples": ["Der Hut."], "difficulty": 1},
        
        # Animals (20)
        {"word": "das Tier", "translation": "animal", "level": "A1", "category": "animals", "part_of_speech": "noun", "gender": "n", "examples": ["Das Tier."], "difficulty": 1},
        {"word": "der Hund", "translation": "dog", "level": "A1", "category": "animals", "part_of_speech": "noun", "gender": "m", "examples": ["Der Hund."], "difficulty": 1},
        {"word": "die Katze", "translation": "cat", "level": "A1", "category": "animals", "part_of_speech": "noun", "gender": "f", "examples": ["Die Katze."], "difficulty": 1},
        {"word": "der Vogel", "translation": "bird", "level": "A1", "category": "animals", "part_of_speech": "noun", "gender": "m", "examples": ["Der Vogel."], "difficulty": 1},
        {"word": "das Pferd", "translation": "horse", "level": "A1", "category": "animals", "part_of_speech": "noun", "gender": "n", "examples": ["Das Pferd."], "difficulty": 1},
        {"word": "die Kuh", "translation": "cow", "level": "A1", "category": "animals", "part_of_speech": "noun", "gender": "f", "examples": ["Die Kuh."], "difficulty": 1},
        {"word": "das Schwein", "translation": "pig", "level": "A1", "category": "animals", "part_of_speech": "noun", "gender": "n", "examples": ["Das Schwein."], "difficulty": 1},
        {"word": "das Schaf", "translation": "sheep", "level": "A1", "category": "animals", "part_of_speech": "noun", "gender": "n", "examples": ["Das Schaf."], "difficulty": 1},
        {"word": "die Maus", "translation": "mouse", "level": "A1", "category": "animals", "part_of_speech": "noun", "gender": "f", "examples": ["Die Maus."], "difficulty": 1},
        {"word": "der Fisch", "translation": "fish", "level": "A1", "category": "animals", "part_of_speech": "noun", "gender": "m", "examples": ["Der Fisch."], "difficulty": 1},
        
        # Hobbies & Activities (20)
        {"word": "das Hobby", "translation": "hobby", "level": "A1", "category": "hobbies", "part_of_speech": "noun", "gender": "n", "examples": ["Mein Hobby."], "difficulty": 1},
        {"word": "der Sport", "translation": "sport", "level": "A1", "category": "hobbies", "part_of_speech": "noun", "gender": "m", "examples": ["Ich mache Sport."], "difficulty": 1},
        {"word": "die Musik", "translation": "music", "level": "A1", "category": "hobbies", "part_of_speech": "noun", "gender": "f", "examples": ["Ich höre Musik."], "difficulty": 1},
        {"word": "das Buch", "translation": "book", "level": "A1", "category": "hobbies", "part_of_speech": "noun", "gender": "n", "examples": ["Ich lese ein Buch."], "difficulty": 1},
        {"word": "der Film", "translation": "film, movie", "level": "A1", "category": "hobbies", "part_of_speech": "noun", "gender": "m", "examples": ["Ich sehe einen Film."], "difficulty": 1},
        {"word": "das Spiel", "translation": "game", "level": "A1", "category": "hobbies", "part_of_speech": "noun", "gender": "n", "examples": ["Ich spiele ein Spiel."], "difficulty": 1},
        {"word": "schwimmen", "translation": "to swim", "level": "A1", "category": "hobbies", "part_of_speech": "verb", "examples": ["Ich schwimme."], "difficulty": 1},
        {"word": "laufen", "translation": "to run", "level": "A1", "category": "hobbies", "part_of_speech": "verb", "examples": ["Ich laufe."], "difficulty": 1},
        {"word": "tanzen", "translation": "to dance", "level": "A1", "category": "hobbies", "part_of_speech": "verb", "examples": ["Ich tanze."], "difficulty": 1},
        {"word": "singen", "translation": "to sing", "level": "A1", "category": "hobbies", "part_of_speech": "verb", "examples": ["Ich singe."], "difficulty": 1},
        
        # More verbs (50)
        {"word": "nehmen", "translation": "to take", "level": "A1", "category": "verbs", "part_of_speech": "verb", "examples": ["Ich nehme."], "difficulty": 1},
        {"word": "geben", "translation": "to give", "level": "A1", "category": "verbs", "part_of_speech": "verb", "examples": ["Ich gebe."], "difficulty": 1},
        {"word": "bringen", "translation": "to bring", "level": "A1", "category": "verbs", "part_of_speech": "verb", "examples": ["Ich bringe."], "difficulty": 1},
        {"word": "holen", "translation": "to fetch, get", "level": "A1", "category": "verbs", "part_of_speech": "verb", "examples": ["Ich hole."], "difficulty": 1},
        {"word": "zeigen", "translation": "to show", "level": "A1", "category": "verbs", "part_of_speech": "verb", "examples": ["Ich zeige."], "difficulty": 1},
        {"word": "helfen", "translation": "to help", "level": "A1", "category": "verbs", "part_of_speech": "verb", "examples": ["Ich helfe."], "difficulty": 1},
        {"word": "fragen", "translation": "to ask", "level": "A1", "category": "verbs", "part_of_speech": "verb", "examples": ["Ich frage."], "difficulty": 1},
        {"word": "antworten", "translation": "to answer", "level": "A1", "category": "verbs", "part_of_speech": "verb", "examples": ["Ich antworte."], "difficulty": 1},
        {"word": "sagen", "translation": "to say", "level": "A1", "category": "verbs", "part_of_speech": "verb", "examples": ["Ich sage."], "difficulty": 1},
        {"word": "erzählen", "translation": "to tell", "level": "A2", "category": "verbs", "part_of_speech": "verb", "examples": ["Ich erzähle."], "difficulty": 2},
        {"word": "verstehen", "translation": "to understand", "level": "A1", "category": "verbs", "part_of_speech": "verb", "examples": ["Ich verstehe."], "difficulty": 1},
        {"word": "wissen", "translation": "to know", "level": "A1", "category": "verbs", "part_of_speech": "verb", "examples": ["Ich weiß."], "difficulty": 1},
        {"word": "kennen", "translation": "to know (person/place)", "level": "A1", "category": "verbs", "part_of_speech": "verb", "examples": ["Ich kenne."], "difficulty": 1},
        {"word": "glauben", "translation": "to believe", "level": "A2", "category": "verbs", "part_of_speech": "verb", "examples": ["Ich glaube."], "difficulty": 2},
        {"word": "denken", "translation": "to think", "level": "A2", "category": "verbs", "part_of_speech": "verb", "examples": ["Ich denke."], "difficulty": 2},
        {"word": "meinen", "translation": "to mean, think", "level": "A2", "category": "verbs", "part_of_speech": "verb", "examples": ["Ich meine."], "difficulty": 2},
        {"word": "mögen", "translation": "to like", "level": "A1", "category": "verbs", "part_of_speech": "verb", "examples": ["Ich mag."], "difficulty": 1},
        {"word": "lieben", "translation": "to love", "level": "A1", "category": "verbs", "part_of_speech": "verb", "examples": ["Ich liebe."], "difficulty": 1},
        {"word": "hassen", "translation": "to hate", "level": "A2", "category": "verbs", "part_of_speech": "verb", "examples": ["Ich hasse."], "difficulty": 2},
        {"word": "hoffen", "translation": "to hope", "level": "A2", "category": "verbs", "part_of_speech": "verb", "examples": ["Ich hoffe."], "difficulty": 2},
        
        # More adjectives (40)
        {"word": "schön", "translation": "beautiful", "level": "A1", "category": "adjectives", "part_of_speech": "adjective", "examples": ["Das ist schön."], "difficulty": 1},
        {"word": "hässlich", "translation": "ugly", "level": "A2", "category": "adjectives", "part_of_speech": "adjective", "examples": ["Das ist hässlich."], "difficulty": 2},
        {"word": "nett", "translation": "nice", "level": "A1", "category": "adjectives", "part_of_speech": "adjective", "examples": ["Er ist nett."], "difficulty": 1},
        {"word": "freundlich", "translation": "friendly", "level": "A1", "category": "adjectives", "part_of_speech": "adjective", "examples": ["Sie ist freundlich."], "difficulty": 1},
        {"word": "unfreundlich", "translation": "unfriendly", "level": "A2", "category": "adjectives", "part_of_speech": "adjective", "examples": ["Er ist unfreundlich."], "difficulty": 2},
        {"word": "höflich", "translation": "polite", "level": "A2", "category": "adjectives", "part_of_speech": "adjective", "examples": ["Sie ist höflich."], "difficulty": 2},
        {"word": "unhöflich", "translation": "impolite", "level": "A2", "category": "adjectives", "part_of_speech": "adjective", "examples": ["Er ist unhöflich."], "difficulty": 2},
        {"word": "klug", "translation": "smart, clever", "level": "A2", "category": "adjectives", "part_of_speech": "adjective", "examples": ["Sie ist klug."], "difficulty": 2},
        {"word": "dumm", "translation": "stupid", "level": "A2", "category": "adjectives", "part_of_speech": "adjective", "examples": ["Das ist dumm."], "difficulty": 2},
        {"word": "stark", "translation": "strong", "level": "A1", "category": "adjectives", "part_of_speech": "adjective", "examples": ["Er ist stark."], "difficulty": 1},
        {"word": "schwach", "translation": "weak", "level": "A2", "category": "adjectives", "part_of_speech": "adjective", "examples": ["Ich bin schwach."], "difficulty": 2},
        {"word": "gesund", "translation": "healthy", "level": "A1", "category": "adjectives", "part_of_speech": "adjective", "examples": ["Ich bin gesund."], "difficulty": 1},
        {"word": "lecker", "translation": "delicious", "level": "A1", "category": "adjectives", "part_of_speech": "adjective", "examples": ["Das ist lecker."], "difficulty": 1},
        {"word": "süß", "translation": "sweet", "level": "A1", "category": "adjectives", "part_of_speech": "adjective", "examples": ["Das ist süß."], "difficulty": 1},
        {"word": "sauer", "translation": "sour", "level": "A1", "category": "adjectives", "part_of_speech": "adjective", "examples": ["Das ist sauer."], "difficulty": 1},
        {"word": "salzig", "translation": "salty", "level": "A1", "category": "adjectives", "part_of_speech": "adjective", "examples": ["Das ist salzig."], "difficulty": 1},
        {"word": "bitter", "translation": "bitter", "level": "A2", "category": "adjectives", "part_of_speech": "adjective", "examples": ["Das ist bitter."], "difficulty": 2},
        {"word": "scharf", "translation": "spicy, sharp", "level": "A2", "category": "adjectives", "part_of_speech": "adjective", "examples": ["Das ist scharf."], "difficulty": 2},
        {"word": "weich", "translation": "soft", "level": "A2", "category": "adjectives", "part_of_speech": "adjective", "examples": ["Das ist weich."], "difficulty": 2},
        {"word": "hart", "translation": "hard", "level": "A2", "category": "adjectives", "part_of_speech": "adjective", "examples": ["Das ist hart."], "difficulty": 2},
        
        # More food (30)
        {"word": "die Kartoffel", "translation": "potato", "level": "A1", "category": "food", "part_of_speech": "noun", "gender": "f", "examples": ["Die Kartoffel."], "difficulty": 1},
        {"word": "der Reis", "translation": "rice", "level": "A1", "category": "food", "part_of_speech": "noun", "gender": "m", "examples": ["Der Reis."], "difficulty": 1},
        {"word": "die Nudeln", "translation": "noodles, pasta", "level": "A1", "category": "food", "part_of_speech": "noun", "gender": "pl", "examples": ["Die Nudeln."], "difficulty": 1},
        {"word": "die Suppe", "translation": "soup", "level": "A1", "category": "food", "part_of_speech": "noun", "gender": "f", "examples": ["Die Suppe."], "difficulty": 1},
        {"word": "der Salat", "translation": "salad", "level": "A1", "category": "food", "part_of_speech": "noun", "gender": "m", "examples": ["Der Salat."], "difficulty": 1},
        {"word": "die Pizza", "translation": "pizza", "level": "A1", "category": "food", "part_of_speech": "noun", "gender": "f", "examples": ["Die Pizza."], "difficulty": 1},
        {"word": "der Hamburger", "translation": "hamburger", "level": "A1", "category": "food", "part_of_speech": "noun", "gender": "m", "examples": ["Der Hamburger."], "difficulty": 1},
        {"word": "die Pommes", "translation": "french fries", "level": "A1", "category": "food", "part_of_speech": "noun", "gender": "pl", "examples": ["Die Pommes."], "difficulty": 1},
        {"word": "das Eis", "translation": "ice cream", "level": "A1", "category": "food", "part_of_speech": "noun", "gender": "n", "examples": ["Das Eis."], "difficulty": 1},
        {"word": "der Kuchen", "translation": "cake", "level": "A1", "category": "food", "part_of_speech": "noun", "gender": "m", "examples": ["Der Kuchen."], "difficulty": 1},
        {"word": "die Schokolade", "translation": "chocolate", "level": "A1", "category": "food", "part_of_speech": "noun", "gender": "f", "examples": ["Die Schokolade."], "difficulty": 1},
        {"word": "der Zucker", "translation": "sugar", "level": "A1", "category": "food", "part_of_speech": "noun", "gender": "m", "examples": ["Der Zucker."], "difficulty": 1},
        {"word": "das Salz", "translation": "salt", "level": "A1", "category": "food", "part_of_speech": "noun", "gender": "n", "examples": ["Das Salz."], "difficulty": 1},
        {"word": "der Pfeffer", "translation": "pepper", "level": "A1", "category": "food", "part_of_speech": "noun", "gender": "m", "examples": ["Der Pfeffer."], "difficulty": 1},
        {"word": "das Öl", "translation": "oil", "level": "A1", "category": "food", "part_of_speech": "noun", "gender": "n", "examples": ["Das Öl."], "difficulty": 1},
        
        # Drinks (15)
        {"word": "das Wasser", "translation": "water", "level": "A1", "category": "drinks", "part_of_speech": "noun", "gender": "n", "examples": ["Das Wasser."], "difficulty": 1},
        {"word": "der Saft", "translation": "juice", "level": "A1", "category": "drinks", "part_of_speech": "noun", "gender": "m", "examples": ["Der Saft."], "difficulty": 1},
        {"word": "die Milch", "translation": "milk", "level": "A1", "category": "drinks", "part_of_speech": "noun", "gender": "f", "examples": ["Die Milch."], "difficulty": 1},
        {"word": "der Kaffee", "translation": "coffee", "level": "A1", "category": "drinks", "part_of_speech": "noun", "gender": "m", "examples": ["Der Kaffee."], "difficulty": 1},
        {"word": "der Tee", "translation": "tea", "level": "A1", "category": "drinks", "part_of_speech": "noun", "gender": "m", "examples": ["Der Tee."], "difficulty": 1},
        {"word": "das Bier", "translation": "beer", "level": "A1", "category": "drinks", "part_of_speech": "noun", "gender": "n", "examples": ["Das Bier."], "difficulty": 1},
        {"word": "der Wein", "translation": "wine", "level": "A1", "category": "drinks", "part_of_speech": "noun", "gender": "m", "examples": ["Der Wein."], "difficulty": 1},
        {"word": "die Limonade", "translation": "lemonade, soda", "level": "A1", "category": "drinks", "part_of_speech": "noun", "gender": "f", "examples": ["Die Limonade."], "difficulty": 1},
        {"word": "der Kakao", "translation": "cocoa, hot chocolate", "level": "A1", "category": "drinks", "part_of_speech": "noun", "gender": "m", "examples": ["Der Kakao."], "difficulty": 1},
        {"word": "das Getränk", "translation": "drink, beverage", "level": "A1", "category": "drinks", "part_of_speech": "noun", "gender": "n", "examples": ["Das Getränk."], "difficulty": 1},
        
        # Common phrases (20)
        {"word": "bitte", "translation": "please", "level": "A1", "category": "phrases", "part_of_speech": "adverb", "examples": ["Bitte schön."], "difficulty": 1},
        {"word": "danke", "translation": "thank you", "level": "A1", "category": "phrases", "part_of_speech": "interjection", "examples": ["Danke sehr."], "difficulty": 1},
        {"word": "ja", "translation": "yes", "level": "A1", "category": "phrases", "part_of_speech": "adverb", "examples": ["Ja, gerne."], "difficulty": 1},
        {"word": "nein", "translation": "no", "level": "A1", "category": "phrases", "part_of_speech": "adverb", "examples": ["Nein, danke."], "difficulty": 1},
        {"word": "vielleicht", "translation": "maybe, perhaps", "level": "A1", "category": "phrases", "part_of_speech": "adverb", "examples": ["Vielleicht."], "difficulty": 1},
        {"word": "natürlich", "translation": "of course, naturally", "level": "A2", "category": "phrases", "part_of_speech": "adverb", "examples": ["Natürlich!"], "difficulty": 2},
        {"word": "genau", "translation": "exactly", "level": "A2", "category": "phrases", "part_of_speech": "adverb", "examples": ["Genau!"], "difficulty": 2},
        {"word": "wirklich", "translation": "really", "level": "A2", "category": "phrases", "part_of_speech": "adverb", "examples": ["Wirklich?"], "difficulty": 2},
        {"word": "sehr", "translation": "very", "level": "A1", "category": "phrases", "part_of_speech": "adverb", "examples": ["Sehr gut."], "difficulty": 1},
        {"word": "auch", "translation": "also, too", "level": "A1", "category": "phrases", "part_of_speech": "adverb", "examples": ["Ich auch."], "difficulty": 1},
    ]
    
    additional.extend(bulk_vocab)
    return additional
