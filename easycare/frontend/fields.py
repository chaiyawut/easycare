#-*-coding: utf-8 -*-
from django.forms import fields
from frontend.widgets import AutoCompleteWidget
from django.contrib.auth.models import User
from django import forms

class ResponseAutoCompleteField(fields.MultiValueField):
    widget = AutoCompleteWidget(attrs={'maxlength': 70,'rows': 3 })

    def __init__(self, *args, **kwargs):
        all_fields = (
            fields.CharField(),
            fields.CharField(),
            fields.CharField(),
            )
        super(ResponseAutoCompleteField, self).__init__(all_fields, *args, **kwargs)
    
    def compress(self, data_list):
        """
        Takes the values from the MultiWidget and passes them as a
        list to this function. This function needs to compress the
        list into a single object to save.
        """
        if data_list:
            return '|'.join(data_list)
        raise forms.ValidationError("ข้อมูลตอบกลับว่างเปล่า")