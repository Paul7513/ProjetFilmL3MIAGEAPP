import sys
import pandas as pd  # Importation de pandas
sys.path.append('/home/manda/FilmProjet/')
from movies.recommender.recommender import recommend_movies

# Charger les matrices nécessaires
user_movie_matrix = pd.read_csv('user_movie_matrix_with_standardized_metadata.csv', index_col=0)
user_similarity_df = pd.read_csv('user_similarity_matrix.csv', index_col=0)

# Spécifier un ID utilisateur pour tester
user_id = 3000  # Exemple d'ID utilisateur

# Définir le nombre de voisins k
k = 5

# Obtenir les recommandations pour cet utilisateur
recommendations = recommend_movies(user_id=user_id, 
                                   user_similarity_df=user_similarity_df, 
                                   user_movie_matrix=user_movie_matrix, 
                                   k=k)

# Afficher les recommandations
print(f"Top 10 recommandations de films pour l'utilisateur {user_id} :")
print(recommendations.head(10))
