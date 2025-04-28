import json

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.http import JsonResponse
from validate_email import validate_email
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from settings.aboba_swagger import aboba_swagger

from .middleware import create_token_obj, get_request_token, set_token_in_response
from .models import CustomUser
from .forms import CustomUserCreationForm, CustomAuthenticationForm

def register(request):
    if request.user.is_authenticated:
        return redirect('barter:ad_list')
        
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Создаем пользователя с хешированным паролем
            user = CustomUser.objects.create(
                username=form.cleaned_data['email'],
                email=form.cleaned_data['email'],
                password=make_password(form.cleaned_data['password1']),
                is_active=True
            )
            
            # Создаем токен и сохраняем его в базе
            token = create_token_obj(request, user)
            user.token_hash = token
            user.token_created_at = timezone.now()
            user.save()
            
            # Устанавливаем токен в ответ
            response = redirect('barter:ad_list')
            set_token_in_response(response, token)
            messages.success(request, 'Регистрация успешна!')
            return response
    else:
        form = CustomUserCreationForm()
    return render(request, 'user/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('barter:ad_list')
        
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                if user.is_active:
                    # Создаем новый токен и сохраняем его в базе
                    token = create_token_obj(request, user)
                    user.token_hash = token
                    user.token_created_at = timezone.now()
                    user.save()
                    
                    # Устанавливаем токен в ответ
                    response = redirect('barter:ad_list')
                    set_token_in_response(response, token)
                    messages.success(request, 'Вы успешно вошли в систему!')
                    return response
                else:
                    messages.error(request, 'Ваш аккаунт неактивен')
            else:
                messages.error(request, 'Неверный email или пароль')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'user/login.html', {'form': form})

@login_required
def logout_view(request):
    request.user.token_hash = None
    request.user.token_created_at = None
    request.user.save()

    return redirect('barter:ad_list')

@login_required
def current(request):
    return JsonResponse({
        'user': {
            'email': request.user.email,
            'tg_id': request.user.tg_id,
            'groups': [group.name for group in request.user.groups.all()]
        }
    }, status=200)