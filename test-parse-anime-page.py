import urllib2
from bs4 import BeautifulSoup
import re


def fetchUrl(url):
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
	response = urllib2.urlopen(req)
	html=response.read()
	response.close()
	return html

def get_video_url(provider_name, url):	
	'''
	html = fetchUrl('http://www.animedreaming.tv/fairy-tail-episode-134/')
	soup = BeautifulSoup(html)
	providers = soup.findAll('div', {'class': 'videoembed activeembed'})
	provider_page_url = providers[0].contents[0]['src']

	return sapo_get_video_url(provider_page_url)
	'''
	html = fetchUrl(url)
	soup = BeautifulSoup(html)
	providers = soup.findAll('div', {'class': 'videoembed activeembed'})
	provider_page_url = providers[0].contents[0]['src']
	video_url = ''
	if (provider_name == 'sapo'):
	    video_url = sapo_get_video_url(provider_page_url)
	if (provider_name == 'yourupload'):
	    video_url = yourupload_get_video_url(provider_page_url)
	if (provider_name == 'videoweed'):
	    video_url = videoweed_get_video_url(provider_page_url)

	return video_url

def sapo_get_video_url(url):
	html = fetchUrl(url)
	match=re.compile("url:\s+'(http:.*?\.mp4)'").findall(html)

	return match[0]

def yourupload_get_video_url(url):
	# http://f12.yourupload.com/stream/cf700038dfd54ec37a89910b0f4e104e
	html = fetchUrl(url)
	match=re.compile("(http:.*?yourupload\.com/stream.*)'").findall(html)

	return match[0]

def uploadc_get_video_url(url):
	#http://www.uploadc.com/embed-0o7mous7l569.html
	#file=http://www15.uploadc.com:182/d/tigndl5mvsulzrqmbpn3fanql3bs6fhgkigvscwiuawmu2go2c5z447d/135.mp4
	html = fetchUrl(url)
	match=re.compile("http:.*?:182/.*?\.mp4").findall(html)

	return match[0]

def mp4upload_get_video_url(url):
	#http://mp4upload.com/embed-2eq8hcuy3z8s-650x370.html
	#file=http%3A%2F%2Fwww3.mp4upload.com%2Ffiles%2F3%2F4jmk3grgqhy6le%2Fvideo.mp4
	html = fetchUrl(url)
	match=re.compile("http.*?files.*?mp4").findall(html)
	
	if (match):
		return match[0]
	else:
		return ''

def rutube_get_video_url(url):
	#http://www.animedreaming.tv/fairy-tail-episode-135/mirror-145196/
	#http://bl.rutube.ru/474cf104e9ca7abd1982334977a190ed.iflv
	html = fetchUrl(url)
	match=re.compile("file=(http.*?iflv)").findall(html)
	
	if (match):
		return match[0]
	else:
		return ''

def get_video_providers(url):
	html = fetchUrl(url)
	soup = BeautifulSoup(html)
	generic_video_items = soup.select('div.generic-video-item')
	result = []
	for item in generic_video_items:
		ssoup = BeautifulSoup(str(item.contents))
		video_page = ssoup.select('div.thumb')
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

print rutube_get_video_url("http://www.animedreaming.tv/fairy-tail-episode-135/mirror-145196/")
#print mp4upload_get_video_url("http://mp4upload.com/embed-2eq8hcuy3z8s-650x370.html")
#print yourupload_get_video_url("http://www.animedreaming.tv/yourup.php?id=cf700038dfd54ec37a89910b0f4e104e&w=660&h=359")
#print uploadc_get_video_url("http://www.uploadc.com/embed-0o7mous7l569.html")
#print get_video_providers('http://www.animedreaming.tv/saint-seiya-omega-episode-11/')
