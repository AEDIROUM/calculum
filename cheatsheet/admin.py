from django.contrib import admin
from django import forms
from cheatsheet.models import Algorithm, AlgorithmCategory


# Custom form with CodeMirror syntax highlighting
class AlgorithmAdminForm(forms.ModelForm):
    class Meta:
        model = Algorithm
        fields = '__all__'
        widgets = {
            'code': forms.Textarea(attrs={
                'class': 'code-editor',
                'style': 'font-family: monospace; width: 100%; min-height: 400px;'
            }),
        }


@admin.register(AlgorithmCategory)
class AlgorithmCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'algorithm_count']
    search_fields = ['name', 'description']
    
    def algorithm_count(self, obj):
        return obj.algorithms.count()
    algorithm_count.short_description = 'Algorithms'


@admin.register(Algorithm)
class AlgorithmAdmin(admin.ModelAdmin):
    form = AlgorithmAdminForm
    list_display = ['title', 'category', 'language', 'time_complexity', 'space_complexity', 'updated_at']
    list_filter = ['category', 'language', 'created_at', 'updated_at']
    search_fields = ['title', 'description', 'code']
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'category', 'description')
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
    
    class Media:
        css = {
            'all': (
                'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/codemirror.min.css',
                'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/theme/monokai.min.css',
            )
        }
        js = (
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/codemirror.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/python/python.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/clike/clike.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/javascript/javascript.min.js',
            'admin/js/algorithm_codemirror.js',
        )