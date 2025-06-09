#!/opt/prod/db4e/venv/bin/python
# Use venv environment for Python
"""
bin/db4e-os.py
"""

# Import supporting modules
import os, sys
import urwid

# The directory that this script is in
script_dir = os.path.dirname(__file__)
# DB4E modules are in the lib_dir
lib_dir = script_dir + '/../lib/'

# Import DB4E modules
db4e_dirs = [
  lib_dir + 'Infrastructure',
  lib_dir + 'Mining'
]
for db4e_dir in db4e_dirs:
  sys.path.append(db4e_dir)

from Db4eConfig.Db4eConfig import Db4eConfig
from Db4eOS.Db4eOS import Db4eOS

class Model:
    def __init__(self):
        # Get access to the YAML data through Db4eConfig
        ini = Db4eConfig()

        # Init daemon checker
        self.os = Db4eOS()

        # Load the data from Db4eConfig
        self.daemon_data = {}
        self.daemon_list = ['monerod', 'p2pool', 'xmrig']
        for daemon in self.daemon_list:
            install_dir = ini.config[daemon]['install_dir']
            proc_name = ini.config[daemon]['proc_name']
            pid = self.os.get_pid(proc_name)
            if pid:
                status = "UP"
            elif os.path.exists(install_dir):
                status = "DOWN"
            else:
                status = "N/A"
            self.daemon_data[daemon] = {
                'name': daemon,
                'install_dir': install_dir,
                'proc_name': proc_name,
                'status': status
            }
        # Set the default daemon to the first one
        self.cur_daemon = self.daemon_list[0]

    def get_daemon_data(self):
        return self.daemon_data

    def set_daemon(self, daemon):
        self.cur_daemon = daemon

    def get_daemon(self):
        return self.cur_daemon

    def get_daemon_list(self):
        return self.daemon_list

class View:
    def __init__(self, model):
        self.model = model
        self.text_widget = urwid.Text("", align='center')
        self.message = urwid.Text("", align='center')
        self.radio_buttons = self._build_radio_buttons()

        self.main_widget = urwid.Filler(
            urwid.Pile([
                #urwid.Text(f'Timestamp', 'right'),

                urwid.LineBox(urwid.Pile(self.radio_buttons), 'Select a Component'),
                urwid.Divider(),
                self.text_widget,
                self.message
            ]), valign='top')

    def _build_radio_buttons(self):
        daemon_list = self.model.get_daemon_list()
        group = []
        buttons = []
        #data = self.model.get_daemon_data()
        for daemon in daemon_list:
            #label = f"{daemon} [{data[daemon]['status']}]"
            label = f'{daemon}'
            #btn = urwid.RadioButton(group, label, state=(daemon == self.model.get_daemon()))
            btn = urwid.RadioButton(group, label)
            urwid.connect_signal(btn, 'change', self._on_radio_change, daemon)
            buttons.append(btn)
        return buttons

    def _on_radio_change(self, button, state, daemon):
        if state:
            self.model.set_daemon(daemon)
            self.update_display(f"Selected daemon: {daemon}")

    def get_widgets(self):
        return self.main_widget

    def update_display(self, data):
        self.text_widget.set_text(f"{data}")

    def set_message(self, msg):
        self.message.set_text(msg)

class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.loop = urwid.MainLoop(
            view.get_widgets(),
            unhandled_input=self.handle_input)

    def start(self):
        # str(self.model.get_daemon_data())
        self.view.update_display('Welcome to the db4e OS!')
        self.loop.run()

    def handle_input(self, key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()


def main():
    model = Model()
    view = View(model)
    controller = Controller(model, view)
    controller.start()

if __name__ == '__main__':
    main()
