#-*-coding: utf-8 -*-
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""	

from django.test import TestCase

class WordTestCase(TestCase):

	def test_convert_word_name(self):
		"Word should convert collectly"
		from frontend.utils.words import *
		self.assertEqual(PERIODS['morning'], "เช้า")
		self.assertEqual(PERIODS['afternoon'], "กลางวัน")
		self.assertEqual(PERIODS['evening'], "เย็น")
		self.assertEqual(NUMS_TO_PERIODS['1'], "morning")
		self.assertEqual(NUMS_TO_PERIODS['2'], "afternoon")
		self.assertEqual(NUMS_TO_PERIODS['3'], "evening")
		self.assertEqual(DRUG_NAMES['l'], "lasix")
		
