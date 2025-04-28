from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import Ad, ExchangeProposal
from .forms import AdCreateForm, AdUpdateForm, ExchangeProposalForm

class AdListView(ListView):
    model = Ad
    template_name = 'barter/ad_list.html'
    context_object_name = 'ads'

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_authenticated:
            # Исключаем объявления текущего пользователя
            queryset = queryset.exclude(user=self.request.user)
        return queryset

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

class AdUpdateView(LoginRequiredMixin, UpdateView):
    model = Ad
    form_class = AdUpdateForm
    template_name = 'barter/ad_form.html'
    success_url = reverse_lazy('barter:ad_list')

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

class AdDeleteView(LoginRequiredMixin, DeleteView):
    model = Ad
    template_name = 'barter/ad_confirm_delete.html'
    success_url = reverse_lazy('barter:ad_list')

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

@login_required
def create_proposal(request, ad_id):
    ad_sender = get_object_or_404(Ad, id=ad_id, user=request.user)
    
    if request.method == 'POST':
        form = ExchangeProposalForm(request.POST)
        if form.is_valid():
            proposal = form.save(commit=False)
            proposal.ad_sender = ad_sender
            proposal.status = 'pending'
            proposal.save()
            messages.success(request, 'Предложение обмена отправлено!')
            return redirect('barter:ad_detail', ad_id=ad_id)
    else:
        form = ExchangeProposalForm()
        # Фильтруем объявления, исключая свои и те, на которые уже есть предложения
        form.fields['ad_receiver'].queryset = Ad.objects.exclude(
            user=request.user
        ).exclude(
            exchange_proposals_received__ad_sender=ad_sender
        )
    
    return render(request, 'barter/create_proposal.html', {
        'form': form,
        'ad_sender': ad_sender
    })

@login_required
def my_proposals(request):
    sent_proposals = ExchangeProposal.objects.filter(ad_sender__user=request.user)
    received_proposals = ExchangeProposal.objects.filter(ad_receiver__user=request.user)
    
    return render(request, 'barter/my_proposals.html', {
        'sent_proposals': sent_proposals,
        'received_proposals': received_proposals
    })

@login_required
def update_proposal_status(request, proposal_id, status):
    proposal = get_object_or_404(ExchangeProposal, id=proposal_id)
    
    # Проверяем, что пользователь является владельцем объявления-получателя
    if proposal.ad_receiver.user != request.user:
        messages.error(request, 'У вас нет прав для изменения этого предложения')
        return redirect('barter:my_proposals')
    
    if status in ['accepted', 'rejected']:
        proposal.status = status
        proposal.save()
        messages.success(request, f'Статус предложения изменен на "{status}"')
    else:
        messages.error(request, 'Неверный статус')
    
    return redirect('barter:my_proposals')

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
