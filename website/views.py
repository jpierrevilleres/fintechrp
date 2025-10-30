from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import ContactMessage, Article
from .forms import ContactForm


def home(request):
    # show latest 5 published articles on the home page
    latest_articles = Article.objects.filter(is_published=True)[:5]
    return render(request, "website/home.html", {
        "latest_articles": latest_articles
    })


def about(request):
    return render(request, "website/about.html")


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, "website/contact_thanks.html")
    else:
        form = ContactForm()
    return render(request, "website/contact.html", {"form": form})


def article_list(request, category_slug=None):
    """
    Show all published articles.
    If a category is in the URL, filter by that category only.
    """
    qs = Article.objects.filter(is_published=True)
    category_label = "All"

    if category_slug == "finance":
        qs = qs.filter(category="finance")
        category_label = "Finance"
    elif category_slug == "technology":
        qs = qs.filter(category="technology")
        category_label = "Technology"
    elif category_slug == "real-estate":
        qs = qs.filter(category="real_estate")
        category_label = "Real Estate"

    return render(request, "website/article_list.html", {
        "articles": qs,
        "category_label": category_label,
    })


def article_detail(request, slug):
    """
    Show one article by slug.
    """
    article = get_object_or_404(Article, slug=slug, is_published=True)
    return render(request, "website/article_detail.html", {
        "article": article
    })
