import csv  # Ajoutez cette ligne pour importer le module csv
from django.core.management.base import BaseCommand
from movies.models import Movie  # Assurez-vous que vous avez le bon modèle de film


class Command(BaseCommand):
    help = 'Récupère les titres des films sans affiche et les enregistre dans un fichier CSV'

    def handle(self, *args, **kwargs):
        # Récupérer tous les films sans affiche à l'aide de Django ORM
        films_sans_affiche = Movie.objects.filter(poster_url__isnull=True) | Movie.objects.filter(poster_url='')

        # Enregistrer les titres dans un fichier CSV
        with open("films_sans_affiche.csv", "w", newline='', encoding="utf-8") as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(["Title"])  # En-tête
            for film in films_sans_affiche:
                csv_writer.writerow([film.title])

        self.stdout.write(self.style.SUCCESS('Les titres des films sans affiche ont été enregistrés dans "films_sans_affiche.csv".'))
