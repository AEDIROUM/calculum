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
	# EXISTING: Search fields
	search_fields = ['platform', 'link', 'solution_link']
	
	# NEW: Add categories to the admin interface
	filter_horizontal = ('meets', 'categories')
	list_display = ('link_short', 'platform', 'difficulty', 'categories_list')
	list_filter = ('platform', 'categories')
	
	def get_ordering(self, request):
		# EXISTING: Sort by platform and extracted title (as in __str__)
		return ['platform', 'link']
	
	# NEW: Helper methods for better display
	def link_short(self, obj):
		"""Display shortened link in list view"""
		return obj.link[:60] + '...' if len(obj.link) > 60 else obj.link
	link_short.short_description = 'Link'
	
	def categories_list(self, obj):
		"""Display comma-separated list of categories"""
		categories = obj.categories.all()
		if categories:
			return ', '.join([cat.name for cat in categories])
		return '-'
	categories_list.short_description = 'Categories'
	
	# NEW: Bulk actions for managing problems
	actions = ['fetch_difficulties', 'clear_categories']
	
	def fetch_difficulties(self, request, queryset):
		"""Fetch difficulties for selected problems from Kattis/LeetCode"""
		count = 0
		for problem in queryset:
			if 'kattis.com' in problem.link:
				if problem._fetch_kattis_difficulty():
					count += 1
			elif 'leetcode.com' in problem.link:
				if problem._fetch_leetcode_difficulty():
					count += 1
		self.message_user(request, f"Successfully fetched difficulty for {count} problems.")
	fetch_difficulties.short_description = "Fetch difficulties for selected problems"
	
	def clear_categories(self, request, queryset):
		"""Clear all categories from selected problems"""
		for problem in queryset:
			problem.categories.clear()
		self.message_user(request, f"Cleared categories from {queryset.count()} problems.")
	clear_categories.short_description = "Clear categories from selected problems"


admin.site.register(Problem, ProblemAdmin)
admin.site.register(Session)