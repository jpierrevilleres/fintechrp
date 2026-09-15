from django.contrib.syndication.views import Feed
from django.urls import reverse
from django.utils.feedgenerator import Atom1Feed

from .models import Article


class LatestArticlesFeed(Feed):
    title = "FinTechRP - Latest Articles"
    description = "Latest finance, technology, real estate and trade insights from FinTechRP."

    def link(self):
        return reverse("article_list")

    def items(self):
        return Article.objects.filter(is_published=True).order_by("-created_at")[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.summary or item.body

    def item_link(self, item):
        return item.get_absolute_url()

    def item_pubdate(self, item):
        return item.created_at

    def item_categories(self, item):
        return [item.get_category_display()]

    def item_author_name(self, item):
        if not item.author:
            return "FinTechRP"
        return item.author.user.get_full_name() or item.author.user.username


class LatestArticlesAtomFeed(LatestArticlesFeed):
    feed_type = Atom1Feed
    subtitle = LatestArticlesFeed.description
