from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import Ad, ExchangeProposal
from .forms import AdCreateForm, AdUpdateForm, ExchangeProposalForm
from django.db import models
from settings.aboba_swagger import aboba_swagger
from .serializers import (
    AdSerializer, AdDetailSerializer, AdCreateUpdateSerializer,
    ExchangeProposalSerializer, ExchangeProposalListSerializer, 
    ExchangeProposalCreateSerializer, ExchangeProposalUpdateSerializer
)
from rest_framework.response import Response
from rest_framework import status

# Классы представлений для основных страниц
class AdListView(ListView):
    model = Ad
    template_name = 'barter/ad_list.html'
    context_object_name = 'ads'
    paginate_by = 9

    def get_queryset(self):
        queryset = super().get_queryset().filter(is_active=True)
        
        if self.request.user.is_authenticated:
            queryset = queryset.exclude(user=self.request.user)
        
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                models.Q(title__icontains=search_query) |
                models.Q(description__icontains=search_query)
            )
        
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        condition = self.request.GET.get('condition')
        if condition:
            queryset = queryset.filter(condition=condition)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Ad.Category.choices
        context['conditions'] = Ad.Condition.choices
        return context

class AdDetailView(DetailView):
    model = Ad
    template_name = 'barter/ad_detail.html'
    context_object_name = 'ad'

