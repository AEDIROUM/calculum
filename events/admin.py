from django.contrib import admin
from django.utils.safestring import mark_safe
import markdown

from events.models import Event, Media


class EventAdmin(admin.ModelAdmin):
	list_display = ('title', 'start', 'end', 'short_summary', 'server_status')
	readonly_fields = ('rendered_summary', 'slug')
	fieldsets = (
		(None, {'fields': ('title', 'slug', 'start', 'end')}),
		('Summary', {'fields': ('summary', 'rendered_summary')}),
		('Server Proxy', {
			'fields': ('server_port', 'is_active'),
			'description': 'Configure a proxied server for this event. The server will be accessible at /events/{slug}'
		}),
	)

	def rendered_summary(self, obj):
		text = obj.summary or ''
		html = markdown.markdown(text, extensions=['fenced_code', 'codehilite'])
		return mark_safe(html)

	rendered_summary.short_description = 'Rendered summary (Markdown)'

	def short_summary(self, obj):
		s = (obj.summary or '')
		return s[:75] + ('...' if len(s) > 75 else '')

	short_summary.short_description = 'Summary'
	
	def server_status(self, obj):
		if obj.server_port:
			if obj.is_active:
				return mark_safe(f'<span style="color: #2ecc71;">● Active (:{obj.server_port})</span>')
			else:
				return mark_safe(f'<span style="color: #95a5a6;">○ Inactive (:{obj.server_port})</span>')
		return '-'
	
	server_status.short_description = 'Server'


admin.site.register(Event, EventAdmin)
admin.site.register(Media)