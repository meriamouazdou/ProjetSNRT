from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import FichierCSV

@admin.register(FichierCSV)
class FichierCSVAdmin(admin.ModelAdmin):
    list_display = ('nom', 'fichier', 'date_import')

# dashboard/admin.py
from django.contrib import admin
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import CSVDataSource, DynamicData, UserRole, process_csv_file

@admin.register(CSVDataSource)
class CSVDataSourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'uploaded_at', 'is_active', 'data_count']
    list_filter = ['category', 'is_active', 'uploaded_at']
    search_fields = ['name']
    actions = ['process_csv_files', 'activate_sources', 'deactivate_sources']
    
    def data_count(self, obj):
        """Afficher le nombre de lignes de données"""
        return obj.data_entries.count()
    data_count.short_description = "Nombre de lignes"
    
    def process_csv_files(self, request, queryset):
        """Action pour traiter les fichiers CSV sélectionnés"""
        processed = 0
        for csv_source in queryset:
            success, message = process_csv_file(csv_source)
            if success:
                processed += 1
                self.message_user(request, f"{csv_source.name}: {message}", messages.SUCCESS)
            else:
                self.message_user(request, f"{csv_source.name}: {message}", messages.ERROR)
        
        self.message_user(request, f"{processed} fichier(s) traité(s) avec succès.", messages.INFO)
    
    process_csv_files.short_description = "Traiter les fichiers CSV sélectionnés"
    
    def activate_sources(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, "Sources activées avec succès.", messages.SUCCESS)
    activate_sources.short_description = "Activer les sources sélectionnées"
    
    def deactivate_sources(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, "Sources désactivées avec succès.", messages.SUCCESS)
    deactivate_sources.short_description = "Désactiver les sources sélectionnées"
    
    def save_model(self, request, obj, form, change):
        """Traiter automatiquement le CSV après sauvegarde"""
        super().save_model(request, obj, form, change)
        
        # Traiter automatiquement le fichier CSV
        if obj.csv_file:
            success, message = process_csv_file(obj)
            if success:
                messages.success(request, f"Fichier traité automatiquement: {message}")
            else:
                messages.error(request, f"Erreur lors du traitement: {message}")

@admin.register(DynamicData)
class DynamicDataAdmin(admin.ModelAdmin):
    list_display = ['id', 'source', 'created_at', 'preview_data']
    list_filter = ['source', 'created_at']
    search_fields = ['source__name']
    readonly_fields = ['row_data', 'created_at']
    
    def preview_data(self, obj):
        """Aperçu des premières données"""
        data = obj.row_data
        if isinstance(data, dict):
            preview = []
            for key, value in list(data.items())[:3]:  # Première 3 colonnes
                preview.append(f"{key}: {value}")
            return " | ".join(preview)
        return str(data)[:100]
    
    preview_data.short_description = "Aperçu des données"
    
    def has_add_permission(self, request):
        """Empêcher l'ajout manuel - données viennent des CSV"""
        return False

@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'get_allowed_categories']
    list_filter = ['role']
    search_fields = ['user__username', 'user__email']
    
    def get_allowed_categories(self, obj):
        """Afficher les catégories autorisées"""
        return ", ".join(obj.allowed_categories) if obj.allowed_categories else "Aucune"
    get_allowed_categories.short_description = "Catégories autorisées"
    
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """Personnaliser les champs si nécessaire"""
        return super().formfield_for_manytomany(db_field, request, **kwargs)

# Configuration pour personnaliser le titre de l'admin
admin.site.site_header = "Administration Dashboard"
admin.site.site_title = "Dashboard Admin"
admin.site.index_title = "Gestion des Dashboards"