import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import App, Review


class Command(BaseCommand):
    """
    Management command to load initial data from CSV files
    """
    help = 'Load apps and reviews from CSV files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--apps-file',
            type=str,
            default='googleplaystore.csv',
            help='Path to apps CSV file'
        )
        parser.add_argument(
            '--reviews-file',
            type=str,
            default='googleplaystore_user_reviews.csv',
            help='Path to reviews CSV file'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before import'
        )

    def handle(self, *args, **options):
        """Main command handler"""
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            Review.objects.all().delete()
            App.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS('Existing data cleared.')
            )

        # Load apps
        apps_file = os.path.join(settings.BASE_DIR, options['apps_file'])
        if os.path.exists(apps_file):
            self.load_apps(apps_file)
        else:
            self.stdout.write(
                self.style.ERROR(f'Apps file not found: {apps_file}')
            )

        # Load reviews
        reviews_file = os.path.join(settings.BASE_DIR, options['reviews_file'])
        if os.path.exists(reviews_file):
            self.load_reviews(reviews_file)
        else:
            self.stdout.write(
                self.style.ERROR(f'Reviews file not found: {reviews_file}')
            )

        self.stdout.write(
            self.style.SUCCESS('Data import completed!')
        )

    def load_apps(self, file_path):
        """Load apps from CSV file"""
        self.stdout.write(f'Loading apps from {file_path}...')

        apps_created = 0
        apps_updated = 0

        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            reader = csv.DictReader(file)

            for row in reader:
                try:
                    # Clean and prepare data
                    name = row.get('App', '').strip()
                    if not name:
                        continue

                    # Convert rating to float
                    rating = None
                    if row.get('Rating') and row.get('Rating') != 'nan':
                        try:
                            rating = float(row.get('Rating'))
                        except (ValueError, TypeError):
                            rating = None

                    # Convert reviews count
                    reviews_count = 0
                    if row.get('Reviews'):
                        try:
                            reviews_count = int(row.get('Reviews', 0))
                        except (ValueError, TypeError):
                            reviews_count = 0

                    # Create or update app
                    app, created = App.objects.get_or_create(
                        name=name,
                        defaults={
                            'category': row.get('Category', '').strip(),
                            'rating': rating,
                            'reviews_count': reviews_count,
                            'size': row.get('Size', '').strip(),
                            'installs': row.get('Installs', '').strip(),
                            'app_type': row.get('Type', '').strip(),
                            'price': row.get('Price', '').strip(),
                            'content_rating': row.get('Content Rating', '').strip(),
                            'genres': row.get('Genres', '').strip(),
                            'last_updated': row.get('Last Updated', '').strip(),
                            'current_version': row.get('Current Ver', '').strip(),
                            'android_version': row.get('Android Ver', '').strip(),
                        }
                    )

                    if created:
                        apps_created += 1
                    else:
                        apps_updated += 1

                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'Error processing app {name}: {e}')
                    )
                    continue

        self.stdout.write(
            self.style.SUCCESS(
                f'Apps loaded: {apps_created} created, {apps_updated} updated'
            )
        )

    def load_reviews(self, file_path):
        """Load reviews from CSV file"""
        self.stdout.write(f'Loading reviews from {file_path}...')

        reviews_created = 0
        reviews_skipped = 0

        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            reader = csv.DictReader(file)

            for row in reader:
                try:
                    app_name = row.get('App', '').strip()
                    review_text = row.get('Translated_Review', '').strip()

                    # Skip if no app name or review text, or if review is 'nan'
                    if not app_name or not review_text or review_text.lower() == 'nan':
                        reviews_skipped += 1
                        continue

                    # Find the app
                    try:
                        app = App.objects.get(name=app_name)
                    except App.DoesNotExist:
                        reviews_skipped += 1
                        continue

                    # Convert sentiment data
                    sentiment = row.get('Sentiment', '').strip()
                    if sentiment.lower() == 'nan':
                        sentiment = None

                    sentiment_polarity = None
                    if row.get('Sentiment_Polarity') and row.get('Sentiment_Polarity') != 'nan':
                        try:
                            sentiment_polarity = float(row.get('Sentiment_Polarity'))
                        except (ValueError, TypeError):
                            sentiment_polarity = None

                    sentiment_subjectivity = None
                    if row.get('Sentiment_Subjectivity') and row.get('Sentiment_Subjectivity') != 'nan':
                        try:
                            sentiment_subjectivity = float(row.get('Sentiment_Subjectivity'))
                        except (ValueError, TypeError):
                            sentiment_subjectivity = None

                    # Create review
                    Review.objects.create(
                        app=app,
                        review_text=review_text,
                        sentiment=sentiment,
                        sentiment_polarity=sentiment_polarity,
                        sentiment_subjectivity=sentiment_subjectivity,
                        status='imported'  # Mark as imported from CSV
                    )

                    reviews_created += 1

                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'Error processing review: {e}')
                    )
                    reviews_skipped += 1
                    continue

        self.stdout.write(
            self.style.SUCCESS(
                f'Reviews loaded: {reviews_created} created, {reviews_skipped} skipped'
            )
        )