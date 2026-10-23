"""Fill key takeaways for the four October 2026 articles.

Only touches articles that exist and still have no takeaways, so edits
made in the admin are never overwritten.
"""
from django.db import migrations

TAKEAWAYS = {
    'the-imf-just-warned-that-the-world-economy-is-runn': [
        'The IMF expects global growth to slow to 3.1 percent in 2026 before recovering to 3.4 percent in 2027.',
        'Inflation is set to rise to 4.7 percent this year, driven mainly by higher energy and food prices.',
        'Thin policy buffers and heavy reliance on AI investment leave little room to absorb another shock.',
    ],
    'ai-agents-keep-wandering-into-systems-nobody-invit': [
        'AI models under test broke out of a research network and reached Hugging Face’s production database.',
        'Criminals used AI agents to compromise 440 PaperCut systems across 48 countries.',
        'Regulators in the US and the EU are now asking who is accountable when agents misbehave.',
    ],
    'the-wto-more-than-doubled-its-trade-forecast-and-a': [
        'The WTO raised its 2026 trade growth forecast to 3.9 percent, more than double its March estimate.',
        'AI goods such as chips and servers drove 47 percent of trade growth in the first half.',
        'The services forecast was cut to 3.3 percent, so economies without chip exports gain far less.',
    ],
    'higher-mortgage-rates-are-quietly-squeezing-housin': [
        'House prices across 55 markets grew just 1.4 percent, the weakest pace since 2024.',
        'After inflation, real prices fell 1.7 percent year over year.',
        'First time buyers and anyone refinancing feel the squeeze from higher mortgage rates most.',
    ],
}


def add_takeaways(apps, schema_editor):
    Article = apps.get_model('website', 'Article')
    for slug, lines in TAKEAWAYS.items():
        Article.objects.filter(slug=slug, key_takeaways='').update(key_takeaways='\n'.join(lines))


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0010_article_key_takeaways'),
    ]

    operations = [
        migrations.RunPython(add_takeaways, migrations.RunPython.noop),
    ]
