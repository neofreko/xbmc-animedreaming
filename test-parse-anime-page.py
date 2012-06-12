import urllib2
from bs4 import BeautifulSoup
import re
import soupselect; soupselect.monkeypatch()


def fetchUrl(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    html=response.read()
    response.close()
    return html

def get_video_url():	
	html = fetchUrl('http://www.animedreaming.tv/fairy-tail-episode-134/')
	soup = BeautifulSoup(html)
	providers = soup.findAll('div', {'class': 'videoembed activeembed'})
	provider_page_url = providers[0].contents[0]['src']

	return sapo_get_video_url(provider_page_url)

def sapo_get_video_url(url):
	html = fetchUrl(url)
	match=re.compile("url:\s+'(http:.*?\.mp4)'").findall(html)

	return match[0]

def get_video_providers(url):
	html = fetchUrl(url)
	soup = BeautifulSoup(html)
	generic_video_items = soup.findSelect('div.generic-video-item')
	result = []
	for item in generic_video_items:
		ssoup = BeautifulSoup(str(item.contents))
		video_page = ssoup.findSelect('div.thumb')
		if (not video_page[0].a):
			provider_url = url
			temp = BeautifulSoup(str(video_page[0].contents))
			span = temp.findAll('span')
			provider_name = span[1].string
		else:
			provider_name = video_page[0].a.center.span.string
			provider_url = video_page[0].a['href']
		#print video_page[0]
		data = {'provider_name': provider_name, 
			'provider_url': provider_url}
		print data
		result.append(data)

	return result

print get_video_providers('http://www.animedreaming.tv/saint-seiya-omega-episode-11/')