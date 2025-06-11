"""
bin/db4e-os.py

This is the db4e TUI; terminal user interface. It is used to manage
and deploy the db4e software as well as the Monero Blockchain daemon,
the P2Pool daemon, the XMRig miner and the db4e website GitHub 
repository
"""


"""
  This file is part of *db4e*, the *Database 4 Everything* project
  <https://github.com/NadimGhaznavi/db4e>, developed independently
  by Nadim-Daniel Ghaznavi. Copyright (c) 2024-2025 NadimGhaznavi
  <https://github.com/NadimGhaznavi/db4e>.
 
  This program is free software: you can redistribute it and/or 
  modify it under the terms of the GNU General Public License as 
  published by the Free Software Foundation, version 3.
 
  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
  General Public License for more details.

  You should have received a copy (LICENSE.txt) of the GNU General 
  Public License along with this program. If not, see 
  <http://www.gnu.org/licenses/>.
"""

# Import supporting modules
import urwid
import os, sys
import subprocess
import psutil

# Where the DB4E modules live
lib_dir = os.path.dirname(__file__) + "/../lib/"
# Import DB4E modules
db4e_dirs = [
  lib_dir + 'Infrastructure',
  lib_dir + 'Mining'
]
for db4e_dir in db4e_dirs:
  sys.path.append(db4e_dir)

# DB4E modules
from Db4eOS.Db4eOS import Db4eOS
from Db4eRepoSetupUI.Db4eRepoSetupUI import Db4eRepoSetupUI

DB4E_CORE = ['db4e', 'p2pool', 'xmrig', 'monerod', 'repo']

DISPLAY_NAMES = {
    'db4e': 'db4e core',
    'p2pool': 'P2Pool daemon',
    'xmrig': 'XMRig miner',
    'monerod': 'Monero daemon',
    'repo': 'Website repo'
}

PALETTE = [
    ('na', '', ''),
    ('title', 'dark green, bold', ''),    
    ('bold', 'bold', ''),
    ('running', 'dark green,bold', ''),
    ('stopped', 'dark red', ''),
    ('not_installed', 'yellow', ''),
    ('button', 'light cyan', ''),
    ('reversed', 'standout', '')
]

STATUS = {
    'running': '🟢',
    'stopped': '🟡',
    'not_installed': '🔴',
    'unknown': '❔'
}

WELCOME_MSG = "Welcome to the db4e OS console!\n\n"
WELCOME_MSG += "Use the arrow keys and the spacebar to select a component. "
WELCOME_MSG += "Use the spacebar or mouse to \"click\" the \"More Info\" or "
WELCOME_MSG += "\"Exit\" button. "

# Dummy model for status reporting and probing
class Db4eModel:
    def __init__(self):
        # ['db4e', 'p2pool', 'xmrig', 'monerod', 'repo']
        self.daemons = DB4E_CORE
        self.os = Db4eOS()
        
    def get_daemons(self):
        return self.daemons

    def get_daemon_status(self, name):
        # TODO: Replace with actual probe logic
        return {
            'db4e'   : (STATUS[self.os.get_status('db4e')], ''),
            'p2pool' : (STATUS[self.os.get_status('p2pool')], ''),
            'xmrig'  : (STATUS[self.os.get_status('xmrig')], ''),
            'monerod': (STATUS[self.os.get_status('monerod')], ''),
            'repo'   : (STATUS[self.os.get_status('repo')], '')
        }.get(name, ('N/A', ''))
    
    def get_db4e_info(self):
        # TODO: Replace with actual info
        return 'Some db4e info to display'

    def get_p2pool_info(self):
        # TODO: Replace with actual info
        return 'Some p2pool info to display'

    def get_xmrig_info(self):
        # TODO: Replace with actual info
        return 'Some xmrig info to display'

    def get_monerod_info(self):
        # TODO: Replace with actual info
        return 'Some monerod info to display'

    def get_repo_info(self):
        repo = self.os.get_info('repo')
        if 'install_path' not in repo:
            new_repo_msg = self.os.new_repo_msg()
            return new_repo_msg
        
    def set_daemon_status(self, daemon, status):
        self.os.depl[daemon]['status'] = status

