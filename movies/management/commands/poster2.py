from django.core.management.base import BaseCommand
import requests
import pandas as pd
import re

# Configuration de l'API TMDb
API_KEY = "dc952207f58060efb4e51e18cb1002c4"  # Remplacez par votre propre clé API
TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"

INPUT_FILE = "/home/manda/FilmProjet/films_sans_affiche.csv"  # Fichier CSV des films sans affiche
OUTPUT_FILE = "/home/manda/FilmProjet/films_avec_affiches_tmdb.csv"  # Fichier CSV avec affiches récupérées

def clean_title(title):
    """Nettoie le titre en supprimant les informations entre parenthèses et les guillemets."""
    # Enlever les informations entre parenthèses
    title = re.sub(r'\(.*\)', '', title)
    # Nettoyer les guillemets
    title = title.replace('"', '').replace("'", '').strip()
    return title

def fetch_poster_url(title):
    """Récupère l'URL de l'affiche pour un film donné en utilisant l'API TMDb."""
    cleaned_title = clean_title(title)  # Nettoyer le titre avant de l'utiliser
    params = {
        "api_key": API_KEY,
        "query": cleaned_title,  # Titre du film nettoyé
    }
    try:
        response = requests.get(TMDB_SEARCH_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            if data['results']:
                first_result = data['results'][0]
                poster_path = first_result.get('poster_path')
                if poster_path:
                    return f"{POSTER_BASE_URL}{poster_path}"
        else:
            print(f"Erreur API pour {cleaned_title}: {response.status_code}")
        return None
    except Exception as e:
        print(f"Erreur pour {cleaned_title}: {e}")
        return None

class Command(BaseCommand):
    help = "Récupère les affiches pour les films sans affiche dans un fichier CSV."

    def handle(self, *args, **kwargs):
        """Lecture du fichier, récupération des affiches et sauvegarde."""
        print(f"Lecture du fichier {INPUT_FILE}...")
        films_sans_affiche = pd.read_csv(INPUT_FILE)

        # Afficher les colonnes pour vérifier
        print(f"Colonnes du fichier CSV : {films_sans_affiche.columns.tolist()}")

        # Assurez-vous que la colonne 'Title' existe
        if 'Title' not in films_sans_affiche.columns:
            print("La colonne 'Title' est manquante dans le fichier CSV.")
            return

        # Ajouter une nouvelle colonne pour l'URL de l'affiche
        films_sans_affiche['Poster_URL'] = None

        # Récupération des affiches
        for idx, row in films_sans_affiche.iterrows():
            title = row['Title']
            cleaned_title = clean_title(title)
            print(f"Récupération de l'affiche pour {cleaned_title}...")
            poster_url = fetch_poster_url(cleaned_title)

            if poster_url:
                films_sans_affiche.at[idx, 'Poster_URL'] = poster_url
                print(f"Affiche trouvée : {poster_url}")
            else:
                print(f"Aucune affiche trouvée pour {cleaned_title}.")

        # Sauvegarder les résultats dans un nouveau fichier CSV
        print(f"Enregistrement du fichier avec les affiches dans {OUTPUT_FILE}...")
        films_sans_affiche.to_csv(OUTPUT_FILE, index=False)

        self.stdout.write(self.style.SUCCESS(f"Extraction des affiches terminée. Fichier sauvegardé sous '{OUTPUT_FILE}'."))