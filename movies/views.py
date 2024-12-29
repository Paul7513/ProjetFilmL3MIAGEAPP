from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.generic import TemplateView  # Pour les classes basées sur des vues
from movies.models import UserProfile
from movies.forms import UserRegistrationForm
from django.contrib.auth import logout
from django.shortcuts import render
from .models import Movie
from django.db.models import Avg
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
   