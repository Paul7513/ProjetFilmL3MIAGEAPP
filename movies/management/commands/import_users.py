from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from movies.models import UserProfile
import csv

class Command(BaseCommand):
    help = 'Imports users from a UTF-8 encoded file (users_utf8.dat)'

    def handle(self, *args, **kwargs):
        # Chemin vers votre fichier users_utf8.dat
        file_path = '/home/manda/FilmProjet/data/ml-1m/users_utf8.dat'
        with open(file_path, 'r', encoding='utf-8') as file:
            # Parse le fichier avec les délimiteurs et les colonnes spécifiées
            for line in file:
                try:
                    user_id, gender, age, occupation, _ = line.strip().split('::')  # Ignore le champ zip_code

                    # Vérifiez si l'utilisateur existe déjà, sinon créez-le
                    if not User.objects.filter(username=user_id).exists():
                        user = User.objects.create_user(
                            username=user_id,
                            password='defaultpassword',  # Vous pouvez attribuer un mot de passe par défaut ou générer un mot de passe
                        )
                        self.stdout.write(f"User {user_id} created.")

                        # Validation des champs pour UserProfile
                        if gender not in ['M', 'F']:
                            raise ValueError(f"Invalid gender: {gender}")
                        
                        user_profile_age = self.get_age_group(age)
                        if user_profile_age == 'Unknown':
                            raise ValueError(f"Invalid age group: {age}")
                        
                        user_profile_occupation = self.get_occupation(occupation)
                        if user_profile_occupation == 'Unknown':
                            raise ValueError(f"Invalid occupation: {occupation}")
                        
                        # Afficher les valeurs avant de créer le profil
                        self.stdout.write(f"Creating profile for user {user_id}: Gender: {gender}, Age: {user_profile_age}, Occupation: {user_profile_occupation}")

                        # Créez un profil utilisateur associé
                        profile = UserProfile.objects.create(
                            user=user,
                            gender=gender,
                            age=self.get_age_value(user_profile_age),
                            occupation=self.get_occupation_value(user_profile_occupation)
                        )
                        self.stdout.write(f"Profile created for user {user_id}.")
                    
                except ValueError as e:
                    self.stdout.write(self.style.ERROR(f"Error processing line '{line.strip()}': {e}"))
                    continue  # Ignore this line and continue with the next one

            self.stdout.write(self.style.SUCCESS(f'Successfully imported users from {file_path}'))

    def get_age_group(self, age):
        age_groups = {
            '1': 'Under 18',
            '18': '18-24',
            '25': '25-34',
            '35': '35-44',
            '45': '45-49',
            '50': '50-55',
            '56': '56+'
        }
        return age_groups.get(age, 'Unknown')

    def get_age_value(self, age_group):
        # Convertir l'âge en valeur correcte pour l'enregistrement
        age_values = {
            'Under 18': 1,
            '18-24': 18,
            '25-34': 25,
            '35-44': 35,
            '45-49': 45,
            '50-55': 50,
            '56+': 56
        }
        return age_values.get(age_group, 0)  # 0 si inconnu

    def get_occupation(self, occupation_id):
        occupations = {
            '0': 'other',
            '1': 'academic/educator',
            '2': 'artist',
            '3': 'clerical/admin',
            '4': 'college/grad student',
            '5': 'customer service',
            '6': 'doctor/health care',
            '7': 'executive/managerial',
            '8': 'farmer',
            '9': 'homemaker',
            '10': 'K-12 student',
            '11': 'lawyer',
            '12': 'programmer',
            '13': 'retired',
            '14': 'sales/marketing',
            '15': 'scientist',
            '16': 'self-employed',
            '17': 'technician/engineer',
            '18': 'tradesman/craftsman',
            '19': 'unemployed',
            '20': 'writer'
        }
        return occupations.get(occupation_id, 'Unknown')

    def get_occupation_value(self, occupation_name):
        # Convertir l'occupation en valeur correcte pour l'enregistrement
        occupation_values = {
            'other': 0,
            'academic/educator': 1,
            'artist': 2,
            'clerical/admin': 3,
            'college/grad student': 4,
            'customer service': 5,
            'doctor/health care': 6,
            'executive/managerial': 7,
            'farmer': 8,
            'homemaker': 9,
            'K-12 student': 10,
            'lawyer': 11,
            'programmer': 12,
            'retired': 13,
            'sales/marketing': 14,
            'scientist': 15,
            'self-employed': 16,
            'technician/engineer': 17,
            'tradesman/craftsman': 18,
            'unemployed': 19,
            'writer': 20
        }
        return occupation_values.get(occupation_name, 0)  # 0 si inconnu
