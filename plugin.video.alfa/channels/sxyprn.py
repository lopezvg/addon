# -*- coding: utf-8 -*-
#------------------------------------------------------------
import re

from modules import autoplay
from platformcode import logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools
from core import urlparse
from bs4 import BeautifulSoup

host = "https://www.sxyprn.com"


# list_language = []
list_servers = ['streamtape', 'Directo']
list_quality = []
            # https://www.sxyprn.com/popular/top-pop.html
            # https://www.sxyprn.com/blog/all/0.html?fl=other&sm=latest
# https://www.sxyprn.com/blog/all/0.html?sm=views                 https://www.sxyprn.com/popular/top-viewed.html?p=all
# https://www.sxyprn.com/blog/all/0.html?fl=all&sm=orgasmic       https://www.sxyprn.com/orgasm/0

def mainlist(item):
    logger.info()
    itemlist = []
    autoplay.init(item.channel, list_servers, list_quality)
    check = ""

    itemlist.append(Item(channel=item.channel, title="Nuevos", action="lista", url=host + "/blog/all/0.html?fl=other&sm=latest"))
    itemlist.append(Item(channel=item.channel, title="Mas vistos", action="lista", url=host + "/popular/top-viewed.html?p=month"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorada", action="lista", url=host + "/blog/all/0.html?sm=rating"))
    itemlist.append(Item(channel=item.channel, title="Top", action="lista", url=host + "/popular/top-pop.html"))
    itemlist.append(Item(channel=item.channel, title="Orgasmic", action="lista", url=host + "/blog/all/0.html?fl=all&sm=orgasmic"))
    itemlist.append(Item(channel=item.channel, title="Sitios", action="catalogo", url=host))
    itemlist.append(Item(channel=item.channel, title="Categorias", action="categorias", url=host))
    itemlist.append(Item(channel=item.channel, title="Buscar", action="search"))
    itemlist.append(Item(channel=item.channel, title="", folder=0))

    itemlist.append(Item(channel=item.channel, title="[COLOR blue]EXTERNAL LINKS[/COLOR]" , action="submenu"))
    
    autoplay.show_option(item.channel, itemlist)
    return itemlist


def submenu(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Nuevos" , action="lista", url=host + "/blog/all/0.html?fl=all&sm=latest"))
    # itemlist.append(Item(channel=item.channel, title="Mas vistos" , action="findvideos", url=host + "/blog/all/0.html?fl=all&sm=latest"))
    itemlist.append(Item(channel=item.channel, title="Mejor valorada" , action="lista", url=host + "/blog/all/0.html?fl=top&sm=latest"))
    itemlist.append(Item(channel=item.channel, title="Sitios" , action="catalogo", url=host + "?page=0&op"))
    itemlist.append(Item(channel=item.channel, title="Categorias" , action="categorias", url=host + "?page=0&op"))
    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search", op=True))

    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "-")
    item.url = host + "/%s.html?page=0" % texto
    if item.op:
        item.url += "&op"

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
    soup = create_soup(item.url)
    matches = soup.find_all('div', class_='htag_el')
    for elem in matches:
        url = elem.parent['href'].replace("trending", "latest")
        title = elem.find('span', class_='htag_el_tag').text.strip().replace("#", "")
        thumbnail = elem.img['data-src']
        cantidad = elem.find('span', class_='htag_el_count').text.strip()
        thumbnail = "https:" + thumbnail
        url = urlparse.urljoin(item.url,url)
        if "&op" in item.url:
            url += "?page=0&op"
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url, thumbnail=thumbnail, fanart=thumbnail ) )
    return itemlist


def catalogo(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all('div', class_='top_sub_el_sc')
    for elem in matches:
        url = elem.parent['href'].replace("trending", "latest")
        title = elem.find('span', class_='top_sub_el_key_sc').text.strip()
        cantidad = elem.find('span', class_='top_sub_el_count').text.strip()
        thumbnail = ""
        url = urlparse.urljoin(item.url,url)
        if "&op" in item.url:
            url += "?page=0&op"
            title = "%s (%s)" %(title, cantidad)
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url, thumbnail=thumbnail, fanart=thumbnail ) )
    return itemlist


def create_soup(url, referer=None, unescape=False):
    logger.info()
    if referer:
        data = httptools.downloadpage(url, headers={'Referer': referer}).data
    else:
        data = httptools.downloadpage(url).data
        data = re.sub(r"\n|\r|\t|&nbsp;|<br>", "", data)

    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    return soup


def lista(item):
    logger.info()
    itemlist = []
    # url = "https://www.sxyprn.com/php/vo.php"
    # soup = create_soup(url, referer=item.url)
    # logger.debug(soup)
    soup = create_soup(item.url)
    matches = soup.find_all('div', class_='post_el_small')
    for elem in matches:
        # logger.debug(elem)
        ext = ""
        time = ""
        quality = ""
        serv = ['jetload', 'waaw', 'aparat.cam/reg', 'ninjastream']
        url = elem.find('a', class_='post_time')['href']
        titulo = elem.find('a', class_='post_time')['title']
        thumbnail = elem.img
        if thumbnail.get("src", "" ): 
            thumbnail = thumbnail['src']
        else:
            thumbnail = thumbnail['data-src']
        if "removed.png" in thumbnail:
            thumbnail = urlparse.urljoin(item.url,thumbnail)
        titulo = re.sub("#\w+", "", titulo).strip()
        title = scrapertools.find_single_match(titulo, '(.*?)https')
        if not title:
            title = titulo.replace("Visit Hornyfanz.com ", "")
        if thumbnail and "removed.png" not in thumbnail:
            time = elem.find('span', class_='duration_small')
            if time:
                time = time.text.strip()
            quality = elem.find('span', class_='shd_small')
            if not thumbnail.startswith("https"):
                thumbnail = "https:%s" % thumbnail
        # if not "EXTERNAL LINK" in time and item.check:
            # title = "[COLOR %s]%s[/COLOR]" % (item.check, title)
        if time and "EXTERNAL LINK" in time:
            time = ""
            ext = True
            ext1 = elem.find_all('a', class_='extlink')
            ext2 =[elem['href'] for elem in ext1]
            col = [a for a in serv for b in ext2 if a in b]
            if len(col) and len(ext1) <= 1:
                title = " [COLOR red]%s[/COLOR]" % title
        if quality:
            quality = quality.text.strip()
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]%s[/COLOR] %s" % (time, quality, title)
        else:
            title = "[COLOR yellow]%s[/COLOR] %s" % (time, title)
        url = urlparse.urljoin(item.url,url)
        itemlist.append(Item(channel=item.channel, action="findvideos", title=title, url=url, contentTitle = title,
                          thumbnail=thumbnail, fanart=thumbnail, ext=ext))
    next_page = soup.find('div', class_='next_page')
    logger.debug(next_page)
    if next_page:
        next_page = next_page.parent['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
        
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    logger.debug("ITEM: %s" % item)
    video_urls = []
    soup = create_soup(item.url)
    # if item.ext:  post_el_small 
    matches = soup.find('div', class_='post_el_post').find_all('a', class_='extlink')
    logger.debug(matches)
    for elem in matches:
        url = elem['href']
        itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=url))
    if soup.find('span', class_='vidsnfo'):
        itemlist.append(Item(channel=item.channel, action="play", title= "%s", contentTitle = item.title, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    # Requerido para AutoPlay
    autoplay.start(itemlist, item)
    return itemlist

