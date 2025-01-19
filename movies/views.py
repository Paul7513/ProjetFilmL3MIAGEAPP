from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.generic import TemplateView  # Pour les classes basées sur des vues
from movies.models import UserProfile
from movies.forms import UserRegistrationForm
from django.contrib.auth import logout
from django.shortcuts import render, get_object_or_404
from .models import  UserSimilarityMatrix, Movie, Rating, Wishlist, Order, CartItem, OrderItem 
from django.core.mail import send_mail
from django.db.models import Avg
from math import floor
from django.db.models import Q,Count
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .forms import UserProfileForm 
from django.contrib import messages
from .models import CartItem
import json
from movies.recommender.recommender import recommend_movies
from .models import UserProfile  # Assure-toi d'importer le modèle UserProfile si nécessaire
import pandas as pd
import ast
import uuid
import time
from django.urls import reverse
from .models import NewsletterSubscription
from django.conf import settings


# Charger les matrices nécessaires pour la recommandation
user_movie_matrix = pd.read_csv('user_movie_matrix_with_standardized_metadata.csv', index_col=0)
user_similarity_df = pd.read_csv('user_similarity_matrix.csv', index_col=0)


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
    order_history = Order.objects.filter(user=user)  # Récupère toutes les commandes de l'utilisateur
     # Vous pouvez également récupérer les articles associés à chaque commande
    order_details = []
    for order in order_history:
        order_items = OrderItem.objects.filter(order=order)  # Récupère les articles de la commande
        subtotal = sum(item.total_price for item in order_items)  # Calcul du sous-total
        order_details.append({
            'order': order,
            'items': order_items,
            'subtotal': subtotal  # Ajout du sous-total à chaque commande
        })
    # Vous pouvez également ajouter d'autres informations, par exemple, les films de la wishlist ou les notes de films
    return render(request, 'movies/dashboard.html', {
        'user': user,
        'user_profile': user_profile,
        'wishlist_items': wishlist_items,  # Ajout de la wishlist dans le contexte
        'order_history': order_details,  # Passez les détails des commandes à la template
    })  
    # Assurez-vous que 'dashboard.html' existe dans 'movies/templates/movies/'


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
        'related_movies': related_movies,
        'note_envoyee': request.GET.get('note_envoyee', False)
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

@login_required
def remove_from_wishlist(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)  # Récupérer le film
    user = request.user

    # Vérifie si le film est bien dans la wishlist avant de le supprimer
    wishlist_item = Wishlist.objects.filter(user=user, movie=movie).first()
    if wishlist_item:
        wishlist_item.delete()
        return JsonResponse({"status": "success", "message": f"{movie.title} a été retiré de votre wishlist."})
    else:
        return JsonResponse({"status": "error", "message": f"{movie.title} n'était pas dans votre wishlist."})

@login_required
def submit_rating(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    user = request.user
    if request.method == "POST":
        rating_value = int(request.POST.get('rating'))
        
        # Créer ou mettre à jour la note
        rating, created = Rating.objects.update_or_create(
            user=user, movie=movie,
            defaults={'rating': rating_value, 'timestamp': int(time.time())}
        )
        
      
        
        # Rediriger vers la page du film
        return redirect(f"{reverse('movie_detail', kwargs={'movie_id': movie.id})}?note_envoyee=True")
        
    
    # Si l'utilisateur accède à cette URL sans POST, le rediriger vers la page du film
    return redirect(reverse('movie_detail', kwargs={'movie_id': movie.id}))


@login_required
def update_profile(request):
    user_profile = request.user.userprofile

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil mis à jour avec succès !")
            return redirect('dashboard')  # Redirige vers la page dashboard
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'movies/update_profile.html', {'form': form})

def user_profile(request):
    # Ton code pour récupérer les informations du profil utilisateur
    # Par exemple, récupérer l'utilisateur connecté et ses informations
    user = request.user
    user_profile = UserProfile.objects.get(user=user)  # Exemple de récupération de profil utilisateur
    wishlist_items = user_profile.wishlist.all()  # Exemple de récupération des films dans la wishlist
    return render(request, 'movies/user_profile.html', {
        'user': user,
        'user_profile': user_profile,
        'wishlist_items': wishlist_items,
    })

