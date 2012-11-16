#-*-coding: utf-8 -*-
from ESL import *

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

def sendSMSFromWeb(contact_number, messages):
	con = ESLconnection("127.0.0.1", "8021", "ClueCon")
	if con.connected():
		for message in messages:
			if not len(message.decode('utf-8')) > 70:
				api = "chat SMS|gsm01|"+contact_number+"| "+ message.decode('utf-8')
				con.send("api " + api.encode('utf-8'))
			else:
				api = "chat SMS|gsm01|"+contact_number+"|exceed maximum lenght"
				con.send("api " + api.encode('utf-8'))
		api = "chat SMS|gsm01|"+contact_number+"|Thank you. Advance Heart failure Clinic, Chulalongkorn Hospital."
		con.send("api " + api.encode('utf-8'))
		con.disconnect()
		return True
	return False
