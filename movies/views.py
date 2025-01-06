from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.generic import TemplateView  # Pour les classes basées sur des vues
from movies.models import UserProfile
from movies.forms import UserRegistrationForm
from django.contrib.auth import logout
from django.shortcuts import render, get_object_or_404
from .models import Movie, Rating, Wishlist
from django.db.models import Avg
from math import floor
from django.db.models import Q,Count
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

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

@login_required
def dashboard(request):
    user = request.user  # Récupère l'utilisateur connecté
    user_profile = user.userprofile  # Récupère le profil utilisateur (assurez-vous que UserProfile existe pour l'utilisateur)
    wishlist_items = user.wishlist_set.all()  # Récupère tous les films de la wishlist de l'utilisateur
    # Vous pouvez également ajouter d'autres informations, par exemple, les films de la wishlist ou les notes de films
    return render(request, 'movies/dashboard.html', {
        'user': user,
        'user_profile': user_profile,
        'wishlist_items': wishlist_items,  # Ajout de la wishlist dans le contexte
    })  # Assurez-vous que 'dashboard.html' existe dans 'movies/templates/movies/'


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
    
   # Calculer la note moyenne (si elle existe)
    rating = movie.rating_set.aggregate(average_rating=Avg('rating'))['average_rating'] or 0

    # Calculer les étoiles
    full_stars = floor(rating)  # Nombre d'étoiles pleines
    half_star = 1 if (rating - full_stars) >= 0.5 else 0  # Demi-étoile si la décimale est >= 0.5
    empty_stars = 5 - full_stars - half_star  # Nombre d'étoiles vides

    # Créer des listes pour chaque type d'étoile
    star_rating = {
        'full': ['bxs-star'] * full_stars,
        'half': ['bxs-star-half'] * half_star,
        'empty': ['bx-star'] * empty_stars,
    }
#  
   # Diviser les genres du film actuel en une liste
    genres_list = [genre.strip() for genre in movie.genre.split(',')]

    # Construire une requête Q pour vérifier chaque genre
    genre_query = Q()
    for genre in genres_list:
        genre_query |= Q(genre__icontains=genre)

    # Requête pour trouver les films ayant au moins un genre en commun, en excluant le film lui-même
    related_movies = Movie.objects.filter(genre_query).exclude(id=movie.id).distinct()[:5]


    return render(request, 'movies/article.html', {
        'movie': movie,
        'star_rating': star_rating,
        'rating': rating,
        'related_movies': related_movies
})

@login_required
def add_to_wishlist(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)  # Récupère le film par son ID
    user = request.user

    # Vérifie si le film est déjà dans la wishlist de l'utilisateur
    if not Wishlist.objects.filter(user=user, movie=movie).exists():
        # Si ce n'est pas le cas, ajoute-le à la wishlist
        Wishlist.objects.create(user=user, movie=movie)

    # Retourner une réponse JSON pour signaler que l'ajout a réussi
    return JsonResponse({"status": "success", "message": f"{movie.title} ajouté à votre wishlist."})