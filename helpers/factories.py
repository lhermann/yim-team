import factory
from django.contrib.auth.models import Permission, User
from factory import Faker
from helpers import models

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = Faker('user_name')
    email = Faker('email')
    is_active = True
    password = factory.PostGenerationMethodCall('set_password', 'pw')

    @factory.post_generation
    def all_permissions(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            self.user_permissions = Permission.objects.all()

class HelperFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Helper

    email = Faker('email')
    label = Faker('text', max_nb_chars=30)
    area = Faker('text', max_nb_chars=30)
    food_privilege = Faker('boolean', chance_of_getting_true=50)
    free_admission = Faker('boolean', chance_of_getting_true=50)
    above_35 = Faker('boolean', chance_of_getting_true=50)
    t_shirt_size = Faker('text', max_nb_chars=20)
    user = factory.SubFactory(UserFactory)

    class Params:
        complete = factory.Trait(
            reg_id=Faker('random_int', min=1000, max=5000),
            first_name=Faker('first_name'),
            last_name=Faker('last_name'),
            age=Faker('random_int', min=9, max=90),
            t_shirt_size=Faker('text', max_nb_chars=20),
        )
