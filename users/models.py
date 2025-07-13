

# Create your models here.
 # users/models.py
from django.db import models
from django.contrib.auth.models import User

class UserRole(models.Model):
    """
    Modèle pour gérer les rôles utilisateur et leurs permissions
    """
    ROLE_CHOICES = [
        ('directeur', 'Directeur'),
        ('chef_departement', 'Chef de Département'),
        ('chef_projet', 'Chef de Projet'),
        ('cs', 'CS'),
    ]
    
    CATEGORY_CHOICES = [
        ('rh', 'Ressources Humaines'),
        ('finance', 'Finance'),
        ('projet', 'Gestion de Projet'),
        ('commercial', 'Commercial'),
        ('production', 'Production'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_role')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name="Rôle")
    allowed_categories = models.JSONField(default=list, verbose_name="Catégories autorisées")
    department = models.CharField(max_length=100, blank=True, null=True, verbose_name="Département")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Rôle utilisateur"
        verbose_name_plural = "Rôles utilisateur"
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"
    
    def can_access_category(self, category):
        """Vérifier si l'utilisateur peut accéder à une catégorie"""
        return category in self.allowed_categories
    
    def get_display_name(self):
        """Obtenir le nom d'affichage complet"""
        return f"{self.user.first_name} {self.user.last_name}" if self.user.first_name else self.user.username