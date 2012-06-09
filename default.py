

import sys
import xbmc, xbmcgui, xbmcplugin
import urllib2

from bs4 import BeautifulSoup
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
    url = sys.argv[0] + '?' + urllib2.urlencode(parameters)
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

def get_video_url(url):    
    #html = fetchUrl('http://www.animedreaming.tv/fairy-tail-episode-134/')
    html = fetchUrl(url)
    soup = BeautifulSoup(html)
    providers = soup.findAll('div', {'class': 'videoembed activeembed'})
    provider_page_url = providers[0].contents[0]['src']

    return sapo_get_video_url(provider_page_url)

def sapo_get_video_url(url):
    html = fetchUrl(url)
    match=re.compile("url:\s+'(http:.*?\.mp4)'").findall(html)
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
        #addDirectoryItem(name, isFolder=True, parameters ={'link': link, 'mode': MODE_FIRST})
        video_url = get_video_url(link) 
        if (video_url):
            addLink(name, video_url)
    xbmcplugin.endOfDirectory(handle=handle, succeeded=True)
    
def show_first_submenu():
    ''' Show first submenu. '''
    params = parameters_string_to_dict(sys.argv[2])
    link = params.get('link', "")
    
    #addLink()
    xbmcplugin.endOfDirectory(handle=handle, succeeded=True)

def show_second_submenu():
    ''' Show second submenu. '''
    for i in range(0, 10):
        name = "%s Item %d" % (SECOND_SUBMENU, i)
        addDirectoryItem(name, isFolder=False)
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