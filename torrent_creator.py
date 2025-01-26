import webview

from lib.wv_async import WVAsync, JsApi
from lib.torrent_creator_lib import TorrentCreator


# add user function
class Js(JsApi):
    def minimize(self):
        window.minimize()

    def call23(self, d):
        print('call23', d)
        window_slave.show()

    def close_app(self):
        wv_app.on_closing()


wv_app = WVAsync()
js_api = Js(wv_app.jq)

app = TorrentCreator(wv_app)


window = webview.create_window(
    'Torrent creator', 'web/index.html', frameless=True, easy_drag=False, js_api=js_api,
    width=app.s.main_window_width, height=app.s.main_window_height
)
window_slave = webview.create_window('Slave', hidden=True, url='web/slave.html', js_api=js_api, frameless=True)

window.events.loaded += app.on_loaded

wv_app.start(window, window_slave)

webview.start()
