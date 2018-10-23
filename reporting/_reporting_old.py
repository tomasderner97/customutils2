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

original_print = print

SHOW_PLOTS = True
FOLDER_PATH = ""
REPORT_FILE = ""
SCRIPT_FILE = ""
INITED = False

HTMl_HEADER = """<html>
<head>
<title>
{0} report from {1}
</title>
</head>
<body>
<h1>
{0} report from {1}
</h1>
"""

HTML_IMG = '<img src="{}">'

figure_counter = 0


def init_reporting(launch_report=False, show_plots=True):

    global SHOW_PLOTS, FOLDER_PATH, REPORT_FILE, INITED, SCRIPT_FILE

    SHOW_PLOTS = show_plots

    timestamp = int(time())
    FOLDER_PATH = f"reports/report_{timestamp}"

    pathlib.Path(FOLDER_PATH).mkdir(parents=True, exist_ok=True)

    REPORT_FILE = os.path.join(FOLDER_PATH, "report.html")

    _frame = list(sys._current_frames().values())[0]
    _file_path = _frame.f_back.f_globals['__file__']
    SCRIPT_FILE = os.path.split(_file_path)[1]

    if launch_report:
        atexit.register(lambda: os.system(f"firefox {os.path.abspath(REPORT_FILE)}"))

    with open(REPORT_FILE, "w+") as f:
        pretty_time = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %T")
        f.write(HTMl_HEADER.format(SCRIPT_FILE, pretty_time))

    INITED = True


def _initialize_if_not_done_before():

    if not INITED:
        init()
        warn("Reporting was not initialized, initializing with default settings.")


def dump_vars(repr=False):

    pass


def plt_show(fig=None):

    global figure_counter

    _initialize_if_not_done_before()

    if not fig:
        fig = plt.gcf()

    fig_name = f"fig{figure_counter}.png"
    fig.savefig(os.path.join(FOLDER_PATH, fig_name))
    figure_counter += 1

    with open(REPORT_FILE, "a+") as f:
        f.write(HTML_IMG.format(fig_name))

    if SHOW_PLOTS:
        plt.show()


def print(*objects, sep=' ', end='\n', file=sys.stdout, flush=False):

    _initialize_if_not_done_before()

    original_print(*objects, sep=sep, end=end, file=file, flush=flush)

    string = f"{sep.join(map(str, objects))}{end}"
    string = html.escape(string)

    with open(REPORT_FILE, "a+") as f:
        f.write(f'<pre><span style="font-size: 18px">{string}</span></pre>')
