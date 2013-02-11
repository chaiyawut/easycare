#-*-coding: utf-8 -*-
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""	

from django.test import TestCase

class GraphTest(TestCase):
	
	def test_voice_path(self):
		"Voice path should be exist"
		from frontend.handlers.call import VOICE_PATH
		import os
		self.assertTrue(os.path.exists(VOICE_PATH))

