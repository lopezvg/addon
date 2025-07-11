# -*- coding: utf-8 -*-
#------------------------------------------------------------
from platformcode import config, logger, platformtools
from core import scrapertools
from core import servertools
from core.item import Item
from core import httptools
from bs4 import BeautifulSoup
from modules import autoplay
from lib import alfa_assistant

list_quality = ['default']
list_servers = ['gounlimited']

forced_proxy_opt = 'ProxySSL'
timeout = 30

canonical = {
             'channel': 'porndish', 
             'host': config.get_setting("current_host", 'porndish', default=''), 
             'host_alt': ["https://www.porndish.com"], 
             'host_black_list': [], 
             'set_tls': False, 'set_tls_min': False, 'retries_cloudflare': 3, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]


def mainlist(item):
    if httptools.OPENSSL_VERSION < (1, 1, 1):
        if not config.get_setting('assistant_version', default=None):
            platformtools.dialog_ok("Alfa Assistant: Error", "NECESITAS la app Alfa Assistant para ver este canal")
            return
    logger.info()
    itemlist = []
    
    autoplay.init(item.channel, list_servers, list_quality)
    
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host))
    itemlist.append(Item(channel=item.channel, title="Canal" , action="categorias", url=host))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    
    autoplay.show_option(item.channel, itemlist)
    
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s/?s=%s" % (host,texto)
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
    soup = create_soup(item.url).find('nav', class_='g1-primary-nav')
    matches = soup.find_all('li', class_='menu-item-g1-standard')
    for elem in matches:
        title = elem.a.text.strip()
        id = elem['id']
        if "Home" not in title:
            itemlist.append(Item(channel=item.channel, action="canal", url=host, title=title, id=id))
    return itemlist


def canal(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url).find('li', id=item.id)
    matches = soup.find_all('a')
    for elem in matches:
        url = elem['href']
        title = elem.text
        plot = ""
        thumbnail = ""
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url,
                              fanart=thumbnail, thumbnail=thumbnail , plot=plot) )
    return itemlist


def create_soup(url):
    logger.info()
    data = ""
    if httptools.OPENSSL_VERSION >= (1, 1, 1):
        response = httptools.downloadpage(url, ignore_response_code=True, canonical=canonical)
        if response.sucess:
            data = response.data
    elif alfa_assistant.open_alfa_assistant():
        data = alfa_assistant.get_source_by_page_finished(url, 5, closeAfter=True)
        if not data:
            platformtools.dialog_ok("Alfa Assistant: Error", "ACTIVE la app Alfa Assistant para continuar")
            data = alfa_assistant.get_source_by_page_finished(url, 5, closeAfter=True)
            if not data:
                return False
        data = alfa_assistant.find_htmlsource_by_url_pattern(data, url)
        if isinstance(data, dict):
            data = data.get('source', '')
            if not data:
                return False
    if data:
        soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
        return soup
    
    return False


def lista(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find('div', id='primary').find_all('article')
    for elem in matches:
        elem = elem.find('div', class_='entry-featured-media')
        url = elem.a['href']
        title = elem.img['alt']
        thumbnail = elem.img['src']
        if "svg" in thumbnail:
            thumbnail = elem.img['data-src']
        plot = ""
        itemlist.append(Item(channel=item.channel, action="findvideos", title=title, contentTitle=title, url=url,
                              fanart=thumbnail, thumbnail=thumbnail, plot=plot,))
    try:
        if "/?s=" in item.url:
            next_page = soup.find('div', class_='g1-collection-more-inner').a['data-g1-next-page-url']
        else:
            next_page = soup.find('link', rel='next')['href']
    except Exception:
        next_page = None
    if next_page:
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page.strip()))
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    if not soup:
        return itemlist
    # soup = soup.find('div', class_='entry-content')
    soup = soup.find('div', class_='entry-inner')
    matches = soup.find_all('iframe')
    for elem in matches:
        url = elem['src']
        if "gif" in url:
            url = elem['data-src']
        itemlist.append(Item(channel=item.channel, action="play", title= "%s" , contentTitle=item.title, url=url)) 
    if soup.button:
        data = soup.find_all('script')[1]
        url =  scrapertools.find_single_match(str(data), '(?:src|SRC)="([^"]+)"')
        itemlist.append(Item(channel=item.channel, action="play", title= "%s" , contentTitle=item.title, url=url)) 
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize()) 
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)
    return itemlist

