from django.core.management.base import BaseCommand
from django.core.management import CommandError
from accounts.models import CustomUser


class Command(BaseCommand):
    help = 'Create a supervisor user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username for the supervisor')
        parser.add_argument('email', type=str, help='Email for the supervisor')
        parser.add_argument('--first-name', type=str, help='First name', default='')
        parser.add_argument('--last-name', type=str, help='Last name', default='')
        parser.add_argument('--password', type=str, help='Password (if not provided, will prompt)')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        first_name = options['first_name']
        last_name = options['last_name']
        password = options['password']

        # Check if user already exists
        if CustomUser.objects.filter(username=username).exists():
            raise CommandError(f'User "{username}" already exists.')

        if CustomUser.objects.filter(email=email).exists():
            raise CommandError(f'User with email "{email}" already exists.')

        # Get password if not provided
        if not password:
            import getpass
            password = getpass.getpass('Password: ')
            confirm_password = getpass.getpass('Password (again): ')

            if password != confirm_password:
                raise CommandError('Passwords do not match.')

        # Create supervisor user
        try:
            supervisor = CustomUser.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password,
                role='supervisor'
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created supervisor: {supervisor.username}'
                )
            )
            self.stdout.write(f'  Full name: {supervisor.get_full_name()}')
            self.stdout.write(f'  Email: {supervisor.email}')
            self.stdout.write(f'  Role: {supervisor.get_role_display()}')
            self.stdout.write(f'  Is supervisor: {supervisor.is_supervisor()}')

        except Exception as e:
            raise CommandError(f'Error creating supervisor: {str(e)}')