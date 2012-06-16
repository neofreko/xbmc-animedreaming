

import sys
import xbmc, xbmcgui, xbmcplugin
import urllib2
import urllib

from bs4 import BeautifulSoup
import soupselect; soupselect.monkeypatch()
import re
import feedparser

#sys.path.append("./xbmc_env/bin/python2.5") 
#sys.path.append("./xbmc_env/lib/python2.5") 
#sys.path.append("./xbmc_env/lib/python2.5/site-packages") 

# plugin modes
MODE_FIRST = 10
MODE_SECOND = 20

# parameter keys
PARAMETER_KEY_MODE = "mode"

# menu item names
FIRST_SUBMENU = "First Submenu"
SECOND_SUBMENU = "Second Submenu"

# plugin handle
handle = int(sys.argv[1])

# utility functions
def parameters_string_to_dict(parameters):
    ''' Convert parameters encoded in a URL to a dict. '''
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict

def addDirectoryItem(name, isFolder=True, parameters={}):
    ''' Add a list item to the XBMC UI.'''
    li = xbmcgui.ListItem(name)
    url = sys.argv[0] + '?' + urllib.urlencode(parameters)
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=isFolder)

def addLink(name,url):
        ok=True
        liz=xbmcgui.ListItem(name)
        liz.setInfo( type="video",  infoLabels = {
                'title' : name 
        })
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        return ok

def fetchUrl(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    html=response.read()
    response.close()
    return html

'''
XBMC plays mp4
'''
def get_video_url(provider_name, url):    
    #html = fetchUrl('http://www.animedreaming.tv/fairy-tail-episode-134/')
    html = fetchUrl(url)
    soup = BeautifulSoup(html)

    video_url = ''
    if provider_name == 'rutube':
        video_url = rutube_get_video_url(url)
    else:
        providers = soup.findAll('div', {'class': 'videoembed activeembed'})
        provider_page_url = providers[0].contents[0]['src']
        
        if (provider_name == 'sapo'):
            video_url = sapo_get_video_url(provider_page_url)

        #if (provider_name == 'yourupload'):
        #    video_url = yourupload_get_video_url(provider_page_url)

        if (provider_name == 'uploadc'):
            video_url = uploadc_get_video_url(provider_page_url)

        if (provider_name == 'mp4upload'):
            video_url = mp4upload_get_video_url(provider_page_url)

    return video_url

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

        data = {'provider_name': provider_name, 
            'provider_url': provider_url}

        result.append(data)

    return result

def sapo_get_video_url(url):
    html = fetchUrl(url)
    match=re.compile("url:\s+'(http:.*?\.mp4)'").findall(html)
    if (match):
        return match[0]
    else:
        return ''

def yourupload_get_video_url(url):
    # http://f12.yourupload.com/stream/cf700038dfd54ec37a89910b0f4e104e
    html = fetchUrl(url)
    match=re.compile("(http:.*?yourupload\.com/stream.*)'").findall(html)

    if (match):
        return match[0]
    else:
        return ''

def uploadc_get_video_url(url):
    #http://www.uploadc.com/embed-0o7mous7l569.html
    #file=http://www15.uploadc.com:182/d/tigndl5mvsulzrqmbpn3fanql3bs6fhgkigvscwiuawmu2go2c5z447d/135.mp4
    html = fetchUrl(url)
    match=re.compile("http:.*?:182/.*?\.mp4").findall(html)

    if (match):
        return match[0]
    else:
        return ''

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

# UI builder functions
def show_root_menu():
    ''' Show the plugin root menu. '''
    '''addDirectoryItem(name=FIRST_SUBMENU, parameters={ PARAMETER_KEY_MODE: MODE_FIRST }, isFolder=True)
    addDirectoryItem(name=SECOND_SUBMENU, parameters={ PARAMETER_KEY_MODE: MODE_SECOND }, isFolder=True)
    '''
    
    d = feedparser.parse('http://www.animedreaming.tv/rss.xml')
    for i in d.entries:
        name = i.title
        link = i.link
        addDirectoryItem(name, isFolder=True, parameters ={'link': link, 'mode': MODE_FIRST})
        #video_url = get_video_url(link) 
        #if (video_url):
        #    addLink(name, video_url)
    xbmcplugin.endOfDirectory(handle=handle, succeeded=True)
    
def show_first_submenu():
    ''' Show first submenu. '''
    params = parameters_string_to_dict(sys.argv[2])
    link = params.get('link', "")
    providers = get_video_providers(urllib.unquote(link))
    for provider in providers:
        print "processing %s from %s" % (provider['provider_name'], provider['provider_url'])
        video_url = get_video_url(provider['provider_name'], provider['provider_url'])
        print video_url
        if (video_url):
            addLink("Play from %s" % provider['provider_name'], video_url)
        #addDirectoryItem(provider['provider_name'], isFolder=True, parameters ={'link': provider['provider_url'], 'mode': MODE_SECOND})
    #addLink()
    xbmcplugin.endOfDirectory(handle=handle, succeeded=True)

def show_second_submenu():
    ''' Show second submenu. '''
    params = parameters_string_to_dict(sys.argv[2])
    link = params.get('link', "")
    video_url = get_video_url(urllib.unquote(link)) 
    if (video_url):
        addLink("Play from %s" % name, video_url)
    xbmcplugin.endOfDirectory(handle=handle, succeeded=True)

# parameter values
params = parameters_string_to_dict(sys.argv[2])
mode = int(params.get(PARAMETER_KEY_MODE, "0"))
print "##########################################################"
print("Mode: %s" % mode)
print "##########################################################"

# Depending on the mode, call the appropriate function to build the UI.
if not sys.argv[2]:
    # new start
    ok = show_root_menu()
elif mode == MODE_FIRST:
    ok = show_first_submenu()
elif mode == MODE_SECOND:
    ok = show_second_submenu()