def panier(request):
    if request.user.is_authenticated:
        # Utilisateur connecté : récupérer les éléments depuis la base de données
        cart_items = CartItem.objects.filter(user=request.user)
        total_amount = sum(item.total_price() for item in cart_items)  # Utilisation correcte
    else:
        # Utilisateur non connecté : récupérer les éléments depuis la session
        cart_items = []
        cart_data = request.session.get('cart_items', {})
        for movie_id, item in cart_data.items():
            movie = Movie.objects.get(id=movie_id)
            cart_items.append({
                'movie': movie,
                'quantity': item['quantity'],
                'total_price': movie.price * item['quantity']  # Utilisation d'un dictionnaire ici
            })
        total_amount = sum(item['total_price'] for item in cart_items)

    return render(request, 'movies/panier.html', {
        'cart_items': cart_items,
        'total_amount': total_amount
    })

def add_to_cart(request, movie_id):
    movie = Movie.objects.get(id=movie_id)
    if request.user.is_authenticated:
        cart_item, created = CartItem.objects.get_or_create(user=request.user, movie=movie)
        if not created:
            cart_item.quantity += 1
            cart_item.save()
    else:
          # Utilisateur non connecté : sauvegarde dans la session sous 'cart_items'
        cart = request.session.get('cart_items', {})
        if str(movie_id) in cart:
            cart[str(movie_id)]['quantity'] += 1
        else:
            cart[str(movie_id)] = {'quantity': 1}
        request.session['cart_items'] = cart  # Mise à jour de la session

    return JsonResponse({'status': 'success', 'message': 'Film ajouté au panier'})


import uuid

def checkout(request):
    print("Début de la vue checkout")

    # Gestion du panier pour utilisateur connecté ou anonyme
    if request.user.is_authenticated:
        print(f"Utilisateur connecté : {request.user.username}")
        # Utilisateur connecté
        cart_items = CartItem.objects.filter(user=request.user)
        print(f"Panier de l'utilisateur connecté : {cart_items}")
    else:
        print("Utilisateur anonyme")
        # Utilisateur anonyme : on récupère les articles depuis la session 'cart_items'
        cart_items = request.session.get('cart_items', {})
        print(f"Panier de l'utilisateur anonyme (en session) : {cart_items}")

        # Conversion des données de session en objets semblables à CartItem (avec Movie)
        cart_items = [
            {
                'movie': Movie.objects.get(id=movie_id),  # Récupérer le film
                'quantity': item['quantity'],
                'price': Movie.objects.get(id=movie_id).price  # Récupérer le prix
            }
            for movie_id, item in cart_items.items()
        ]
        print(f"Panier après transformation : {cart_items}")

    # Vérification du contenu du panier
    if not cart_items:
        print("Le panier est vide.")
        # Affichage d'un message d'erreur si le panier est vide
        messages.error(request, "Votre panier est vide.")
        return redirect('panier')  # Redirection vers la page panier

    # Calculer le montant total
    if request.user.is_authenticated:
        total_amount = sum(item.quantity * item.movie.price for item in cart_items)
    else:
        total_amount = sum(item['quantity'] * item['price'] for item in cart_items)

    print(f"Montant total du panier : {total_amount} €")

    if request.method == "POST":
        print("Traitement de la commande (POST)")
        # Traitement des informations de commande
        first_name = request.POST.get('firstName')
        last_name = request.POST.get('lastName')
        email = request.POST.get('email')

        print(f"Nom : {first_name}, Prénom : {last_name}, Email : {email}")

        if not all([first_name, last_name, email]):
            print("Des champs sont manquants.")
            messages.error(request, "Tous les champs doivent être remplis.")
            return redirect('checkout')  # Rediriger vers la même page si des champs sont manquants

        # Génération du numéro de suivi
        tracking_number = str(uuid.uuid4().hex[:12]).upper()
        print(f"Numéro de suivi généré : {tracking_number}")

        # Créer une commande
        if request.user.is_authenticated:
            print("Création de la commande pour un utilisateur connecté.")
            order = Order.objects.create(user=request.user, status="pending", tracking_number=tracking_number)
            for item in cart_items:
                total_price = item.quantity * item.movie.price
                print(f"Création de l'OrderItem pour le film : {item.movie.title}, Quantité : {item.quantity}, Prix total : {total_price}")
                OrderItem.objects.create(
                    order=order,
                    movie=item.movie,
                    quantity=item.quantity,
                    price_per_item=item.movie.price,
                    total_price=total_price
                )
            CartItem.objects.filter(user=request.user).delete()  # Vider le panier utilisateur
            print("Panier utilisateur vidé après commande.")
        else:
            # Pour les utilisateurs non connectés
            order = Order.objects.create(user=None, status="pending", tracking_number=tracking_number)
            for item in cart_items:
                total_price = item['quantity'] * item['price']
                print(f"Création de l'OrderItem pour le film (anonyme) : {item['movie'].title}, Quantité : {item['quantity']}, Prix total : {total_price}")
                OrderItem.objects.create(
                    order=order,
                    movie=item['movie'],  # Utilisation de item['movie'] pour accéder à l'objet Movie
                    quantity=item['quantity'],
                    price_per_item=item['price'],
                    total_price=total_price
                )
            request.session['cart_items'] = []  # Vider le panier en session pour un utilisateur anonyme
            print("Panier vidé pour un utilisateur anonyme après commande.")
        # Envoi de l'email de confirmation
        print(f"Envoi de l'email à {email}")
        send_mail(
            'Confirmation de commande',
            f'Merci {first_name}, votre commande a bien été enregistrée.',
            'from@example.com',
            [email],
            fail_silently=False,
        )

        # Message de succès
        print("Commande validée avec succès !")
        messages.success(request, "Votre commande a été validée avec succès!")

        # Renvoyer la page avec les informations mises à jour
        context = {
            'cart_items': cart_items,
            'total_amount': total_amount,
            'show_modal': True  # Modal affiché après soumission
        }
        return render(request, 'movies/checkout.html', context)

    # Affichage de la page de checkout pour GET
    print("Affichage de la page de checkout pour GET")
    context = {
        'cart_items': cart_items,
        'total_amount': total_amount,
        'show_modal': False
    }
    return render(request, 'movies/checkout.html', context)




