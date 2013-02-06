#-*-coding: utf-8 -*-
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""	

from django.test import TestCase

class LogTestCase(TestCase):
	fixtures = ['frontend.json',]

	def setUp(self):
		from frontend.models import Log
		import datetime
		from django.utils import timezone
		now = datetime.datetime.now().replace(tzinfo=timezone.get_default_timezone())
		self.Log = Log
		self.today = now.date()
		self.first = datetime.date(day=1, month=self.today.month, year=self.today.year)
		self.lastMonth = self.first - datetime.timedelta(days=10)

	def test_no_log(self):
		"It should return new month log when no log entry"
		log = self.Log.update_month_log('sms')
		self.assertEqual(log.created.month, self.today.month)
		self.assertEqual(log.created.year, self.today.year)
		self.assertEqual(log.sms_count, 1)
		log = self.Log.update_month_log('email')
		self.assertEqual(log.created.month, self.today.month)
		self.assertEqual(log.created.year, self.today.year)
		self.assertEqual(log.email_count, 1)

	def test_log_exist(self):
		"It should return existing month log and increment by 1"
		self.Log.objects.create(sms_count=3, email_count=3)
		log = self.Log.update_month_log('sms')
		self.assertEqual(log.created.month, self.today.month)
		self.assertEqual(log.created.year, self.today.year)
		self.assertEqual(log.sms_count, 4)
		log = self.Log.update_month_log('email')
		self.assertEqual(log.created.month, self.today.month)
		self.assertEqual(log.created.year, self.today.year)
		self.assertEqual(log.email_count, 4)

	def test_log_last_month(self):
		"It should return new month log when entering new month"
		self.Log.objects.create(created=self.lastMonth)
		log = self.Log.update_month_log('sms')
		self.assertEqual(log.created.month, self.today.month)
		self.assertEqual(log.created.year, self.today.year)
		self.assertEqual(log.sms_count, 1)
		log = self.Log.update_month_log('email')
		self.assertEqual(log.created.month, self.today.month)
		self.assertEqual(log.created.year, self.today.year)
		self.assertEqual(log.email_count, 1)

	def test_add_both(self):
		"It should increment both email and sms value when using both"
		self.Log.objects.create(sms_count=3, email_count=3)
		log = self.Log.update_month_log('both')
		self.assertEqual(log.created.month, self.today.month)
		self.assertEqual(log.created.year, self.today.year)
		self.assertEqual(log.sms_count, 4)
		self.assertEqual(log.email_count, 4)

