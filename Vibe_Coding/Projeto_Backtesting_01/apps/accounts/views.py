from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.accounts.forms import ProfileForm


@login_required
def profile(request):
    """Display and edit the logged-in user's profile."""
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil atualizado com sucesso!")
        else:
            messages.error(request, "Corrija os erros abaixo.")
    else:
        form = ProfileForm(instance=request.user)

    return render(request, "account/profile.html", {"form": form})
