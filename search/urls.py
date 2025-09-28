from django.urls import path
from . import views

app_name = 'search'

urlpatterns = [
    # API endpoints
    path('api/search/', views.search_apps, name='search_apps'),
    path('api/autocomplete/', views.autocomplete_apps,
         name='autocomplete_apps'),
    path('api/app/<int:app_id>/', views.get_app_details, name='app_details'),
    path('api/app/<int:app_id>/reviews/', views.get_app_reviews,
         name='app_reviews'),
    path('api/categories/', views.get_categories, name='categories'),

    # Web interface
    path('', views.search_page, name='search_page'),
]