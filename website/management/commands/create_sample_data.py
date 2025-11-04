from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from website.models import Author, Article
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Creates sample data for testing'

    def handle(self, *args, **kwargs):
        # Create an author profile for the superuser
        user = User.objects.first()
        if not Author.objects.filter(user=user).exists():
            author = Author.objects.create(
                user=user,
                bio="Expert in finance and technology with over 10 years of experience.",
                twitter_handle="@fintechrp",
                linkedin_url="https://linkedin.com/in/fintechrp",
                featured=True
            )
            self.stdout.write(self.style.SUCCESS(f'Created author profile for {user.username}'))

        # Create sample articles
        articles_data = [
            {
                'title': 'The Future of Digital Banking in 2026',
                'category': 'finance',
                'summary': 'Exploring the upcoming trends in digital banking and what they mean for consumers.',
                'body': """The banking landscape is rapidly evolving with new technologies and changing consumer preferences. 
                
Key trends we're seeing include:

1. AI-Powered Personal Banking
- Customized financial advice
- Automated portfolio management
- Predictive spending analysis

2. Blockchain Integration
- Faster cross-border transactions
- Enhanced security measures
- Smart contracts implementation

3. Open Banking Evolution
- Third-party service integration
- API-first banking platforms
- Enhanced customer data control

The future of banking is becoming increasingly digital, personalized, and secure."""
            },
            {
                'title': 'Emerging Real Estate Markets in Tech Hubs',
                'category': 'real_estate',
                'summary': 'Analysis of growing real estate opportunities in emerging technology centers.',
                'body': """As technology companies expand beyond traditional tech hubs, new real estate opportunities are emerging.

Key Markets:

1. Austin, Texas
- Growing tech presence
- Affordable housing compared to Silicon Valley
- Strong job market

2. Raleigh-Durham, North Carolina
- Research Triangle Park expansion
- University talent pipeline
- Quality of life advantages

3. Nashville, Tennessee
- Growing startup ecosystem
- Lower cost of living
- Cultural attractions

Investment Considerations:
- Commercial office space demand
- Multi-family housing developments
- Infrastructure improvements"""
            },
            {
                'title': 'AI Revolution in Financial Analysis',
                'category': 'technology',
                'summary': 'How artificial intelligence is transforming financial analysis and investment strategies.',
                'body': """Artificial Intelligence is revolutionizing how we analyze financial markets and make investment decisions.

Key Applications:

1. Market Analysis
- Pattern recognition in market data
- Sentiment analysis of news and social media
- Automated trading strategies

2. Risk Assessment
- Real-time risk monitoring
- Fraud detection
- Credit scoring improvements

3. Portfolio Management
- Automated rebalancing
- Tax-loss harvesting
- Custom portfolio optimization

The integration of AI in finance is creating new opportunities while requiring new skills from financial professionals."""
            }
        ]

        for article_data in articles_data:
            if not Article.objects.filter(title=article_data['title']).exists():
                article = Article.objects.create(
                    title=article_data['title'],
                    slug=slugify(article_data['title']),
                    author=Author.objects.first(),
                    category=article_data['category'],
                    summary=article_data['summary'],
                    body=article_data['body'],
                    status='published',
                    is_published=True
                )
                article.tags.add(article_data['category'], 'trends', '2026')
                self.stdout.write(self.style.SUCCESS(f'Created article: {article.title}'))

        self.stdout.write(self.style.SUCCESS('Successfully created sample data'))