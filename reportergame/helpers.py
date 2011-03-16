'''
Created on January 5th, 2011

@author: Frederik Cornillie

'''

from google.appengine.api import users

from models import *

# **********
# HELPER FUNCTIONS
# **********

def get_current_player():
	player_query = Player.gql("WHERE user = :1", users.get_current_user())
	if player_query.count() > 0:
		player = player_query[0]
		return player
	else:
		return None
		
def get_current_session():
	session = GameSession.gql("WHERE game=:1 AND player=:2", Game.all()[0], get_current_player()) 		# game should be changed to whatever game is needed
	if session.count() == 0:
		game = Game.all()[0]	# needs to be changed to whatever game was requested
		session = GameSession(game=game, player=get_current_player())
		session.coins = game.start_coins
		session.level = Level.gql("WHERE game = :1 AND number = :2", game, 1)[0]
		session.put()
	elif session.count() == 1:
		session = session[0]
	return session
	
def append_base_template_values(template_values):
	"""
	Appends the values for the base template to the values for the requested view. The appended values are:
	- player: the current user
	- logouturl: the logout url
	
	Requires a dictionary containing the values for the requested view.
	"""
	
	player = get_current_player()
	template_values['player'] = player
	template_values['logouturl'] = users.create_logout_url("/")
	template_values['is_current_user_admin'] = users.is_current_user_admin()
	if player is not None:
		game_session = player.get_last_game_session()
		if game_session is not None:
			template_values['game_key'] = game_session.game.key()
	
	return template_values