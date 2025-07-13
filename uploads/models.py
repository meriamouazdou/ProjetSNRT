# uploads/models.py
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
        ('production', 'Production'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('processed', 'Traité'),
        ('error', 'Erreur'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Nom du fichier")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name="Catégorie")
    csv_file = models.FileField(upload_to='csv_uploads/', verbose_name="Fichier CSV")
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Uploadé par")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'upload")
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name="Date de traitement")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Statut")
    error_message = models.TextField(blank=True, null=True, verbose_name="Message d'erreur")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    row_count = models.IntegerField(default=0, verbose_name="Nombre de lignes")
    
    class Meta:
        verbose_name = "Source CSV"
        verbose_name_plural = "Sources CSV"
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.name} - {self.category} ({self.status})"
    
    def get_file_size(self):
        """Obtenir la taille du fichier en Mo"""
        if self.csv_file:
            return round(self.csv_file.size / (1024*1024), 2)
        return 0

class DynamicData(models.Model):
    """
    Modèle flexible pour stocker les données des CSV
    """
    source = models.ForeignKey(CSVDataSource, on_delete=models.CASCADE, related_name='data_entries')
    row_data = models.JSONField(verbose_name="Données de la ligne")
    row_number = models.IntegerField(verbose_name="Numéro de ligne")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Données dynamiques"
        verbose_name_plural = "Données dynamiques"
        ordering = ['source', 'row_number']
        indexes = [
            models.Index(fields=['source', 'row_number']),
        ]
    
    def __str__(self):
        return f"Ligne {self.row_number} - {self.source.name}"
    
    def get_value(self, column_name):
        """Obtenir la valeur d'une colonne spécifique"""
        return self.row_data.get(column_name, None)

class ProcessingLog(models.Model):
    """
    Modèle pour logger les traitements de fichiers
    """
    source = models.ForeignKey(CSVDataSource, on_delete=models.CASCADE, related_name='processing_logs')
    message = models.TextField(verbose_name="Message")
    level = models.CharField(max_length=10, choices=[
        ('info', 'Info'),
        ('warning', 'Avertissement'),
        ('error', 'Erreur'),
    ], default='info')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Log de traitement"
        verbose_name_plural = "Logs de traitement"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.level.upper()} - {self.source.name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"