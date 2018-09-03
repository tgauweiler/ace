import urwid

def callback(key):
    if key == 'q':
        raise urwid.ExitMainLoop()

def update(main_loop, user_data):
    print("bla")

class SelectableText(urwid.Text):
    def selectable(self):
        return True

    def keypress(self, size, key):
        return key


content = urwid.SimpleListWalker([
    urwid.AttrMap(SelectableText('-- example_config.ymal ----'), '',  'reveal focus'),
    urwid.AttrMap(SelectableText('bar'), '',  'reveal focus'),
    urwid.AttrMap(SelectableText('baz'), '',  'reveal focus'),
])

listbox = urwid.ListBox(content)
linebox = urwid.LineBox(listbox)

palette = [
    ('reveal focus', 'black', 'dark cyan', 'standout')
   ]

header = urwid.Text("Cluster Job Monitor v0.1")
footer = urwid.Text("Footer")

frame = urwid.Frame(linebox, header=header, footer=footer)

mainloop = urwid.MainLoop(frame, unhandled_input=callback, palette=palette)
handle = mainloop.set_alarm_in(2, update, user_data=[])
mainloop.run()
