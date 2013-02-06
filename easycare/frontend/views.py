#-*-coding: utf-8 -*-
from django.shortcuts import render_to_response, redirect, render
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from frontend.forms import * #RecordForm, WeightForm, DrugForm, PressureForm, PatientForm, ResponseForm, DeleteForm, HistoryFilterForm
from frontend.models import *
from django.forms.formsets import formset_factory
from django.http import HttpResponse
from django.contrib import messages
from django.views.generic import *
from django.views.generic.edit import *
from django.core.urlresolvers import reverse_lazy
from datetime import date, timedelta
from django.utils import timezone
import json
import decimal
import re
from django.utils import simplejson
from frontend.services.send_messages_to_patient import send_messages_to_patient
from django.template.loader import render_to_string
import os
from frontend.utils.words import PERIODS
from easycare.settings import PROJECT_PATH

def json_encode_decimal(obj):
	if isinstance(obj, decimal.Decimal):
		return int(obj)
	raise TypeError(repr(obj) + " is not JSON serializable")

def homepage(request):
	if request.path == "/":
		return redirect('/homepage/')
	return render(request, 'homepage.html')

def aboutus(request):
	return render(request, 'aboutus.html')

def contactus(request):
	return render(request, 'contactus.html')

def record_create(request):
	if request.method == 'POST': # If the form has been submitted...
		form = RecordForm(request.POST) # A form bound to the POST data
		if form.is_valid(): # All validation rules pass
			period = form.cleaned_data['period']
			patient = form.get_patient_from_contact_number()
			if patient:
				if patient.check_for_no_duplicate_period(period):
					new_record = patient.create_new_record(period, 'web')
					if new_record.create_entry_for_record_from_web(form):
						html_messages = render_to_string('email/confirm_record.html', { 'record': new_record })
						reply_messages = '#' + str(new_record.id) + ' ช่วง:' + PERIODS[period] + ' '
						if new_record.weight_set.all():
							weight_message = "น้ำหนัก:"
							for data in new_record.weight_set.all():
								weight_message = weight_message + str(data.weight) + ' '
							reply_messages = reply_messages + weight_message
						if new_record.drug_set.all():
							drug_message = "ยา:"
							for data in new_record.drug_set.all():
								drug_message = drug_message + str(data.size)+'มก.'+str(data.amount) + 'เม็ด '
							reply_messages = reply_messages + drug_message
						if new_record.pressure_set.all():
							pressure_message = "ความดัน:"
							for data in new_record.pressure_set.all():
								pressure_message = pressure_message + str(data.up)+'/'+str(data.down) + ' '
							reply_messages = reply_messages + pressure_message
						sent = send_messages_to_patient(patient.confirm_by, patient.contact_number, patient.email, reply_messages, html_messages)
						if sent:
							messages.success(request, "คำร้องขอถูกสร้างแล้ว", extra_tags='alert alert-success')
						else:
							messages.success(request, "ระบบส่งข้อความผิดพลาด คนไข้จะไม่ได้รับข้อความ", extra_tags='alert alert-error')
						return render(request, 'record/create_success.html', { 'HEADER':'ระบบบันทึกข้อมูลของท่านเรียบร้อยแล้วค่ะ', 'record': new_record })
					else:
						messages.error(request, 'ไม่สามารถเซฟได้กรุณาจดเลข "' + str(new_record.id) + '" และติดต่อพยาบาล', extra_tags='alert alert-error')
				else:
					messages.error(request, "ท่านได้ส่งข้อมูลสำหรับช่วงเวลา" + PERIODS[period] + "แล้ว", extra_tags='alert alert-error')
			else:
				messages.error(request, 'หมายเลขโทรศัพท์ของท่านยังไม่ได้ทำการลงทะเบียนเอาไว้ค่ะ', extra_tags='alert alert-error')
	else:
		form = RecordForm() # An unbound form

	return render(request, 'record/create.html', {
		'form': form,
	})

