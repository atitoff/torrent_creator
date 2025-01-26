from lib.torrent_creator_lib import MI, MIAudio
import asyncio



async def main():
    mi = MI()
    # mi.parse(r'''D:\Downloads\video_torrent\films\Ital'yanskaya.Rabota.1969.RUS.BDRip.XviD.AC3.-HQCLUB\Ital'yanskaya.Rabota.1969.RUS.BDRip.XviD.AC3.-HQCLUB.mkv''')
    mi.parse(r'D:\Downloads\video_torrent\films\Dreamcaster\Ловец снов - Dreamcatcher (2003) [Open Matte].mkv')
    # mi.parse(r'D:\Downloads\video_torrent\films\к\1.mkv')
    print(mi.video_result_str)
    print(mi.audio_result_str)
    print(mi.audio_header_str)
    print(mi.translate_str())

asyncio.run(main())



