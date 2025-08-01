# Generated by Django 5.2.4 on 2025-07-13 10:04

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("uploads", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Dashboard",
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
                    "title",
                    models.CharField(max_length=200, verbose_name="Titre du dashboard"),
                ),
                (
                    "description",
                    models.TextField(blank=True, null=True, verbose_name="Description"),
                ),
                (
                    "is_default",
                    models.BooleanField(
                        default=False, verbose_name="Dashboard par défaut"
                    ),
                ),
                (
                    "layout_config",
                    models.JSONField(
                        default=dict, verbose_name="Configuration du layout"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="dashboards",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Dashboard",
                "verbose_name_plural": "Dashboards",
                "ordering": ["-updated_at"],
            },
        ),
        migrations.CreateModel(
            name="UserPreferences",
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
                    "theme",
                    models.CharField(
                        choices=[
                            ("light", "Clair"),
                            ("dark", "Sombre"),
                            ("auto", "Automatique"),
                        ],
                        default="light",
                        max_length=10,
                        verbose_name="Thème",
                    ),
                ),
                (
                    "language",
                    models.CharField(
                        default="fr", max_length=10, verbose_name="Langue"
                    ),
                ),
                (
                    "timezone",
                    models.CharField(
                        default="Europe/Paris",
                        max_length=50,
                        verbose_name="Fuseau horaire",
                    ),
                ),
                (
                    "notifications_enabled",
                    models.BooleanField(
                        default=True, verbose_name="Notifications activées"
                    ),
                ),
                (
                    "refresh_interval",
                    models.IntegerField(
                        default=300,
                        verbose_name="Intervalle de rafraîchissement (secondes)",
                    ),
                ),
                (
                    "default_dashboard",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="dashboard.dashboard",
                        verbose_name="Dashboard par défaut",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="preferences",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Préférences utilisateur",
                "verbose_name_plural": "Préférences utilisateur",
            },
        ),
        migrations.CreateModel(
            name="Widget",
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
                    "title",
                    models.CharField(max_length=200, verbose_name="Titre du widget"),
                ),
                (
                    "widget_type",
                    models.CharField(
                        choices=[
                            ("chart_bar", "Graphique en barres"),
                            ("chart_pie", "Graphique en camembert"),
                            ("chart_line", "Graphique en ligne"),
                            ("table", "Tableau"),
                            ("metric", "Métrique"),
                            ("list", "Liste"),
                        ],
                        max_length=20,
                        verbose_name="Type de widget",
                    ),
                ),
                (
                    "config",
                    models.JSONField(
                        default=dict, verbose_name="Configuration du widget"
                    ),
                ),
                (
                    "position_x",
                    models.IntegerField(default=0, verbose_name="Position X"),
                ),
                (
                    "position_y",
                    models.IntegerField(default=0, verbose_name="Position Y"),
                ),
                ("width", models.IntegerField(default=6, verbose_name="Largeur")),
                ("height", models.IntegerField(default=4, verbose_name="Hauteur")),
                (
                    "is_visible",
                    models.BooleanField(default=True, verbose_name="Visible"),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "dashboard",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="widgets",
                        to="dashboard.dashboard",
                    ),
                ),
                (
                    "data_source",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="uploads.csvdatasource",
                        verbose_name="Source de données",
                    ),
                ),
            ],
            options={
                "verbose_name": "Widget",
                "verbose_name_plural": "Widgets",
                "ordering": ["position_y", "position_x"],
            },
        ),
    ]
