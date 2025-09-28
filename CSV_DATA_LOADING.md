# CSV Data Loading System Documentation

This document explains how the Franklin Search application loads initial data from CSV files containing Google Play Store apps and reviews.

## Overview

The system uses Django management commands to import data from two CSV files:
1. **`googleplaystore.csv`** - Contains app information (9,659 apps)
2. **`googleplaystore_user_reviews.csv`** - Contains user reviews (194,865 reviews)

## Data Files Structure

### Apps CSV (`googleplaystore.csv`)
```csv
App,Category,Rating,Reviews,Size,Installs,Type,Price,Content Rating,Genres,Last Updated,Current Ver,Android Ver
```

**Fields:**
- `App` → `name` (App name)
- `Category` → `category` (App category)
- `Rating` → `rating` (Float, 0-5 stars)
- `Reviews` → `reviews_count` (Integer, number of reviews)
- `Size` → `size` (String, e.g. "19M")
- `Installs` → `installs` (String, e.g. "10,000+")
- `Type` → `app_type` (Free/Paid)
- `Price` → `price` (String, e.g. "$2.99")
- `Content Rating` → `content_rating` (Everyone, Teen, etc.)
- `Genres` → `genres` (Semicolon separated)
- `Last Updated` → `last_updated` (String date)
- `Current Ver` → `current_version` (Version string)
- `Android Ver` → `android_version` (Required Android version)

### Reviews CSV (`googleplaystore_user_reviews.csv`)
```csv
App,Translated_Review,Sentiment,Sentiment_Polarity,Sentiment_Subjectivity
```

**Fields:**
- `App` → Links to App model by name
- `Translated_Review` → `review_text` (Review content)
- `Sentiment` → `sentiment` (Positive/Negative/Neutral)
- `Sentiment_Polarity` → `sentiment_polarity` (Float, -1 to 1)
- `Sentiment_Subjectivity` → `sentiment_subjectivity` (Float, 0 to 1)

## Management Command Usage

### Basic Import
```bash
# Load both apps and reviews
python manage.py load_initial_data
```

### Custom File Paths
```bash
# Specify custom CSV files
python manage.py load_initial_data --apps-file path/to/apps.csv --reviews-file path/to/reviews.csv
```

### Clear and Reload
```bash
# Clear existing data and reload
python manage.py load_initial_data --clear
```

### Docker Usage
```bash
# Inside Docker container
docker exec -it franklin_web python manage.py load_initial_data
```

## Import Process Details

### Apps Import Process
1. **File Reading**: Opens `googleplaystore.csv` with UTF-8 encoding
2. **Data Cleaning**:
   - Strips whitespace from all fields
   - Converts rating to float (handles 'nan' values)
   - Converts reviews count to integer
   - Skips rows with empty app names
3. **Database Operations**:
   - Uses `get_or_create()` to avoid duplicates
   - Creates new apps or updates existing ones
   - Handles exceptions gracefully with warnings
4. **Progress Tracking**: Reports created vs updated counts

### Reviews Import Process
1. **File Reading**: Opens `googleplaystore_user_reviews.csv` with UTF-8 encoding
2. **Data Validation**:
   - Skips reviews with empty text or 'nan' values
   - Only imports reviews for existing apps
   - Converts sentiment data to appropriate formats
3. **Database Operations**:
   - Creates Review objects with `status='imported'`
   - Links to App model via foreign key relationship
   - Handles missing or malformed data gracefully
4. **Progress Tracking**: Reports created vs skipped counts

## Data Quality Features

### Error Handling
- **Encoding Issues**: Uses UTF-8 with error ignore mode
- **Missing Fields**: Handles empty/null values gracefully
- **Type Conversion**: Safely converts strings to numbers
- **App Linking**: Skips reviews for non-existent apps
- **Exception Logging**: Logs but continues on individual record errors

### Data Integrity
- **Duplicate Prevention**: Uses `get_or_create()` for apps
- **Foreign Key Validation**: Only links reviews to existing apps
- **Status Tracking**: Marks CSV reviews as 'imported' status
- **Model Validation**: Uses Django model validators

