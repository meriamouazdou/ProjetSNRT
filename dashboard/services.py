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
        # Récupérer tous les sites depuis staff site
        staff_sites = snrt_service.get_collection_data('staff site')
        
        if not staff_sites:
            return {
                'total_sites': 0,
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
        
        # Compter les sites en contrôle
        control_count = sum(1 for site in staff_sites if site.get('control') is True)
        
        return {
            'total_sites': len(staff_sites),
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
            'total_sites': 0,
            'services_tnt': 0,
            'services_fm': 0,
            'services_am': 0,
            'control_count': 0
        }

def get_region_distribution():
    """Récupère la répartition des sites par région SNRT_RS avec couleurs spécifiques"""
    try:
        staff_sites = snrt_service.get_collection_data('staff site')
        
        if not staff_sites:
            return {'regions': [], 'counts': [], 'colors': []}
        
        # Compter par SNRT_RS (région SNRT)
        region_counter = Counter()
        for site in staff_sites:
            snrt_rs = site.get('SNRT_RS')
            if snrt_rs:
                region_counter[snrt_rs] += 1
        
        # Trier par nombre de sites (décroissant)
        sorted_regions = region_counter.most_common()
        
        regions = [region for region, count in sorted_regions]
        counts = [count for region, count in sorted_regions]
        
        # Couleurs spécifiques pour chaque région
        region_colors = {
            'Agadir': '#ff6b6b',
            'Casablanca': '#4ecdc4',
            'Rabat': '#45b7d1',
            'Fes': '#96ceb4',
            'Marrakech': '#ffeaa7',
            'Oujda': '#a29bfe',
            'Tanger': '#fd79a8',
            'Laayoune': '#fdcb6e',
            'Meknes': '#6c5ce7',
            'Taza': '#fd79a8'
        }
        
        # Assigner les couleurs ou couleur par défaut
        colors = [region_colors.get(region, '#95a5a6') for region in regions]
        
        return {
            'regions': regions,
            'counts': counts,
            'colors': colors
        }
        
    except Exception as e:
        logger.error(f"Erreur région distribution: {e}")
        return {'regions': [], 'counts': [], 'colors': []}

def get_services_distribution():
    """Récupère la répartition des services (TNT, FM, AM, etc.)"""
    try:
        staff_sites = snrt_service.get_collection_data('staff site')
        
        if not staff_sites:
            return {'services': [], 'counts': [], 'colors': []}
        
        # Compter chaque type de service
        service_counts = {
            'TNT': sum(1 for site in staff_sites if site.get('TNT') is True),
            'FM': sum(1 for site in staff_sites if site.get('FM') is True),
            'AM': sum(1 for site in staff_sites if site.get('AM') is True),
            'FH': sum(1 for site in staff_sites if site.get('FH') is True),
            'ST': sum(1 for site in staff_sites if site.get('ST') is True),
            'Administration': sum(1 for site in staff_sites if site.get('Administration') is True)
        }
        
        # Couleurs spécifiques pour les services
        service_colors = {
            'TNT': '#ff4757',
            'FM': '#2ed573',
            'AM': '#ffa502',
            'Administration': '#3742fa',
            'FH': '#8c7ae6',
            'ST': '#ff6b6b'
        }
        
        # Filtrer les services qui ont au moins 1 occurrence
        filtered_services = {k: v for k, v in service_counts.items() if v > 0}
        
        services = list(filtered_services.keys())
        counts = list(filtered_services.values())
        colors = [service_colors.get(service, '#95a5a6') for service in services]
        
        return {
            'services': services,
            'counts': counts,
            'colors': colors
        }
        
    except Exception as e:
        logger.error(f"Erreur services distribution: {e}")
        return {'services': [], 'counts': [], 'colors': []}

def get_category_distribution():
    """Récupère la répartition par catégorie en style bar chart"""
    try:
        staff_sites = snrt_service.get_collection_data('staff site')
        
        if not staff_sites:
            return {'categories': [], 'counts': [], 'colors': []}
        
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
        
        # Couleurs pour les catégories
        category_colors = {
            'Catégorie G': '#e17055',
            'Catégorie P': '#74b9ff',
            'Catégorie S': '#00b894',
            'Catégorie M': '#a29bfe',
            'Catégorie L': '#fd79a8'
        }
        
        colors = [category_colors.get(cat, '#95a5a6') for cat in categories]
        
        return {
            'categories': categories,
            'counts': counts,
            'colors': colors
        }
        
    except Exception as e:
        logger.error(f"Erreur category distribution: {e}")
        return {'categories': [], 'counts': [], 'colors': []}

def get_services_by_region():
    """Récupère la répartition des services par région en style bar chart"""
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
        
        # Couleurs pour les services
        service_colors = {
            'TNT': '#ff4757',
            'FM': '#2ed573',
            'AM': '#ffa502',
            'Administration': '#3742fa',
            'FH': '#8c7ae6',
            'ST': '#ff6b6b'
        }
        
        # Créer les datasets pour chaque service en style bar
        datasets = []
        service_types = ['TNT', 'FM', 'AM', 'FH', 'ST', 'Administration']
        
        for service in service_types:
            data = [regions_data[region][service] for region in regions]
            # Ne garder que les services qui ont au moins une occurrence
            if sum(data) > 0:
                datasets.append({
                    'label': service,
                    'data': data,
                    'backgroundColor': service_colors.get(service, '#95a5a6'),
                    'borderColor': service_colors.get(service, '#95a5a6'),
                    'borderWidth': 1
                })
        
        return {
            'regions': regions,
            'datasets': datasets
        }
        
    except Exception as e:
        logger.error(f"Erreur services by region: {e}")
        return {'regions': [], 'datasets': []}

def get_stations_by_site():
    """NOUVEAU: Récupère les stations par site avec leurs services (comme demandé)"""
    try:
        # Récupérer les données des nouvelles collections
        material_station_sites = snrt_service.get_collection_data('material station site')
        staff_sites = snrt_service.get_collection_data('staff site')
        
        if not material_station_sites or not staff_sites:
            return {'sites': [], 'datasets': []}
        
        # Créer un mapping site_id -> site_name depuis staff site
        site_mapping = {}
        for site in staff_sites:
            site_id = site.get('_id')
            site_name = site.get('Site', f'Site {site_id}')
            if site_id:
                site_mapping[str(site_id)] = {
                    'name': site_name,
                    'services': {
                        'TNT': site.get('TNT', False),
                        'FM': site.get('FM', False),
                        'AM': site.get('AM', False),
                        'FH': site.get('FH', False),
                        'ST': site.get('ST', False),
                        'Administration': site.get('Administration', False)
                    }
                }
        
        # Compter les stations par site depuis material station site
        site_station_count = defaultdict(int)
        for station_site in material_station_sites:
            site_id = str(station_site.get('site_id', ''))
            if site_id in site_mapping:
                site_station_count[site_id] += 1
        
        # Organiser les données par site avec services
        sites_data = {}
        service_colors = {
            'TNT': '#ff4757',
            'FM': '#2ed573',
            'AM': '#ffa502',
            'Administration': '#3742fa',
            'FH': '#8c7ae6',
            'ST': '#ff6b6b'
        }
        
        for site_id, station_count in site_station_count.items():
            if site_id in site_mapping:
                site_info = site_mapping[site_id]
                site_name = site_info['name']
                services = site_info['services']
                
                # Pour chaque service actif, ajouter le nombre de stations
                sites_data[site_name] = {}
                for service, is_active in services.items():
                    if is_active:
                        sites_data[site_name][service] = station_count
                    else:
                        sites_data[site_name][service] = 0
        
        # Préparer les données pour le graphique
        sites = list(sites_data.keys())
        datasets = []
        
        # Créer un dataset pour chaque service
        service_types = ['TNT', 'FM', 'AM', 'FH', 'ST', 'Administration']
        
        for service in service_types:
            data = []
            for site in sites:
                data.append(sites_data[site].get(service, 0))
            
            # Ne garder que les services qui ont au moins une occurrence
            if sum(data) > 0:
                datasets.append({
                    'label': service,
                    'data': data,
                    'backgroundColor': service_colors.get(service, '#95a5a6'),
                    'borderColor': service_colors.get(service, '#95a5a6'),
                    'borderWidth': 1
                })
        
        return {
            'sites': sites,
            'datasets': datasets
        }
        
    except Exception as e:
        logger.error(f"Erreur stations by site: {e}")
        return {'sites': [], 'datasets': []}

def get_site_details(site_name):
    """Récupère les détails d'un site spécifique par son nom"""
    try:
        # Chercher par Site (nom du site)
        site_data = snrt_service.get_collection_data(
            'staff site',
            {'Site': site_name}
        )
        
        if not site_data:
            return None
        
        # Retourner le premier résultat
        site = site_data[0]
        
        # Analyser les services
        services = {
            'TNT': site.get('TNT', False),
            'FM': site.get('FM', False),
            'AM': site.get('AM', False),
            'FH': site.get('FH', False),
            'ST': site.get('ST', False),
            'Administration': site.get('Administration', False)
        }
        
        return {
            'name': site.get('Site', ''),
            'province': site.get('Province', ''),
            'region': site.get('Region', ''),
            'snrt_rs': site.get('SNRT_RS', ''),
            'latitude': site.get('Latitude', 0),
            'longitude': site.get('Longitude', 0),
            'altitude': site.get('Altitude', 0),
            'category': site.get('Category', ''),
            'gsm': site.get('Gsm', ''),
            'config_user': site.get('ConfigUser', ''),
            'creation_date': site.get('CreationDate', ''),
            'control': site.get('control', False),
            'services': services,
            'code': site.get('_id', ''),
            'photo': site.get('Photo', '')
        }
        
    except Exception as e:
        logger.error(f"Erreur détails site: {e}")
        return None

def get_all_site_names():
    """Récupère tous les noms de sites disponibles"""
    try:
        staff_sites = snrt_service.get_collection_data('staff site')
        
        if not staff_sites:
            return []
        
        # Extraire tous les noms de sites
        site_names = []
        for site in staff_sites:
            site_name = site.get('Site')
            if site_name:
                site_names.append({
                    'name': site_name,
                    'display_name': site_name.replace('-', ' ').title(),
                    'slug': site_name.lower().replace(' ', '-')
                })
        
        # Trier alphabétiquement
        site_names.sort(key=lambda x: x['name'])
        
        return site_names
        
    except Exception as e:
        logger.error(f"Erreur récupération noms sites: {e}")
        return []