# -*- coding: utf-8 -*-
# -*- Channel HenaoJara -*-
# -*- Created for Alfa Addon -*-
# -*- By DieFeM -*-

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int; _dict = dict

from lib import AlfaChannelHelper
if not PY3: _dict = dict; from AlfaChannelHelper import dict
from AlfaChannelHelper import DictionaryAllChannel
from AlfaChannelHelper import re, traceback, time, base64, xbmcgui
from AlfaChannelHelper import Item, servertools, scrapertools, jsontools, get_thumb, config, logger, filtertools, autoplay

IDIOMAS = AlfaChannelHelper.IDIOMAS_ANIME
list_language = list(set(IDIOMAS.values()))
list_quality_movies = AlfaChannelHelper.LIST_QUALITY_MOVIES
list_quality_tvshow = AlfaChannelHelper.LIST_QUALITY_TVSHOW
list_quality = list_quality_movies + list_quality_tvshow
list_servers = ['uqload', 'voe', 'streamtape', 'doodstream', 'okru', 'streamlare', 'wolfstream', 'mega']
forced_proxy_opt = 'ProxySSL'

canonical = {
             'channel': 'henaojara', 
             'host': config.get_setting("current_host", 'henaojara', default=''), 
             'host_alt': ['https://www.henaojara.com/'], 
             'host_black_list': [], 
             'set_tls': True, 'set_tls_min': True, 'retries_cloudflare': 1, 'forced_proxy_ifnot_assistant': forced_proxy_opt, 
             'CF': False, 'CF_test': False, 'alfa_s': True
             }
host = canonical['host'] or canonical['host_alt'][0]

timeout = 15
kwargs = {}
debug = config.get_setting('debug_report', default=False)
movie_path = '/ver/category/pelicula'
tv_path = '/ver/category/categorias'
language = []
url_replace = []

finds = {'find': dict([('find', [{'tag': ['ul'], 'class': ['MovieList']}]), 
                       ('find_all', [{'tag': ['li']}])]), 
         'categories': dict([('find', [{'tag': ['div'], 'id': ['categories-3']}]),
                             ('find_all', [{'tag': ['li']}])]),
         'search': {}, 
         'get_language': {}, 
         'get_language_rgx': '', 
         'get_quality': {}, 
         'get_quality_rgx': '', 
         'next_page': {}, 
         'next_page_rgx': [['\/page\/\d+', '/page/%s/']],
         'last_page': dict([('find', [{'tag': ['div'], 'class': ['wp-pagenavi']}]),
                            ('find_all', [{'tag': ['a'], 'class': ['page-numbers'], '@POS': [-2]}]),
                            ('get_text', [{'tag': '', '@STRIP': True, '@TEXT': '(\d+)'}])]),
         'year': {}, 
         'season_episode': {}, 
         'seasons': {'find_all': [{'tag': ['div'], 'class': ['AABox']}]},
         'season_num': dict([('find', [{'tag': ['div'], 'class': ['AA-Season']}, 
                                       {'tag': ['span']}]), 
                             ('get_text', [{'tag': '', '@STRIP': True}])]),
         'seasons_search_num_rgx': '', 
         'seasons_search_qty_rgx': '', 
         'season_url': host, 
         'episode_url': '', 
         'episodes': {'find_all': [{'tag': ['div'], 'class': ['AABox']}]},
         'episode_num': [], 
         'episode_clean': [['(?i)\s*-\s*proximo\s*capitulo(?:\:|)\s*\d+-[A-Za-z]+-\d+', '']], 
         'plot': {}, 
         'findvideos': {'find_all': [{'tag': ['div'], 'class': ['TPlayerTb']}]},
         'title_clean': [['(?i)HD|Español Castellano|Sub Español|Español Latino|ova\s+\d+\:|OVA\s+\d+|\:|\((.*?)\)|\s19\d{2}|\s20\d{2}', ''],
                         ['(?i)\s*Temporada\s*\d+', '']],
         'quality_clean': [],
         'language_clean': [], 
         'url_replace': [], 
         'controls': {'duplicates': [], 'min_temp': False, 'url_base64': False, 'add_video_to_videolibrary': True, 'cnt_tot': 20, 
                      'get_lang': False, 'reverse': False, 'videolab_status': True, 'tmdb_extended_info': True, 'seasons_search': False, 
                      'IDIOMAS_TMDB': {0: 'es', 1: 'ja', 2: 'es'}, 'join_dup_episodes': False, 'season_TMDB_limit': False}, 
         'timeout': timeout}
