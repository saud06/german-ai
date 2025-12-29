#!/bin/bash

# MongoDB Backup Script
# Backs up MongoDB database to S3/local storage with rotation

set -e

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/backups}"
DB_NAME="${DB_NAME:-german_ai}"
MONGODB_URL="${MONGODB_URL:-mongodb://localhost:27017}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
S3_BUCKET="${S3_BUCKET:-}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="mongodb_backup_${TIMESTAMP}"

echo "🔄 Starting MongoDB backup..."
echo "Database: $DB_NAME"
echo "Timestamp: $TIMESTAMP"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Perform MongoDB dump
echo "📦 Creating MongoDB dump..."
mongodump \
    --uri="$MONGODB_URL" \
    --db="$DB_NAME" \
    --out="$BACKUP_DIR/$BACKUP_NAME" \
    --gzip

# Create archive
echo "🗜️  Creating compressed archive..."
cd "$BACKUP_DIR"
tar -czf "${BACKUP_NAME}.tar.gz" "$BACKUP_NAME"
rm -rf "$BACKUP_NAME"

# Calculate backup size
BACKUP_SIZE=$(du -h "${BACKUP_NAME}.tar.gz" | cut -f1)
echo "✅ Backup created: ${BACKUP_NAME}.tar.gz ($BACKUP_SIZE)"

# Upload to S3 if configured
if [ -n "$S3_BUCKET" ]; then
    echo "☁️  Uploading to S3..."
    aws s3 cp "${BACKUP_NAME}.tar.gz" "s3://${S3_BUCKET}/backups/${BACKUP_NAME}.tar.gz"
    echo "✅ Uploaded to S3: s3://${S3_BUCKET}/backups/${BACKUP_NAME}.tar.gz"
fi

# Remove old backups (local)
echo "🧹 Cleaning up old backups (older than $RETENTION_DAYS days)..."
find "$BACKUP_DIR" -name "mongodb_backup_*.tar.gz" -type f -mtime +$RETENTION_DAYS -delete

# Remove old backups (S3)
if [ -n "$S3_BUCKET" ]; then
    echo "🧹 Cleaning up old S3 backups..."
    aws s3 ls "s3://${S3_BUCKET}/backups/" | \
        awk '{print $4}' | \
        grep "mongodb_backup_" | \
        while read -r file; do
            file_date=$(echo "$file" | grep -oP '\d{8}')
            if [ -n "$file_date" ]; then
                days_old=$(( ($(date +%s) - $(date -d "$file_date" +%s)) / 86400 ))
                if [ $days_old -gt $RETENTION_DAYS ]; then
                    echo "Deleting old backup: $file (${days_old} days old)"
                    aws s3 rm "s3://${S3_BUCKET}/backups/$file"
                fi
            fi
        done
fi

echo "✅ Backup completed successfully!"
echo "Backup file: ${BACKUP_NAME}.tar.gz"
echo "Size: $BACKUP_SIZE"

# Send notification (optional)
if [ -n "$SLACK_WEBHOOK_URL" ]; then
    curl -X POST "$SLACK_WEBHOOK_URL" \
        -H 'Content-Type: application/json' \
        -d "{\"text\":\"✅ MongoDB backup completed: ${BACKUP_NAME}.tar.gz ($BACKUP_SIZE)\"}"
fi
