from lib.torrent_creator_lib import MI, MIAudio
import asyncio
import urllib.parse
import json

async def main():
    # mi = MI()
    # # mi.parse(r'''D:\Downloads\video_torrent\films\Ital'yanskaya.Rabota.1969.RUS.BDRip.XviD.AC3.-HQCLUB\Ital'yanskaya.Rabota.1969.RUS.BDRip.XviD.AC3.-HQCLUB.mkv''')
    # mi.parse(r'D:\Downloads\video_torrent\films\Dreamcaster\Ловец снов - Dreamcatcher (2003) [Open Matte].mkv')
    # # mi.parse(r'D:\Downloads\video_torrent\films\к\1.mkv')
    # print(mi.video_result_str)
    # print(mi.audio_result_str)
    # print(mi.audio_header_str)
    # print(mi.translate_str())
    s = """[b]Название:[/b] Ловец снов
[b]Оригинальное название:[/b] Dreamcatcher
[b]Год выпуска:[/b] 2003
[b]Жанр:[/b] триллер, драма, фантастика, ужасы
[b]Выпущено:[/b] США, Канада, Castle Rock Entertainment, Village Roadshow Pictures, NPV Entertainment, Kasdan Pictures, WV Films II
[b]Режиссер:[/b] Лоуренс Кэздан
[b]В ролях:[/b] Морган Фриман, Томас Джейн, Джейсон Ли, Дэмиэн Льюис, Тимоти Олифант, Том Сайзмор, Донни Уолберг, Майки Хоулкамп, Рис Томпсон, Джакомо Бессато"""
    print(urllib.parse.quote_plus(s))
    s1 = {'dssds': s}
    print(json.dumps(s1))

asyncio.run(main())