class RecordPendingListView(ListView):
	model = Record
	template_name = 'record/pending.html'
	paginate_by = 10
	context_object_name = 'records'

	def get_queryset(self):
		queryset = Record.objects.all().exclude(response__isnull=False)
		return queryset

	def get_context_data(self, **kwargs):
		context = super(RecordPendingListView, self).get_context_data(**kwargs)
		next_page_url = self.get_url_encoded(page = str(context['page_obj'].next_page_number()))
		previous_page_url = self.get_url_encoded(page = str(context['page_obj'].previous_page_number()))
		context['next_page_url'] = next_page_url
		context['previous_page_url'] = previous_page_url
		return context

	def get_url_encoded(self, **kwargs):
		q = self.request.GET.copy()
		q.__setitem__('page', kwargs['page'])
		url = "?" + q.urlencode()
		return url

class PatientVisitCreateView(CreateView):
	form_class = VisitForm
	model = Visit
	template_name = 'patient/visit.html'
	success_url = reverse_lazy('patient-visit')

	def form_valid(self, form):
		hn = form.cleaned_data['hn']
		date = form.cleaned_data['date']
		visit_type = form.cleaned_data['visit_type']	
		Visit.objects.create(
			patient = Patient.objects.get(hn= hn),
			date = date,
			visit_type = visit_type
		)
		messages.success(self.request, "ประวัติการเข้ารับบริการของคนไข้ถูกสร้างแล้ว", extra_tags='alert alert-success')
		return redirect(self.success_url)


class PatientReisterCreateView(CreateView):
	form_class = PatientForm
	model = Patient
	template_name = 'patient/register.html'
	success_url = reverse_lazy('patient-register')

	def form_valid(self, form):
		messages.success(self.request, "ประวัติคนไข้ถูกสร้างแล้ว", extra_tags='alert alert-success')

		if not form.cleaned_data['sound_for_name']:
			import requests
			r = requests.get('http://translate.google.co.th/translate_tts?ie=UTF-8&q=%E0%B8%84%E0%B8%B8%E0%B8%93'+ form.cleaned_data['firstname'] +'&tl=th&total=1&idx=0&textlen=6&prev=input&sa=N', stream=True)
			sound = r.raw.read()
			myFile = open(PROJECT_PATH + '/media/voices/sounds_for_name/'+ form.cleaned_data['hn'].replace('/', '_') +'.mp3', 'w')
			myFile.write(sound)
			myFile.close() 

		return super(PatientReisterCreateView, self).form_valid(form)

class PatientUpdateView(UpdateView):
	model = Patient
	context_object_name = 'patient'
	template_name = 'patient/edit.html'
	success_url = reverse_lazy('record-pending')

	def get_context_data(self, **kwargs):
		context = super(PatientUpdateView, self).get_context_data(**kwargs)
		patient = super(PatientUpdateView, self).get_object()
		records = Record.objects.filter(patient=patient)
		if records:
			record = records.latest()
		else:
			record = None
		context['record'] = record
		return context

	def form_valid(self, form):
		messages.success(self.request, "ประวัติคนไข้ถูกแก้ไขแล้ว", extra_tags='alert alert-success')

		if not form.cleaned_data['sound_for_name']:
			import requests
			r = requests.get('http://translate.google.co.th/translate_tts?ie=UTF-8&q=%E0%B8%84%E0%B8%B8%E0%B8%93'+ form.cleaned_data['firstname'] +'&tl=th&total=1&idx=0&textlen=6&prev=input&sa=N', stream=True)
			sound = r.raw.read()
			myFile = open(PROJECT_PATH + '/media/voices/sounds_for_name/'+ form.cleaned_data['hn'].replace('/', '_') +'.mp3', 'w')
			myFile.write(sound)
			myFile.close() 

		return super(PatientUpdateView, self).form_valid(form)

class PatientListView(ListView):
	model = Patient
	template_name = 'patient/list.html'
	paginate_by = 10
	date_field = 'datetime'


