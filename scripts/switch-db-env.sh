#!/bin/bash

# Script to switch between development and production database environments
# Usage: ./scripts/switch-db-env.sh [dev|prod]

set -e

ENV_FILE=".env"
BACKUP_FILE=".env.backup"

if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Error: .env file not found"
    echo "Please create .env from .env.example first"
    exit 1
fi

if [ $# -eq 0 ]; then
    echo "Usage: ./scripts/switch-db-env.sh [dev|prod]"
    echo ""
    echo "Current database configuration:"
    grep "MONGODB_DB_NAME" $ENV_FILE || echo "MONGODB_DB_NAME not set"
    grep "ENVIRONMENT" $ENV_FILE || echo "ENVIRONMENT not set"
    exit 0
fi

ENVIRONMENT=$1

# Backup current .env
cp $ENV_FILE $BACKUP_FILE
echo "📦 Backed up current .env to .env.backup"

case $ENVIRONMENT in
    dev|development)
        echo "🔧 Switching to DEVELOPMENT environment..."
        
        # Update database name
        if grep -q "^MONGODB_DB_NAME=" $ENV_FILE; then
            sed -i '' 's/^MONGODB_DB_NAME=.*/MONGODB_DB_NAME=german_ai_dev/' $ENV_FILE
        else
            echo "MONGODB_DB_NAME=german_ai_dev" >> $ENV_FILE
        fi
        
        # Update environment
        if grep -q "^ENVIRONMENT=" $ENV_FILE; then
            sed -i '' 's/^ENVIRONMENT=.*/ENVIRONMENT=development/' $ENV_FILE
        else
            echo "ENVIRONMENT=development" >> $ENV_FILE
        fi
        
        echo "✅ Switched to development database: german_ai_dev"
        echo ""
        echo "Next steps:"
        echo "1. Restart services: docker compose restart backend"
        echo "2. Seed data if needed:"
        echo "   docker compose exec backend python scripts/seed_comprehensive_scenarios.py"
        echo "   docker compose exec backend python scripts/seed_comprehensive_learning_paths.py"
        echo "   docker compose exec backend python scripts/seed_locations.py"
        ;;
        
    prod|production)
        echo "🚀 Switching to PRODUCTION environment..."
        
        # Update database name
        if grep -q "^MONGODB_DB_NAME=" $ENV_FILE; then
            sed -i '' 's/^MONGODB_DB_NAME=.*/MONGODB_DB_NAME=german_ai_prod/' $ENV_FILE
        else
            echo "MONGODB_DB_NAME=german_ai_prod" >> $ENV_FILE
        fi
        
        # Update environment
        if grep -q "^ENVIRONMENT=" $ENV_FILE; then
            sed -i '' 's/^ENVIRONMENT=.*/ENVIRONMENT=production/' $ENV_FILE
        else
            echo "ENVIRONMENT=production" >> $ENV_FILE
        fi
        
        echo "✅ Switched to production database: german_ai_prod"
        echo ""
        echo "⚠️  WARNING: You are now using PRODUCTION database!"
        echo ""
        echo "Next steps:"
        echo "1. Ensure production data is ready"
        echo "2. Restart services: docker compose restart backend"
        echo "3. DO NOT run seed scripts in production!"
        ;;
        
    *)
        echo "❌ Invalid environment: $ENVIRONMENT"
        echo "Usage: ./scripts/switch-db-env.sh [dev|prod]"
        exit 1
        ;;
esac

echo ""
echo "Current configuration:"
grep "MONGODB_DB_NAME" $ENV_FILE
grep "ENVIRONMENT" $ENV_FILE
