#-*-coding: utf-8 -*-
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""	

from django.test import TestCase

class GraphTest(TestCase):
	fixtures = ['frontend.json',]

	def setUp(self):
		from django.test.client import Client
		from django.contrib.auth.models import User
		self.admin = User.objects.create_superuser('easycare', 'myemail@test.com', 'wmp;ui;y<oN')
		self.c = Client()
	
	def test_weight_graph_no_login(self):
		#It should return redirect to login page when not login
		response = self.c.get('/records/weight_graph/1/')
		self.assertEqual(response.status_code, 302)
		self.assertRedirects(response, '/accounts/login/?next=/records/weight_graph/1/')

	def test_weight_graph_data(self):
		#It should return json object about weight for specific user when logged in
		self.c.login(username='easycare', password='wmp;ui;y<oN')
		response = self.c.get('/records/weight_graph/1/')
		self.assertEqual(response.status_code, 200)
		import json
		data = json.loads(response.content)
		#self.assertEqual(len(data['weights']), 3)
		#self.assertEqual(type(data['weights']['morning']), type([]))
		#self.assertEqual(type(data['weights']['afternoon']), type([]))
		#self.assertEqual(type(data['weights']['evening']), type([]))
