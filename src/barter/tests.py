from django.test import TestCase, Client
from django.utils import timezone
from user.models import CustomUser
from .models import Ad, ExchangeProposal
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class AdModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.ad = Ad.objects.create(
            user=self.user,
            title='Test Ad',
            description='Test Description',
            category=Ad.Category.ELECTRONICS,
            condition=Ad.Condition.NEW
        )

    def test_ad_creation(self):
        self.assertEqual(self.ad.title, 'Test Ad')
        self.assertEqual(self.ad.description, 'Test Description')
        self.assertEqual(self.ad.category, Ad.Category.ELECTRONICS)
        self.assertEqual(self.ad.condition, Ad.Condition.NEW)
        self.assertTrue(self.ad.is_active)
        self.assertIsNotNone(self.ad.created_at)

    def test_ad_str_representation(self):
        self.assertEqual(str(self.ad), 'Test Ad (Электроника)')


class ExchangeProposalModelTest(TestCase):
    def setUp(self):
        self.user1 = CustomUser.objects.create_user(
            username='user1',
            password='testpass123'
        )
        self.user2 = CustomUser.objects.create_user(
            username='user2',
            password='testpass123'
        )
        
        self.ad1 = Ad.objects.create(
            user=self.user1,
            title='Ad 1',
            description='Description 1',
            category=Ad.Category.ELECTRONICS
        )
        self.ad2 = Ad.objects.create(
            user=self.user2,
            title='Ad 2',
            description='Description 2',
            category=Ad.Category.CLOTHING
        )
        
        self.proposal = ExchangeProposal.objects.create(
            ad_sender=self.ad1,
            ad_receiver=self.ad2,
            comment='Test comment'
        )

    def test_proposal_creation(self):
        self.assertEqual(self.proposal.ad_sender, self.ad1)
        self.assertEqual(self.proposal.ad_receiver, self.ad2)
        self.assertEqual(self.proposal.comment, 'Test comment')
        self.assertEqual(self.proposal.status, ExchangeProposal.Status.PENDING)
        self.assertIsNotNone(self.proposal.created_at)

    def test_proposal_str_representation(self):
        self.assertTrue(str(self.proposal).startswith('Предложение обмена #'))
        self.assertTrue('(Ожидает)' in str(self.proposal))

    def test_unique_constraint(self):
        with self.assertRaises(Exception):
            ExchangeProposal.objects.create(
                ad_sender=self.ad1,
                ad_receiver=self.ad2,
                comment='Duplicate proposal'
            )


class AdViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.ad = Ad.objects.create(
            user=self.user,
            title='Test Ad',
            description='Test Description',
            category=Ad.Category.ELECTRONICS,
            condition=Ad.Condition.NEW
        )

    def test_ad_list_view(self):
        response = self.client.get(reverse('barter:ad_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'barter/ad_list.html')
        self.assertContains(response, 'Test Ad')

    def test_ad_detail_view(self):
        response = self.client.get(reverse('barter:ad_detail', args=[self.ad.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'barter/ad_detail.html')
        self.assertContains(response, 'Test Ad')

    def test_ad_create_view_unauthorized(self):
        response = self.client.get(reverse('barter:ad_create'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_ad_create_view_authorized(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('barter:ad_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'barter/ad_form.html')

    def test_ad_create_post(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('barter:ad_create'), {
            'title': 'New Ad',
            'description': 'New Description',
            'category': Ad.Category.CLOTHING,
            'condition': Ad.Condition.USED
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(Ad.objects.filter(title='New Ad').exists())

    def test_ad_update_view_unauthorized(self):
        response = self.client.get(reverse('barter:ad_update', args=[self.ad.pk]))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_ad_update_view_authorized(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('barter:ad_update', args=[self.ad.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'barter/ad_form.html')

    def test_ad_update_post(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('barter:ad_update', args=[self.ad.pk]), {
            'title': 'Updated Ad',
            'description': 'Updated Description',
            'category': Ad.Category.BOOKS,
            'condition': Ad.Condition.USED,
            'is_active': True
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.ad.refresh_from_db()
        self.assertEqual(self.ad.title, 'Updated Ad')

    def test_ad_delete_view_unauthorized(self):
        response = self.client.get(reverse('barter:ad_delete', args=[self.ad.pk]))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_ad_delete_view_authorized(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('barter:ad_delete', args=[self.ad.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'barter/ad_confirm_delete.html')

    def test_ad_delete_post(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('barter:ad_delete', args=[self.ad.pk]))
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertFalse(Ad.objects.filter(pk=self.ad.pk).exists())
