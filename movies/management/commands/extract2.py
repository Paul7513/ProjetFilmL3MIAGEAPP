import pandas as pd
from django.core.management.base import BaseCommand
from movies.models import Movie  # Assurez-vous que votre modèle Movie est importé correctement

class Command(BaseCommand):
    help = 'Exporte les films dont poster_url est "nan" dans un fichier CSV'

    def handle(self, *args, **kwargs):
        # Récupérer les films où poster_url est égal à "nan"
        films_nan_affiche = Movie.objects.filter(poster_url="nan")

        # Créer une liste des films à exporter
        films_list = []
        for film in films_nan_affiche:
            films_list.append({
                'title': film.title,
                'genre': film.genre,
                'synopsis': film.synopsis,
                'release_date': film.release_date,
                'year': film.year,
                'poster_url': film.poster_url,
                'trailer_url': film.trailer_url,
                'price': film.price,
            })

        # Convertir en DataFrame
        df = pd.DataFrame(films_list)

        # Exporter les films dans un fichier CSV
        df.to_csv('films_nan_affiche.csv', index=False)

        # Afficher un message de succès dans la console
        self.stdout.write(self.style.SUCCESS(f'{len(films_nan_affiche)} films exportés vers films_nan_affiche.csv'))
