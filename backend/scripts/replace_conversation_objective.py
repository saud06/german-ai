"""
Replace vague 'Have conversation' objective with specific, achievable tasks
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Mapping of scenario categories to specific objectives
CATEGORY_OBJECTIVES = {
    "café": {
        "description": "Order a drink",
        "keywords": ["kaffee", "tee", "wasser", "cola", "saft", "cappuccino", "espresso", "latte", "möchte", "nehme"],
        "hint": "Order something to drink (e.g., 'Ich möchte einen Kaffee')"
    },
    "restaurant": {
        "description": "Order food",
        "keywords": ["essen", "bestellen", "möchte", "nehme", "hätte gern", "schnitzel", "pizza", "salat", "suppe"],
        "hint": "Order something to eat (e.g., 'Ich nehme das Schnitzel')"
    },
    "supermarket": {
        "description": "Ask for item location",
        "keywords": ["wo", "finden", "gibt", "haben sie", "suche", "brauche", "brot", "milch", "obst"],
        "hint": "Ask where to find something (e.g., 'Wo finde ich Brot?')"
    },
    "hotel": {
        "description": "Ask about room",
        "keywords": ["zimmer", "reservierung", "buchen", "frei", "verfügbar", "preis", "kosten"],
        "hint": "Ask about a room (e.g., 'Haben Sie ein Zimmer frei?')"
    },
    "doctor": {
        "description": "Describe symptoms",
        "keywords": ["schmerzen", "tut weh", "kopfschmerzen", "fieber", "husten", "erkältet", "krank"],
        "hint": "Describe how you feel (e.g., 'Ich habe Kopfschmerzen')"
    },
    "pharmacy": {
        "description": "Ask for medicine",
        "keywords": ["medikament", "tabletten", "schmerzmittel", "rezept", "brauche", "gegen", "haben sie"],
        "hint": "Ask for medicine (e.g., 'Ich brauche Schmerzmittel')"
    },
    "bank": {
        "description": "Ask about service",
        "keywords": ["konto", "geld", "überweisen", "abheben", "karte", "öffnen", "möchte"],
        "hint": "Ask about a banking service (e.g., 'Ich möchte Geld abheben')"
    },
    "train": {
        "description": "Ask about train",
        "keywords": ["zug", "fahrt", "abfahrt", "ankunft", "gleis", "ticket", "wann", "nach"],
        "hint": "Ask about a train (e.g., 'Wann fährt der Zug nach Berlin?')"
    },
    "airport": {
        "description": "Ask about flight",
        "keywords": ["flug", "gate", "abflug", "check-in", "gepäck", "boarding", "nach"],
        "hint": "Ask about your flight (e.g., 'Wo ist das Gate für Flug LH123?')"
    },
    "post": {
        "description": "Send package",
        "keywords": ["paket", "brief", "schicken", "senden", "porto", "marke", "versenden"],
        "hint": "Ask to send something (e.g., 'Ich möchte ein Paket schicken')"
    },
    "default": {
        "description": "Ask a question",
        "keywords": ["wie", "was", "wo", "wann", "können sie", "haben sie", "gibt es", "?"],
        "hint": "Ask a relevant question"
    }
}

def get_objective_for_scenario(scenario_name: str, category: str):
    """Determine the appropriate objective based on scenario name and category"""
    name_lower = scenario_name.lower()
    
    # Check scenario name for keywords
    if "café" in name_lower or "coffee" in name_lower:
        return CATEGORY_OBJECTIVES["café"]
    elif "restaurant" in name_lower or "essen" in name_lower:
        return CATEGORY_OBJECTIVES["restaurant"]
    elif "supermarkt" in name_lower or "markt" in name_lower:
        return CATEGORY_OBJECTIVES["supermarket"]
    elif "hotel" in name_lower:
        return CATEGORY_OBJECTIVES["hotel"]
    elif "arzt" in name_lower or "doktor" in name_lower or "krankenhaus" in name_lower:
        return CATEGORY_OBJECTIVES["doctor"]
    elif "apotheke" in name_lower or "pharmacy" in name_lower:
        return CATEGORY_OBJECTIVES["pharmacy"]
    elif "bank" in name_lower:
        return CATEGORY_OBJECTIVES["bank"]
    elif "bahnhof" in name_lower or "zug" in name_lower or "train" in name_lower:
        return CATEGORY_OBJECTIVES["train"]
    elif "flughafen" in name_lower or "airport" in name_lower:
        return CATEGORY_OBJECTIVES["airport"]
    elif "post" in name_lower:
        return CATEGORY_OBJECTIVES["post"]
    
    # Fallback to category
    return CATEGORY_OBJECTIVES.get(category, CATEGORY_OBJECTIVES["default"])

async def replace_conversation_objectives():
    """Replace 'Have conversation' with specific objectives"""
    
    # Connect to MongoDB
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(mongodb_uri)
    db = client[os.getenv("MONGODB_DB_NAME", "german_ai")]
    
    print("🔧 Replacing 'Have conversation' objectives with specific tasks...")
    print("")
    
    # Get all scenarios
    scenarios = await db.scenarios.find({}).to_list(length=1000)
    
    updated_count = 0
    for scenario in scenarios:
        modified = False
        
        if "objectives" in scenario:
            for obj in scenario["objectives"]:
                # Find "Have conversation" objectives
                if obj.get("description", "").lower() in ["have conversation", "respond naturally", "converse"]:
                    # Get specific objective based on scenario
                    new_objective = get_objective_for_scenario(
                        scenario.get("name", ""),
                        scenario.get("category", "")
                    )
                    
                    # Update the objective
                    obj["description"] = new_objective["description"]
                    obj["keywords"] = new_objective["keywords"]
                    obj["hint"] = new_objective["hint"]
                    obj["required"] = True  # Make it required again
                    
                    modified = True
                    print(f"  ✓ {scenario['name']}: '{new_objective['description']}'")
        
        if modified:
            await db.scenarios.update_one(
                {"_id": scenario["_id"]},
                {"$set": {"objectives": scenario["objectives"], "updated_at": datetime.utcnow()}}
            )
            updated_count += 1
    
    print("")
    print(f"✅ Updated {updated_count} scenarios with specific objectives")
    print("")
    print("🎉 All scenarios now have clear, achievable objectives!")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(replace_conversation_objectives())
