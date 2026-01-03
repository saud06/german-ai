"""
Comprehensive Learning Paths Seed Script
Creates 10-15 chapters per CEFR level for Student journey
and 10-15 chapters per difficulty for other journeys
"""

import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os

# MongoDB connection
MONGODB_URL = os.getenv("MONGODB_URI", "mongodb+srv://saud:A20WJXcybOc2aAgb@cluster0.8hmnx1o.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DB_NAME = os.getenv("MONGODB_DB_NAME", "german_ai")

async def seed_comprehensive_learning_paths():
    """Seed comprehensive learning paths for all levels"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DB_NAME]
    
    print("🗺️ Seeding comprehensive learning paths...")
    print("=" * 50)
    
    # Clear existing learning paths
    await db.learning_paths.delete_many({})
    print("🗑️ Cleared existing learning paths")
    
    learning_paths = []
    
    # Student Journey - CEFR Levels (A1, A2, B1, B2, C1)
    student_paths = {
        "A1": [
            {"chapter": 1, "title": "Ankunft in Deutschland", "description": "Your first day in Germany - basic greetings and introductions", "story": "You've just arrived in Germany. Your first challenge is to introduce yourself and understand basic directions."},
            {"chapter": 2, "title": "Im Café", "description": "Ordering coffee and pastries, understanding prices", "story": "You're hungry and need to order food. Learn to ask for coffee and understand the menu."},
            {"chapter": 3, "title": "Einkaufen", "description": "Shopping for groceries and basic items", "story": "Your fridge is empty. Time to go shopping and learn numbers and food vocabulary."},
            {"chapter": 4, "title": "Die Wohnung", "description": "Describing your apartment and furniture", "story": "You need to describe your new apartment. Learn furniture and room vocabulary."},
            {"chapter": 5, "title": "Unterwegs", "description": "Using public transport and asking for directions", "story": "You're lost in the city. Learn to ask for and understand directions."},
            {"chapter": 6, "title": "Im Restaurant", "description": "Dining out and understanding menus", "story": "You're hungry for a proper meal. Learn restaurant vocabulary and ordering."},
            {"chapter": 7, "title": "Die Familie", "description": "Talking about family members and relationships", "story": "You meet new people and want to talk about your family."},
            {"chapter": 8, "title": "Das Wetter", "description": "Discussing weather and seasons", "story": "Planning your week? Learn to talk about weather and make plans."},
            {"chapter": 9, "title": "Die Zeit", "description": "Telling time and making appointments", "story": "You need to schedule meetings. Learn to tell time and make appointments."},
            {"chapter": 10, "title": "Farben und Kleidung", "description": "Describing colors and clothing", "story": "Going shopping for clothes. Learn colors and clothing vocabulary."},
            {"chapter": 11, "title": "Hobbys", "description": "Talking about hobbies and free time", "story": "Making new friends and discussing what you like to do."},
            {"chapter": 12, "title": "Am Telefon", "description": "Making phone calls and leaving messages", "story": "You need to call someone. Learn phone etiquette and basic phrases."},
        ],
        "A2": [
            {"chapter": 1, "title": "Arbeitssuche", "description": "Job hunting and writing basic CV", "story": "You need a job. Learn to talk about your skills and experience."},
            {"chapter": 2, "title": "Beim Arzt", "description": "Doctor visits and describing symptoms", "story": "You're not feeling well. Learn to describe symptoms and understand medical advice."},
            {"chapter": 3, "title": "Bankgeschäfte", "description": "Opening bank account and basic transactions", "story": "You need to manage your money. Learn banking vocabulary and procedures."},
            {"chapter": 4, "title": "Postamt", "description": "Sending mail and packages", "story": "You need to send a package home. Learn postal vocabulary."},
            {"chapter": 5, "title": "Wohnungssuche", "description": "Finding and renting an apartment", "story": "You need a better place to live. Learn apartment hunting vocabulary."},
            {"chapter": 6, "title": "Fitnessstudio", "description": "Joining a gym and discussing exercise", "story": "You want to stay fit. Learn gym and exercise vocabulary."},
            {"chapter": 7, "title": "Bibliothek", "description": "Using library services", "story": "You want to borrow books. Learn library vocabulary and procedures."},
            {"chapter": 8, "title": "Friseur", "description": "Getting a haircut and describing styles", "story": "You need a haircut. Learn to describe hairstyles and salon vocabulary."},
            {"chapter": 9, "title": "Kino", "description": "Going to movies and discussing films", "story": "You want to watch a movie. Learn cinema and film vocabulary."},
            {"chapter": 10, "title": "Beschwerden", "description": "Making complaints and resolving issues", "story": "Something is wrong. Learn to make polite complaints."},
            {"chapter": 11, "title": "Versicherung", "description": "Understanding insurance policies", "story": "You need insurance. Learn insurance vocabulary and concepts."},
            {"chapter": 12, "title": "Autoreparatur", "description": "Car problems and repairs", "story": "Your car broke down. Learn car repair vocabulary."},
        ],
        "B1": [
            {"chapter": 1, "title": "Vorstellungsgespräch", "description": "Job interviews and professional introductions", "story": "You have a job interview! Learn professional German and interview skills."},
            {"chapter": 2, "title": "Geschäftstreffen", "description": "Business meetings and presentations", "story": "You have an important meeting. Learn business German and presentation skills."},
            {"chapter": 3, "title": "Mietvertrag", "description": "Understanding rental contracts and rights", "story": "You're signing a lease. Learn legal vocabulary and tenant rights."},
            {"chapter": 4, "title": "Arzttermin", "description": "Making doctor appointments by phone", "story": "You need to schedule appointments. Learn phone skills and medical vocabulary."},
            {"chapter": 5, "title": "Nachbarschaft", "description": "Resolving conflicts with neighbors", "story": "Neighbor issues? Learn conflict resolution and polite German."},
            {"chapter": 6, "title": "Behördengang", "description": "Dealing with government offices", "story": "Paperwork at the Bürgeramt. Learn bureaucratic German and procedures."},
            {"chapter": 7, "title": "Kunstausstellung", "description": "Discussing art and culture", "story": "Visiting an art gallery. Learn art vocabulary and cultural discussion."},
            {"chapter": 8, "title": "Politische Diskussion", "description": "Discussing current events and politics", "story": "Talking about current affairs. Learn political vocabulary and debate skills."},
            {"chapter": 9, "title": "Gesundheitsberatung", "description": "Health consultations and advice", "story": "Health check-up. Learn detailed medical vocabulary and health discussions."},
            {"chapter": 10, "title": "Finanzberatung", "description": "Financial planning and investments", "story": "Meeting a financial advisor. Learn banking and investment vocabulary."},
            {"chapter": 11, "title": "Vereinsleben", "description": "Joining clubs and organizations", "story": "Joining a local club. Learn social vocabulary and club culture."},
            {"chapter": 12, "title": "Reiseplanung", "description": "Planning complex travel itineraries", "story": "Planning a big trip. Learn travel planning vocabulary and complex arrangements."},
            {"chapter": 13, "title": "Umweltschutz", "description": "Environmental discussions and activism", "story": "Environmental concerns. Learn ecology vocabulary and discussion skills."},
            {"chapter": 14, "title": "Technischer Support", "description": "Technical support and troubleshooting", "story": "Computer problems! Learn technical vocabulary and support conversations."},
            {"chapter": 15, "title": "Elternabend", "description": "Parent-teacher meetings", "story": "Meeting your child's teacher. Learn educational vocabulary and formal discussions."},
        ],
        "B2": [
            {"chapter": 1, "title": "Vertragsverhandlungen", "description": "Negotiating contracts and agreements", "story": "Business negotiations. Learn formal German and negotiation skills."},
            {"chapter": 2, "title": "Wissenschaftliche Diskussion", "description": "Academic and scientific discussions", "story": "University seminar. Learn academic German and scientific vocabulary."},
            {"chapter": 3, "title": "Medizinische Diagnose", "description": "Understanding medical diagnoses", "story": "Complex medical situation. Learn advanced medical vocabulary."},
            {"chapter": 4, "title": "Rechtsberatung", "description": "Legal consultations and advice", "story": "Legal matters. Learn legal vocabulary and formal procedures."},
            {"chapter": 5, "title": "Unternehmensgründung", "description": "Starting a business in Germany", "story": "Starting your own company. Learn business German and entrepreneurship."},
            {"chapter": 6, "title": "Kulturelle Integration", "description": "Deep cultural understanding and integration", "story": "Cultural immersion. Learn nuanced cultural expressions and idioms."},
            {"chapter": 7, "title": "Medienanalyse", "description": "Analyzing media and news", "story": "Media literacy. Learn to analyze German media and news."},
            {"chapter": 8, "title": "Philosophische Debatten", "description": "Philosophical discussions and debates", "story": "Deep conversations. Learn abstract vocabulary and philosophical concepts."},
            {"chapter": 9, "title": "Historische Kontexte", "description": "Understanding German history and context", "story": "Historical discussions. Learn historical vocabulary and context."},
            {"chapter": 10, "title": "Literarische Analyse", "description": "Analyzing German literature", "story": "Book club discussion. Learn literary analysis and criticism."},
            {"chapter": 11, "title": "Wirtschaftspolitik", "description": "Economic policy discussions", "story": "Economic forum. Learn economics and policy vocabulary."},
            {"chapter": 12, "title": "Soziale Integration", "description": "Social integration and community building", "story": "Community involvement. Learn social integration vocabulary."},
        ],
        "C1": [
            {"chapter": 1, "title": "Akademische Forschung", "description": "Conducting academic research", "story": "Research project. Learn academic German and research methodology."},
            {"chapter": 2, "title": "Politische Reden", "description": "Writing and delivering speeches", "story": "Public speaking. Learn rhetorical devices and formal speech."},
            {"chapter": 3, "title": "Literarische Kreativität", "description": "Creative writing and expression", "story": "Writing workshop. Learn creative writing and literary expression."},
            {"chapter": 4, "title": "Wissenschaftliche Publikation", "description": "Publishing research papers", "story": "Academic publishing. Learn scientific writing and publication."},
            {"chapter": 5, "title": "Internationale Diplomatie", "description": "Diplomatic negotiations and discussions", "story": "Diplomatic mission. Learn diplomatic language and international relations."},
            {"chapter": 6, "title": "Kulturelle Kritik", "description": "Cultural criticism and analysis", "story": "Cultural criticism. Learn advanced cultural analysis vocabulary."},
            {"chapter": 7, "title": "Philosophische Texte", "description": "Reading and analyzing philosophy", "story": "Philosophy seminar. Learn complex philosophical vocabulary."},
            {"chapter": 8, "title": "Medienproduktion", "description": "Creating media content", "story": "Media production. Learn media creation and production vocabulary."},
            {"chapter": 9, "title": "Sozialwissenschaftliche Analyse", "description": "Social science research", "story": "Social research. Learn social science vocabulary and methodology."},
            {"chapter": 10, "title": "Künstlerische Expression", "description": "Advanced artistic expression", "story": "Art exhibition. Learn advanced artistic vocabulary and expression."},
        ]
    }
    
    # Other Journeys - Difficulty Levels (Beginner, Intermediate, Advanced)
    other_paths = {
        "Beginner": [
            {"chapter": 1, "title": "Erste Schritte", "description": "Basic survival German", "story": "Starting your German journey with essential phrases."},
            {"chapter": 2, "title": "Alltagssituationen", "description": "Daily life situations", "story": "Handling everyday situations in German."},
            {"chapter": 3, "title": "Einkaufen gehen", "description": "Shopping and numbers", "story": "Shopping for daily needs."},
            {"chapter": 4, "title": "Im Restaurant", "description": "Dining out basics", "story": "Eating out and ordering food."},
            {"chapter": 5, "title": "Unterwegs", "description": "Transportation and directions", "story": "Getting around in German-speaking areas."},
            {"chapter": 6, "title": "Kleine Gespräche", "description": "Basic small talk", "story": "Making simple conversations."},
            {"chapter": 7, "title": "Wohnen", "description": "Housing and furniture", "story": "Talking about where you live."},
            {"chapter": 8, "title": "Freizeit", "description": "Hobbies and free time", "story": "Discussing leisure activities."},
            {"chapter": 9, "title": "Gesundheit", "description": "Basic health expressions", "story": "Talking about health and feelings."},
            {"chapter": 10, "title": "Arbeit", "description": "Basic work vocabulary", "story": "Talking about jobs and work."},
        ],
        "Intermediate": [
            {"chapter": 1, "title": "Berufsleben", "description": "Work and career discussions", "story": "Advancing in your career with German."},
            {"chapter": 2, "title": "Soziale Beziehungen", "description": "Building relationships", "story": "Making friends and social connections."},
            {"chapter": 3, "title": "Kultur und Traditionen", "description": "Cultural understanding", "story": "Exploring German culture and traditions."},
            {"chapter": 4, "title": "Reisen und Tourismus", "description": "Travel planning and experiences", "story": "Planning and experiencing travel."},
            {"chapter": 5, "title": "Medien und Kommunikation", "description": "Media and communication", "story": "Engaging with German media."},
            {"chapter": 6, "title": "Bildungswesen", "description": "Education system", "story": "Understanding German education."},
            {"chapter": 7, "title": "Wirtschaft und Finanzen", "description": "Economic topics", "story": "Discussing economic matters."},
            {"chapter": 8, "title": "Technologie und Innovation", "description": "Technology discussions", "story": "Talking about technology and innovation."},
            {"chapter": 9, "title": "Umwelt und Nachhaltigkeit", "description": "Environmental topics", "story": "Discussing environmental issues."},
            {"chapter": 10, "title": "Gesellschaft und Politik", "description": "Social and political topics", "story": "Understanding society and politics."},
        ],
        "Advanced": [
            {"chapter": 1, "title": "Akademische Welt", "description": "Academic and intellectual discussions", "story": "Engaging in academic discourse."},
            {"chapter": 2, "title": "Professionelle Kommunikation", "description": "Professional communication", "story": "Mastering professional German."},
            {"chapter": 3, "title": "Kulturelle Tiefe", "description": "Deep cultural analysis", "story": "Deep understanding of German culture."},
            {"chapter": 4, "title": "Wissenschaftliche Debatten", "description": "Scientific discussions", "story": "Participating in scientific debates."},
            {"chapter": 5, "title": "Literarische Diskussionen", "description": "Literary analysis and discussion", "story": "Analyzing German literature."},
            {"chapter": 6, "title": "Philosophische Reflexionen", "description": "Philosophical discussions", "story": "Engaging in philosophical discourse."},
            {"chapter": 7, "title": "Historische Analysen", "description": "Historical analysis", "story": "Understanding German history deeply."},
            {"chapter": 8, "title": "Künstlerische Ausdrucksformen", "description": "Artistic expression", "story": "Expressing artistic concepts."},
            {"chapter": 9, "title": "Internationale Beziehungen", "description": "International relations", "story": "Discussing global matters in German."},
            {"chapter": 10, "title": "Innovation und Zukunft", "description": "Future and innovation", "story": "Discussing future trends and innovations."},
        ]
    }
    
    # Create Student Journey paths (CEFR levels)
    for level, chapters in student_paths.items():
        for chapter_data in chapters:
            path = {
                "_id": ObjectId(),
                "chapter": chapter_data["chapter"],
                "level": level,
                "title": chapter_data["title"],
                "description": chapter_data["description"],
                "story": chapter_data["story"],
                "image": f"/images/learning-paths/{level.lower()}-chapter-{chapter_data['chapter']}.jpg",
                "locations": [],
                "characters": [],
                "estimated_hours": 3 + (chapter_data["chapter"] * 0.5),
                "completion_reward": {
                    "xp": 100 * chapter_data["chapter"],
                    "badge": f"{level}_chapter_{chapter_data['chapter']}",
                    "unlock": f"{level}_chapter_{chapter_data['chapter'] + 1}" if chapter_data["chapter"] < len(chapters) else None
                },
                "unlock_requirements": {} if chapter_data["chapter"] == 1 else {"min_xp": 100 * (chapter_data["chapter"] - 1)},
                "created_at": datetime.utcnow(),
                "journey_type": "student"
            }
            learning_paths.append(path)
    
    # Create Other Journey paths (Difficulty levels)
    for level, chapters in other_paths.items():
        for chapter_data in chapters:
            path = {
                "_id": ObjectId(),
                "chapter": chapter_data["chapter"],
                "level": level,
                "title": chapter_data["title"],
                "description": chapter_data["description"],
                "story": chapter_data["story"],
                "image": f"/images/learning-paths/{level.lower()}-chapter-{chapter_data['chapter']}.jpg",
                "locations": [],
                "characters": [],
                "estimated_hours": 2 + (chapter_data["chapter"] * 0.3),
                "completion_reward": {
                    "xp": 80 * chapter_data["chapter"],
                    "badge": f"{level.lower()}_chapter_{chapter_data['chapter']}",
                    "unlock": f"{level.lower()}_chapter_{chapter_data['chapter'] + 1}" if chapter_data["chapter"] < len(chapters) else None
                },
                "unlock_requirements": {} if chapter_data["chapter"] == 1 else {"min_xp": 80 * (chapter_data["chapter"] - 1)},
                "created_at": datetime.utcnow(),
                "journey_type": "other"
            }
            learning_paths.append(path)
    
    # Insert all learning paths
    if learning_paths:
        result = await db.learning_paths.insert_many(learning_paths)
        print(f"\n🎉 Successfully seeded {len(result.inserted_ids)} learning paths!")
    
    # Summary
    print("\n📊 Summary:")
    print(f"Student Journey (CEFR):")
    for level, chapters in student_paths.items():
        print(f"  {level}: {len(chapters)} chapters")
    print(f"Other Journeys (Difficulty):")
    for level, chapters in other_paths.items():
        print(f"  {level}: {len(chapters)} chapters")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_comprehensive_learning_paths())
