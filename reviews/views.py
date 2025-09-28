from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from core.models import App, Review, ReviewApproval


@api_view(['GET'])
def get_app_reviews(request, app_id):
    """
    Get reviews for a specific app
    """
    try:
        app = App.objects.get(id=app_id)

        # Get query parameters
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 10))
        sentiment_filter = request.GET.get('sentiment', '')
        min_rating = request.GET.get('min_rating', '')

        # Base queryset - only approved or imported reviews for public viewing
        reviews = Review.objects.filter(
            app=app,
            status__in=['approved', 'imported']
        ).select_related('user')

        # Apply filters
        if sentiment_filter:
            reviews = reviews.filter(sentiment=sentiment_filter)

        if min_rating:
            try:
                min_rating = float(min_rating)
                # Note: Review model doesn't have rating field
                # in current structure
                # Will need to add this field or use sentiment as proxy
            except ValueError:
                pass

        # Pagination
        start = (page - 1) * limit
        end = start + limit
        paginated_reviews = reviews.order_by('-created_at')[start:end]

        # Prepare response
        review_data = []
        for review in paginated_reviews:
            review_data.append({
                'id': review.id,
                'review_text': review.review_text,
                'sentiment': review.sentiment,
                'sentiment_polarity': review.sentiment_polarity,
                'user': review.user.username if review.user else 'Anonymous',
                'rating': review.rating,  # Include user rating
                'created_at': review.created_at,
                # Note: status is NOT included in public API for security
            })

        total_count = reviews.count()

        return Response({
            'app': {
                'id': app.id,
                'name': app.name,
                'category': app.category,
            },
            'reviews': review_data,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total_count,
                'has_next': end < total_count,
                'has_previous': page > 1,
            }
        })

    except App.DoesNotExist:
        return Response({
            'error': 'App not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_review(request, app_id):
    """
    Submit a new review for an app (requires authentication)
    """
    try:
        app = App.objects.get(id=app_id)

        # Check if user already reviewed this app
        existing_review = Review.objects.filter(
            app=app,
            user=request.user
        ).first()

        if existing_review:
            return Response({
                'error': 'You have already reviewed this app'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get review data
        review_text = request.data.get('review_text', '').strip()
        rating = request.data.get('rating')

        # Validate input
        if not review_text or len(review_text) < 10:
            return Response({
                'error': 'Review text must be at least 10 characters long'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            rating = float(rating)
            if not (1 <= rating <= 5):
                raise ValueError
        except (ValueError, TypeError):
            return Response({
                'error': 'Rating must be a number between 1 and 5'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Simple sentiment analysis based on rating
        if rating >= 4:
            sentiment = 'Positive'
        elif rating >= 3:
            sentiment = 'Neutral'
        else:
            sentiment = 'Negative'

        # Create review with pending status for user-submitted reviews
        review = Review.objects.create(
            app=app,
            user=request.user,
            review_text=review_text,
            sentiment=sentiment,
            rating=rating,
            status='pending'  # User-submitted reviews need approval
        )

        return Response({
            'message': 'Review submitted successfully and is pending approval',
            'review': {
                'id': review.id,
                'review_text': review.review_text,
                'sentiment': review.sentiment,
                'rating': review.rating,
                'status': 'pending',
                'created_at': review.created_at,
            }
        }, status=status.HTTP_201_CREATED)

    except App.DoesNotExist:
        return Response({
            'error': 'App not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_pending_reviews(request):
    """
    Get pending reviews for supervisor approval
    (Only accessible by supervisors)
    """
    if not request.user.is_supervisor():
        return Response({
            'error': 'Access denied. Supervisor privileges required.'
        }, status=status.HTTP_403_FORBIDDEN)

    # Get query parameters
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 20))

    # Get pending reviews
    pending_reviews = ReviewApproval.objects.filter(
        status='pending'
    ).select_related('review', 'review__app', 'review__user').order_by(
        'created_at'
    )

    # Pagination
    start = (page - 1) * limit
    end = start + limit
    paginated_reviews = pending_reviews[start:end]

    # Prepare response
    review_data = []
    for approval in paginated_reviews:
        review = approval.review
        review_data.append({
            'approval_id': approval.id,
            'review_id': review.id,
            'app': {
                'id': review.app.id,
                'name': review.app.name,
                'category': review.app.category,
            },
            'user': review.user.username if review.user else 'Anonymous',
            'review_text': review.review_text,
            'sentiment': review.sentiment,
            'rating': review.rating,
            'submitted_at': review.created_at,
            'days_pending': (
                approval.created_at - review.created_at
            ).days if approval.created_at else 0,
        })

    total_count = pending_reviews.count()

    return Response({
        'reviews': review_data,
        'pagination': {
            'page': page,
            'limit': limit,
            'total': total_count,
            'has_next': end < total_count,
            'has_previous': page > 1,
        },
        'stats': {
            'total_pending': total_count,
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_review(request, approval_id):
    """
    Approve or reject a pending review
    (Only accessible by supervisors)
    """
    if not request.user.is_supervisor():
        return Response({
            'error': 'Access denied. Supervisor privileges required.'
        }, status=status.HTTP_403_FORBIDDEN)

    try:
        approval = ReviewApproval.objects.select_related(
            'review', 'review__app'
        ).get(id=approval_id)

        if approval.status != 'pending':
            return Response({
                'error': 'Review has already been processed'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get action from request
        action = request.data.get('action')  # 'approve' or 'reject'
        supervisor_notes = request.data.get('notes', '').strip()

        if action not in ['approve', 'reject']:
            return Response({
                'error': 'Action must be either "approve" or "reject"'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Update approval record
        approval.status = 'approved' if action == 'approve' else 'rejected'
        approval.supervisor = request.user
        approval.supervisor_notes = supervisor_notes
        approval.save()

        return Response({
            'message': f'Review {action}d successfully',
            'review': {
                'id': approval.review.id,
                'app_name': approval.review.app.name,
                'status': approval.status,
                'supervisor_notes': approval.supervisor_notes,
                'processed_by': request.user.username,
                'processed_at': approval.updated_at,
            }
        })

    except ReviewApproval.DoesNotExist:
        return Response({
            'error': 'Review approval record not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def supervisor_dashboard(request):
    """
    Get supervisor dashboard statistics
    """
    if not request.user.is_supervisor():
        return Response({
            'error': 'Access denied. Supervisor privileges required.'
        }, status=status.HTTP_403_FORBIDDEN)

    # Get statistics
    stats = {
        'pending_reviews': ReviewApproval.objects.filter(
            status='pending'
        ).count(),
        'approved_reviews': ReviewApproval.objects.filter(
            status='approved'
        ).count(),
        'rejected_reviews': ReviewApproval.objects.filter(
            status='rejected'
        ).count(),
        'total_reviews': Review.objects.count(),
        'reviews_by_me': ReviewApproval.objects.filter(
            supervisor=request.user,
            status__in=['approved', 'rejected']
        ).count(),
        'recent_activity': ReviewApproval.objects.filter(
            status__in=['approved', 'rejected'],
            updated_at__isnull=False
        ).order_by('-updated_at')[:5].values(
            'review__app__name',
            'status',
            'supervisor__username',
            'updated_at'
        )
    }

    return Response(stats)


def review_management_page(request):
    """
    Render the review management interface
    """
    context = {
        'title': 'Review Management',
        'is_supervisor': (
            request.user.is_authenticated and
            request.user.is_supervisor()
        ),
    }
    return render(request, 'reviews/review_management.html', context)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_pending_reviews(request):
    """
    Get all pending reviews for supervisor approval
    """
    # Check if user is supervisor
    if not request.user.is_supervisor():
        return Response({
            'error': 'Access denied. Supervisor privileges required.'
        }, status=status.HTTP_403_FORBIDDEN)

    # Get query parameters
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 20))

    # Get pending reviews
    reviews = Review.objects.filter(
        status='pending'
    ).select_related('user', 'app').order_by('-created_at')

    # Pagination
    start = (page - 1) * limit
    end = start + limit
    total_count = reviews.count()
    paginated_reviews = reviews[start:end]

    # Prepare response
    review_data = []
    for review in paginated_reviews:
        review_data.append({
            'id': review.id,
            'app_name': review.app.name,
            'app_id': review.app.id,
            'user_name': review.user.username if review.user else 'Anonymous',
            'user_full_name': review.user.get_full_name() if review.user else 'Anonymous',
            'review_text': review.review_text,
            'rating': review.rating,
            'sentiment': review.sentiment,
            'created_at': review.created_at,
            'status': review.status
        })

    return Response({
        'reviews': review_data,
        'pagination': {
            'current_page': page,
            'total_pages': (total_count + limit - 1) // limit,
            'total_count': total_count,
            'has_next': end < total_count,
            'has_previous': page > 1
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_review(request, review_id):
    """
    Approve a pending review
    """
    # Check if user is supervisor
    if not request.user.is_supervisor():
        return Response({
            'error': 'Access denied. Supervisor privileges required.'
        }, status=status.HTTP_403_FORBIDDEN)

    try:
        review = Review.objects.get(id=review_id, status='pending')
        comments = request.data.get('comments', '')

        # Update review status
        review.status = 'approved'
        review.save()

        # Create approval record
        ReviewApproval.objects.create(
            review=review,
            supervisor=request.user,
            action='approve',
            comments=comments
        )

        return Response({
            'message': 'Review approved successfully',
            'review_id': review.id
        })

    except Review.DoesNotExist:
        return Response({
            'error': 'Review not found or already processed'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_review(request, review_id):
    """
    Reject a pending review
    """
    # Check if user is supervisor
    if not request.user.is_supervisor():
        return Response({
            'error': 'Access denied. Supervisor privileges required.'
        }, status=status.HTTP_403_FORBIDDEN)

    try:
        review = Review.objects.get(id=review_id, status='pending')
        comments = request.data.get('comments', '')

        # Update review status
        review.status = 'rejected'
        review.save()

        # Create approval record
        ReviewApproval.objects.create(
            review=review,
            supervisor=request.user,
            action='reject',
            comments=comments
        )

        return Response({
            'message': 'Review rejected successfully',
            'review_id': review.id
        })

    except Review.DoesNotExist:
        return Response({
            'error': 'Review not found or already processed'
        }, status=status.HTTP_404_NOT_FOUND)
