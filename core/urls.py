from django.contrib import admin
from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from website.sitemaps import ArticleSitemap, StaticSitemap

sitemaps = {
   'articles': ArticleSitemap,
   'static': StaticSitemap,
}

urlpatterns = [
# Use a custom admin URL for security in development to mirror production
    path("control-panel-72d3/", admin.site.urls),
    # Keep the default admin path commented out to avoid exposing it unintentionally
#    path("admin/", admin.site.urls),  # default (commented out)
    path('ckeditor/', include('ckeditor_uploader.urls')),
    
    # SEO
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    
    # Main app
    path("", include("website.urls")),
]

# Serve media files in development
# if settings.DEBUG:
#    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
