#-*-coding: utf-8 -*-
from django import template

register = template.Library()

WORDS = {
	'morning': 'เช้า',
	'afternoon': 'กลางวัน',
	'evening': 'เย็น',
	}

@register.filter(name='to_thai')
def to_thai(value):
    return WORDS[value]