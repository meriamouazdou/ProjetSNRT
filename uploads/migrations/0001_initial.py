# Generated by Django 5.2.4 on 2025-07-13 10:04

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
            name="CSVDataSource",
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
                    "name",
                    models.CharField(max_length=100, verbose_name="Nom du fichier"),
                ),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("rh", "Ressources Humaines"),
                            ("finance", "Finance"),
                            ("projet", "Gestion de Projet"),
                            ("commercial", "Commercial"),
                            ("production", "Production"),
                        ],
                        max_length=20,
                        verbose_name="Catégorie",
                    ),
                ),
                (
                    "csv_file",
                    models.FileField(
                        upload_to="csv_uploads/", verbose_name="Fichier CSV"
                    ),
                ),
                (
                    "uploaded_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Date d'upload"
                    ),
                ),
                (
                    "processed_at",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Date de traitement"
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "En attente"),
                            ("processed", "Traité"),
                            ("error", "Erreur"),
                        ],
                        default="pending",
                        max_length=20,
                        verbose_name="Statut",
                    ),
                ),
                (
                    "error_message",
                    models.TextField(
                        blank=True, null=True, verbose_name="Message d'erreur"
                    ),
                ),
                ("is_active", models.BooleanField(default=True, verbose_name="Actif")),
                (
                    "row_count",
                    models.IntegerField(default=0, verbose_name="Nombre de lignes"),
                ),
                (
                    "uploaded_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Uploadé par",
                    ),
                ),
            ],
            options={
                "verbose_name": "Source CSV",
                "verbose_name_plural": "Sources CSV",
                "ordering": ["-uploaded_at"],
            },
        ),
        migrations.CreateModel(
            name="ProcessingLog",
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
                ("message", models.TextField(verbose_name="Message")),
                (
                    "level",
                    models.CharField(
                        choices=[
                            ("info", "Info"),
                            ("warning", "Avertissement"),
                            ("error", "Erreur"),
                        ],
                        default="info",
                        max_length=10,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "source",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="processing_logs",
                        to="uploads.csvdatasource",
                    ),
                ),
            ],
            options={
                "verbose_name": "Log de traitement",
                "verbose_name_plural": "Logs de traitement",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="DynamicData",
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
                ("row_data", models.JSONField(verbose_name="Données de la ligne")),
                ("row_number", models.IntegerField(verbose_name="Numéro de ligne")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "source",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="data_entries",
                        to="uploads.csvdatasource",
                    ),
                ),
            ],
            options={
                "verbose_name": "Données dynamiques",
                "verbose_name_plural": "Données dynamiques",
                "ordering": ["source", "row_number"],
                "indexes": [
                    models.Index(
                        fields=["source", "row_number"],
                        name="uploads_dyn_source__e9f209_idx",
                    )
                ],
            },
        ),
    ]
