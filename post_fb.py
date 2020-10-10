#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram.ext import Updater, MessageHandler, Filters

import traceback as tb
import json
import yaml
import time
import urllib.request
import facebook
import os

with open('CREDENTIALS') as f:
	CREDENTIALS = json.load(f)

with open('SUBSCRIPTION') as f:
	SUBSCRIPTION = yaml.load(f, Loader=yaml.FullLoader)

with open('TELE_CHANNELS') as f:
	TELE_CHANNELS = set(yaml.load(f, Loader=yaml.FullLoader))

test_channel = -1001171873580

debug_group = -1001198682178

EXPECTED_ERRORS = ['Message to forward not found', "Message can't be forwarded"]

def matchKey(t, keys):
	if not t:
		return False
	for k in keys:
		if k in t:
			return True
	return False

def isUrl(t):
	for key in ['telegra.ph', 'com/', 'org/', '.st/', 'http', 't.co/']:
		if key in t:
			return True
	return False

def parseUrl(t):
	r = t
	for x in t.split():
		if not isUrl(x):
			continue
		if '://' in x:
			x = x[x.find('://') + 3:]
		else:
			r = r.replace(x, 'https://'+ x)
		for s in x.split('/'):
			if '?' in s:
				continue
			r = r.replace(s, urllib.request.pathname2url(s))
	return r

def getUrl(t):
	for x in t.split():
		if isUrl(x):
			if '://' in x:
				return x[x.find('://') + 3:]
			return x

def fb_post_page(api, keys, msg, chat):
	try:
		if msg.media_group_id:
			return
		if (not matchKey(msg.text, keys)) and (not matchKey(chat.title, keys)):
			return
		if msg.photo:
			filename = 'tmp' + msg.photo[-1].get_file().file_path.strip().split('/')[-1]
			msg.photo[-1].get_file().download(filename)
			api.put_photo(
				parent_object="439266300053488", # TODO
				connection_name="feed",
				image=open(filename, 'rb'))
			os.system('rm ' + filename)
			return 
		if not msg.text:
			return
		text = parseUrl(msg.text)
		if not text:
			print('FAIL: did not find text')
			print(msg.text)
			return
		print(text, getUrl(text))
		api.put_object(
			parent_object="439266300053488", # TODO
			connection_name="feed",
			message=text,
			link=getUrl(text))
	except Exception as e:
		if str(e) in EXPECTED_ERRORS:
			return
		updater.bot.send_message(chat_id=debug_group, text=str(e)) 
		print(e)
		tb.print_exc()

def fb_post(msg, chat):
	for page, subscription in SUBSCRIPTION.items():
		fb_post_page(graph[page], subscription['keys'], msg, chat)
	
def manage(update, context):
	try:
		msg = update.effective_message 
		if (not msg) or msg.media_group_id or (not update.effective_chat):
			return
		if update.effective_chat.id not in TELE_CHANNELS:
			return
		fb_post(msg, update.effective_chat)
	except Exception as e:
		if str(e) in EXPECTED_ERRORS:
			return
		print(e)
		updater.bot.send_message(chat_id=debug_group, text=str(e)) 
		tb.print_exc()

def backfill(chat_id, fill_range):
	for message_id in fill_range:
		print(message_id)
		try:
			time.sleep(5)
			r = updater.bot.forward_message(
				chat_id = test_channel, message_id = message_id, from_chat_id = chat_id)
			fb_post(r, r.forward_from_chat)
		except Exception as e:
			if str(e) in EXPECTED_ERRORS:
				continue
			updater.bot.send_message(chat_id=debug_group, text=str(e)) 
			print(e)
			tb.print_exc()

updater = Updater(CREDENTIALS['bot_token'], use_context=True)
dp = updater.dispatcher

graph = {
	'equality_page': facebook.GraphAPI(CREDENTIALS['equality_page']),
	'equality_group': facebook.GraphAPI(CREDENTIALS['equality_group'])
}

dp.add_handler(MessageHandler(Filters.update.channel_posts, manage))

backfill(-1001409716127, range(75, 300))

updater.start_polling()
updater.idle()