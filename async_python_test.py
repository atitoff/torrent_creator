import webview

html = """"""

class JsAsync:
    event_dict = {}  # {id: {event, ret_val}}
    id: int = 0

    def call(self, event):
        self.id += 1
        id = self.id
        self.event_dict[id] = event


def callback(result):
    print(result)


def evaluate_js_async(window):
    window.evaluate_js(
        '''new Promise(async (resolve, reject) => {
            let ret = await new BsDialogs().ok_cancel('header', 'body')
            resolve(ret);
        })''', callback)
    pass


if __name__ == '__main__':
    window = webview.create_window('Run async Javascript', url='web/test.html')
    webview.start(evaluate_js_async, window)
