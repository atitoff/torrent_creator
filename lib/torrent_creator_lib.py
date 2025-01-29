import asyncio
import ctypes
import json
import math
import os.path
import pickle
import re
import shutil
from dataclasses import dataclass
from msilib import add_data
from uuid import uuid4
import urllib.parse

import psutil
import requests
import webview
from PIL import Image
from imdb import IMDb
from pymediainfo import MediaInfo
from screeninfo import get_monitors

from lib.lang import Lang
from lib.settings import *
from lib.wv_async import WVAsync, Settings, JsAsync


class IMDB:
    def __init__(self, imdb_id, cache_dir):
        self.movie = None
        self.production_companies = []
        self.country_codes = []
        self.genres = []
        self.language_codes = []
        self.rating: float = 0
        self.year: str = ''
        im = IMDb()
        try:
            with open(os.path.join(cache_dir, imdb_id + '.pickle'), 'rb') as f:
                self.movie = pickle.load(f)
        except FileNotFoundError:
            self.movie = im.get_movie(imdb_id)
            with open(os.path.join(cache_dir, imdb_id + '.pickle'), 'wb') as f:
                pickle.dump(self.movie, f)
        for item in self.movie['production companies']:
            self.production_companies.append(f'{item}')
        for item in self.movie['country codes']:
            self.country_codes.append(f'{item}')
        for item in self.movie['genres']:
            self.genres.append(f'{item}')
        for item in self.movie['language codes']:
            self.language_codes.append(f'{item}')
        # # for key, val in cls.movie.items():
        # #     print(key, val)
        self.rating = self.movie['rating']
        self.year = self.movie['year']


class KinoPoisk:
    def __init__(self, key, cache_dir):
        self.countries = []
        self.genres = []
        self.description: str = ''
        self.nameOriginal: str = ''
        self.nameRu: str = ''
        self.ratingKinopoisk: float = 0
        self.ratingImdb: float = 0
        self.year: int = 0
        self.imdbId: str = ''
        self.actors = []
        self.directors = []
        self.producers = []
        self.writers = []
        self.operators = []
        self.composers = []
        self.designs = []
        self.editors = []
        self._film_id = ''
        self._key = key
        self._cache_dir = cache_dir

    def _cache_load(self, name):
        try:
            file = os.path.join(self._cache_dir, name + self._film_id + '.json')
            print('load cache file', file)
            json_data = json.load(open(file))
            return json_data
        except FileNotFoundError:
            return None

    def _cache_save(self, cache_data, name):
        file = os.path.join(self._cache_dir, name + self._film_id + '.json')
        with open(file, 'w') as f:
            json.dump(cache_data, f)

    def set_id(self, film_id):
        self._film_id = film_id
        self._get_film()
        self._get_staff()

    def _get_data(self, name, url):
        cache = self._cache_load(name)
        if cache is None:
            try:
                x = requests.get(
                    url,
                    headers={"Content-Type": "application/json", 'X-API-KEY': self._key},
                )
            except Exception as err:
                pass
            if x.status_code != 200:
                pass
            else:
                print('cache_save')
                self._cache_save(x.json(), name)
                return x.json()

        else:
            return cache

    def _get_film(self):
        data = self._get_data('get_film', f'https://kinopoiskapiunofficial.tech/api/v2.2/films/{self._film_id}')
        for key, val in data.items():
            if val is None:
                continue
            if key == 'countries':
                for item in val:
                    self.countries += list(item.values())
            if key == 'genres':
                for item in val:
                    self.genres += list(item.values())
            if key == 'description':
                for item in val:
                    self.description = val.replace("\n", "")
            if key == 'nameOriginal':
                self.nameOriginal = val
            if key == 'ratingKinopoisk':
                self.ratingKinopoisk = val
            if key == 'ratingImdb':
                self.ratingImdb = val
            if key == 'year':
                self.year = val
            if key == 'imdbId':
                self.imdbId = val
            if key == 'nameRu':
                self.nameRu = val

    def _get_staff(self):
        data = self._get_data(
            'get_staff',
            f'https://kinopoiskapiunofficial.tech/api/v1/staff?filmId={self._film_id}'
        )
        for item in data:
            if item['professionKey'] == 'ACTOR':
                self.actors.append(item['nameRu'])
            if item['professionKey'] == 'DIRECTOR':
                self.directors.append(item['nameRu'])
            if item['professionKey'] == 'PRODUCER':
                self.producers.append(item['nameRu'])
            if item['professionKey'] == 'WRITER':
                self.writers.append(item['nameRu'])
            if item['professionKey'] == 'OPERATOR':
                self.operators.append(item['nameRu'])
            if item['professionKey'] == 'COMPOSER':
                self.composers.append(item['nameRu'])
            if item['professionKey'] == 'DESIGN':
                self.designs.append(item['nameRu'])
            if item['professionKey'] == 'EDITOR':
                self.editors.append(item['nameRu'])


