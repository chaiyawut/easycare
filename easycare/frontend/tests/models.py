#-*-coding: utf-8 -*-
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""	

from django.test import TestCase

class PatientModelTestCase(TestCase):
	fixtures = ['frontend.json',]

	def setUp(self):
		from frontend.models import *
		import datetime
		self.patient = Patient.objects.get(contact_number='0860216060')
		self.record = Record.objects.create(
			patient = self.patient,
			datetime = datetime.datetime.now(),
			period = 'morning',
			submitted_by = 'sms',
		)

	def test_get_full_name(self):
		"Should has attribute fullname correctly"
		self.assertEqual(self.patient.fullname, u"ชยวุฒิ สุกปลั่ง")

	def test_no_duplicate_period(self):
		"Should return true when has no duplicate period"
		self.assertTrue(self.patient.check_for_no_duplicate_period('afternoon'))

	def test_duplicate_period(self):
		"Should return false when has duplicate period"
		self.assertFalse(self.patient.check_for_no_duplicate_period('morning'))

	def test_create_new_record(self):
		"Should create new record with patient id"
		from frontend.models import Record
		record = self.patient.create_new_record('afternoon', 'ivr')
		self.assertIsInstance(record, Record)
		self.assertEqual(record.patient, self.patient)
		self.assertEqual(record.period, 'afternoon')
		self.assertEqual(record.submitted_by, 'ivr')


class RecordModelTestCase(TestCase):
	fixtures = ['frontend.json',]

	def setUp(self):
		from frontend.models import *
		import datetime
		self.patient = Patient.objects.get(contact_number='0860216060')
		self.record = Record.objects.create(
			patient = self.patient,
			datetime = datetime.datetime.now(),
			period = 'morning',
			submitted_by = 'sms',
		)

	def test_change_status(self):
		"Should change record's status to what specify"
		self.record.change_status('ลบ')
		self.assertEqual(self.record.status, 'ลบ')

	def test_create_entry_for_record_from_voip(self):
		"Should create entry for record for what specify"
		from frontend.models import *
		weight = self.record.create_entry_for_record_from_voip(weight={'weight':'55.6'})
		self.assertIsInstance(weight, Weight)
		self.assertEqual(weight.weight, '55.6')
		drug = self.record.create_entry_for_record_from_voip(drug={'name':'lasix', 'size':'500','amount':'2.5'})
		self.assertIsInstance(drug, Drug)
		self.assertEqual(drug.name, 'lasix')
		self.assertEqual(drug.size, '500')
		self.assertEqual(drug.amount, '2.5')
		entry = self.record.create_entry_for_record_from_voip(pressure={'up':'120','down':'80'})
		self.assertIsInstance(entry, Pressure)
		self.assertEqual(entry.up, '120')
		self.assertEqual(entry.down, '80')

	def create_entry_for_record_from_web(self):

		#need to do form and graph test

		pass




