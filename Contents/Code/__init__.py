def Start():

	HTTP.CacheTime = CACHE_1DAY


class TVRageAgent(Agent.TV_Shows):

	name = 'TVRage'
	languages = [Locale.Language.English]
	primary_provider = False
	contributes_to = []

	def search(self, results, media, lang):
		pass

	def update(self, metadata, media, lang):
		pass