@dataclass
class IniSettings(YamlSettings):
    def __init__(self, yaml_file_path):
        super().__init__(yaml_file_path)

    screenshot_scene: float = 0.5
    min_screenshot_qty: int = 6
    max_screenshots: int = 30
    jpg_quality: int = 80
    kinopoisk_key: str = ''


@dataclass
class MIText:
    language: str = ''
    language_str: str = ''


@dataclass
class MIAudio:
    language: str = ''
    language_str: str = ''
    format: str = ''
    bit_rate: int = 0
    bit_rate_str: str = ''
    channel_s: int = 0
    channel_str: str = ''
    title_translate_type: str = ''
    title_description: str = ''


@dataclass
class MI:
    video_width: int = 0
    video_height: int = 0
    video_format: str = ''
    video_duration: float = 0
    video_duration_str: str = ''
    video_bit_rate: int = 0
    video_bit_rate_str: str = ''
    video_frame_rate: str = ''
    audio_result_str: str = ''
    video_result_str: str = ''
    audio_header_str: str = ''
    text_format: str = ''
    interlaced: bool = False
    language: str = ''
    file_size: int = 0

    def __init__(self):
        self.mi = None
        self.mi: MediaInfo
        self.audio = []
        self.text = []

    def parse(self, file):
        self.mi = MediaInfo.parse(file)
        self.file_size = os.path.getsize(file)
        self.text_format = MediaInfo.parse(file, output='text')
        video_track = False
        for track in self.mi.tracks:
            if track.track_type == "Video" and video_track == False:
                video_track = True
                self._parse_video(track)
            if track.track_type == "Audio":
                self._parse_audio(track)
            if track.track_type == "Text":
                self._parse_text(track)
        # create audio result string
        items = []
        for idx, audio in enumerate(self.audio):
            audio: MIAudio
            items.append(f'{audio.language_str.lower()} ({audio.format}, {audio.channel_str}, {audio.bit_rate_str})')
        self.audio_result_str = ', '.join(items)
        self._audio_header()

    def _parse_video(self, track):
        vd = track.to_data()
        try:
            if vd['other_scan_type'] == ['Interlaced']:
                self.interlaced = True
        except KeyError:
            pass
        self.video_width = vd['width']
        self.video_height = vd['height']
        self.video_format = vd['format']
        self.video_duration = vd['duration']
        self.video_duration_str = vd['other_duration'][3][0:-4]
        self.video_bit_rate = vd['bit_rate']
        self.video_frame_rate = vd['frame_rate']
        self.video_bit_rate_str = self.human_bitrate(self.video_bit_rate)
        self.video_result_str = (
            f'{self.video_format}, {self.video_bit_rate_str}, {self.video_width}x{self.video_height}, '
            f'{self.video_frame_rate} к/с')

    def _parse_audio(self, track):
        track = track.to_data()
        ma = MIAudio()
        n_track = ''
        try:
            n_track = track['track_id']
            ma.language = track['language']
            ma.format = self._audio_codec(track['format'])
            ma.bit_rate = track['bit_rate']
            ma.bit_rate_str = self.human_bitrate(ma.bit_rate)
            ma.channel_s = track['channel_s']
            ma.channel_str = f'{track['channel_s']} ch'
            ma.language_str = Lang.get_language(ma.language)
            # todo error handler
            ma.title_translate_type, ma.title_description = self._audio_description(track['title'])
            self.audio.append(ma)
        except KeyError as e:
            print(f'Запись о аудиотреке {n_track} не добавлена, не указан:', e)

    def _parse_text(self, track):
        track = track.to_data()
        text = MIText()
        n_track = ''
        try:
            n_track = track['track_id']
            text.language = track['language']
            text.language_str = Lang.get_language(text.language)
            # TODO error handler
            self.text.append(text)
        except KeyError as e:
            print(f'Запись о субтитрах {n_track} не добавлена, не указан:', e)

    @staticmethod
    def _audio_description(title: str):
        find = re.compile(r'^.{2,3}\s(.{1,}$)')
        suffix = ''
        try:
            suffix = find.findall(title)[0]
        except IndexError:
            pass
        title_m = title.lower()
        if title_m.startswith(("mvo", "мп")):
            return 'МП', suffix
        if title_m.startswith(("avo", "мп")):
            return 'АП', suffix
        if title_m.startswith(("dvo", "дп")):
            return 'ДП', suffix
        if title_m.startswith(("dub", "дб")):
            return 'ДБ', suffix
        return '', ''

    def _audio_header(self):
        out_dict = {}
        for audio in self.audio:
            audio: MIAudio
            try:
                out_dict[audio.title_translate_type] += 1
            except KeyError:
                out_dict[audio.title_translate_type] = 1
        ret = []
        for key, value in out_dict.items():
            if key != '' and value > 1:
                ret.append(f'{value} x {key}')
            elif key != '' and value == 0:
                ret.append(f'{value} x {key}')
        sub = ''
        if len(self.text) == 1:
            sub = ', СТ'
        elif len(self.text) > 1:
            sub = f', {len(self.text)} x СТ'

        self.audio_header_str = ', '.join(ret) + sub


    @staticmethod
    def _audio_codec(codec: str) -> str:
        codecs = {'AC-3': 'AC3'}
        if codec in codecs:
            return codecs[codec]
        else:
            return codec

    @staticmethod
    def human_bitrate(s: int) -> str:
        units = ['б/с', 'кб/с', 'Мб/с', 'Гб/с', 'Тб/с']
        for unit in units:
            if s < 1000:
                if int(s) == s:
                    s = int(s)
                    return f"{s} {unit}"
                else:
                    return f"{s:.1f} {unit}"
            s /= 1000

    @staticmethod
    def human_size(s: int) -> str:
        units = ['Б', 'кБ', 'МБ', 'ГБ', 'ТБ']
        for unit in units:
            if s < 1000:
                if int(s) == s:
                    s = int(s)
                    return f"{s} {unit}"
                else:
                    return f"{s:.1f} {unit}"
            s /= 1024

    def translate_str(self) -> str:
        ret = []
        for item in self.audio:
            item: MIAudio
            descr = item.title_description.strip()
            if descr == '':
                continue
            ret.append(f'{item.title_translate_type} {descr}')
        return ', '.join(ret)


