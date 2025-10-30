from django.db import models


class ContactMessage(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email} - {self.created_at:%Y-%m-%d %H:%M}"


class Article(models.Model):
    CATEGORY_CHOICES = [
        ("finance", "Finance"),
        ("technology", "Technology"),
        ("real_estate", "Real Estate"),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, help_text="URL text. Example: 'fed-rate-outlook-2025'")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    summary = models.TextField(help_text="Short teaser or preview paragraph", blank=True)
    body = models.TextField(help_text="Full article content")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]  # newest first

    def __str__(self):
        return self.title
