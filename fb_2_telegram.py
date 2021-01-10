from telegram.ext import Updater
import yaml
import facebook

with open('credential') as f:
	credential = yaml.load(f, Loader=yaml.FullLoader)
fb_graph = facebook.GraphAPI(credential['access_token'])
fb_graph.put_object(
	parent_object="439266300053488",
	connection_name="feed",
	message="test")