AlfaChannel = DictionaryAllChannel(host, movie_path=movie_path, tv_path=tv_path, canonical=canonical, finds=finds, 
                                   idiomas=IDIOMAS, language=language, list_language=list_language, list_servers=list_servers, 
                                   list_quality_movies=list_quality_movies, list_quality_tvshow=list_quality_tvshow, 
                                   channel=canonical['channel'], actualizar_titulos=True, url_replace=url_replace, debug=debug)


def mainlist(item):
    logger.info()

    autoplay.init(item.channel, list_servers, list_quality)

    itemlist = list()

    itemlist.append(Item(channel=item.channel, title='Últimos Episodios', url=host, action='list_all',
                         thumbnail=get_thumb('new episodes', auto=True), c_type='episodios'))

    itemlist.append(Item(channel=item.channel, title='Estrenos', url=host + 'ver/category/estrenos/', action='list_all',
                         thumbnail=get_thumb('premieres', auto=True), extra='estrenos'))

    itemlist.append(Item(channel=item.channel, title='Series', url=host + 'ver/category/categorias/', action='list_all',
                         thumbnail=get_thumb('anime', auto=True), c_type='series'))

    itemlist.append(Item(channel=item.channel, title='Películas', url=host + 'ver/category/pelicula/', action='list_all',
                         thumbnail=get_thumb('movies', auto=True), c_type='peliculas'))

    itemlist.append(Item(channel=item.channel, title='Categorías',  action='section', url=host, 
                         thumbnail=get_thumb('categories', auto=True), extra='categorías'))

    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search", url=host,
                         thumbnail=get_thumb("search", auto=True)))

    itemlist = filtertools.show_option(itemlist, item.channel, list_language, list_quality_tvshow, list_quality_movies)

    autoplay.show_option(item.channel, itemlist)

    return itemlist


def section(item):
    logger.info()

    return AlfaChannel.section(item, **kwargs)


def list_all(item):
    logger.info()

    findS = finds.copy()

    return AlfaChannel.list_all(item, matches_post=list_all_matches, generictools=True, finds=findS, **kwargs)


def list_all_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []

    findS = AHkwargs.get('finds', finds)

    for elem in matches_int:
        elem_json = {}
        #logger.error(elem)

        try:

            if item.c_type == 'episodios':
                sxe = elem.find("span", class_="ClB").get_text(strip=True)
                try:
                    season, episode = sxe.split('x')
                    elem_json['season'] = int(season)
                    elem_json['episode'] = int(episode)
                except Exception:
                    elem_json['season'] = 1
                    elem_json['episode'] = 1
                elem_json['mediatype'] = 'episode'

            elem_json['title'] = elem.find("h3", class_="Title").get_text(strip=True)
            elem_json['language'] = get_lang_from_title(elem_json['title'])

            seasonPattern = '\s+Temporada\s+(\d+)'
            if re.search(seasonPattern, elem_json['title']):
                season = int(scrapertools.find_single_match(elem_json['title'], seasonPattern))
                if season > 1:
                    elem_json['season'] = season
                    elem_json['mediatype'] = 'season'

            elem_json['url'] = elem.find("article", class_="TPost C").a.get('href', '')

            try:
                Qlty = elem.find("span", class_="Qlty").get_text(strip=True)
            except Exception:
                Qlty = ''

            if not elem_json.get('mediatype'):
                elem_json['mediatype'] = 'tvshow' if not "pelicula" in elem_json['title'] and Qlty not in ["PELICULA", "ESTRENO"] else 'movie'

            if item.c_type == 'series' and elem_json['mediatype'] == 'movie':
                continue
            if item.c_type == 'peliculas' and elem_json['mediatype'] == 'tvshow':
                continue

            if elem_json['mediatype'] == 'movie':
                elem_json['action'] = 'seasons'

            elem_json['thumbnail'] = elem.find("noscript").find("img").get("src", "")

            try:
                elem_json['year'] = elem.find("span", class_="Date AAIco-date_range").get_text(strip=True)
            except Exception:
                elem_json['year'] = '-'

            elem_json['quality'] = 'HD'

            if elem.find("div", class_=["Description"]): 
                elem_json['plot'] = elem.find("div", class_=["Description"]).p.get_text(strip=True)

        except Exception:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue

        if not elem_json['url']: continue

        matches.append(elem_json.copy())

    return matches


