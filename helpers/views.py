# -*- coding: utf-8 -*-
import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from rest_framework import mixins, viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import MethodNotAllowed, NotFound
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.views import APIView
from helpers.models import Helper
from helpers import permissions, serializers
from helpers.authentications import TokenAuthentication

@login_required
def home_view(request):
    if request.method == 'GET':
        return render(request, 'index.html')
    raise MethodNotAllowed(request.method)

class RegisterSeatView(APIView):
    """
    Reveive API from registerseat.com.
    """
    def get(self, request, field, value):
        post_fields = {
            'ws': 'get_registrations',
            'f': 'json',
            '_auth_t': settings.RS_TOKEN,
            'eventID': settings.RS_EVENT_ID,
            # 'customfield{}'.format(field): value,
        }

        if field.isdigit():
            post_fields.update({
                'customfield{}'.format(field): value,
            })

        if field == '10':
            post_fields.update({
                'customfield10_compare': 'like',
                'customfield10': '%' + value + '%',
            })

        if field == 'reg_id':
            post_fields.update({
                # query the reg_id
                # 'registration_iweekendID': value,
            })

        response = requests.post(
            url='https://registerseat.com/ws.php',
            data=post_fields,
        )
        return Response(response.json())

class HelperViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows helpers to be viewed or edited by the owners.
    """
    serializer_class = serializers.HelperSerializer
    permission_classes = (permissions.IsOwner,)

    def get_queryset(self):
        qs = Helper.objects.filter(user_id=self.request.user.id).order_by('pk')
        return qs

    def email_check(self, data, instance=None):
        """
        Allow same email for multiple entries with equal fields only.
        """
        area = None
        email = data.get('email')
        if email is None:
            email = instance.email
        # There is no instance when creating a helper
        elif instance is not None:
            # Check for all fields which have to be equal if email gets updated
            area = getattr(instance, 'area')
        # Update old value with new value
        if 'area' in data:
            area = data['area']
        if area:
            qs_incl_inst = Helper.objects.filter(email=email).exclude(area=area)
            if instance is None:
                deny = qs_incl_inst.exists()
            else:
                deny = qs_incl_inst.exclude(pk=instance.pk).exists()
            if deny:
                message = (
                    'Mit der eMail-Adresse "{}" wurden bereits Helfer '
                    'für einen anderen Bereich eingetragen, der allerdings '
                    'übereinstimmen muss. '
                    '(Falls in deiner Liste die eMail-Adresse nicht auftaucht, '
                    'wurde sie von einem anderen Benutzer verwendet.)'
                )
                raise ValidationError(message.format(email))

    def perform_create(self, serializer):
        """
        Allow same email for multiple entries with equal fields only.
        """
        self.email_check(serializer.validated_data)
        serializer.save(user_id=self.request.user.id)

    def perform_update(self, serializer):
        """
        Email and registered helpers checks.

        Allow same email for multiple entries with equal fields only.
        Disallow edit on registered helpers.
        """
        self.email_check(serializer.validated_data, serializer.instance)

        """
        Disallowing edit on registered helpers is now disabled
        """
        # Registered helpers validation
        # deny = Helper.objects.filter(pk=self.kwargs['pk']).filter(
        #         last_name__regex=r'^.+').exists()
        # if deny:
        #     message = (
        #         'Dieser Helfer hat sich bereits angemeldet. Daher können '
        #         'keine Änderungen mehr erfolgen.'
        #     )
        #     raise ValidationError(message)
        serializer.save()

    def perform_destroy(self, instance):
        """
        Don't delete registered helpers.
        """
        if instance.last_name:
            raise ValidationError(
                'Dieser Helfer ist bereits angemeldet und '
                'kann daher nicht mehr gelöscht werden.'
            )
        instance.delete()

    def dispatch(self, request, *args, **kwargs):
        response = super(HelperViewSet, self).dispatch(request, *args, **kwargs)
        if request.user.is_authenticated:
            response['data-user'] = request.user.first_name
        return response

class EmailRetrieveSupplementHelperViewSet(mixins.RetrieveModelMixin,
                                           mixins.UpdateModelMixin,
                                           viewsets.GenericViewSet):
    """
    Endpoint to retrive/supplement not registered helpers based on their email.
    """
    queryset = Helper.objects.all()
    lookup_url_kwarg = 'email'
    lookup_value_regex = '[-@\.\w]+'
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    serializer_class = serializers.UnregisteredHelperSerializer
    permission_classes = (permissions.WhiteListAndAPIKey,)

    def get_object(self):
        """
        Return the first matching object because email is not unique.
        """
        queryset = self.get_queryset()
        queryset = queryset.filter(
            email__iexact=self.kwargs['email'],
            last_name='',
        )
        try:
            obj = queryset[0]
        except IndexError:
            raise NotFound()
        self.check_object_permissions(self.request, obj)
        return obj