class AdCreateView(LoginRequiredMixin, CreateView):
    model = Ad
    form_class = AdCreateForm
    template_name = 'barter/ad_form.html'
    success_url = reverse_lazy('barter:ad_list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создание объявления'
        return context
        
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

class AdUpdateView(LoginRequiredMixin, UpdateView):
    model = Ad
    form_class = AdUpdateForm
    template_name = 'barter/ad_form.html'
    success_url = reverse_lazy('barter:ad_list')
    
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
        
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

class AdDeleteView(LoginRequiredMixin, DeleteView):
    model = Ad
    template_name = 'barter/ad_confirm_delete.html'
    success_url = reverse_lazy('barter:ad_list')
    
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

class MyAdsListView(LoginRequiredMixin, ListView):
    model = Ad
    template_name = 'barter/my_ads.html'
    context_object_name = 'ads'
    
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

class MyProposalsListView(LoginRequiredMixin, ListView):
    model = ExchangeProposal
    template_name = 'barter/my_proposals.html'
    context_object_name = 'proposals'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sent_proposals'] = ExchangeProposal.objects.filter(ad_sender__user=self.request.user)
        context['received_proposals'] = ExchangeProposal.objects.filter(ad_receiver__user=self.request.user)
        return context

# Функции представлений
@aboba_swagger(
    http_methods=["GET", "POST"],
    summary="Create exchange proposal",
    description="Form for creating a new exchange proposal for a specific advertisement",
    query_params={
        "ad_id": int
    },
    body_params={
        "ad_sender": int,
        "comment": str
    },
    responses={
        "200": {"Success": "Form displayed/processed"},
        "302": "Redirect after proposal creation",
        "400": "Invalid form data",
        "403": "Cannot propose exchange on own advertisement",
        "404": "Advertisement not found"
    },
    tags=["exchange_proposals"],
    need_auth=True,
)
def create_proposal(request, ad_id):
    ad_receiver = get_object_or_404(Ad, id=ad_id, is_active=True)
    
    if ad_receiver.user == request.user:
        messages.error(request, 'Вы не можете предложить обмен на свое объявление')
        return redirect('barter:ad_detail', pk=ad_id)
    
    if request.method == 'POST':
        form = ExchangeProposalForm(request.POST)
        if form.is_valid():
            proposal = form.save(commit=False)
            proposal.ad_receiver = ad_receiver
            proposal.status = 'pending'
            proposal.save()
            messages.success(request, 'Предложение обмена отправлено!')
            return redirect('barter:ad_detail', pk=ad_id)
    else:
        form = ExchangeProposalForm()
        form.fields['ad_sender'].queryset = Ad.objects.filter(
            user=request.user,
            is_active=True
        ).exclude(
            sent_proposals__ad_receiver=ad_receiver
        )
    
    return render(request, 'barter/create_proposal.html', {
        'form': form,
        'ad_receiver': ad_receiver
    })

@aboba_swagger(
    http_methods=["GET"],
    summary="Update exchange proposal status",
    description="Update the status of a specific exchange proposal",
    query_params={
        "proposal_id": int,
        "status": str
    },
    responses={
        "302": "Redirect after status update",
        "403": "Not authorized to update this proposal",
        "404": "Proposal not found"
    },
    tags=["exchange_proposals"],
    need_auth=True,
    is_drf=False
)
def update_proposal_status(request, proposal_id, status):
    proposal = get_object_or_404(ExchangeProposal, id=proposal_id)
    
    if proposal.ad_receiver.user != request.user:
        messages.error(request, 'У вас нет прав для изменения этого предложения')
        return redirect('barter:my_proposals')
    
    if proposal.status != 'pending':
        messages.error(request, 'Статус этого предложения уже изменен')
        return redirect('barter:my_proposals')
    
    if status == 'accepted':
        proposal.status = 'accepted'
        proposal.save()
        
        proposal.ad_sender.is_active = False
        proposal.ad_receiver.is_active = False
        proposal.ad_sender.save()
        proposal.ad_receiver.save()
        
        ExchangeProposal.objects.filter(
            ad_sender=proposal.ad_sender,
            status='pending'
        ).exclude(id=proposal.id).update(status='cancelled')
        
        ExchangeProposal.objects.filter(
            ad_receiver=proposal.ad_sender,
            status='pending'
        ).exclude(id=proposal.id).update(status='cancelled')
        
        ExchangeProposal.objects.filter(
            ad_sender=proposal.ad_receiver,
            status='pending'
        ).exclude(id=proposal.id).update(status='cancelled')
        
        ExchangeProposal.objects.filter(
            ad_receiver=proposal.ad_receiver,
            status='pending'
        ).exclude(id=proposal.id).update(status='cancelled')
        
        messages.success(request, 'Предложение принято! Оба объявления деактивированы.')
    
    elif status == 'rejected':
        proposal.status = 'rejected'
        proposal.save()
        
        messages.success(request, 'Предложение отклонено.')
    
    else:
        messages.error(request, 'Неверный статус. Разрешены только: accepted, rejected')
    
    return redirect('barter:my_proposals')

@aboba_swagger(
    http_methods=["GET"],
    summary="Список объявлений API",
    description="API для получения списка всех активных объявлений",
    query_params={
        "category": str,
        "condition": str,
        "search": str,
    },
    responses={
        "200": [
            {
                "id": 1,
                "title": "Мобильный телефон",
                "description": "Хороший телефон в отличном состоянии",
                "category": "electronics",
                "category_display": "Электроника",
                "condition": "used",
                "condition_display": "Б/у",
                "is_active": True,
                "created_at": "2024-03-20T12:00:00Z",
                "user": 1,
                "user_username": "username",
                "image_url": "/media/ads_images/phone.jpg"
            }
        ]
    },
    tags=["api"],
    is_drf=False
)
def ad_list_api(request):
    ads = Ad.objects.filter(is_active=True)
    if request.user.is_authenticated:
        ads = ads.exclude(user=request.user)
    
    search_query = request.GET.get('search')
    if search_query:
        ads = ads.filter(
            models.Q(title__icontains=search_query) |
            models.Q(description__icontains=search_query)
        )
    
    category = request.GET.get('category')
    if category:
        ads = ads.filter(category=category)
    
    condition = request.GET.get('condition')
    if condition:
        ads = ads.filter(condition=condition)
    
    serializer = AdSerializer(ads, many=True, context={'request': request})
    return Response(serializer.data)

@aboba_swagger(
    http_methods=["GET"],
    summary="Детали объявления API",
    description="API для получения детальной информации об объявлении",
    query_params={
        "pk": int
    },
    responses={
        "200": {
            "id": 1,
            "title": "Мобильный телефон",
            "description": "Хороший телефон в отличном состоянии",
            "category": "electronics",
            "category_display": "Электроника",
            "condition": "used",
            "condition_display": "Б/у",
            "is_active": True,
            "created_at": "2024-03-20T12:00:00Z",
            "user": {
                "id": 1,
                "username": "username",
                "email": "user@example.com",
                "phone": "+7 123 456-78-90"
            },
            "image_url": "/media/ads_images/phone.jpg"
        },
        "404": {
            "detail": "Объявление не найдено"
        }
    },
    tags=["api"],
    is_drf=False
)
def ad_detail_api(request, pk):
    try:
        ad = Ad.objects.get(pk=pk)
        serializer = AdDetailSerializer(ad, context={'request': request})
        return Response(serializer.data)
    except Ad.DoesNotExist:
        return Response({'detail': 'Объявление не найдено'}, status=status.HTTP_404_NOT_FOUND)

@aboba_swagger(
    http_methods=["POST"],
    summary="Создание объявления API",
    description="API для создания нового объявления",
    body_params={
        "title": str,
        "description": str,
        "category": str,
        "condition": str,
        "image": "bytes"
    },
    responses={
        "201": {
            "id": 1,
            "title": "Мобильный телефон",
            "description": "Хороший телефон в отличном состоянии",
            "category": "electronics",
            "category_display": "Электроника",
            "condition": "used",
            "condition_display": "Б/у",
            "is_active": True,
            "created_at": "2024-03-20T12:00:00Z",
            "user": 1,
            "user_username": "username",
            "image_url": "/media/ads_images/phone.jpg"
        },
        "400": {
            "errors": {
                "title": ["Это поле обязательно."],
                "description": ["Это поле обязательно."]
            }
        },
        "401": {
            "detail": "Учетные данные не были предоставлены."
        }
    },
    need_auth=True,
    tags=["api"],
)
def ad_create_api(request):
    serializer = AdCreateUpdateSerializer(data=request.data)
    if serializer.is_valid():
        ad = serializer.save(user=request.user)
        response_serializer = AdSerializer(ad, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@aboba_swagger(
    http_methods=["PUT", "PATCH"],
    summary="Обновление объявления API",
    description="API для обновления существующего объявления",
    query_params={
        "pk": int
    },
    body_params={
        "title": str,
        "description": str,
        "category": str,
        "condition": str,
        "is_active": bool,
        "image": "bytes"
    },
    responses={
        "200": {
            "id": 1,
            "title": "Обновленный телефон",
            "description": "Обновленное описание",
            "category": "electronics",
            "category_display": "Электроника",
            "condition": "used",
            "condition_display": "Б/у",
            "is_active": True,
            "created_at": "2024-03-20T12:00:00Z",
            "user": 1,
            "user_username": "username",
            "image_url": "/media/ads_images/phone.jpg"
        },
        "400": {
            "errors": {
                "title": ["Минимум 5 символов."],
                "description": ["Минимум 20 символов."]
            }
        },
        "401": {
            "detail": "Учетные данные не были предоставлены."
        },
        "403": {
            "detail": "У вас нет прав редактировать это объявление."
        },
        "404": {
            "detail": "Объявление не найдено."
        }
    },
    need_auth=True,
    tags=["api"],
)
def ad_update_api(request, pk):
    try:
        ad = Ad.objects.get(pk=pk)
        
        # Проверка прав доступа
        if ad.user != request.user:
            return Response({'detail': 'У вас нет прав редактировать это объявление.'}, 
                           status=status.HTTP_403_FORBIDDEN)
        
        # Частичное или полное обновление
        partial = request.method == 'PATCH'
        serializer = AdCreateUpdateSerializer(ad, data=request.data, partial=partial)
        
        if serializer.is_valid():
            ad = serializer.save()
            response_serializer = AdSerializer(ad, context={'request': request})
            return Response(response_serializer.data)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    except Ad.DoesNotExist:
        return Response({'detail': 'Объявление не найдено.'}, 
                       status=status.HTTP_404_NOT_FOUND)

@aboba_swagger(
    http_methods=["DELETE"],
    summary="Удаление объявления API",
    description="API для удаления объявления",
    query_params={
        "pk": int
    },
    responses={
        "204": {
            "detail": "Объявление удалено."
        },
        "401": {
            "detail": "Учетные данные не были предоставлены."
        },
        "403": {
            "detail": "У вас нет прав удалить это объявление."
        },
        "404": {
            "detail": "Объявление не найдено."
        }
    },
    need_auth=True,
    tags=["api"],
)
def ad_delete_api(request, pk):
    try:
        ad = Ad.objects.get(pk=pk)
        
        # Проверка прав доступа
        if ad.user != request.user:
            return Response({'detail': 'У вас нет прав удалить это объявление.'}, 
                           status=status.HTTP_403_FORBIDDEN)
        
        ad.delete()
        return Response({'detail': 'Объявление удалено.'}, status=status.HTTP_204_NO_CONTENT)
    
    except Ad.DoesNotExist:
        return Response({'detail': 'Объявление не найдено.'}, 
                       status=status.HTTP_404_NOT_FOUND)

@aboba_swagger(
    http_methods=["GET"],
    summary="Мои объявления API",
    description="API для получения списка объявлений текущего пользователя",
    responses={
        "200": [
            {
                "id": 1,
                "title": "Мобильный телефон",
                "description": "Хороший телефон в отличном состоянии",
                "category": "electronics",
                "category_display": "Электроника",
                "condition": "used",
                "condition_display": "Б/у",
                "is_active": True,
                "created_at": "2024-03-20T12:00:00Z",
                "user": 1,
                "user_username": "username",
                "image_url": "/media/ads_images/phone.jpg"
            }
        ],
        "401": {
            "detail": "Учетные данные не были предоставлены."
        }
    },
    need_auth=True,
    tags=["api"],
)
def my_ads_api(request):
    ads = Ad.objects.filter(user=request.user)
    serializer = AdSerializer(ads, many=True, context={'request': request})
    return Response(serializer.data)

@aboba_swagger(
    http_methods=["GET"],
    summary="Список предложений обмена API",
    description="API для получения списка всех предложений обмена текущего пользователя",
    responses={
        "200": {
            "sent_proposals": [
                {
                    "id": 1,
                    "ad_sender_title": "Мой товар",
                    "ad_receiver_title": "Чужой товар",
                    "comment": "Предлагаю обмен",
                    "status": "pending",
                    "status_display": "Ожидает",
                    "created_at": "2024-03-20T12:00:00Z"
                }
            ],
            "received_proposals": [
                {
                    "id": 2,
                    "ad_sender_title": "Товар другого пользователя",
                    "ad_receiver_title": "Мой товар",
                    "comment": "Хочу обменяться",
                    "status": "pending",
                    "status_display": "Ожидает",
                    "created_at": "2024-03-20T12:00:00Z"
                }
            ]
        },
        "401": {
            "detail": "Учетные данные не были предоставлены."
        }
    },
    need_auth=True,
    tags=["api"],
)
def proposal_list_api(request):
    sent_proposals = ExchangeProposal.objects.filter(ad_sender__user=request.user)
    received_proposals = ExchangeProposal.objects.filter(ad_receiver__user=request.user)
    
    sent_serializer = ExchangeProposalListSerializer(sent_proposals, many=True)
    received_serializer = ExchangeProposalListSerializer(received_proposals, many=True)
    
    return Response({
        'sent_proposals': sent_serializer.data,
        'received_proposals': received_serializer.data
    })

@aboba_swagger(
    http_methods=["GET"],
    summary="Детали предложения обмена API",
    description="API для получения деталей конкретного предложения обмена",
    query_params={
        "pk": int
    },
    responses={
        "200": {
            "id": 1,
            "ad_sender": {
                "id": 1,
                "title": "Мой товар",
                "description": "Описание",
                "category_display": "Электроника",
                "condition_display": "Б/у",
                "user_username": "username"
            },
            "ad_receiver": {
                "id": 2,
                "title": "Чужой товар",
                "description": "Описание",
                "category_display": "Книги",
                "condition_display": "Новый",
                "user_username": "another_user"
            },
            "comment": "Предлагаю обмен",
            "status": "pending",
            "status_display": "Ожидает",
            "created_at": "2024-03-20T12:00:00Z"
        },
        "401": {
            "detail": "Учетные данные не были предоставлены."
        },
        "403": {
            "detail": "У вас нет доступа к этому предложению обмена."
        },
        "404": {
            "detail": "Предложение обмена не найдено."
        }
    },
    need_auth=True,
    tags=["api"],
)
def proposal_detail_api(request, pk):
    try:
        proposal = ExchangeProposal.objects.get(pk=pk)
        
        # Проверка прав доступа
        if proposal.ad_sender.user != request.user and proposal.ad_receiver.user != request.user:
            return Response({'detail': 'У вас нет доступа к этому предложению обмена.'},
                           status=status.HTTP_403_FORBIDDEN)
        
        serializer = ExchangeProposalSerializer(proposal)
        return Response(serializer.data)
    
    except ExchangeProposal.DoesNotExist:
        return Response({'detail': 'Предложение обмена не найдено.'},
                       status=status.HTTP_404_NOT_FOUND)

@aboba_swagger(
    http_methods=["POST"],
    summary="Создание предложения обмена API",
    description="API для создания нового предложения обмена",
    query_params={
        "ad_id": int
    },
    body_params={
        "ad_sender": int,
        "comment": str
    },
    responses={
        "201": {
            "id": 1,
            "ad_sender": {
                "id": 1,
                "title": "Мой товар",
                "description": "Описание",
                "category_display": "Электроника",
                "condition_display": "Б/у",
                "user_username": "username"
            },
            "ad_receiver": {
                "id": 2,
                "title": "Чужой товар",
                "description": "Описание",
                "category_display": "Книги",
                "condition_display": "Новый",
                "user_username": "another_user"
            },
            "comment": "Предлагаю обмен",
            "status": "pending",
            "status_display": "Ожидает",
            "created_at": "2024-03-20T12:00:00Z"
        },
        "400": {
            "errors": {
                "ad_sender": ["Вы можете предлагать только свои объявления"],
                "non_field_errors": ["Нельзя предлагать обмен на свое же объявление"]
            }
        },
        "401": {
            "detail": "Учетные данные не были предоставлены."
        },
        "404": {
            "detail": "Объявление не найдено."
        }
    },
    need_auth=True,
    tags=["api"],
)
def proposal_create_api(request, ad_id):
    try:
        ad_receiver = Ad.objects.get(pk=ad_id, is_active=True)
        
        # Проверка, не пытается ли пользователь предложить обмен на свое объявление
        if ad_receiver.user == request.user:
            return Response(
                {'detail': 'Нельзя предлагать обмен на свое объявление'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ExchangeProposalCreateSerializer(
            data=request.data, 
            context={
                'request': request,
                'ad_receiver': ad_receiver
            }
        )
        
        if serializer.is_valid():
            proposal = serializer.save(ad_receiver=ad_receiver, status='pending')
            response_serializer = ExchangeProposalSerializer(proposal)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    except Ad.DoesNotExist:
        return Response({'detail': 'Объявление не найдено.'}, status=status.HTTP_404_NOT_FOUND)

@aboba_swagger(
    http_methods=["PUT", "PATCH"],
    summary="Обновление предложения обмена API",
    description="API для обновления статуса предложения обмена (принятие или отклонение)",
    query_params={
        "pk": int
    },
    body_params={
        "status": str
    },
    responses={
        "200": {
            "id": 1,
            "ad_sender": {
                "id": 1,
                "title": "Мой товар",
                "description": "Описание",
                "category_display": "Электроника",
                "condition_display": "Б/у",
                "user_username": "username"
            },
            "ad_receiver": {
                "id": 2,
                "title": "Чужой товар",
                "description": "Описание",
                "category_display": "Книги",
                "condition_display": "Новый",
                "user_username": "another_user"
            },
            "comment": "Предлагаю обмен",
            "status": "accepted",
            "status_display": "Принято",
            "created_at": "2024-03-20T12:00:00Z"
        },
        "400": {
            "errors": {
                "status": ["Статус может быть только 'accepted' или 'rejected'"],
                "non_field_errors": ["Статус этого предложения уже изменен"]
            }
        },
        "401": {
            "detail": "Учетные данные не были предоставлены."
        },
        "403": {
            "detail": "У вас нет прав для изменения этого предложения."
        },
        "404": {
            "detail": "Предложение обмена не найдено."
        }
    },
    need_auth=True,
    tags=["api"],
)
def proposal_update_api(request, pk):
    try:
        proposal = ExchangeProposal.objects.get(pk=pk)
        
        # Проверка прав доступа
        if proposal.ad_receiver.user != request.user:
            return Response(
                {'detail': 'У вас нет прав для изменения этого предложения.'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Проверка, что предложение в статусе ожидания
        if proposal.status != 'pending':
            return Response(
                {'detail': 'Статус этого предложения уже изменен'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ExchangeProposalUpdateSerializer(proposal, data=request.data, partial=True)
        
        if serializer.is_valid():
            updated_proposal = serializer.save()
            
            # Если статус изменен на "accepted" (принято)
            if updated_proposal.status == 'accepted':
                # Деактивируем объявления
                updated_proposal.ad_sender.is_active = False
                updated_proposal.ad_receiver.is_active = False
                updated_proposal.ad_sender.save()
                updated_proposal.ad_receiver.save()
                
                # Отменяем другие предложения для этих объявлений
                ExchangeProposal.objects.filter(
                    models.Q(ad_sender=updated_proposal.ad_sender) | 
                    models.Q(ad_receiver=updated_proposal.ad_sender) |
                    models.Q(ad_sender=updated_proposal.ad_receiver) |
                    models.Q(ad_receiver=updated_proposal.ad_receiver),
                    status='pending'
                ).exclude(id=updated_proposal.id).update(status='cancelled')
            
            response_serializer = ExchangeProposalSerializer(updated_proposal)
            return Response(response_serializer.data)
        
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    except ExchangeProposal.DoesNotExist:
        return Response({'detail': 'Предложение обмена не найдено.'},
                       status=status.HTTP_404_NOT_FOUND)
