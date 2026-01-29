from django.contrib import admin
from django import forms
from cheatsheet.models import Algorithm, AlgorithmCategory


# Custom form with better code editing
class AlgorithmAdminForm(forms.ModelForm):
    class Meta:
        model = Algorithm
        fields = '__all__'
        widgets = {
            'code': forms.Textarea(attrs={
                'style': 'font-family: monospace; width: 100%; min-height: 400px;'
            }),
        }


@admin.register(AlgorithmCategory)
class AlgorithmCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'algorithm_count']
    list_editable = ['order']
    search_fields = ['name', 'description']
    
    def algorithm_count(self, obj):
        return obj.algorithms.count()
    algorithm_count.short_description = 'Algorithms'


@admin.register(Algorithm)
class AlgorithmAdmin(admin.ModelAdmin):
    form = AlgorithmAdminForm
    list_display = ['title', 'category', 'language', 'time_complexity', 'space_complexity', 'order', 'updated_at']
    list_filter = ['category', 'language', 'created_at', 'updated_at']
    list_editable = ['order']
    search_fields = ['title', 'description', 'code']
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'category', 'description', 'order')
        }),
        ('Code', {
            'fields': ('language', 'code'),
            'classes': ('wide',)
        }),
        ('Complexity', {
            'fields': ('time_complexity', 'space_complexity'),
            'classes': ('collapse',)
        }),
    )