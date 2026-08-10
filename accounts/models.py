from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('lector', 'Lector'),
        ('colaborador', 'Colaborador'),
        ('revisor', 'Revisor'),
        ('administrador', 'Administrador'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='lector')

    def __str__(self):
        return self.username
