from google.appengine.ext import db
import logging
import settings

class Player(db.Model):
	"""
	Our user.
	"""
	
	from datetime import datetime
	
	user = db.UserProperty()
	joined_date = db.DateTimeProperty(auto_now_add=True)
	friends_list = db.ListProperty(db.Key)		# XX ListProperties are limited to 5000 entries
	show_debug = db.BooleanProperty(default=False)
	_is_admin = db.BooleanProperty(default=False)
	
	@property
	def is_admin(self):
		return self._is_admin
		
	@property
	def nickname(self):
		return self.user.nickname()
		
	@property
	def email(self):
		return self.user.email()
		
	def friends(self, keys_only=False):
		"""
		Returns a list containing the friend instances.
		"""
		if self.friends_list:
			if keys_only:
				return self.friends_list
			else:
				return Player.get(self.friends_list)
		else:
			return []
	
	def friend(self, player_key):
		"""
		Adds a Player to the list of friends.
		
		Requires the key of the Player instance.
		
		Returns True if the Player has been added to the list. Returns False if the Player was already friended.
		"""
		if player_key != self.key():		# obviously you cannot friend yourself
			try:
				self.friends_list.index(player_key)
				return False
			except ValueError:
				self.friends_list.append(player_key)
				self.put()
				return True
	
	def defriend(self, player_key):
		"""
		Removes a Player from the list of friends.
		
		Requires the key of the Player instance.
		
		Returns True if the Player has been removed from the list. Returns False if the Player was not in the list.
		"""
		if player_key != self.key():		# obviously you cannot defriend yourself
			try:
				self.friends_list.index(player_key)
				self.friends_list.remove(player_key)
				self.put()
				return True
			except ValueError:
				return False
		
	def calculate_score(self, game_key):
		from datetime import datetime
		
		game = Game.get(game_key)
		session = self.sessions.filter("game", game)
		if session.count() == 0:
			session = GameSession(game=game, player=self)
			session.put()
		elif session.count() == 1:
			session = session[0]
	
	def get_last_game_session(self, game_key=None):
		game = None
		if game_key == None:
			if Game.all().count() > 0:
				game = Game.all()[0]
		else:
			game = Game.get(game_key)
		if game is None: 
			return None
		
		# XXX should take last played session, keep track of date of last played
		sessions = GameSession.gql("WHERE player = :1 AND game = :2", self, game)
		if sessions.count() == 0:
			session = GameSession(game=game, player=self)
			# XXX better add start currencies with factory method?? see: http://stackoverflow.com/questions/3279833/how-to-use-a-custom-init-of-an-app-engine-python-model-class-properly
			session.xp = game.start_xp
			session.put()
			session.update_absolutescore()
		else:
			session = sessions[0]
			
		return session
		
	def reward(self, coins_amount):
		try:
			game_session = self.get_last_game_session()
			game_session._coins += coins_amount
			game_session.update_absolutescore()
			game_session.put()
			return True
		except:
			return False

class Game(db.Model):
	title = db.StringProperty()
	subtitle = db.StringProperty()
	teaser = db.TextProperty()
	background_image = db.BlobProperty()
	maps_location = db.GeoPtProperty()
	maps_zoom = db.IntegerProperty()
	start_xp = db.IntegerProperty(default=0)
	admin_only = db.BooleanProperty(default=False)

class MiniGame(db.Model):
	title = db.StringProperty()

class Story(db.Model):
	game = db.ReferenceProperty(Game, collection_name="stories")
	title = db.StringProperty()
	headline = db.StringProperty()
	text = db.TextProperty()
	maps_location = db.GeoPtProperty()
	maps_zoom = db.IntegerProperty()
	minigames_list = db.ListProperty(db.Key)
	timestamp = db.DateTimeProperty(auto_now_add=True)
	
	@property
	def minigames(self):
		return MiniGame.get(self.minigames_list)

class GameSession(db.Model):
	from datetime import datetime
	
	game = db.ReferenceProperty(Game, required=True, collection_name="sessions")
	player = db.ReferenceProperty(Player, required=True, collection_name="sessions")
	_xp = db.IntegerProperty(default=0)
	badges_list = db.ListProperty(db.Key)
	absolutescore = db.IntegerProperty(default=1)
	last_played = db.DateTimeProperty(auto_now_add=True)
	
	def setxp(self, xp):
		self._xp = xp
		self.update_absolutescore()
	def getxp(self):
		return self._xp
	xp = property(getxp, setxp)
	
	def badges(self, keys_only=False):
		"""
		Returns a list containing the badge instances.
		"""
		if self.badges_list:
			if keys_only:
				return self.badges_list
			else:
				return Badge.get(self.badges_list)
		else:
			return []
	
	def earn_badge(self, badge_key):
		try:
			self.badges_list.index(badge_key)
			return False
		except ValueError:
			self.badges_list.append(badge_key)
			self.put()
			return True
	
	@property
	def score(self):
		score = {}
		
		score['xp'] = self.xp
		score['badges'] = len(self.badges_list)
		return score
	
	def update_absolutescore(self):
		self.absolutescore = self.xp + len(self.badges_list)
		self.put()

class Badge(db.Model):
	name = db.StringProperty()