def seasons(item):
    logger.info()

    return AlfaChannel.seasons(item, **kwargs)


def episodios(item):
    logger.info()

    itemlist = []

    templist = seasons(item)

    for tempitem in templist:
        itemlist += episodesxseason(tempitem)

    return itemlist


def episodesxseason(item, **AHkwargs):
    logger.info()

    """ Aquí le decimos a qué función tienen que saltar para las películas de un solo vídeo """
    kwargs['matches_post_get_video_options'] = findvideos
    soup = AHkwargs.get('soup', '')

    return AlfaChannel.episodes(item, data=soup, matches_post=episodesxseason_matches, **kwargs)


def episodesxseason_matches(item, matches_int, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)
    
    # Asi lee los datos correctos de TMDB
    titleSeason = item.contentSeason
    if item.contentSeason == 1:
        titleSeason = get_title_season(item.url)

    for elem_season in matches_int:
        if elem_season.find("div", class_="AA-Season").span.get_text(strip=True) != str(item.contentSeason): continue

        try:
            epi_list = elem_season.find("div", class_="TPTblCn")
        except Exception:
            return matches

        for elem in epi_list.find_all("tr"):
            elem_json = {}
            # logger.error(elem)

            try:
                info = elem.find("td", class_="MvTbTtl")
                elem_json['title'] = info.a.get_text(strip=True)
                elem_json['episode'] = int(elem.find("span", class_="Num").get_text(strip=True) or 1)
                elem_json['url'] = info.a.get("href", "")
                elem_json['season'] = titleSeason

                try:
                    elem_json['thumbnail'] = elem.find(["noscript", "span"]).find("img").get("src", "")
                except Exception:
                    pass

            except Exception:
                logger.error(elem)
                logger.error(traceback.format_exc())
                continue

            if not elem_json.get('url', ''): 
                continue

            matches.append(elem_json.copy())

    return matches


def findvideos(item, **AHkwargs):
    logger.info()

    kwargs['matches_post_episodes'] = episodesxseason_matches

    return AlfaChannel.get_video_options(item, item.url, data='', matches_post=findvideos_matches, 
                                         verify_links=False, findvideos_proc=True, **kwargs)


