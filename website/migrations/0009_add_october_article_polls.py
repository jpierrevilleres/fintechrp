"""Add reader polls to the four October 2026 articles.

Skips any article that doesn't exist (e.g. a fresh dev database) or that
already has a poll, so it is safe to run anywhere. Polls are edited in the
admin afterwards like any other.
"""
from django.db import migrations

POLLS = {
    'the-imf-just-warned-that-the-world-economy-is-runn': (
        'How prepared is your budget for another jump in energy and food prices?',
        ['Well prepared, I have a buffer', 'Somewhat, it would hurt', 'Not prepared at all'],
    ),
    'ai-agents-keep-wandering-into-systems-nobody-invit': (
        'Does your organization know which AI tools hold access credentials?',
        ['Yes, we track them', 'Partly', 'No idea'],
    ),
    'the-wto-more-than-doubled-its-trade-forecast-and-a': (
        'How exposed is your business to the AI hardware boom?',
        ['Heavily', 'Somewhat', 'Not at all', 'Not sure'],
    ),
    'higher-mortgage-rates-are-quietly-squeezing-housin': (
        'Would your budget survive a mortgage payment one percentage point higher?',
        ['Yes, comfortably', 'Only just', 'No', 'I do not have a mortgage'],
    ),
}


def add_polls(apps, schema_editor):
    Article = apps.get_model('website', 'Article')
    Poll = apps.get_model('website', 'Poll')
    PollOption = apps.get_model('website', 'PollOption')
    for slug, (question, options) in POLLS.items():
        article = Article.objects.filter(slug=slug).first()
        if article is None or Poll.objects.filter(article=article).exists():
            continue
        poll = Poll.objects.create(article=article, question=question)
        for order, text in enumerate(options):
            PollOption.objects.create(poll=poll, text=text, order=order)


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0008_like_session_key'),
    ]

    operations = [
        migrations.RunPython(add_polls, migrations.RunPython.noop),
    ]
