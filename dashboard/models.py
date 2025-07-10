from django.db import models

# Create your models here.
# dashboard/models.py
from django.db import models
from django.contrib.auth.models import User
import pandas as pd
import os
from django.conf import settings

class CSVDataSource(models.Model):
    """
    Modèle pour gérer les sources de données CSV
    """
    CATEGORY_CHOICES = [
        ('rh', 'Ressources Humaines'),
        ('finance', 'Finance'),
        ('projet', 'Gestion de Projet'),
        ('commercial', 'Commercial'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Nom du fichier")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name="Catégorie")
    csv_file = models.FileField(upload_to='csv_uploads/', verbose_name="Fichier CSV")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'upload")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    
    class Meta:
        verbose_name = "Source CSV"
        verbose_name_plural = "Sources CSV"
    
    def __str__(self):
        return f"{self.name} - {self.category}"

class DynamicData(models.Model):
    """
    Modèle flexible pour stocker les données des CSV
    """
    source = models.ForeignKey(CSVDataSource, on_delete=models.CASCADE, related_name='data_entries')
    row_data = models.JSONField(verbose_name="Données de la ligne")  # Stockage flexible des données
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Données dynamiques"
        verbose_name_plural = "Données dynamiques"
    
    def __str__(self):
        return f"Data from {self.source.name} - Row {self.id}"

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
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_role')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name="Rôle")
    allowed_categories = models.JSONField(default=list, verbose_name="Catégories autorisées")
    
    class Meta:
        verbose_name = "Rôle utilisateur"
        verbose_name_plural = "Rôles utilisateur"
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"

# Fonctions utilitaires pour traiter les CSV
def process_csv_file(csv_source):
    """
    Fonction pour traiter un fichier CSV et l'importer en base
    """
    try:
        # Lire le fichier CSV avec pandas
        df = pd.read_csv(csv_source.csv_file.path)
        
        # Nettoyer les données
        df = df.dropna(how='all')  # Supprimer les lignes vides
        df.columns = df.columns.str.strip()  # Nettoyer les noms de colonnes
        
        # Supprimer les anciennes données de cette source
        DynamicData.objects.filter(source=csv_source).delete()
        
        # Créer les nouvelles entrées
        data_entries = []
        for _, row in df.iterrows():
            # Convertir la ligne en dictionnaire
            row_dict = row.to_dict()
            
            # Créer l'entrée
            data_entry = DynamicData(
                source=csv_source,
                row_data=row_dict
            )
            data_entries.append(data_entry)
        
        # Sauvegarder en bulk pour optimiser les performances
        DynamicData.objects.bulk_create(data_entries)
        
        return True, f"Fichier traité avec succès. {len(data_entries)} lignes importées."
        
    except Exception as e:
        return False, f"Erreur lors du traitement : {str(e)}"

def get_user_data(user, category=None):
    """
    Fonction pour récupérer les données autorisées pour un utilisateur
    """
    try:
        user_role = user.user_role
        allowed_categories = user_role.allowed_categories
        
        # Filtrer les sources selon les catégories autorisées
        sources = CSVDataSource.objects.filter(
            category__in=allowed_categories,
            is_active=True
        )
        
        if category:
            sources = sources.filter(category=category)
        
        # Récupérer les données
        data = DynamicData.objects.filter(source__in=sources)
        
        return data
        
    except UserRole.DoesNotExist:
        return DynamicData.objects.none()