#!/usr/bin/env python3

import sys
import shlex
import urllib.parse
import signal
import argparse
import os.path
import base64

from PySide.QtCore import *
from PySide.QtGui import *



ICON = base64.b64decode("""\
iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAYAAADDPmHLAAAABHNCSVQICAgIfAhkiAAAAAlwSFlz
AABuugAAbroB1t6xFwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAPsSURB
VHic7d27btRaGMXx9Zk0dJMCIWhiYymiRAo9HQVKgXQq5iUi2gASCEgLvESokCiiFOcZzkiUKJLP
7GkIEkXSTQP+KJiChrETb+PLWr8We9uK/+zxZS7m7hBeSdc7IN1SAOQUADkFQE4BkFMA5BQAOQVA
TgGQUwDkFAA5BUBOAZBTAOQUADkFQE4BkFMA5BQAOQVATgGQUwDkFAA5BUBOAZBTAOQUADkFQE4B
kFMA5BQAOQVATgGQUwDkFAA5BUBOAZBTAOQUADkFQE4BkFMA5BQAOQVATgGQUwDkFAC5ja53ILY8
z7fLspy6+44BOwBuVKxy6sDMzGZJkhwWRXHyN/azL2wsPxhhZpam6R7cDwBcveQwS5jthxDe+Vj+
MBVGEYCZWbq1dQTgQaQhj8NiscsQwSjOAdI03UO8gw8AD1Zjjt7gZ4A8z7fLHz8+4fLT/p8skytX
7oz9nGDwM0D5/fsjxD/4AHC1LMtpC+P2yuADcLO7rY3tvtPW2H0x+ABWl3qDG7svxnAfYO11/tNn
T9au/Orl60uPPQaDnwGkGQVATgGQUwDkFAA5BUBOAZCLfh8gS9NtAFP8uolS53l8r2Vp2veHJaUD
38zsswEH/8/n/15k5WgBZGlqAPYANHkeLxeXGHAd7tcduJdl2cfzs7N/zs7Py1orx9iD1cE/AvAG
Ovjdcn84mUy+bk4mtY5trHOA2M/jpZlrk83ND3UWbBzA6jX/oOk4Epn7w1tZdr9qsRgzwBSa9nvJ
gf2qZWIEMPpHpkPl7rerllEAI2bAtaplYlwGtvk8vvH6VarGr9J0/5uq2H7lf3DdCSSnAMgpAHIK
gJwCIKcAyCkAcmP4XEAjPb+Ob337mgHIKQByCoCcAiCnAMgpAHIKgFzn9wHavs7V9tfTDEBOAZBT
AOQUADkFQE4BkFMA5Bp/V3CWpl8w8O8A6LOmn4uYh2Dr/j3GDDCLMIZ0RAGQixHAIYBlhHGkA40D
mIdwghofQ5Z+inUV8A7AcaSx5C+KEsA8BAewC+Ax9HIwKNHuA8xD8HkIbwHcAfACv7406jTW+NKO
6O8HWJ0TPI897lh1/T2EuhNITgGQUwDkFAA5BUBOAZBTAOQG/9vBQ9fy+ylO5yHcXLeAZoCOeYuP
0+uMrQA6Zu7/tTa2mQLou2Rj4z3aeYC2TJLksHL7LWxYLqAoihOYxX8/hdl+URQnlYvpJLB7Zmbp
1tYR4v3qynFYLHa9xsHVDNAD7u5hsdiFWdP3Uyxh9rjuwQc0A/ROnufbZVlO3X3H6v3s3qkDMzOb
JUlyWGfa/50CIKeXAHIKgJwCIKcAyCkAcgqAnAIg9xPQCvsjOHEPwwAAAABJRU5ErkJggg==
""")



