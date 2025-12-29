#!/bin/bash

# MongoDB Restore Script
# Restores MongoDB database from backup

set -e

# Configuration
BACKUP_FILE="${1:-}"
MONGODB_URL="${MONGODB_URL:-mongodb://localhost:27017}"
DB_NAME="${DB_NAME:-german_ai}"
TEMP_DIR="/tmp/mongodb_restore_$$"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file.tar.gz>"
    echo "Example: $0 mongodb_backup_20250109_120000.tar.gz"
    exit 1
fi

echo "🔄 Starting MongoDB restore..."
echo "Backup file: $BACKUP_FILE"
echo "Database: $DB_NAME"

# Check if backup file exists or is S3 URL
if [[ "$BACKUP_FILE" == s3://* ]]; then
    echo "📥 Downloading from S3..."
    BACKUP_FILENAME=$(basename "$BACKUP_FILE")
    aws s3 cp "$BACKUP_FILE" "/tmp/$BACKUP_FILENAME"
    BACKUP_FILE="/tmp/$BACKUP_FILENAME"
elif [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

# Create temp directory
mkdir -p "$TEMP_DIR"

# Extract backup
echo "📦 Extracting backup..."
tar -xzf "$BACKUP_FILE" -C "$TEMP_DIR"

# Find the backup directory
BACKUP_DIR=$(find "$TEMP_DIR" -type d -name "mongodb_backup_*" | head -n 1)

if [ -z "$BACKUP_DIR" ]; then
    echo "❌ Error: Could not find backup directory in archive"
    rm -rf "$TEMP_DIR"
    exit 1
fi

# Confirm restore
echo "⚠️  WARNING: This will replace the current database!"
read -p "Are you sure you want to restore? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Restore cancelled"
    rm -rf "$TEMP_DIR"
    exit 0
fi

# Perform restore
echo "🔄 Restoring database..."
mongorestore \
    --uri="$MONGODB_URL" \
    --db="$DB_NAME" \
    --drop \
    --gzip \
    "$BACKUP_DIR/$DB_NAME"

# Cleanup
echo "🧹 Cleaning up..."
rm -rf "$TEMP_DIR"

echo "✅ Restore completed successfully!"

# Send notification (optional)
if [ -n "$SLACK_WEBHOOK_URL" ]; then
    curl -X POST "$SLACK_WEBHOOK_URL" \
        -H 'Content-Type: application/json' \
        -d "{\"text\":\"✅ MongoDB restore completed from: $BACKUP_FILE\"}"
fi
