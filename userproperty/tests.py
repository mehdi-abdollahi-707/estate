from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from agencies.models import Agency
from property.models import Property
from .models import SaveProperty


class UserSavePropertyTests(APITestCase):
    def setUp(self):
        self.agent = User.objects.create_user(
            phone_number="09120000001", email="agent@example.com",
            first_name="Agent", last_name="One", password="pass12345",
        )
        self.agency = Agency.objects.create(
            agent=self.agent, name="Test Agency", license_number="LIC-001",
            business_phone="09120000001", description="desc",
            province="Tehran", city="Tehran", exact_address="addr",
        )
        self.property = Property.objects.create(
            agency=self.agency, title="Nice Flat", description="desc",
            listing_type=Property.ListingType.SALE, property_type=Property.PropertyType.APARTMENT,
            price=1000, area=50, province="Tehran", city="Tehran", address="addr",
        )

        self.customer = User.objects.create_user(
            phone_number="09120000002", email="customer@example.com",
            first_name="Customer", last_name="One", password="pass12345",
        )
        self.url = reverse("userproperty:add_property", kwargs={"slug": self.property.slug})

    def test_requires_authentication(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_customer_can_save_property(self):
        self.client.force_authenticate(self.customer)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(SaveProperty.objects.filter(user=self.customer, property=self.property).exists())

    def test_saving_twice_does_not_duplicate(self):
        self.client.force_authenticate(self.customer)
        self.client.post(self.url)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(SaveProperty.objects.filter(user=self.customer, property=self.property).count(), 1)

    def test_agent_cannot_save_own_property(self):
        self.client.force_authenticate(self.agent)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(SaveProperty.objects.filter(user=self.agent, property=self.property).exists())

    def test_unknown_slug_returns_404(self):
        self.client.force_authenticate(self.customer)
        url = reverse("userproperty:add_property", kwargs={"slug": "does-not-exist"})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
