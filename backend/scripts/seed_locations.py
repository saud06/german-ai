"""
Seed Locations for Learning Paths
Creates sample locations for each chapter to make the map functional
"""

import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os

# MongoDB connection
MONGODB_URL = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("MONGODB_DB_NAME", "german_ai")

if not MONGODB_URL:
    raise ValueError("MONGODB_URI environment variable is required. Please set it in your .env file.")

async def seed_locations():
    """Seed sample locations for learning paths"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DB_NAME]
    
    print("🗺️ Seeding locations for learning paths...")
    print("=" * 50)
    
    # Clear existing locations
    await db.locations.delete_many({})
    print("🗑️ Cleared existing locations")
    
    # Get all learning paths
    learning_paths = await db.learning_paths.find({}).to_list(100)
    
    locations = []
    
    # Sample location templates by level (expanded to 7+ per level)
    location_templates = {
        "A1": [
            {"name": "Café Einstein", "type": "cafe", "description": "Cozy coffee shop for practicing basic greetings"},
            {"name": "Bäckerei Schmidt", "type": "bakery", "description": "Local bakery for food vocabulary"},
            {"name": "Supermarkt REWE", "type": "supermarket", "description": "Grocery store for numbers and shopping"},
            {"name": "Bushaltestelle", "type": "bus_stop", "description": "Bus stop for directions and transport"},
            {"name": "Park am See", "type": "park", "description": "City park for outdoor conversations"},
            {"name": "Buchhandlung", "type": "bookstore", "description": "Bookstore for reading and literature"},
            {"name": "Kino", "type": "cinema", "description": "Movie theater for entertainment vocabulary"},
        ],
        "A2": [
            {"name": "Restaurant Zum Goldenen Löffel", "type": "restaurant", "description": "Traditional German restaurant"},
            {"name": "Apotheke", "type": "pharmacy", "description": "Pharmacy for health and medicine vocabulary"},
            {"name": "Bank", "type": "bank", "description": "Bank for financial transactions"},
            {"name": "Postamt", "type": "post_office", "description": "Post office for mailing packages"},
            {"name": "Fitnessstudio", "type": "gym", "description": "Gym for health and fitness discussions"},
            {"name": "Friseur", "type": "hair_salon", "description": "Hair salon for personal care vocabulary"},
            {"name": "Bahnhof", "type": "train_station", "description": "Train station for travel planning"},
        ],
        "B1": [
            {"name": "Arbeitsamt", "type": "job_center", "description": "Job center for employment discussions"},
            {"name": "Arztpraxis Dr. Weber", "type": "doctor", "description": "Doctor's office for medical appointments"},
            {"name": "Mietwohnung", "type": "apartment", "description": "Apartment viewing and rental discussions"},
            {"name": "Behörde", "type": "government_office", "description": "Government office for bureaucratic procedures"},
            {"name": "Versicherungsbüro", "type": "insurance", "description": "Insurance office for policy discussions"},
            {"name": "Sprachschule", "type": "language_school", "description": "Language school for education topics"},
            {"name": "Rathaus", "type": "city_hall", "description": "City hall for civic matters"},
        ],
        "B2": [
            {"name": "Unternehmensberatung", "type": "consulting", "description": "Business consulting firm"},
            {"name": "Universität", "type": "university", "description": "University for academic discussions"},
            {"name": "Anwaltskanzlei", "type": "law_office", "description": "Law office for legal matters"},
            {"name": "Technologiepark", "type": "tech_park", "description": "Technology park for innovation discussions"},
            {"name": "Konferenzzentrum", "type": "conference_center", "description": "Conference center for professional events"},
            {"name": "Startup Inkubator", "type": "startup", "description": "Startup incubator for entrepreneurship"},
            {"name": "Handelskammer", "type": "chamber_commerce", "description": "Chamber of commerce for business networking"},
        ],
        "C1": [
            {"name": "Forschungsinstitut", "type": "research_institute", "description": "Research institute for scientific discussions"},
            {"name": "Kunstmuseum", "type": "art_museum", "description": "Art museum for cultural discussions"},
            {"name": "Philosophische Fakultät", "type": "philosophy_department", "description": "Philosophy department for deep discussions"},
            {"name": "Internationale Konferenz", "type": "conference", "description": "International conference for diplomatic talks"},
            {"name": "Literaturhaus", "type": "literature_house", "description": "Literature house for literary discussions"},
            {"name": "Opernhaus", "type": "opera_house", "description": "Opera house for classical arts"},
            {"name": "Diplomatisches Zentrum", "type": "diplomatic", "description": "Diplomatic center for international relations"},
        ],
        "Beginner": [
            {"name": "Willkommens-Café", "type": "welcome_cafe", "description": "Welcome café for first conversations"},
            {"name": "Sprachtreff", "type": "language_meetup", "description": "Language meetup for practice"},
            {"name": "Stadtführung", "type": "city_tour", "description": "City tour for orientation"},
            {"name": "Nachbarschaftszentrum", "type": "community_center", "description": "Community center for integration"},
            {"name": "Bibliothek", "type": "library", "description": "Library for learning resources"},
            {"name": "Marktplatz", "type": "marketplace", "description": "Marketplace for shopping practice"},
            {"name": "Tourist Information", "type": "tourist_info", "description": "Tourist information for city guidance"},
        ],
        "Intermediate": [
            {"name": "Volkshochschule", "type": "adult_education", "description": "Adult education center for courses"},
            {"name": "Kulturzentrum", "type": "cultural_center", "description": "Cultural center for events"},
            {"name": "Sportverein", "type": "sports_club", "description": "Sports club for team activities"},
            {"name": "Handwerksbetrieb", "type": "workshop", "description": "Workshop for practical skills"},
            {"name": "Gemeindezentrum", "type": "parish_center", "description": "Parish center for community"},
            {"name": "Musikschule", "type": "music_school", "description": "Music school for artistic expression"},
            {"name": "Tanzstudio", "type": "dance_studio", "description": "Dance studio for movement and culture"},
        ],
        "Advanced": [
            {"name": "Wirtschaftsforum", "type": "business_forum", "description": "Business forum for professional networking"},
            {"name": "Akademie", "type": "academy", "description": "Academy for advanced studies"},
            {"name": "Think Tank", "type": "think_tank", "description": "Think tank for policy discussions"},
            {"name": "Medienhaus", "type": "media_house", "description": "Media house for journalism"},
            {"name": "Architekturbüro", "type": "architecture", "description": "Architecture office for design"},
            {"name": "Innovationslabor", "type": "innovation_lab", "description": "Innovation lab for technology"},
            {"name": "Kulturstiftung", "type": "cultural_foundation", "description": "Cultural foundation for arts patronage"},
        ]
    }
    
    # Create locations for each learning path
    for path in learning_paths:
        level = path.get("level", "A1")
        chapter = path.get("chapter", 1)
        
        # Get appropriate templates for this level
        templates = location_templates.get(level, location_templates["A1"])
        
        # Create 5-7 locations per chapter
        num_locations = min(len(templates), 5 + (chapter % 3))
        
        for i in range(num_locations):
            template = templates[i % len(templates)]
            
            location = {
                "_id": ObjectId(),
                "chapter_id": str(path["_id"]),
                "name": template["name"],
                "type": template["type"],
                "description": template["description"],
                "image": f"/images/locations/{template['type']}.jpg",
                "position": {
                    "x": 100 + (i * 200),
                    "y": 100 + (i * 150)
                },
                "scenarios": [],
                "characters": [],
                "estimated_minutes": 15 + (i * 5),
                "difficulty_requirements": {
                    "min_level": level.lower(),
                    "recommended_xp": chapter * 100
                },
                "unlock_requirements": {
                    "previous_location": None if i == 0 else str(locations[-1]["_id"]) if locations else None,
                    "min_xp": (chapter * 100) + (i * 25)
                },
                "completion_reward": {
                    "xp": 50 + (i * 10),
                    "unlock_next": True
                },
                "created_at": datetime.utcnow()
            }
            
            locations.append(location)
            
            # Add location ID to learning path
            if "locations" not in path:
                path["locations"] = []
            path["locations"].append(str(location["_id"]))
    
    # Insert all locations
    if locations:
        result = await db.locations.insert_many(locations)
        print(f"✅ Created {len(result.inserted_ids)} locations")
    
    # Update learning paths with location references
    for path in learning_paths:
        if "locations" in path and path["locations"]:
            await db.learning_paths.update_one(
                {"_id": path["_id"]},
                {"$set": {"locations": path["locations"]}}
            )
    
    print(f"\n📊 Summary:")
    print(f"Total locations created: {len(locations)}")
    print(f"Learning paths updated: {len(learning_paths)}")
    
    # Show sample by level
    by_level = {}
    for location in locations:
        level = location.get("difficulty_requirements", {}).get("min_level", "A1")
        by_level[level] = by_level.get(level, 0) + 1
    
    print("\nLocations by level:")
    for level, count in sorted(by_level.items()):
        print(f"  {level.upper()}: {count} locations")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_locations())
