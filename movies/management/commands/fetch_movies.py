import csv
import re
from django.core.management.base import BaseCommand
from movies.models import Movie

class Command(BaseCommand):
    help = "Charge ou met à jour les films depuis un fichier CSV."

    def handle(self, *args, **kwargs):
        file_path = '/home/manda/FilmProjet/movies_with_posters.csv'
        self.stdout.write(f"Chargement des films depuis {file_path}...")
        
        with open(file_path, encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    # Extraire les données du fichier
                    title = row['Title'].strip()
                    clean_title = row['Clean_Title'].strip()
                    genres = row['Genres'].strip()
                    year = self.clean_year(row['Year'])
                    poster_url = row['Poster_URL'].strip()
                    synopsis = row['Synopsis'].strip()
                    trailer_url = row['Trailer_URL'].strip()

                    # Construire la date de sortie
                    release_date = f"{year}-01-01" if year else None

                    # Mettre à jour ou créer un film
                    movie, created = Movie.objects.update_or_create(
                        title=title,
                        defaults={
                            'clean_title': clean_title,
                            'genres': genres,
                            'release_date': release_date,
                            'poster_url': poster_url,
                            'synopsis': synopsis,
                            'trailer_url': trailer_url,
                        },
                    )
                    
                    action = "créé" if created else "mis à jour"
                    self.stdout.write(self.style.SUCCESS(f"Film '{title}' {action}."))
                
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Erreur lors du traitement du film '{row['Title']}': {e}"))

    def clean_year(self, year):
        """Nettoie et valide l'année pour garantir un entier ou None."""
        try:
            return int(float(year))  # Convertit en entier puis en chaîne
        except (ValueError, TypeError):
            return None
