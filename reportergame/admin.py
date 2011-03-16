'''
Created on December 15th, 2010

@author: Frederik Cornillie

'''

import cgi
import wsgiref.handlers
import os
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp.util import login_required
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext.db import GqlQuery
from google.appengine.api import memcache
from django.utils import simplejson as json
import logging

from models import *
from helpers import *

# **********
# MAIN VIEWS
# **********

class import_game(webapp.RequestHandler):
	""" 
	Stores a game in the database from a script.
	"""
	
	@login_required
	def get(self):
		user = users.get_current_user()
		if users.is_current_user_admin()==False:
			print "you are not an admin, user! get outta here"
		else:
			message = ""
			template_values = {
				'message':message,
			}
			path = os.path.join(os.path.dirname(__file__), 'templates/game_import.html')
			self.response.out.write(template.render(path, template_values))
	
	def post(self):
		from google.appengine.api import users
		user = users.get_current_user()
		if user:
			if users.is_current_user_admin()==False:
				print "you are not an admin, user! get outta here"
			else:
				g_raw = self.request.get('game_script').split("---")
				
				g_raw_header = g_raw[0].strip()
				g_title = g_raw_header.split("|")[0].strip()
				g_subtitle = g_raw_header.split("|")[1].strip()
				g = Game.gql("WHERE title = :1", g_title)
				if g.count() == 0:
					g = Game(title=g_title, subtitle=g_subtitle)
					g.maps_location = g_raw_header.split("|")[2]
					g.maps_zoom = int(g_raw_header.split("|")[3])
					g.start_xp = int(g_raw_header.split("|")[4])
					g.put()
					
				message = """Game has been successfully imported ... [ <a href='/_ah/login?&continue=/&action=Logout'>logout</a> ]"""

				template_values = {
					'message':message,
				}
				path = os.path.join(os.path.dirname(__file__), 'templates/game_import.html')
				self.response.out.write(template.render(path, template_values))
		else:
			self.redirect(users.create_login_url(self.request.uri))

class MainHandler(webapp.RequestHandler):  
	@login_required
	def get(self):
		print "main handler for admin pages here"
		# self.redirect("/redirect url here")
			
# **********
# MAIN
# **********

def main():
	logging.getLogger().setLevel(logging.DEBUG)
	application = webapp.WSGIApplication([('/admin/', MainHandler),
										('/admin/import_game',import_game),
								],
											debug=True)

	wsgiref.handlers.CGIHandler().run(application)
	
	
if __name__ == '__main__':
	main()
