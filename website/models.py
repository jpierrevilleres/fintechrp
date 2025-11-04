from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from taggit.managers import TaggableManager
from ckeditor_uploader.fields import RichTextUploadingField


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField()
    profile_image = models.ImageField(upload_to='authors/', blank=True)
    twitter_handle = models.CharField(max_length=50, blank=True)
    linkedin_url = models.URLField(blank=True)
    website = models.URLField(blank=True)
    featured = models.BooleanField(default=False)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    def get_absolute_url(self):
        return reverse('author_detail', kwargs={'pk': self.pk})


class Article(models.Model):
    CATEGORY_CHOICES = [
        ("finance", "Finance"),
        ("technology", "Technology"),
        ("real_estate", "Real Estate"),
         ("trade", "Trade"),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('premium', 'Premium'),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, help_text="URL text. Example: 'fed-rate-outlook-2025'")
    author = models.ForeignKey(Author, on_delete=models.PROTECT, related_name='articles', null=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    tags = TaggableManager()
    summary = models.TextField(help_text="Short teaser or preview paragraph", blank=True)
    body = RichTextUploadingField(help_text="Full article content")
    featured_image = models.ImageField(upload_to='articles/%Y/%m/', blank=True)
    meta_description = models.CharField(max_length=160, blank=True, help_text="SEO meta description")
    meta_keywords = models.CharField(max_length=255, blank=True, help_text="SEO keywords (comma-separated)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    read_time = models.PositiveIntegerField(default=0, help_text="Estimated reading time in minutes")
    view_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]





class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['article', 'created_at']),
        ]

    def __str__(self):
        return f'Comment by {self.name} on {self.article}'


class Newsletter(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    interests = models.JSONField(default=dict, help_text="Subscriber's topic interests")

    def __str__(self):
        return self.email


class ContactMessage(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=200, default='Contact Form Message')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.subject} - {self.created_at:%Y-%m-%d %H:%M}"


class Sponsor(models.Model):
    name = models.CharField(max_length=200)
    website = models.URLField()
    logo = models.ImageField(upload_to='sponsors/')
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    contact_email = models.EmailField()
    contact_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class SponsoredContent(models.Model):
    sponsor = models.ForeignKey(Sponsor, on_delete=models.CASCADE)
    article = models.OneToOneField(Article, on_delete=models.CASCADE)
    campaign_start = models.DateField()
    campaign_end = models.DateField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.sponsor.name} - {self.article.title}"
