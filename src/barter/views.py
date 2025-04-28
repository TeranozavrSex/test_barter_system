from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Ad
from .forms import AdCreateForm, AdUpdateForm

class AdListView(ListView):
    model = Ad
    template_name = 'barter/ad_list.html'
    context_object_name = 'ads'

class AdDetailView(DetailView):
    model = Ad
    template_name = 'barter/ad_detail.html'
    context_object_name = 'ad'

class AdCreateView(CreateView):
    model = Ad
    form_class = AdCreateForm
    template_name = 'barter/ad_form.html'
    success_url = reverse_lazy('ad_list')

class AdUpdateView(UpdateView):
    model = Ad
    form_class = AdUpdateForm
    template_name = 'barter/ad_form.html'
    success_url = reverse_lazy('ad_list')

class AdDeleteView(DeleteView):
    model = Ad
    template_name = 'barter/ad_confirm_delete.html'
    success_url = reverse_lazy('ad_list')
