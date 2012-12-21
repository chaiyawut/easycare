#-*-coding: utf-8 -*-
from frontend.models import Patient, Record, Weight, Pressure, Drug, Response
from django import forms
from frontend.fields import ResponseAutoCompleteField
from django.core import validators 
import os

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
		exclude = ('reply_text',)
		widgets = {
			'record': forms.HiddenInput(),
			'nurse': forms.HiddenInput(),
			'deleted': forms.HiddenInput(),
		}

class PatientForm(forms.ModelForm):
	class Meta:
		model = Patient

	def clean_sound_for_name(self):
		uploaded_file = self.cleaned_data['sound_for_name']
		fileName, fileExtension = os.path.splitext(uploaded_file.name)
		if fileExtension != '.mp3':
			raise forms.ValidationError("ไฟล์เสียงสำหรับชื่อต้องเป็น .mp3 เท่านั้น")
		return uploaded_file



class WeightForm(forms.ModelForm):
	class Meta:
		model = Weight
		exclude = ('record',)
		widgets = {
			'period': forms.HiddenInput(),
			'weight': forms.TextInput(attrs={'class': 'input-medium',})
		}

	def __init__(self, *args, **kwargs):
		super(WeightForm, self).__init__(*args, **kwargs)
		self.fields['weight'].validators.append(validators.MinValueValidator(0))
		self.fields['weight'].validators.append(validators.MaxValueValidator(200))

class DrugForm(forms.ModelForm):
	class Meta:
		model = Drug
		exclude = ('record',)
		widgets = {
			'period': forms.HiddenInput(),
			'name': forms.HiddenInput(),
			'size': forms.Select(attrs={'class': 'input-small',}),
			'amount': forms.Select(attrs={'class': 'input-small',}),
		}

	def clean(self):
		cleaned_data = super(DrugForm, self).clean()
		size = cleaned_data.get("size")
		amount = cleaned_data.get("amount")

		if size and not amount:
			msg = u"กรุณาใส่จำนวนยา"
			self._errors["amount"] = self.error_class([msg])
			del cleaned_data["size"]
		elif amount and not size:
			msg = u"กรุณาใส่ขนาดยา"
			self._errors["size"] = self.error_class([msg])
			del cleaned_data["amount"]
		return cleaned_data

class PressureForm(forms.ModelForm):
	class Meta:
		model = Pressure
		exclude = ('record',)
		widgets = {
			'period': forms.HiddenInput(),
			'name': forms.HiddenInput(),
			'up': forms.TextInput(attrs={'class': 'input-mini',}),
			'down': forms.TextInput(attrs={'class': 'input-mini',})
		}

	def clean(self):
		cleaned_data = super(PressureForm, self).clean()
		up = cleaned_data.get("up")
		down = cleaned_data.get("down")

		if up and not down:
			msg = u"กรุณาใส่ความดันตัวล่าง"
			self._errors["down"] = self.error_class([msg])
			del cleaned_data["up"]
		elif down and not up:
			msg = u"กรุณาใส่ความดันตัวบน"
			self._errors["down"] = self.error_class([msg])
			del cleaned_data["down"]
		return cleaned_data

	def __init__(self, *args, **kwargs):
		super(PressureForm, self).__init__(*args, **kwargs)
		self.fields['up'].validators.append(validators.MinValueValidator(0))
		self.fields['up'].validators.append(validators.MaxValueValidator(200))
		self.fields['down'].validators.append(validators.MinValueValidator(0))
		self.fields['down'].validators.append(validators.MaxValueValidator(200))

class RecordForm(forms.Form):
	contact_number = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder':'หมายเลขโทรศัพท์ - 08xx, 02xx'}))

	def get_patient_from_hn(self):
		contact_number = self.cleaned_data['contact_number']
		try:
			return Patient.objects.get(contact_number=contact_number)
		except Exception, e:
			return False

class HNFilterForm(forms.Form):
	hn = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'input-medium search-query','placeholder':'จากรหัสผู้ป่วยนอก'}))
	from_date = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'input-small search-query','placeholder':'จากวันที่'}))
	to_date = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'input-small search-query','placeholder':'ถึงวันที่'}))


class RecordFilterForm(forms.Form):
	record = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'input-medium search-query','placeholder':'จากเลขอ้างอิง'}))