class Db4eTui:
    def __init__(self):
        self.model = Db4eModel()
        self.os = Db4eOS()
        self.selected_daemon = 'db4e'
        self.daemon_radios = []
        self.right_panel = urwid.LineBox(urwid.Padding(
            urwid.Text(WELCOME_MSG),
            right=2, left=2),
            title='Info', title_align="right", title_attr="title")
        
        self.repo_setup_ui = Db4eRepoSetupUI(self) 
        self.main_loop = urwid.MainLoop(self.build_main_frame(), PALETTE, unhandled_input=self.exit_on_q)

    def build_daemon_list(self):
        items = []
        self.daemon_radios = []
        group = []
        for daemon in self.model.get_daemons():
            name = DISPLAY_NAMES.get(daemon, daemon)
            status_text, status_style = self.model.get_daemon_status(daemon)
            radio = urwid.RadioButton(group, '', on_state_change=self.select_daemon, user_data=daemon, state=(daemon == self.selected_daemon))
            self.daemon_radios.append(radio)
            row = urwid.Columns([
                ('pack', radio),
                urwid.Text(name),
                ('pack', urwid.Text((status_style, status_text)))
            ])
            items.append(row)
        res = urwid.Pile(items)
        res = urwid.Padding(res, right=2, left=2)
        return urwid.LineBox(res, title="Components", title_align="left", title_attr="title")

    def build_actions(self):
        action_list = [
            ('pack', urwid.Button(('button', 'More Info'), on_press=self.show_component_info)),
            ('pack', urwid.Button(('button', 'Exit'), on_press=self.exit_app))
        ]
        res = urwid.Columns(action_list)
        res = urwid.Padding(res, right=2, left=2)
        return urwid.LineBox(res, title="Actions", title_align="left", title_attr="title")

    def build_main_frame(self):
        components = self.build_daemon_list()
        actions = self.build_actions()
        left_panel = urwid.Pile([components, actions])
        columns = urwid.Columns([
            ('pack', left_panel),
            self.right_panel
        ])
        return urwid.LineBox(columns, title="Database 4 Everything", title_align="center", title_attr="title")

    def select_daemon(self, radio, new_state, daemon):
        if new_state:
            self.selected_daemon = daemon

    # The main screen shows this content
    def show_component_info(self, button):
        if self.selected_daemon == 'repo':
            repo = self.model.os.get_info('repo')
            if 'install_path' not in repo:
                new_repo_msg = self.repo_setup_ui.new_repo_msg()
                text = urwid.Text(new_repo_msg)
                continue_button = urwid.Columns([('pack', urwid.Button(('button', 'Continue'), on_press=self.show_repo_setup))])
                pile = urwid.Pile([text, urwid.Divider(), continue_button])
                self.right_panel = urwid.LineBox(
                    urwid.Padding(pile, left=2, right=2),
                    title='Info', title_align="right", title_attr="title"
                )
                self.main_loop.widget = self.build_main_frame()
                return

        func_name = f'get_{self.selected_daemon}_info'
        info = getattr(self.model, func_name, lambda: 'No info available')()
        self.right_panel = urwid.LineBox(
            urwid.Text(info),
            title='INFO', title_align='right', title_attr='title'
        )
        self.main_loop.widget = self.build_main_frame()

    def show_repo_setup(self, button):
        self.main_loop.widget = self.repo_setup_ui.widget()
        if self.os.probe_env('repo') == 'running':
            self.model.set_daemon_status('repo', 'running')
        else:
            self.model.set_daemon_status('repo', 'not_installed')

    def return_to_main(self):
        self.right_panel = urwid.LineBox(urwid.Padding(
            urwid.Text(WELCOME_MSG),
            right=2, left=2),
            title='TIME', title_align="right", title_attr="title")
        self.main_loop.widget = self.build_main_frame()

    def exit_app(self, button):
        raise urwid.ExitMainLoop()
    
    def exit_on_q(self, key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()

    def run(self):
        try:
            self.main_loop.run()
        except KeyboardInterrupt:
            print('Exiting...')
            sys.exit(0)


if __name__ == '__main__':
    Db4eTui().run()
