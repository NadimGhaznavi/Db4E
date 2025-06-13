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
import warnings
from urwid.widget.columns import ColumnsWarning

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
from Db4eOSDb.Db4eOSDb import Db4eOSDb
from Db4eOSRepoSetupUI.Db4eOSRepoSetupUI import Db4eOSRepoSetupUI
from Db4eOSDb4eSetupUI.Db4eOSDb4eSetupUI import Db4eOSDb4eSetupUI


# Needed, otherwise we get STDERR warnings being dumped into the TUI
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=ColumnsWarning)

DB4E_CORE = ['db4e', 'p2pool', 'xmrig', 'monerod', 'repo']

DISPLAY_NAMES = {
    'db4e'    : 'db4e core',
    'p2pool'  : 'P2Pool daemon',
    'xmrig'   : 'XMRig miner',
    'monerod' : 'Monero daemon',
    'repo'    : 'Website repo'
}

PALETTE = [
    ('title', 'dark green, bold', ''),
    ('button', 'light cyan', '')
]

STATUS = {
    'running'       : '🟢',
    'stopped'       : '🟡',
    'not_installed' : '🔴',
    'unknown'       : '❔'
}

WELCOME_MSG = "Welcome to the db4e OS console!\n\n"
WELCOME_MSG += "Use the arrow keys and the spacebar to select a component. "
WELCOME_MSG += "Use the spacebar or mouse to \"click\" the \"More Info\" or "
WELCOME_MSG += "\"Exit\" button. "

# Dummy model for status reporting and probing
class Db4eModel:
    def __init__(self):
        # ['db4e', 'p2pool', 'xmrig', 'monerod', 'repo']
        self.deployments = DB4E_CORE
        self._os = Db4eOS()
        self._db = Db4eOSDb()

    def get_db4e_deployment(self):
        db4e_rec = self._db.get_db4e_deployment()
        db4e = {
            'name': db4e_rec['name'],
            'status': db4e_rec['status']
        }
        return db4e
    
    def get_repo_deployment(self):
        repo_rec = self._db.get_repo_deployment()
        repo = {
            'name': repo_rec['name'],
            'status': repo_rec['status']
        }
        return repo

    def get_monerod_deployments(self):
        deployments = {}
        for deployment in self._db.get_monerod_deployments():
            name = deployment['name']
            status = deployment['status']
            instance = deployment['instance']
            deployments[instance] = { 'name': name, 'status': status, 'instance': instance }
        return deployments

    def get_p2pool_deployments(self):
        deployments = {}
        for deployment in self._db.get_p2pool_deployments():
            name = deployment['name']
            status = deployment['status']
            instance = deployment['instance']
            deployments[instance] = { 'name': name, 'status': status, 'instance': instance }
        return deployments

    def get_xmrig_deployments(self):
        deployments = {}
        for deployment in self._db.get_xmrig_deployments():
            name = deployment['name']
            status = deployment['status']
            instance = deployment['instance']
            deployments[instance] = { 'name': name, 'status': status, 'instance': instance }
        return deployments
    
    def update_db4e(self, update_fields):
        self._db.update_db4e(update_fields)

    def update_repo(self, update_fields):
        self._db.update_repo(update_fields)

    def update_monerod(self, update_fields, instance):
        self._db.update_monerod(update_fields, instance)

    def update_p2pool(self, update_fields, instance):
        self._db.update_p2pool(update_fields, instance)

    def update_xmrig(self, update_fields, instance):
        self._db.update_xmrig(update_fields, instance)

