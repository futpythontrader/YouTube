from django import forms
from django.contrib.auth.models import User


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name"]
        labels = {
            "first_name": "Nome",
            "last_name": "Sobrenome",
        }
        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "placeholder": "Seu nome",
                    "class": "w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "placeholder": "Seu sobrenome",
                    "class": "w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                }
            ),
        }
