"""
Seed journey configurations for the Learning Purpose Wrapper
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://mongodb:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "german_ai")

JOURNEY_CONFIGURATIONS = [
    {
        "journey_type": "student",
        "display_name": "Student Journey",
        "description": "Prepare for exams or structured levels (A1–C1)",
        "icon": "🎓",
        "color": "#3B82F6",
        "level_system": {
            "type": "cefr",
            "levels": ["A1", "A2", "B1", "B2", "C1"]
        },
        "dashboard_config": {
            "hero_title": "Your Exam & Level Journey",
            "hero_subtitle": "Master German with structured learning and exam preparation",
            "primary_cta": "Continue Your Learning Path",
            "sections": [
                {
                    "id": "core_lessons",
                    "title": "Core Lessons",
                    "description": "Curriculum-style modules for systematic learning",
                    "content_types": ["lesson", "grammar"],
                    "order": 1
                },
                {
                    "id": "exam_practice",
                    "title": "Exam Practice",
                    "description": "Mock tests and exam-style questions",
                    "content_types": ["quiz"],
                    "order": 2
                },
                {
                    "id": "grammar_boosters",
                    "title": "Grammar Boosters",
                    "description": "Short drills to strengthen your grammar",
                    "content_types": ["grammar"],
                    "order": 3
                },
                {
                    "id": "practice_scenarios",
                    "title": "Practice Scenarios",
                    "description": "Apply your knowledge in real situations",
                    "content_types": ["scenario"],
                    "order": 4
                },
                {
                    "id": "progress_tracker",
                    "title": "Progress to Next Level",
                    "description": "Track your advancement through CEFR levels",
                    "content_types": ["progress"],
                    "order": 5
                }
            ]
        },
        "milestones": [
            {
                "id": "complete_a1",
                "title": "Complete A1 Level",
                "description": "Finish all A1 core lessons",
                "criteria": {"type": "lessons_completed", "target": 20, "level": "A1"}
            },
            {
                "id": "exam_ready_a2",
                "title": "A2 Exam Ready",
                "description": "Score 70%+ on A2 mock test",
                "criteria": {"type": "quiz_score", "target": 70, "level": "A2"}
            },
            {
                "id": "grammar_master",
                "title": "Grammar Master",
                "description": "Complete 50 grammar exercises",
                "criteria": {"type": "grammar_completed", "target": 50}
            }
        ]
    },
    {
        "journey_type": "traveler",
        "display_name": "Traveler Journey",
        "description": "Travel, culture, and real-life conversations",
        "icon": "✈️",
        "color": "#10B981",
        "level_system": {
            "type": "difficulty",
            "levels": ["Beginner", "Intermediate", "Advanced"]
        },
        "dashboard_config": {
            "hero_title": "Get Ready for Your Trip",
            "hero_subtitle": "Learn practical German for travel and cultural experiences",
            "primary_cta": "Practice a Travel Scenario",
            "sections": [
                {
                    "id": "essential_phrases",
                    "title": "Essential Phrases for Your Trip",
                    "description": "Must-know phrases for travelers",
                    "content_types": ["vocab", "lesson"],
                    "order": 1
                },
                {
                    "id": "travel_scenarios",
                    "title": "Real-Life Travel Scenarios",
                    "description": "Airport, hotel, restaurant, and more",
                    "content_types": ["scenario"],
                    "order": 2
                },
                {
                    "id": "culture_etiquette",
                    "title": "Culture & Etiquette",
                    "description": "Learn German customs and social norms",
                    "content_types": ["lesson"],
                    "order": 3
                },
                {
                    "id": "pronunciation",
                    "title": "Pronunciation & Listening",
                    "description": "Sound natural and understand locals",
                    "content_types": ["speech", "lesson"],
                    "order": 4
                },
                {
                    "id": "travel_readiness",
                    "title": "Travel Readiness Meter",
                    "description": "See how prepared you are for your trip",
                    "content_types": ["progress"],
                    "order": 5
                }
            ]
        },
        "milestones": [
            {
                "id": "restaurant_ready",
                "title": "Restaurant Ready",
                "description": "Order at a restaurant without English",
                "criteria": {"type": "scenario_completed", "target": 1, "scenario_type": "restaurant"}
            },
            {
                "id": "directions_master",
                "title": "Directions Master",
                "description": "Ask for and understand directions",
                "criteria": {"type": "scenario_completed", "target": 1, "scenario_type": "directions"}
            },
            {
                "id": "hotel_confident",
                "title": "Hotel Confident",
                "description": "Check into a hotel confidently",
                "criteria": {"type": "scenario_completed", "target": 1, "scenario_type": "hotel"}
            }
        ]
    },
    {
        "journey_type": "professional",
        "display_name": "Professional Journey",
        "description": "Use German at work or for your career",
        "icon": "💼",
        "color": "#8B5CF6",
        "level_system": {
            "type": "difficulty",
            "levels": ["Beginner", "Intermediate", "Advanced"]
        },
        "dashboard_config": {
            "hero_title": "Business & Career German",
            "hero_subtitle": "Master professional communication for workplace success",
            "primary_cta": "Continue Workplace Communication",
            "sections": [
                {
                    "id": "business_lessons",
                    "title": "Core Business German Lessons",
                    "description": "Essential professional vocabulary and phrases",
                    "content_types": ["lesson", "vocab"],
                    "order": 1
                },
                {
                    "id": "email_writing",
                    "title": "Email & Message Writing",
                    "description": "Write clear professional communications",
                    "content_types": ["writing"],
                    "order": 2
                },
                {
                    "id": "meetings_presentations",
                    "title": "Meetings & Presentations",
                    "description": "Participate confidently in business settings",
                    "content_types": ["scenario", "lesson"],
                    "order": 3
                },
                {
                    "id": "job_interviews",
                    "title": "Job Interviews & Networking",
                    "description": "Make a great professional impression",
                    "content_types": ["scenario"],
                    "order": 4
                },
                {
                    "id": "professional_culture",
                    "title": "Professional Culture & Norms",
                    "description": "Understand German workplace culture",
                    "content_types": ["lesson"],
                    "order": 5
                }
            ]
        },
        "milestones": [
            {
                "id": "professional_intro",
                "title": "Professional Introduction",
                "description": "Introduce yourself in a professional setting",
                "criteria": {"type": "scenario_completed", "target": 1, "scenario_type": "job_interview"}
            },
            {
                "id": "email_writer",
                "title": "Email Writer",
                "description": "Write 10 professional emails",
                "criteria": {"type": "writing_completed", "target": 10}
            },
            {
                "id": "meeting_leader",
                "title": "Meeting Leader",
                "description": "Lead a short meeting in German",
                "criteria": {"type": "scenario_completed", "target": 1, "scenario_type": "meeting"}
            }
        ]
    },
    {
        "journey_type": "hobby",
        "display_name": "Hobby Journey",
        "description": "Learn for fun, media, and personal interest",
        "icon": "🎨",
        "color": "#F59E0B",
        "level_system": {
            "type": "difficulty",
            "levels": ["Beginner", "Intermediate", "Advanced"]
        },
        "dashboard_config": {
            "hero_title": "Enjoy Learning German Your Way",
            "hero_subtitle": "Explore German through your interests and have fun",
            "primary_cta": "Pick Something Fun to Explore",
            "sections": [
                {
                    "id": "learn_through_media",
                    "title": "Learn Through Media",
                    "description": "Songs, clips, articles, and more",
                    "content_types": ["reading", "lesson"],
                    "order": 1
                },
                {
                    "id": "topics_you_like",
                    "title": "Topics You Like",
                    "description": "Sports, politics, tech, art, and more",
                    "content_types": ["vocab", "reading"],
                    "order": 2
                },
                {
                    "id": "light_practice",
                    "title": "Light Practice",
                    "description": "Short quizzes and vocab games",
                    "content_types": ["quiz", "vocab"],
                    "order": 3
                },
                {
                    "id": "casual_conversations",
                    "title": "Casual Conversations & Phrases",
                    "description": "Chat about everyday topics",
                    "content_types": ["scenario", "lesson"],
                    "order": 4
                },
                {
                    "id": "fun_stats",
                    "title": "Your Learning Journey",
                    "description": "See how much you've enjoyed learning",
                    "content_types": ["progress"],
                    "order": 5
                }
            ]
        },
        "milestones": [
            {
                "id": "media_consumer",
                "title": "Media Consumer",
                "description": "Complete 5 reading articles",
                "criteria": {"type": "reading_completed", "target": 5}
            },
            {
                "id": "topic_explorer",
                "title": "Topic Explorer",
                "description": "Learn 100 words in your favorite topics",
                "criteria": {"type": "vocab_learned", "target": 100}
            },
            {
                "id": "casual_chatter",
                "title": "Casual Chatter",
                "description": "Complete 10 casual conversation scenarios",
                "criteria": {"type": "scenarios_completed", "target": 10}
            }
        ]
    }
]

async def seed_journey_configurations():
    """Seed journey configurations into MongoDB"""
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[MONGODB_DB_NAME]
    
    print("🌱 Seeding journey configurations...")
    
    # Clear existing configurations
    await db.journey_configurations.delete_many({})
    print("   Cleared existing configurations")
    
    # Insert new configurations
    result = await db.journey_configurations.insert_many(JOURNEY_CONFIGURATIONS)
    print(f"   ✅ Inserted {len(result.inserted_ids)} journey configurations")
    
    # Verify
    count = await db.journey_configurations.count_documents({})
    print(f"   📊 Total configurations in database: {count}")
    
    # Display configurations
    print("\n📋 Journey Configurations:")
    for config in JOURNEY_CONFIGURATIONS:
        print(f"   • {config['icon']} {config['display_name']}")
        print(f"     Level System: {config['level_system']['type']} - {', '.join(config['level_system']['levels'])}")
        print(f"     Sections: {len(config['dashboard_config']['sections'])}")
        print(f"     Milestones: {len(config['milestones'])}")
    
    client.close()
    print("\n✅ Journey configurations seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed_journey_configurations())