class HistoryListView(ListView, FormMixin):
	model = Record
	template_name = 'record/history.html'
	paginate_by = 10
	date_field = 'datetime'
	form_class = HNFilterForm

	def get_queryset(self):
		queryset = super(HistoryListView, self).get_queryset().exclude(response__isnull=True).order_by('-id')
		if 'record' in self.request.GET:
			record_id = self.request.GET.get('record')
			return Record.objects.filter(id=record_id)

		if 'hn' in self.request.GET:
			from_date = self.request.GET.get('from_date')
			to_date = self.request.GET.get('to_date')
			hn = self.request.GET.get('hn')
			if from_date and to_date:
				from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
				to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d").date() + datetime.timedelta(1)
				if hn:
					queryset = Record.objects.filter(patient__hn=hn,datetime__range=[from_date, to_date]).exclude(response__isnull=True).order_by('id')
				else:
					queryset = Record.objects.filter(datetime__range=[from_date, to_date]).exclude(response__isnull=True).order_by('id')
			else:
				queryset = Record.objects.filter(patient__hn=hn).exclude(response__isnull=True).order_by('-id')	
		return queryset

	def get_context_data(self, **kwargs):
		context = super(HistoryListView, self).get_context_data(**kwargs)
		next_page_url = self.get_url_encoded(page = str(context['page_obj'].next_page_number()))
		previous_page_url = self.get_url_encoded(page = str(context['page_obj'].previous_page_number()))
		context['next_page_url'] = next_page_url
		context['previous_page_url'] = previous_page_url
		context['hn_form'] = HNFilterForm(self.request.GET)
		context['record_form'] = RecordFilterForm(self.request.GET)
		return context

	def get_url_encoded(self, **kwargs):
		q = self.request.GET.copy()
		q.__setitem__('page', kwargs['page'])
		url = "?" + q.urlencode()
		return url

class RecordDetailView(DetailView):
	model = Record
	context_object_name = 'record'
	template_name = 'record/detail.html'


class RecordResponseView(CreateView):
	model = Response
	form_class = ResponseForm
	template_name = 'record/reply.html'
	success_url = reverse_lazy('record-pending')

	def get_reply_text(self, autofill):
		REPLY_LIST = {
			'1':['เราทบทวนข้อมูลของคุณแล้ว ไม่ปรับยา ให้ทานเหมือนเดิม ขอบคุณค่ะ'],
			'2':['เราทบทวนข้อมูลของคุณแล้ว คงต้องมีการปรับยา', 'เราจะติดต่อกลับภายใน 24 ซม.นะคะ หากมีปัญหาติดต่อ 0813839302'],
		}
		if autofill in REPLY_LIST:
			return "|".join(REPLY_LIST[autofill])


	def get_initial(self):
		if 'autofill' in self.request.GET:
			autofill = self.request.GET['autofill']
			reply_text = self.get_reply_text(autofill)
		else:
			reply_text = ""
		self.record = Record.objects.get(id=self.kwargs['record'])
		user = self.request.user
		return {'record': self.record.id, 'nurse': user , 'reply_text':reply_text}

	def get_context_data(self, **kwargs):
		context = super(RecordResponseView, self).get_context_data(**kwargs)
		context['record'] = self.record
		return context

	def form_valid(self, form):
		redirect_url = super(RecordResponseView, self).form_valid(form)
		self.record.change_status('ตอบกลับแล้ว')

		contact_number = self.record.patient.contact_number
		contact_email = self.record.patient.email
		msg_type = self.record.patient.confirm_by

		reponse_text = form.cleaned_data['reply_text'].replace('|',' ').encode('utf-8')
		reply_messages = '#'+ str(self.record.id) + ' ' + reponse_text
	
		html_messages = render_to_string('email/reply_record.html', { 'record': self.record })
		sent = send_messages_to_patient(msg_type, contact_number, contact_email, reply_messages, html_messages)
		if sent:
			messages.success(self.request, "คำร้องขอถูกตอบกลับเรียบร้อยแล้ว", extra_tags='alert alert-success')
		else:
			messages.success(self.request, "ระบบส่งข้อความผิดพลาด คนไข้จะไม่ได้รับข้อความ", extra_tags='alert alert-error')
		return redirect_url

	def form_invalid(self, form):
		for hidden in form.hidden_fields(): 
			if hidden.errors:
				messages.success(self.request, "คำร้องขอถูกตอบกลับเรียบร้อยแล้ว", extra_tags='alert alert-success')
				return redirect(self.success_url)
		redirect_url = super(RecordResponseView, self).form_invalid(form)
		return redirect_url

