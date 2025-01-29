from pymediainfo import MediaInfo
import asyncio
from pprint import pprint




async def main():
    media_info = MediaInfo.parse(r'D:\Downloads\video_torrent\films\video_test\hevc.mkv')
    # for track in media_info.tracks:
    #     if track.track_type == "Video":
    #         pprint(track.to_data())
    #     elif track.track_type == "Audio":
    #         print("Track data:")
    #         pprint(track.to_data())
    print(media_info.to_data())
    # media_info = MediaInfo.parse(r'D:\FilmWork\Zoia\zoia.mkv', output='text')
    # print(media_info)



asyncio.run(main())
