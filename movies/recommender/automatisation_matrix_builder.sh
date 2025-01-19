#!/bin/bash

# Détecter l'environnement Python virtuel
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Veuillez activer votre environnement virtuel Python avant d'exécuter ce script."
    exit 1
fi

# Chemin du projet et du script
PROJECT_PATH=$(pwd)
SCRIPT_PATH="$PROJECT_PATH/matrix_builder.py"
PYTHON_EXEC=$(which python3)

# Ajouter une tâche cron
echo "Configuration de la tâche cron..."
(crontab -l 2>/dev/null; echo "10 22 * * * /home/manda/FilmProjet/env/bin/python3 /home/manda/FilmProjet/movies/recommender/matrix_builder.py

") | crontab -

# Afficher la tâche ajoutée
echo "Tâche cron configurée avec succès :"
crontab -l | grep "$SCRIPT_PATH"

echo "Le calcul de la matrice de similarité sera exécuté chaque jour à 1h."
