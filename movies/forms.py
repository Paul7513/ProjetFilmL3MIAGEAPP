from django import forms
from django.contrib.auth.models import User
from movies.models import UserProfile

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female')]
    AGE_GROUP_CHOICES = [
        (1, "Under 18"),
        (18, "18-24"),
        (25, "25-34"),
        (35, "35-44"),
        (45, "45-49"),
        (50, "50-55"),
        (56, "56+"),
    ]
    OCCUPATION_CHOICES = [
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
        (20, "Writer"),
    ]

    gender = forms.ChoiceField(choices=GENDER_CHOICES, label="Gender")
    age = forms.ChoiceField(choices=AGE_GROUP_CHOICES, label="Age Group")
    occupation = forms.ChoiceField(choices=OCCUPATION_CHOICES, label="Occupation")

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data
