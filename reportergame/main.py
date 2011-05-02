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

class get_game(webapp.RequestHandler):
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

class get_story(webapp.RequestHandler):
	"""
	Returns a Django template for one story.
	
	Requires the following parameters:
	- story: the key of the story
	"""
	
	@login_required
	def get(self):
		player = get_current_player()
		story = None
		if self.request.get('story'):
			story = Story.get(self.request.get('story'))
		
		template_values = {
			'story':story,
		}
		
		path = os.path.join(os.path.dirname(__file__), 'templates/story_detail.html')
		self.response.out.write(template.render(path, append_base_template_values(template_values)))
		
class get_minigame(webapp.RequestHandler):
	"""
	Returns an HTML template for a minigame.
	
	Requires the following parameters:
	- type: the type of the minigame (truefalse, ...)
	"""
	
	@login_required
	def get(self):
		minigame_type = self.request.get('type')
		
		# get content
		import content
		if minigame_type == "truefalse":
			minigame = content.truefalse_en_dative_alternation
		elif minigame_type == "fib":
			minigame = content.fib_en_tenses
		elif minigame_type == "assoc":
			minigame = content.assoc_en_some_any
		elif minigame_type == "empty":
			minigame = None
		
		if minigame != None:
			# shuffle items
			from random import shuffle
			shuffle(minigame['items'])
			
			# add characters to items
			from random import choice
			from content import characters
			for i in minigame['items']:
				i['character'] = choice(characters)
		
		# generate template
		template_values = {
			'minigame': minigame,
		}
		path = os.path.join(os.path.dirname(__file__), 'templates/minigame_' + minigame_type + '.html')
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

class profile(webapp.RequestHandler):
	""" Updates the player's profile """
	
	@login_required
	
	def get(self):
		player = get_current_player()
		if player:
			if self.request.get('avatar'):
				player.avatar = db.Blob(self.request.get('avatar'))
				player.put()
				
		# generate template
		template_values = {
			
		}
		
		path = os.path.join(os.path.dirname(__file__), 'templates/player_detail.html')
		self.response.out.write(template.render(path, append_base_template_values(template_values)))
		
	def post(self):
		player = get_current_player()
		logging.debug("*****" + player.nickname)
		if player:
			if self.request.get('avatar'):
				avatar = self.request.get('avatar')
				logging.debug("*****" + avatar)
				player.avatar = db.Blob(avatar)
				player.put()
		self.redirect("/profile")

class get_image(webapp.RequestHandler):
	""" Gets the image data for a certain object.
	
	Requires:
	+ object_key: the key of a certain object
	+ image_property: the name of the Blob property.
	"""
	
	def get(self):
		from google.appengine.ext import db
		object = db.Model.get(self.request.get('object_key'))
		# image_data = object._properties[self.request.get('image_property')]
		image_data = object.avatar
		self.response.headers['Content-Type'] = 'image/jpeg'
		self.response.out.write(image_data)
		
class MainHandler(webapp.RequestHandler):  
	@login_required
	def get(self):
		player = get_current_player()
		if player == None:
			player = Player(user=users.get_current_user())
			player.put()
		self.redirect("/game")

# **********
# MAIN
# **********

def main():
	logging.getLogger().setLevel(logging.DEBUG)
	application = webapp.WSGIApplication([('/', MainHandler),
										('/get_player_score', get_player_score),
										('/get_player_leaderboard', get_player_leaderboard),
										('/game', get_game),
										('/story', get_story),
										('/minigame', get_minigame),
										('/get_image',get_image),
										('/profile', profile),
								],
											debug=True)

	wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
	main()