def checkout_success(request):
    return render(request, 'movies/checkout_success.html')

@login_required
def suggestion(request):
 # Récupération des paramètres de la requête
    search_query = request.GET.get('q', '')
    selected_genres = request.GET.getlist('genre')

    # Construction de la requête de filtrage de base
    query = Q()
    if search_query:
        query &= Q(title__icontains=search_query)
    if selected_genres:
        for genre in selected_genres:
            query &= Q(genre__icontains=genre)

    # Initialisation de films avec une requête vide
    films = Movie.objects.none()
    recommendations_list = []

    # Appel à la fonction de recommandation si l'utilisateur est authentifié
    if request.user.is_authenticated:
        user_id = request.user.id
        try:
            # Charger les matrices de données
            user_movie_matrix = pd.read_csv('user_movie_matrix_with_standardized_metadata.csv', index_col=0)
            user_similarity_df = pd.read_csv('user_similarity_matrix.csv', index_col=0)

            # Appel à la fonction de recommandation
            recommendations_list = recommend_movies(
                user_id=user_id, 
                user_similarity_df=user_similarity_df, 
                user_movie_matrix=user_movie_matrix, 
                k=5
            )

            # Conversion des éléments de la liste en entiers
            recommendations_list = [int(movie_id) for movie_id in recommendations_list]

        except Exception as e:
            print(f"Erreur lors de la récupération des films : {e}")
            recommendations_list = []  # S'assurer que la variable est définie même en cas d'erreur

    # Récupérer les films correspondants aux IDs recommandés tout en respectant l'ordre
    if recommendations_list:  
        # Utilisation de .filter avec un tri manuel
        films = list(Movie.objects.filter(id__in=recommendations_list).annotate(
            average_rating=Avg('rating__rating')
        ))

        # Trier les films selon l'ordre des IDs dans recommendations_list
        films.sort(key=lambda x: recommendations_list.index(x.id))

        print(f"Films recommandés récupérés (ordonnés) : {[film.title for film in films]}")

    # Gestion de l'affichage des étoiles pour chaque film
    for film in films:
        rating = film.average_rating if film.average_rating else 0
        full_stars = int(rating)
        half_star = 1 if (rating - full_stars) >= 0.5 else 0
        empty_stars = 5 - full_stars - half_star
        film.star_rating = {
            'full': ['bxs-star'] * full_stars,
            'half': ['bxs-star-half'] * half_star,
            'empty': ['bx-star'] * empty_stars,
        }

    # Extraction des genres pour les filtres du formulaire
    all_genres = [
        genre for movie in Movie.objects.values_list('genre', flat=True)
        for genre in movie.split('|')
    ]
    genres = sorted(set(all_genres))

    # Définition du contexte
    context = {
        'films': films,
        'genres': genres,
        'selected_genres': selected_genres,
        'search_query': search_query,
        'no_results': len(films) == 0,  # Correction de la condition pour éviter l'erreur
    }

    return render(request, 'movies/suggestion.html', context)    



