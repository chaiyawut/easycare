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
		self.Log = Log
		self.today = datetime.date.today()
		self.first = datetime.date(day=1, month=self.today.month, year=self.today.year)
		self.lastMonth = self.first - datetime.timedelta(days=10)

	def test_no_log(self):
		"Should return new month log"
		log = self.Log.update_month_log('sms')
		self.assertEqual(log.created.month, self.today.month)
		self.assertEqual(log.created.year, self.today.year)
		self.assertEqual(log.sms_count, 1)
		log = self.Log.update_month_log('email')
		self.assertEqual(log.created.month, self.today.month)
		self.assertEqual(log.created.year, self.today.year)
		self.assertEqual(log.email_count, 1)

	def test_log_exist(self):
		"Should return existing month log increment by 1"
		self.Log.objects.create(sms_count=3, email_count=3)
		log = self.Log.update_month_log('sms')
		self.assertEqual(log.created.month, self.today.month)
		self.assertEqual(log.created.year, self.today.year)
		self.assertEqual(log.sms_count, 4)
		log = self.Log.update_month_log('email')
		self.assertEqual(log.created.month, self.today.month)
		self.assertEqual(log.created.year, self.today.year)
		self.assertEqual(log.email_count, 4)

	def test_log_not_exist(self):
		"Should return new month log"
		self.Log.objects.create(created=self.lastMonth)
		log = self.Log.update_month_log('sms')
		self.assertEqual(log.created.month, self.today.month)
		self.assertEqual(log.created.year, self.today.year)
		self.assertEqual(log.sms_count, 1)
		log = self.Log.update_month_log('email')
		self.assertEqual(log.created.month, self.today.month)
		self.assertEqual(log.created.year, self.today.year)
		self.assertEqual(log.email_count, 1)

	def test_log_exist_add_both(self):
		"Should increment both email and sms value"
		self.Log.objects.create(sms_count=3, email_count=3)
		log = self.Log.update_month_log('both')
		self.assertEqual(log.created.month, self.today.month)
		self.assertEqual(log.created.year, self.today.year)
		self.assertEqual(log.sms_count, 4)
		self.assertEqual(log.email_count, 4)

