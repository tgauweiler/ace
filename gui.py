import urwid
from widget_file_browser import *
import logging

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s [%(levelname)-2s %(filename)s:%(lineno)s - %(funcName)5s()] %(message)s")

logger = logging.getLogger('gui')

# def callback(key):
#     if key == 'q':
#         raise urwid.ExitMainLoop()
#     if key == 'o':
#         urwid.main_loop.widget = urwid.Overlay(DirectoryBrowser(), urwid.main_loop.widget)

class SelectableText(urwid.Text):
    def selectable(self):
        return True

    def keypress(self, size, key):
        return key


palette = [
        ('reveal focus', 'black', 'dark cyan', 'standout'),
        ('body', 'black', 'light gray'),
        ('flagged', 'black', 'dark green', ('bold','underline')),
        ('focus', 'light gray', 'dark blue', 'standout'),
        ('flagged focus', 'yellow', 'dark cyan',
                ('bold','standout','underline')),
        ('head', 'yellow', 'black', 'standout'),
        ('foot', 'light gray', 'black'),
        ('key', 'light cyan', 'black','underline'),
        ('title', 'white', 'black', 'bold'),
        ('dirmark', 'black', 'dark cyan', 'bold'),
        ('flag', 'dark gray', 'light gray'),
        ('error', 'dark red', 'light gray'),
        ]


class MainWidget(urwid.WidgetWrap):
    def __init__(self):
        self.content = urwid.SimpleListWalker([
        urwid.AttrMap(SelectableText('-- example_config.ymal ----'), 'asd',  'reveal focus'),
        urwid.AttrMap(SelectableText('bar'), '',  'reveal focus'),
        urwid.AttrMap(SelectableText('baz'), '',  'reveal focus'),
        ])

        self.header = urwid.Text("Cluster Job Monitor v0.1")
        self.footer = urwid.Text("Footer")

        super(MainWidget, self).__init__(urwid.Frame(urwid.LineBox(urwid.ListBox(self.content)), header=self.header, footer=self.footer))

    def update(self, main_loop, user_data):
        self.content.append(urwid.AttrMap(SelectableText('NEEEEEWWW'), '',  'reveal focus'))

    def setFooter(self, text):
        self.footer.set_text(text)



class JobMonitor(object):
    def __init__(self):
        self.top = MainWidget()
        self.back = None
        self.modus = 'main'

    def callback(self, key):
        if key == 'q':
            raise urwid.ExitMainLoop()
        elif key == 'o':
            if self.modus == 'main':
                self.modus = 'open'
                browser = DirectoryBrowser()
                self.back = self.top._w.contents['body'][0]
                overlay = urwid.Overlay(browser.view, self.top._w.contents['body'][0], align=('relative', 20), width=('relative', 80), valign='middle', height=('relative', 80))
                self.top._w.contents['body'] = (overlay, None)
        elif key == 'enter':
            if self.modus == 'open':
                # Terminate browsing and switch back to main
                self.top._w.contents['body'] = (self.back, None)
                names = [escape_filename_sh(x) for x in get_flagged_names()]
                self.top.setFooter(names[0])



main = JobMonitor()
mainloop = urwid.MainLoop(main.top, unhandled_input=main.callback, palette=palette)
# handle = mainloop.set_alarm_in(2, main.top.update, user_data=[])
mainloop.run()