class LineEdit(QLineEdit):

    def __init__(self, strings, parent=None):
        QLineEdit.__init__(self, parent)
        completer = QCompleter(sorted(strings), self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        self.setCompleter(completer)

    def keyPressEvent(self, event):
        if event.key() != Qt.Key_Tab:
            return super().keyPressEvent(event)
        try:
            completer = self.completer()
            popup = completer.popup()
            use_default = not popup.isVisible()
        except AttributeError:
            use_default = True
        if use_default:
            return super().keyPressEvent(event)

        current_row = popup.currentIndex().row()
        completer.setCurrentRow(0 if current_row == -1 else current_row)
        self.setText(completer.currentCompletion())
        popup.hide()



class Dialog(QDialog):

    def __init__(self, commands, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.commands = commands
        self.settings = QSettings()
        self.setup_ui()
        self.exit_now = False

    def setup_ui(self):
        go_action = QAction("&Go", self)
        go_action.triggered.connect(self.go)

        menu = QMenu(self)
        menu.addAction("&Help", self.help, QKeySequence("F1"))
        menu.addSeparator();
        menu.addAction("About &Qt", qApp.aboutQt)
        menu.addAction("&About ubq", self.about)

        self.button = button = QToolButton()
        button.setDefaultAction(go_action)
        button.setMenu(menu)
        button.setPopupMode(QToolButton.MenuButtonPopup)
        button.setToolButtonStyle(Qt.ToolButtonTextOnly)
        button.setFocusPolicy(Qt.ClickFocus)

        self.input = input = LineEdit(list(self.commands), parent=self)
        input.setPlaceholderText('stomp your booty to exit...')
        input.returnPressed.connect(self.go)

        layout = QHBoxLayout()
        layout.addWidget(input)
        layout.addWidget(button)
        self.setLayout(layout)

        self.setFixedHeight(self.sizeHint().height())
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)
        self.resize(self.settings.value("size", self.sizeHint()))
        self.move(self.settings.value("pos", self.pos()))
        self.setWindowTitle(self.settings.applicationName())

        self.setWindowIcon(QIcon(QPixmap(QImage.fromData(ICON))))

    def resizeEvent(self, event):
        self.settings.setValue("size", self.size())
        return super().resizeEvent(event)

    def moveEvent(self, event):
        self.settings.setValue("pos", self.pos())
        return super().moveEvent(event)

    def closeEvent(self, event):
        self.exit_now = True
        return super().closeEvent(event)

    def hideEvent(self, event):
        self.setEnabled(True)
        self.button.setEnabled(True)
        self.input.clear()
        self.input.setEnabled(True)
        self.input.setReadOnly(False)
        return super().hideEvent(event)

    def message(self, message, *args):
        self.input.setText(message.format(*args))
        QTimer.singleShot(500, self.accept)

    def go(self):
        self.setEnabled(False)
        text = self.input.text().strip()
        if not text:
            self.message("empty input; doing nothing...")
            return
        name, sep, argument = text.partition(' ')
        command = self.commands.get(name)
        if not command:
            self.message("unable to comply: command '{0}' not found", name)
            return
        if not argument:
            argument = QApplication.clipboard().text(QClipboard.Selection)
        self.message("running command '{0}'...", name)
        QProcess.startDetached(*command(argument))

    def help(self):
        print('help()')

    def about(self):
        QMessageBox.about(self, "About ubq",
            "<h3>ubq 0.5</h3><p>an application launcher inspired by "
            "<a href='http://wiki.mozilla.org/Labs/Ubiquity'>Ubiquity</a></p>"
        )



def make_command(placeholder, program, *arguments):
    def command(arg=''):
        return program, list(arguments)
    return command

def make_raw_command(placeholder, program, *arguments):
    def command(arg=''):
        return program, [a.replace(placeholder, arg) for a in arguments]
    return command

def make_urlencode_command(placeholder, program, *arguments):
    def command(arg=''):
        arg = urllib.parse.quote_plus(arg)
        return program, [a.replace(placeholder, arg) for a in arguments]
    return command

def load_commands(lines, placeholder, command_types):
    commands = {}
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = shlex.split(line)
        if len(parts) < 3:
            continue
        name, command_type, *command = parts
        if command_type not in command_types:
            continue
        commands[name] = command_types[command_type](placeholder, *command)
    return commands


command_types = {
    'nop': make_command,
    'raw': make_raw_command,
    'url': make_urlencode_command,
}


def make_parser():
    parser = argparse.ArgumentParser(description=
        "an application launcher inspired by Ubiquity "
        "<https://wiki.mozilla.org/Labs/Ubiquity>")
    parser.add_argument('config',
        metavar='CONFIG', nargs='?', default=os.path.expanduser('~/.ubq'),
        help="configuration file; defaults to ~/.ubq")
    parser.add_argument('-p',
        metavar="PLACEHOLDER", default='____',
        help="argument placeholder; defaults to '____'")
    parser.add_argument('-v', action='version', version='ubq 0.5')
    return parser


def main(args=None):
    parser = make_parser()
    args = parser.parse_args(args)

    try:
        with open(args.config) as f:
            commands = load_commands(f, args.p, command_types)
    except (IOError, OSError) as e:
        sys.exit("{}: {}: '{}'".format(os.path.basename(sys.argv[0]),
            e.strerror.lower(), e.filename))

    app = QApplication(sys.argv)
    app.setOrganizationName("ubq")
    app.setApplicationName("ubq")
    dialog = Dialog(commands)

    signal.signal(signal.SIGUSR1, lambda *args: None)
    signal.signal(signal.SIGINT, lambda *args: sys.exit())

    while True:
        dialog.exec_()
        if dialog.exit_now:
            sys.exit()
        signal.pause()



if __name__ == "__main__":

     main()

