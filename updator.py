import math

from lib.torrent_creator_lib import Updator


def call(d):

        if 'chunk' in d:
            percent = math.ceil((d['chunk'][0] - d['chunk'][1]) / d['chunk'][0] * 100)
            if percent >= 100:
                percent = 100
            print(f"{percent:.0f}%")
        else:
            print(f"Calling {d}")

if __name__ == '__main__':
    upd = Updator(
        r'C:\Users\User\PycharmProjects\torrent_creator\add',
        {'ffmpeg': 1, 'imgupload': 1},
        'https://github.com/atitoff/torrent_creator/releases/download/0.10/',
        callback=call
    )





