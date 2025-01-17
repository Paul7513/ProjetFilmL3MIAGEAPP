import os
import pandas as pd
import requests
from django.core.management.base import BaseCommand
from bs4 import BeautifulSoup


# Variables globales pour les chemins des fichiers
INPUT_FILE = "/home/manda/FilmProjet/movies_cleaned.csv"
OUTPUT_FILE = "/home/manda/FilmProjet/movies_with_posters.csv"


# Configuration de l'API
API_KEY = "dc952207f58060efb4e51e18cb1002c4"  # Remplacez par votre propre clé API
TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"


def fetch_poster_url(title, year):
    """Récupère l'URL de l'affiche pour un film donné."""
    params = {
        "api_key": API_KEY,
        "query": title,
        "year": year,
    }
    try:
        response = requests.get(TMDB_SEARCH_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            if data['results']:
                first_result = data['results'][0]
                poster_path = first_result.get('poster_path')
                movie_id = first_result.get('id')  # Récupérer l'ID du film
                if poster_path:
                    return f"{POSTER_BASE_URL}{poster_path}", movie_id
        else:
            print(f"Erreur API pour {title} ({year}): {response.status_code}")
        return None, None
    except Exception as e:
        print(f"Erreur pour {title} ({year}): {e}")
        return None, None


def fetch_youtube_trailer_url(movie_id):
    """Récupère l'URL de la bande-annonce YouTube à partir de la page HTML du film."""
    # URL de la page du film sur TMDB
    movie_url = f"https://www.themoviedb.org/movie/{movie_id}"


    try:
        response = requests.get(movie_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
           
            # Recherche de l'élément contenant la bande-annonce
            trailer_link = soup.find('a', {'class': 'no_click play_trailer'})
           
            if trailer_link and 'data-id' in trailer_link.attrs:
                video_id = trailer_link['data-id']
                trailer_url = f"https://www.youtube.com/watch?v={video_id}"
                print(f"Bande-annonce trouvée : {trailer_url}")
                return trailer_url
            else:
                print("Aucune bande-annonce trouvée sur TMDB pour ce film.")
                return None
        else:
            print(f"Erreur lors de la récupération de la page du film {movie_id}. Code : {response.status_code}")
            return None
    except Exception as e:
        print(f"Erreur lors de la récupération des détails du film {movie_id}: {e}")
        return None
# def fetch_movie_details(movie_id):
#     """Récupère le synopsis et la bande-annonce d'un film à partir de TMDB."""
#     details_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=fr"
#     try:
#         response = requests.get(details_url)
#         if response.status_code == 200:
#             data = response.json()
#             synopsis = data.get('overview', 'Aucun synopsis disponible')
#             trailer_url = None
#             if 'videos' in data:
#                 for video in data['videos']['results']:
#                     if video['type'] == 'Trailer':  # Chercher la bande-annonce
#                         trailer_url = f"https://www.youtube.com/watch?v={video['key']}"
#                         break
#             return synopsis, trailer_url
#         else:
#             print(f"Erreur API pour l'ID {movie_id}: {response.status_code}")
#     except Exception as e:
#         print(f"Erreur lors de la récupération des détails pour l'ID {movie_id}: {e}")
#     return None, None


def fetch_movie_details(movie_id):
    """Récupère le synopsis et la bande-annonce d'un film à partir de TMDB."""
    details_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=fr"
    try:
        response = requests.get(details_url)
        if response.status_code == 200:
            data = response.json()
            synopsis = data.get('overview', 'Aucun synopsis disponible')
            trailer_url = None


            return synopsis
        else:
            print(f"Erreur API pour l'ID {movie_id}: {response.status_code}")
    except Exception as e:
        print(f"Erreur lors de la récupération des détails pour l'ID {movie_id}: {e}")
        return None




class Command(BaseCommand):
    help = "Fetch movie posters from TMDb and save to a CSV file."


    def handle(self, *args, **kwargs):
        """Lecture du fichier, récupération des affiches et sauvegarde."""
        # Charger les données
        print(f"Lecture du fichier {INPUT_FILE}...")
        movies = pd.read_csv(INPUT_FILE)


        # Limiter à un sous-ensemble de films pour tester (facultatif)
        # movies = movies.head(10)  # Test avec seulement les 10 premiers films


        # Ajouter une nouvelle colonne pour les URL d'affiches, synopsis et bande-annonce
        print("Récupération des URL des affiches, synopsis et bande-annonces...")


        for idx, row in movies.iterrows():
            # Récupérer l'URL de l'affiche et l'ID du film
            poster_url, movie_id = fetch_poster_url(row['Clean_Title'], row['Year'])


            if movie_id:
                # Récupérer le synopsis et la bande-annonce
                synopsis= fetch_movie_details(movie_id)
                trailer_url= fetch_youtube_trailer_url(movie_id)


                # Ajouter les informations dans le DataFrame
                movies.at[idx, 'Poster_URL'] = poster_url
                movies.at[idx, 'Synopsis'] = synopsis
                movies.at[idx, 'Trailer_URL'] = trailer_url


                print(f"Affiche pour {row['Clean_Title']} ({row['Year']}): {poster_url}")
                print(f"Synopsis: {synopsis}")
                print(f"Bande-annonce: {trailer_url}")


        # Sauvegarder les résultats dans un nouveau fichier
        print(f"Écriture du fichier de sortie dans {OUTPUT_FILE}...")
        movies.to_csv(OUTPUT_FILE, index=False)


        self.stdout.write(self.style.SUCCESS(f"Extraction des affiches terminée. Fichier sauvegardé sous '{OUTPUT_FILE}'."))



