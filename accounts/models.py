from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('reader', 'Reader'),

        ('contributor', 'Contributor'),

        ('reviewer', 'Reviewer'),

        ('administrator', 'Administrator'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='reader')

    def __str__(self):
        return self.username
