# Complete Data Loading and Setup Guide

## 🚀 Quick Start: From Zero to Running Application

This guide shows you exactly how to load CSV data and set up the Franklin Search application from scratch.

### Prerequisites
- Python 3.8+
- PostgreSQL running
- CSV files in project root: `googleplaystore.csv` and `googleplaystore_user_reviews.csv`

### Option 1: Complete Setup (Automated)
```bash
# One command setup (recommended for new installs)
./setup-dev.sh
```

### Option 2: Manual Step-by-Step Setup

#### 1. Database Setup
```bash
# Run migrations to create tables
python manage.py migrate
```

#### 2. Load CSV Data (Takes a few minutes)
```bash
# Load all data from CSV files
python manage.py load_initial_data

# Output will look like:
# Loading apps from /path/to/googleplaystore.csv...
# Apps loaded: 9659 created, 0 updated
# Loading reviews from /path/to/googleplaystore_user_reviews.csv...
# Reviews loaded: 194865 created, 0 skipped
# Data import completed!
```

#### 3. Create Test Users
```bash
# Create test accounts for immediate use
python manage.py seed_users

# Creates:
# - testuser / testpass123 (Regular User)
# - supervisor / supervisor123 (Supervisor)
```

#### 4. Verify Data Loading
```bash
# Inspect loaded data
python manage.py inspect_data --detailed --categories

# Quick verification
python manage.py shell -c "
from core.models import App, Review;
print(f'✅ Apps: {App.objects.count():,}');
print(f'✅ Reviews: {Review.objects.count():,}')"
```

#### 5. Start Application
```bash
# Start development server
python manage.py runserver

# Application available at: http://localhost:8000
```

## 📊 What Data Gets Loaded

### Google Play Store Apps (`googleplaystore.csv`)
- **9,659 apps** across 33+ categories
- App metadata: name, category, rating, reviews count, installs, size, etc.
- Categories include: GAME, HEALTH_AND_FITNESS, FAMILY, DATING, TOOLS, etc.

### User Reviews (`googleplaystore_user_reviews.csv`)
- **194,865 reviews** with sentiment analysis
- Review text (translated to English)
- Sentiment classification: Positive, Negative, Neutral
- Sentiment polarity (-1 to 1) and subjectivity (0 to 1)
- All imported reviews marked with `status='imported'`

### Data Statistics
```
📱 Total Apps: 9,659
💬 Total Reviews: 194,865
   ├─ Imported (CSV): 194,865
   └─ User Generated: 0

💭 Review Sentiments:
   Positive: 124,940 (64%)
   Negative: 43,578 (22%)
   Neutral: 26,347 (14%)
```

## 🔄 CSV Data Loading Process Explained

### How It Works

1. **Apps Import** (`load_apps()` method):
   ```python
   # For each row in googleplaystore.csv:
   # 1. Read and clean data
   # 2. Convert types (rating to float, reviews to int)
   # 3. Create or update App record
   # 4. Handle duplicates with get_or_create()
   ```

2. **Reviews Import** (`load_reviews()` method):
   ```python
   # For each row in googleplaystore_user_reviews.csv:
   # 1. Find corresponding app by name
   # 2. Clean review text and sentiment data
   # 3. Create Review record with status='imported'
   # 4. Skip if app not found or review text empty
   ```

### Data Mapping

**Apps CSV → Django App Model:**
```
CSV Field              → Django Field
App                    → name
Category               → category
Rating                 → rating
Reviews                → reviews_count
Size                   → size
Installs               → installs
Type                   → app_type
Price                  → price
Content Rating         → content_rating
Genres                 → genres
Last Updated           → last_updated
Current Ver            → current_version
Android Ver            → android_version
```

**Reviews CSV → Django Review Model:**
```
CSV Field              → Django Field
App                    → app (ForeignKey lookup)
Translated_Review      → review_text
Sentiment              → sentiment
Sentiment_Polarity     → sentiment_polarity
Sentiment_Subjectivity → sentiment_subjectivity
(auto-set)             → status='imported'
(auto-set)             → user=null
```

## 🛠️ Advanced Usage

### Custom CSV Files
```bash
# Load from different files
python manage.py load_initial_data \
  --apps-file custom_apps.csv \
  --reviews-file custom_reviews.csv
```

### Clear and Reload Data
```bash
# WARNING: This deletes ALL existing data
python manage.py load_initial_data --clear
```

### Docker Environment
```bash
# Load data in Docker container
docker exec -it franklin_web python manage.py load_initial_data

# Or build with automatic loading (already configured)
docker-compose up --build
```

## 🚨 Troubleshooting Common Issues

### Issue: "Apps file not found"
```bash
# Check if CSV files exist
ls -la *.csv

# Expected output:
# googleplaystore.csv
# googleplaystore_user_reviews.csv
```

### Issue: "Permission denied"
```bash
# Fix file permissions
chmod 644 *.csv
```

### Issue: Import seems stuck
```bash
# The import processes 194K+ reviews, it takes time
# Watch progress with:
tail -f /tmp/django.log  # if logging enabled

# Or run with verbose output:
python manage.py load_initial_data -v 2
```

### Issue: Database connection error
```bash
# Check PostgreSQL is running
python manage.py check --database

# Check database settings
python manage.py shell -c "from django.db import connection; print(connection.settings_dict)"
```

## 📈 Performance Expectations

### Import Times (approximate)
- **Apps import**: ~30 seconds for 9,659 apps
- **Reviews import**: ~5-10 minutes for 194,865 reviews
- **Total time**: ~10-15 minutes on average hardware

### Memory Usage
- **Peak memory**: ~200-300MB during reviews import
- **Database size**: ~150MB after full import
- **Storage**: CSV files use ~8.5MB total

## 🔍 Data Quality & Validation

### Built-in Data Cleaning
- Handles encoding issues (UTF-8 with error ignore)
- Converts 'nan' strings to null values
- Skips empty or malformed records
- Validates foreign key relationships
- Prevents duplicate app creation

### Data Integrity Checks
```bash
# Check for orphaned reviews (should be 0)
python manage.py shell -c "
from core.models import Review;
orphaned = Review.objects.filter(app__isnull=True).count();
print(f'Orphaned reviews: {orphaned}')"

# Check sentiment distribution
python manage.py shell -c "
from core.models import Review;
from django.db.models import Count;
stats = Review.objects.values('sentiment').annotate(count=Count('id'));
for stat in stats: print(f'{stat[\"sentiment\"]}: {stat[\"count\"]}')"
```

## 🔄 Updating Data

### Partial Updates
The system supports incremental updates:
```bash
# Re-running load_initial_data is safe
# Existing apps are updated, not duplicated
# New reviews are added, existing ones are preserved
python manage.py load_initial_data
```

### Fresh Start
```bash
# Complete reset (WARNING: deletes all data)
python manage.py load_initial_data --clear
```

## 📝 Integration with Application Features

### Search Functionality
- Apps are indexed for full-text search using PostgreSQL trigrams
- Search works on app names, categories, and other text fields
- Imported data provides comprehensive search results

### Review System
- Imported reviews display immediately (status='imported')
- User-submitted reviews require supervisor approval
- Mixed display of both imported and user reviews

### User Roles
- Seed users can immediately test the application
- Supervisor can manage both imported and user reviews
- Regular users can search and submit new reviews

This comprehensive data loading system ensures that your Franklin Search application is immediately functional with a rich dataset for testing and demonstration purposes!