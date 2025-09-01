from django.conf import settings
import pymongo
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import logging
from collections import Counter, defaultdict

logger = logging.getLogger(__name__)

class SNRTMongoService:
    
    def __init__(self):
        self.host = settings.MONGODB_SETTINGS['host']
        self.db_name = settings.MONGODB_SETTINGS['database']
        self.collections = settings.SNRT_COLLECTIONS
    
    def get_connection(self):
        try:
            client = pymongo.MongoClient(self.host, serverSelectionTimeoutMS=5000)
            client.server_info()
            return client
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Erreur de connexion MongoDB: {e}")
            return None
    
    def get_collection_data(self, collection_name, filters=None, limit=None):
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
            
            for item in data:
                if '_id' in item:
                    item['_id'] = str(item['_id'])
                    
            return data
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données: {e}")
            return []
        finally:
            client.close()

snrt_service = SNRTMongoService()

def get_dashboard_stats():
    try:
        staff_sites = snrt_service.get_collection_data('staff site')
        
        if not staff_sites:
            return {
                'total_sites': 0,
                'services_tnt': 0,
                'services_fm': 0,
                'control_count': 0
            }
        
        services_tnt = sum(1 for site in staff_sites if site.get('TNT') is True)
        services_fm = sum(1 for site in staff_sites if site.get('FM') is True)
        services_am = sum(1 for site in staff_sites if site.get('AM') is True)
        services_fh = sum(1 for site in staff_sites if site.get('FH') is True)
        services_st = sum(1 for site in staff_sites if site.get('ST') is True)
        services_admin = sum(1 for site in staff_sites if site.get('Administration') is True)
        
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
    try:
        staff_sites = snrt_service.get_collection_data('staff site')
        
        if not staff_sites:
            return {'regions': [], 'counts': [], 'colors': []}
        
        region_counter = Counter()
        for site in staff_sites:
            snrt_rs = site.get('SNRT_RS')
            if snrt_rs:
                region_counter[snrt_rs] += 1
        
        sorted_regions = region_counter.most_common()
        
        regions = [region for region, count in sorted_regions]
        counts = [count for region, count in sorted_regions]
        
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
    try:
        staff_sites = snrt_service.get_collection_data('staff site')
        
        if not staff_sites:
            return {'services': [], 'counts': [], 'colors': []}
        
        service_counts = {
            'TNT': sum(1 for site in staff_sites if site.get('TNT') is True),
            'FM': sum(1 for site in staff_sites if site.get('FM') is True),
            'AM': sum(1 for site in staff_sites if site.get('AM') is True),
            'FH': sum(1 for site in staff_sites if site.get('FH') is True),
            'ST': sum(1 for site in staff_sites if site.get('ST') is True),
            'Administration': sum(1 for site in staff_sites if site.get('Administration') is True)
        }
        
        service_colors = {
            'TNT': '#ff4757',
            'FM': '#2ed573',
            'AM': '#ffa502',
            'Administration': '#3742fa',
            'FH': '#8c7ae6',
            'ST': '#ff6b6b'
        }
        
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
    try:
        staff_sites = snrt_service.get_collection_data('staff site')
        
        if not staff_sites:
            return {'categories': [], 'counts': [], 'colors': []}
        
        category_counter = Counter()
        for site in staff_sites:
            category = site.get('Category')
            if category:
                category_counter[category] += 1
        
        sorted_categories = sorted(category_counter.items())
        
        categories = [f"Catégorie {cat}" for cat, count in sorted_categories]
        counts = [count for cat, count in sorted_categories]
        
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
    try:
        staff_sites = snrt_service.get_collection_data('staff site')
        
        if not staff_sites:
            return {'regions': [], 'datasets': []}
        
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
        
        service_colors = {
            'TNT': '#ff4757',
            'FM': '#2ed573',
            'AM': '#ffa502',
            'Administration': '#3742fa',
            'FH': '#8c7ae6',
            'ST': '#ff6b6b'
        }
        
        datasets = []
        service_types = ['TNT', 'FM', 'AM', 'FH', 'ST', 'Administration']
        
        for service in service_types:
            data = [regions_data[region][service] for region in regions]
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
    try:
        material_station_sites = snrt_service.get_collection_data('material station site')
        staff_sites = snrt_service.get_collection_data('staff site')
        
        if not material_station_sites or not staff_sites:
            return {'sites': [], 'datasets': []}
        
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
        
        site_station_count = defaultdict(int)
        for station_site in material_station_sites:
            site_id = str(station_site.get('site_id', ''))
            if site_id in site_mapping:
                site_station_count[site_id] += 1
        
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
                
                sites_data[site_name] = {}
                for service, is_active in services.items():
                    if is_active:
                        sites_data[site_name][service] = station_count
                    else:
                        sites_data[site_name][service] = 0
        
        sites = list(sites_data.keys())
        datasets = []
        
        service_types = ['TNT', 'FM', 'AM', 'FH', 'ST', 'Administration']
        
        for service in service_types:
            data = []
            for site in sites:
                data.append(sites_data[site].get(service, 0))
            
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

