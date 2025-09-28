from django.core.management.base import BaseCommand
from django.core.management import CommandError
from accounts.models import CustomUser


class Command(BaseCommand):
    help = 'Create seed users (test user and supervisor) for development/testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete existing seed users before creating new ones',
        )
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='Skip creating users that already exist (default behavior)',
        )

    def handle(self, *args, **options):
        self.stdout.write('🌱 Starting user seeding process...')

        # Define seed users
        seed_users = [
            {
                'username': 'testuser',
                'email': 'test@franklin.com',
                'first_name': 'Test',
                'last_name': 'User',
                'password': 'testpass123',
                'role': 'regular_user',
                'is_staff': False,
                'is_superuser': False,
            },
            {
                'username': 'supervisor',
                'email': 'supervisor@franklin.com',
                'first_name': 'Admin',
                'last_name': 'Supervisor',
                'password': 'supervisor123',
                'role': 'supervisor',
                'is_staff': True,
                'is_superuser': False,
            }
        ]

        # Reset users if requested
        if options['reset']:
            self.stdout.write('🗑️  Resetting existing seed users...')
            for user_data in seed_users:
                try:
                    user = CustomUser.objects.get(username=user_data['username'])
                    user.delete()
                    self.stdout.write(
                        self.style.WARNING(f'   Deleted existing user: {user_data["username"]}')
                    )
                except CustomUser.DoesNotExist:
                    pass

        # Create seed users
        created_count = 0
        skipped_count = 0

        for user_data in seed_users:
            username = user_data['username']
            email = user_data['email']

            # Check if user already exists
            if CustomUser.objects.filter(username=username).exists():
                if options['skip_existing'] or not options['reset']:
                    self.stdout.write(
                        self.style.WARNING(f'   User "{username}" already exists, skipping...')
                    )
                    skipped_count += 1
                    continue
                else:
                    raise CommandError(f'User "{username}" already exists. Use --reset to delete existing users.')

            if CustomUser.objects.filter(email=email).exists():
                if options['skip_existing'] or not options['reset']:
                    self.stdout.write(
                        self.style.WARNING(f'   Email "{email}" already exists, skipping...')
                    )
                    skipped_count += 1
                    continue
                else:
                    raise CommandError(f'User with email "{email}" already exists. Use --reset to delete existing users.')

            # Create user
            try:
                user = CustomUser.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    password=user_data['password'],
                    role=user_data['role'],
                    is_staff=user_data['is_staff'],
                    is_superuser=user_data['is_superuser']
                )

                self.stdout.write(
                    self.style.SUCCESS(f'✅ Created {user_data["role"]}: {user.username}')
                )
                self.stdout.write(f'     Full name: {user.get_full_name()}')
                self.stdout.write(f'     Email: {user.email}')
                self.stdout.write(f'     Role: {user.get_role_display()}')
                self.stdout.write(f'     Is supervisor: {user.is_supervisor()}')
                self.stdout.write('')

                created_count += 1

            except Exception as e:
                raise CommandError(f'Error creating user "{username}": {str(e)}')

        # Summary
        self.stdout.write(self.style.SUCCESS('🎉 User seeding completed!'))
        self.stdout.write(f'   Created: {created_count} users')
        self.stdout.write(f'   Skipped: {skipped_count} users')

        if created_count > 0:
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('📝 Login Credentials:'))
            self.stdout.write('   Test User:')
            self.stdout.write('     Username: testuser')
            self.stdout.write('     Password: testpass123')
            self.stdout.write('     Role: Regular User')
            self.stdout.write('')
            self.stdout.write('   Supervisor:')
            self.stdout.write('     Username: supervisor')
            self.stdout.write('     Password: supervisor123')
            self.stdout.write('     Role: Supervisor')
            self.stdout.write('')
            self.stdout.write('🚀 You can now login with these credentials!')