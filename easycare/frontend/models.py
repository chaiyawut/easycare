#-*-coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail, BadHeaderError
import os
import datetime
from django.utils import timezone

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
	(0, '0 เม็ด'),
	(0.25, '0.25 เม็ด'),
	(0.5, '0.5 เม็ด'),
	(0.75, '0.75 เม็ด'),
	(1, '1 เม็ด'),
	(1.25, '1.25 เม็ด'),
	(1.5, '1.5 เม็ด'),
	(1.75, '1.75 เม็ด'),
	(2, '2 เม็ด'),
	(2.25, '2.25 เม็ด'),
	(2.5, '2.5 เม็ด'),
	(2.75, '2.75 เม็ด'),
	(3, '3 เม็ด'),
	(3.25, '3.25 เม็ด'),
	(3.5, '3.5 เม็ด'),
	(3.75, '3.75 เม็ด'),
	(4, '4 เม็ด'),
	(4.25, '4.25 เม็ด'),
	(4.5, '4.5 เม็ด'),
	(4.75, '4.75 เม็ด'),
	(5, '5 เม็ด'),
)

SUBMIT_OPTIONS = (
	('sms', 'เอสเอ็มเอส'),
	('web', 'เวปไซด์'),
	('ivr', 'ไอวีอาร์'),
)

VISIT_TYPES = (
	('phone', 'โทรศัพท์'),
	('hospital', 'คลินิก'),
)

def get_file_path(instance, filename):
	path = 'voices/sounds_for_name/'
	format = str(instance.hn).replace('/', '_')  + ".mp3"
	return os.path.join(path, format)

class Patient(models.Model):
	hn = models.CharField(unique=True, max_length=200, verbose_name='หมายเลขผู้ป่วยนอก')
	contact_number = models.CharField(blank=True, unique=True, max_length=200, verbose_name='หมายเลขโทรศัพท์ติดต่อ')
	firstname = models.CharField(max_length=200, verbose_name='ชื่อ')
	lastname = models.CharField(blank=True, max_length=200, verbose_name='นามสกุล')
	age = models.CharField(blank=True, max_length=200, verbose_name='อายุ')
	email = models.CharField(blank=True, max_length=200, verbose_name='อีเมลล์ติดต่อ')
	confirm_by = models.CharField(max_length=200, choices=CONFIRM_BY, verbose_name='ติดต่อผ่านทาง')
	sound_for_name = models.FileField(blank=True, upload_to=get_file_path, verbose_name='ไฟล์เสียงสำหรับชื่อคนไข้')

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

	def check_for_no_duplicate_period(self, period):
		now = timezone.now()
		submitted_periods = self.record_set.filter( datetime__range=(datetime.datetime.combine(now.date(), datetime.time.min).replace(tzinfo=timezone.get_default_timezone()),
                            datetime.datetime.combine(now.date(), datetime.time.max).replace(tzinfo=timezone.get_default_timezone()))).exclude(response__deleted=True).values_list('period', flat=True)
		if period in submitted_periods:
			return False
		return True

	def create_new_record(self, period, submitted_by):
		return self.record_set.create(period=period, submitted_by=submitted_by)

class Visit(models.Model):
	patient = models.ForeignKey(Patient)
	date = models.DateField(verbose_name='วันที่มารับบริการ')
	visit_type = models.CharField(max_length=200, choices=VISIT_TYPES, verbose_name='ประเภทบริการ')

	def __unicode__(self):
		return str(self.date) + ' ' + self.patient.fullname

	class Meta:
		verbose_name_plural = "8. ข้อมูลการให้บริการ"
		verbose_name = "ข้อมูลการให้บริการ"

class Log(models.Model):
	created = models.DateField(auto_now_add=True)
	sms_count = models.IntegerField(default=0)
	email_count = models.IntegerField(default=0)

	def __unicode__(self):
		return 'Month: ' + str(self.created.month) + ' '+str(self.created.year)

	class Meta:
		verbose_name_plural = "9. Log"
		verbose_name = "Log"
		get_latest_by = 'created'

	@classmethod
	def update_month_log(cls, message_type):
		today = timezone.now()
		if Log.objects.all():
			recent_log = Log.objects.latest()
			if recent_log.created.year == today.year:
				if not recent_log.created.month <  today.month :
					if message_type == 'sms':
						recent_log.increment_sms_count()
					elif message_type == 'email':
						recent_log.increment_email_count()
					elif message_type == 'both':
						recent_log.increment_sms_count()
						recent_log.increment_email_count()
					return recent_log
		if message_type == 'sms':
			return Log.objects.create(sms_count=1)
		elif message_type == 'email':
			return Log.objects.create(email_count=1)
		elif message_type == 'both':
			return Log.objects.create(sms_count=1, email_count=1)
		else:
			return Log.objects.create()

	def increment_sms_count(self):
		self.sms_count = self.sms_count + 1
		self.save()

	def increment_email_count(self):
		self.email_count = self.email_count + 1
		self.save()



