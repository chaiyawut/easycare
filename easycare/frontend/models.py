#-*-coding: utf-8 -*-
from django.db import models
import datetime
from pytz import timezone
from django.contrib.auth.models import User
from django.core.mail import send_mail, BadHeaderError
import os


CONFIRM_BY = (
	('email', 'อีเมลล์'),
	('sms', 'เอสเอ็มเอส'),
	('both', 'อีเมลล์ & เอสเอ็มเอส'),
)

PEROIDS = (
	('morning', 'เช้า'),
	('afternoon', 'กลางวัน'),
	('evening', 'เย็น'),
)

DRUGS = (
	('lasix', 'ลาซิก'),
	('belsid', 'เบลซิด'),
)

DRUG_SIZES = (
	(40, '40 มิลิกรัม'),
	(500, '500 มิลิกรัม'),
)

DRUG_AMOUNTS = (
	(0.5, '0.5 เม็ด'),
	(1, '1 เม็ด'),
	(1.5, '1.5 เม็ด'),
	(2, '2 เม็ด'),
	(2.5, '2.5 เม็ด'),
	(3, '3 เม็ด'),
	(3.5, '3.5 เม็ด'),
	(4, '4 เม็ด'),
	(4.5, '4.5 เม็ด'),
	(5, '5 เม็ด'),
)

def get_file_path(instance, filename):
	path = 'voices/sounds_for_name/'
	format = instance.hn  + ".wav"
	return os.path.join(path, format)

class Patient(models.Model):
	hn = models.CharField(unique=True, max_length=200, verbose_name='หมายเลขผู้ป่วยนอก')
	contact_number = models.CharField(unique=True, max_length=200, verbose_name='หมายเลขติดต่อ')
	firstname = models.CharField(blank=True ,max_length=200, verbose_name='ชื่อ')
	lastname = models.CharField(blank=True, max_length=200, verbose_name='นามสกุล')
	email = models.CharField(blank=True, unique=True, max_length=200, verbose_name='อีเมลล์ติดต่อ')
	confirm_by = models.CharField(max_length=200, choices=CONFIRM_BY, verbose_name='ติดต่อโดย')
	sound_for_name = models.FileField(upload_to=get_file_path, verbose_name='ไฟล์เสียงสำหรับชื่อคนไข้')

	def __unicode__(self):
		return self.hn+" "+self.fullname

	def send_email(self, subject, message):
		send_mail(subject, message, 'easycare.sit@gmail.com',[self.email], fail_silently=False)

	def _get_full_name(self):
		return self.firstname+" "+self.lastname
	fullname = property(_get_full_name)

	class Meta:
		verbose_name_plural = "1. ผู้ป่วย"
		verbose_name = "ผู้ป่วย"

	def check_for_no_duplicate_period_in_formset(self, entry, field_name, formset):
		today_submitted_periods = self.get_today_submitted_periods(entry)
		for form in formset:
			if form.cleaned_data[field_name] != None and form.cleaned_data['period'] in today_submitted_periods:
				return False, "ท่านได้ส่ง"+ str(form._meta.model._meta.verbose_name) +"สำหรับช่วงเวลา" + dict(PEROIDS)[form.cleaned_data['period']] + "แล้ว"
		return True, ""

	def get_today_submitted_periods(self, entry):
		submitted_records = self.record_set.filter( datetime__gte=datetime.date.today()).exclude(response__deleted=True)
		today_submitted_periods = []
		for record in submitted_records:
			if entry == 'weight':
				periods = record.weight_set.values_list('period', flat=True)
			elif entry == 'pressure':
				periods = record.pressure_set.values_list('period', flat=True)
			elif entry == 'drug':
				periods = record.drug_set.values_list('period', flat=True)
			for period in periods:
				if not period in today_submitted_periods:
					today_submitted_periods.append(period)
		return today_submitted_periods

	def create_new_record(self):
		return self.record_set.create()


