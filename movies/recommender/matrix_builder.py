import os
import django
import pandas as pd
import numpy as np
import sys
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity

# Ajouter le chemin du projet au sys.path pour que Django puisse le trouver
sys.path.append('/home/manda/FilmProjet')

# Définir la variable d'environnement pour le fichier settings.py
os.environ['DJANGO_SETTINGS_MODULE'] = 'FilmProjet.settings'

# Initialiser Django
django.setup()

# Importer les modèles nécessaires
from movies.models import Rating, UserProfile

# Charger les notes des films
ratings = pd.DataFrame(Rating.objects.values('user_id', 'movie_id', 'rating'))

# Charger les profils utilisateurs depuis la base de données Django (UserProfile)
user_profiles = UserProfile.objects.all().values('user_id', 'age', 'occupation')

# Convertir les données des profils utilisateurs en DataFrame
user_profiles = pd.DataFrame(user_profiles)

# Vérifier si des utilisateurs manquent dans les ratings
missing_users = ratings[~ratings['user_id'].isin(user_profiles['user_id'])]
print(missing_users['user_id'].unique())
if not missing_users.empty:
    print("Utilisateurs manquants dans UserProfile :", missing_users['user_id'].unique())
    # Ajouter des utilisateurs fictifs avec des valeurs par défaut
    default_age = user_profiles['age'].mean()
    default_occupation = 0  # Occupation par défaut
    missing_profiles = pd.DataFrame({
        'user_id': missing_users['user_id'].unique(),
        'age': default_age,
        'occupation': default_occupation
    })
    user_profiles = pd.concat([user_profiles, missing_profiles], ignore_index=True)

# Préparation des colonnes d'occupation (one-hot encoding)
occupation_dummies = pd.get_dummies(user_profiles['occupation'], prefix='occupation')
user_profiles = pd.concat([user_profiles, occupation_dummies], axis=1)

# Standardisation des données d'âge et occupation
scaler = StandardScaler()

# Normalisation de l'âge
user_profiles[['age']] = scaler.fit_transform(user_profiles[['age']])

# Fusionner les profils utilisateurs avec les ratings (moyenne des ratings pour chaque utilisateur)
ratings_with_profiles = ratings.merge(user_profiles, on='user_id', how='left')

# Créer la matrice utilisateur-film (matrice de ratings)
user_movie_matrix = ratings_with_profiles.pivot_table(index='user_id', columns='movie_id', values='rating', fill_value=0)

# Supprimer la colonne 'user_id' et ajouter des informations supplémentaires sur les utilisateurs (occupation et age)
user_profiles = user_profiles.set_index('user_id')

# Joindre la matrice utilisateur-film avec les métadonnées utilisateur (occupation et age)
user_metadata = user_profiles[['age'] + [col for col in user_profiles.columns if col.startswith('occupation_')]]

# Joindre les colonnes d'occupation et d'âge à la matrice des films
user_movie_matrix = user_movie_matrix.join(user_metadata)

# Standardiser la matrice complète avec les informations utilisateur (age et occupation)
user_movie_matrix_standardized = user_movie_matrix.apply(
    lambda x: scaler.fit_transform(x.values.reshape(-1, 1)).flatten() 
    if x.name in user_metadata.columns else x
)

# Sauvegarder la matrice de similarité
user_movie_matrix_standardized.to_csv('user_movie_matrix_with_standardized_metadata.csv')

# Calcul de la similarité des utilisateurs en utilisant la similarité cosinus
user_similarity = cosine_similarity(user_movie_matrix_standardized)

# Sauvegarder la matrice de similarité
user_similarity_df = pd.DataFrame(user_similarity, index=user_movie_matrix.index, columns=user_movie_matrix.index)
user_similarity_df.to_csv('user_similarity_matrix.csv')

# Afficher un aperçu des résultats
# Afficher les 20 premières lignes
#print(user_similarity_df.head(20))
# Sauvegarder la matrice dans un fichier CSV
# Accéder à la colonne 'age' dans la matrice user_movie_matrix

print(user_profiles.columns)  # Vérifier si 'age' est bien présent
print(user_profiles.tail())
# Afficher les 5 premières valeurs de la colonne 'age'


user_similarity_df.to_csv('user_similarity_matrix_full.csv')

