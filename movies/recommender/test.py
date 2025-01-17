import os
import django
import pandas as pd
from recommender import recommend_movies  # Assurez-vous que ce chemin est correct
import  os
import sys
import django

# Ajouter le chemin vers votre projet FilmProjet
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Assurez-vous que DJANGO_SETTINGS_MODULE est correctement défini
os.environ['DJANGO_SETTINGS_MODULE'] = 'FilmProjet.settings'

# Configurez Django
django.setup()

# Importez les modèles après avoir configuré Django
from movies.models import Movie

# Testez la récupération d'un film
try:
    movie = Movie.objects.first()  # Exemple de requête
    print(movie)
except Movie.DoesNotExist:
    print("Aucun film trouvé.")
# Charger les matrices de similarité et de notes des films
user_similarity_df = pd.read_csv('user_similarity_matrix.csv', index_col=0)
user_movie_matrix = pd.read_csv('user_movie_matrix_with_standardized_metadata.csv', index_col=0)

# Exemple d'appel à la fonction de recommandation
user_id = 6054  # ID de l'utilisateur pour lequel vous souhaitez des recommandations

# Récupérer les recommandations
recommendations = recommend_movies(user_id, user_similarity_df, user_movie_matrix, k=10)

# Convertir l'Index en Series pour pouvoir utiliser head()
recommendations_series = pd.Series(recommendations)

# Afficher les 10 premières recommandations
print("Top 10 recommandations de films pour l'utilisateur 6054 :")
print(recommendations_series.head(10))

# Liste des IDs de films recommandés
recommended_movie_ids = recommendations_series.head(10).tolist()

# Récupérer les films correspondant aux IDs recommandés
recommended_movies = Movie.objects.filter(id__in=recommended_movie_ids)

# Afficher les titres des films recommandés
for movie in recommended_movies:
    print(f"ID: {movie.id}, Title: {movie.title}, Genre: {movie.genre}")
