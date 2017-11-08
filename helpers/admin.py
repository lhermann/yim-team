from django.contrib import admin
from .models import Helper

class HelperAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'area', 'label', 'user')
    search_fields = ('^email$', '^last_name')

admin.site.register(Helper, HelperAdmin)
