
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
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

class UserAdmin(BaseUserAdmin):
	def has_add_permission(self, request):
		return request.user.is_superuser
	
	def has_change_permission(self, request, obj=None):
		return request.user.is_superuser
	
	def has_delete_permission(self, request, obj=None):
		return request.user.is_superuser
	
	def has_view_permission(self, request, obj=None):
		return request.user.is_superuser

admin.site.register(User, UserAdmin)

class ProblemAdmin(admin.ModelAdmin):
	search_fields = ['platform', 'link', 'solution_link']

	def get_ordering(self, request):
		# Sort by platform and extracted title (as in __str__)
		return ['platform', 'link']

admin.site.register(Problem, ProblemAdmin)
admin.site.register(Session)