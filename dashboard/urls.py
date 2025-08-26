from django.urls import path
from . import views

urlpatterns = [
    # Vue principale du dashboard
    path('', views.dashboard_view, name='dashboard'),
    
    # APIs pour les données des graphiques
    path('api/chart-data/', views.chart_data_api, name='chart_data_api'),
    path('api/site-details/', views.site_details_api, name='site_details_api'),
    path('api/refresh-data/', views.refresh_data_api, name='refresh_data_api'),
    path('api/sites-list/', views.sites_list_api, name='sites_list_api'),
    
    # Vue de test MongoDB
    path('mongodb-test/', views.mongodb_test_view, name='mongodb_test'),
    
    # Vue pour explorer les collections
    path('collection/<str:collection_name>/', views.collection_data_view, name='collection_data'),
]