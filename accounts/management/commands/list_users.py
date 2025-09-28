from django.core.management.base import BaseCommand
from accounts.models import CustomUser


class Command(BaseCommand):
    help = 'List all users and their roles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--role',
            type=str,
            choices=['regular_user', 'supervisor'],
            help='Filter users by role',
        )
        parser.add_argument(
            '--active-only',
            action='store_true',
            help='Show only active users',
        )

    def handle(self, *args, **options):
        queryset = CustomUser.objects.all()

        # Filter by role if specified
        if options['role']:
            queryset = queryset.filter(role=options['role'])

        # Filter by active status if specified
        if options['active_only']:
            queryset = queryset.filter(is_active=True)

        # Order by role, then by username
        queryset = queryset.order_by('role', 'username')

        if not queryset.exists():
            self.stdout.write(
                self.style.WARNING('No users found matching the criteria.')
            )
            return

        self.stdout.write(f'📋 Found {queryset.count()} user(s):')
        self.stdout.write('')

        current_role = None
        for user in queryset:
            # Group by role
            if current_role != user.role:
                current_role = user.role
                role_display = user.get_role_display()
                self.stdout.write(
                    self.style.SUCCESS(f'👥 {role_display.upper()}S:')
                )

            # User info
            status = '✅ Active' if user.is_active else '❌ Inactive'
            staff_indicator = ' (Staff)' if user.is_staff else ''
            superuser_indicator = ' (Superuser)' if user.is_superuser else ''

            self.stdout.write(f'  • {user.username}{staff_indicator}{superuser_indicator}')
            self.stdout.write(f'    Email: {user.email}')
            self.stdout.write(f'    Name: {user.get_full_name() or "Not provided"}')
            self.stdout.write(f'    Status: {status}')
            self.stdout.write(f'    Last login: {user.last_login or "Never"}')
            self.stdout.write('')