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
    get_stations_by_site,
    get_tnt_subfamilies_distribution,
    get_fm_subfamilies_distribution,
    get_energie_subfamilies_distribution,
    get_all_site_names,
    snrt_service
)

logger = logging.getLogger(__name__)

def dashboard_view(request):
    try:
        stats = get_dashboard_stats()
        region_data = get_region_distribution()
        services_data = get_services_distribution()
        category_data = get_category_distribution()
        services_by_region_data = get_services_by_region()
        stations_by_site_data = get_stations_by_site()
        tnt_subfamilies_data = get_tnt_subfamilies_distribution()
        fm_subfamilies_data = get_fm_subfamilies_distribution()
        energie_subfamilies_data = get_energie_subfamilies_distribution()
        site_names = get_all_site_names()
        
        logger.info(f"TNT Subfamilies Data: {tnt_subfamilies_data}")
        logger.info(f"FM Subfamilies Data: {fm_subfamilies_data}")
        logger.info(f"Energie Subfamilies Data: {energie_subfamilies_data}")
        
        context = {
            'stats': stats,
            'regions_data': region_data,
            'services_data': services_data,
            'category_data': category_data,
            'services_by_region_data': services_by_region_data,
            'stations_by_site_data': stations_by_site_data,
            'tnt_subfamilies_data': tnt_subfamilies_data,
            'fm_subfamilies_data': fm_subfamilies_data,
            'energie_subfamilies_data': energie_subfamilies_data,
            'site_names': site_names,
            'mongodb_connected': True
        }
        
        logger.info(f"Dashboard chargé avec {stats['total_sites']} sites depuis MongoDB")
        logger.info(f"Sous-familles TNT: {len(tnt_subfamilies_data.get('subfamilies', []))}")
        logger.info(f"Sous-familles FM: {len(fm_subfamilies_data.get('subfamilies', []))}")
        logger.info(f"Sous-familles Énergie: {len(energie_subfamilies_data.get('subfamilies', []))}")
        
        return render(request, 'dashboard/tableau.html', context)
        
    except Exception as e:
        logger.error(f"Erreur dans dashboard_view: {e}")
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
            'stations_by_site_data': {'sites': [], 'datasets': []},
            'tnt_subfamilies_data': {'subfamilies': [], 'counts': [], 'colors': [], 'labels': []},
            'fm_subfamilies_data': {'subfamilies': [], 'counts': [], 'colors': [], 'labels': []},
            'energie_subfamilies_data': {'subfamilies': [], 'counts': [], 'colors': [], 'labels': []},
            'site_names': []
        }
        return render(request, 'dashboard/tableau.html', context)

@csrf_exempt
def chart_data_api(request):
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
        elif chart_type == 'stations_by_site':
            data = get_stations_by_site()
        elif chart_type == 'tnt_subfamilies':
            data = get_tnt_subfamilies_distribution()
            logger.info(f"API TNT Subfamilies appelée, données: {data}")
        elif chart_type == 'fm_subfamilies':
            data = get_fm_subfamilies_distribution()
            logger.info(f"API FM Subfamilies appelée, données: {data}")
        elif chart_type == 'energie_subfamilies':
            data = get_energie_subfamilies_distribution()
            logger.info(f"API Energie Subfamilies appelée, données: {data}")
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
    try:
        data = {
            'stats': get_dashboard_stats(),
            'regions': get_region_distribution(),
            'services': get_services_distribution(),
            'categories': get_category_distribution(),
            'services_by_region': get_services_by_region(),
            'stations_by_site': get_stations_by_site(),
            'tnt_subfamilies': get_tnt_subfamilies_distribution(),
            'fm_subfamilies': get_fm_subfamilies_distribution(),
            'energie_subfamilies': get_energie_subfamilies_distribution(),
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
        
        tnt_data = get_tnt_subfamilies_distribution()
        fm_data = get_fm_subfamilies_distribution()
        energie_data = get_energie_subfamilies_distribution()
        
        logger.info(f"Test TNT subfamilies data: {tnt_data}")
        logger.info(f"Test FM subfamilies data: {fm_data}")
        logger.info(f"Test Energie subfamilies data: {energie_data}")
        
        test_data = {
            'stats': get_dashboard_stats(),
            'regions_count': len(get_region_distribution()['regions']),
            'services_count': len(get_services_distribution()['services']),
            'categories_count': len(get_category_distribution()['categories']),
            'stations_by_site_count': len(get_stations_by_site()['sites']),
            'tnt_subfamilies_count': len(tnt_data.get('subfamilies', [])),
            'tnt_subfamilies_total_stations': tnt_data.get('total_stations', 0),
            'fm_subfamilies_count': len(fm_data.get('subfamilies', [])),
            'fm_subfamilies_total_stations': fm_data.get('total_stations', 0),
            'energie_subfamilies_count': len(energie_data.get('subfamilies', [])),
            'energie_subfamilies_total_stations': energie_data.get('total_stations', 0),
            'tnt_subfamilies_sample': tnt_data,
            'fm_subfamilies_sample': fm_data,
            'energie_subfamilies_sample': energie_data
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
    try:
        if collection_name not in snrt_service.collections.values():
            return JsonResponse({'error': 'Collection non trouvée'}, status=404)
        
        limit = int(request.GET.get('limit', 10))
        skip = int(request.GET.get('skip', 0))
        
        data = snrt_service.get_collection_data(collection_name, limit=limit)
        total_count = len(data)
        
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