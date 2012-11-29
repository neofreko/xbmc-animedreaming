
import sys
import xbmc, xbmcgui, xbmcplugin
import urllib2
import urllib
import CommonFunctions
common = CommonFunctions

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
MODE_SEARCH = 30
MODE_RESULT = 40
# parameter keys
PARAMETER_KEY_MODE = "mode"

# menu item names
FIRST_SUBMENU = "First Submenu"
SECOND_SUBMENU = "Second Submenu"

# plugin handle
handle = int(sys.argv[1])

#patterns
YOURUPLOAD = re.compile("content.*?(http:.*?\.mp4)")
SAPO = re.compile("url:\s+'(http:.*?\.mp4)'")
MP4UPLOAD = re.compile("(http:.*?:182/.*?\.mp4)")
UPLOADC = re.compile("(http:.*?:182/.*?\.mp4)")
ENGINE = re.compile("url:\s+'(http.*?mp4.*?)'")
VIDEOWEED = re.compile("advURL.*?(http.*?file.*?)\"")
VIDEONEST = re.compile("(http.*?mp4)")
UPLOAD2 = re.compile("video=(http.*?mp4.*?)\&")
RUTUBE = re.compile("file=(http.*?iflv)")

VIDEOEMBED = re.compile("div class=\"videoembed activeembed\".*?src=\"(http.*?)\"")

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
    html = fetchUrl(url)
    
    match = False
    video_url = ''
    if provider_name == 'rutube':
        match=RUTUBE.search(html)
    else:
        try:
       
           provider_page_url = VIDEOEMBED.search(html).group(1)
           html = fetchUrl(provider_page_url)
           
           if (provider_name == 'sapo'):
              match=SAPO.search(html)
           elif (provider_name == 'yourupload'):
              match=YOURUPLOAD.search(html)
           elif (provider_name == 'uploadc'):
              match=UPLOADC.search(html)
           elif (provider_name == 'upload2'):
              match=UPLOAD2.search(html)
           elif (provider_name == 'mp4upload'):
              match=MP4UPLOAD.search(html)
           #elif (provider_name == 'videoweed'):
           #  match=VIDEOWEED.search(html)
           elif (provider_name == 'engine'):
              match=ENGINE.search(html)
           elif (provider_name == 'videonest'):
              match=VIDEONEST.search(html)
           else:
             try:
                print "AD-TV: unknown provider - "+provider_page_url+"\n"+html
             except:
                print "AD-TV: unknown provider - "+provider_page_url+"\n"+repr(html)
             match=VIDEONEST.search(html)

        except Exception as inst:
           print "AD-TV: parsing problem - \n"+html, inst

    if(match):
        video_url = match.group(1)
        if (provider_name == 'engine'):
            video_url = urllib.unquote(video_url)

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

# UI builder functions
def show_root_menu():
    ''' Show the plugin root menu. '''
    '''addDirectoryItem(name=FIRST_SUBMENU, parameters={ PARAMETER_KEY_MODE: MODE_FIRST }, isFolder=True)
    addDirectoryItem(name=SECOND_SUBMENU, parameters={ PARAMETER_KEY_MODE: MODE_SECOND }, isFolder=True)
    '''
    
    addDirectoryItem(' - Search - ', isFolder=True, parameters ={'mode': MODE_SEARCH})

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

def getSearch():
    query = common.getUserInput('Search', '')
    if not query:
        return False
    html = fetchUrl('http://www.animedreaming.tv/search.php?searchquery='+urllib.quote_plus(query))
    for link in re.compile('<li.*?href="(http://www.animedreaming.tv/.*?)">(.*?)</a>').findall(html):
        addDirectoryItem(re.sub('<b>|</b>','*',link[1]), isFolder=True, parameters ={'link': link[0], 'mode': MODE_RESULT})
    xbmcplugin.endOfDirectory(handle=handle, succeeded=True)

def parseResults():
    params = parameters_string_to_dict(sys.argv[2])
    link = params.get('link', "")
    html = fetchUrl(urllib.unquote(link))
    for link in re.compile('<li.*?href="(http://www.animedreaming.tv/.*?)".*?>(.*?)&nbsp;<').findall(html):
        addDirectoryItem(link[1], isFolder=True, parameters ={'link': link[0], 'mode': MODE_FIRST})
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
elif mode == MODE_SEARCH:
    ok = getSearch()
elif mode == MODE_RESULT:
    ok = parseResults()
