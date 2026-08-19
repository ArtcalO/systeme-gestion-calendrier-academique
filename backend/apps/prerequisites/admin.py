from django.contrib import admin
from .models import ModulePrerequisite, PrerequisiteGraph


@admin.register(ModulePrerequisite)
class ModulePrerequisiteAdmin(admin.ModelAdmin):
    list_display = ['prerequisite', 'module', 'prerequisite_type', 'minimum_grade']
    list_filter = ['prerequisite_type']
    search_fields = ['module__code', 'module__name', 'prerequisite__code', 'prerequisite__name']
    autocomplete_fields = ['module', 'prerequisite']


@admin.register(PrerequisiteGraph)
class PrerequisiteGraphAdmin(admin.ModelAdmin):
    list_display = ['program', 'generated_at', 'is_valid']
    list_filter = ['is_valid']
    readonly_fields = ['generated_at']
