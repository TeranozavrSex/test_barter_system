from django.contrib import admin
from .models import Ad, ExchangeProposal


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'condition', 'created_at', 'is_active')
    list_filter = ('category', 'condition', 'is_active', 'created_at')
    search_fields = ('title', 'description', 'user__username')
    date_hierarchy = 'created_at'


@admin.register(ExchangeProposal)
class ExchangeProposalAdmin(admin.ModelAdmin):
    list_display = ('id', 'ad_sender', 'ad_receiver', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('ad_sender__title', 'ad_receiver__title', 'comment')
    date_hierarchy = 'created_at'
