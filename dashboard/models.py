# dashboards/models.py
from django.db import models
from django.contrib.auth.models import User
from uploads.models import CSVDataSource

class Dashboard(models.Model):
    """
    Modèle pour personnaliser les dashboards par utilisateur
    """
    WIDGET_TYPES = [
        ('chart_bar', 'Graphique en barres'),
        ('chart_pie', 'Graphique en camembert'),
        ('chart_line', 'Graphique en ligne'),
        ('table', 'Tableau'),
        ('metric', 'Métrique'),
        ('list', 'Liste'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dashboards')
    title = models.CharField(max_length=200, verbose_name="Titre du dashboard")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    is_default = models.BooleanField(default=False, verbose_name="Dashboard par défaut")
    layout_config = models.JSONField(default=dict, verbose_name="Configuration du layout")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Dashboard"
        verbose_name_plural = "Dashboards"
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"

class Widget(models.Model):
    """
    Modèle pour les widgets des dashboards
    """
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name='widgets')
    title = models.CharField(max_length=200, verbose_name="Titre du widget")
    widget_type = models.CharField(max_length=20, choices=Dashboard.WIDGET_TYPES, verbose_name="Type de widget")
    data_source = models.ForeignKey(CSVDataSource, on_delete=models.CASCADE, verbose_name="Source de données")
    config = models.JSONField(default=dict, verbose_name="Configuration du widget")
    position_x = models.IntegerField(default=0, verbose_name="Position X")
    position_y = models.IntegerField(default=0, verbose_name="Position Y")
    width = models.IntegerField(default=6, verbose_name="Largeur")
    height = models.IntegerField(default=4, verbose_name="Hauteur")
    is_visible = models.BooleanField(default=True, verbose_name="Visible")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Widget"
        verbose_name_plural = "Widgets"
        ordering = ['position_y', 'position_x']
    
    def __str__(self):
        return f"{self.dashboard.title} - {self.title}"

class UserPreferences(models.Model):
    """
    Modèle pour les préférences utilisateur
    """
    THEME_CHOICES = [
        ('light', 'Clair'),
        ('dark', 'Sombre'),
        ('auto', 'Automatique'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='light', verbose_name="Thème")
    language = models.CharField(max_length=10, default='fr', verbose_name="Langue")
    timezone = models.CharField(max_length=50, default='Europe/Paris', verbose_name="Fuseau horaire")
    notifications_enabled = models.BooleanField(default=True, verbose_name="Notifications activées")
    default_dashboard = models.ForeignKey(Dashboard, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Dashboard par défaut")
    refresh_interval = models.IntegerField(default=300, verbose_name="Intervalle de rafraîchissement (secondes)")
    
    class Meta:
        verbose_name = "Préférences utilisateur"
        verbose_name_plural = "Préférences utilisateur"
    
    def __str__(self):
        return f"Préférences de {self.user.username}"