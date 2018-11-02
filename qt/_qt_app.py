import sys
from PyQt5.QtWidgets import QApplication

app = QApplication(sys.argv)


def qt_app(main_widget, sys_exit=True):

    main_widget.show()
    code = app.exec()

    if sys_exit:
        sys.exit(code)
    else:
        return code
