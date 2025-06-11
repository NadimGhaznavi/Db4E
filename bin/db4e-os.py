"""
bin/db4e-os.py
"""
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
    ('button', 'light cyan,bold', ''),
    ('reversed', 'standout', '')
]

WELCOME_MSG = "Welcome to the db4e OS console\n\n"
WELCOME_MSG += "Use the arrow keys and the spacebar to select a component. "
WELCOME_MSG += "Use the spacebar to \"click\" the \"More Info\" or \"Exit\" button. "

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
            'db4e': (self.os.depl['db4e']['status'], ''),
            'p2pool': (self.os.depl['p2pool']['status'], ''),
            'xmrig': (self.os.depl['xmrig']['status'], ''),
            'monerod': (self.os.depl['monerod']['status'], ''),
            'repo': (self.os.depl['repo']['status'], '')
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
            return 'Not initialized'

class Db4eTui:
    def __init__(self):
        self.model = Db4eModel()
        self.selected_daemon = 'db4e'
        self.daemon_radios = []
        self.right_panel = urwid.LineBox(urwid.Padding(
            urwid.Text(WELCOME_MSG),
            right=2, left=2),
            title='TIME', title_align="right", title_attr="title")
            
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
            urwid.Button("More Info", on_press=self.show_component_info),
            urwid.Button("Exit", on_press=lambda b: exit(0))
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
        func_name = f'get_{self.selected_daemon}_info'
        info = getattr(self.model, func_name, lambda: 'No info available')()
        self.right_panel = urwid.LineBox(
            urwid.Text(info),
            title='INFO', title_align="right", title_attr="title"
        )
        self.main_loop.widget = self.build_main_frame()

    def exit_on_q(self, key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()

    def run(self):
        self.main_loop.run()


if __name__ == '__main__':
    Db4eTui().run()
