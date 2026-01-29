from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from board.models import Meet, Problem, Session


# Customize the existing admin site instead of replacing it
admin.site.site_header = "Edit website"
admin.site.site_title = "Calculum Edit"
admin.site.index_title = "Applications"
admin.site.site_url = None


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


# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


class ProblemAdmin(admin.ModelAdmin):
	search_fields = ['platform', 'link', 'solution_link']

	def get_ordering(self, request):
		# Sort by platform and extracted title (as in __str__)
		return ['platform', 'link']


admin.site.register(Problem, ProblemAdmin)
admin.site.register(Session)