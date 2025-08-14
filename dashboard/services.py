from django.conf import settings
import pymongo
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import logging
from collections import Counter, defaultdict

logger = logging.getLogger(__name__)

class SNRTMongoService:
    """Service pour interagir avec la base MongoDB SNRT"""
    
    def __init__(self):
        self.host = settings.MONGODB_SETTINGS['host']
        self.db_name = settings.MONGODB_SETTINGS['database']
        self.collections = settings.SNRT_COLLECTIONS
    
    def get_connection(self):
        """Crée une connexion MongoDB"""
        try:
            client = pymongo.MongoClient(self.host, serverSelectionTimeoutMS=5000)
            client.server_info()
            return client
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Erreur de connexion MongoDB: {e}")
            return None
    
    def get_collection_data(self, collection_name, filters=None, limit=None):
        """Récupère les données d'une collection"""
        client = self.get_connection()
        if not client:
            return []
        
        try:
            db = client[self.db_name]
            collection = db[collection_name]
            
            query = filters if filters else {}
            cursor = collection.find(query)
            
            if limit:
                cursor = cursor.limit(limit)
            
            data = list(cursor)
            
            # Convertir ObjectId en string pour JSON
            for item in data:
                if '_id' in item:
                    item['_id'] = str(item['_id'])
                    
            return data
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données: {e}")
            return []
        finally:
            client.close()

# Instance globale du service
snrt_service = SNRTMongoService()

def get_dashboard_stats():
    """Récupère les statistiques principales pour le dashboard basées sur tes données réelles"""
    try:
        # Récupérer toutes les stations depuis staff site (données principales)
        staff_sites = snrt_service.get_collection_data('staff site')
        
        if not staff_sites:
            return {
                'total_stations': 0,
                'services_tnt': 0,
                'services_fm': 0,
                'control_count': 0
            }
        
        # Compter les services depuis staff site
        services_tnt = sum(1 for site in staff_sites if site.get('TNT') is True)
        services_fm = sum(1 for site in staff_sites if site.get('FM') is True)
        services_am = sum(1 for site in staff_sites if site.get('AM') is True)
        services_fh = sum(1 for site in staff_sites if site.get('FH') is True)
        services_st = sum(1 for site in staff_sites if site.get('ST') is True)
        services_admin = sum(1 for site in staff_sites if site.get('Administration') is True)
        
        # Compter les stations en contrôle
        control_count = sum(1 for site in staff_sites if site.get('control') is True)
        
        return {
            'total_stations': len(staff_sites),
            'services_tnt': services_tnt,
            'services_fm': services_fm,
            'services_am': services_am,
            'services_fh': services_fh,
            'services_st': services_st,
            'services_admin': services_admin,
            'control_count': control_count
        }
        
    except Exception as e:
        logger.error(f"Erreur lors du calcul des stats: {e}")
        return {
            'total_stations': 0,
            'services_tnt': 0,
            'services_fm': 0,
            'services_am': 0,
            'control_count': 0
        }

def get_region_distribution():
    """Récupère la répartition des stations par région SNRT_RS"""
    try:
        staff_sites = snrt_service.get_collection_data('staff site')
        
        if not staff_sites:
            return {'regions': [], 'counts': []}
        
        # Compter par SNRT_RS (région SNRT)
        region_counter = Counter()
        for site in staff_sites:
            snrt_rs = site.get('SNRT_RS')
            if snrt_rs:
                region_counter[snrt_rs] += 1
        
        # Trier par nombre de stations (décroissant)
        sorted_regions = region_counter.most_common()
        
        regions = [region for region, count in sorted_regions]
        counts = [count for region, count in sorted_regions]
        
        return {
            'regions': regions,
            'counts': counts
        }
        
    except Exception as e:
        logger.error(f"Erreur région distribution: {e}")
        return {'regions': [], 'counts': []}

def get_services_distribution():
    """Récupère la répartition des services (TNT, FM, AM, etc.)"""
    try:
        staff_sites = snrt_service.get_collection_data('staff site')
        
        if not staff_sites:
            return {'services': [], 'counts': []}
        
        # Compter chaque type de service
        service_counts = {
            'TNT': sum(1 for site in staff_sites if site.get('TNT') is True),
            'FM': sum(1 for site in staff_sites if site.get('FM') is True),
            'AM': sum(1 for site in staff_sites if site.get('AM') is True),
            'FH': sum(1 for site in staff_sites if site.get('FH') is True),
            'ST': sum(1 for site in staff_sites if site.get('ST') is True),
            'Administration': sum(1 for site in staff_sites if site.get('Administration') is True)
        }
        
        # Filtrer les services qui ont au moins 1 occurrence
        filtered_services = {k: v for k, v in service_counts.items() if v > 0}
        
        return {
            'services': list(filtered_services.keys()),
            'counts': list(filtered_services.values())
        }
        
    except Exception as e:
        logger.error(f"Erreur services distribution: {e}")
        return {'services': [], 'counts': []}

