from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Custom user model with role-based permissions
    """
    ROLE_CHOICES = [
        ('regular_user', 'Regular User'),
        ('supervisor', 'Supervisor'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='regular_user',
        help_text='User role for permissions'
    )

    email = models.EmailField(
        unique=True,
        help_text='Email address for login and notifications'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    def is_supervisor(self):
        """Check if user is a supervisor"""
        return self.role == 'supervisor'

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
