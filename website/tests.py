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
