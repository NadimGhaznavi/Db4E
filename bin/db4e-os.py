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

DB4E_CORE = ['db4e', 'p2pool', 'xmrig', 'monerod', 'repo']

DISPLAY_NAMES = {
    'db4e'    : 'db4e core',
    'p2pool'  : 'P2Pool daemon',
    'xmrig'   : 'XMRig miner',
    'monerod' : 'Monero daemon',
    'repo'    : 'Website repo'
}

PALETTE = [
    ('na', '', ''),
    ('title', 'dark green, bold', ''),    
    ('running', 'dark green, bold', ''),
    ('stopped', 'dark red', ''),
    ('not_installed', 'yellow', ''),
    ('button', 'light cyan', ''),
    ('reversed', 'standout', '')
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

NEW_DB4E_SERVICE_MSG = "Database 4 Everything Service Setup\n\n"
NEW_DB4E_SERVICE_MSG += "This screen lets you install db4e as a service. "
NEW_DB4E_SERVICE_MSG += "The service will start at boot time and is "
NEW_DB4E_SERVICE_MSG += "responsible for the following:\n\n"
NEW_DB4E_SERVICE_MSG += "* The Monero blockchain daemon(s).\n"
NEW_DB4E_SERVICE_MSG += "* The P2Pool daemon(s).\n"
NEW_DB4E_SERVICE_MSG += "* The XMRig miner(s)."

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
        for deployment in self._db.get_monerod_deployments():
            name = deployment['name']
            status = deployment['status']
            instance = deployment['instance']
            deployments[instance] = { 'name': name, 'status': status, 'instance': instance }
        return deployments

    def get_xmrig_deployments(self):
        deployments = {}
        for deployment in self._db.get_monerod_deployments():
            name = deployment['name']
            status = deployment['status']
            instance = deployment['instance']
            deployments[instance] = { 'name': name, 'status': status, 'instance': instance }
        return deployments
    
    def install_db4e_service(self):
        return self._os.install_db4e_service()

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
        self.main_loop = urwid.MainLoop(self.build_main_frame(), PALETTE, unhandled_input=self.exit_on_q)


    def build_deployments_list(self):
        items = []
        self.deployment_radios = []
        group = []

        # db4e radiobutton
        db4e = self.model.get_db4e_deployment()
        db4e_radio = urwid.RadioButton(group, '', on_state_change=self.select_deployment, user_data='db4e', state=('db4e' == self.selected_deployment))
        self.deployment_radios.append(db4e_radio)
        items.append(urwid.Columns([
            ('pack', db4e_radio), 
            urwid.Text(db4e['name']), 
            ('pack', urwid.Text(('', STATUS[db4e['status']])))
        ]))
        
        # repo radiobutton
        repo = self.model.get_repo_deployment()
        repo_radio = urwid.RadioButton(group, '', on_state_change=self.select_deployment, user_data='repo', state=('repo' == self.selected_deployment))
        self.deployment_radios.append(db4e_radio)
        items.append(urwid.Columns([
            ('pack', repo_radio), 
            urwid.Text(repo['name']), 
            ('pack', urwid.Text(('', STATUS[repo['status']])))
        ]))

        ### TODO add monerod, p2pool and xmrig instances
        monerod_list = self.model.get_monerod_deployments()
        p2pool_list = self.model.get_p2pool_deployments()
        xmrig_list = self.model.get_xmrig_deployments()

        res = urwid.Pile(items)
        res = urwid.Padding(res, right=2, left=2)
        return urwid.LineBox(res, title="Deployments", title_align="left", title_attr="title")

    def build_actions(self):
        action_list = [
            ('pack', urwid.Button(('button', 'More Info'), on_press=self.show_component_info)),
            ('pack', urwid.Button(('button', 'Exit'), on_press=self.exit_app))
        ]
        res = urwid.Columns(action_list)
        res = urwid.Padding(res, right=2, left=2)
        return urwid.LineBox(res, title="Actions", title_align="left", title_attr="title")

    def build_main_frame(self):
        deployments = self.build_deployments_list()
        actions = self.build_actions()
        left_panel = urwid.Pile([deployments, actions])
        columns = urwid.Columns([
            ('pack', left_panel),
            self.right_panel
        ])
        return urwid.LineBox(columns, title="Database 4 Everything", title_align="center", title_attr="title")

    def install_db4e_service(self, radiobutton):
        results = self.model.install_db4e_service()
        self.results_contents.set_text(results)

    def select_deployment(self, radio, new_state, deployment):
        if new_state:
            self.selected_deployment = deployment

    # The main screen shows this content
    def show_component_info(self, button):
        if self.selected_deployment == 'repo':
            repo = self.model.get_repo_deployment()
            if repo['status'] == 'not_installed':
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
        
        elif self.selected_deployment == 'db4e':
            db4e = self.model.get_db4e_deployment()
            if db4e['status'] == 'stopped':
                text = urwid.Text(NEW_DB4E_SERVICE_MSG)
                install_service_button = urwid.Columns([('pack', urwid.Button(('button', 'Install Service'), on_press=self.install_db4e_service))])
                results = urwid.LineBox(
                    self.results_contents,
                    title='Results',
                    title_align='left',
                    title_attr='title'
                )
                pile = urwid.Pile([
                    text, urwid.Divider(), results, urwid.Divider(), install_service_button])
                self.right_panel = urwid.LineBox(
                    urwid.Padding(pile, left=2, right=2),
                    title='Info', title_align="right", title_attr="title"
                )
                self.main_loop.widget = self.build_main_frame()

        else:
            self.right_panel = urwid.LineBox(
                urwid.Text('No info available.'),
                title='INFO', title_align='right', title_attr='title'
            )
            self.main_loop.widget = self.build_main_frame()
        

    def show_repo_setup(self, button):
        self.main_loop.widget = self.repo_setup_ui.widget()

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
