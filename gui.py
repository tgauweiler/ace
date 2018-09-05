import urwid

def callback(key):
    if key == 'q':
        raise urwid.ExitMainLoop()


class SelectableText(urwid.Text):
    def selectable(self):
        return True

    def keypress(self, size, key):
        return key


palette = [
    ('reveal focus', 'black', 'dark cyan', 'standout')
   ]


class MainWidget(urwid.WidgetWrap):
    def __init__(self):
        self.content = urwid.SimpleListWalker([
        # urwid.AttrMap(SelectableText('-- example_config.ymal ----'), 'asd',  'reveal focus'),
        # urwid.AttrMap(SelectableText('bar'), '',  'reveal focus'),
        # urwid.AttrMap(SelectableText('baz'), '',  'reveal focus'),
            urwid.Text("Test text"),
            urwid.Text("Test text2")
        ])

        self.header = urwid.Text("Cluster Job Monitor v0.1")
        self.footer = urwid.Text("Footer")
        super(MainWidget, self).__init__(urwid.Frame(urwid.LineBox(urwid.ListBox(self.content)), header=self.header, footer=self.footer))

    def update(self):
        pass
        # self.content.append(urwid.AttrMap(SelectableText('NEEEEEWWW'), '',  'reveal focus'))


class JobMonitor(object):
    def __init__(self):
        self.top = MainWidget()

def update(main_loop, user_data):
    main_loop.widget.update()
    main_loop.set_alarm_in(2, update, user_data=[])

main = JobMonitor()
mainloop = urwid.MainLoop(main.top, unhandled_input=callback, palette=palette)
handle = mainloop.set_alarm_in(2, update, user_data=[])
mainloop.run()
