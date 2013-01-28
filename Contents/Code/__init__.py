#TVRage "better than nothing" poster grabber
TVRAGE_SEARCH = 'http://services.tvrage.com/feeds/search.php?show=%s'

def Start():
  HTTP.CacheTime = CACHE_1DAY

class TVRageAgent(Agent.TV_Shows):
  name = 'TVRage'
  languages = [Locale.Language.English]
  primary_provider = False
  contributes_to = ['com.plexapp.agents.thetvdb']

  def search(self, results, media, lang):
    pass

  def update(self, metadata, media, lang):
    pass