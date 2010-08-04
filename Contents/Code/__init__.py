#TVRage "better than nothing" poster grabber
GOOGLE_AJAX     = 'http://ajax.googleapis.com/ajax/services/search/images?v=1.0&rsz=large&q="%s"+site:tvrage.com'
TVRAGE_SEARCH   = 'http://services.tvrage.com/feeds/search.php?show=%s'

def Start():
  HTTP.CacheTime = CACHE_1DAY
  
class TVRageAgent(Agent.TV_Shows):
  name = 'TVRage'
  languages = [Locale.Language.English]
  primary_provider = False
  contributes_to = ['com.plexapp.agents.thetvdb']
  
  def search(self, results, media, lang):
    if media.primary_metadata.first_aired:
      year = ' ' + str(media.primary_metadata.first_aired).split('-')[0]
    else:
      year = ''  
    name = media.primary_metadata.name + ' ' + year
    
    TVrageShowUrl = XML.ElementFromURL(TVRAGE_SEARCH % String.Quote(name.encode('utf-8'))).xpath('.//show')[0].xpath('link')[0].text

    if len(TVrageShowUrl) > 0:
      results.Append(MetadataSearchResult(id = TVrageShowUrl, score = 100))
          
  def update(self, metadata, lang):
    # Poster.
    url = metadata.id
    try:
      if url not in metadata.posters:
        imgSrc = HTML.ElementFromURL(url).xpath("//tr[@id='iconn1']//img")[0].get('src')
        metadata.posters[url] = Proxy.Media(HTTP.Request(imgSrc))
    except:
      pass  