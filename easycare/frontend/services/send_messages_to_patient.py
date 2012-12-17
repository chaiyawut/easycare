#-*-coding: utf-8 -*-
import string
import sys
from django.core.mail import send_mail, BadHeaderError

def send_messages_to_patient(msg_type, contact_number, contact_email, messages):
        if msg_type == 'sms' or msg_type == 'both':
                try:
                        from ESL import *
                        con = ESLconnection("202.44.9.119", "8021", "ClueCon")
        		if con.connected():
                        	for message in messages:
                                	if not len(message.decode('utf-8')) > 70:
        					api = "gsmopen_sendsms gsm01 "+ contact_number + " " + message.decode('utf-8')
                                        	#api = "chat SMS|gsm01|"+contact_number+"| "+ message.decode('utf-8')
                                        	con.send("api " + api.encode('utf-8'))
                                	else:
                                        	api = "gsmopen_sendsms gsm01 "+ contact_number + " " + message.decode('utf-8')
        					#api = "chat SMS|gsm01|"+contact_number+"|exceed maximum lenght"
                                        	con.send("api " + api.encode('utf-8'))
                        	api = "gsmopen_sendsms gsm01 "+ contact_number + " Thank you. Advance Heart failure Clinic, Chulalongkorn Hospital."
        			#api = "chat SMS|gsm01|"+contact_number+"|Thank you. Advance Heart failure Clinic, Chulalongkorn Hospital."
                        	con.send("api " + api.encode('utf-8'))
                        	con.disconnect()
                        	return True
                	return False
        	except Exception, e:
                        return False
        
        if msg_type == 'email' or msg_type == 'both':
                try:
                        subject = 'Subject here'
                        send_mail(subject, messages, 'easycare.sit@gmail.com',[contact_email], fail_silently=False)
                except Exception, e:
                        return False

# def sendSMS(contact_number, messages):
# 	con = ESLconnection("127.0.0.1", "8021", "ClueCon")
# 	if con.connected():
# 		for message in messages:
# 			if not len(message.decode('utf-8')) > 70:
# 				api = "chat SMS|gsm01|"+contact_number+"| "+ message
# 				con.send("api " + api)
# 			else:
# 				api = "chat SMS|gsm01|"+contact_number+"|exceed maximum lenght"
# 				con.send("api " + api)
# 		api = "chat SMS|gsm01|"+contact_number+"|Thank you. Advance Heart failure Clinic, Chulalongkorn Hospital."
# 		con.send("api " + api)
# 		con.disconnect()

