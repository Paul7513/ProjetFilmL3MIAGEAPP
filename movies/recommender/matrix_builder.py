#!/usr/bin/env python3
import os
import django
import pandas as pd
import numpy as np
import sys
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity

def main():
    # Ajouter le chemin du projet au sys.path pour que Django puisse le trouver
    sys.path.append('/home/manda/FilmProjet')

    # Définir la variable d'environnement pour le fichier settings.py
    os.environ['DJANGO_SETTINGS_MODULE'] = 'FilmProjet.settings'
    # Chemin absolu vers le répertoire où sauvegarder les fichiers
    recommender_dir = '/home/manda/FilmProjet/movies/recommender'
    # Initialiser Django
    django.setup()

    # Importer les modèles nécessaires
    from movies.models import Rating, UserProfile, Wishlist

    # Charger les notes des films
    ratings = pd.DataFrame(Rating.objects.values('user_id', 'movie_id', 'rating'))

    # Charger les Wishlists des utilisateurs
    wishlists = pd.DataFrame(Wishlist.objects.values('user_id', 'movie_id'))

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

    # Créer la liste complète des utilisateurs et des films
    all_user_ids = user_profiles['user_id'].unique()  # Tous les utilisateurs
    all_movie_ids = np.unique(np.concatenate((ratings['movie_id'].unique(), wishlists['movie_id'].unique())))

    # Créer une matrice utilisateur-film complète avec toutes les combinaisons
    full_user_movie_matrix = pd.DataFrame(index=all_user_ids, columns=all_movie_ids).fillna(0)

    # Remplir la matrice avec les notes existantes
    for _, row in ratings.iterrows():
        full_user_movie_matrix.at[row['user_id'], row['movie_id']] = row['rating']

    # Ajouter les films de la Wishlist à la matrice utilisateur-film
    for _, row in wishlists.iterrows():
        # Attribuer un score de 1.0 pour les films dans la Wishlist
        full_user_movie_matrix.at[row['user_id'], row['movie_id']] += 1.0

    # Joindre les métadonnées utilisateur (âge et occupation encodée)
    full_user_movie_matrix = full_user_movie_matrix.join(user_profiles.set_index('user_id'))

    # Standardisation des données (âge et occupation uniquement, pas les notes de films)
    user_metadata_columns = ['age'] + [col for col in user_profiles.columns if col.startswith('occupation_')]

    # Standardisation de ces colonnes uniquement
    full_user_movie_matrix[user_metadata_columns] = scaler.fit_transform(full_user_movie_matrix[user_metadata_columns])

    # Sauvegarder la matrice mise à jour
    full_user_movie_matrix.to_csv(os.path.join(recommender_dir,'user_movie_matrix_with_standardized_metadata.csv'))

    # Calcul de la similarité des utilisateurs en utilisant la similarité cosinus
    user_similarity = cosine_similarity(full_user_movie_matrix)

    # Sauvegarder la matrice de similarité
    user_similarity_df = pd.DataFrame(user_similarity, index=full_user_movie_matrix.index, columns=full_user_movie_matrix.index)
    user_similarity_df.to_csv(os.path.join(recommender_dir,'user_similarity_matrix.csv'))

    # Afficher un aperçu des résultats
    print(user_profiles.columns)  # Vérifier si 'age' est bien présent
    print(user_profiles.tail())  # Afficher les 5 dernières lignes
    print("Matrice de similarité sauvegardée avec succès.")

    # Sauvegarder la matrice de similarité complète
    user_similarity_df.to_csv(os.path.join(recommender_dir,'user_similarity_matrix_full.csv'))

    # Afficher un aperçu des résultats
    print(user_profiles.columns)  # Vérifier si 'age' est bien présent
    print(user_profiles.tail())  # Afficher les 5 dernières lignes

if __name__ == "__main__":
    print("Calcul et sauvegarde de la matrice de similarité incluant les Wishlists...")
    main()
