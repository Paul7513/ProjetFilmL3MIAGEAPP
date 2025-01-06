from django.db import models
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User
from django.views.generic import TemplateView

class Movie(models.Model):
    title = models.CharField(max_length=255)
    genre = models.CharField(max_length=100)
    synopsis = models.TextField(blank=True)  # Description optionnelle au départ
    release_date = models.DateField(null=True, blank=True)  # Null si année manquante
    year = models.IntegerField(null=True, blank=True)  # Année en tant qu'entier (extrait)
    poster_url = models.URLField(max_length=500, null=True, blank=True)  # URL de l'affiche
    trailer_url = models.URLField(max_length=500, null=True, blank=True)  # URL de la bande-annonce
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Prix du film (par exemple 19.99)

    
# class Movie(models.Model):
#     title = models.CharField(max_length=255)
#     genre = models.CharField(max_length=100)
#     description = models.TextField()
#     release_date = models.DateField()

def __str__(self):
    return self.title


def __str__(self):
    return self.title

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    added_on = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.movie.title}"

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    rating = models.IntegerField()
    timestamp = models.BigIntegerField()

    def __str__(self):
        return f"{self.user.username} rated {self.movie.title} as {self.rating}"

# class Order(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
#     order_date = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Order by {self.user.username} for {self.movie.title}"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('completed', 'Completed')])
    tracking_number = models.CharField(max_length=100, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Calculer automatiquement le prix total basé sur le prix du film et la quantité
        self.total_price = self.quantity * self.movie.price  # Assurez-vous que le modèle Movie a un champ price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order by {self.user.username} for {self.movie.title} - {self.status}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female')], null=True)
    age = models.IntegerField(choices=[
        (1, "Under 18"),
        (18, "18-24"),
        (25, "25-34"),
        (35, "35-44"),
        (45, "45-49"),
        (50, "50-55"),
        (56, "56+")
    ], null=True)
    occupation = models.IntegerField(choices=[
        (0, "Other or not specified"),
        (1, "Academic/Educator"),
        (2, "Artist"),
        (3, "Clerical/Admin"),
        (4, "College/Grad student"),
        (5, "Customer service"),
        (6, "Doctor/Healthcare"),
        (7, "Executive/Managerial"),
        (8, "Farmer"),
        (9, "Homemaker"),
        (10, "K-12 student"),
        (11, "Lawyer"),
        (12, "Programmer"),
        (13, "Retired"),
        (14, "Sales/Marketing"),
        (15, "Scientist"),
        (16, "Self-employed"),
        (17, "Technician/Engineer"),
        (18, "Tradesman/Craftsman"),
        (19, "Unemployed"),
        (20, "Writer")
    ], null=True)
   
class CustomLoginView(LoginView):
    def get_success_url(self):
        if self.request.user.is_superuser:
            return '/admin/'  # Redirection pour les super utilisateurs
        return '/dashboard/'  # Redirection pour les utilisateurs normaux

    def __str__(self):
        return self.user.username




class UserSimilarityMatrix(models.Model):
    user1 = models.IntegerField()
    user2 = models.IntegerField()
    similarity = models.FloatField()

    class Meta:
        unique_together = ('user1', 'user2')
