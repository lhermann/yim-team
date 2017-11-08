# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from rest_framework import mixins, viewsets
from rest_framework.exceptions import MethodNotAllowed, NotFound
from rest_framework.serializers import ValidationError
from helpers.models import Helper
from helpers import permissions, serializers

@login_required
def home_view(request):
    if request.method == 'GET':
        return render(request, 'index.html')
    raise MethodNotAllowed(request.method)

class HelperViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows helpers to be viewed or edited by the owners.
    """
    serializer_class = serializers.HelperSerializer
    permission_classes = (permissions.IsOwner,)

    def get_queryset(self):
        return Helper.objects.filter(user_id=self.request.user.id)

    def email_check(self, data, instance=None):
        """
        Allow same email for multiple entries with equal fields only.
        """
        fields = serializers.fields_new[1:]
        excl = {}
        email = data.get('email')
        if email is None:
            email = instance.email
        # There is no instance when creating a helper
        elif instance is not None:
            # Check for all fields which have to be equal if email gets updated
            excl = {f: getattr(instance, f) for f in fields}
        # Update old values with new values
        excl.update({f: data[f] for f in fields if f in data})
        if excl:
            qs_incl_instance = Helper.objects.filter(email=email).exclude(**excl)
            if instance is None:
                deny = qs_incl_instance.exists()
            else:
                deny = qs_incl_instance.exclude(pk=instance.pk).exists()
            if deny:
                message = (
                    'Mit der eMail-Adresse "{}" wurden bereits Helfer '
                    'mit anderen Angaben eingetragen. Sie müssen übereinstimmen. '
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
        # Registered helpers validation
        deny = Helper.objects.filter(pk=self.kwargs['pk']).filter(
                last_name__regex=r'^.+').exists()
        if deny:
            message = (
                'Dieser Helfer hat sich bereits angemeldet. Daher können '
                'keine Änderungen mehr erfolgen.'
            )
            raise ValidationError(message)
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

class EmailRetrieveSupplementHelperViewSet(mixins.RetrieveModelMixin,
                                           mixins.UpdateModelMixin,
                                           viewsets.GenericViewSet):
    """
    Endpoint to retrive/supplement not registered helpers based on their email.
    """
    queryset = Helper.objects.all()
    lookup_url_kwarg = 'email'
    lookup_value_regex = '[-@\.\w]+'
    serializer_class = serializers.UnregisteredHelperSerializer
    permission_classes = (permissions.WhiteListAndAPIKey,)

    def get_object(self):
        """
        Return the first matching object because email is not unique.
        """
        queryset = self.get_queryset()
        queryset = queryset.filter(email=self.kwargs['email'], last_name='')
        try:
            obj = queryset[0]
        except IndexError:
            raise NotFound()
        self.check_object_permissions(self.request, obj)
        return obj