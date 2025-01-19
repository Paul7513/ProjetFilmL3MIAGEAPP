from django.core.management.base import BaseCommand
import pandas as pd
from movies.models import Movie  # Assurez-vous d'importer votre modèle Movie

INPUT_FILE = "/home/manda/FilmProjet/films_avec_affiches_tmdb.csv"  # Fichier CSV avec affiches

class Command(BaseCommand):
    help = "Mise à jour de la base de données avec les affiches des films depuis le fichier CSV."

    def handle(self, *args, **kwargs):
        """Lecture du fichier CSV et mise à jour de la base de données."""
        print(f"Lecture du fichier {INPUT_FILE}...")
        films_avec_affiches = pd.read_csv(INPUT_FILE)

        # Afficher les colonnes pour vérifier
        print(f"Colonnes du fichier CSV : {films_avec_affiches.columns.tolist()}")

        # Assurez-vous que les colonnes 'Title' et 'Poster_URL' existent
        if 'Title' not in films_avec_affiches.columns or 'Poster_URL' not in films_avec_affiches.columns:
            print("Les colonnes 'Title' ou 'Poster_URL' sont manquantes dans le fichier CSV.")
            return

        # Mise à jour des films dans la base de données
        for idx, row in films_avec_affiches.iterrows():
            title = row['Title']
            poster_url = row['Poster_URL']
            print(f"Mise à jour de {title}...")

            try:
                # Trouver le film existant dans la base de données
                movie = Movie.objects.get(title=title)
                # Mettre à jour l'URL de l'affiche
                movie.poster_url = poster_url
                movie.save()  # Sauvegarder les changements dans la base de données
                print(f"Affiche mise à jour pour {title}.")
            except Movie.DoesNotExist:
                print(f"Film '{title}' non trouvé dans la base de données.")
            except Exception as e:
                print(f"Erreur lors de la mise à jour de {title}: {e}")

        print(f"Mise à jour des affiches terminée.")