def get_config_users_distribution():
    """Récupère la répartition par ConfigUser"""
    try:
        staff_sites = snrt_service.get_collection_data('staff site')
        
        if not staff_sites:
            return {'users': [], 'counts': []}
        
        # Compter par ConfigUser
        user_counter = Counter()
        for site in staff_sites:
            config_user = site.get('ConfigUser')
            if config_user:
                user_counter[config_user] += 1
        
        # Trier par nombre de stations (décroissant)
        sorted_users = user_counter.most_common()
        
        users = [user for user, count in sorted_users]
        counts = [count for user, count in sorted_users]
        
        return {
            'users': users,
            'counts': counts
        }
        
    except Exception as e:
        logger.error(f"Erreur config users: {e}")
        return {'users': [], 'counts': []}

def get_category_distribution():
    """Récupère la répartition par catégorie"""
    try:
        staff_sites = snrt_service.get_collection_data('staff site')
        
        if not staff_sites:
            return {'categories': [], 'counts': []}
        
        # Compter par Category
        category_counter = Counter()
        for site in staff_sites:
            category = site.get('Category')
            if category:
                category_counter[category] += 1
        
        # Trier par ordre alphabétique
        sorted_categories = sorted(category_counter.items())
        
        categories = [f"Catégorie {cat}" for cat, count in sorted_categories]
        counts = [count for cat, count in sorted_categories]
        
        return {
            'categories': categories,
            'counts': counts
        }
        
    except Exception as e:
        logger.error(f"Erreur category distribution: {e}")
        return {'categories': [], 'counts': []}

def get_services_by_region():
    """Récupère la répartition des services par région pour le graphique en ligne"""
    try:
        staff_sites = snrt_service.get_collection_data('staff site')
        
        if not staff_sites:
            return {'regions': [], 'datasets': []}
        
        # Organiser par région
        regions_data = defaultdict(lambda: {
            'TNT': 0, 'FM': 0, 'AM': 0, 'FH': 0, 'ST': 0, 'Administration': 0
        })
        
        for site in staff_sites:
            snrt_rs = site.get('SNRT_RS')
            if snrt_rs:
                if site.get('TNT') is True:
                    regions_data[snrt_rs]['TNT'] += 1
                if site.get('FM') is True:
                    regions_data[snrt_rs]['FM'] += 1
                if site.get('AM') is True:
                    regions_data[snrt_rs]['AM'] += 1
                if site.get('FH') is True:
                    regions_data[snrt_rs]['FH'] += 1
                if site.get('ST') is True:
                    regions_data[snrt_rs]['ST'] += 1
                if site.get('Administration') is True:
                    regions_data[snrt_rs]['Administration'] += 1
        
        regions = list(regions_data.keys())
        
        # Créer les datasets pour chaque service
        datasets = []
        service_types = ['TNT', 'FM', 'AM', 'FH', 'ST', 'Administration']
        
        for service in service_types:
            data = [regions_data[region][service] for region in regions]
            # Ne garder que les services qui ont au moins une occurrence
            if sum(data) > 0:
                datasets.append({
                    'label': service,
                    'data': data
                })
        
        return {
            'regions': regions,
            'datasets': datasets
        }
        
    except Exception as e:
        logger.error(f"Erreur services by region: {e}")
        return {'regions': [], 'datasets': []}

def get_station_details(station_name):
    """Récupère les détails d'une station spécifique par son nom de site"""
    try:
        # Chercher par Site (nom de la station)
        station_data = snrt_service.get_collection_data(
            'staff site',
            {'Site': station_name}
        )
        
        if not station_data:
            return None
        
        # Retourner le premier résultat
        station = station_data[0]
        
        # Analyser les services
        services = {
            'TNT': station.get('TNT', False),
            'FM': station.get('FM', False),
            'AM': station.get('AM', False),
            'FH': station.get('FH', False),
            'ST': station.get('ST', False),
            'Administration': station.get('Administration', False)
        }
        
        return {
            'name': station.get('Site', ''),
            'province': station.get('Province', ''),
            'region': station.get('Region', ''),
            'snrt_rs': station.get('SNRT_RS', ''),
            'latitude': station.get('Latitude', 0),
            'longitude': station.get('Longitude', 0),
            'altitude': station.get('Altitude', 0),
            'category': station.get('Category', ''),
            'gsm': station.get('Gsm', ''),
            'config_user': station.get('ConfigUser', ''),
            'creation_date': station.get('CreationDate', ''),
            'control': station.get('control', False),
            'services': services,
            'code': station.get('_id', ''),
            'photo': station.get('Photo', '')
        }
        
    except Exception as e:
        logger.error(f"Erreur détails station: {e}")
        return None

def get_all_station_names():
    """Récupère tous les noms de stations disponibles"""
    try:
        staff_sites = snrt_service.get_collection_data('staff site')
        
        if not staff_sites:
            return []
        
        # Extraire tous les noms de sites
        station_names = []
        for site in staff_sites:
            site_name = site.get('Site')
            if site_name:
                station_names.append({
                    'name': site_name,
                    'display_name': site_name.replace('-', ' ').title(),
                    'slug': site_name.lower().replace(' ', '-')
                })
        
        # Trier alphabétiquement
        station_names.sort(key=lambda x: x['name'])
        
        return station_names
        
    except Exception as e:
        logger.error(f"Erreur récupération noms stations: {e}")
        return []