#!/usr/bin/python
#
#
# Written by MetalChris
# Released under GPL(v2 or Later)

import xbmcaddon, urllib.request, urllib.parse, urllib.error, xbmcgui, xbmcplugin, urllib.request, urllib.error, urllib.parse, re, sys
from bs4 import BeautifulSoup
import html5lib
import json
from datetime import datetime, timedelta as td


now = (str(datetime.utcnow() - td(hours=5)).split(' ')[0]).replace('-','/')
cbcnow = now.split('/')
now = cbcnow[1] + '/' + cbcnow[2] + '/' + cbcnow[0]

_addon = xbmcaddon.Addon()
_addon_path = _addon.getAddonInfo('path')
selfAddon = xbmcaddon.Addon(id='plugin.video.cbc-sports')
translation = selfAddon.getLocalizedString

defaultimage = 'special://home/addons/plugin.video.cbc-sports/icon.png'
defaultfanart = 'special://home/addons/plugin.video.cbc-sports/fanart.jpg'
defaultvideo = 'special://home/addons/plugin.video.cbc-sports/icon.png'
defaulticon = 'special://home/addons/plugin.video.cbc-sports/icon.png'
baseurl = 'http://www.cbc.ca/sports'
basefeed = 'http://tpfeed.cbc.ca/f/ExhSPC/vms_5akSXx4Ng_Zn?byGuid='
mp4base = 'http://main.mp4.cbc.ca/prodVideo/sports/'
cbcfeedbase = 'http://tpfeed.cbc.ca/f/ExhSPC/vms_5akSXx4Ng_Zn?range=1-10&byCategoryIds='
cbcfeedpost = '&sort=pubDate|desc'
pluginhandle = int(sys.argv[1])
addon_handle = int(sys.argv[1])
confluence_views = [500,501,502,503,504,508]
plugin = 'CBC Sports'


def CATEGORIES():
	dir30003 = xbmcaddon.Addon().getLocalizedString(30003)
	dir30004 = xbmcaddon.Addon().getLocalizedString(30004)
	dir30006 = xbmcaddon.Addon().getLocalizedString(30006)
	dir30008 = xbmcaddon.Addon().getLocalizedString(30008)
	addDir(dir30003, 'http://www.cbc.ca/sports-content/v11/includes/json/schedules/broadcast_schedule.json', 1, defaultimage)
	addDir(dir30004, cbcfeedbase + '461602883775' + cbcfeedpost, 6, defaultimage)
	addDir(dir30006, cbcfeedbase + '461477443878' + cbcfeedpost, 6, defaultimage)
	addDir(dir30008, cbcfeedbase + '461088323897' + cbcfeedpost, 6, defaultimage)
	xbmcplugin.endOfDirectory(int(sys.argv[1]))


#1
def INDEX(url):
	jresponse = urllib.request.urlopen(url)
	jdata = json.load(jresponse);i=0
	item_dict = jdata
	count = len(item_dict['schedule'])
	for item in jdata['schedule']:
		#title = ((jdata['schedule'][i]['ti']).replace('&amp;','&').encode('ASCII', 'ignore'))
		title = (jdata['schedule'][i]['ti'])
		#title = (title.split('-'))[0]
		if 'Hockey Night' in title:
			i = i + 1
			continue
		etime = jdata['schedule'][i]['stt']
		#dtime = (etime.split(' ',1)[-1]).split(' ',1)[0]
		edate = etime.split(' ',1)[0]
		if edate < now:
			i = i + 1
			continue
		#xbmc.log('EDATE: ' + str(edate))
		etime = etime.split(' ',1)[-1].upper().lstrip("0")
		url = baseurl + jdata['schedule'][i]['url']
		image = jdata['schedule'][i]['thumb']
		if edate == now:
			title = etime + ' - ' + title
		else:
			title = edate + ' - ' + etime + ' - ' + title
		i=i+1
		addDir2(title, url, 2, image)
	xbmcplugin.endOfDirectory(int(sys.argv[1]))


#2
def IFRAME(name,url):
	#name = (name.split(' - '))[2]
	xbmc.log('url: ' + str(url))
	data = get_html(url)
	try: mediaId = re.compile("mediaId': '(.+?)'").findall(str(data))[0]
	except IndexError:               
		xbmcgui.Dialog().notification(name, translation(30000), defaultimage, 5000, False)
		return
	furl = basefeed + mediaId
	xbmc.log('furl: ' + str(furl))
	jresponse = urllib.request.urlopen(furl)
	jdata = json.load(jresponse)
	smil_url = jdata['entries'][0]['content'][0]['url']
	xbmc.log('smil_url: ' + str(smil_url))
	smil = get_html(smil_url)
	contents = BeautifulSoup(smil,'html5lib')
	stream = (re.compile('video src="(.+?)"').findall(str(contents))[0]).replace('/z/','/i/').replace('manifest.f4m','master.m3u8')
	listitem = xbmcgui.ListItem(name)
	listitem.setArt({'thumb': defaultimage, 'icon': defaultimage})	
	xbmc.Player().play( stream, listitem )
	sys.exit()
	xbmcplugin.endOfDirectory(int(sys.argv[1]))


