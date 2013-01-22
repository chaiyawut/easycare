#-*-coding: utf-8 -*-
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""	

from django.test import TestCase

class CallHandlerTest(TestCase):

	def test_voice_path(self):
		"Voice path should be exist"
		from frontend.handlers.call import VOICE_PATH
		import os
		self.assertTrue(os.path.exists(VOICE_PATH))


class SMSHandlerTest(TestCase):
	fixtures = ['frontend.json',]

	def setUp(self):
		from frontend.handlers.chat import ChatHandler
		self.handler = ChatHandler("+66860216060", "p2 w55.5 bp120/80 l500mg2.5")

	def test_initial_chat_handler(self):
		"Chat handler should be initial with patient's number and recieived text message"
		from frontend.models import *
		self.assertEqual(self.handler.get_contact_number(), "0860216060")
		self.assertEqual(self.handler.get_patient(), Patient.objects.get(contact_number='0860216060'))
		self.assertEqual(self.handler.get_period(), 'afternoon')
		self.assertEqual(self.handler.get_weight(), {'weight':'55.5'})
		self.assertEqual(self.handler.get_pressure(), {'up':'120', 'down':'80'})
		self.assertEqual(self.handler.get_drug(), {'name':'lasix', 'size':'500', 'amount':'2.5'})