class Record(models.Model):
	patient = models.ForeignKey(Patient)
	datetime = models.DateTimeField(default=datetime.datetime.now(), verbose_name='เวลา')
	voicemail = models.CharField(blank=True, max_length=200, verbose_name='ข้อมูลฝากเสียง')
	status = models.CharField(default='รอการตอบกลับ', max_length=200, verbose_name='สถานะ')

	def __unicode__(self):
		return "id: " + str(self.id) + " timestamp: " + str(self.datetime)#.astimezone(timezone('Asia/Bangkok')).strftime("%d/%m/%y %H:%M:%S"))

	class Meta:
		verbose_name_plural = "2. บันทึกรายวัน"
		verbose_name = "บันทึกรายวัน"

	def change_status(self, status):
		self.status = status
		self.save()

	def create_entry_for_record_from_voip(self, period, weight=None, pressure=None, drug=None):
		if weight:
			entry = self.weight_set.create(
				period = period,
				weight = weight['weight']
			)
		elif drug:
			entry = self.drug_set.create(
				name = drug['name'],
				period = period,
				size = drug['size'],
				amount = drug['amount']
			)
		elif pressure:
			entry = self.pressure_set.create(
				period = period,
				up = pressure['up'],
				down = pressure['down']
			)
		return entry


	def create_entry_for_record_from_web(self, entry, formset):
		for form in formset:
			if entry == 'weight' and form.cleaned_data['weight'] != None:
				try:
					self.weight_set.create(
						period = form.cleaned_data['period'],
						weight = form.cleaned_data['weight']
					)
				except Exception, e:
					return None
			elif entry == 'drug' and form.cleaned_data['amount'] != None:
				try:
					self.drug_set.create(
						name = form.cleaned_data['name'],
						period = form.cleaned_data['period'],
						size = form.cleaned_data['size'],
						amount = form.cleaned_data['amount']
					)
				except Exception, e:
					return None
			elif entry == 'pressure' and form.cleaned_data['up'] != None:
				try:
					self.pressure_set.create(
						period = form.cleaned_data['period'],
						up = form.cleaned_data['up'],
						down = form.cleaned_data['down']
					)
				except Exception, e:
					return None
		return True

class Response(models.Model):
	record = models.OneToOneField(Record)
	nurse = models.ForeignKey(User)
	reply_text = models.CharField(blank=True, max_length=200, verbose_name='ข้อความตอบกลับ')
	deleted = models.BooleanField(default=False, verbose_name='ลบ')

	def __unicode__(self):
		return str(self.record.id) +" "+self.nurse.username

	class Meta:
		verbose_name_plural = "3. ตอบกลับบันทึก"
		verbose_name = "ตอบกลับบันทึก"

class RecordElementBase(models.Model):
	record = models.ForeignKey(Record)
	period = models.CharField(max_length=200, choices=PEROIDS, verbose_name='ช่วงเวลา')

	class Meta:
		abstract = True

class Drug(RecordElementBase):
	name = models.CharField(max_length=200, choices=DRUGS, blank=True, null=True, verbose_name='ชื่อยา')
	size = models.IntegerField(choices=DRUG_SIZES, blank=True, null=True, verbose_name='ขนาดยา')
	amount = models.DecimalField(max_digits=2, decimal_places=1, choices=DRUG_AMOUNTS, blank=True, null=True, verbose_name='จำนวนยา')

	def __unicode__(self):
		return "Record: " + str(self.record.id) + " " + self.period + " " + self.name + " " + str(self.size) + " " + str(self.amount)

	class Meta:
		verbose_name_plural = "5. ยา"
		verbose_name = "ยา"

class Pressure(RecordElementBase):
	up = models.IntegerField(blank=True, null=True, verbose_name='ความดันตัวบน')
	down = models.IntegerField(blank=True, null=True, verbose_name='ความดันตัวล่าง')

	def __unicode__(self):
		return "Record: " + str(self.record.id) + " " + self.period + " " + str(self.up) + " " + str(self.down)

	class Meta:
		verbose_name_plural = "6. ความดัน"
		verbose_name = "ความดัน"

class Weight(RecordElementBase):
	weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name='น้ำหนัก')

	def __unicode__(self):
		return "Record: " + str(self.record.id) + " " + self.period + " " + str(self.weight)

	class Meta:
		verbose_name_plural = "4. น้ำหนัก"
		verbose_name = "น้ำหนัก"

