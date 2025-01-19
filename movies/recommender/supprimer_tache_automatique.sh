#!/bin/bash

# Chemin du script à supprimer de cron
PROJECT_PATH=$(pwd)
SCRIPT_PATH="/home/manda/FilmProjet/movies/recommender/matrix_builder.py"

# Supprimer la tâche cron associée
echo "Suppression de la tâche cron associée à $SCRIPT_PATH..."
crontab -l | grep -v "$SCRIPT_PATH" | crontab -

# Confirmer la suppression
echo "Tâche cron supprimée avec succès. Voici les tâches restantes :"
crontab -l
