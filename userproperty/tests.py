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
        self.other_customer = User.objects.create_user(
            phone_number="09120000003", email="customer2@example.com",
            first_name="Customer", last_name="Two", password="pass12345",
        )
        self.url = reverse("userproperty:save_property", kwargs={"slug": self.property.slug})

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
        url = reverse("userproperty:save_property", kwargs={"slug": "does-not-exist"})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UserUnsavePropertyTests(APITestCase):
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
        self.other_customer = User.objects.create_user(
            phone_number="09120000003", email="customer2@example.com",
            first_name="Customer", last_name="Two", password="pass12345",
        )
        self.saved = SaveProperty.objects.create(user=self.customer, property=self.property)
        self.url = reverse("userproperty:unsave_property", kwargs={"pk": self.saved.pk})

    def test_requires_authentication(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_can_unsave(self):
        self.client.force_authenticate(self.customer)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(SaveProperty.objects.filter(pk=self.saved.pk).exists())

    def test_non_owner_gets_404_not_400(self):
        self.client.force_authenticate(self.other_customer)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(SaveProperty.objects.filter(pk=self.saved.pk).exists())

    def test_non_owner_and_unknown_pk_return_identical_404(self):
        self.client.force_authenticate(self.other_customer)
        owned_response = self.client.delete(self.url)
        unknown_url = reverse("userproperty:unsave_property", kwargs={"pk": 999999})
        unknown_response = self.client.delete(unknown_url)
        self.assertEqual(owned_response.status_code, unknown_response.status_code)
        self.assertEqual(owned_response.data, unknown_response.data)

    def test_unknown_pk_returns_404(self):
        self.client.force_authenticate(self.customer)
        url = reverse("userproperty:unsave_property", kwargs={"pk": 999999})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ListSavedPropertiesTests(APITestCase):
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
        self.property1 = Property.objects.create(
            agency=self.agency, title="Flat One", description="desc",
            listing_type=Property.ListingType.SALE, property_type=Property.PropertyType.APARTMENT,
            price=1000, area=50, province="Tehran", city="Tehran", address="addr",
        )
        self.property2 = Property.objects.create(
            agency=self.agency, title="Flat Two", description="desc",
            listing_type=Property.ListingType.RENT, property_type=Property.PropertyType.HOUSE,
            price=2000, area=80, province="Tehran", city="Tehran", address="addr",
        )

        self.customer = User.objects.create_user(
            phone_number="09120000002", email="customer@example.com",
            first_name="Customer", last_name="One", password="pass12345",
        )
        self.other_customer = User.objects.create_user(
            phone_number="09120000003", email="customer2@example.com",
            first_name="Customer", last_name="Two", password="pass12345",
        )
        self.url = reverse("userproperty:list_saved_properties")

    def test_requires_authentication(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_lists_only_own_saved_properties(self):
        SaveProperty.objects.create(user=self.customer, property=self.property1)
        SaveProperty.objects.create(user=self.other_customer, property=self.property2)

        self.client.force_authenticate(self.customer)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["property"]["id"], self.property1.id)

    def test_empty_when_nothing_saved(self):
        self.client.force_authenticate(self.customer)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(response.data["results"], [])
