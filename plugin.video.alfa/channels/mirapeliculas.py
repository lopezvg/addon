# -*- coding: utf-8 -*-
#------------------------------------------------------------

import re

from modules import autoplay
from platformcode import config, logger, platformtools
from core.item import Item
from core import httptools, scrapertools, tmdb
from core import servertools
from core import urlparse
from modules import filtertools

IDIOMAS = {'Latino': 'LAT', 'Español': 'ESP', 'Subtitulado': 'VOSE'}
list_language = list(IDIOMAS.values())
list_servers = ['streamango', 'streamplay', 'openload', 'okru']
list_quality = ['BR-Rip', 'HD-Rip', 'DVD-Rip', 'TS-HQ', 'TS-Screner', 'Cam']
forced_proxy_opt = 'ProxyCF'

canonical = {
             'channel': 'mirapeliculas', 
             'host': config.get_setting("current_host", 'mirapeliculas', default=''), 
             'host_alt': ["https://ww2.dipelis.com/"], 
             'host_black_list': ["https://mirapeliculasde.com/"], 
             'pattern': '<link\s*rel="[^>]*icon"[^>]+href="([^"]+)"', 
             'set_tls': True, 'set_tls_min': False, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
host_save = host

__channel__ = canonical['channel']
__comprueba_enlaces__ = config.get_setting('comprueba_enlaces', __channel__)
__comprueba_enlaces_num__ = config.get_setting('comprueba_enlaces_num', __channel__)
__modo_grafico__ = config.get_setting('modo_grafico', __channel__, True)


def mainlist(item):
    logger.info()
    
    itemlist = []
    
    autoplay.init(item.channel, list_servers, list_quality)
    
    itemlist.append(item.clone(title="Novedades", action="lista", url= host, language=[]))
    itemlist.append(item.clone(title="Castellano", action="lista", url= host + "ver/castellano/", language=['CAST']))
    itemlist.append(item.clone(title="Latino", action="lista", url= host + "ver/latino/", language=['LAT']))
    itemlist.append(item.clone(title="Subtituladas", action="lista", url= host + "ver/subtituladas/", language=['VOSE']))
    itemlist.append(item.clone(title="Categorias", action="categorias", url= host, language=[]))
    itemlist.append(item.clone(title="Buscar", action="search", language=[]))
    
    itemlist.append(item.clone(title="Configurar canal...", text_color="gold", action="configuracion", folder=False, language=[]))
    
    autoplay.show_option(item.channel, itemlist)
    
    return itemlist


def configuracion(item):
    
    ret = platformtools.show_channel_settings()
    platformtools.itemlist_refresh()
    
    return ret


def search(item, texto):
    logger.info()
    
    texto = texto.replace(" ", "+")
    item.url = host + "buscar/?q=%s" % texto
    
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
    
    data = httptools.downloadpage(item.url, canonical=canonical).data
    
    patron  = '<li class="cat-item cat-item-3"><a href="([^"]+)" title="([^"]+)">'
    matches = re.compile(patron,re.DOTALL).findall(data)
    
    for scrapedurl, scrapedtitle in matches:
        
        itemlist.append(item.clone(channel=item.channel, action="lista", url=scrapedurl, 
                                   title=scrapedtitle.replace('ver películas de ', '').strip()))
    
    return itemlist


def lista(item):
    logger.info()
    
    itemlist = []
    
    data = httptools.downloadpage(item.url, canonical=canonical).data

    patron  = '<div class="col-mt-5 postsh">.*?<a href="([^"]+)".*?'
    patron += '<span class="under-title-gnro">([^"]+)</span>.*?'
    patron += '<p>(\d+)</p>.*?'
    patron += '<img src="([^"]+)".*?'
    patron += 'title="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    
    for scrapedurl, calidad, scrapedyear, scrapedthumbnail, scrapedtitle in matches:

        itemlist.append(item.clone(action="findvideos", title=scrapedtitle.strip(), url=scrapedurl,
                                   infoLabels={'year': scrapedyear or '-'}, 
                                   thumbnail=scrapedthumbnail, quality=calidad.strip(), 
                                   contentType='movie', contentTitle=scrapedtitle.strip()))

    tmdb.set_infoLabels(itemlist, True)

    next_page_url = scrapertools.find_single_match(data,'<span class="current">\d+</span>.*?<a href="([^"]+)"')
    if next_page_url!="":
        next_page_url = urlparse.urljoin(item.url,next_page_url)
        itemlist.append(item.clone(channel=item.channel , action="lista" , title="Next page >>" , 
                                   text_color="blue", url=next_page_url) )

    return itemlist


def findvideos(item):
    logger.info()
    
    itemlist = []
    
    data = httptools.downloadpage(item.url, canonical=canonical).data
    
    patron = '<li data-id="\d+">([^<]+)<'
    idioma = scrapertools.find_multiple_matches(data, patron)
    video_urls = scrapertools.find_multiple_matches(data, "e\[\d+\]='([^']+)'")
    for video, lang in zip(video_urls, idioma): 
        if "|" in video:
            video = video.split("|")
            srv = video[1]
            id = video[0]
            if "1" in srv:
                url = "https://swdyu.com/e/%s" %id
            if "2" in srv:
                url = "https://filemoon.sx/e/%s" %id
            if "3" in srv:
                url = "https://d000d.com/e/%s" %id
            if "4" in srv:
                url = "https://mixdrop.ag/e/%s" %id
        else:
            url = video
        
        itemlist.append(item.clone(action="play", title='%s', url=url, language=lang))
    
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize()) 
    
    # Requerido para Filtrar enlaces
    if __comprueba_enlaces__:
        itemlist = servertools.check_list_links(itemlist, __comprueba_enlaces_num__)
    
    # Requerido para FilterTools
    itemlist = filtertools.get_links(itemlist, item, list_language)
    
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)

    if config.get_videolibrary_support() and len(itemlist) > 0 and item.extra !='findvideos' :
        itemlist.append(Item(channel=item.channel, action="add_pelicula_to_library", 
                             title='[COLOR yellow]Añadir esta pelicula a la videoteca[/COLOR]', url=item.url,
                             extra="findvideos", contentTitle=item.contentTitle)) 
    return itemlist



