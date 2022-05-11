# -*- coding: utf-8 -*-
#------------------------------------------------------------
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                             # Es muy lento en PY2.  En PY3 es nativo
else:
    import urlparse                                             # Usamos el nativo de PY2 que es más rápido

import re

from core import scrapertools
from core import servertools
from core.item import Item
from platformcode import config, logger
from core import httptools

canonical = {
             'channel': 'mporno', 
             'host': config.get_setting("current_host", 'mporno', default=''), 
             'host_alt': ["http://mporno.tv"], 
             'host_black_list': [], 
             'pattern': ['href="?([^"|\s*]+)["|\s*]\s*rel="?stylesheet"?'], 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Novedades" , action="lista", url=host + "/most-recent/"))
    itemlist.append(Item(channel=item.channel, title="Mejor valoradas" , action="lista", url=host + "/top-rated/"))
    itemlist.append(Item(channel=item.channel, title="Mas vistas" , action="lista", url=host + "/most-viewed/"))
    itemlist.append(Item(channel=item.channel, title="Longitud" , action="lista", url=host + "/longest/"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "/channels/"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "-")
    item.url = "%s/search/videos/%s/page1.html" % (host, texto)
    try:
        return lista(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def categorias(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    patron  = '<h3><a href="([^"]+)">(.*?)</a> <small>(.*?)</small></h3>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle,cantidad in matches:
        scrapedplot = ""
        scrapedthumbnail = ""
        scrapedtitle = "%s %s" %(scrapedtitle,cantidad)
        itemlist.append(Item(channel=item.channel, action="lista", title=scrapedtitle, url=scrapedurl,
                              thumbnail=scrapedthumbnail , plot=scrapedplot) )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)
    patron  = '<img class="content_image" src="([^"]+).mp4/.*?" alt="([^"]+)".*?this.src="(.*?)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle,scrapedthumbnail in matches:
        contentTitle = scrapedtitle
        title = scrapedtitle
        thumbnail = scrapedthumbnail
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, url=scrapedurl, thumbnail=thumbnail,
                              fanart=thumbnail, plot=plot, server= "directo", contentTitle=contentTitle))
    next_page_url = scrapertools.find_single_match(data,'<a href=\'([^\']+)\' class="next">Next &gt;&gt;</a>')
    if next_page_url!="":
        next_page_url = urlparse.urljoin(item.url,next_page_url)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page_url) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    url = item.url.replace("/thumbs/", "/videos/") + ".mp4"
    itemlist.append(Item(channel=item.channel, action="play", title= "Directo", url=url, contentTitle=item.contentTitle))
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    url = item.url.replace("/thumbs/", "/videos/") + ".mp4"
    itemlist.append(Item(channel=item.channel, action="play", server= "directo", url=url, contentTitle=item.contentTitle))
    return itemlist