from django.conf import settings
from .models import Article
from taggit.models import Tag

def site_settings(request):
    """Global values to pass to templates"""
    return {
        'SITE_NAME': 'FinTechRP',
        'META_DESCRIPTION': 'Expert insights on Finance, Technology, and Real Estate',
        'CURRENT_YEAR': settings.USE_TZ,
    }

def categories(request):
    """Categories for navigation"""
    return {
        'ARTICLE_CATEGORIES': Article.CATEGORY_CHOICES
    }

def popular_tags(request):
    """Most used tags"""
    return {
        'POPULAR_TAGS': Tag.objects.all()[:10]
    }