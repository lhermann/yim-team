from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from helpers import factories, models

class HomeTests(TestCase):
    def test_home(self):
        r = self.client.get(reverse('home'))
        self.assertEqual(r.status_code, 302)
        user = factories.UserFactory()
        self.client.force_login(user)
        r = self.client.get(reverse('home'))
        self.assertContains(r, 'Mitarbeiter')

class AdminTests(TestCase):
    def test_helper_list_view(self):
        user = factories.UserFactory(is_superuser=True, is_staff=True)
        self.client.force_login(user)
        helper = factories.HelperFactory()
        r = self.client.get(reverse('admin:helpers_helper_changelist'))
        self.assertContains(r, helper.email)
        self.assertContains(r, helper.area)
        self.assertContains(r, helper.label)

class AuthTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = factories.UserFactory()

    def test_login_form(self):
        url = '{}?next=/'.format(reverse('rest_framework:login'))
        r = self.client.get(url)
        self.assertContains(r, 'password')
        self.assertContains(r, 'YiM Team')
        r = self.client.post(
            url,
            {'username': self.user.username, 'password': 'pw'},
            follow=True,
        )
        self.assertContains(r, 'Mitarbeiter')

    def test_logout_form(self):
        self.client.login(username=self.user.username, password='pw')
        r = self.client.get(reverse('rest_framework:logout'))
        # View shows a login form
        self.assertContains(r, 'password')
        # Custom style sheets
        self.assertContains(r, 'open-iconic-bootstrap.min.css')
        self.assertNotContains(r, 'Django REST framework')

