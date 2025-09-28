from django.shortcuts import render
from django.db.models import Q
from django.contrib.postgres.search import TrigramSimilarity
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from core.models import App, Review


@api_view(['GET'])
def search_apps(request):
    """
    Advanced search for apps using PostgreSQL trigram similarity
    Supports fuzzy matching and autocomplete functionality with pagination
    """
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '')
    min_rating = request.GET.get('min_rating', '')
    limit = int(request.GET.get('limit', 20))
    page = int(request.GET.get('page', 1))

    if len(query) < 3:
        return Response({
            'error': 'Query must be at least 3 characters long',
            'results': [],
            'count': 0,
            'pagination': {'page': page, 'pages': 0, 'total': 0}
        }, status=status.HTTP_400_BAD_REQUEST)

    # Base queryset
    apps = App.objects.all()

    # Apply filters
    if category:
        apps = apps.filter(category__iexact=category)

    if min_rating:
        try:
            min_rating = float(min_rating)
            apps = apps.filter(rating__gte=min_rating)
        except ValueError:
            pass

    # Text search using trigrams with improved logic
    apps = apps.annotate(
        name_similarity=TrigramSimilarity('name', query),
        # Add more fields for similarity search
    ).filter(
        Q(name_similarity__gt=0.3) |  # Higher similarity threshold (30%)
        Q(name__istartswith=query) |  # Exact prefix match (high priority)
        Q(name__icontains=f' {query}') |  # Query as separate word
        Q(name__icontains=f'{query} ') |  # Query followed by space (word boundary)
        (Q(name__icontains=query) & Q(name_similarity__gt=0.2))  # Contains + some similarity
    ).order_by('-name_similarity', '-rating', '-reviews_count')

    # Get total count before pagination
    total_count = apps.count()
    total_pages = (total_count + limit - 1) // limit

    # Apply pagination
    offset = (page - 1) * limit
    apps = apps[offset:offset + limit]

    # Prepare results
    results = []
    for app in apps:
        # Handle invalid float values
        rating = app.rating
        if rating is not None and (
            rating != rating or
            rating == float('inf') or
            rating == float('-inf')
        ):
            rating = None

        similarity_score = getattr(app, 'name_similarity', 0)
        if (similarity_score != similarity_score or
                similarity_score == float('inf') or
                similarity_score == float('-inf')):
            similarity_score = 0

        results.append({
            'id': app.id,
            'name': app.name,
            'category': app.category,
            'rating': rating,
            'reviews_count': app.reviews_count,
            'installs': app.installs,
            'app_type': app.app_type,
            'similarity_score': (
                float(similarity_score) if similarity_score else 0
            ),
        })

    return Response({
        'results': results,
        'count': total_count,  # Total count of all matching results
        'query': query,
        'filters': {
            'category': category,
            'min_rating': min_rating,
        },
        'pagination': {
            'page': page,
            'pages': total_pages,
            'total': total_count,
            'per_page': limit,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    })


@api_view(['GET'])
def autocomplete_apps(request):
    """
    Autocomplete suggestions for app names
    Triggered after typing 3+ characters
    """
    query = request.GET.get('q', '').strip()
    limit = int(request.GET.get('limit', 10))

    if len(query) < 3:
        return Response({
            'suggestions': [],
            'count': 0
        })

    # Get app name suggestions using trigram similarity
    apps = App.objects.annotate(
        similarity=TrigramSimilarity('name', query)
    ).filter(
        Q(similarity__gt=0.2) |  # Higher threshold for autocomplete
        Q(name__istartswith=query)  # Prefix matching
    ).order_by('-similarity', '-rating')[:limit]

    suggestions = []
    for app in apps:
        # Handle invalid float values
        rating = app.rating
        if rating is not None and (
            rating != rating or
            rating == float('inf') or
            rating == float('-inf')
        ):
            rating = None

        suggestions.append({
            'id': app.id,
            'name': app.name,
            'category': app.category,
            'rating': rating,
        })

    return Response({
        'suggestions': suggestions,
        'count': len(suggestions),
        'query': query
    })


@api_view(['GET'])
def get_app_details(request, app_id):
    """
    Get detailed information about a specific app
    """
    try:
        app = App.objects.get(id=app_id)

        # Get recent reviews for this app
        recent_reviews = Review.objects.filter(app=app).order_by(
            '-created_at'
        )[:5]

        app_data = {
            'id': app.id,
            'name': app.name,
            'category': app.category,
            'rating': app.rating,
            'reviews_count': app.reviews_count,
            'size': app.size,
            'installs': app.installs,
            'app_type': app.app_type,
            'recent_reviews': [
                {
                    'id': review.id,
                    'review_text': (
                        review.review_text[:200] + '...'
                        if len(review.review_text) > 200
                        else review.review_text
                    ),
                    'sentiment': review.sentiment,
                    'rating': review.rating,
                    'created_at': review.created_at,
                }
                for review in recent_reviews
            ]
        }

        return Response(app_data)

    except App.DoesNotExist:
        return Response({
            'error': 'App not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_categories(request):
    """
    Get all available app categories
    """
    categories = App.objects.values_list(
        'category', flat=True
    ).distinct().order_by('category')
    return Response({
        'categories': list(categories)
    })


@api_view(['GET'])
def get_app_reviews(request, app_id):
    """
    Get reviews for a specific app with pagination
    """
    try:
        app = App.objects.get(id=app_id)

        # Get pagination parameters
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 10))
        offset = (page - 1) * limit

        # Get reviews for this app - only approved and imported reviews for public view
        reviews = Review.objects.filter(
            app=app,
            status__in=['approved', 'imported']
        ).select_related('app')
        reviews = reviews.order_by('-created_at', 'id')[offset:offset + limit]
        total_reviews = Review.objects.filter(
            app=app,
            status__in=['approved', 'imported']
        ).count()

        # Serialize reviews data
        reviews_data = []
        for review in reviews:
            review_dict = {
                'id': review.id,
                'review_text': review.review_text,
                'sentiment': review.sentiment,
                'sentiment_polarity': review.sentiment_polarity,
                'sentiment_subjectivity': review.sentiment_subjectivity,
                'rating': review.rating,  # Include user rating
                'created_at': (
                    review.created_at.isoformat()
                    if review.created_at else None
                ),
                'user': review.user.username if review.user else None,
                # Note: status field removed for security - public API should not expose internal status
            }
            reviews_data.append(review_dict)

        return Response({
            'app': {
                'id': app.id,
                'name': app.name,
                'category': app.category,
                'rating': app.rating,
                'reviews_count': app.reviews_count,
                'installs': app.installs,
                'app_type': app.app_type,
            },
            'reviews': reviews_data,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total_reviews,
                'pages': (total_reviews + limit - 1) // limit,
            }
        })

    except App.DoesNotExist:
        return Response({
            'error': 'App not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except ValueError:
        return Response({
            'error': 'Invalid parameters'
        }, status=status.HTTP_400_BAD_REQUEST)


def search_page(request):
    """
    Render the search interface page
    """
    context = {
        'title': 'Search Apps',
        'placeholder_text': 'Search for apps... (min 3 characters)',
        'is_authenticated': request.user.is_authenticated,
        'username': request.user.username if request.user.is_authenticated else None,
    }
    return render(request, 'search/search.html', context)
