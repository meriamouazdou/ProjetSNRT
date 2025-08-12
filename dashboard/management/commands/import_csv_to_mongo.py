from django.core.management.base import BaseCommand
import csv
import sys
import os

# Ajouter le répertoire parent au chemin Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from database import MongoDBConnection

class Command(BaseCommand):
    help = 'Importe un fichier CSV vers MongoDB'
    
    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Chemin vers le fichier CSV')
        parser.add_argument('collection', type=str, help='Nom de la collection MongoDB')
    
    def handle(self, *args, **options):
        # Utiliser votre connexion MongoDB
        mongo_db = MongoDBConnection()
        collection = mongo_db.get_collection(options['collection'])
        
        # Lire et importer le CSV
        try:
            with open(options['csv_file'], 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                documents = []
                
                for row in reader:
                    # Nettoyer les données (enlever les espaces)
                    clean_row = {k.strip(): v.strip() if isinstance(v, str) else v for k, v in row.items()}
                    documents.append(clean_row)
                
                if documents:
                    # Supprimer les anciens documents de cette collection (optionnel)
                    collection.delete_many({})
                    
                    # Insérer les nouveaux documents
                    collection.insert_many(documents)
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Importé {len(documents)} enregistrements dans la collection "{options["collection"]}"')
                    )
                else:
                    self.stdout.write(self.style.WARNING('⚠️ Aucune donnée à importer'))
                    
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'❌ Fichier non trouvé: {options["csv_file"]}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erreur: {str(e)}'))