#6
def VIDEOS(url):
	jresponse = urllib.request.urlopen(url)
	jdata = json.load(jresponse);i=0
	item_dict = jdata
	count = len(item_dict['entries'])
	for item in jdata['entries']:
		#title = (jdata['entries'][i]['title']).encode('utf-8').replace('&amp;','&')
		title = (jdata['entries'][i]['title'])
		url = jdata['entries'][i]['content'][0]['url']
		image = jdata['entries'][i]['defaultThumbnailUrl']
		addDir2(title, url, 7, image);i=i+1
	xbmc.log('url:' + str(url))
	xbmcplugin.endOfDirectory(int(sys.argv[1]))
		

#7
def GET_STREAM(name,url):
	smil = get_html(url)
	contents = BeautifulSoup(smil,'html5lib')
	stream = (re.compile('src="(.+?)"').findall(str(contents))[0])
	if mp4base not in stream:
		stream = stream
	xbmc.log('stream:' + str(stream))
	listitem = xbmcgui.ListItem(name)
	listitem.setArt({'thumb': defaultimage, 'icon': defaultimage})	
	xbmc.Player().play( stream, listitem )
	sys.exit()
	xbmcplugin.endOfDirectory(int(sys.argv[1]))


#99
def play(url):
	item = xbmcgui.ListItem(path=url)
	return xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)


def striphtml(data):
	p = re.compile(r'<.*?>')
	return p.sub('', data)


def sanitize(data):
	output = ''
	for i in data:
		for current in i:
			if ((current >= '\x20') and (current <= '\xD7FF')) or ((current >= '\xE000') and (current <= '\xFFFD')) or ((current >= '\x10000') and (current <= '\x10FFFF')):
			   output = output + current
	return output



def get_html(url):
	req = urllib.request.Request(url)
	req.add_header('User-Agent','User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:44.0) Gecko/20100101 Firefox/44.0')

	try:
		response = urllib.request.urlopen(req)
		code = response.getcode()
		xbmc.log('CODE: ' + str(code))
		if code == 403:              
			xbmcgui.Dialog().notification(name, translation(30001), defaultimage, 5000, False)
			sys.exit()
		elif code == 22:              
			xbmcgui.Dialog().notification(name, translation(30010), defaultimage, 5000, False)
			sys.exit()	    
		html = response.read()
		response.close()
	except urllib.error.URLError:              
		xbmcgui.Dialog().notification(name, translation(30002), defaultimage, 5000, False)
		sys.exit()	 
	return html


def get_params():
	param = []
	paramstring = sys.argv[2]
	if len(paramstring) >= 2:
		params = sys.argv[2]
		cleanedparams = params.replace('?', '')
		if (params[len(params) - 1] == '/'):
			params = params[0:len(params) - 2]
		pairsofparams = cleanedparams.split('&')
		param = {}
		for i in range(len(pairsofparams)):
			splitparams = {}
			splitparams = pairsofparams[i].split('=')
			if (len(splitparams)) == 2:
				param[splitparams[0]] = splitparams[1]

	return param


def addDir(name, url, mode, iconimage, fanart=False, infoLabels=True):
	u = sys.argv[0] + "?url=" + urllib.parse.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.parse.quote_plus(name) + "&iconimage=" + urllib.parse.quote_plus(iconimage)
	ok = True
	liz = xbmcgui.ListItem(name)
	liz.setInfo(type="Video", infoLabels={"Title": name})
	liz.setProperty('IsPlayable', 'true')
	if not fanart:
		fanart=defaultfanart
	liz.setArt({'thumb': iconimage, 'icon': iconimage, 'fanart': fanart})	
	ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
	return ok


def addDir2(name,url,mode,iconimage, fanart=False, infoLabels=False):
		u=sys.argv[0]+"?url="+urllib.parse.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.parse.quote_plus(name)
		ok=True
		liz = xbmcgui.ListItem(name)
		liz.setInfo( type="Video", infoLabels={ "Title": name } )
		if not fanart:
			fanart=defaultfanart
		liz.setArt({'thumb': iconimage, 'icon': iconimage, 'fanart': fanart})	
		ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
		return ok


def unescape(s):
	p = htmllib.HTMLParser(None)
	p.save_bgn()
	p.feed(s)
	return p.save_end()	


params = get_params()
url = None
name = None
mode = None
cookie = None

try:
	url = urllib.parse.unquote_plus(params["url"])
except:
	pass
try:
	name = urllib.parse.unquote_plus(params["name"])
except:
	pass
try:
	mode = int(params["mode"])
except:
	pass

xbmc.log("Mode: " + str(mode))
xbmc.log("URL: " + str(url))
xbmc.log("Name: " + str(name))

if mode == None or url == None or len(url) < 1:
	xbmc.log("CBC Sports Menu")
	CATEGORIES()
elif mode == 1:
	xbmc.log("CBC Sports Live")
	INDEX(url)
elif mode == 2:
	xbmc.log("CBC Sports Play Live Event")
	IFRAME(name,url)
elif mode == 6:
	xbmc.log("CBC Sports Videos")
	VIDEOS(url)
elif mode == 7:
	xbmc.log("CBC Sports Get Archive Stream")
	GET_STREAM(name,url)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
