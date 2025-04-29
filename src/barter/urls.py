from django.urls import path
from . import views

app_name = 'barter'

urlpatterns = [
    # Web UI endpoints
    path('', views.AdListView.as_view(), name='ad_list'),
    path('my-ads/', views.MyAdsListView.as_view(), name='my_ads'),
    path('ad/<int:pk>/', views.AdDetailView.as_view(), name='ad_detail'),
    path('ad/create/', views.AdCreateView.as_view(), name='ad_create'),
    path('ad/<int:pk>/update/', views.AdUpdateView.as_view(), name='ad_update'),
    path('ad/<int:pk>/delete/', views.AdDeleteView.as_view(), name='ad_delete'),
    path('proposals/my/', views.MyProposalsListView.as_view(), name='my_proposals'),
    path('proposals/create/<int:ad_id>/', views.create_proposal, name='create_proposal'),
    path('proposals/<int:proposal_id>/<str:status>/', views.update_proposal_status, name='update_proposal_status'),
    
    # API endpoints - Advertisements
    path('api/ads/', views.ad_list_api, name='api_ad_list'),
    path('api/ads/<int:pk>/', views.ad_detail_api, name='api_ad_detail'),
    path('api/ads/create/', views.ad_create_api, name='api_ad_create'),
    path('api/ads/<int:pk>/update/', views.ad_update_api, name='api_ad_update'),
    path('api/ads/<int:pk>/delete/', views.ad_delete_api, name='api_ad_delete'),
    path('api/ads/my/', views.my_ads_api, name='api_my_ads'),
    
    # API endpoints - Exchange Proposals
    path('api/proposals/', views.proposal_list_api, name='api_proposal_list'),
    path('api/proposals/<int:pk>/', views.proposal_detail_api, name='api_proposal_detail'),
    path('api/proposals/create/<int:ad_id>/', views.proposal_create_api, name='api_proposal_create'),
    path('api/proposals/<int:pk>/update/', views.proposal_update_api, name='api_proposal_update'),
] 