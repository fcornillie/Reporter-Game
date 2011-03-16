'''
Created on March 16, 2011

@author: Frederik Cornillie <frederik.cornillie@gmail.com>

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

class play_game(webapp.RequestHandler):
	"""
	Returns a Django template for one game.
	
	Requires the following parameters:
	- game: the key of the game
	"""
	
	@login_required
	def get(self):
		player = get_current_player()
		game = None
		if self.request.get('game'):
			game = Game.get(self.request.get('game'))
		else:
			games = Game.all()
			if games.count() > 0:
				game = Game.all()[0]

			template_values = {
				'game':game,
			}
			
			path = os.path.join(os.path.dirname(__file__), 'templates/game_detail.html')
			self.response.out.write(template.render(path, append_base_template_values(template_values)))

class get_player_score(webapp.RequestHandler):
	""" Returns the current player score for a particular game in JSON format """
	
	@login_required
	def get(self):
		self.response.out.write(json.dumps(get_current_player().get_last_game_session().score))

class get_player_leaderboard(webapp.RequestHandler):
	""" Returns the current player score for a particular game in JSON format """
	
	@login_required
	def get(self):
		player = get_current_player()
		if player:
			gamesession = player.get_last_game_session()
			leadersessions = GameSession.gql("WHERE game = :1 "
							   "ORDER BY absolutescore DESC",
							   gamesession.game)
			leaderboard = ""
			for l in leadersessions:
				leaderboard = leaderboard + "<div class=\"nick\" style=\'float:left;width:180px;\' ><a href='/profile?game=" + str(gamesession.game.key()) + "&amp;player=" + str(l.player.key()) + "'>" + l.player.nickname + "</a></div><div class=\"score\" style=\'float:left;width:40px;text-align:right;\'><b>" + str(l.absolutescore) + "</b></div><div style=\'clear:both;\'></div>"
			self.response.out.write("<span style=\'font-weight:bold;\'>HIGH SCORES</span><br/>" + leaderboard)

class MainHandler(webapp.RequestHandler):  
	@login_required
	def get(self):
		player = get_current_player()
		if player == None:
			player = Player(user=users.get_current_user())
			player.put()	
		self.redirect("/play_game")

# **********
# MAIN
# **********

def main():
	logging.getLogger().setLevel(logging.DEBUG)
	application = webapp.WSGIApplication([('/', MainHandler),
										('/get_player_score',get_player_score),
										('/get_player_leaderboard',get_player_leaderboard),
										('/play_game',play_game),
								],
											debug=True)

	wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
	main()

