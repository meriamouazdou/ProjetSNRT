from django.shortcuts import render

# Create your views here.
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .models import UserRole

@login_required
def redirect_after_login(request):
    user = request.user

    try:
        role_obj = user.user_role  # via related_name='user_role'
    except UserRole.DoesNotExist:
        # Si l'utilisateur n'a pas de rôle défini
        return redirect('no_role_page')  # À personnaliser

    # Redirection selon le rôle
    if role_obj.role == 'directeur':
        return redirect('dashboard_directeur')
    elif role_obj.role == 'chef_projet':
        return redirect('dashboard_chef_projet')
    elif role_obj.role == 'chef_departement':
        return redirect('dashboard_chef_departement')
    elif role_obj.role == 'cs':
        return redirect('dashboard_cs')
    else:
        return redirect('default_dashboard')
