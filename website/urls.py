from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("newsletter/signup/", views.newsletter_signup, name="newsletter_signup"),

    # article list pages
    path("articles/", views.article_list, name="article_list"),
    path("articles/<slug:category_slug>/", views.article_list, name="article_list_by_category"),

    # single article
    path("article/<slug:slug>/", views.article_detail, name="article_detail"),
]
