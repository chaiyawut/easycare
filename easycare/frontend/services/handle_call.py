#-*-coding: utf-8 -*-
from freeswitch import *
from frontend.handlers.call import CallHandler

def input_callback_record_file_pound_stop(session, type, obj):
	return "stop"

def handler(session, args):
	#All mobile incomming calls are now disabled by freeswitch dialplan.
	#All calls are from phone line and no call_id.
	session.answer()
	session.setInputCallback(input_callback_record_file_pound_stop)
	handler = CallHandler(session)
	handler.main_menu()

