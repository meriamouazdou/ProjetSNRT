from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import logging
from .services import (
    get_dashboard_stats, 
    get_region_distribution, 
    get_services_distribution,
    get_site_details,
    get_category_distribution,
    get_services_by_region,
    get_all_site_names,
    snrt_service
)

logger = logging.getLogger(__name__)

def dashboard_view(request):
    """Vue principale du dashboard avec données MongoDB réelles"""
    try:
        # Récupérer toutes les données réelles de MongoDB
        stats = get_dashboard_stats()
        region_data = get_region_distribution()
        services_data = get_services_distribution()
        category_data = get_category_distribution()
        services_by_region_data = get_services_by_region()
        site_names = get_all_site_names()
        
        # Préparer le contexte avec UNIQUEMENT les données MongoDB
        context = {
            'stats': stats,
            'regions_data': region_data,
            'services_data': services_data,
            'category_data': category_data,
            'services_by_region_data': services_by_region_data,
            'site_names': site_names,
            'mongodb_connected': True
        }
        
        logger.info(f"Dashboard chargé avec {stats['total_sites']} sites depuis MongoDB")
        
        return render(request, 'dashboard/tableau.html', context)
        
    except Exception as e:
        logger.error(f"Erreur dans dashboard_view: {e}")
        # En cas d'erreur MongoDB, afficher un message d'erreur
        context = {
            'mongodb_connected': False,
            'error_message': f"Erreur de connexion à MongoDB: {str(e)}",
            'stats': {
                'total_sites': 0,
                'services_tnt': 0,
                'services_fm': 0,
                'control_count': 0
            },
            'regions_data': {'regions': [], 'counts': [], 'colors': []},
            'services_data': {'services': [], 'counts': [], 'colors': []},
            'category_data': {'categories': [], 'counts': [], 'colors': []},
            'services_by_region_data': {'regions': [], 'datasets': []},
            'site_names': []
        }
        return render(request, 'dashboard/tableau.html', context)

@csrf_exempt
def chart_data_api(request):
    """API pour fournir les données des graphiques en JSON (données réelles MongoDB)"""
    try:
        chart_type = request.GET.get('type', 'regions')
        
        if chart_type == 'regions':
            data = get_region_distribution()
        elif chart_type == 'services':
            data = get_services_distribution()
        elif chart_type == 'categories':
            data = get_category_distribution()
        elif chart_type == 'services_by_region':
            data = get_services_by_region()
        elif chart_type == 'stats':
            data = get_dashboard_stats()
        else:
            return JsonResponse({'error': 'Type de données non supporté'}, status=400)
        
        return JsonResponse({
            'success': True,
            'data': data,
            'type': chart_type,
            'source': 'mongodb'
        })
        
    except Exception as e:
        logger.error(f"Erreur API chart_data: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
def site_details_api(request):
    """API pour récupérer les détails d'un site (données réelles MongoDB)"""
    try:
        site_name = request.GET.get('site')
        if not site_name:
            return JsonResponse({'error': 'Nom de site requis'}, status=400)
        
        details = get_site_details(site_name)
        
        if not details:
            return JsonResponse({
                'error': 'Site non trouvé dans MongoDB',
                'site': site_name
            }, status=404)
        
        return JsonResponse({
            'success': True,
            'data': details,
            'source': 'mongodb'
        })
        
    except Exception as e:
        logger.error(f"Erreur site details: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def refresh_data_api(request):
    """API pour rafraîchir toutes les données du dashboard"""
    try:
        # Récupérer toutes les données fraîches
        data = {
            'stats': get_dashboard_stats(),
            'regions': get_region_distribution(),
            'services': get_services_distribution(),
            'categories': get_category_distribution(),
            'services_by_region': get_services_by_region(),
            'site_names': get_all_site_names()
        }
        
        return JsonResponse({
            'success': True,
            'data': data,
            'timestamp': request.build_absolute_uri(),
            'source': 'mongodb'
        })
        
    except Exception as e:
        logger.error(f"Erreur refresh data: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def mongodb_test_view(request):
    """Vue de test pour vérifier la connexion MongoDB et afficher des échantillons"""
    try:
        client = snrt_service.get_connection()
        if not client:
            return JsonResponse({
                'status': 'error',
                'message': 'Impossible de se connecter à MongoDB'
            })
        
        db = client[snrt_service.db_name]
        collections_info = {}
        
        for name, collection_name in snrt_service.collections.items():
            try:
                count = db[collection_name].count_documents({})
                # Récupérer un échantillon
                sample = list(db[collection_name].find().limit(1))
                
                collections_info[name] = {
                    'collection': collection_name,
                    'count': count,
                    'status': 'ok',
                    'sample': sample[0] if sample else None
                }
            except Exception as e:
                collections_info[name] = {
                    'collection': collection_name,
                    'error': str(e),
                    'status': 'error'
                }
        
        # Tester les fonctions de données
        test_data = {
            'stats': get_dashboard_stats(),
            'regions_count': len(get_region_distribution()['regions']),
            'services_count': len(get_services_distribution()['services']),
            'categories_count': len(get_category_distribution()['categories'])
        }
        
        client.close()
        
        return JsonResponse({
            'status': 'success',
            'database': snrt_service.db_name,
            'collections': collections_info,
            'test_data': test_data
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })

def collection_data_view(request, collection_name):
    """Vue pour afficher les données d'une collection spécifique avec pagination"""
    try:
        if collection_name not in snrt_service.collections.values():
            return JsonResponse({'error': 'Collection non trouvée'}, status=404)
        
        limit = int(request.GET.get('limit', 10))
        skip = int(request.GET.get('skip', 0))
        
        # Récupérer les données avec pagination
        data = snrt_service.get_collection_data(collection_name, limit=limit)
        total_count = len(data)  # Pour une vraie pagination, il faudrait count_documents()
        
        # Informations sur la structure
        sample_fields = []
        if data:
            sample_fields = list(data[0].keys())
        
        return JsonResponse({
            'success': True,
            'collection': collection_name,
            'total_count': total_count,
            'returned_count': len(data),
            'sample_fields': sample_fields,
            'data': data
        })
        
    except Exception as e:
        logger.error(f"Erreur collection data: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def sites_list_api(request):
    """API pour récupérer la liste de tous les sites"""
    try:
        sites = get_all_site_names()
        
        return JsonResponse({
            'success': True,
            'count': len(sites),
            'sites': sites,
            'source': 'mongodb'
        })
        
    except Exception as e:
        logger.error(f"Erreur sites list: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)