def get_subfamily_distribution_by_family(family_name):
    try:
        achat_families = snrt_service.get_collection_data('achat family')
        achat_subfamilies = snrt_service.get_collection_data('achat subfamily')
        material_station_families = snrt_service.get_collection_data('material station family')
        material_station_subfamilies = snrt_service.get_collection_data('material station subfamily')
        
        if not achat_families or not achat_subfamilies:
            logger.warning(f"Collections achat family ou achat subfamily vides pour {family_name}")
            return get_fallback_subfamily_data(family_name)
        
        family_id = None
        for family in achat_families:
            if family.get('name', '').upper() == family_name.upper():
                family_id = str(family.get('_id'))
                break
        
        if not family_id:
            logger.warning(f"Famille {family_name} non trouvée dans achat family")
            return get_fallback_subfamily_data(family_name)
        
        logger.info(f"Famille {family_name} trouvée avec ID: {family_id}")
        
        subfamilies = {}
        for subfamily in achat_subfamilies:
            if str(subfamily.get('family_id', '')) == family_id:
                subfamily_id = str(subfamily.get('_id'))
                subfamily_name = subfamily.get('name', f'Sous-famille {subfamily_id}')
                subfamilies[subfamily_id] = subfamily_name
        
        logger.info(f"Sous-familles {family_name} trouvées: {subfamilies}")
        
        if not subfamilies:
            logger.warning(f"Aucune sous-famille trouvée pour {family_name}")
            return get_fallback_subfamily_data(family_name)
        
        subfamily_station_count = defaultdict(int)
        
        if material_station_subfamilies:
            for station_subfamily in material_station_subfamilies:
                subfamily_id = str(station_subfamily.get('subfamily_id', ''))
                if subfamily_id in subfamilies:
                    subfamily_name = subfamilies[subfamily_id]
                    subfamily_station_count[subfamily_name] += 1
        
        if not subfamily_station_count and material_station_families:
            for station_family in material_station_families:
                if str(station_family.get('family_id', '')) == family_id:
                    subfamily_station_count[f'{family_name} Général'] += 1
        
        logger.info(f"Comptage final par sous-famille {family_name}: {dict(subfamily_station_count)}")
        
        if subfamily_station_count:
            return format_subfamily_data(subfamily_station_count, family_name)
        else:
            logger.warning(f"Aucune station trouvée pour les sous-familles {family_name}")
            return get_fallback_subfamily_data(family_name)
        
    except Exception as e:
        logger.error(f"Erreur {family_name} subfamilies: {e}")
        return get_fallback_subfamily_data(family_name)

def get_tnt_subfamilies_distribution():
    return get_subfamily_distribution_by_family('TNT')

def get_fm_subfamilies_distribution():
    return get_subfamily_distribution_by_family('FM')

def get_energie_subfamilies_distribution():
    return get_subfamily_distribution_by_family('Energie')

def format_subfamily_data(subfamily_counts, family_name):
    try:
        sorted_subfamilies = sorted(subfamily_counts.items(), key=lambda x: x[1], reverse=True)
        
        subfamilies = [subfamily for subfamily, count in sorted_subfamilies]
        counts = [count for subfamily, count in sorted_subfamilies]
        
        subfamily_colors = get_subfamily_colors(family_name)
        
        colors = []
        for i, subfamily in enumerate(subfamilies):
            if subfamily in subfamily_colors:
                colors.append(subfamily_colors[subfamily])
            else:
                base_hue = get_base_hue(family_name)
                hue = base_hue + (i * 30) % 120
                colors.append(f'hsl({hue}, 70%, 55%)')
        
        total_stations = sum(counts)
        labels = []
        for subfamily, count in zip(subfamilies, counts):
            percentage = (count / total_stations * 100) if total_stations > 0 else 0
            labels.append(f"{subfamily}: {count} stations ({percentage:.1f}%)")
        
        return {
            'subfamilies': subfamilies,
            'counts': counts,
            'colors': colors,
            'labels': labels,
            'total_stations': total_stations,
            'subfamily_count': len(subfamilies)
        }
        
    except Exception as e:
        logger.error(f"Erreur formatage données sous-familles {family_name}: {e}")
        return get_fallback_subfamily_data(family_name)

