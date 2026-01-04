# Database Setup Guide

## Strategy: Separate Dev/Prod Databases in MongoDB Atlas

We use **MongoDB Atlas** for both development and production, with separate databases to isolate environments.

### Architecture

```
MongoDB Atlas Cluster (cluster0.8hmnx1o.mongodb.net)
├── german_ai_dev  (Development)
└── german_ai_prod (Production)
```

### Why This Approach?

#### ✅ Advantages
- **Same infrastructure** - No local/cloud differences
- **No migration complexity** - Just switch database name
- **Free tier covers both** - 512MB free (plenty for dev)
- **Consistent behavior** - Same MongoDB version everywhere
- **Cloud backups** - Automatic for both environments
- **Easy switching** - One environment variable change
- **No sync issues** - Independent databases
- **Network testing** - Test real-world conditions in dev

#### ❌ Disadvantages
- **Requires internet** - Can't work fully offline
- **Slight latency** - ~50-100ms (negligible for development)

### Setup Instructions

#### 1. Create Development Database

The development database (`german_ai_dev`) is automatically created when you run seed scripts with `MONGODB_DB_NAME=german_ai_dev`.

#### 2. Environment Configuration

**Development (.env):**
```bash
MONGODB_URI=mongodb+srv://saud:A20WJXcybOc2aAgb@cluster0.8hmnx1o.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
MONGODB_DB_NAME=german_ai_dev
ENVIRONMENT=development
```

**Production (.env.production):**
```bash
MONGODB_URI=mongodb+srv://saud:A20WJXcybOc2aAgb@cluster0.8hmnx1o.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
MONGODB_DB_NAME=german_ai_prod
ENVIRONMENT=production
```

#### 3. Seed Development Database

```bash
# Ensure .env has MONGODB_DB_NAME=german_ai_dev
docker compose up -d backend

# Seed all data
docker compose exec backend python scripts/seed_comprehensive_scenarios.py
docker compose exec backend python scripts/seed_comprehensive_learning_paths.py
docker compose exec backend python scripts/seed_locations.py
```

#### 4. Promote to Production

When ready to deploy, copy development data to production:

```bash
# Option 1: MongoDB Atlas UI
# 1. Go to MongoDB Atlas dashboard
# 2. Select your cluster
# 3. Click "Collections"
# 4. Use "Clone Database" feature
# 5. Clone german_ai_dev → german_ai_prod

# Option 2: Using mongodump/mongorestore (requires MongoDB tools)
mongodump --uri="mongodb+srv://saud:A20WJXcybOc2aAgb@cluster0.8hmnx1o.mongodb.net/german_ai_dev" --out=./backup
mongorestore --uri="mongodb+srv://saud:A20WJXcybOc2aAgb@cluster0.8hmnx1o.mongodb.net/german_ai_prod" ./backup/german_ai_dev --nsFrom="german_ai_dev.*" --nsTo="german_ai_prod.*"
```

### Current Database Status

**german_ai** (Current production):
- 29 users
- 45 scenarios (A1: 15, A2: 15, B1: 15)
- 91 learning paths
- 546 locations

### Migration Plan

1. **Immediate**: Continue using `german_ai` for production
2. **Development**: Switch to `german_ai_dev` for all development work
3. **Before Production Deploy**: Clone `german_ai_dev` → `german_ai_prod`
4. **Production Deploy**: Update production .env to use `german_ai_prod`

### Troubleshooting

#### Issue: Random Chapter Switching (B1 ↔ C1)

**Cause**: Frontend caching or multiple browser sessions with different users

**Solution**:
1. Hard refresh browser (`Cmd + Shift + R`)
2. Clear localStorage: `localStorage.clear()`
3. Check which user is logged in
4. Verify user's `active_journey_id` in database

#### Issue: No Scenarios in Locations

**Cause**: Locations not linked to scenarios

**Solution**:
```bash
docker compose exec backend python scripts/seed_locations.py
```

### Best Practices

1. **Always specify MONGODB_DB_NAME** in .env
2. **Never commit .env** to git (already in .gitignore)
3. **Use .env.example** as template
4. **Test in dev** before promoting to prod
5. **Backup before major changes** (Atlas does this automatically)
6. **Monitor Atlas free tier usage** (512MB limit)

### Database Collections

- `users` - User accounts and journey data
- `scenarios` - Conversation scenarios
- `learning_paths` - Chapter/lesson structure
- `locations` - Map locations with scenarios
- `journey_configurations` - Journey type configs
- `content_mappings` - Content priority mappings
- `vocabulary` - Word database
- `user_progress` - Learning progress tracking

### Monitoring

Check database size in MongoDB Atlas:
1. Go to cluster dashboard
2. Click "Metrics"
3. View "Data Size" chart
4. Ensure under 512MB for free tier
