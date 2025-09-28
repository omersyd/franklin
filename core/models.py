from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.postgres.indexes import GinIndex


User = get_user_model()


class App(models.Model):
    """
    Google Play Store App model based on googleplaystore.csv
    """
    # Basic app information
    name = models.CharField(
        max_length=500,
        db_index=True,
        help_text='Application name'
    )
    category = models.CharField(
        max_length=100,
        db_index=True,
        help_text='App category'
    )
    rating = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        help_text='App rating (0-5 stars)'
    )
    reviews_count = models.IntegerField(
        default=0,
        help_text='Number of reviews'
    )
    size = models.CharField(
        max_length=50,
        blank=True,
        help_text='App size (e.g., "19M")'
    )
    installs = models.CharField(
        max_length=50,
        blank=True,
        db_index=True,
        help_text='Number of installs (e.g., "10,000+")'
    )
    app_type = models.CharField(
        max_length=20,
        blank=True,
        help_text='Free or Paid'
    )
    price = models.CharField(
        max_length=20,
        blank=True,
        help_text='App price'
    )
    content_rating = models.CharField(
        max_length=50,
        blank=True,
        help_text='Content rating (Everyone, Teen, etc.)'
    )
    genres = models.TextField(
        blank=True,
        help_text='App genres (semicolon separated)'
    )
    last_updated = models.CharField(
        max_length=100,
        blank=True,
        help_text='Last updated date'
    )
    current_version = models.CharField(
        max_length=100,
        blank=True,
        help_text='Current version'
    )
    android_version = models.CharField(
        max_length=100,
        blank=True,
        help_text='Required Android version'
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'App'
        verbose_name_plural = 'Apps'
        ordering = ['-rating', '-reviews_count']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['category']),
            models.Index(fields=['rating']),
            GinIndex(fields=['name'], name='app_name_gin_idx'),
        ]

    def __str__(self):
        return self.name

    @property
    def install_count_numeric(self):
        """Convert install string to numeric value for sorting"""
        if not self.installs:
            return 0

        installs_str = self.installs.replace(',', '').replace('+', '')
        if 'M' in installs_str:
            return int(float(installs_str.replace('M', '')) * 1000000)
        elif 'K' in installs_str:
            return int(float(installs_str.replace('K', '')) * 1000)
        else:
            try:
                return int(installs_str)
            except (ValueError, TypeError):
                return 0


class Review(models.Model):
    """
    Review model for both CSV data and user-submitted reviews
    """
    STATUS_CHOICES = [
        ('approved', 'Approved'),
        ('pending', 'Pending Approval'),
        ('rejected', 'Rejected'),
        ('imported', 'Imported from CSV'),
    ]

    SENTIMENT_CHOICES = [
        ('Positive', 'Positive'),
        ('Negative', 'Negative'),
        ('Neutral', 'Neutral'),
    ]

    # Core fields
    app = models.ForeignKey(
        App,
        on_delete=models.CASCADE,
        related_name='reviews',
        help_text='Associated app'
    )
    review_text = models.TextField(
        help_text='Review content'
    )

    # Sentiment analysis
    sentiment = models.CharField(
        max_length=10,
        choices=SENTIMENT_CHOICES,
        blank=True,
        null=True,
        help_text='Review sentiment'
    )
    sentiment_polarity = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(-1.0), MaxValueValidator(1.0)],
        help_text='Sentiment polarity (-1 to 1)'
    )
    sentiment_subjectivity = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text='Sentiment subjectivity (0 to 1)'
    )

    # User and approval
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='reviews',
        help_text='Review author (null for imported reviews)'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='imported',
        db_index=True,
        help_text='Review approval status'
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['app', 'status']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['sentiment']),
        ]

    def __str__(self):
        return f"Review for {self.app.name} by {self.user or 'Anonymous'}"

    def is_approved(self):
        """Check if review is approved or imported"""
        return self.status in ['approved', 'imported']


class ReviewApproval(models.Model):
    """
    Track review approval/rejection actions by supervisors
    """
    ACTION_CHOICES = [
        ('approve', 'Approve'),
        ('reject', 'Reject'),
    ]

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='approvals',
        help_text='Review being acted upon'
    )
    supervisor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='review_actions',
        help_text='Supervisor who took action'
    )
    action = models.CharField(
        max_length=10,
        choices=ACTION_CHOICES,
        help_text='Action taken'
    )
    comments = models.TextField(
        blank=True,
        help_text='Optional comments about the decision'
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text='When the action was taken'
    )

    class Meta:
        verbose_name = 'Review Approval'
        verbose_name_plural = 'Review Approvals'
        ordering = ['-timestamp']
        unique_together = ['review', 'supervisor']

    def __str__(self):
        return (
            f"{self.supervisor} {self.action}d review for "
            f"{self.review.app.name}"
        )
