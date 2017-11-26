# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User

class Helper(models.Model):
    email = models.EmailField()
    label = models.CharField(max_length=30)
    area = models.CharField(max_length=30)
    food_privilege = models.BooleanField()
    free_admission = models.BooleanField()
    above_35 = models.BooleanField()
    t_shirt_size = models.CharField(max_length=20, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    age = models.PositiveSmallIntegerField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        index_together = ['email', 'last_name']

    def __str__(self):
        if self.last_name:
            return '{} {}'.format(self.first_name, self.last_name)
        else:
            return self.email
