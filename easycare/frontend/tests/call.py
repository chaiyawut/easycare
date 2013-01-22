#-*-coding: utf-8 -*-
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""	

from django.test import TestCase
from frontend.models import Patient, Weight, Pressure, Drug
from django.contrib.auth.models import User
from frontend.handlers import CallHandler
from frontend.utils.words import *


class CallHandlerTest(TestCase):
	fixtures = ['frontend.json',]

	def setUp(self):
		self.user = User.objects.create_user('easycall', 'easycall@thevcgroup.com', 'powerall')

	

