
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

admin.site.register(User)

class ProblemAdmin(admin.ModelAdmin):
	search_fields = ['platform', 'link', 'solution_link']

	def get_ordering(self, request):
		# Sort by platform and extracted title (as in __str__)
		return ['platform', 'link']

admin.site.register(Problem, ProblemAdmin)
admin.site.register(Session)