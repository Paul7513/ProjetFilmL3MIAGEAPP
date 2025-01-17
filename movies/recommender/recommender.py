def recommend_movies(user_id, user_similarity_df, user_movie_matrix, k=5):
    """
    Fonction de recommandation pour suggérer des films à un utilisateur en fonction des k plus proches voisins.

    Args:
        user_id (int): L'ID de l'utilisateur auquel nous recommandons des films.
        user_similarity_df (pd.DataFrame): La matrice de similarité utilisateur (similarité cosinus).
        user_movie_matrix (pd.DataFrame): La matrice utilisateur-film des notes.
        k (int): Le nombre de voisins les plus proches à considérer.

    Returns:
        list: Une liste des IDs des films recommandés.
    """
    # Étape 1 : Trouver les k plus proches voisins
    user_similarities = user_similarity_df.loc[user_id]
    
    # Étape 2 : Obtenir les k plus proches voisins (ceci doit être fait avant d'utiliser k_nearest_neighbors)
    k_nearest_neighbors = user_similarities.sort_values(ascending=False).iloc[1:k+1]
    
    # Étape 3 : Obtenir les notes des k plus proches voisins
    neighbors_ratings = user_movie_matrix.loc[k_nearest_neighbors.index.astype(int)]
    
    # Étape 4 : Calculer la moyenne pondérée des notes pour chaque film
    weighted_ratings = neighbors_ratings.T.dot(k_nearest_neighbors.values)
    total_similarity = k_nearest_neighbors.sum()
    movie_scores = weighted_ratings / total_similarity
    
    # Étape 5 : Supprimer les films déjà notés par l'utilisateur
    user_rated_movies = user_movie_matrix.loc[user_id]
    movies_to_recommend = movie_scores[user_rated_movies == 0]
    
    # Étape 6 : Trier les films par les scores les plus élevés
    recommended_movies = movies_to_recommend.sort_values(ascending=False)
    
    # Retourner la liste des IDs des films recommandés
    return recommended_movies.index.tolist()
