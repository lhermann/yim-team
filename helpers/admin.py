from django.contrib import admin
from .models import Helper

class HelperAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'reg_id', 'area', 'label', 'user')
    search_fields = ('^email$', '^last_name', '^reg_id')

admin.site.register(Helper, HelperAdmin)
