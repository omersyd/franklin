from django.contrib import admin
from .models import App, Review, ReviewApproval


@admin.register(App)
class AppAdmin(admin.ModelAdmin):
    """
    Admin configuration for App model
    """
    list_display = ('name', 'category', 'rating', 'reviews_count', 'installs', 'app_type')
    list_filter = ('category', 'app_type', 'content_rating', 'rating')
    search_fields = ('name', 'genres')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 50

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category', 'rating', 'reviews_count')
        }),
        ('Technical Details', {
            'fields': ('size', 'installs', 'app_type', 'price', 'content_rating')
        }),
        ('Metadata', {
            'fields': ('genres', 'last_updated', 'current_version', 'android_version')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Admin configuration for Review model
    """
    list_display = ('app', 'user', 'sentiment', 'status', 'created_at')
    list_filter = ('status', 'sentiment', 'created_at')
    search_fields = ('app__name', 'review_text', 'user__username')
    readonly_fields = ('created_at', 'updated_at', 'sentiment_polarity', 'sentiment_subjectivity')
    list_per_page = 50

    fieldsets = (
        ('Review Information', {
            'fields': ('app', 'user', 'review_text')
        }),
        ('Sentiment Analysis', {
            'fields': ('sentiment', 'sentiment_polarity', 'sentiment_subjectivity')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('app', 'user')


@admin.register(ReviewApproval)
class ReviewApprovalAdmin(admin.ModelAdmin):
    """
    Admin configuration for ReviewApproval model
    """
    list_display = ('review_app', 'supervisor', 'action', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('review__app__name', 'supervisor__username', 'comments')
    readonly_fields = ('timestamp',)

    def review_app(self, obj):
        return obj.review.app.name
    review_app.short_description = 'App'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('review__app', 'supervisor')
