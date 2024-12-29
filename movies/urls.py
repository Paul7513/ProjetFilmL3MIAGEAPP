from django.urls import path
from django.contrib.auth import views as auth_views
from . import views  # Import de vos vues personnalisées


urlpatterns = [
    # Page d'inscription
    path('register/', views.register, name='register'), 

    # Page d'accueil
    path('', views.home, name='home'),  

    # Connexion avec la vue intégrée de Django
    path(
        'login/',
        auth_views.LoginView.as_view(template_name='movies/login.html'),
        name='login'
    ),

    # Tableau de bord
    path('dashboard/', views.dashboard, name='dashboard'),

    # Déconnexion
    path('logout/', views.logout_view, name='logout'),
     # Déconnexion avec la vue intégrée de Django
    #path('logout/', auth_views.LogoutView.as_view(), name='movies/logout'),

     # Nouvelle route pour `index.html`
    path('index/', views.index, name='index'),  # Nouvelle vue pour votre fichier
]
