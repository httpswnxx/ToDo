from django.contrib import admin

from apps.models import Task, User, Category

admin.site.register(Task)
admin.site.register(User)
admin.site.register(Category)