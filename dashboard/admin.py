from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import FichierCSV

@admin.register(FichierCSV)
class FichierCSVAdmin(admin.ModelAdmin):
    list_display = ('nom', 'fichier', 'date_import')

