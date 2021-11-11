from django.contrib import admin

from .models import Category

# Register your models here.

# class CategoryAdmin(admin.ModelAdmin):
#   prepopulated_fields = ({'slug': ('name'),})
#   fields = ('name', 'slug')

admin.site.register(Category)