class RecordDeleteView(CreateView):
	model = Response
	form_class = DeleteForm
	template_name = 'record/delete.html'
	success_url = reverse_lazy('record-pending')

	def get_initial(self):
		self.record = Record.objects.get(id=self.kwargs['record'])
		user = self.request.user
		return {'record': self.record.id, 'nurse': user, 'deleted':True, 'reply_text':'ลบ' }

	def get_context_data(self, **kwargs):
		context = super(RecordDeleteView, self).get_context_data(**kwargs)
		context['record'] = self.record
		return context

	def form_valid(self, form):
		redirect_url = super(RecordDeleteView, self).form_valid(form)
		self.record.change_status('ลบ')

		contact_number = self.record.patient.contact_number
		contact_email = self.record.patient.email
		msg_type = self.record.patient.confirm_by

		reply_messages = '#'+ str(self.record.id) + ' คำร้องขอถูกลบเรียบร้อยแล้ว'
		html_messages = render_to_string('email/reply_record.html', { 'record': self.record })

		sent = send_messages_to_patient(msg_type, contact_number, contact_email, reply_messages, html_messages)
		if sent:
			messages.success(self.request, "คำร้องขอถูกลบเรียบร้อยแล้ว", extra_tags='alert alert-success')
		else:
			messages.success(self.request, "ระบบส่งข้อความผิดพลาด คนไข้จะไม่ได้รับข้อความ", extra_tags='alert alert-error')

		return redirect_url


@login_required
def graph_weight(request, record_id):
	record = Record.objects.get(id=record_id)
	patient = record.patient
	start_date = record.datetime.date() - timedelta(days=6)
	last_7_days = []
	last_7_days_morning_weights = []
	last_7_days_afternoon_weights = []
	last_7_days_evening_weights = []

	for i in range(7):
		date = start_date + timedelta(days=i)
		last_7_days.append(str(date.strftime('%a %d/%m/%Y')))

		#build morning weight
		morning_weight = Weight.objects.filter(record__patient=patient, record__period='morning', record__datetime__range=(datetime.datetime.combine(date, datetime.time.min).replace(tzinfo=timezone.get_default_timezone()),datetime.datetime.combine(date, datetime.time.max).replace(tzinfo=timezone.get_default_timezone()))).exclude(record__response__isnull=True).exclude(record__response__deleted=True)
		if morning_weight:
			last_7_days_morning_weights.append(morning_weight[0].weight)
		else:
			last_7_days_morning_weights.append(0)

		#build afternoon weight
		afternoon_weight = Weight.objects.filter(record__patient=patient, record__period='afternoon', record__datetime__range=(datetime.datetime.combine(date, datetime.time.min).replace(tzinfo=timezone.get_default_timezone()),datetime.datetime.combine(date, datetime.time.max).replace(tzinfo=timezone.get_default_timezone()))).exclude(record__response__isnull=True).exclude(record__response__deleted=True)
		if afternoon_weight:
			last_7_days_afternoon_weights.append(afternoon_weight[0].weight)
		else:
			last_7_days_afternoon_weights.append(0)

		#build evening weight
		evening_weight = Weight.objects.filter(record__patient=patient, record__period='evening', record__datetime__range=(datetime.datetime.combine(date, datetime.time.min).replace(tzinfo=timezone.get_default_timezone()),datetime.datetime.combine(date, datetime.time.max).replace(tzinfo=timezone.get_default_timezone()))).exclude(record__response__isnull=True).exclude(record__response__deleted=True)
		if evening_weight:
			last_7_days_evening_weights.append(evening_weight[0].weight)
		else:
			last_7_days_evening_weights.append(0)

	response = json.dumps({
		'last_7_days':last_7_days,
		'last_7_days_morning_weights':last_7_days_morning_weights,
		'last_7_days_afternoon_weights':last_7_days_afternoon_weights,
		'last_7_days_evening_weights':last_7_days_evening_weights,
	}, default=json_encode_decimal)
	return HttpResponse(response)


