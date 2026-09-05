from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('reader', 'Reader'),
        ('reviewer', 'Reviewer'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='reader')

    def __str__(self):
        return self.username

    def is_reviewer(self):
        return self.role == 'reviewer' or self.is_staff