class HelperAPITests(APITestCase):
    dict_new = {
        'id': 1,
        'email': 'new@example.com',
        'label': 'Registration',
        'area': 'Coworker',
        'food_privilege': True,
        'free_admission': True,
        'above_35': True,
        'first_name': '',
        'last_name': '',
        'age': None,
    }
    dict_registered = {
        'id': 2,
        'email': 'registered@example.com',
        'label': 'boots',
        'area': 'Volunteer',
        'food_privilege': True,
        'free_admission': False,
        'above_35': True,
        'first_name': 'Timmy',
        'last_name': 'Jonson',
        'age': 34,
    }

    @classmethod
    def setUpTestData(cls):
        cls.user = factories.UserFactory()
        cls.helper_new = models.Helper(user=cls.user, **cls.dict_new)
        cls.helper_registered = models.Helper(
            user=cls.user,
            **cls.dict_registered
        )
        models.Helper.objects.bulk_create([
            cls.helper_new,
            cls.helper_registered,
        ])

    def test_authentication_required(self):
        r = self.client.get(reverse('helper-list'))
        self.assertEqual(r.json(), [])
        r = self.client.get(reverse('query-detail', args=('new@example.com',)))
        self.assertEqual(r.status_code, 403)

    def test_permission_white_list_and_api_key(self):
        r = self.client.get(
            reverse('query-detail', args=('new@example.com',)),
            REMOTE_ADDR='127.0.0.1',
            HTTP_API_KEY='test1234567890',
        )
        self.assertEqual(r.status_code, 200)

        # Wrong IP address
        r = self.client.get(
            reverse('query-detail', args=('new@example.com',)),
            HTTP_API_KEY='test1234567890',
            REMOTE_ADDR='127.0.0.2',
        )
        self.assertEqual(r.status_code, 403)

        # Super user
        super_user = factories.UserFactory(is_staff=True, is_superuser=True)
        self.client.force_login(super_user)
        r = self.client.get(
            reverse('query-detail', args=('new@example.com',)),
            REMOTE_ADDR='127.0.0.2',
        )
        self.assertEqual(r.status_code, 200)


    def test_owned_list_get(self):
        self.client.force_login(self.user)
        r = self.client.get(reverse('helper-list'))
        url = 'http://testserver/helpers/{}/'
        dict_new = {'url': url.format(1)}
        dict_registered = {'url': url.format(2)}
        dict_new.update(self.dict_new)
        dict_registered.update(self.dict_registered)
        self.assertEqual(r.json(), [dict_new, dict_registered])
        factories.HelperFactory()

        # Only own helpers should be included
        self.assertEqual(r.json(), [dict_new, dict_registered])

    def test_query_get_detail(self):
        r = self.client.get(
            reverse('query-detail', args=('new@example.com',)),
            HTTP_API_KEY='test1234567890',
        )
        self.assertEqual(r.json(), self.dict_new)

        # Helper registered already
        r = self.client.get(
            reverse('query-detail', args=('registered@example.com',)),
            HTTP_API_KEY='test1234567890',
        )
        self.assertEqual(r.status_code, 404)

        # Email does not exist
        r = self.client.get(
            reverse('query-detail', args=('doesnotexist@example.com',)),
            HTTP_API_KEY='test1234567890',
        )
        self.assertEqual(r.status_code, 404)

    def test_ak_create(self):
        self.client.force_login(self.user)
        new = self.dict_new.copy()
        new.pop('id')
        new.pop('first_name')
        r = self.client.post(reverse('helper-list'), new, format='json')
        self.assertEqual(r.status_code, 201)
        count = models.Helper.objects.filter(email='new@example.com').count()
        self.assertEqual(count, 2)

    def test_query_create(self):
        # Not allowed
        r = self.client.post(
            '/query/',
            {},
            format='json',
        )
        self.assertEqual(r.status_code, 404)

    def test_ak_update(self):
        self.client.force_login(self.user)

        # Partial update
        # Change area of object with same email as another object
        dict_new = self.dict_new.copy()
        dict_new.pop('id')
        helper = models.Helper.objects.create(user_id=self.user.id, **dict_new)
        r = self.client.patch(
            reverse('helper-detail', args=(helper.pk,)),
            {'area': 'Kitchen'},
            format='json',
        )
        self.assertEqual(r.status_code, 400)
        # Email that already exists with other area
        helper = factories.HelperFactory(food_privilege=False, user=self.user)
        r = self.client.patch(
            reverse('helper-detail', args=(helper.pk,)),
            {'email': 'registered@example.com'},
            format='json',
        )
        self.assertEqual(r.status_code, 400)
        # Email
        r = self.client.patch(
            '/helpers/1/',
            {'email': 'some@thi.ng'},
            format='json',
        )
        self.assertEqual(r.status_code, 200)
        email = models.Helper.objects.get(pk=1).email
        self.assertEqual(email, 'some@thi.ng')
        # The serializer discards unknown and read-only fields -> 200
        # (See https://stackoverflow.com/a/37827123)
        # ID
        r = self.client.patch(
            reverse('helper-detail', args=(1,)),
            {'id': 1000},
            format='json',
        )
        self.assertEqual(r.status_code, 200)
        exists = models.Helper.objects.filter(pk=1000).exists()
        self.assertFalse(exists)
        # Label
        r = self.client.patch(
            reverse('helper-detail', args=(1,)),
            {'label': 'something'},
            format='json',
        )
        self.assertEqual(r.status_code, 200)
        exists = models.Helper.objects.filter(pk=1
                ).filter(label='something').exists()
        self.assertTrue(exists)
        # Area
        r = self.client.patch(
            reverse('helper-detail', args=(1,)),
            {'area': 'something else'},
            format='json',
        )
        self.assertEqual(r.status_code, 200)
        exists = models.Helper.objects.filter(pk=1
                ).filter(area='something else').exists()
        self.assertTrue(exists)
        # Food privilege
        r = self.client.patch(
            reverse('helper-detail', args=(1,)),
            {'food_privilege': False},
            format='json',
        )
        self.assertEqual(r.status_code, 200)
        exists = models.Helper.objects.filter(pk=1
                ).filter(food_privilege=False).exists()
        self.assertTrue(exists)
        # Free admission
        r = self.client.patch(
            reverse('helper-detail', args=(1,)),
            {'free_admission': False},
            format='json',
        )
        self.assertEqual(r.status_code, 200)
        exists = models.Helper.objects.filter(pk=1
                ).filter(free_admission=False).exists()
        self.assertTrue(exists)
        # Above 35
        r = self.client.patch(
            reverse('helper-detail', args=(1,)),
            {'above_35': False},
            format='json',
        )
        self.assertEqual(r.status_code, 200)
        exists = models.Helper.objects.filter(pk=1
                ).filter(above_35=False).exists()
        self.assertTrue(exists)
        # First name
        r = self.client.patch(
            reverse('helper-detail', args=(1,)),
            {'first_name': 'Mona'},
            format='json',
        )
        self.assertEqual(r.status_code, 200)
        exists = models.Helper.objects.filter(pk=1
                ).filter(first_name='Mona').exists()
        self.assertFalse(exists)
        # Last name
        r = self.client.patch(
            reverse('helper-detail', args=(1,)),
            {'last_name': ''},
            format='json',
        )
        self.assertEqual(r.status_code, 200)
        exists = models.Helper.objects.filter(pk=1
                ).filter(last_name='Air').exists()
        self.assertFalse(exists)
        # Age
        r = self.client.patch(
            reverse('helper-detail', args=(1,)),
            {'age': 10},
            format='json',
        )
        self.assertEqual(r.status_code, 200)
        exists = models.Helper.objects.filter(pk=1
                ).filter(age=10).exists()
        self.assertFalse(exists)

        # Complete update
        # Valid
        dict_new = {
            'email': 'new@example.com',
            'label': 'Registration',
            'area': 'Coworker',
            'food_privilege': True,
            'free_admission': True,
            'above_35': True,
        }
        r = self.client.put(
            reverse('helper-detail', args=(1,)),
            dict_new,
            format='json',
        )
        self.assertEqual(r.status_code, 200)
        # Not allowed fields
        r = self.client.put(
            reverse('helper-detail', args=(1,)),
            self.dict_registered,
            format='json',
        )
        self.assertEqual(r.status_code, 200)
        # Helper registered already
        dict_registered = {
            'email': 'registered@example.com',
            'label': 'boots',
            'area': 'Volunteer',
            'food_privilege': True,
            'free_admission': False,
            'above_35': True,
        }
        r = self.client.put(
            reverse('helper-detail', args=(2,)),
            dict_registered,
            format='json',
        )
        self.assertEqual(r.status_code, 400)

    def test_query_update(self):
        # Second entry with same email
        helper = factories.HelperFactory(email='new@example.com')

        # Partial update
        # Email
        r = self.client.patch(
            '/query/new@example.com/',
            {'email': 'some@thi.ng'},
            HTTP_API_KEY='test1234567890',
            format='json',
        )
        exists = models.Helper.objects.filter(email='some@thi.ng').exists()
        self.assertFalse(exists)
        self.assertEqual(r.status_code, 200)
        # ID
        r = self.client.patch(
            reverse('query-detail', args=('new@example.com',)),
            {'id': 1000},
            HTTP_API_KEY='test1234567890',
            format='json',
        )
        self.assertEqual(r.status_code, 200)
        exists = models.Helper.objects.filter(pk=1000).exists()
        self.assertFalse(exists)
        # Label
        r = self.client.patch(
            reverse('query-detail', args=('new@example.com',)),
            {'label': 'something'},
            HTTP_API_KEY='test1234567890',
            format='json',
        )
        self.assertEqual(r.status_code, 200)
        exists = models.Helper.objects.filter(label='something').exists()
        self.assertFalse(exists)
        # Area
        r = self.client.patch(
            reverse('query-detail', args=('new@example.com',)),
            {'area': 'something else'},
            HTTP_API_KEY='test1234567890',
            format='json',
        )
        self.assertEqual(r.status_code, 200)
        exists = models.Helper.objects.filter(area='something else').exists()
        self.assertFalse(exists)
        # Food privilege
        r = self.client.patch(
            reverse('query-detail', args=('new@example.com',)),
            {'food_privilege': False},
            HTTP_API_KEY='test1234567890',
            format='json',
        )
        self.assertEqual(r.status_code, 200)
        exists = models.Helper.objects.filter(pk=1
                ).filter(food_privilege=False).exists()
        self.assertFalse(exists)
        # Free admission
        r = self.client.patch(
            reverse('query-detail', args=('new@example.com',)),
            {'free_admission': False},
            HTTP_API_KEY='test1234567890',
            format='json',
        )
        self.assertEqual(r.status_code, 200)
        exists = models.Helper.objects.filter(pk=1
                ).filter(free_admission=False).exists()
        self.assertFalse(exists)
        # Above 35
        r = self.client.patch(
            reverse('query-detail', args=('new@example.com',)),
            {'above_35': False},
            HTTP_API_KEY='test1234567890',
            format='json',
        )
        self.assertEqual(r.status_code, 200)
        exists = models.Helper.objects.filter(pk=1
                ).filter(above_35=False).exists()
        self.assertFalse(exists)
        # First name
        r = self.client.patch(
            reverse('query-detail', args=('new@example.com',)),
            {'first_name': 'Peter'},
            HTTP_API_KEY='test1234567890',
            format='json',
        )
        self.assertEqual(r.status_code, 200)
        exists = models.Helper.objects.filter(pk=1
                ).filter(first_name='Peter').exists()
        self.assertTrue(exists)
        # Last name
        r = self.client.patch(
            reverse('query-detail', args=('new@example.com',)),
            {'last_name': 'Smith'},
            HTTP_API_KEY='test1234567890',
            format='json',
        )
        self.assertEqual(r.status_code, 200)
        exists = models.Helper.objects.filter(pk=1
                ).filter(last_name='Smith').exists()
        self.assertTrue(exists)
        # Age
        # Now the next helper with the same email is used
        # (because the last name is set).
        r = self.client.patch(
            reverse('query-detail', args=('new@example.com',)),
            {'age': 10},
            HTTP_API_KEY='test1234567890',
            format='json',
        )
        self.assertEqual(r.status_code, 200)
        exists = models.Helper.objects.filter(pk=helper.pk
                ).filter(age=10).exists()
        self.assertTrue(exists)
        # Helper registered already
        r = self.client.patch(
            reverse('query-detail', args=('registered@example.com',)),
            {'age': 10},
            HTTP_API_KEY='test1234567890',
            format='json',
        )
        self.assertEqual(r.status_code, 404)

        # Complete update
        # Valid
        dict_helper = {
            'first_name': 'Timmy',
            'last_name': 'Jonson',
            'age': 34,
        }
        r = self.client.put(
            reverse('query-detail', args=('new@example.com',)),
            dict_helper,
            HTTP_API_KEY='test1234567890',
            format='json',
        )
        self.assertEqual(r.status_code, 200)
        # Not allowed fields
        helper = factories.HelperFactory()
        r = self.client.put(
            reverse('query-detail', args=(helper.email,)),
            {'non_existent': True},
            HTTP_API_KEY='test1234567890',
            format='json',
        )
        self.assertEqual(r.status_code, 200)

    def test_ak_delete(self):
        self.client.force_login(self.user)
        r = self.client.delete(reverse('helper-detail', args=(1,)))
        self.assertEqual(r.status_code, 204)
        deleted = not models.Helper.objects.filter(pk=1).exists()
        self.assertTrue(deleted)
        # Helper registered already
        r = self.client.delete(reverse('helper-detail', args=(2,)))
        self.assertEqual(r.status_code, 400)
        deleted = not models.Helper.objects.filter(pk=2).exists()
        self.assertFalse(deleted)

    def test_query_delete(self):
        # Not allowed
        r = self.client.delete(
            reverse('query-detail', args=(1,)),
            HTTP_API_KEY='test1234567890',
        )
        self.assertEqual(r.status_code, 405)
        deleted = not models.Helper.objects.filter(pk=1).exists()
        self.assertFalse(deleted)

class CSRFTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient(enforce_csrf_checks=True)

    def test_csrf(self):
        user = factories.UserFactory()
        logged_in = self.client.login(username=user.username, password='pw')
        self.assertTrue(logged_in)
        r = self.client.get(reverse('helper-list'))
        self.assertEqual(r.status_code, 200)
        #csrf_token = r.cookies['csrftoken']
        data = {
            'email': 'csrf@example.com',
            'label': 'Security',
            'area': 'CSRF',
            'food_privilege': True,
            'free_admission': True,
            'above_35': True,
        }
        r = self.client.post(
            reverse('helper-list'),
            data,
            #headers={'X-CSRFToken': csrf_token},
        )
        self.assertEqual(r.status_code, 201)
