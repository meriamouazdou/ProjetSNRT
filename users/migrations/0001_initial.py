# Generated by Django 5.2.4 on 2025-07-13 10:03

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="UserRole",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("directeur", "Directeur"),
                            ("chef_departement", "Chef de Département"),
                            ("chef_projet", "Chef de Projet"),
                            ("cs", "CS"),
                        ],
                        max_length=20,
                        verbose_name="Rôle",
                    ),
                ),
                (
                    "allowed_categories",
                    models.JSONField(
                        default=list, verbose_name="Catégories autorisées"
                    ),
                ),
                (
                    "department",
                    models.CharField(
                        blank=True,
                        max_length=100,
                        null=True,
                        verbose_name="Département",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user_role",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Rôle utilisateur",
                "verbose_name_plural": "Rôles utilisateur",
            },
        ),
    ]