def findvideos_matches(item, matches_int, langs, response, **AHkwargs):
    logger.info()

    matches = []
    findS = AHkwargs.get('finds', finds)

    for elem in matches_int:
        elem_json = {}
        # logger.error(elem)

        try:
            content = elem.get_text(strip=True)
            if content != '':
                elem = AlfaChannel.do_soup(scrapertools.htmlparser(content)).iframe
            else:
                elem = elem.iframe

            url = elem.get('src', '')
            if url == "" or not url.startswith('http'):
                continue

            iframeData = AlfaChannel.create_soup(url, hide_infobox=True, **kwargs)
            if not iframeData:
                continue

            iframe = iframeData.find("iframe")
            if not iframe:
                continue

            iframeUrl = iframe.get('src', '')

            if iframeUrl != "":
                iframeUrl = check_hjstream(iframeUrl)
                uriData = AlfaChannel.urlparse(iframeUrl)

                if re.search(r'embedwish|hqq|netuplayer|krakenfiles|hj.henaojara.com', uriData.hostname, re.IGNORECASE):
                    continue

                elem_json['url'] = iframeUrl
                elem_json['title'] = '%s'
                elem_json['language'] = item.language
                elem_json['quality'] = 'HD'

            if not elem_json.get('url'): continue
            matches.append(elem_json.copy())

        except Exception:
            logger.error(elem)
            logger.error(traceback.format_exc())
            continue

    return matches, langs

def actualizar_titulos(item):
    logger.info()
    #Llamamos al método que actualiza el título con tmdb.find_and_set_infoLabels

    return AlfaChannel.do_actualizar_titulos(item)


def search(item, texto, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)

    try:
        # https://docs.python.org/2/library/urllib.html#urllib.quote_plus (escapa los caracteres de la busqueda para usarlos en la URL)
        texto = AlfaChannel.do_quote(texto, '', plus=True) 
        item.url = item.url + "?s=" + texto

        if texto:
            item.c_type = 'search'
            item.texto = texto
            return list_all(item)
        else:
            return []

    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except Exception:
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def newest(categoria, **AHkwargs):
    logger.info()
    kwargs.update(AHkwargs)

    itemlist = []
    item = Item()

    item.title = "newest"
    item.category_new = "newest"
    item.channel = channel

    try:
        if categoria in ['anime']:
            item.url = host
            item.c_type = 'episodios'
            item.extra = "novedades"
            item.action = "list_all"
            itemlist = list_all(item)

        if len(itemlist) > 0 and ">> Página siguiente" in itemlist[-1].title:
            itemlist.pop()

    # Se captura la excepción, para no interrumpir al canal novedades si un canal falla
    except Exception:
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        logger.error(traceback.format_exc())
        return []

    return itemlist


# henaojara usa varios scripts para embeber algunos enlaces en diferentes subdominios de hjstream.xyz,
# esta funcion se encarga de extraer el enlace del servidor original a partir de los parámetros de la url,
# en el parámetro v (v=xxxx), a veces en texto plano, a veces en base64.
def check_hjstream(url):
    logger.info()

    if "hjstream.xyz" in url:
        queryData = AlfaChannel.parse_qs(AlfaChannel.urlparse(url).query)
        if "v" in queryData:
            v = queryData["v"][0]

            if v.startswith('https'):
                url = scrapertools.htmlparser(v)
            else:
                decurl = base64.b64decode(v).decode("utf-8")
                if decurl.startswith('https'):
                    url = scrapertools.htmlparser(decurl)

    return url

def get_lang_from_title(title):

    if 'latino' in title.lower():
        lang = 'Latino'
    elif 'castellano' in title.lower():
        lang = 'Castellano'
    elif 'audio español' in title.lower():
        lang = ['Latino', 'Castellano']
    else:
        lang = 'VOSE'

    return lang

# Algunas series tienen la temporada en el titulo, lo cual hace que TMDB devuelva los datos incorrectos
# Ya que por defecto la temporada se obtiene de otro lado, esto crea una ambigüedad.
# Esta funcion se usa para extraer el numero de temporada correcto del titulo
def get_title_season(url):
    logger.info()

    page = AlfaChannel.create_soup(url, hide_infobox=True, **kwargs)
    title = page.find("h1", class_="Title").get_text(strip=True)
    season = 1
    seasonPattern = '\s+Temporada\s+(\d+)'
    if re.search(seasonPattern, title):
        season = int(scrapertools.find_single_match(title, seasonPattern))

    return season