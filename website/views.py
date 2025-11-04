from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from .models import ContactMessage, Article, Newsletter
from .forms import ContactForm, NewsletterForm


def home(request):
    """
    Homepage:
    - latest_articles: latest 5 published articles overall
    - *_articles: up to 3 per category for the Topics section
    """
    latest_articles = Article.objects.filter(is_published=True).order_by("-created_at")[:5]

    finance_articles = Article.objects.filter(
        is_published=True, category="finance"
    ).order_by("-created_at")[:3]

    technology_articles = Article.objects.filter(
        is_published=True, category="technology"
    ).order_by("-created_at")[:3]

    real_estate_articles = Article.objects.filter(
        is_published=True, category="real_estate"
    ).order_by("-created_at")[:3]

    trade_articles = Article.objects.filter(
        is_published=True, category="trade"
    ).order_by("-created_at")[:3]

    return render(
        request,
        "website/home.html",
        {
            "latest_articles": latest_articles,
            "finance_articles": finance_articles,
            "technology_articles": technology_articles,
            "real_estate_articles": real_estate_articles,
            "trade_articles": trade_articles,
        },
    )



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


def newsletter_signup(request):
    if request.method == "POST":
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'message': 'Thank you for subscribing!'})
            messages.success(request, 'Thank you for subscribing to our newsletter!')
            return redirect(request.META.get('HTTP_REFERER', 'home'))
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'errors': form.errors})
            messages.error(request, 'Please correct the errors below.')
            return redirect(request.META.get('HTTP_REFERER', 'home'))
    return redirect('home')

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
    elif category_slug == "trade":
        qs = qs.filter(category="trade")
        category_label = "trade"        

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
