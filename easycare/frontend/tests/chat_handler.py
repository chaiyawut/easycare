#-*-coding: utf-8 -*-
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""	

from django.test import TestCase
from frontend.models import Patient, Weight, Pressure, Drug
from django.contrib.auth.models import User
from frontend.handlers import ChatHandler
from frontend.utils.words import *


class SMSHandlerTest(TestCase):
	fixtures = ['frontend.json',]

	def setUp(self):
		self.user = User.objects.create_user('easycall', 'easycall@thevcgroup.com', 'powerall')

	def test_save_record_from_sms(self):
		received_number = "+66860216060"
		received_body = "p1 w55.5 bp120/80 l500mg1.5"
		handler = ChatHandler(received_number, received_body)
		contact_number = handler.get_contact_number()
		patient = handler.get_patient()
		period = handler.get_period()
		storeNumber = Patient.objects.all().values_list('contact_number', flat=True)
		if contact_number in storeNumber and period:
			weight = handler.get_weight()
			pressure = handler.get_pressure()
			drug = handler.get_drug()
			if weight and period in patient.get_today_submitted_periods(entry='weight'):
				messages = ["ท่านได้ส่งข้อมูลน้ำหนักของช่วงเวลานี้แล้ว"]
			elif pressure and period in patient.get_today_submitted_periods(entry='pressure'):
				messages = ["ท่านได้ส่งข้อมูลความดันของช่วงเวลานี้แล้ว"]
			elif drug and period in patient.get_today_submitted_periods(entry='drug'):
				messages =  ["ท่านได้ส่งข้อมูลยาของช่วงเวลานี้แล้ว"]
			elif not weight and not pressure and not drug:
				messages =  ["ผิดพลาด ท่านไม่ได้ใส่ข้อมูลเลย กรุณาใส่ข้อมูล"]
			else:
				record = patient.create_new_record()
				entry_messages = "p:" + PERIODS[period] + " "
				if weight:
					weight_entry = record.create_entry_for_record_from_voip(period, weight=weight)
					entry_messages = entry_messages + "w" + str(weight_entry.weight) + " "
				if pressure:
					pressure_entry = record.create_entry_for_record_from_voip(period, pressure=pressure)
					entry_messages = entry_messages + "bp" + str(pressure_entry.up)+"/"+ str(pressure_entry.down) + " "
				if drug:
					drug_entry = record.create_entry_for_record_from_voip(period, drug=drug)
					entry_messages = entry_messages + "l" + str(drug_entry.size)+"mg"+ str(drug_entry.amount) + " "
				messages =  ["บันทึกข้อมูล " + entry_messages, "หมายเลขอ้างอิง = " + str(record.id)]
		elif not period:
			messages =  ["ท่านระบุช่วงเวลาไม่ถูกต้อง"]
		elif not contact_number in storeNumber:
			messages =  ["เบอร์ของท่านไม่ได้ลงทะเบียนในระบบ"]
		self.assertIsInstance(weight_entry, Weight)
		self.assertEqual(weight_entry.weight, '55.5')
		self.assertIsInstance(pressure_entry, Pressure)
		self.assertEqual(pressure_entry.up, '120')
		self.assertEqual(pressure_entry.down, '80')
		self.assertIsInstance(drug_entry, Drug)
		self.assertEqual(drug_entry.name, 'lasix')
		self.assertEqual(drug_entry.size, '500')
		self.assertEqual(drug_entry.amount, '1.5')

	def test_save_record_from_sms_with_no_entry(self):
		received_number = "+66860216060"
		received_body = "p1 "
		handler = ChatHandler(received_number, received_body)
		contact_number = handler.get_contact_number()
		patient = handler.get_patient()
		period = handler.get_period()
		storeNumber = Patient.objects.all().values_list('contact_number', flat=True)
		if contact_number in storeNumber and period:
			weight = handler.get_weight()
			pressure = handler.get_pressure()
			drug = handler.get_drug()
		self.assertTrue(not weight and not pressure and not drug)

	def test_save_record_from_sms_with_missing_entry(self):
		received_number = "+66860216060"
		received_body = "p1 w55.5 l500mg1.5"
		handler = ChatHandler(received_number, received_body)
		contact_number = handler.get_contact_number()
		patient = handler.get_patient()
		period = handler.get_period()
		storeNumber = Patient.objects.all().values_list('contact_number', flat=True)
		if contact_number in storeNumber and period:
			weight = handler.get_weight()
			pressure = handler.get_pressure()
			drug = handler.get_drug()
		self.assertTrue(not pressure)

	def test_save_record_from_sms_with_missing_period(self):
		received_number = "+66860216060"
		received_body = "w55.5 l500mg1.5"
		handler = ChatHandler(received_number, received_body)
		contact_number = handler.get_contact_number()
		patient = handler.get_patient()
		period = handler.get_period()
		storeNumber = Patient.objects.all().values_list('contact_number', flat=True)
		self.assertIsNone(period)
		self.assertFalse(contact_number in storeNumber and period)

	def test_save_record_from_sms_with_invalid_contact_number(self):
		received_number = "+66860060"
		received_body = "p1 w55.5 l500mg1.5"
		handler = ChatHandler(received_number, received_body)
		contact_number = handler.get_contact_number()
		patient = handler.get_patient()
		period = handler.get_period()
		storeNumber = Patient.objects.all().values_list('contact_number', flat=True)
		self.assertNotIn(contact_number, storeNumber)
