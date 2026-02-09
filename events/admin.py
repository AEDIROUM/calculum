from django.contrib import admin
from django.utils.safestring import mark_safe
import markdown

from events.models import Event, Media


class EventAdmin(admin.ModelAdmin):
	list_display = ('title', 'start', 'end', 'short_summary')
	readonly_fields = ('rendered_summary',)
	fieldsets = (
		(None, {'fields': ('title', 'start', 'end')}),
		('Summary', {'fields': ('summary', 'rendered_summary')}),
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


admin.site.register(Event, EventAdmin)
admin.site.register(Media)