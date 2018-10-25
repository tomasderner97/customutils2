import os
import sys
from time import time
from datetime import datetime
import matplotlib.pyplot as plt
import win32file
import atexit
import html
from warnings import warn
import pathlib
import inspect

original_print = print


class Reporting:

    def __init__(self):

        self.TIMESTAMP = int(time())
        self.FOLDER_PATH = f"reports/report_{self.TIMESTAMP}"
        self.REPORT_FILE = os.path.join(self.FOLDER_PATH, "report.html")
        self.SCRIPT_FILE = self._get_script_filename()

        self.show_plots = True
        self.print_to_console = True
        self.launch_report = False

        self._make_directory_tree()

        self.html_writer = HtmlWriter(self)
        self.html_writer.header()

        self.script_globals_at_import = tuple(
            self._get_script_last_frameinfo().frame.f_globals.keys()
        )

    def settings(self,
                 show_plots=None,
                 print_to_console=None,
                 launch_report=None):

        if show_plots is not None:
            self.show_plots = show_plots

        if print_to_console is not None:
            self.print_to_console = print_to_console

        if launch_report is not None:

            if launch_report and not self.launch_report:
                self._register_launch()
            elif not launch_report and self.launch_report:
                self._unregister_launch()

    def plt_show(self, fig=None):

        if not fig:
            fig = plt.gcf()

        # timestamp returns with 7 decimal places
        timestamp = int(time() * 1e7)
        fig_name = f"fig{timestamp}.png"

        fig.savefig(os.path.join(self.FOLDER_PATH, fig_name),
                    dpi=200,
                    pad_inches=0)

        self.html_writer.image(fig_name)

        if self.show_plots:

            if fig:
                plt.figure(fig.number)

            plt.show()

    def print(self, *objects, sep=' ', end='\n', file=sys.stdout, flush=False):

        string = f"{sep.join(map(str, objects))}{end}"
        self.html_writer.monospace_text(string)

        if self.print_to_console:
            original_print(*objects, sep=sep, end=end, file=file, flush=flush)

    def dump_vars(self):

        frameinfo = self._get_script_last_frameinfo()
        frameinfo_index = inspect.stack().index(frameinfo)

        for fi in inspect.stack()[frameinfo_index:]:
            if fi.filename == frameinfo.filename and fi.function != "<module>":
                self._pretty_print_vardump(fi.frame.f_locals,
                                           f"{fi.function} locals")
            else:
                break

        script_globals = dict(frameinfo.frame.f_globals)

        for g in self.script_globals_at_import:
            del script_globals[g]

        for k in list(script_globals.keys()):
            if k in script_globals.keys() and inspect.isfunction(script_globals[k]):
                del script_globals[k]
            if k in script_globals.keys() and inspect.ismethod(script_globals[k]):
                del script_globals[k]

        self._pretty_print_vardump(script_globals, "globals")

    def _pretty_print_vardump(self, var_dict, title=""):

        print(f"{title}:")
        for k, v in var_dict.items():
            print(f"\t{k}: {v}")
        if not var_dict:
            print(f"\tno variables in {title}")

    def _get_script_last_frameinfo(self):

        stack = inspect.stack()

        last_frame_in_script = stack[-1]

        for f in stack:

            is_bootstrap = "importlib._bootstrap" in f.filename
            is_this_init_py = "reporting/__init__.py" in f.filename.replace("\\", "/")
            is_this_file = f.filename == __file__

            if not (is_bootstrap or is_this_file or is_this_init_py):
                last_frame_in_script = f
                break

        # print("-----")
        # print("from _get_script_last_frameinfo: ")
        # print("\tscript file:", last_frame_in_script.filename)
        # print("\tcode context:", last_frame_in_script.code_context)
        # print("-----")

        return last_frame_in_script

    def _get_script_filename(self):

        frame = self._get_script_last_frameinfo()
        file_path = frame.filename

        return os.path.split(file_path)[1]

    def _make_directory_tree(self):

        pathlib.Path(self.FOLDER_PATH).mkdir(parents=True, exist_ok=True)

    def _launch_report_func(self):

        os.system(f"firefox {os.path.abspath(self.REPORT_FILE)}")

    def _register_launch(self):

        atexit.register(self._launch_report_func)

    def _unregister_launch(self):

        atexit.unregister(self._launch_report_func)


class HtmlWriter:

    def __init__(self, rep_obj: Reporting):

        self.rep_obj = rep_obj

        self.header_done = False

        self.style = [
            "#monospace {font-size: 18px}"
        ]

    def header(self):

        script_file = self.rep_obj.SCRIPT_FILE
        timestamp = self.rep_obj.TIMESTAMP
        pretty_date = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %T")

        title = f"{script_file} report from {pretty_date}"

        with open(self.rep_obj.REPORT_FILE, "w+") as f:
            f.writelines([
                "<html>"
                "<head>",
                f"<title> {title} </title>",
                "<style>"
            ])

            f.writelines(self.style)

            f.writelines([
                "</style>"
                "</head>",
                "<body>",
                f"<h1> {title} </h1>",
            ])

        self.header_done = True

    def monospace_text(self, string):

        self.check_header()

        string = html.escape(string)

        with open(self.rep_obj.REPORT_FILE, "a+") as f:
            f.write(f'<pre><span id="monospace">{string}</span></pre>')

    def image(self, path):

        self.check_header()

        with open(self.rep_obj.REPORT_FILE, "a+") as f:
            f.write(f'<img src="{path}" width="50%">')

    def check_header(self):

        if not self.header_done:
            warn("The report doesn't have a header!")


reporting = Reporting()

settings = reporting.settings
plt_show = reporting.plt_show
print = reporting.print
dump_vars = reporting.dump_vars
