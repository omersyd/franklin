from django.core.management.base import BaseCommand
from django.db.models import Count, Avg, Q
from core.models import App, Review


class Command(BaseCommand):
    help = 'Display data statistics and sample records'

    def add_arguments(self, parser):
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed statistics and samples',
        )
        parser.add_argument(
            '--categories',
            action='store_true',
            help='Show category breakdown',
        )
        parser.add_argument(
            '--samples',
            type=int,
            default=3,
            help='Number of sample records to show (default: 3)',
        )

    def handle(self, *args, **options):
        self.stdout.write('📊 Franklin Search - Data Statistics')
        self.stdout.write('=' * 50)

        # Basic counts
        app_count = App.objects.count()
        review_count = Review.objects.count()
        imported_reviews = Review.objects.filter(status='imported').count()
        user_reviews = Review.objects.exclude(status='imported').count()

        self.stdout.write(f'📱 Total Apps: {app_count:,}')
        self.stdout.write(f'💬 Total Reviews: {review_count:,}')
        self.stdout.write(f'   ├─ Imported (CSV): {imported_reviews:,}')
        self.stdout.write(f'   └─ User Generated: {user_reviews:,}')
        self.stdout.write('')

        if options['detailed']:
            self._show_detailed_stats()

        if options['categories']:
            self._show_category_breakdown()

        self._show_samples(options['samples'])

    def _show_detailed_stats(self):
        self.stdout.write('📈 Detailed Statistics')
        self.stdout.write('-' * 30)

        # App statistics
        rated_apps = App.objects.filter(rating__isnull=False)
        avg_rating = rated_apps.aggregate(avg=Avg('rating'))['avg']
        high_rated = App.objects.filter(rating__gte=4.0).count()

        self.stdout.write(f'⭐ Apps with ratings: {rated_apps.count():,}')
        self.stdout.write(f'📊 Average rating: {avg_rating:.2f}★' if avg_rating else '📊 Average rating: N/A')
        self.stdout.write(f'🌟 High rated (4.0+): {high_rated:,}')

        # Review statistics
        sentiment_stats = Review.objects.filter(
            sentiment__isnull=False
        ).values('sentiment').annotate(
            count=Count('id')
        ).order_by('-count')

        self.stdout.write('')
        self.stdout.write('💭 Review Sentiments:')
        for stat in sentiment_stats:
            self.stdout.write(f'   {stat["sentiment"]}: {stat["count"]:,}')

        self.stdout.write('')

    def _show_category_breakdown(self):
        self.stdout.write('📂 App Categories')
        self.stdout.write('-' * 20)

        categories = App.objects.values('category').annotate(
            app_count=Count('id'),
            review_count=Count('reviews')
        ).order_by('-app_count')[:15]  # Top 15 categories

        for cat in categories:
            self.stdout.write(
                f'  {cat["category"]:<25} {cat["app_count"]:>6} apps, '
                f'{cat["review_count"]:>8} reviews'
            )

        if App.objects.values('category').distinct().count() > 15:
            remaining = App.objects.values('category').distinct().count() - 15
            self.stdout.write(f'  ... and {remaining} more categories')

        self.stdout.write('')

    def _show_samples(self, sample_count):
        self.stdout.write(f'📝 Sample Data (showing {sample_count} records)')
        self.stdout.write('-' * 40)

        # Sample apps
        self.stdout.write('🎮 Sample Apps:')
        sample_apps = App.objects.filter(
            rating__isnull=False
        ).order_by('-rating', '-reviews_count')[:sample_count]

        for app in sample_apps:
            rating_display = f'{app.rating:.1f}★' if app.rating else 'No rating'
            self.stdout.write(f'  • {app.name}')
            self.stdout.write(f'    Category: {app.category} | Rating: {rating_display}')
            self.stdout.write(f'    Reviews: {app.reviews_count:,} | Installs: {app.installs}')
            self.stdout.write('')

        # Sample reviews
        self.stdout.write('💬 Sample Reviews:')
        sample_reviews = Review.objects.filter(
            review_text__isnull=False,
            sentiment__isnull=False
        ).order_by('?')[:sample_count]  # Random sample

        for review in sample_reviews:
            sentiment_emoji = {
                'Positive': '😊',
                'Negative': '😞',
                'Neutral': '😐'
            }.get(review.sentiment, '❓')

            review_preview = review.review_text[:80]
            if len(review.review_text) > 80:
                review_preview += '...'

            self.stdout.write(f'  {sentiment_emoji} {review.app.name}')
            self.stdout.write(f'    "{review_preview}"')
            self.stdout.write(f'    Sentiment: {review.sentiment} | Status: {review.status}')
            self.stdout.write('')

        self.stdout.write('✨ Data inspection complete!')
        self.stdout.write('')
        self.stdout.write('💡 Tip: Use these commands for more data management:')
        self.stdout.write('   • python manage.py load_initial_data --help')
        self.stdout.write('   • python manage.py seed_users')
        self.stdout.write('   • python manage.py list_users')
        self.stdout.write('   • python manage.py inspect_data --detailed --categories')