def get_subfamily_colors(family_name):
    color_schemes = {
        'TNT': {
            'TNT Émetteur': '#ff4757',
            'TNT Antenne': '#ff6b6b',
            'TNT Combineur': '#ff5722',
            'TNT Filtre': '#e84393',
            'TNT Amplificateur': '#fd79a8',
            'TNT Câblage': '#fdcb6e',
            'TNT Général': '#ff7675',
            'TNT Maintenance': '#a29bfe',
            'TNT Transmission': '#6c5ce7',
            'TNT Infrastructure': '#74b9ff'
        },
        'FM': {
            'FM Émetteur': '#2ed573',
            'FM Antenne': '#00b894',
            'FM Amplificateur': '#55a3ff',
            'FM Filtre': '#00cec9',
            'FM Combineur': '#81ecec',
            'FM Câblage': '#a7f0ba',
            'FM Général': '#00e640',
            'FM Maintenance': '#26de81',
            'FM Transmission': '#20bf6b',
            'FM Infrastructure': '#0fb9b1'
        },
        'Energie': {
            'Energie Onduleur': '#ffa502',
            'Energie Batterie': '#ff7675',
            'Energie Groupe Electrogène': '#fd79a8',
            'Energie Panneau Solaire': '#fdcb6e',
            'Energie Convertisseur': '#e84393',
            'Energie Régulateur': '#a29bfe',
            'Energie Câblage': '#6c5ce7',
            'Energie Général': '#ff9ff3',
            'Energie Maintenance': '#ffeaa7',
            'Energie Infrastructure': '#fab1a0'
        }
    }
    
    return color_schemes.get(family_name, {})

def get_base_hue(family_name):
    base_hues = {
        'TNT': 0,
        'FM': 120,
        'Energie': 40
    }
    return base_hues.get(family_name, 0)

def get_fallback_subfamily_data(family_name):
    fallback_data = {
        'TNT': {
            'TNT Émetteur': 45,
            'TNT Antenne': 38,
            'TNT Combineur': 25,
            'TNT Filtre': 20,
            'TNT Amplificateur': 15,
            'TNT Câblage': 12,
            'TNT Général': 8
        },
        'FM': {
            'FM Émetteur': 35,
            'FM Antenne': 28,
            'FM Amplificateur': 22,
            'FM Filtre': 18,
            'FM Combineur': 15,
            'FM Câblage': 10,
            'FM Général': 8
        },
        'Energie': {
            'Energie Onduleur': 42,
            'Energie Batterie': 38,
            'Energie Groupe Electrogène': 25,
            'Energie Panneau Solaire': 20,
            'Energie Convertisseur': 15,
            'Energie Régulateur': 12,
            'Energie Général': 8
        }
    }
    
    selected_data = fallback_data.get(family_name, {})
    logger.info(f"Utilisation des données de fallback pour {family_name} subfamilies")
    return format_subfamily_data(selected_data, family_name)

def get_site_details(site_name):
    try:
        site_data = snrt_service.get_collection_data(
            'staff site',
            {'Site': site_name}
        )
        
        if not site_data:
            return None
        
        site = site_data[0]
        
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
    try:
        staff_sites = snrt_service.get_collection_data('staff site')
        
        if not staff_sites:
            return []
        
        site_names = []
        for site in staff_sites:
            site_name = site.get('Site')
            if site_name:
                site_names.append({
                    'name': site_name,
                    'display_name': site_name.replace('-', ' ').title(),
                    'slug': site_name.lower().replace(' ', '-')
                })
        
        site_names.sort(key=lambda x: x['name'])
        
        return site_names
        
    except Exception as e:
        logger.error(f"Erreur récupération noms sites: {e}")
        return []