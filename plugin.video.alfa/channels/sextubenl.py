# -*- coding: utf-8 -*-
#------------------------------------------------------------
from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools
from core import urlparse
from bs4 import BeautifulSoup

##https://www.sextube.nl  https://www.12milf.com  https://www.poldertube.nl  https://www.porntube.nl  
canonical = {
             'channel': 'sextubenl', 
             'host': config.get_setting("current_host", 'sextubenl', default=''), 
             'host_alt': ["https://www.sextube.nl/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "?filter=latest"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="lista", url=host + "?filter=most-viewed"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "?filter=popular"))
    itemlist.append(Item(channel=item.channel, title="Mas metraje" , action="lista", url=host + "?filter=longest"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "categorieen/"))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s?s=%s&filter=latest" % (host,texto)
    try:
        return lista(item)
    except Exception:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def categorias(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Borsten" , action="lista", url=host + "/?s=borsten&filter=latest",
                                thumbnail = "https://images.sextube.nl/output/1670347e76ec08d7713496749c2a4068/poster.jpg"))
    soup = create_soup(item.url)
    matches = soup.find_all('div', class_='video-block-cat')
    for elem in matches:
        logger.debug(elem)
        url = elem.a['href']
        title = elem.find('span', class_='title').text.strip()
        if elem.img.get("src", ""):
            thumbnail = elem.img['src']
        else:
            thumbnail = elem.img['data-src']
        cantidad = elem.find('div', class_='video-datas')
        if cantidad:
            title = "%s (%s)" %(title,cantidad.text.strip())
        url = urlparse.urljoin(item.url,url)
        thumbnail = urlparse.urljoin(item.url,thumbnail)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    return itemlist


def create_soup(url, referer=None, unescape=False):
    logger.info()
    if referer:
        data = httptools.downloadpage(url, headers={'Referer': referer}, canonical=canonical).data
    else:
        data = httptools.downloadpage(url, canonical=canonical).data
    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    return soup


def lista(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all('div', class_='video-block')
    for elem in matches:
        url = elem.find('a', class_='infos')['href']
        title = elem.find('a', class_='infos')['title']
        thumbnail = elem.img['data-src']
        time = elem.find('span', class_='duration').text.strip()
        quality = elem.find('span', class_='is-hd')
        if quality:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]HD[/COLOR] %s" % (time,title)
        else:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time,title)
        plot = ""
        action = "play"
        if logger.info() is False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, contentTitle=title, url=url,
                             fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('a', class_='next')
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    url = soup.iframe['src']
    if "/player-x.php?q=" in url:
        import base64
        url = scrapertools.find_single_match(url, "q=([^']+)")
        url = base64.b64decode(url).decode('utf-8')
        url = urlparse.unquote(url)
        url = scrapertools.find_single_match(url, '<(?:iframe|source) src="([^"]+)"')
    itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist