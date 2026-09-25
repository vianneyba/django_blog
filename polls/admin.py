from django.contrib import admin
from .models import Poll, PollChoice, PollResponse


class PollChoiceInline(admin.TabularInline):
    model = PollChoice
    extra = 3


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ("slug", "question_short", "poll_type", "is_active",
                    "created_at", "total_votes_display")
    list_filter = ("poll_type", "is_active", "require_login")
    search_fields = ("slug", "question")
    prepopulated_fields = {"slug": ("question",)}
    inlines = [PollChoiceInline]

    def question_short(self, obj):
        return obj.question[:60]
    question_short.short_description = "Question"

    def total_votes_display(self, obj):
        return obj.total_votes()
    total_votes_display.short_description = "Votes"


@admin.register(PollResponse)
class PollResponseAdmin(admin.ModelAdmin):
    list_display = ("poll", "choice", "user", "created_at", "ip_address")
    list_filter = ("poll",)
    search_fields = ("free_text", "user__username")
    readonly_fields = ("created_at", "ip_address", "session_key")