# Franklin Search - Project Requirements Document

## 📋 **Core Requirements Checklist**

### **1. Data Structure & Models**
- [ ] **App Model**: Store data from `googleplaystore.csv`
  - Fields: App name, category, rating, reviews count, size, installs, type, price, content rating, genres, last updated, current version, android version
- [ ] **Review Model**: Store data from `googleplaystore_user_reviews.csv` + new user reviews
  - Fields: App (foreign key), review text, sentiment, sentiment polarity, sentiment subjectivity, user, created_at, status (pending/approved/rejected)
- [ ] **CustomUser Model**: Extend Django User with roles
  - Fields: role (regular_user/supervisor), email, first_name, last_name
- [ ] **ReviewApproval Model**: Track approval workflow
  - Fields: review, supervisor, action (approve/reject), timestamp, comments

### **2. Search Functionality**
- [ ] **Text Similarity Algorithm**: PostgreSQL trigram similarity + full-text search
- [ ] **Autocomplete**: Triggered after 3+ characters typed
  - Should return app name suggestions
  - AJAX-based, real-time
  - Debounced input (300ms delay)
- [ ] **Search Results Page**:
  - Display apps matching search query
  - Show data from googleplaystore.csv
  - Clickable results leading to app detail page
- [ ] **Search Algorithm Features**:
  - Text similarity ranking
  - Consider app popularity (installs, ratings)
  - Fast database queries with indexing

### **3. App Detail & Reviews**
- [ ] **App Detail Page**:
  - Display complete app information
  - Show existing reviews from CSV
  - Reviews categorized by sentiment (positive/negative/neutral)
- [ ] **Reviews Display**:
  - Show reviews from `googleplaystore_user_reviews.csv`
  - Show approved user-submitted reviews
  - Pagination for reviews
  - Filter by sentiment

### **4. User Review System**
- [ ] **Review Creation**:
  - Authenticated users can create reviews
  - Form validation
  - Automatic sentiment analysis (or manual selection)
  - Status: "pending approval"
- [ ] **Review Submission**:
  - Save to database with pending status
  - Send notification to supervisors
  - Show confirmation to user

### **5. Approval Workflow**
- [ ] **Supervisor Dashboard**:
  - List all pending reviews
  - Review details view
  - Approve/Reject actions
  - Add comments to approval decision
- [ ] **Approval Actions**:
  - Approve: Change status to approved, show in public
  - Reject: Change status to rejected, optionally add reason
  - Email notifications to review authors
- [ ] **Supervisor Features**:
  - Bulk approval actions
  - Filter reviews by status/date
  - Search pending reviews

### **6. User Authentication & Authorization**
- [ ] **User Registration**:
  - Standard Django registration
  - Email verification (optional)
  - Default role: regular_user
- [ ] **User Login/Logout**: Standard Django auth
- [ ] **Role-Based Access**:
  - Regular users: search, view, create reviews
  - Supervisors: all above + approve/reject reviews
- [ ] **User Profile**: Basic profile management

### **7. API Endpoints**
- [ ] `GET /api/search/?q=<query>` - Search apps with autocomplete
- [ ] `GET /api/apps/<id>/` - Get app details
- [ ] `GET /api/apps/<id>/reviews/` - Get app reviews (approved only)
- [ ] `POST /api/reviews/` - Create new review (authenticated)
- [ ] `GET /api/reviews/pending/` - Get pending reviews (supervisors only)
- [ ] `PUT /api/reviews/<id>/approve/` - Approve review (supervisors only)
- [ ] `PUT /api/reviews/<id>/reject/` - Reject review (supervisors only)

### **8. Frontend Requirements**
- [ ] **Search Interface**:
  - Search bar with autocomplete dropdown
  - Real-time suggestions (3+ chars)
  - Search results page with app cards
- [ ] **App Detail Page**:
  - App information display
  - Reviews section
  - "Write Review" button (authenticated users)
- [ ] **Review Forms**:
  - Create review form
  - Validation and error handling
- [ ] **Dashboard Pages**:
  - User dashboard (my reviews)
  - Supervisor dashboard (pending approvals)
- [ ] **Responsive Design**: Bootstrap-based, mobile-friendly

### **9. Data Import & Setup**
- [ ] **CSV Import Scripts**:
  - Import `googleplaystore.csv` to App model
  - Import `googleplaystore_user_reviews.csv` to Review model
  - Data cleaning and validation
  - Handle duplicates and malformed data
- [ ] **Database Setup**:
  - PostgreSQL with required extensions
  - Database indexes for fast search
  - Full-text search configuration

### **10. Docker & Deployment**
- [x] **Docker Configuration**:
  - docker-compose.yml with PostgreSQL + Django
  - Dockerfile for Django app
  - Environment configuration
  - Automatic setup scripts
- [x] **Easy Setup**:
  - Single command deployment
  - Automatic migrations
  - Sample data loading
  - Default superuser creation

### **11. Technical Implementation**
- [ ] **Search Algorithm**:
  - PostgreSQL trigram similarity
  - Full-text search with ranking
  - Caching for popular searches
- [ ] **Performance**:
  - Database query optimization
  - Pagination for large result sets
  - Static file handling
- [ ] **Error Handling**:
  - User-friendly error pages
  - API error responses
  - Form validation messages

## 🎯 **Success Criteria**

1. **User can search for apps** with autocomplete working after typing 3 characters
2. **Search results** display apps from the CSV data with clickable links
3. **App detail pages** show complete information and existing reviews
4. **Users can create reviews** that go into pending approval status
5. **Supervisors can approve/reject reviews** through a dashboard
6. **Approved reviews appear** on app detail pages
7. **Entire system runs** with single Docker command
8. **Project is easy to evaluate** with clear setup instructions

## 📊 **Major Checkpoints**

### **Checkpoint 1: Foundation & Models** ⏸️ **(CURRENT)**
- Database models created
- Basic Django setup with Docker
- CSV data import functionality

### **Checkpoint 2: Search Implementation**
- Search API with text similarity
- Autocomplete functionality
- Search results page

### **Checkpoint 3: App Details & Reviews Display**
- App detail pages
- Review display system
- Basic frontend templates

### **Checkpoint 4: User Review System**
- Review creation forms
- User authentication
- Review submission workflow

### **Checkpoint 5: Approval Workflow**
- Supervisor dashboard
- Approval/rejection functionality
- Email notifications

### **Checkpoint 6: Final Polish & Testing**
- UI/UX improvements
- Performance optimization
- Final testing and documentation

## 🤔 **Discussion Points for Each Checkpoint**

- Are we meeting the requirements?
- Any missing functionality?
- Performance considerations?
- User experience feedback?
- Technical implementation questions?