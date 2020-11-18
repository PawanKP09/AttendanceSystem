from django.contrib import admin
from applications.accounts.models import User, UserImages, Logs
# Register your models here.


from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


class UserAdmin(BaseUserAdmin):

    search_fields = (
        'first_name',
        'last_name',
        'email',

    )

    list_filter = (
        'created',

    )

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Dates'), {'fields': ('date_joined',)}),
    )

admin.site.register(User, UserAdmin)
admin.site.register(UserImages)
admin.site.register(Logs)
