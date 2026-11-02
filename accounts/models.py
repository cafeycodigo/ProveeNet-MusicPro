"""Modelos del módulo accounts."""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import F, Q
from django.utils import timezone


class Usuario(AbstractUser):
    id_usuario = models.BigAutoField(primary_key=True)
    first_name = models.CharField(max_length=100, db_column="nombre")
    last_name = models.CharField(max_length=100, blank=True, db_column="apellido")
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128, db_column="password_hash")
    is_active = models.BooleanField(default=True, db_column="activo")
    date_joined = models.DateTimeField(default=timezone.now, db_column="fecha_registro")

    class Meta:
        db_table = 'usuario'
