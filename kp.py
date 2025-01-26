from lib.torrent_creator_lib import KinoPoisk, IMDB
import asyncio
from pprint import pprint



async def main():
    KinoPoisk.init(
        '6834c208-9ed1-451f-8d5d-6fcaa5f2a0f0',
        r'C:\Users\User\PycharmProjects\TorrentCreator\add\kp_cache'
    )
    try:
        KinoPoisk.set_id('6060')
    except AttributeError:
        print('нет фильма')
        return
    print('genres', KinoPoisk.genres)
    print('countries', KinoPoisk.countries)
    print('description', KinoPoisk.description)
    print('nameOriginal', KinoPoisk.nameOriginal)
    print('nameRu', KinoPoisk.nameRu)
    print('ratingKinopoisk', KinoPoisk.ratingKinopoisk)
    print('imdbId', KinoPoisk.imdbId)
    print('actors', KinoPoisk.actors)

    # print('composers', KinoPoisk.composers)
    # print('directors', KinoPoisk.directors)
    # print('designs', KinoPoisk.designs)
    # print('editors', KinoPoisk.editors)
    # print('operators', KinoPoisk.operators)
    # print('writers', KinoPoisk.writers)
    # print('producers', KinoPoisk.producers)
    IMDB.load(KinoPoisk.imdbId[2:], r'C:\Users\User\PycharmProjects\TorrentCreator\add\kp_cache')
    print(IMDB.production_companies)
    print(IMDB.country_codes)
    print(IMDB.language_codes)
    print(IMDB.rating)
    print(IMDB.year)
    print(IMDB.genres)




asyncio.run(main())