@login_required
def graph_drug(request, record_id):
	record = Record.objects.get(id=record_id)
	patient = record.patient
	start_date = record.datetime.date() - timedelta(days=6)
	last_7_days = []
	last_7_days_drug_consume_amounts = []

	for i in range(7):
		date = start_date + timedelta(days=i)
		last_7_days.append(str(date.strftime('%a %d/%m/%Y')))

		#build drug consuming amount
		drugs = Drug.objects.filter(record__patient=patient, record__datetime__range=(datetime.datetime.combine(date, datetime.time.min).replace(tzinfo=timezone.get_default_timezone()),datetime.datetime.combine(date, datetime.time.max).replace(tzinfo=timezone.get_default_timezone()))).exclude(record__response__isnull=True).exclude(record__response__deleted=True)
		total_drug_for_today = 0
		if drugs:
			for drug in drugs:
				total_drug_for_today =  total_drug_for_today + (drug.size*drug.amount)
			last_7_days_drug_consume_amounts.append(total_drug_for_today)
		else:
			last_7_days_drug_consume_amounts.append(None)
	
	response = json.dumps({
		'last_7_days':last_7_days,
		'last_7_days_drug_consume_amounts':last_7_days_drug_consume_amounts,
	}, default=json_encode_decimal)
	return HttpResponse(response)

@login_required
def graph_pressure(request, record_id):
	record = Record.objects.get(id=record_id)
	patient = record.patient
	start_date = record.datetime.date() - timedelta(days=6)
	last_7_days = []
	last_7_days_morning_pressure_up = []
	last_7_days_morning_pressure_down = []
	last_7_days_afternoon_pressure_up = []
	last_7_days_afternoon_pressure_down = []
	last_7_days_evening_pressure_up = []
	last_7_days_evening_pressure_down = []

	for i in range(7):
		date = start_date + timedelta(days=i)
		last_7_days.append(str(date.strftime('%a %d/%m/%Y')))

		#build morning pressure
		morning_pressure = Pressure.objects.filter(record__patient=patient, record__period='morning', record__datetime__range=(datetime.datetime.combine(date, datetime.time.min).replace(tzinfo=timezone.get_default_timezone()),datetime.datetime.combine(date, datetime.time.max).replace(tzinfo=timezone.get_default_timezone()))).exclude(record__response__isnull=True).exclude(record__response__deleted=True)
		if morning_pressure:
			last_7_days_morning_pressure_up.append(morning_pressure[0].up)
			last_7_days_morning_pressure_down.append(-morning_pressure[0].down)
		else:
			last_7_days_morning_pressure_up.append(0)
			last_7_days_morning_pressure_down.append(0)

		#build afternoon pressure
		afternoon_pressure = Pressure.objects.filter(record__patient=patient, record__period='afternoon', record__datetime__range=(datetime.datetime.combine(date, datetime.time.min).replace(tzinfo=timezone.get_default_timezone()),datetime.datetime.combine(date, datetime.time.max).replace(tzinfo=timezone.get_default_timezone()))).exclude(record__response__isnull=True).exclude(record__response__deleted=True)
		if afternoon_pressure:
			last_7_days_afternoon_pressure_up.append(afternoon_pressure[0].up)
			last_7_days_afternoon_pressure_down.append(-afternoon_pressure[0].down)
		else:
			last_7_days_afternoon_pressure_up.append(0)
			last_7_days_afternoon_pressure_down.append(0)

		#build morning pressure
		evening_pressure = Pressure.objects.filter(record__patient=patient, record__period='evening', record__datetime__range=(datetime.datetime.combine(date, datetime.time.min).replace(tzinfo=timezone.get_default_timezone()),datetime.datetime.combine(date, datetime.time.max).replace(tzinfo=timezone.get_default_timezone()))).exclude(record__response__isnull=True).exclude(record__response__deleted=True)
		if evening_pressure:
			last_7_days_evening_pressure_up.append(evening_pressure[0].up)
			last_7_days_evening_pressure_down.append(-evening_pressure[0].down)
		else:
			last_7_days_evening_pressure_up.append(0)
			last_7_days_evening_pressure_down.append(0)
	
	response = json.dumps({
		'last_7_days':last_7_days,
		'last_7_days_morning_pressure_up':last_7_days_morning_pressure_up,
		'last_7_days_morning_pressure_down':last_7_days_morning_pressure_down,
		'last_7_days_afternoon_pressure_up':last_7_days_afternoon_pressure_up,
		'last_7_days_afternoon_pressure_down':last_7_days_afternoon_pressure_down,
		'last_7_days_evening_pressure_up':last_7_days_evening_pressure_up,
		'last_7_days_evening_pressure_down':last_7_days_evening_pressure_down,
	}, default=json_encode_decimal)
	return HttpResponse(response)


