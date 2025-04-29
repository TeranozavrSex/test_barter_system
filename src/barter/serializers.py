from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Ad, ExchangeProposal

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя в API"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class AdSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для объявлений"""
    category_display = serializers.SerializerMethodField()
    condition_display = serializers.SerializerMethodField()
    user_username = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Ad
        fields = ['id', 'title', 'description', 'category', 'category_display', 
                 'condition', 'condition_display', 'user', 'user_username', 
                 'is_active', 'created_at', 'image_url']
        read_only_fields = ['user', 'created_at']
    
    def get_category_display(self, obj):
        return obj.get_category_display()
    
    def get_condition_display(self, obj):
        return obj.get_condition_display()
    
    def get_user_username(self, obj):
        return obj.user.username
    
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class AdDetailSerializer(AdSerializer):
    """Расширенный сериализатор для детального просмотра объявления"""
    user = UserSerializer(read_only=True)
    
    class Meta(AdSerializer.Meta):
        fields = AdSerializer.Meta.fields


class AdCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления объявлений"""
    class Meta:
        model = Ad
        fields = ['title', 'description', 'category', 'condition', 'is_active', 'image']
        
    def validate_title(self, value):
        if len(value) < 5:
            raise serializers.ValidationError("Заголовок должен содержать не менее 5 символов")
        return value
    
    def validate_description(self, value):
        if len(value) < 20:
            raise serializers.ValidationError("Описание должно содержать не менее 20 символов")
        return value


class SimpleAdSerializer(serializers.ModelSerializer):
    """Упрощенный сериализатор для отображения объявления в предложениях обмена"""
    category_display = serializers.SerializerMethodField()
    condition_display = serializers.SerializerMethodField()
    user_username = serializers.SerializerMethodField()
    
    class Meta:
        model = Ad
        fields = ['id', 'title', 'description', 'category_display', 'condition_display', 'user_username']
    
    def get_category_display(self, obj):
        return obj.get_category_display()
    
    def get_condition_display(self, obj):
        return obj.get_condition_display()
    
    def get_user_username(self, obj):
        return obj.user.username


class ExchangeProposalSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для предложений обмена"""
    ad_sender = SimpleAdSerializer(read_only=True)
    ad_receiver = SimpleAdSerializer(read_only=True)
    status_display = serializers.SerializerMethodField()
    
    class Meta:
        model = ExchangeProposal
        fields = ['id', 'ad_sender', 'ad_receiver', 'comment', 'status', 'status_display', 'created_at']
        read_only_fields = ['status', 'created_at']
    
    def get_status_display(self, obj):
        return obj.get_status_display()


class ExchangeProposalListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка предложений обмена"""
    ad_sender_title = serializers.SerializerMethodField()
    ad_receiver_title = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    
    class Meta:
        model = ExchangeProposal
        fields = ['id', 'ad_sender_title', 'ad_receiver_title', 'comment', 'status', 'status_display', 'created_at']
    
    def get_ad_sender_title(self, obj):
        return obj.ad_sender.title
    
    def get_ad_receiver_title(self, obj):
        return obj.ad_receiver.title
    
    def get_status_display(self, obj):
        return obj.get_status_display()


class ExchangeProposalCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания предложений обмена"""
    class Meta:
        model = ExchangeProposal
        fields = ['ad_sender', 'comment']
    
    def validate_ad_sender(self, value):
        user = self.context['request'].user
        if value.user != user:
            raise serializers.ValidationError("Вы можете предлагать только свои объявления")
        if not value.is_active:
            raise serializers.ValidationError("Нельзя предлагать неактивные объявления")
        return value
    
    def validate(self, data):
        ad_receiver = self.context.get('ad_receiver')
        
        if 'ad_sender' in data and ad_receiver:
            if data['ad_sender'].user == ad_receiver.user:
                raise serializers.ValidationError({"ad_sender": "Нельзя предлагать обмен на свое же объявление"})
            
            # Проверка уникальности
            existing = ExchangeProposal.objects.filter(
                ad_sender=data['ad_sender'],
                ad_receiver=ad_receiver,
                status='pending'
            ).exists()
            
            if existing:
                raise serializers.ValidationError({"ad_sender": "Предложение обмена между этими объявлениями уже существует"})
        
        return data


class ExchangeProposalUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления статуса предложения обмена"""
    class Meta:
        model = ExchangeProposal
        fields = ['status']
        
    def validate_status(self, value):
        if value not in ['accepted', 'rejected']:
            raise serializers.ValidationError("Статус может быть только 'accepted' или 'rejected'")
        return value 