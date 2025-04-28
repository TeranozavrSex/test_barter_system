from django.urls import path
from . import views

app_name = 'barter'

urlpatterns = [
    path('', views.AdListView.as_view(), name='ad_list'),
    path('my-ads/', views.MyAdsListView.as_view(), name='my_ads'),
    path('ad/<int:pk>/', views.AdDetailView.as_view(), name='ad_detail'),
    path('ad/create/', views.AdCreateView.as_view(), name='ad_create'),
    path('ad/<int:pk>/update/', views.AdUpdateView.as_view(), name='ad_update'),
    path('ad/<int:pk>/delete/', views.AdDeleteView.as_view(), name='ad_delete'),
    path('proposals/my/', views.MyProposalsListView.as_view(), name='my_proposals'),
    path('proposals/create/<int:ad_id>/', views.create_proposal, name='create_proposal'),
    path('proposals/<int:proposal_id>/<str:status>/', views.update_proposal_status, name='update_proposal_status'),
] 