def films(request):
    from django.db.models import Q, Avg

    # Récupération des paramètres de la requête
    search_query = request.GET.get('q', '')
    selected_genres = request.GET.getlist('genre')

    # Construction de la requête avec ET logique pour la recherche et les genres
    query = Q()
    if search_query:
        query &= Q(title__icontains=search_query)
    if selected_genres:
        # On filtre uniquement si chaque genre doit être pris en compte individuellement
        for genre in selected_genres:
            query &= Q(genre__icontains=genre)

    # Application des filtres
    popular_movies = Movie.objects.filter(query).annotate(
        average_rating=Avg('rating__rating')
    ).order_by('-average_rating')

    # Gestion du message si aucun résultat
    no_results = not popular_movies.exists()

    # Calcul des étoiles pour l'affichage des notes
    for film in popular_movies:
        rating = film.average_rating if film.average_rating is not None else 0
        full_stars = int(rating)
        half_star = 1 if (rating - full_stars) >= 0.5 else 0
        empty_stars = 5 - full_stars - half_star
        film.star_rating = {
            'full': ['bxs-star'] * full_stars,
            'half': ['bxs-star-half'] * half_star,
            'empty': ['bx-star'] * empty_stars,
        }

    # Extraction des genres uniques pour les filtres
    all_genres = [
        genre for movie in Movie.objects.values_list('genre', flat=True)
        for genre in movie.split('|')
    ]
    genres = sorted(set(all_genres))

    # Rendu du template
    return render(request, 'movies/films.html', {
        'films': popular_movies,
        'genres': genres,
        'selected_genres': selected_genres,
        'search_query': search_query,
        'no_results': no_results
    })











def movie_recommendations_view(request):
    # Utilisateur à tester
    user_id = 6054
    
    # Charger ou calculer la matrice de similarité des utilisateurs (user_similarity_df)
    # Exemple : Charger les similarités utilisateur depuis la base de données
    similarities = UserSimilarityMatrix.objects.all()
    
    # Convertir les similarités en DataFrame
    similarity_data = [(sim.user1, sim.user2, sim.similarity) for sim in similarities]
    user_similarity_df = pd.DataFrame(similarity_data, columns=['user1', 'user2', 'similarity'])
    user_similarity_df = user_similarity_df.pivot(index='user1', columns='user2', values='similarity')
    
    # Charger la matrice utilisateur-film des notes (user_movie_matrix)
    ratings = Rating.objects.all()
    ratings_data = [(rating.user.id, rating.movie.id, rating.rating) for rating in ratings]
    user_movie_matrix = pd.DataFrame(ratings_data, columns=['user_id', 'movie_id', 'rating'])
    user_movie_matrix = user_movie_matrix.pivot(index='user_id', columns='movie_id', values='rating').fillna(0)

    # Appel de la fonction de recommandation pour l'utilisateur 6054
    recommended_movie_ids = recommend_movies(user_id, user_similarity_df, user_movie_matrix, k=5)
    
    # Récupérer les films correspondants depuis la base de données
    recommended_movies = Movie.objects.filter(id__in=recommended_movie_ids)
    
    # Passer les films recommandés au template
    context = {
        'recommended_movies': recommended_movies
    }
    
    return render(request, 'movies/recommendations.html', context)

def subscribe_to_newsletter(request):
    if request.method == 'POST':
        # Récupérer les données JSON envoyées par le client
        data = json.loads(request.body)
        email = data.get('email')
        
        print(f"Email reçu : {email}")  # Ajout du print pour déboguer
        
        if not email:
            return JsonResponse({"status": "error", "message": "L'adresse email est requise."})
        
        # Vérifier si l'email existe déjà
        if NewsletterSubscription.objects.filter(email=email).exists():
            return JsonResponse({"status": "error", "message": "Cet email est déjà abonné."})
        
        # Créer un nouvel abonné
        subscription = NewsletterSubscription(email=email)
        subscription.save()

         # Envoi de l'email de confirmation
        subject = 'Merci de vous être abonné à notre newsletter'
        message = (
            "Bonjour,\n\n"
            "Merci de vous être inscrit à notre newsletter ! Vous recevrez bientôt nos dernières actualités, mises à jour et offres exclusives.\n\n"
            "Cordialement,\n"
            "L'équipe de la newsletter"
        )
        from_email = settings.EMAIL_HOST_USER
        
        send_mail(subject, message, from_email, [email], fail_silently=False)
        
        return JsonResponse({"status": "success", "message": "Merci de vous être abonné à notre newsletter"})
    
    # Récupérer l'email de l'utilisateur connecté si disponible
    user_email = request.user.email if request.user.is_authenticated else None
    return render(request, 'movies/newsletter.html', {'user_email': user_email})