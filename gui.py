from widget_file_browser import *
from benchmark import Benchmark
import logging
import datetime

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s [%(levelname)-2s %(filename)s:%(lineno)s - %(funcName)5s()] %(message)s")

logger = logging.getLogger('gui')

update_interval = 10

class SelectableText(urwid.Text):
    def __init__(self, text, data=None):
        self.__super.__init__(text)
        self.data = data

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
        # urwid.AttrMap(SelectableText('-- example_config.ymal ----'), 'asd',  'reveal focus'),
        # urwid.AttrMap(SelectableText('bar'), '',  'reveal focus'),
        # urwid.AttrMap(SelectableText('baz'), '',  'reveal focus'),
        ])

        self.header_prefix = "Cluster Job Monitor v0.1"
        self.header = urwid.Text(self.header_prefix)
        self.footer = urwid.Text("Status")

        self.list = urwid.ListBox(self.content)

        super(MainWidget, self).__init__(urwid.Frame(urwid.LineBox(self.list), header=self.header, footer=self.footer))

    def add_line(self, text: str, data):
        self.content.append(urwid.AttrMap(SelectableText(text, data), '',  'reveal focus'))

    def get_job_line(self, job):
        return str(job['jobid']) + " " + str(job['status']['job_state'])

    def update_lines(self):
        self.header.set_text(self.header_prefix + "    Last Update: " + datetime.datetime.now().time().strftime("%H:%M:%S"))

        for line in self.list.body:
            line_widget = line._get_base_widget()

            if type(line_widget.data) is Benchmark:
                line_widget.data.update()  # Get all job status from slurm
                for job in line_widget.data.configurations:
                    # Update line text of each job
                    if 'widget' not in job and 'jobid' in job:
                        # Case that job got scheduled but doesnt have a line widget yet
                        job['widget'] = urwid.AttrMap(SelectableText(self.get_job_line(job), job), '', 'reveal focus')
                        self.content.append(job['widget'])
                    elif 'widget' in job and 'jobid' in job:
                        # Update line widget text
                        job['widget'].original_widget.set_text(self.get_job_line(job))

                # Check all jobs status code for error
                line_widget.data.check_jobs()

    def update(self, main_loop: urwid.main_loop, user_data):
        self.update_lines()
        main_loop.draw_screen()
        if user_data:
            main_loop.set_alarm_in(update_interval, self.update, user_data=True)

    def set_footer(self, text: str):
        self.footer.set_text(text)

    def keypress(self, size, key):
        key = self.__super.keypress(size, key)
        if key == 'r':
            element = self._w.contents['body'][0]._w.get_focus_widgets()[-1]._get_base_widget()
            if type(element) is SelectableText and type(element.data) is Benchmark:
                self.set_footer("Running " + str(len(element.data.configurations)) + " Jobs of config: " + element.data.file)
                element.data.run()
                self.update_lines()
                self.set_footer("")

        else:
            return key


class JobMonitor(object):
    def __init__(self):
        self.top = MainWidget()
        self.back = None
        self.modus = 'main'
        self.benchmarks = []

    def addConfig(self, file):
        bench = Benchmark(file)
        self.benchmarks.append(bench)
        self.top.set_footer(file)
        self.top.add_line(file + " #Configurations: " + str(len(self.benchmarks[-1].configurations)), bench)

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
                for file in names:
                    self.addConfig(file.replace('"', ''))
                self.modus = 'main'


main = JobMonitor()
mainloop = urwid.MainLoop(main.top, unhandled_input=main.callback, palette=palette)
handle = mainloop.set_alarm_in(update_interval, main.top.update, user_data=True)
mainloop.run()
