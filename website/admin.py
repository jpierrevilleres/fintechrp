from django import forms
from django.contrib import admin
from .models import ContactMessage, Article, Newsletter, Poll, PollOption
import csv
from django.http import HttpResponse


class PollInlineForm(forms.ModelForm):
    """Edit a poll's options as one textarea (one option per line) instead
    of a nested inline, which the Django admin doesn't support."""

    options_text = forms.CharField(
        label="Options",
        widget=forms.Textarea(attrs={"rows": 4}),
        help_text="One option per line, 2 to 6 options. Renaming an option resets its votes.",
    )

    class Meta:
        model = Poll
        fields = ("question", "is_active")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["options_text"].initial = "\n".join(
                o.text for o in self.instance.options.all()
            )

    def clean_options_text(self):
        lines = [line.strip() for line in self.cleaned_data["options_text"].splitlines()]
        lines = list(dict.fromkeys(line for line in lines if line))
        if not 2 <= len(lines) <= 6:
            raise forms.ValidationError("Enter between 2 and 6 options, one per line.")
        if any(len(line) > 200 for line in lines):
            raise forms.ValidationError("Each option must be 200 characters or fewer.")
        return lines

    def save(self, commit=True):
        poll = super().save(commit=commit)
        if commit:
            self._sync_options(poll)
        else:
            original_save_m2m = self.save_m2m

            def save_m2m():
                original_save_m2m()
                self._sync_options(poll)

            self.save_m2m = save_m2m
        return poll

    def _sync_options(self, poll):
        # Match by text so unchanged options keep their vote counts
        lines = self.cleaned_data["options_text"]
        existing = {o.text: o for o in poll.options.all()}
        for order, text in enumerate(lines):
            option = existing.pop(text, None) or PollOption(poll=poll, text=text)
            option.order = order
            option.save()
        for leftover in existing.values():
            leftover.delete()


class PollInline(admin.StackedInline):
    model = Poll
    form = PollInlineForm
    extra = 0
    max_num = 1
    verbose_name = "Reader poll"
    verbose_name_plural = "Reader poll (optional, shown at the end of the article)"


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "created_at")
    search_fields = ("name", "email", "message")
    readonly_fields = ("created_at",)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "created_at", "is_published")
    list_filter = ("category", "is_published", "created_at")
    search_fields = ("title", "summary", "body")
    prepopulated_fields = {"slug": ("title",)}  # auto fill slug based on title
    ordering = ("-created_at",)
    inlines = [PollInline]


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ("email", "name", "subscribed_at", "is_active")
    list_filter = ("is_active", "subscribed_at")
    search_fields = ("email", "name")
    readonly_fields = ("subscribed_at",)
    actions = ["export_as_csv", "mark_active", "mark_inactive"]

    def export_as_csv(self, request, queryset):
        """Export selected newsletter subscribers as CSV."""
        meta = self.model._meta
        field_names = ["email", "name", "subscribed_at", "is_active"]

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f"attachment; filename=subscribers_{request.user.username}.csv"

        writer = csv.writer(response)
        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, f) for f in field_names])
        return response

    export_as_csv.short_description = "Export selected subscribers as CSV"

    def mark_active(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, "Selected subscribers marked active.")

    mark_active.short_description = "Mark selected as active"

    def mark_inactive(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, "Selected subscribers marked inactive.")

    mark_inactive.short_description = "Mark selected as inactive"
