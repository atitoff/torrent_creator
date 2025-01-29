from lib.torrent_creator_lib import MI, MIAudio
import asyncio
import urllib.parse
import json



async def main():

    mi = MI()
    # mi.parse(r'D:\FilmWork\Zoia\zoia.mkv')  # MPEG Video
    # mi.parse(r'D:\Downloads\video_torrent\films\Dreamcaster\Ловец снов - Dreamcatcher (2003) [Open Matte].mkv') # AVC
    # mi.parse(r'D:\Downloads\video_torrent\films\video_test\hevc.mkv')  # HEVC
    mi.parse(r'D:\Downloads\video_torrent\films\video_test\vc1.mkv')  # VC-1
    print(mi.interlaced)






asyncio.run(main())
