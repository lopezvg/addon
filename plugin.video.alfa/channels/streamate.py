# -*- coding: utf-8 -*-
#------------------------------------------------------------
import re

from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import httptools

IDIOMAS = {'vo': 'VO'}
list_language = list(IDIOMAS.values())
list_quality = ['default']
list_servers = []

#  https://www.fapcandy.com    https://www.streamate.com
canonical = {
             'channel': 'streamate', 
             'host': config.get_setting("current_host", 'streamate', default=''), 
             'host_alt': ["https://www.streamate.com/"], 
             'host_black_list': [], 
             'pattern': ['href="?([^"|\s*]+)["|\s*]\s*hrefLang="?en"?'], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'cf_assistant': False, 
             'CF': False, 'CF_test': False, 'alfa_s': True
            }
host = canonical['host'] or canonical['host_alt'][0]
cat = "https://member.naiadsystems.com/search/v3/categories?domain=streamate.com&shouldIncludeTransOnStraightSkins=false"
api = "https://member.naiadsystems.com/search/v3/performers?domain=streamate.com&from=0&size=100&filters=gender:f,ff,mf,tm2f,g;online:true&genderSetting=f"
httptools.downloadpage(host, canonical=canonical).data


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(Item(channel=item.channel, title="Chicas" , action="categorias", url=cat, chicas = True))
    itemlist.append(Item(channel=item.channel, title="Chicos" , action="categorias", url=cat))
    return itemlist


def categorias(item):
    logger.info()
    itemlist = []
    data = naiadsystems(item.url)
    if item.chicas:
        data = data["groups"][0]
        filter = "gender:f,ff,mf,tm2f,g"
        
    else:
        data = data["groups"][1]
        filter = "gender:m,mm,tf2m,g"
    for elem in data["categories"]:
        name = elem["name"]
        cantidad = elem["liveCount"]
        thumbnail = ""
        title = "%s (%s)" % (name,cantidad)
        if "allgirls" in name or "allguys" in name:
            cat = filter
        else:
            cat = "category:%s;%s" % (name, filter)
        url = "https://member.naiadsystems.com/search/v3/performers?domain=streamate.com&from=0&size=40&filters=%s;online:true&genderSetting=f" % cat
        itemlist.append(Item(channel=item.channel, action="lista", title=title, url=url, thumbnail=thumbnail, fanart=thumbnail ))
    return itemlist


def naiadsystems(url, post=None):
    logger.info()
    UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36'
    headers = {"platform": "SCP",
               "Accept": "application/json, text/plain, */*",
               "smeid": "ffffffff-ffff-ffff-ffff-ffffffffffffG0000000000000",
               "smtid": "ffffffff-ffff-ffff-ffff-ffffffffffffG0000000000000",
               "smvid": "ffffffff-ffff-ffff-ffff-ffffffffffffG0000000000000",
               "User-Agent": UA,
               "Referer": host}
    if post:
        data = httptools.downloadpage(url, post=post,  headers=headers, canonical=canonical)
    else:
        data = httptools.downloadpage(url, headers=headers, canonical=canonical)
    if data.code == 204:
        data = httptools.downloadpage(url, headers=headers, canonical=canonical)
    data = data.json
    return data


def lista(item):
    logger.info()
    itemlist = []
    data = naiadsystems(item.url)
    total = data['totalResultCount']
    for elem in data['performers']:
        thumbnail = "http://m1.nsimg.net/media/snap/{0}.jpg".format(elem['id'])
        name = elem['nickname']
        age = elem['age']
        country = elem['country']
        quality = 'HD' if elem['highDefinition'] else ''
        title = "%s [%s] (%s)" %(name,age,country)
        url = "https://manifest-server.naiadsystems.com/live/s:%s.json?last=load&format=mp4-hls" % name
        action = "play"
        if logger.info() is False:
            action = "findvideos"
        itemlist.append(Item(channel=item.channel, action=action, title=title, url=url, thumbnail=thumbnail,
                                   fanart=thumbnail, contentTitle=title ))
    page = scrapertools.find_single_match(item.url, '&from=(\d+)')
    page = int(page)
    if total > page  and (total - page) > 40:
        page += 40
        next_page = re.sub(r"&from=\d+", "&from={0}".format(page), item.url)
        itemlist.append(Item(channel=item.channel, action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).json
    data = data["formats"]["mp4-hls"]
    for elem in data["encodings"]:
        quality = elem["videoHeight"]
        url = elem["location"]
        itemlist.append(Item(channel=item.channel, action="play", title=quality, url=url) )
    return itemlist[::-1]


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url, canonical=canonical).json
    data = data["formats"]["mp4-hls"]
    for elem in data["encodings"]:
        quality = elem["videoHeight"]
        url = elem["location"]
        itemlist.append(['%sp' %quality, url])
    itemlist.sort(key=lambda item: int( re.sub("\D", "", item[0])))
    return itemlist