## Current Data Statistics

```
Total Apps: 9,659
Total Reviews: 194,865
Imported Reviews: 194,865 (100%)
User Reviews: 0 (none yet created)
```

## Integration with Application

### Automatic Loading
The data loading is integrated into several startup processes:

1. **Docker Container**: Automatically loads data during container startup
2. **Development Setup**: Included in `setup-dev.sh` script
3. **Manual Setup**: Can be run independently for fresh installations

### Database Models
The CSV data maps to Django models in `core/models.py`:

- **App Model**: Stores all app metadata with full-text search indexes
- **Review Model**: Stores both imported and user-generated reviews
- **Search Integration**: PostgreSQL trigram indexes for efficient search

### Review System Integration
- **Imported Status**: CSV reviews marked as 'imported' (auto-approved)
- **User Reviews**: New reviews default to 'pending' status
- **Supervisor Approval**: User reviews require supervisor approval
- **Mixed Display**: Search results show both imported and approved user reviews

## Performance Considerations

### Import Performance
- **Batch Processing**: Processes one record at a time with error recovery
- **Memory Efficiency**: Uses CSV reader with streaming
- **Progress Reporting**: Shows real-time import statistics
- **Resume Capability**: Can be safely re-run (idempotent)

### Database Performance
- **Indexes**: Optimized indexes for search performance
- **Foreign Keys**: Proper relationships for data integrity
- **Search Optimization**: GIN indexes for full-text search

## Troubleshooting

### Common Issues

**File Not Found Error**
```bash
# Error: Apps file not found: /path/to/googleplaystore.csv
# Solution: Ensure CSV files are in the project root directory
ls -la *.csv
```

**Encoding Issues**
```bash
# Error: UnicodeDecodeError
# Solution: The command uses UTF-8 with error ignore mode
# Check file encoding: file -I googleplaystore.csv
```

**Permission Errors**
```bash
# Error: Permission denied
# Solution: Check file permissions
chmod 644 *.csv
```

**Database Connection Issues**
```bash
# Error: Database connection failed
# Solution: Ensure PostgreSQL is running and accessible
python manage.py check --database
```

### Validation Commands

```bash
# Check data counts
python manage.py shell -c "
from core.models import App, Review;
print(f'Apps: {App.objects.count()}');
print(f'Reviews: {Review.objects.count()}')
"

# Check for data integrity
python manage.py shell -c "
from core.models import App, Review;
apps_with_reviews = Review.objects.values('app').distinct().count();
print(f'Apps with reviews: {apps_with_reviews}');
orphaned_reviews = Review.objects.filter(app__isnull=True).count();
print(f'Orphaned reviews: {orphaned_reviews}')
"

# Sample data inspection
python manage.py shell -c "
from core.models import App;
print('Sample apps:');
for app in App.objects.all()[:5]:
    print(f'  {app.name} - {app.category} - {app.rating}★')
"
```

## Production Considerations

### Security
- **CSV Validation**: Always validate CSV files before importing
- **File Permissions**: Restrict access to CSV files in production
- **Error Logging**: Monitor import logs for security issues

### Scaling
- **Large Files**: For very large CSV files, consider chunked processing
- **Memory Usage**: Monitor memory usage during large imports
- **Database Locks**: Consider running imports during low-traffic periods

### Backup
- **Pre-Import Backup**: Always backup database before major imports
- **Rollback Strategy**: Plan for data rollback if import fails
- **Version Control**: Track CSV file versions and changes

## Example Output

```bash
$ python manage.py load_initial_data

Loading apps from /path/to/franklin/googleplaystore.csv...
Apps loaded: 9659 created, 0 updated

Loading reviews from /path/to/franklin/googleplaystore_user_reviews.csv...
Reviews loaded: 194865 created, 0 skipped

Data import completed!
```

This system provides a robust foundation for loading and managing the Google Play Store dataset while maintaining data integrity and supporting the application's search and review features.