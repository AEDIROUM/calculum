from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from board.models import Meet, Problem, Session


admin.site.site_header = "Edit website"
admin.site.site_title = "Calculum Edit"
admin.site.index_title = "Applications"
admin.site.site_url = None


class ProblemInline(admin.TabularInline):
    model = Problem.meets.through
    extra = 1
    verbose_name = "Problem"
    verbose_name_plural = "Problems"


class MeetAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'session', 'contest_link', 'problem_count')
    list_filter = ('session',)
    search_fields = ('description', 'contest_link')
    inlines = [ProblemInline]

    def problem_count(self, obj):
        return obj.problems.count()
    problem_count.short_description = '# Problems'


admin.site.register(Meet, MeetAdmin)


class UserAdmin(BaseUserAdmin):
    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


class HasDifficultyFilter(admin.SimpleListFilter):
    title = 'difficulty status'
    parameter_name = 'has_difficulty'

    def lookups(self, request, model_admin):
        return [
            ('yes', 'Has difficulty'),
            ('no', 'Missing difficulty'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.exclude(difficulty='')
        if self.value() == 'no':
            return queryset.filter(difficulty='')


class ProblemAdmin(admin.ModelAdmin):
    search_fields = ['platform', 'link', 'solution_link']
    filter_horizontal = ('meets', 'categories')
    list_display = ('__str__', 'platform', 'difficulty_display', 'categories_list', 'meets_list')
    list_filter = ('platform', 'categories', HasDifficultyFilter)
    ordering = ['platform', 'link']

    def difficulty_display(self, obj):
        if not obj.difficulty:
            return format_html('<span style="color:#999">—</span>')
        level = obj.get_difficulty_level()
        colors = {'easy': '#5cb85c', 'medium': '#f0ad4e', 'hard': '#d9534f'}
        color = colors.get(level, '#333')
        return format_html('<span style="color:{}">{}</span>', color, obj.difficulty)
    difficulty_display.short_description = 'Difficulty'

    def categories_list(self, obj):
        cats = obj.categories.all()
        return ', '.join([c.name for c in cats]) if cats else '—'
    categories_list.short_description = 'Categories'

    def meets_list(self, obj):
        meets = obj.meets.all()
        return ', '.join([str(m) for m in meets]) if meets else '—'
    meets_list.short_description = 'Meets'

    actions = ['fetch_difficulties', 'clear_categories']

    def fetch_difficulties(self, request, queryset):
        success, failed, skipped = 0, 0, 0
        for problem in queryset:
            if 'kattis.com' in problem.link:
                if problem._fetch_kattis_difficulty():
                    success += 1
                else:
                    failed += 1
            elif 'leetcode.com' in problem.link:
                if problem._fetch_leetcode_difficulty():
                    success += 1
                else:
                    failed += 1
            else:
                skipped += 1
        msg = f"Fetched: {success}"
        if failed:
            msg += f" | Failed: {failed}"
        if skipped:
            msg += f" | Skipped (unknown platform): {skipped}"
        self.message_user(request, msg)
    fetch_difficulties.short_description = "Fetch difficulties for selected problems"

    def clear_categories(self, request, queryset):
        for problem in queryset:
            problem.categories.clear()
        self.message_user(request, f"Cleared categories from {queryset.count()} problems.")
    clear_categories.short_description = "Clear categories from selected problems"


admin.site.register(Problem, ProblemAdmin)
admin.site.register(Session)
