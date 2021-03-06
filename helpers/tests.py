from django.test import override_settings, TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from helpers import factories, models

class CollectedTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = factories.UserFactory()

    def test_home(self):
        r = self.client.get(reverse('home'))
        self.assertEqual(r.status_code, 302)
        self.client.force_login(self.user)
        r = self.client.get(reverse('home'))
        self.assertContains(r, 'Mitarbeiter')

    def test_registerseat_api(self):
        # Log in required
        r = self.client.get(reverse('registerseat', args=(14, 'Surroundings')))
        self.assertEqual(r.status_code, 403)
        self.client.force_login(self.user)

        # Former event with data
        with self.settings(RS_EVENT_ID=66):
            r = self.client.get(reverse('registerseat', args=(19, 'maintenance')))
            self.assertContains(r, 'rg_customfield14')
            r = self.client.get(reverse('registerseat', args=(21, 'setup')))
            self.assertEqual(r.status_code, 200)

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
        r = self.client.get(reverse('rest_framework:logout'), follow=True)
        # View shows a login form
        self.assertContains(r, 'password')
        # Custom style sheets
        self.assertContains(r, 'open-iconic-bootstrap.min.css')
        self.assertNotContains(r, 'Django REST framework')


@override_settings(
    QUERY_API_KEYS='test1234567890',
    QUERY_WHITE_LIST=('127.0.0.1',),
)
class HelperAPITests(APITestCase):
    maxDiff = None
    dict_new = {
        'id': 1,
        'email': 'new@example.com',
        'label': 'Registration',
        'area': 'Coworker',
        'food_privilege': True,
        'free_admission': True,
        'above_35': True,
        't_shirt_size': 'XL',
        'reg_id': None,
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
        't_shirt_size': 'S',
        'reg_id': 11,
        'first_name': 'Timmy',
        'last_name': 'Jonson',
        'age': 34,
    }

    api_key = {
        # This doesn't work because in the real world this header name
        # gets converted to the name below:
        #'x-http-api-key': 'test1234567890',
        'HTTP_X_HTTP_API_KEY': 'test1234567890',
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
            **self.api_key,
        )
        self.assertEqual(r.status_code, 200)

        # Wrong IP address
        r = self.client.get(
            reverse('query-detail', args=('new@example.com',)),
            REMOTE_ADDR='127.0.0.2',
            **self.api_key,
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

    def test_username_in_header(self):
        user = factories.UserFactory(first_name='Auf- und Abbau')
        self.client.force_login(user)
        r = self.client.get(reverse('helper-list'))
        self.assertTrue(r.has_header('data-user'))
        self.assertEqual(r['data-user'], 'Auf- und Abbau')

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
        r = self.client.get(reverse('helper-list'))
        self.assertEqual(r.json(), [dict_new, dict_registered])

    def test_query_get_detail(self):
        r = self.client.get(
            reverse('query-detail', args=('new@example.com',)),
            **self.api_key,
        )
        self.assertEqual(r.json(), self.dict_new)

        # Helper registered already
        r = self.client.get(
            reverse('query-detail', args=('registered@example.com',)),
            **self.api_key,
        )
        self.assertEqual(r.status_code, 404)

        # Email does not exist
        r = self.client.get(
            reverse('query-detail', args=('doesnotexist@example.com',)),
            **self.api_key,
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
        # Change value of object with same email as another object
        dict_new = self.dict_new.copy()
        dict_new.pop('id')
        helper = models.Helper.objects.create(user_id=self.user.id, **dict_new)
        r = self.client.patch(
            reverse('helper-detail', args=(helper.pk,)),
            {'food_privilege': False},
            format='json',
        )
        self.assertEqual(r.status_code, 200)
        # Email that already exists with other area
        helper = factories.HelperFactory(food_privilege=False, user=self.user)
        r = self.client.patch(
            reverse('helper-detail', args=(helper.pk,)),
            {'email': 'registered@example.com'},
            format='json',
        )
        self.assertEqual(r.status_code, 400)
        msg = 'Mit der eMail-Adresse "registered@example.com" wurden ber'
        self.assertEqual(r.json()[0][:len(msg)], msg)
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
        self.assertEqual(r.status_code, 200)

    def test_query_with_capitel_letters_get(self):
        r = self.client.get(
            reverse('query-detail', args=('New@Example.com',)),
            **self.api_key,
            format='json',
        )
        self.assertEqual(r.status_code, 200)

    def test_query_with_capitel_letters_patch(self):
        r = self.client.patch(
            reverse('query-detail', args=('NEW@example.com',)),
            {'first_name': 'NEW'},
            **self.api_key,
            format='json',
        )
        exists = models.Helper.objects.filter(first_name='NEW').exists()
        self.assertTrue(exists)
        self.assertEqual(r.status_code, 200)

    def test_query_db_value_with_capitel_letters(self):
        helper = factories.HelperFactory(email='CAPITAL@EXAMPLE.COM')
        r = self.client.get(
            reverse('query-detail', args=('capital@example.com',)),
            **self.api_key,
            format='json',
        )
        self.assertEqual(r.status_code, 200)

    def test_query_update(self):
        pk_1 = self.helper_new.pk
        # Second entry with same email
        helper = factories.HelperFactory(email='new@example.com')

        # Partial update
        # Email
        r = self.client.patch(
            '/query/new@example.com/',
            {'email': 'some@thi.ng'},
            **self.api_key,
            format='json',
        )
        exists = models.Helper.objects.filter(email='some@thi.ng').exists()
        self.assertFalse(exists)
        self.assertEqual(r.status_code, 200)
        # ID
        r = self.client.patch(
            reverse('query-detail', args=('new@example.com',)),
            {'id': 1000},
            **self.api_key,
            format='json',
        )
        self.assertEqual(r.status_code, 200)
        exists = models.Helper.objects.filter(pk=1000).exists()
        self.assertFalse(exists)
        # Label
        r = self.client.patch(
            reverse('query-detail', args=('new@example.com',)),
            {'label': 'something'},
            **self.api_key,
            format='json',
        )
        self.assertEqual(r.status_code, 200)
        exists = models.Helper.objects.filter(label='something').exists()
        self.assertFalse(exists)
        # Area
        r = self.client.patch(
            reverse('query-detail', args=('new@example.com',)),
            {'area': 'something else'},
            **self.api_key,
            format='json',
        )
        self.assertEqual(r.status_code, 200)
        exists = models.Helper.objects.filter(area='something else').exists()
        self.assertFalse(exists)
        # Food privilege
        r = self.client.patch(
            reverse('query-detail', args=('new@example.com',)),
            {'food_privilege': False},
            **self.api_key,
            format='json',
        )
        self.assertEqual(r.status_code, 200)
        exists = models.Helper.objects.filter(pk=pk_1
                ).filter(food_privilege=False).exists()
        self.assertFalse(exists)
        # Free admission
        r = self.client.patch(
            reverse('query-detail', args=('new@example.com',)),
            {'free_admission': False},
            **self.api_key,
            format='json',
        )
        self.assertEqual(r.status_code, 200)
        exists = models.Helper.objects.filter(pk=pk_1
                ).filter(free_admission=False).exists()
        self.assertFalse(exists)
        # Above 35
        r = self.client.patch(
            reverse('query-detail', args=('new@example.com',)),
            {'above_35': False},
            **self.api_key,
            format='json',
        )
        self.assertEqual(r.status_code, 200)
        exists = models.Helper.objects.filter(pk=pk_1
                ).filter(above_35=False).exists()
        self.assertFalse(exists)
        # First name
        r = self.client.patch(
            reverse('query-detail', args=('new@example.com',)),
            {'first_name': 'Peter'},
            **self.api_key,
            format='json',
        )
        self.assertEqual(r.status_code, 200)
        exists = models.Helper.objects.filter(pk=pk_1
                ).filter(first_name='Peter').exists()
        self.assertTrue(exists)
        # Last name
        r = self.client.patch(
            reverse('query-detail', args=('new@example.com',)),
            {'last_name': 'Smith'},
            **self.api_key,
            format='json',
        )
        self.assertEqual(r.status_code, 200)
        exists = models.Helper.objects.filter(pk=pk_1
                ).filter(last_name='Smith').exists()
        self.assertTrue(exists)
        # Age
        # Now the next helper with the same email is used
        # (because the last name is set).
        r = self.client.patch(
            reverse('query-detail', args=('new@example.com',)),
            {'age': 10},
            **self.api_key,
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
            **self.api_key,
            format='json',
        )
        self.assertEqual(r.status_code, 404)

        # Complete update
        # Valid
        dict_helper = {
            'first_name': 'Timmy',
            'last_name': 'Jonson',
            'age': 34,
            'reg_id': 2000,
            't_shirt_size': 'M',
        }
        r = self.client.put(
            reverse('query-detail', args=('new@example.com',)),
            dict_helper,
            **self.api_key,
            format='json',
        )
        self.assertEqual(r.status_code, 200)
        # Not allowed fields
        helper = factories.HelperFactory()
        r = self.client.put(
            reverse('query-detail', args=(helper.email,)),
            {'non_existent': True},
            **self.api_key,
            format='json',
        )
        self.assertEqual(r.status_code, 200)

    def test_ak_delete(self):
        self.client.force_login(self.user)
        pk_1 = self.helper_new.pk
        pk_2 = self.helper_registered.pk
        r = self.client.delete(reverse('helper-detail', args=(pk_1,)))
        self.assertEqual(r.status_code, 204)
        deleted = not models.Helper.objects.filter(pk=pk_1).exists()
        self.assertTrue(deleted)
        # Helper registered already
        r = self.client.delete(reverse('helper-detail', args=(pk_2,)))
        self.assertEqual(r.status_code, 400)
        deleted = not models.Helper.objects.filter(pk=pk_2).exists()
        self.assertFalse(deleted)

    def test_query_delete(self):
        pk_1 = self.helper_new.pk
        # Not allowed
        r = self.client.delete(
            reverse('query-detail', args=(pk_1,)),
            **self.api_key,
        )
        self.assertEqual(r.status_code, 405)
        deleted = not models.Helper.objects.filter(pk=pk_1).exists()
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
