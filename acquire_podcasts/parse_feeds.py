import feedparser
url = 'http://feed.thisamericanlife.org/talpodcast'
d = feedparser.parse(url)
d['feed']['title']
