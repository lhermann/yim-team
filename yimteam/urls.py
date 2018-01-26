from django.conf.urls import include, url
from django.contrib import admin
from rest_framework import routers
from helpers import views

router = routers.DefaultRouter()
router.register(r'helpers', views.HelperViewSet, 'helper')
router.register(r'query', views.EmailRetrieveSupplementHelperViewSet, 'query')

urlpatterns = [
    url(r'^$', views.home_view, name='home'),
    url(r'^', include(router.urls)),
    url(r'registerseat/(?P<field>.+)/(?P<value>[A-Za-z0-9]+)', views.RegisterSeatView.as_view(), name='registerseat'),
    url(r'auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^maetmiy/', admin.site.urls),
]
