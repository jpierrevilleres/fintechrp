from django.contrib import admin
from .models import ContactMessage, Article, Newsletter
import csv
from django.http import HttpResponse


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
