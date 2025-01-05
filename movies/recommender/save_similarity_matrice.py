import os
import sys
import pandas as pd

# Ajoutez le chemin du projet à sys.path
sys.path.append('/home/manda/FilmProjet')

# Configurez les paramètres Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'FilmProjet.settings'

import django
django.setup()

# Importez les modèles
from movies.models import UserSimilarityMatrix

user_similarity_df = pd.read_csv('user_similarity_matrix_full.csv', index_col=0)

def save_similarity_matrix(user_similarity_df):
    for i in range(user_similarity_df.shape[0]):
        for j in range(i+1, user_similarity_df.shape[1]):  # Ne pas doubler les paires (symétriques)
            user_id_1 = user_similarity_df.index[i]
            user_id_2 = user_similarity_df.columns[j]
            similarity = user_similarity_df.iloc[i, j]

            # Enregistrez la similarité dans la table
            if similarity > 0:  # Enregistrer uniquement si la similarité est significative
                UserSimilarityMatrix.objects.update_or_create(
                    user_id_1=user_id_1,
                    user_id_2=user_id_2,
                    defaults={'similarity': similarity}
                )
