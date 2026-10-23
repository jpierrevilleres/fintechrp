from django.test import TestCase
from django.urls import reverse


class PolicyPagesTests(TestCase):
	def test_privacy_policy_renders(self):
		resp = self.client.get(reverse('privacy_policy'))
		self.assertEqual(resp.status_code, 200)
		self.assertContains(resp, 'Privacy Policy')

	def test_terms_policy_renders(self):
		resp = self.client.get(reverse('terms_policy'))
		self.assertEqual(resp.status_code, 200)
		self.assertContains(resp, 'Terms of Service')

	def test_cookie_policy_renders(self):
		resp = self.client.get(reverse('cookie_policy'))
		self.assertEqual(resp.status_code, 200)
		self.assertContains(resp, 'Cookie Policy')


from django.test import override_settings

from website.admin import PollInlineForm
from website.models import Article, Poll, PollOption
from website.templatetags.html_utils import format_article_body


class FormatArticleBodyTests(TestCase):
	def test_legacy_heading_split_into_h2_and_paragraph(self):
		html = '<p dir="ltr"><strong>Who Pays</strong><br />\nThere is a concern.</p>'
		self.assertEqual(
			format_article_body(html),
			'<h2>Who Pays</h2>\n<p dir="ltr">There is a concern.</p>',
		)

	def test_legacy_references_become_collapsible(self):
		html = '<p dir="ltr">References<br />\nWTO. (2026). <a href="https://wto.org">x</a></p>'
		out = format_article_body(html)
		self.assertIn('<details class="fr-references"><summary>References</summary>', out)
		self.assertIn('<a href="https://wto.org">x</a>', out)
		self.assertNotIn('<h2>', out)

	def test_references_div_becomes_collapsible(self):
		out = format_article_body('<div class="fr-references"><p>A</p><p>B</p></div>')
		self.assertEqual(
			out,
			'<details class="fr-references"><summary>References</summary><p>A</p><p>B</p></details>',
		)

	def test_plain_paragraph_and_inline_bold_untouched(self):
		html = '<p>Growth was <strong>3.9 percent</strong> this year.</p>'
		self.assertEqual(format_article_body(html), html)


# The manifest storage used in production needs collectstatic to have run
_PLAIN_STATIC = {
	'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
	'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
}


@override_settings(STORAGES=_PLAIN_STATIC)
class PollTests(TestCase):
	def setUp(self):
		self.article = Article.objects.create(
			title='T', slug='t', category='trade', body='<p>Body</p>', is_published=True,
		)

	def _form(self, options, instance=None):
		data = {'question': 'Q?', 'is_active': True, 'options_text': options}
		form = PollInlineForm(data=data, instance=instance or Poll(article=self.article))
		return form

	def test_admin_form_creates_and_syncs_options_keeping_votes(self):
		form = self._form('Yes\nNo\n\nNo')
		self.assertTrue(form.is_valid(), form.errors)
		poll = form.save()
		self.assertEqual([o.text for o in poll.options.all()], ['Yes', 'No'])

		PollOption.objects.filter(poll=poll, text='Yes').update(votes=5)
		form = self._form('Maybe\nYes', instance=poll)
		self.assertTrue(form.is_valid(), form.errors)
		form.save()
		self.assertEqual(
			[(o.text, o.votes) for o in poll.options.all()],
			[('Maybe', 0), ('Yes', 5)],
		)

	def test_admin_form_requires_two_options(self):
		self.assertFalse(self._form('Only one').is_valid())

	def test_vote_counts_once_per_session(self):
		poll = Poll.objects.create(article=self.article, question='Q?')
		yes = PollOption.objects.create(poll=poll, text='Yes')
		PollOption.objects.create(poll=poll, text='No', order=1)
		url = reverse('vote_poll', kwargs={'slug': 't'})
		ajax = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}

		resp = self.client.post(url, {'option': yes.id}, **ajax)
		self.assertEqual(resp.json()['voted'], yes.id)
		self.assertEqual(resp.json()['total'], 1)
		self.client.post(url, {'option': yes.id}, **ajax)
		yes.refresh_from_db()
		self.assertEqual(yes.votes, 1)

		page = self.client.get(reverse('article_detail', kwargs={'slug': 't'}))
		self.assertContains(page, '100%')
		self.assertNotContains(page, 'fr-poll-option')

	def test_vote_rejects_option_from_another_poll(self):
		Poll.objects.create(article=self.article, question='Q?')
		other_article = Article.objects.create(title='O', slug='o', category='trade', body='x')
		other = PollOption.objects.create(
			poll=Poll.objects.create(article=other_article, question='?'), text='X',
		)
		resp = self.client.post(reverse('vote_poll', kwargs={'slug': 't'}), {'option': other.id})
		self.assertEqual(resp.status_code, 400)

	def test_article_page_shows_poll_buttons_before_voting(self):
		poll = Poll.objects.create(article=self.article, question='Will it last?')
		PollOption.objects.create(poll=poll, text='Yes')
		resp = self.client.get(reverse('article_detail', kwargs={'slug': 't'}))
		self.assertContains(resp, 'Will it last?')
		self.assertContains(resp, 'fr-poll-option')
		self.assertContains(resp, 'Trade')


@override_settings(STORAGES=_PLAIN_STATIC)
class LikeTests(TestCase):
	def setUp(self):
		self.article = Article.objects.create(
			title='T', slug='t', category='trade', body='<p>Body</p>', is_published=True,
		)
		self.url = reverse('toggle_like', kwargs={'slug': 't'})

	def test_anonymous_visitors_like_independently(self):
		# All requests share REMOTE_ADDR, as they do behind the load balancer
		first, second = self.client, self.client_class()
		self.assertTrue(first.post(self.url).json()['liked'])
		resp = second.post(self.url).json()
		self.assertTrue(resp['liked'])
		self.assertEqual(resp['likes_count'], 2)

	def test_second_click_unlikes_and_page_reflects_state(self):
		self.client.post(self.url)
		page = self.client.get(reverse('article_detail', kwargs={'slug': 't'}))
		self.assertTrue(page.context['user_liked'])
		resp = self.client.post(self.url).json()
		self.assertFalse(resp['liked'])
		self.assertEqual(resp['likes_count'], 0)


class OctoberPollsMigrationTests(TestCase):
	def test_adds_poll_once_and_skips_missing_articles(self):
		import importlib
		from django.apps import apps
		migration = importlib.import_module('website.migrations.0009_add_october_article_polls')
		article = Article.objects.create(
			title='W', slug='the-wto-more-than-doubled-its-trade-forecast-and-a',
			category='trade', body='x',
		)
		migration.add_polls(apps, None)
		migration.add_polls(apps, None)
		self.assertEqual(Poll.objects.count(), 1)
		self.assertEqual(article.poll.options.count(), 4)
