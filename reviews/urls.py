from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    # API endpoints
    path('api/app/<int:app_id>/reviews/', views.get_app_reviews,
         name='app_reviews'),
    path('api/app/<int:app_id>/submit-review/', views.submit_review,
         name='submit_review'),
    path('api/pending/', views.get_pending_reviews, name='pending_reviews'),
    path('api/approve/<int:approval_id>/', views.approve_review,
         name='approve_review'),
    path('api/dashboard/', views.supervisor_dashboard,
         name='supervisor_dashboard'),

    # Web interface
    path('', views.review_management_page, name='review_management'),
]