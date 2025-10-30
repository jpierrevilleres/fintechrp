from django.contrib import admin
from .models import ContactMessage, Article


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
