from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, Http404
from django.contrib import messages
from .models import ContactMessage, Article, Newsletter, Comment, Like
from .forms import ContactForm, NewsletterForm, CommentForm


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

from django.db.models import Q


def article_list(request, category_slug=None):
    """
    Show all published articles.
    If a category is in the URL, filter by that category only.
    """
    qs = Article.objects.filter(is_published=True)
    category_label = "All"

    # Search support: ?q=search+terms
    q = request.GET.get('q')
    if q:
        q = q.strip()
        if q:
            qs = qs.filter(
                Q(title__icontains=q)
                | Q(summary__icontains=q)
                | Q(body__icontains=q)
                | Q(tags__name__icontains=q)
            ).distinct()

    # Normalize incoming category slug so both hyphen and underscore
    # versions work (e.g. 'real-estate' or 'real_estate'). Then map
    # to the Article.category internal value and a human-friendly label.
    if category_slug:
        normalized = category_slug.replace("-", "_")
        allowed = {
            "finance": "Finance",
            "technology": "Technology",
            "real_estate": "Real Estate",
            "trade": "Trade",
        }
        if normalized in allowed:
            qs = qs.filter(category=normalized)
            category_label = allowed[normalized]

    return render(request, "website/article_list.html", {
        "articles": qs,
        "category_label": category_label,
        "q": q,
    })


def article_detail(request, slug):
    """
    Show one article by slug.
    """
    article = get_object_or_404(Article, slug=slug, is_published=True)
    # prepare comment form and approved comments
    comment_form = CommentForm()
    approved_comments = article.comments.filter(is_approved=True)

    # determine whether current visitor has liked this article
    user_liked = False
    if request.user.is_authenticated:
        user_liked = article.likes.filter(user=request.user).exists()
    else:
        ip = request.META.get('REMOTE_ADDR')
        if ip:
            user_liked = article.likes.filter(ip_address=ip).exists()

    # compute absolute article url for share links (avoid calling methods in templates)
    try:
        article_url = request.build_absolute_uri(article.get_absolute_url())
    except Exception:
        article_url = request.build_absolute_uri()

    return render(request, "website/article_detail.html", {
        "article": article,
        "comment_form": comment_form,
        "comments": approved_comments,
        "user_liked": user_liked,
        "article_url": article_url,
    })


def submit_comment(request, slug):
    """Handle comment form POST for an article."""
    article = get_object_or_404(Article, slug=slug, is_published=True)
    if request.method != 'POST':
        return redirect(article.get_absolute_url())
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.article = article
        if request.user.is_authenticated:
            comment.user = request.user
            # auto-approve staff comments
            if request.user.is_staff:
                comment.is_approved = True
        comment.save()
        messages.success(request, 'Thanks — your comment was submitted.' + (
            ' It will appear once approved.' if not comment.is_approved else ''))
    else:
        messages.error(request, 'Please correct the errors in the comment form.')
    return redirect(article.get_absolute_url() + '#comments')


def toggle_like(request, slug):
    """AJAX endpoint to toggle like for an article. Returns JSON with new count."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    article = get_object_or_404(Article, slug=slug, is_published=True)
    user = request.user if request.user.is_authenticated else None
    ip = request.META.get('REMOTE_ADDR')

    liked = False
    if user:
        like = Like.objects.filter(article=article, user=user).first()
        if like:
            like.delete()
            liked = False
        else:
            Like.objects.create(article=article, user=user)
            liked = True
    else:
        # fallback to IP-based likes for anonymous users
        like = Like.objects.filter(article=article, ip_address=ip).first()
        if like:
            like.delete()
            liked = False
        else:
            Like.objects.create(article=article, ip_address=ip)
            liked = True

    return JsonResponse({'liked': liked, 'likes_count': article.likes.count()})

# ...existing code...

def policy_page(request, policy_type):
    """
    Render the appropriate policy template based on policy_type.
    Accepts 'privacy', 'terms', or 'cookie'. Raises 404 for unknown types.
    """
    template_map = {
        'privacy': 'website/privacy-policy.html',
        'terms': 'website/terms-of-service.html',
        'cookie': 'website/cookie-policy.html',
    }
    template = template_map.get(policy_type)
    if not template:
        raise Http404("Policy not found")
    return render(request, template, {'policy_type': policy_type})

# ...existing code...

# test_view removed during cleanup