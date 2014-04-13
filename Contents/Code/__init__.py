# Based on akkifokkusu's Wrestling Metadata Agent (https://forums.plex.tv/index.php/topic/73947-alpha-wrestling-metadata-agent/)
import unicodedata

TVRAGE_SEARCH_URL = 'http://services.tvrage.com/feeds/search.php?show=%s'
TVRAGE_SHOW_INFO_URL = 'http://services.tvrage.com/myfeeds/showinfo.php?key=P8q4BaUCuRJPYWys3RBV&sid=%s'
TVRAGE_EP_INFO_URL = 'http://services.tvrage.com/myfeeds/episode_list.php?key=P8q4BaUCuRJPYWys3RBV&sid=%s'

TVDB_SEARCH_URL = 'http://thetvdb.com/api/GetSeries.php?seriesname=%s'
TVDB_BANNER_LIST_URL = 'http://thetvdb.com/api/D4DDDAEFAD083E6F/series/%s/banners.xml'
TVDB_BANNER_BASE_URL = 'http://thetvdb.com/banners/'

def Start():

	HTTP.CacheTime = CACHE_1DAY


class TVRageAgent(Agent.TV_Shows):

	name = 'TVRage'
	languages = [Locale.Language.English]
	primary_provider = True

	def search(self, results, media, lang):
		if Prefs["tvrcache"]:
			HTTP.ClearCache()
		Log("Working!:")
		media.show = unicodedata.normalize('NFC', unicode(media.show)).strip()
		Log("Show?: " + media.show)
		tvrsearchurl = TVRAGE_SEARCH_URL % String.Quote(media.show,True)
		Log("Searching using URL: " + tvrsearchurl)
		tvrxml = XML.ElementFromURL(tvrsearchurl)
		curscore = 49
		if media.show.lower().replace('-',' ') == tvrxml.xpath("//show/name")[0].text.lower().replace('-',' '):
			curscore = 100
		for match in tvrxml.xpath("//show"):
			nextResult = MetadataSearchResult(id=str(match.xpath("./showid")[0].text),name=str(match.xpath("./name")[0].text),year=match.xpath("./started")[0].text,score=curscore,lang=lang)
			results.Append(nextResult)
			Log(repr(nextResult))
			curscore = curscore - 1

	def update(self, metadata, media, lang):
		if Prefs["tvrcache"]:
			HTTP.ClearCache()
		Log("Working!:")
		Log(metadata.id)
		tvrxml = XML.ElementFromURL(TVRAGE_SHOW_INFO_URL % metadata.id)
		metadata.title = tvrxml.xpath("/Showinfo/showname")[0].text
		metadata.studio = tvrxml.xpath("/Showinfo/network")[0].text
		metadata.duration = int(tvrxml.xpath("/Showinfo/runtime")[0].text) * 60 * 1000
		metadata.originally_available_at = Datetime.ParseDate(tvrxml.xpath("/Showinfo/started")[0].text).date()
		metadata.genres = [genre.text for genre in tvrxml.xpath("/Showinfo/genres/genre")]
		if tvrxml.xpath("/Showinfo/summary"):
			metadata.summary = tvrxml.xpath("/Showinfo/summary")[0].text
		metadata.countries = [tvrxml.xpath("/Showinfo/origin_country")[0].text]
		metadata.tags = [tvrxml.xpath("/Showinfo/classification")[0].text]
		
		showname = metadata.title.lower()
		try:
			tvdsearchurl = TVDB_SEARCH_URL % String.Quote(media.show,True)
			Log("Searching using URL: " + tvdsearchurl)
			tvdxml = XML.ElementFromURL(tvdsearchurl)
			curscore = 49
			if media.show.lower().replace('-',' ') == tvdxml.xpath("//Series/SeriesName")[0].text.lower().replace('-',' '):
				curscore = 100
			for match in tvdxml.xpath("//Series"):
				nextResult = MetadataSearchResult(id=str(match.xpath("./seriesid")[0].text),name=str(match.xpath("./SeriesName")[0].text),year=match.tvrxml.xpath("/Showinfo/started")[0].text,score=curscore,lang=lang)
				results.Append(nextResult)
				Log(repr(nextResult))
				curscore = curscore - 1
		except:
			seriesid = ""
		
		if len(seriesid) > 0:
			Log("Banner url: " + TVDB_BANNER_LIST_URL % seriesid)
			xml2 = XML.ElementFromURL(TVDB_BANNER_LIST_URL % seriesid)
			for banner in xml2.xpath("/Banners/Banner"):
				Log("Working on banner id: " + banner.xpath("./id")[0].text)
				Log("Banner rating: " + str(banner.xpath("./Rating")[0].text))
				banner_sort = None
				if banner.xpath("./Rating")[0].text is not None:
					banner_sort = int(10 - float(banner.xpath("./Rating")[0].text))
				banner_url = TVDB_BANNER_BASE_URL + banner.xpath("./BannerPath")[0].text
				banner_type = banner.xpath("./BannerType")[0].text
				if banner_type == "fanart":
					if banner_url not in metadata.art:
						try:
							banner_thumb = TVDB_BANNER_BASE_URL + banner.xpath("./ThumbnailPath")[0].text
							metadata.art[banner_url] = Proxy.Preview(HTTP.Request(banner_thumb), banner_sort)
						except:
							metadata.art[banner_url] = Proxy.Media(HTTP.Request(banner_url), banner_sort)
				elif banner_type == "poster":
					if banner_url not in metadata.posters:
						try:
							banner_thumb = TVDB_BANNER_BASE_URL + banner.xpath("./ThumbnailPath")[0].text
							metadata.posters[banner_url] = Proxy.Preview(HTTP.Request(banner_thumb), banner_sort)
						except:
							metadata.posters[banner_url] = Proxy.Media(HTTP.Request(banner_url), banner_sort)
				elif banner_type == "series":
					if banner_url not in metadata.banners:
						metadata.banners[banner_url] = Proxy.Media(HTTP.Request(banner_url), banner_sort)
				elif banner_type == "season":
					banner_season = banner.xpath("./Season")[0].text
					if banner_season in media.seasons:
						if banner.xpath("./BannerType2")[0].text == "season":
							if banner_url not in metadata.seasons[banner_season].posters:
								metadata.seasons[banner_season].posters[banner_url] = Proxy.Media(HTTP.Request(banner_url), banner_sort)
						elif banner.xpath("./BannerType2")[0].text == "seasonwide":
							if banner_url not in metadata.seasons[banner_season].banners:
								metadata.seasons[banner_season].banners[banner_url] = Proxy.Media(HTTP.request(banner_url), banner_sort)

		Log("Working on seasons!")
		xml3 = XML.ElementFromURL(TVRAGE_EP_INFO_URL % metadata.id)
		for season in xml3.xpath("/Show/Episodelist/Season"):
			season_no = season.get("no")
			if season_no in media.seasons:
				Log("Season matched: " + season_no)
				for episode in season.xpath("./episode"):
					episode_no = str(int(episode.xpath("./seasonnum")[0].text))
					if episode_no in media.seasons[season_no].episodes:
						Log("Episode matched: " + episode_no)
						ep_object = metadata.seasons[season_no].episodes[episode_no]
						ep_object.title = episode.xpath("./title")[0].text
						if episode.xpath("./summary"):
							ep_object.summary = episode.xpath("./summary")[0].text
						try:
							Log("Date: " + str(Datetime.ParseDate(episode.xpath("./airdate")[0].text).date()))
							ep_object.originally_available_at = Datetime.ParseDate(episode.xpath("./airdate")[0].text).date()
						except ValueError:
							Log("Invalid date.")
						Log("Abs: " + str(int(episode.xpath("./epnum")[0].text)))
						ep_object.absolute_index = int(episode.xpath("./epnum")[0].text)
						if len(episode.xpath("./screencap")) > 0:
							thumb_url = episode.xpath("./screencap")[0].text
							if thumb_url not in ep_object.thumbs:
								ep_object.thumbs[thumb_url] = Proxy.Media(HTTP.Request(thumb_url))
		Log("Done with seasons!")
