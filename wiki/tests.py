from django.test import TestCase

# Create your tests here.
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Page, Revision


class WikiPageTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='pass123')
        self.other_user = User.objects.create_user(username='intruder', password='pass123')
        self.page = Page.objects.create(
            title='Test Page',
            slug='test-page',
            content='Original content',
            owner=self.owner
        )

    def test_anyone_can_list_pages(self):
        url = '/api/pages/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_user_cannot_create_page(self):
        url = '/api/pages/'
        data = {'title': 'New Page', 'slug': 'new-page', 'content': 'Some content'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_user_can_create_page(self):
        self.client.force_authenticate(user=self.owner)
        url = '/api/pages/'
        data = {'title': 'New Page', 'slug': 'new-page', 'content': 'Some content'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['owner'], 'owner')

    def test_owner_can_update_page_and_creates_revision(self):
        self.client.force_authenticate(user=self.owner)
        url = f'/api/pages/{self.page.id}/'
        response = self.client.patch(url, {'content': 'Updated content'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.page.refresh_from_db()
        self.assertEqual(self.page.content, 'Updated content')

        revisions = Revision.objects.filter(page=self.page)
        self.assertEqual(revisions.count(), 1)
        self.assertEqual(revisions.first().content, 'Original content')

    def test_non_owner_cannot_update_page(self):
        self.client.force_authenticate(user=self.other_user)
        url = f'/api/pages/{self.page.id}/'
        response = self.client.patch(url, {'content': 'Hacked content'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_owner_cannot_delete_page(self):
        self.client.force_authenticate(user=self.other_user)
        url = f'/api/pages/{self.page.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_delete_page(self):
        self.client.force_authenticate(user=self.owner)
        url = f'/api/pages/{self.page.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_list_revisions(self):
        self.client.force_authenticate(user=self.owner)
        self.client.patch(f'/api/pages/{self.page.id}/', {'content': 'Second version'})
        url = f'/api/pages/{self.page.id}/revisions/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_owner_can_restore_revision(self):
        self.client.force_authenticate(user=self.owner)
        self.client.patch(f'/api/pages/{self.page.id}/', {'content': 'Second version'})

        revision = Revision.objects.filter(page=self.page).first()
        url = f'/api/pages/{self.page.id}/revisions/{revision.id}/restore/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.page.refresh_from_db()
        self.assertEqual(self.page.content, 'Original content')

    def test_non_owner_cannot_restore_revision(self):
        self.client.force_authenticate(user=self.owner)
        self.client.patch(f'/api/pages/{self.page.id}/', {'content': 'Second version'})
        revision = Revision.objects.filter(page=self.page).first()

        self.client.force_authenticate(user=self.other_user)
        url = f'/api/pages/{self.page.id}/revisions/{revision.id}/restore/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_restoring_revision_creates_new_snapshot(self):
        self.client.force_authenticate(user=self.owner)
        self.client.patch(f'/api/pages/{self.page.id}/', {'content': 'Second version'})
        revision = Revision.objects.filter(page=self.page).first()

        url = f'/api/pages/{self.page.id}/revisions/{revision.id}/restore/'
        self.client.post(url)

        # restoring should snapshot "Second version" before overwriting
        self.assertEqual(Revision.objects.filter(page=self.page).count(), 2)