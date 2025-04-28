from django.urls import path
from .views import login, logout, registration, current, tg_auth

app_name = 'user'

urlpatterns = [
    path('registration/', registration, name='registration'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('current/', current, name='current'),
    path('tg_auth/', tg_auth, name='tg_auth'),
] 