class Db4eTui:
    def __init__(self):
        self.model = Db4eModel()
        self.selected_deployment = 'db4e'
        self.deployment_radios = []
        self.right_panel = urwid.LineBox(urwid.Padding(
            urwid.Text(WELCOME_MSG),
            right=2, left=2),
            title='Info', title_align="right", title_attr="title")
        self.results_contents = urwid.Text('')
        
        self.repo_setup_ui = Db4eOSRepoSetupUI(self)
        self.db4e_setup_ui = Db4eOSDb4eSetupUI(self)

        self.main_loop = urwid.MainLoop(self.build_main_frame(), PALETTE, unhandled_input=self.exit_on_q)

    def build_actions(self):
        action_list = [
            (13, urwid.Button(('button', 'More Info'), on_press=self.show_component_info)),
            (8, urwid.Button(('button', 'Exit'), on_press=self.exit_app))
        ]
        res = urwid.Columns(action_list, dividechars=1)
        res = urwid.Padding(res, right=2, left=2)
        return urwid.LineBox(res, title="Actions", title_align="left", title_attr="title")

    def build_deployments_list(self):
        all_items = []
        self.deployment_radios = []
        group = []

        db4e_items = []
        # db4e radiobutton
        db4e = self.model.get_db4e_deployment()
        db4e_radio = urwid.RadioButton(group, db4e['name'], on_state_change=self.select_deployment, user_data='db4e', state=('db4e' == self.selected_deployment))
        self.deployment_radios.append(db4e_radio)
        db4e_items.append(urwid.Columns([
            (20, db4e_radio), 
            (3, urwid.Text(('', STATUS[db4e['status']]), wrap='clip'))
        ], dividechars=1))
        
        # repo radiobutton
        repo = self.model.get_repo_deployment()
        repo_radio = urwid.RadioButton(group, repo['name'], on_state_change=self.select_deployment, user_data='repo', state=('repo' == self.selected_deployment))
        self.deployment_radios.append(repo_radio)
        db4e_items.append(urwid.Columns([
            (20, repo_radio), 
            (3, urwid.Text(('', STATUS[repo['status']]), wrap='clip'))
        ], dividechars=1))

        db4e_items = urwid.Pile(db4e_items)
        db4e_items = urwid.Padding(db4e_items, right=2, left=2)
        all_items.append(urwid.LineBox(db4e_items, title="db4e core", title_align="left", title_attr="title"))

        # instance groups
        all_items.append(self.build_instance_box("Monero Daemon(s)", self.model.get_monerod_deployments(), group))
        all_items.append(self.build_instance_box("P2Pool(s)", self.model.get_p2pool_deployments(), group))
        all_items.append(self.build_instance_box("XMRig Miner(s)", self.model.get_xmrig_deployments(), group))

        return urwid.Pile(all_items)

    def build_instance_box(self, title, instances_dict, group):
        items = []
        for instance_name, data in sorted(instances_dict.items()):
            is_selected = (instance_name == self.selected_deployment)
            radio = urwid.RadioButton(
                group,
                data['name'],
                on_state_change=self.select_deployment,
                user_data=instance_name,
                state=is_selected
            )
            self.deployment_radios.append(radio)
            items.append(urwid.Columns([
                (20, radio),
                (3, urwid.Text(('', STATUS[data['status']]), wrap='clip'))
            ], dividechars=1))
        return urwid.LineBox(urwid.Padding(urwid.Pile(items), left=2, right=2), title=title, title_align="left", title_attr="title")

        """
                # Monero daemon radiobutton(s)
        monerod_items = []
        monerod_list = self.model.get_monerod_deployments()
        for monerod in monerod_list:
            monerod_radio = urwid.RadioButton(
                group, monerod_list[monerod]['name'], on_state_change=self.select_deployment, 
                user_data=monerod_list['instance'], state=(monerod_list['instance'] == self.selected_deployment))
            self.deployment_radios.append(monerod_radio)
            monerod_items.append(urwid.Columns([
                (20, monerod_radio),
                (3, urwid.Text(('', STATUS[repo['status']]), wrap='clip'))
            ], dividechars=1))
        monerod_box = urwid.Pile(monerod_items)
        monerod_box = urwid.Padding(monerod_box, right=2, left=2)
        monerod_box = urwid.LineBox(monerod_box, title="Monero Daemon(s)", title_align="left", title_attr="title")
        items.append(monerod_box)

        ### TODO p2pool and xmrig instances
        p2pool_list = self.model.get_p2pool_deployments()
        xmrig_list = self.model.get_xmrig_deployments()

        """

    def build_main_frame(self):
        deployments = self.build_deployments_list()
        actions = self.build_actions()
        left_panel = urwid.Pile([deployments, actions])
        columns = urwid.Columns([
            ('weight', 1, left_panel),
            ('weight', 3, self.right_panel)
        ], dividechars=1)
        
        return urwid.LineBox(columns, title="Database 4 Everything", title_align="center", title_attr="title")

    def exit_app(self, button):
        raise urwid.ExitMainLoop()
    
    def exit_on_q(self, key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()

    def return_to_main(self):
        self.right_panel = urwid.LineBox(urwid.Padding(
            urwid.Text(WELCOME_MSG),
            right=2, left=2),
            title='TIME', title_align="right", title_attr="title")
        self.main_loop.widget = self.build_main_frame()

    # The main screen shows this content
    def show_component_info(self, button):
        deployment = self.selected_deployment
        if deployment == 'db4e':
            db4e = self.model.get_db4e_deployment()
            if db4e['status'] == 'stopped':
                setup_service_msg = self.db4e_setup_ui.setup_service_msg()
                text_msg = urwid.Text(setup_service_msg)
                install_service_button = urwid.Columns([
                    (12, urwid.Button(('button', 'Continue'), on_press=self.show_db4e_setup))
                ])
                widgets = [text_msg, urwid.Divider(), install_service_button]
                # Wrap in a ListBox to make scrollable
                listbox = urwid.ListBox(urwid.SimpleFocusListWalker(widgets))
                self.right_panel = urwid.LineBox(
                    urwid.Padding(listbox, left=2, right=2),
                    title='Info', title_align="right", title_attr="title"
                )
                self.main_loop.widget = self.build_main_frame()
                return

        elif deployment == 'repo':
            repo = self.model.get_repo_deployment()
            if repo['status'] == 'not_installed':
                new_repo_msg = self.repo_setup_ui.new_repo_msg()
                text_msg = urwid.Text(new_repo_msg)
                continue_button = urwid.Columns([
                    (12, urwid.Button(('button', 'Continue'), on_press=self.show_repo_setup))
                ])
                widgets = [text_msg, urwid.Divider(), continue_button]
                # Wrap in a ListBox to make scrollable
                listbox = urwid.ListBox(urwid.SimpleFocusListWalker(widgets))
                self.right_panel = urwid.LineBox(
                    urwid.Padding(listbox, left=2, right=2),
                    title='Info', title_align="right", title_attr="title"
                )
                self.main_loop.widget = self.build_main_frame()
                return

        else:
            self.right_panel = urwid.LineBox(
                urwid.Padding(urwid.Text('No info available.'), left=2, right=2),
                title='INFO', title_align='right', title_attr='title'
            )
            self.main_loop.widget = self.build_main_frame()

    def show_db4e_setup(self, button):
        self.main_loop.widget = self.db4e_setup_ui.widget()

    def show_repo_setup(self, button):
        self.main_loop.widget = self.repo_setup_ui.widget()

    def select_deployment(self, radio, new_state, deployment):
        if new_state:
            self.selected_deployment = deployment

    def run(self):
        try:
            self.main_loop.run()
        except KeyboardInterrupt:
            print('Exiting...')
            sys.exit(0)


if __name__ == '__main__':
    Db4eTui().run()
