from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.generic import TemplateView  # Pour les classes basées sur des vues
from movies.models import UserProfile
from movies.forms import UserRegistrationForm
from django.contrib.auth import logout
from django.shortcuts import render, get_object_or_404
from .models import Movie, Rating
from django.db.models import Avg
from math import floor
# Classe pour la vue tableau de bord
class DashboardView(TemplateView):
    template_name = 'dashboard.html'  # Assurez-vous que ce fichier existe

# Vue pour l'inscription
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Créez l'utilisateur
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            # Créez le profil utilisateur
            UserProfile.objects.create(
                user=user,
                gender=form.cleaned_data['gender'],
                age=form.cleaned_data['age'],
                occupation=form.cleaned_data['occupation']
            )

            messages.success(request, 'Your account has been created successfully!')
            return redirect('login')  # Redirigez vers une page de connexion après inscription
    else:
        form = UserRegistrationForm()

    return render(request, 'movies/register.html', {'form': form})

def dashboard(request):
    return render(request, 'movies/dashboard.html')  # Assurez-vous que 'dashboard.html' existe dans 'movies/templates/movies/'


def home(request):
    return render(request, 'movies/home.html')  # Chemin correct pour le fichier home.html

def logout_view(request):
    logout(request)  # Déconnecte l'utilisateur
    return redirect('login')  # Redirige vers la page de connexion 

from django.shortcuts import render

def index(request):
    return render(request, 'movies/index.html')
   

def top_rated_movies_view(request):
    movies = Movie.objects.annotate(average_rating=Avg('rating__rating')).order_by('-average_rating')
    return render(request, 'movies/index.html',{'movies':movies})

def index(request):
    # Récupérer les films populaires
    popular_movies = Movie.objects.annotate(
        average_rating=Avg('rating__rating')
    ).order_by('-average_rating')

    # Calculer les étoiles pour chaque film
    for film in popular_movies:
        # Vérifier si la note moyenne est None et la remplacer par 0 si c'est le cas
        rating = film.average_rating if film.average_rating is not None else 0

        # Calculer la note moyenne arrondie à 0.5 près
        full_stars = floor(rating)  # Nombre d'étoiles pleines
        half_star = 1 if (rating - full_stars) >= 0.5 else 0  # Moitié étoile
        empty_stars = 5 - full_stars - half_star  # Nombre d'étoiles vides

        # Créer des listes pour chaque type d'étoile
        film.star_rating = {
            'full': ['bxs-star'] * full_stars,
            'half': ['bxs-star-half'] * half_star,
            'empty': ['bx-star'] * empty_stars,
        }


    return render(request, 'movies/index.html', {'films': popular_movies})

def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    return render(request, 'movies/article.html', {'movie': movie})
