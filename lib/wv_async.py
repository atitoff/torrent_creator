import asyncio
from dataclasses import dataclass
from threading import Thread
import os
import janus
import sys
import webview


class WVAsync:
    def __init__(self):
        self.jq = janus.Queue()
        self.js_api = JsApi(self.jq)
        self.window: webview.Window
        self.window_slave: webview.Window
        self._t = Thread(target=self._main)
        self._reg = {}  # {fn_name: fn}

    def registry(self, name, fn):
        self._reg[name] = fn

    def on_closing(self):
        self.jq.sync_q.put_nowait({'on_closing': True})


    def _slave_on_closing(self):
        self.window_slave.hide()
        return False


    def start(self, window: webview.Window , window_slave: webview.Window=None):
        self.window = window
        self.window_slave = window_slave
        self.window.events.closing += self.on_closing
        self.window_slave.events.closing += self._slave_on_closing
        self._t.start()

    def _main(self):
        asyncio.run(self._main_loop())

    async def _main_loop(self):
        while True:  # ret = {name: {value}}
            ret = await self.jq.async_q.get()
            print(ret)
            for fn_name in ret:
                if fn_name in self._reg:
                    if ret[fn_name] is not None:
                        asyncio.create_task(self._reg[fn_name](ret[fn_name]))
                    else:
                        asyncio.create_task(self._reg[fn_name]())
                    await asyncio.sleep(0)
            if 'closing' in ret:
                break
        os._exit(0)


class JsApi:
    def __init__(self, jq):
        self.jq = jq


    def call(self, rpc_name, d=None):
        print(rpc_name, d)
        self.jq.sync_q.put_nowait({rpc_name: d})


@dataclass
class Settings:
    path_cwd: str = ''
    path_web: str = ''
    path_add: str = ''

    def __init__(self):
        self._web_path()

    def _web_path(self):
        # determine if application is a script file or frozen exe
        if getattr(sys, 'frozen', False):
            self.path_cwd = os.path.dirname(sys.executable)
            self.path_web = os.path.join(self.path_cwd, '_internal', 'web')
            self.path_add = os.path.join(self.path_cwd, '_internal', '_add')
        elif __file__:
            self.path_cwd = os.getcwd()
            self.path_web = os.path.join(self.path_cwd, 'web')
            self.path_add = os.path.join(self.path_cwd, 'add')


class EventTs(asyncio.Event):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._loop is None:
            self._loop = asyncio.get_event_loop()

    def set(self):
        self._loop.call_soon_threadsafe(super().set)

    def clear(self):
        self._loop.call_soon_threadsafe(super().clear)


class JsAsync:
    event_dict = {}  # {idc: [event, ret_val]}
    id: int = 0

    @classmethod
    def callback(cls, data):
        if data[0] in cls.event_dict:
            arr = cls.event_dict[data[0]]
            arr[1] = data[1]
            arr[0].set()


    @classmethod
    async def call(cls, function, window: webview.Window):
        cls.id += 1
        idc = cls.id
        event = EventTs()
        cls.event_dict[idc] = [event, None]
        fn = f'''new Promise(async (resolve, reject) => {{let ret = await {function}; resolve([{idc},ret]);}})'''
        window.evaluate_js(fn, cls.callback)
        await event.wait()
        ret_val = cls.event_dict[idc][1]
        del cls.event_dict[idc]
        return ret_val