@dataclass
class AppSettings(Settings):
    main_window_width: int = 800
    main_window_height: int = 600
    display_width: int = 0
    display_height: int = 0
    mkv_file_name: str = ''
    mkv_file_name_with_path: str = ''
    display_scale_factor: float = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100

    def __init__(self):
        super().__init__()
        self._screen()
        self.path_ffmpeg = os.path.join(self.path_add, 'ffmpeg.exe')
        self.screenshots_path = os.path.join(self.path_web, 'work', 'screenshots')

    def _screen(self):
        for m in get_monitors():
            if m.is_primary:
                self.display_width = m.width
                self.display_height = m.height
                return


class TorrentCreator:
    def __init__(self, wv_app: WVAsync):
        super().__init__()
        self.s = AppSettings()
        self.ini_s = IniSettings(os.path.join(self.s.path_add, 'settings.yaml'))
        self.wv_app = wv_app
        self.mi = MI()
        self.kinopoisk: KinoPoisk
        self.imbd: IMDB
        self.wv_app.registry('on_closing', self._on_closing)
        self.wv_app.registry('open_mkv', self.open_mkv)
        self.wv_app.registry('create_screenshots', self.create_screenshots)
        self.wv_app.registry('show_img', self.show_img)
        self.wv_app.registry('hide_slave_window', self._hide_slave_window)
        self.wv_app.registry('upload_screenshots', self.upload_screenshots)
        self.wv_app.registry('show_settings', self._show_settings)
        self.wv_app.registry('load_kinopoisk', self._load_kinopoisk)

    async def _on_closing(self, d):
        print('closing')
        ret = await JsAsync.call(
            """new BsDialogs().ok_cancel('Выход', 'Вы действительно хотите выйти?')""",
            self.wv_app.window)
        if ret == 'ok':
            self.wv_app.window.minimize()
            self.wv_app.window_slave.minimize()
            self.wv_app.jq.sync_q.put_nowait({'closing': True})
            self.wv_app.window.hide()
        else:
            return False

    def _empty_all(self):
        shutil.rmtree(self.s.screenshots_path, ignore_errors=True)
        os.makedirs(self.s.screenshots_path)

    async def _hide_slave_window(self):
        self.wv_app.window_slave.hide()

    def on_loaded(self):
        """ on load dom main window """
        self._empty_all()

    async def bs_form(self, frm_header, frm, btn, options=None):
        if options is None:
            options = {}
        d = {
            'frm_header': urllib.parse.quote(frm_header),
            'frm': urllib.parse.quote(frm),
            'btn': urllib.parse.quote(btn),
            'options': options
        }
        return await JsAsync.call(f"app.bs_form('{json.dumps(d)}')", self.wv_app.window)

    async def show_img(self, img):
        rand_token = uuid4()

        # приводим дисплей к значениям с учетом scale_factor
        display_width = math.ceil(self.s.display_width / self.s.display_scale_factor)
        display_height = math.ceil(self.s.display_height / self.s.display_scale_factor)

        w_k = display_width / self.mi.video_width
        h_k = display_height / self.mi.video_height

        print('h_k, w_k', h_k, w_k)

        if w_k >= h_k:
            magnification_k = h_k
        else:
            magnification_k = w_k

        if magnification_k >= 1:
            magnification_k = 1

        window_slave_width = math.ceil(self.mi.video_width * 1.5 * magnification_k)
        window_slave_height = math.ceil(self.mi.video_height * 1.5 * magnification_k)

        img_width = math.ceil(self.mi.video_width * magnification_k)
        img_height = math.ceil(self.mi.video_height * magnification_k)

        left = self.s.display_width - window_slave_width
        left = math.ceil(left / 2 / self.s.display_scale_factor)

        right = self.s.display_height - window_slave_height
        right = math.ceil(right / 2 / self.s.display_scale_factor)

        self.wv_app.window_slave.resize(window_slave_width, window_slave_height)
        self.wv_app.window_slave.move(left, right)
        self.wv_app.window_slave.evaluate_js(
            f"""set_picture('work/screenshots/{img}?{rand_token}', {img_width}, {img_height}, '{self.mi.video_width}x{self.mi.video_height}')"""
        )
        self.wv_app.window_slave.show()
        print(img)

    async def open_mkv(self):
        print('open_mkv')
        file_types = ('Video Files (*.mkv;*.mp4)', 'All files (*.*)')
        result = self.wv_app.window.create_file_dialog(
            webview.OPEN_DIALOG, allow_multiple=False, file_types=file_types
        )
        if result:
            el = self.wv_app.window.dom.get_element('#input_file')
            _, self.s.mkv_file_name = os.path.split(result[0])
            el.value = self.s.mkv_file_name
            self.s.mkv_file_name_with_path = result[0]
            self._empty_all()
            self.wv_app.window.evaluate_js("app.clean_screenshots()")
            await self.on_open_mkv()

    async def on_open_mkv(self):
        self.mi.parse(self.s.mkv_file_name_with_path)

    async def create_screenshots(self):
        """create png files from video file"""
        self.wv_app.window.evaluate_js("app.clean_screenshots(); spinner_modal.show()")
        self._empty_all()
        cmd = [
            self.s.path_ffmpeg, '-i', f'{self.s.mkv_file_name_with_path}', '-to', '00:15:00', '-vf',
            "select='gt(scene,0.3)',select='eq(pict_type,I)'", '-fps_mode', 'vfr', 'frame-%3d.png'
        ]
        print(self.s.screenshots_path)
        psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE, cwd=self.s.screenshots_path
            )
        except Exception as e:
            print(e)
            return
        psutil.Process().nice(psutil.NORMAL_PRIORITY_CLASS)  # reset current priority
        while proc.returncode is None:
            try:
                buf = await proc.stderr.readuntil(b'\r')
                if buf.startswith(b'frame='):
                    self.wv_app.window.evaluate_js(f"""spinner_modal.text('Найдено: {buf[6:11].decode()}')""")
                    if int(buf[6:11].decode()) > self.ini_s.max_screenshots:
                        proc.terminate()
                        break
            except asyncio.IncompleteReadError:
                break
            if buf == b'':
                break
        await proc.communicate()
        self.wv_app.window.evaluate_js("""spinner_modal.hide()""")

        img_cnt = len(os.listdir(self.s.screenshots_path))
        print('img_cnt', img_cnt)
        self.wv_app.window.evaluate_js(f"""document.getElementById('img_cnt').innerHTML = 'Всего: {img_cnt}'""")
        img_list = []
        for item in range(1, img_cnt + 1):
            img_list.append(f'frame-{item:03d}.png')
        json_img = json.dumps(img_list)
        print(json_img)
        self.wv_app.window.evaluate_js(f"app.create_screenshots('{json_img}')")

    async def upload_screenshots(self):
        images = self.wv_app.window.evaluate_js('app.get_info_screenshots()')
        if len(images) < 1:
            ret = await JsAsync.call(
                ("""new BsDialogs().ok('<i class="bi bi-exclamation-triangle"></i>',"""
                 " 'Количество выбранных скриншотов должно быть не менее """
                 f"{self.ini_s.min_screenshot_qty}')"),
                self.wv_app.window)
            print(ret)
            return

        self.wv_app.window.evaluate_js(f"""spinner_modal.show()""")
        self.wv_app.window.evaluate_js(f"""spinner_modal.text('Создаем миниатюры')""")
        miniature_size = 320, math.ceil(self.mi.video_height / self.mi.video_width * 320)
        all_images = []
        for image in images:
            with Image.open(os.path.join(self.s.screenshots_path, image)) as im:
                im1 = im.resize(miniature_size, Image.Resampling.LANCZOS)
                pre, ext = os.path.splitext(image)
                m_image = 'm_' + pre + '.jpg'
                im1.save(os.path.join(self.s.screenshots_path, m_image), 'JPEG', quality=95)
                all_images.append([image, m_image])
        # upload to hosting
        self.wv_app.window.evaluate_js(f"""spinner_modal.text('Загружаем картинки.')""")
        psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
        ret_arr = []

        ### UPLOAD
        async def upload(img):
            cmd = [os.path.join(self.s.path_add, 'imgupload', 'imgupload.exe'), '-s', 'fastpic.ru']
            try:
                proc = await asyncio.create_subprocess_exec(
                    *cmd + [img], stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE, cwd=self.s.screenshots_path
                )
            except Exception as e:
                print(e)
                return

            stdout, _ = await proc.communicate()
            if stdout:
                return stdout.decode()

        i = 0
        for images in all_images:
            i += 1
            im0 = await upload(images[0])
            self.wv_app.window.evaluate_js(f"""spinner_modal.text('Загружено: {i}')""")
            i += 1
            im1 = await upload(images[1])
            self.wv_app.window.evaluate_js(f"""spinner_modal.text('Загружено: {i}')""")
            ret_arr.append([im0, im1])
        self.wv_app.window.evaluate_js(f"""spinner_modal.hide()""")
        psutil.Process().nice(psutil.NORMAL_PRIORITY_CLASS)  # reset current priority
        phpbb = []
        for item in ret_arr:
            phpbb.append(f"[url={item[0]}][img]{item[1]}[/img][/url]")
        self.wv_app.window.evaluate_js(f"""app.set_phpbb_screenshot('{json.dumps(phpbb)}')""")

    async def _show_settings(self):
        print('start settings')

        def row(_, d, text):
            return (f'<div class="row mb-1"><div class="col-8">{text}</div>'
                    f'<div class="col-4">{d}</div></div>')

        SettingsGui.row = row

        SettingsGUISelect(self.ini_s.screenshot_scene, 'screenshot_scene', 'Разница между сценами',
                          [0.2, 0.3, 0.4, 0.5, 0.6, 0.7]),
        SettingsGUISelect(self.ini_s.jpg_quality, 'jpg_quality', 'Качество jpeg миниатюр',
                          [60, 65, 70, 75, 80, 85, 90, 95])
        SettingsGUIInput(self.ini_s.max_screenshots, 'max_screenshots', 'Максимальное количество скриншотов',
                         'type="number" min="10" step="0" max="100"')
        SettingsGUIInput(self.ini_s.min_screenshot_qty, 'min_screenshot_qty', 'Минимальное количество скриншотов',
                         'type="number" min="6" step="0" max="20"')
        SettingsGUIInput(self.ini_s.kinopoisk_key, 'kinopoisk_key', 'Ключ для получения данных с Кинопоиска',
                         'type="text" pattern="[0-9a-fA-F-]{36}"')
        form = ''
        for key, value in SettingsGui.s_dict.items():
            print(key, value)
            form += f'{value}'

        form = f'<form id="settings">{form}</form>'
        ret = await self._bs_form('Настройки', form, 'Сохранить', options={'size': 'xl', 'scrollable': True})

        try:
            for key, value in ret.items():
                s = SettingsGui.s_dict[key]
                ret[key] = s.type_fn(value)
        except AttributeError:
            return

        self.ini_s.save(ret)

    async def _load_kinopoisk(self, d):
        cache_path = os.path.join(self.s.path_add, 'kp_cache')
        self.kinopoisk = KinoPoisk(self.ini_s.kinopoisk_key, cache_path)
        try:
            self.kinopoisk.set_id(d)
            self.wv_app.window.evaluate_js('spinner_modal.show()')
            self.wv_app.window.evaluate_js('spinner_modal.text("Ищем информацию на Кинопоиск и IMDB...")')
        except AttributeError:
            self.wv_app.window.evaluate_js('spinner_modal.hide()')
            await JsAsync.call(
                f"""new BsDialogs().ok('Ошибка', 'Фильм с id {d} не найден.')""",
                self.wv_app.window)
            return
        print('kinopoisk.imdbId', self.kinopoisk.imdbId)
        if self.kinopoisk.imdbId == '':
            ret = await self.bs_form(
                'Не найден IMDB ID, введите вручную',
                '<form><input title="начинается с tt" required type="text" data-name="imdb_id" '
                'pattern="^tt\\d{2,}"></input></form>',
                'Ок'
            )
            if ret is not None:
                self.kinopoisk.imdbId = ret['imdb_id']
        try:
            if self.kinopoisk.imdbId == '':
                raise ValueError('Not kinopoisk.imdbId')
            self.imdb = IMDB(self.kinopoisk.imdbId[2:], cache_path)
            self.wv_app.window.evaluate_js('spinner_modal.hide()')
        except Exception as e:
            self.wv_app.window.evaluate_js('spinner_modal.hide()')
            print(e)
            self.imdb = None

        kz = Kinozal(self)
        await kz.start()



