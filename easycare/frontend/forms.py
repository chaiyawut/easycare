#-*-coding: utf-8 -*-
from frontend.models import *
from django import forms
from frontend.fields import ResponseAutoCompleteField
from django.core import validators 
import os
from frontend.models import DRUG_SIZES, DRUG_AMOUNTS, PEROIDS

AUTO_REPLY = (
	('', '----------'),
	('1', 'ข้อความที่ 1'),
	('2', 'ข้อความที่ 2'),
)


class ResponseForm(forms.ModelForm):
	auto_text = forms.ChoiceField(choices=AUTO_REPLY, required=False)
	reply_text = ResponseAutoCompleteField(required=False)

	class Meta:
		model = Response
		exclude = ('deleted',)
		fields = ['record','nurse','auto_text', 'reply_text']
		widgets = {
			'record': forms.HiddenInput(),
			'nurse': forms.HiddenInput(),
		}

	def __init__(self, *args, **kwargs):
		super(ResponseForm, self).__init__(*args, **kwargs)
		self.fields['auto_text'].label = "ข้อความอัตโนมัติ"
		self.fields['reply_text'].label = "ข้อความตอบกลับ"

	

class DeleteForm(forms.ModelForm):
	class Meta:
		model = Response
		widgets = {
			'record': forms.HiddenInput(),
			'nurse': forms.HiddenInput(),
			'deleted': forms.HiddenInput(),
			'reply_text': forms.HiddenInput(),
		}

class PatientForm(forms.ModelForm):
	class Meta:
		model = Patient
		fields = ['hn','firstname','lastname', 'contact_number', 'email', 'confirm_by', 'sound_for_name']

	def clean_sound_for_name(self):
		if self.cleaned_data['sound_for_name']:
			uploaded_file = self.cleaned_data['sound_for_name']
			fileName, fileExtension = os.path.splitext(uploaded_file.name)
			if fileExtension != '.mp3':
				raise forms.ValidationError("ไฟล์เสียงสำหรับชื่อต้องเป็น .mp3 เท่านั้น")
			return uploaded_file

class VisitForm(forms.ModelForm):
	hn = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'input-medium','placeholder':'ตัวอย่าง 12345/55'}))
	
	class Meta:
		model = Visit
		fields = ['hn','date','visit_type']

	def __init__(self, *args, **kwargs):
		super(VisitForm, self).__init__(*args, **kwargs)
		self.fields['hn'].label = "หมายเลขผู้ป่วยนอก"

	def clean_hn(self):
		hn = self.cleaned_data['hn']
		try:
			Patient.objects.get(hn=hn)
			return hn
		except Exception, e:
			raise forms.ValidationError("หมายเลขผู้ป่วยนอกไม่ได้ลงทะเบียนไว้")
		

class RecordForm(forms.Form):
	contact_number = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'input-medium','placeholder':'ตัวอย่าง 081234567'}))
	period = forms.ChoiceField(choices=PEROIDS, widget=forms.Select(attrs={'class': 'input-medium',}))
	weight = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'input-small',}))
	drug_name = forms.CharField(initial="lasix",widget=forms.HiddenInput())
	drug_size = forms.ChoiceField(required=True, choices=DRUG_SIZES, widget=forms.Select(attrs={'class': 'input-small',}))
	drug_amount = forms.ChoiceField(required=True, choices=DRUG_AMOUNTS, widget=forms.Select(attrs={'class': 'input-small',}))
	pressure_up = forms.IntegerField(max_value=200,required=False, min_value=0, widget=forms.TextInput(attrs={'class': 'input-small',}))
	pressure_down = forms.IntegerField(max_value=200, min_value=0,required=False, widget=forms.TextInput(attrs={'class': 'input-small',}))
	sign = forms.CharField(max_length=100, required=False, widget=forms.Textarea(attrs={'rows': '4',}))

	def get_patient_from_contact_number(self):
		contact_number = self.cleaned_data['contact_number']
		try:
			return Patient.objects.get(contact_number=contact_number)
		except Exception, e:
			return False

	def clean(self):
		cleaned_data = super(RecordForm, self).clean()
		pressure_up = cleaned_data.get("pressure_up")
		pressure_down = cleaned_data.get("pressure_down")
		drug_size = cleaned_data.get("drug_size")
		drug_amount = cleaned_data.get("drug_amount")

		if pressure_up and not pressure_down:
			msg = u"กรุณาใส่ความดันตัวล่าง"
			self._errors["pressure_down"] = self.error_class([msg])
			del cleaned_data["pressure_up"]
		elif pressure_down and not pressure_up:
			msg = u"กรุณาใส่ความดันตัวบน"
			self._errors["pressure_up"] = self.error_class([msg])
			del cleaned_data["pressure_down"]

		if drug_size and not drug_amount:
			msg = u"กรุณาใส่จำนวนยา"
			self._errors["drug_amount"] = self.error_class([msg])
			del cleaned_data["drug_size"]
		elif drug_amount and not drug_size:
			msg = u"กรุณาใส่ขนาดยา"
			self._errors["drug_size"] = self.error_class([msg])
			del cleaned_data["drug_amount"]

		return cleaned_data

	"""
	def __init__(self, *args, **kwargs):
		super(RecordForm, self).__init__(*args, **kwargs)
		self.fields['pressure_up'].validators.append(validators.MinValueValidator(0))
		self.fields['pressure_up'].validators.append(validators.MaxValueValidator(200))
		self.fields['pressure_down'].validators.append(validators.MinValueValidator(0))
		self.fields['pressure_down'].validators.append(validators.MaxValueValidator(200))
	"""


class HNFilterForm(forms.Form):
	hn = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'input-medium search-query','placeholder':'จากรหัสผู้ป่วยนอก'}))
	from_date = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'input-small search-query','placeholder':'จากวันที่'}))
	to_date = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'input-small search-query','placeholder':'ถึงวันที่'}))


class RecordFilterForm(forms.Form):
	record = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'input-medium search-query','placeholder':'จากเลขอ้างอิง'}))