class Record(models.Model):
	patient = models.ForeignKey(Patient)
	datetime = models.DateTimeField(auto_now_add=True, verbose_name='เวลา')
	voicemail = models.CharField(blank=True, max_length=200, verbose_name='ข้อมูลฝากเสียง')
	status = models.CharField(default='รอการตอบกลับ', max_length=200, verbose_name='สถานะ')
	period = models.CharField(max_length=200, choices=PEROIDS, verbose_name='ช่วงเวลา')
	submitted_by = models.CharField(max_length=200, choices=SUBMIT_OPTIONS, verbose_name='ได้รับข้อมูลทาง')

	def __unicode__(self):
		return "id: " + str(self.id) + " timestamp: " + str(self.datetime)#.astimezone(timezone('Asia/Bangkok')).strftime("%d/%m/%y %H:%M:%S"))

	class Meta:
		verbose_name_plural = "2. บันทึกรายวัน"
		verbose_name = "บันทึกรายวัน"
		get_latest_by = 'datetime'

	def change_status(self, status):
		self.status = status
		self.save()

	def create_entry_for_record_from_voip(self, weight=None, pressure=None, drug=None, sign=None):
		if weight:
			entry = self.weight_set.create(
				weight = weight['weight']
			)
		elif drug:
			entry = self.drug_set.create(
				name = drug['name'],
				size = drug['size'],
				amount = drug['amount']
			)
		elif pressure:
			entry = self.pressure_set.create(
				up = pressure['up'],
				down = pressure['down']
			)
		elif sign:
			entry = self.sign_set.create(
				sign = sign,
			)
		return entry


	def create_entry_for_record_from_web(self, form):
		if form.cleaned_data['weight']:
			try:
				self.weight_set.create(
					weight = form.cleaned_data['weight']
				)
			except Exception, e:
				raise e
		if form.cleaned_data['drug_size'] and form.cleaned_data['drug_amount']:
			try:
				self.drug_set.create(
					name = form.cleaned_data['drug_name'],
					size = form.cleaned_data['drug_size'],
					amount = form.cleaned_data['drug_amount']
				)
			except Exception, e:
				raise e
		if form.cleaned_data['pressure_up'] and form.cleaned_data['pressure_down']:
			try:
				self.pressure_set.create(
					up = form.cleaned_data['pressure_up'],
					down = form.cleaned_data['pressure_down']
				)
			except Exception, e:
				raise e
		if form.cleaned_data['sign']:
			try:
				self.sign_set.create(
					sign = form.cleaned_data['sign']
				)
			except Exception, e:
				raise e
		return True

class Response(models.Model):
	record = models.OneToOneField(Record)
	nurse = models.ForeignKey(User)
	reply_text = models.CharField(blank=True, max_length=200, verbose_name='ข้อความตอบกลับ')
	deleted = models.BooleanField(default=False, verbose_name='ลบ')
	timestamp = models.DateTimeField(auto_now_add=True, verbose_name='เวลาที่ตอบกลับ')

	def __unicode__(self):
		return str(self.record.id) +" "+self.nurse.username + " timestamp: " + str(self.timestamp)

	class Meta:
		verbose_name_plural = "3. ตอบกลับบันทึก"
		verbose_name = "ตอบกลับบันทึก"

	def get_reply_text(self):
		return self.reply_text.replace('|',' ')

class RecordElementBase(models.Model):
	record = models.ForeignKey(Record)

	class Meta:
		abstract = True

class Drug(RecordElementBase):
	name = models.CharField(max_length=200, choices=DRUGS, blank=True, null=True, verbose_name='ชื่อยา')
	size = models.IntegerField(choices=DRUG_SIZES, blank=True, null=True, verbose_name='ขนาดยา')
	amount = models.DecimalField(max_digits=2, decimal_places=1, choices=DRUG_AMOUNTS, blank=True, null=True, verbose_name='จำนวนยา')

	def __unicode__(self):
		return "Record: " + str(self.record.id) + " "  + self.name + " " + str(self.size) + " " + str(self.amount)

	class Meta:
		verbose_name_plural = "5. ยา"
		verbose_name = "ยา"

class Pressure(RecordElementBase):
	up = models.IntegerField(blank=True, null=True, verbose_name='ความดันตัวบน')
	down = models.IntegerField(blank=True, null=True, verbose_name='ความดันตัวล่าง')

	def __unicode__(self):
		return "Record: " + str(self.record.id) + " " + str(self.up) + " " + str(self.down)

	class Meta:
		verbose_name_plural = "6. ความดัน"
		verbose_name = "ความดัน"

class Weight(RecordElementBase):
	weight = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True, verbose_name='น้ำหนัก')

	def __unicode__(self):
		return "Record: " + str(self.record.id) + " " + str(self.weight)

	class Meta:
		verbose_name_plural = "4. น้ำหนัก"
		verbose_name = "น้ำหนัก"

class Sign(RecordElementBase):
	sign = models.CharField(max_length=200, blank=True, null=True, verbose_name='อาการอื่นๆ')

	def __unicode__(self):
		return "Record: " + str(self.record.id) + " "  + self.sign

	class Meta:
		verbose_name_plural = "7. อาการอื่นๆ"
		verbose_name = "อาการอื่นๆ"

