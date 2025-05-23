# -*- coding: utf-8 -*-
#------------------------------------------------------------
from platformcode import config, logger, unify
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools
from core import urlparse
from bs4 import BeautifulSoup
from modules import autoplay

UNIFY_PRESET = config.get_setting("preset_style", default="Inicial")
color = unify.colors_file[UNIFY_PRESET]

list_quality = ['default']
list_servers = []

# https://xxxscenes.net  https://www.netflixporno.net   https://mangoporn.net   https://speedporn.net
canonical = {
             'channel': 'xxxscenes', 
             'host': config.get_setting("current_host", 'xxxscenes', default=''), 
             'host_alt': ["https://xxxscenes.net/"], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    logger.info()
    itemlist = []

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist.append(Item(channel=item.channel, title="Peliculas" , action="submenu", url=host + "xxxmovies/"))

    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "page/1?filter=latest"))
    itemlist.append(Item(channel=item.channel, title="Mas visto" , action="lista", url=host + "page/1?filter=most-viewed"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=host + "page/1?filter=popular"))
    itemlist.append(Item(channel=item.channel, title="Pornstar" , action="categorias", url=host + "pornstars"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="canal", url=host + "studios"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "genres"))
    itemlist.append(Item(channel=item.channel, title="Buscar", url=host, action="search"))

    autoplay.show_option(item.channel, itemlist)

    return itemlist

def submenu(item):
    logger.info()
    itemlist = []
    
    autoplay.init(item.channel, list_servers, list_quality)
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=item.url + "page/1?filter=latest"))
    itemlist.append(Item(channel=item.channel, title="Mas visto" , action="lista", url=item.url + "page/1?filter=most-viewed"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorado" , action="lista", url=item.url + "page/1?filter=popular"))
    itemlist.append(Item(channel=item.channel, title="Pornstar" , action="categorias", url=item.url + "pornstars"))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="canal", url=item.url + "studios"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=item.url + "genres"))
    itemlist.append(Item(channel=item.channel, title="Buscar", url=item.url, action="search"))
    
    autoplay.show_option(item.channel, itemlist)

    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%ssearch/%s" % (item.url,texto)
    try:
        return lista(item)
    except Exception:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def canal(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all('div', class_='tag-item')
    for elem in matches:
        url = elem.a['href']
        title = elem.a.text.strip()
        thumbnail = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url, fanart=thumbnail, thumbnail=thumbnail) )
    return itemlist


def categorias(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all('div', class_='video-block')
    for elem in matches:
        url = elem.a['href']
        title = elem.find(class_='title').text.strip()
        cantidad = elem.find(class_='video-datas').text.strip()
        thumbnail = ""
        if elem.img.get('src', ''):
            thumbnail = elem.img['src']
        if "svg+" in thumbnail:
            thumbnail = elem.img['data-lazy-src']
        if cantidad:
            title = "%s (%s)" % (title,cantidad)
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url, fanart=thumbnail, thumbnail=thumbnail) )
    next_page = soup.find('a', class_='next')
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
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
        url = elem.a['href']
        title = elem.find(class_='title').text.strip()
        time = elem.find(class_='duration')
        thumbnail = ""
        if elem.img.get('src', ''):
            thumbnail = elem.img['src']
        if "svg+" in thumbnail:
            thumbnail = elem.img['data-lazy-src']
        if time:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time.text.strip(),title)
        plot = ""
        itemlist.append(Item(channel=item.channel, action="findvideos", title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('a', class_='next')
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    video_urls = []
    soup = create_soup(item.url)
    pornstars = soup.find(id="video-actors").find_all('a')
    for x , value in enumerate(pornstars):
        pornstars[x] = value.text.strip()
    pornstar = ' & '.join(pornstars)
    pornstar = "[COLOR %s]%s[/COLOR]" % (color.get('rating_3',''), pornstar)
    if "/xxxmovies/" not in item.url:
        lista = item.contentTitle.split()
        lista.insert (0, pornstar)
        item.contentTitle = ' '.join(lista)    
    plot = pornstar
    matches = soup.find('div', id='pettabs').find_all('a')
    for elem in matches:
        url = elem['href']
        if url not in video_urls:
            video_urls += url
            itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.contentTitle, url=url, plot=plot))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)
    return itemlist

