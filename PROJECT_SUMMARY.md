# Franklin Search - Google Play Store Search Application

## Project Overview
A full-stack Django application that provides Google Play Store app search functionality with review management and approval workflow. The application features text similarity search, autocomplete capabilities, and role-based user management.

## 🚀 Key Features
- **Smart Search**: Text similarity search with PostgreSQL trigrams
- **Autocomplete**: Search suggestions after typing 3 characters
- **Review System**: User review submission with sentiment analysis
- **Approval Workflow**: Supervisor approval system for user-generated reviews
- **Role-Based Access**: Regular users and supervisors with different permissions
- **Docker Deployment**: Complete containerized setup for easy deployment

## 📊 Current Status - Foundation Complete ✅

### Database Statistics
- **Apps**: 9,659 Google Play Store applications loaded
- **Reviews**: 35,929 user reviews imported
- **Users**: Custom user model with role-based permissions
- **Infrastructure**: PostgreSQL with trigram extensions for text search

### What's Working
- ✅ Docker containers running smoothly
- ✅ Database fully populated with real data
- ✅ Admin interface accessible
- ✅ Status monitoring page
- ✅ Data import and management commands
- ✅ PostgreSQL trigram extensions configured
- ✅ User authentication system

## 🏗️ Architecture

### Technology Stack
- **Backend**: Django 4.2.7 with Django REST Framework
- **Database**: PostgreSQL 15 with trigram extensions
- **Containerization**: Docker Compose
- **Python Version**: 3.12
- **Port Configuration**: Web (8000), Database (5433)

### Project Structure
```
franklin/
├── accounts/                 # Custom user management
│   ├── models.py            # CustomUser with roles (supervisor/regular_user)
│   └── migrations/          # User model migrations
├── core/                    # Core business logic
│   ├── models.py           # App, Review, ReviewApproval models
│   ├── views.py            # Status view and monitoring
│   ├── admin.py            # Admin interface configuration
│   └── management/         # Custom management commands
│       └── commands/
│           └── load_initial_data.py  # CSV data import
├── search/                 # Search functionality (ready for implementation)
├── reviews/                # Review management (ready for implementation)
├── franklin_search/        # Main Django project
│   ├── settings.py         # Configuration with Docker support
│   └── urls.py            # URL routing
├── docker-compose.yml      # Container orchestration
├── Dockerfile             # Web container definition
├── entrypoint.sh          # Container startup script
└── requirements.txt       # Python dependencies
```

### Database Models

#### CustomUser (accounts/models.py)
- **Purpose**: Role-based user management
- **Key Fields**: role (supervisor/regular_user), standard Django user fields
- **Methods**: is_supervisor() for permission checking

#### App (core/models.py)
- **Purpose**: Google Play Store application data
- **Key Fields**: app_name, category, rating, reviews_count, size, installs, etc.
- **Indexes**: GIN indexes for text search optimization

#### Review (core/models.py)
- **Purpose**: User reviews for applications
- **Key Fields**: app, user, review_text, sentiment, rating, helpful_count
- **Indexes**: Text search indexes for review content

#### ReviewApproval (core/models.py)
- **Purpose**: Approval workflow for user reviews
- **Key Fields**: review, supervisor, status (pending/approved/rejected)
- **Workflow**: Tracks review approval process

## 🐳 Docker Configuration

### Services
1. **Web Service (franklin_web)**
   - Django application server
   - Port: 8000
   - Health checks configured
   - Auto-restart policy

2. **Database Service (franklin_db)**
   - PostgreSQL 15
   - Port: 5433 (to avoid conflicts)
   - Persistent data volume
   - Trigram extension enabled

### Management Commands
- `docker exec franklin_web python manage.py load_initial_data` - Import CSV data
- `docker exec franklin_web python manage.py makemigrations` - Create migrations
- `docker exec franklin_web python manage.py migrate` - Apply migrations
- `docker exec franklin_web python manage.py createsuperuser` - Create admin user

## 📈 Data Import Results
Successfully imported real Google Play Store data:
- **googleplaystore.csv**: 9,659 applications
- **googleplaystore_user_reviews.csv**: 35,929 reviews
- Data cleaning and validation implemented
- Error handling for malformed CSV entries

## 🔗 API Endpoints

### Current Endpoints
- `/` - Welcome page
- `/status/` - Application status and database statistics
- `/admin/` - Django admin interface

### Planned Endpoints (Next Phase)
- `/api/search/` - App search with autocomplete
- `/api/apps/<id>/` - App details
- `/api/reviews/` - Review management
- `/api/reviews/pending/` - Supervisor approval queue

## 🚦 Getting Started

### Quick Start
```bash
# Clone and start the application
cd franklin
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f web

# Access application
open http://localhost:8000
```

### Admin Access
1. Navigate to http://localhost:8000/admin
2. Use superuser credentials created during setup
3. Manage apps, reviews, users, and approval workflow

### Development Commands
```bash
# Create superuser
docker exec -it franklin_web python manage.py createsuperuser

# Django shell
docker exec -it franklin_web python manage.py shell

# Run migrations
docker exec franklin_web python manage.py migrate

# Collect static files
docker exec franklin_web python manage.py collectstatic --noinput
```

## 🎯 Next Development Phase: Search Implementation

### Phase 3: Advanced Search Features
1. **Text Similarity Search**
   - PostgreSQL trigram search implementation
   - Fuzzy matching for app names and descriptions
   - Weighted search results

2. **Autocomplete API**
   - Real-time suggestions after 3 characters
   - Efficient database queries with indexes
   - REST API endpoints

3. **Search Interface**
   - Modern search UI with instant feedback
   - Search filters (category, rating, etc.)
   - Pagination for large result sets

### Phase 4: Review Management
1. **Review Submission**
   - User review creation interface
   - Sentiment analysis integration
   - Spam detection and validation

2. **Supervisor Approval**
   - Review moderation dashboard
   - Bulk approval operations
   - Review analytics and reporting

## 🔧 Technical Considerations

### Performance Optimizations
- Database indexes on search fields
- Connection pooling configured
- Static file serving optimized
- Query optimization for large datasets

### Security Features
- Role-based access control
- CSRF protection enabled
- SQL injection prevention
- Secure password handling

### Scalability Preparations
- Docker containerization for easy scaling
- Database connection management
- Efficient query patterns
- Caching strategy ready for implementation

## 📚 Development Notes

### Key Design Decisions
1. **PostgreSQL Choice**: Selected for trigram text search capabilities
2. **Docker First**: Containerized from start for deployment simplicity
3. **Role-Based Users**: Supervisor/regular user distinction for workflow
4. **Real Data**: Used actual Google Play Store data for realistic testing

### Lessons Learned
1. Docker health checks crucial for reliable container startup
2. PostgreSQL configuration differs from development vs production
3. CSV data cleaning essential for large dataset imports
4. Migration strategy important for model evolution

## 📞 Support Information

### Access Points
- **Application**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **Status Page**: http://localhost:8000/status
- **Database**: localhost:5433

### Key Files for Customization
- `franklin_search/settings.py` - Configuration
- `core/models.py` - Data models
- `docker-compose.yml` - Infrastructure
- `requirements.txt` - Dependencies

### Troubleshooting
- Check container logs: `docker compose logs web`
- Database connection: `docker compose logs db`
- Restart services: `docker compose restart`
- Rebuild if needed: `docker compose up --build

---

**Status**: Foundation Phase Complete ✅
**Next**: Search Implementation Phase
**Ready for**: Production deployment or continued development

The application is fully functional with a solid foundation, populated database, and ready for the next development phase focusing on advanced search capabilities and review management features.