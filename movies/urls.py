from django.urls import path
from django.contrib.auth import views as auth_views
from . import views  # Import de vos vues personnalisées
from .views import top_rated_movies_view  # Import de la vue
from .views import movie_detail, submit_rating


urlpatterns = [
    # Page d'inscription
    path('register/', views.register, name='register'), 

      path('films/', views.films, name='films'), 
    
    # Page d'accueil
    path('', views.home, name='home'),  

    path('', views.index, name='index'),

    # Connexion avec la vue intégrée de Django
    path(
        'login/',
        auth_views.LoginView.as_view(template_name='movies/login.html'),
        name='login'
    ),

    # Tableau de bord
    path('dashboard/', views.dashboard, name='dashboard'),

    # Déconnexion
      path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
     # Déconnexion avec la vue intégrée de Django
    #path('logout/', auth_views.LogoutView.as_view(), name='movies/logout'),

     # Nouvelle route pour `index.html`
    path('index/', views.index, name='index'),  # Nouvelle vue pour votre fichier

     path('article/<int:movie_id>/', views.movie_detail, name='movie_detail'),
      path('panier/', views.panier, name='panier'),  # Route ajoutée
  
  
    path('movie/<int:movie_id>/add_to_wishlist/', views.add_to_wishlist, name='add_to_wishlist'),

    path('wishlist/remove/<int:movie_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),

    
    # URL pour la page du tableau de bord (ajustez selon ton nom d'URL)
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/update/', views.update_profile, name='update_profile'),  # Utiliser update_profile
    path('add_to_cart/<int:movie_id>/', views.add_to_cart, name='add_to_cart'),  # Passage de movie_id
    path('checkout/', views.checkout, name='checkout'),
    path('films/', views.films, name='films'),
    path('suggestion/', views.suggestion, name='suggestion'),
     path('article/<int:movie_id>/submit_rating/', views.submit_rating, name='submit_rating'),  # Ajoutez cette ligne
     

]
