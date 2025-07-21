from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# 🚨 COMMENTÉ TEMPORAIREMENT - PROBLÈME D'IMPORT
# Importer la vue de redirection si elle est dans monprojet/views.py
#from . import views  # ou commenter si tu ne l'utilises pas ici

urlpatterns = [
    path("admin/", admin.site.urls),
    path("dashboard/", include("dashboard.urls")),
    # 🚨 COMMENTÉ TEMPORAIREMENT - users.urls n'existe pas encore
    #path("users/", include("users.urls")),
   # path("redirect/", views.redirect_after_login, name="redirect_after_login"),  # si cette vue est bien ici
]

# Ajout pour les fichiers média
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)