class Kinozal:
    def __init__(self, tc: TorrentCreator):
        self.tc = tc
        self.kinopoisk = self.tc.kinopoisk
        self.mi = self.tc.mi

    async def start(self):
        d = list()
        d.append(f"[b]Название:[/b] {self.kinopoisk.nameRu}")
        if self.kinopoisk.nameOriginal is not None:
            d.append(f"[b]Оригинальное название:[/b] {self.kinopoisk.nameOriginal}")
        d.append(f"[b]Год выпуска:[/b] {self.kinopoisk.year}")
        d.append(f"[b]Жанр:[/b] {', '.join(self.kinopoisk.genres)}")
        d.append(f"[b]Выпущено:[/b] {self._released()}")
        d.append(f"[b]Режиссер:[/b] {', '.join(self.kinopoisk.directors)}")
        d.append(f"[b]В ролях:[/b] {', '.join(self.kinopoisk.actors[0:10])}")
        ret = {'preliminary_description': urllib.parse.quote('\r'.join(d))}

        if self.tc.imdb is not None:
            try:
                self.mi.language = self.tc.imdb.language_codes[0]
            except IndexError:
                pass
        else:
            pass

        while True:
            add_dta = await self.tc.bs_form(
                'Дополнительные данные',
                f'<form>{self._add_data_form()}</form>',
                'Выбрать'
            )
            if add_dta is not None:
                break
        try:
            self.mi.language = add_dta['language']
        except KeyError:
            pass

        d = list()
        d.append(f"[b]Качество:[/b] {add_dta['video_quality']}")
        d.append(f"[b]Видео:[/b] {self.mi.video_result_str}")
        d.append(f"[b]Аудио:[/b] {self.mi.audio_result_str}")
        d.append(f"[b]Размер:[/b] {self.mi.human_size(self.mi.file_size)}")
        d.append(f"[b]Продолжительность:[/b] {self.mi.video_duration_str}")
        d.append(f"[b]Перевод:[/b] {self.mi.translate_str()}")
        print(d)
        ret.update({'tech_data': urllib.parse.quote('\r'.join(d))})

        # заполняем поля вкладки Вывод
        self.tc.wv_app.window.evaluate_js(f"app.fill_description('{json.dumps(ret)}')")

    def _released(self):
        """
        Выпущено
        """
        try:
            return f"""{', '.join(self.kinopoisk.countries)}, {', '.join(self.tc.imdb.production_companies)}"""
        except AttributeError:
            return f"""{', '.join(self.kinopoisk.countries)}"""

    def _add_data_form(self):
        d = self._select_video_quality('AVC')
        frm = ('<select class="form-select" data-name="video_quality" required>'
               '<option value="">Выберите качество видео</option>')
        for item in d:
            frm += f'<option value="{item}">{item}</option>'
        frm += '</select>'
        frm += self._select_language()
        return frm

    def _select_video_quality(self, codec):
        mi: MI = self.tc.mi
        video_quality = {
            '': ['BDRip', 'DVB', 'DVD', 'DVD Remux', 'DVDRip', 'HDRip', 'HDTVRip', 'IPTV', 'IPTVRip', 'SATRip',
                 'TVRip',
                 'VHSRip', 'WEB-DLRip', 'WEBRip'],
            '(AVC)': ['BDRip (AVC)', 'DVDRip (AVC)', 'HDRip (AVC)', 'HDTVRip (AVC)', 'SATRip (AVC)',
                      'WEB-DLRip (AVC)',
                      'WEBRip (AVC)'],
            '(720p)': ['BDRip (720p)', 'HDTV (720p)', 'HDTVRip (720p)', 'IPTV (720p)', 'WEB-DL (720p)',
                       'WEB-DLRip (720p)',
                       'WEBRip (720p)'],
            '(1080p)': ['BDRip (1080p)', 'Blu-Ray (1080p)', 'Blu-Ray Remux (1080p)', 'HDTV (1080p)',
                        'HDTVRip (1080p)',
                        'IPTV (1080p)', 'WEB-DL (1080p)', 'WEB-DLRip (1080p)', 'WEBRip (1080p)'],
            '(2160p)': ['BDRip (2160p)', 'Blu-Ray Remux (2160p)', 'Hybrid (2160p)', 'UHDTV (2160p)',
                        'WEB-DL (2160p)',
                        'WEBRip (2160p)'],
            '(1080i)': ['Blu-Ray (1080i)', 'Blu-Ray Remux (1080i)', 'HDTV (1080i)', 'IPTV (1080i)']}
        q = ''

        if mi.video_width < 1280 and mi.video_height <= 576 and codec == 'AVC':
            q = 'AVC'
        elif mi.video_width <= 1280 and 500 < mi.video_height <= 720:
            q = '720'
        elif mi.video_width <= 1920 and 600 < mi.video_height <= 1080:
            q = '1080'
        elif mi.video_width > 1920 or 1080 < mi.video_height:
            q = '2160'
        else:
            return video_quality['']

        if q == 'AVC' or q == '':
            q = f'({q})'
        elif mi.interlaced:
            q = f'({q}i)'
        else:
            q = f'({q}p)'

        return video_quality[q]

    def _select_language(self):
        if self.tc.mi.language == '':
            frm = ('<select class="form-select mt-1" data-name="language" required>'
                   '<option value="">Выберите оригинальный язык фильма</option>')
            for ln, lang in Lang.get_language_common().items():
                frm += f'<option value="{ln}">{lang}</option>'
            return frm + '</select>'
        else:
            return ''