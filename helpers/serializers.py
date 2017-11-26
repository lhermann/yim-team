# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from .models import Helper

fields_new = (
    'email',
    'label',
    'area',
    'food_privilege',
    'free_admission',
    'above_35',
    't_shirt_size'
)
fields_registered = (
    'first_name',
    'last_name',
    'age',
)

class HelperSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Helper
        fields = ['id', 'url']
        fields.extend(fields_new)
        fields.extend(fields_registered)
        read_only_fields = fields_registered

class UnregisteredHelperSerializer(serializers.ModelSerializer):
    class Meta:
        model = Helper
        exclude = ('user',)
        read_only_fields = fields_new
