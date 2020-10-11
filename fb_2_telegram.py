from telegram.ext import Updater
import yaml
import facebook

with open('credential') as f:
	credential = yaml.load(f, Loader=yaml.FullLoader)
fb_graph = facebook.GraphAPI(credential['access_token'])
fb_graph.get_object('transarmy')