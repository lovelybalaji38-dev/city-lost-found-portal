



from django.contrib import admin
from django.contrib.auth.models import User
from .models import Item
from django.db.models import Count, Q

admin.site.register(Item)

from django.contrib import admin
from django.contrib.auth.models import User
from .models import Item
from django.db.models import Count, Q

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'total_posts', 'lost_count', 'found_count')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(
            total_posts=Count('items'),
            lost_count=Count('items', filter=Q(items__status='lost')),
            found_count=Count('items', filter=Q(items__status='found')),
        )
        return qs

    def total_posts(self, obj):
        return obj.total_posts

    def lost_count(self, obj):
        return obj.lost_count

    def found_count(self, obj):
        return obj.found_count

admin.site.unregister(User)
admin.site.register(User, UserAdmin)