
from django.contrib import admin
from django.contrib.auth.models import User
from board.models import Meet, Problem, Session

class CustomAdminSite(admin.AdminSite):
	site_header = "Edit website"
	site_title = "Calculum Edit"
	index_title = "Applications"
	site_url = None
	
	def index(self, request, extra_context=None):
		extra_context = extra_context or {}
		return super().index(request, extra_context)

admin.site = CustomAdminSite()

admin.site.register(Meet)

class UserAdmin(admin.ModelAdmin):
	def get_queryset(self, request):
		# Staff can only see themselves; superusers see all
		qs = super().get_queryset(request)
		if request.user.is_superuser:
			return qs
		return qs.filter(pk=request.user.pk)
	
	def get_readonly_fields(self, request):
		# Superusers can edit everything; staff cannot edit sensitive fields
		if request.user.is_superuser:
			return []
		return ['username', 'is_staff', 'is_superuser', 'is_active', 'groups', 'user_permissions', 'last_login', 'date_joined']
	
	def get_fieldsets(self, request, obj=None):
		# Show limited fields to staff
		fieldsets = super().get_fieldsets(request, obj)
		if request.user.is_superuser:
			return fieldsets
		return (
			(None, {'fields': ('username', 'password')}),
			('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
			('Permissions', {'fields': ('is_staff', 'is_superuser', 'is_active'), 'classes': ('collapse',)}),
		)

admin.site.register(User, UserAdmin)

class ProblemAdmin(admin.ModelAdmin):
	search_fields = ['platform', 'link', 'solution_link']

	def get_ordering(self, request):
		# Sort by platform and extracted title (as in __str__)
		return ['platform', 'link']

admin.site.register(Problem, ProblemAdmin)
admin.site.register(Session)