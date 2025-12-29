"""
Database Index Creation for Performance Optimization
Run this script to create all necessary indexes
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os


async def create_indexes():
    """Create all database indexes for optimal performance"""
    
    # Connect to MongoDB
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(mongodb_url)
    db = client["german_ai"]
    
    print("Creating database indexes...")
    
    # Users collection
    print("Creating indexes for 'users' collection...")
    await db.users.create_index("email", unique=True)
    await db.users.create_index("created_at")
    await db.users.create_index("last_active")
    await db.users.create_index([("email", 1), ("password_hash", 1)])
    
    # Subscriptions collection
    print("Creating indexes for 'subscriptions' collection...")
    await db.subscriptions.create_index("user_id", unique=True)
    await db.subscriptions.create_index("stripe_customer_id")
    await db.subscriptions.create_index("stripe_subscription_id")
    await db.subscriptions.create_index([("tier", 1), ("status", 1)])
    await db.subscriptions.create_index("current_period_end")
    
    # Scenarios collection
    print("Creating indexes for 'scenarios' collection...")
    await db.scenarios.create_index("category")
    await db.scenarios.create_index("difficulty")
    await db.scenarios.create_index([("category", 1), ("difficulty", 1)])
    await db.scenarios.create_index("created_at")
    
    # Conversation states collection
    print("Creating indexes for 'conversation_states' collection...")
    await db.conversation_states.create_index("user_id")
    await db.conversation_states.create_index("scenario_id")
    await db.conversation_states.create_index([("user_id", 1), ("scenario_id", 1)])
    await db.conversation_states.create_index("created_at")
    await db.conversation_states.create_index("updated_at")
    
    # Vocabulary collection
    print("Creating indexes for 'vocabulary' collection...")
    await db.vocabulary.create_index("german")
    await db.vocabulary.create_index("level")
    await db.vocabulary.create_index("category")
    await db.vocabulary.create_index([("level", 1), ("category", 1)])
    
    # Quiz questions collection
    print("Creating indexes for 'quiz_questions' collection...")
    await db.quiz_questions.create_index("topic")
    await db.quiz_questions.create_index("level")
    await db.quiz_questions.create_index([("topic", 1), ("level", 1)])
    
    # User progress collection
    print("Creating indexes for 'user_progress' collection...")
    await db.user_progress.create_index("user_id", unique=True)
    await db.user_progress.create_index("level")
    await db.user_progress.create_index("updated_at")
    
    # Review cards collection (Spaced Repetition)
    print("Creating indexes for 'review_cards' collection...")
    await db.review_cards.create_index("user_id")
    await db.review_cards.create_index("next_review")
    await db.review_cards.create_index([("user_id", 1), ("next_review", 1)])
    await db.review_cards.create_index([("user_id", 1), ("status", 1)])
    
    # Achievements collection
    print("Creating indexes for 'achievements' collection...")
    await db.achievements.create_index("category")
    await db.achievements.create_index("difficulty")
    
    # User achievements collection
    print("Creating indexes for 'user_achievements' collection...")
    await db.user_achievements.create_index("user_id")
    await db.user_achievements.create_index("achievement_id")
    await db.user_achievements.create_index([("user_id", 1), ("achievement_id", 1)], unique=True)
    await db.user_achievements.create_index("unlocked_at")
    
    # Organizations collection
    print("Creating indexes for 'organizations' collection...")
    await db.organizations.create_index("slug", unique=True)
    await db.organizations.create_index("owner_id")
    await db.organizations.create_index("created_at")
    
    # Organization members collection
    print("Creating indexes for 'organization_members' collection...")
    await db.organization_members.create_index("organization_id")
    await db.organization_members.create_index("user_id")
    await db.organization_members.create_index([("organization_id", 1), ("user_id", 1)], unique=True)
    await db.organization_members.create_index([("organization_id", 1), ("role", 1)])
    
    # API keys collection
    print("Creating indexes for 'api_keys' collection...")
    await db.api_keys.create_index("key_hash", unique=True)
    await db.api_keys.create_index("organization_id")
    await db.api_keys.create_index([("organization_id", 1), ("active", 1)])
    await db.api_keys.create_index("last_used_at")
    
    # Webhooks collection
    print("Creating indexes for 'webhooks' collection...")
    await db.webhooks.create_index("organization_id")
    await db.webhooks.create_index([("organization_id", 1), ("active", 1)])
    await db.webhooks.create_index("events")
    
    # Webhook deliveries collection
    print("Creating indexes for 'webhook_deliveries' collection...")
    await db.webhook_deliveries.create_index("webhook_id")
    await db.webhook_deliveries.create_index("status")
    await db.webhook_deliveries.create_index("created_at")
    await db.webhook_deliveries.create_index([("webhook_id", 1), ("created_at", -1)])
    
    # Audit logs collection
    print("Creating indexes for 'audit_logs' collection...")
    await db.audit_logs.create_index("user_id")
    await db.audit_logs.create_index("organization_id")
    await db.audit_logs.create_index("action")
    await db.audit_logs.create_index("created_at")
    await db.audit_logs.create_index([("organization_id", 1), ("created_at", -1)])
    
    # Referral codes collection
    print("Creating indexes for 'referral_codes' collection...")
    await db.referral_codes.create_index("code", unique=True)
    await db.referral_codes.create_index("user_id")
    await db.referral_codes.create_index([("user_id", 1), ("active", 1)])
    
    # Referral rewards collection
    print("Creating indexes for 'referral_rewards' collection...")
    await db.referral_rewards.create_index("referrer_id")
    await db.referral_rewards.create_index("referred_id")
    await db.referral_rewards.create_index([("referrer_id", 1), ("claimed", 1)])
    await db.referral_rewards.create_index("created_at")
    
    # Conversion events collection
    print("Creating indexes for 'conversion_events' collection...")
    await db.conversion_events.create_index("user_id")
    await db.conversion_events.create_index("event_type")
    await db.conversion_events.create_index("source")
    await db.conversion_events.create_index("created_at")
    await db.conversion_events.create_index([("event_type", 1), ("created_at", -1)])
    await db.conversion_events.create_index([("source", 1), ("event_type", 1)])
    
    # Invoices collection
    print("Creating indexes for 'invoices' collection...")
    await db.invoices.create_index("user_id")
    await db.invoices.create_index("stripe_invoice_id", unique=True)
    await db.invoices.create_index("status")
    await db.invoices.create_index("created_at")
    await db.invoices.create_index([("user_id", 1), ("created_at", -1)])
    
    # Usage tracking collection
    print("Creating indexes for 'usage_tracking' collection...")
    await db.usage_tracking.create_index([("user_id", 1), ("date", 1)], unique=True)
    await db.usage_tracking.create_index("date")
    
    # Email logs collection
    print("Creating indexes for 'email_logs' collection...")
    await db.email_logs.create_index("to_email")
    await db.email_logs.create_index("template_name")
    await db.email_logs.create_index("sent_at")
    await db.email_logs.create_index([("to_email", 1), ("sent_at", -1)])
    
    # Create compound indexes for common queries
    print("Creating compound indexes for common queries...")
    
    # User activity tracking
    await db.users.create_index([("last_active", -1), ("level", 1)])
    
    # Scenario completion tracking
    await db.conversation_states.create_index([
        ("user_id", 1),
        ("completed", 1),
        ("updated_at", -1)
    ])
    
    # Review cards due today
    await db.review_cards.create_index([
        ("user_id", 1),
        ("next_review", 1),
        ("status", 1)
    ])
    
    # Active subscriptions
    await db.subscriptions.create_index([
        ("status", 1),
        ("tier", 1),
        ("current_period_end", 1)
    ])
    
    print("✅ All indexes created successfully!")
    
    # Print index statistics
    print("\nIndex Statistics:")
    collections = await db.list_collection_names()
    for collection_name in collections:
        collection = db[collection_name]
        indexes = await collection.index_information()
        print(f"  {collection_name}: {len(indexes)} indexes")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(create_indexes())
