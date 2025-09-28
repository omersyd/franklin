# Franklin Search - Google Play Store Search Application

A full-stack Django application that enables users to search for Google Play Store apps and manage reviews with an approval workflow.

## 🚀 Current Status: Foundation Complete ✅

**Database Populated**: 9,659 apps and 35,929 reviews loaded
**Docker Deployment**: Running and healthy
**Admin Interface**: Fully functional
**Next Phase**: Search implementation with PostgreSQL trigrams

## Features

- 🔍 **Smart Search**: Text similarity-based search with autocomplete (3+ characters) *[Ready for Implementation]*
- 📱 **App Database**: 9,659 Google Play Store apps with complete metadata ✅
- ⭐ **Review System**: 35,929 user reviews with sentiment analysis ✅
- 👥 **User Management**: Role-based access (Users and Supervisors) ✅
- 🐳 **Docker Ready**: Complete containerized setup ✅
- 📊 **Monitoring**: Status page with database statistics ✅

## Quick Start with Docker

### Prerequisites
- Docker and Docker Compose installed
- Git (to clone the repository)

### Setup Instructions

1. **Clone and navigate to the project**:
   ```bash
   git clone <your-repo-url>
   cd franklin
   ```

2. **Start the application**:
   ```bash
   docker-compose up --build
   ```

3. **Access the application**:
   - **Web Application**: http://localhost:8000
   - **Status Page**: http://localhost:8000/status (database stats)
   - **Django Admin**: http://localhost:8000/admin
   - **Database Stats**: 9,659 apps and 35,929 reviews loaded ✅

4. **Superuser Access** (if needed):
   ```bash
   docker exec -it franklin_web python manage.py createsuperuser
   ```

### What happens during startup:
- PostgreSQL database is created with required extensions
- Django migrations are applied automatically
- Sample data from CSV files is imported
- A superuser account is created
- Web server starts on port 8000

## Development Setup (Local)

If you prefer to run without Docker:

1. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start PostgreSQL** (ensure it's running on localhost:5432)

4. **Run migrations and load data**:
   ```bash
   python manage.py migrate
   python manage.py load_initial_data
   python manage.py createsuperuser
   ```

5. **Start development server**:
   ```bash
   python manage.py runserver
   ```

## Project Structure

```
franklin/
├── docker-compose.yml      # Docker services configuration
├── Dockerfile             # Django app container
├── requirements.txt       # Python dependencies
├── manage.py              # Django management script
├── franklin_search/       # Main Django project
├── core/                  # Core models (App, Review)
├── search/                # Search functionality
├── reviews/               # Review management
├── accounts/              # User management
├── templates/             # HTML templates
├── static/                # CSS, JS, images
└── data/                  # CSV dataset files
```

## API Endpoints

- `GET /api/search/?q=<query>` - Search apps
- `GET /api/apps/<id>/reviews/` - Get app reviews
- `POST /api/reviews/` - Create new review
- `GET /api/reviews/pending/` - Get pending reviews (supervisors)
- `PUT /api/reviews/<id>/approve/` - Approve review

## User Roles

- **Regular User**: Can search apps, view reviews, create reviews
- **Supervisor**: All user permissions + approve/reject reviews

## Stopping the Application

```bash
docker-compose down
```

To remove all data and start fresh:
```bash
docker-compose down -v
docker-compose up --build
```

## Technical Details

- **Backend**: Django 4.2 + Django REST Framework
- **Database**: PostgreSQL with full-text search capabilities
- **Frontend**: Django Templates + Bootstrap + HTMX
- **Search**: PostgreSQL trigram similarity + full-text search
- **Authentication**: Django's built-in auth system