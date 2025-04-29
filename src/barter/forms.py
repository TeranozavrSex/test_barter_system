from django import forms

from .models import Ad, ExchangeProposal


class AdCreateForm(forms.ModelForm):
    class Meta:
        model = Ad
        fields = ["title", "description", "image", "category", "condition"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "category": forms.Select(attrs={"class": "form-control"}),
            "condition": forms.Select(attrs={"class": "form-control"}),
        }
        labels = {
            "title": "Заголовок",
            "description": "Описание",
            "image": "Изображение",
            "category": "Категория",
            "condition": "Состояние",
        }


class AdUpdateForm(forms.ModelForm):
    class Meta:
        model = Ad
        fields = ["title", "description", "image", "category", "condition", "is_active"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "category": forms.Select(attrs={"class": "form-control"}),
            "condition": forms.Select(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            "title": "Заголовок",
            "description": "Описание",
            "image": "Изображение",
            "category": "Категория",
            "condition": "Состояние",
            "is_active": "Активно",
        }


class ExchangeProposalForm(forms.ModelForm):
    class Meta:
        model = ExchangeProposal
        fields = ["ad_sender", "comment"]
        labels = {
            "ad_sender": "Ваше объявление для обмена",
            "comment": "Комментарий к предложению",
        }
        widgets = {
            "comment": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
            "ad_sender": forms.Select(attrs={"class": "form-select"}),
        }
