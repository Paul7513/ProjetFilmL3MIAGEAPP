import pandas as pd
import re
from django.core.management.base import BaseCommand
from movies.models import Movie

class Command(BaseCommand):
    help = "Charge les films depuis un fichier CSV dans la base de données"

    def handle(self, *args, **kwargs):
        # Chemin du fichier CSV nettoyé
        file_path = '/home/manda/FilmProjet/movies_cleaned.csv'
        try:
            self.stdout.write(f"Chargement des films depuis {file_path}...")
            movies = pd.read_csv(file_path)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Fichier non trouvé : {file_path}"))
            return

        # Fonction pour extraire le titre et l'année
    def extract_title_and_year(title):
        match = re.match(r"(.*)\s\((\d{4})\)$", title)
        if match:
            title_cleaned = match.group(1)
            try:
                year = int(match.group(2))  # Convertir l'année en entier
                return title_cleaned, year
            except ValueError:
                pass  # Si l'année n'est pas convertible en entier, la laisser comme None
        return title, None


        # Appliquer la fonction pour nettoyer les titres et extraire les années
        movies[['Clean_Title', 'Year']] = movies['Title'].apply(lambda x: pd.Series(extract_title_and_year(x)))

        # Charger les films dans la base de données
        for _, row in movies.iterrows():
            title = row['Clean_Title']
            genre = row['Genres']
            description = "Description non disponible"
            year = row['Year']

            # Formatage de la date de sortie
            release_date = None
            if year:  # Si une année existe
                try:
                    # Assurez-vous que l'année est un entier
                    release_date = f"{year}-01-01"  # Pas besoin de conversion float ici
                except (ValueError, TypeError):
                    self.stdout.write(self.style.WARNING(f"Année invalide pour le film '{title}': {year}"))
                    release_date = None

            # Mise à jour ou création du film
            movie, created = Movie.objects.update_or_create(
                title=title,
                defaults={
                    'genre': genre,
                    'description': description,
                    'release_date': release_date,
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Film ajouté : {title} ({year})"))
            else:
                self.stdout.write(self.style.WARNING(f"Film mis à jour : {title} ({year})"))

        self.stdout.write(self.style.SUCCESS("Chargement des films terminé."))


