"""
lib/Mining/Db4eOSTui.py

This is the db4e-os view, which is part of db4e-os MVC pattern.
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

from Db4eOSModel.Db4eOSModel import Db4eOSModel
from Db4eOSRepoSetupUI.Db4eOSRepoSetupUI import Db4eOSRepoSetupUI
from Db4eOSDb4eSetupUI.Db4eOSDb4eSetupUI import Db4eOSDb4eSetupUI
from Db4eOSMonerodRemoteSetupUI.Db4eOSMonerodRemoteSetupUI import Db4eOSMonerodRemoteSetupUI
from Db4eOSP2PoolRemoteSetupUI.Db4eOSP2PoolRemoteSetupUI import Db4eOSP2PoolRemoteSetupUI
from Db4eOSXMRigSetupUI.Db4eOSXMRigSetupUI import Db4eOSXMRigSetupUI


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
WELCOME_MSG += "Use the spacebar or mouse to click the \"More Info\" or "
WELCOME_MSG += "\"Exit\" button. "

MONEROD_SETUP = "Monero Blockchain Daemon Setup\n\n"
MONEROD_SETUP = "This screen lets you setup a Monero blockchain daemon. "
MONEROD_SETUP += "You have two deployment choices: You can either configure "
MONEROD_SETUP += "db4e to use an existing remote Monero daemon or you can "
MONEROD_SETUP += "setup a Monero daemon on this machine."

P2POOL_PREREQ = "P2Pool Daemon Pre-Requisites\n\n"
P2POOL_PREREQ += "You must create a Monero daemon deployment before setting "
P2POOL_PREREQ += "up P2Pool."

P2POOL_SETUP = "P2Pool Daemon Setup\n\n"
P2POOL_SETUP += "This screen lets you setup a P2Pool daemon. You have two "
P2POOL_SETUP += "deployment choices: You can either configure db4e to use an "
P2POOL_SETUP += "existing remote P2Pool daemon or you can setup a P2Pool "
P2POOL_SETUP += "daemon on this machine. You must deploy a Monero daemon "
P2POOL_SETUP += "before configuring P2Pool."

XMRIG_SETUP = "XMRig Miner Setup\n\n"
XMRIG_SETUP += "This screen lets you setup a XMRig miner. This is a local "
XMRIG_SETUP += "installation: The XMRig miner will be deployed and running "
XMRIG_SETUP += "on this machine. You must configure a P2Pool daemon before "
XMRIG_SETUP += "you setup XMRig."

XMRIG_PREREQ = "XMRig Miner Pre-Requisites\n\n"
XMRIG_PREREQ += "You must create a P2Pool daemon deployment before setting "
XMRIG_PREREQ += "up XMRig."

class Db4eOSTui:
    def __init__(self):
        self.model = Db4eOSModel()
        self.selected_deployment = 'db4e'
        self.deployment_radios = []
        self.right_panel = urwid.LineBox(urwid.Padding(
            urwid.Text(WELCOME_MSG),
            right=2, left=2),
            title='Info', title_align="right", title_attr="title")
        self.results_contents = urwid.Text('')
        
        self.repo_setup_ui = Db4eOSRepoSetupUI(self)
        self.db4e_setup_ui = Db4eOSDb4eSetupUI(self)
        self.monerod_remote_setup_ui = Db4eOSMonerodRemoteSetupUI(self)
        self.p2pool_remote_setup_ui = Db4eOSP2PoolRemoteSetupUI(self)
        self.xmrig_setup_ui = Db4eOSXMRigSetupUI(self)

        self.main_loop = urwid.MainLoop(self.build_main_frame(), PALETTE, unhandled_input=self.exit_on_q)

    def add_new_monerod(self, button):
        text_msg = urwid.Text(MONEROD_SETUP)
        continue_button = urwid.Columns([
            (9, urwid.Button(('button', 'Local'), on_press=self.show_monerod_setup)),
            (10, urwid.Button(('button', 'Remote'), on_press=self.show_remote_monerod_setup))
        ], dividechars=2)
        widgets = [text_msg, urwid.Divider(), continue_button]
        # Wrap in a ListBox to make scrollable
        listbox = urwid.ListBox(urwid.SimpleFocusListWalker(widgets))
        self.right_panel = urwid.LineBox(
            urwid.Padding(listbox, left=2, right=2),
            title='Info', title_align="right", title_attr="title"
        )
        self.main_loop.widget = self.build_main_frame()
        return

    def add_new_p2pool(self, button):
        if not self.model.get_monerod_deployments():
            # You need to have a Monero daemon deployment before setting up a P2Pool instance.
            text_msg = urwid.Text(P2POOL_PREREQ)
            self.right_panel = urwid.LineBox(text_msg)
            self.main_loop.widget = self.build_main_frame()
            return

        text_msg = urwid.Text(P2POOL_SETUP)
        continue_button = urwid.Columns([
            (9, urwid.Button(('button', 'Local'), on_press=self.show_p2pool_setup)),
            (10, urwid.Button(('button', 'Remote'), on_press=self.show_remote_p2pool_setup))
        ], dividechars=2)
        widgets = [text_msg, urwid.Divider(), continue_button]
        # Wrap in a ListBox to make scrollable
        listbox = urwid.ListBox(urwid.SimpleFocusListWalker(widgets))
        self.right_panel = urwid.LineBox(
            urwid.Padding(listbox, left=2, right=2),
            title='Info', title_align="right", title_attr="title"
        )
        self.main_loop.widget = self.build_main_frame()
        return
    
    def add_new_xmrig(self, button):
        if not self.model.get_p2pool_deployments():
            # You need to have a P2Pool daemon deployment before setting up a XMRig instance.
            text_msg = urwid.Text(XMRIG_PREREQ)
            self.right_panel = urwid.LineBox(text_msg)
            self.main_loop.widget = self.build_main_frame()
            return

        text_msg = urwid.Text(XMRIG_SETUP)
        continue_button = urwid.Columns([
            (12, urwid.Button(('button', 'Continue'), on_press=self.show_xmrig_setup)),
        ], dividechars=2)
        widgets = [text_msg, urwid.Divider(), continue_button]
        # Wrap in a ListBox to make scrollable
        listbox = urwid.ListBox(urwid.SimpleFocusListWalker(widgets))
        self.right_panel = urwid.LineBox(
            urwid.Padding(listbox, left=2, right=2),
            title='Info', title_align="right", title_attr="title"
        )
        self.main_loop.widget = self.build_main_frame()
        return
    
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
        all_items.append(self.build_instance_box("Monero Daemon(s)", self.model.get_monerod_deployments(), group, 'monerod'))
        all_items.append(self.build_instance_box("P2Pool(s)", self.model.get_p2pool_deployments(), group, 'p2pool'))
        all_items.append(self.build_instance_box("XMRig Miner(s)", self.model.get_xmrig_deployments(), group, 'xmrig'))

        return urwid.Pile(all_items)

    def build_instance_box(self, title, instances_dict, group, depl_type):
        items = []
        for instance_name, data in sorted(instances_dict.items()):
            is_selected = (instance_name == self.selected_deployment)
            radio = urwid.RadioButton(
                group,
                data['instance'],
                on_state_change=self.select_deployment,
                user_data=depl_type + ':' + instance_name,
                state=is_selected
            )
            self.deployment_radios.append(radio)
            items.append(urwid.Columns([
                (20, radio),
                (3, urwid.Text(('', STATUS[data['status']]), wrap='clip'))
            ], dividechars=1))

        # Dynamically construct the method name
        callback_method_name = f'add_new_{depl_type}'
        on_add_callback = getattr(self, callback_method_name, None)
        add_button = urwid.Button(('button', 'New Deployment'), on_press=on_add_callback)
        add_button = urwid.Columns([(18, add_button)])
        items.append(add_button)    
        return urwid.LineBox(urwid.Padding(urwid.Pile(items), left=2, right=2), title=title, title_align="left", title_attr="title")

    def build_main_frame(self):
        deployments = self.build_deployments_list()
        actions = self.build_actions()
        left_panel = urwid.Pile([deployments, actions])
        columns = urwid.Columns([
            (30, left_panel),
            self.right_panel
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

    def select_deployment(self, radio, new_state, deployment):
        if new_state:
            self.selected_deployment = deployment

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
            
            elif db4e['status'] == 'running':
                header_msg = urwid.Text('db4e Service Status\n')
                status = self.model.get_db4e_status()
                status_msg = urwid.Text('* ' + status['service_installed'] )
                enabled_msg = urwid.Text('* ' + status['service_enabled'] )
                running_msg = urwid.Text('* ' + status['service_running'] )
                listbox = urwid.ListBox(urwid.SimpleFocusListWalker([
                    header_msg, status_msg, enabled_msg, running_msg]))
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
            
            elif repo['status'] == 'running':
                header_msg = urwid.Text('Website Repository Status\n')
                repo_dir = self.model.get_repo_dir()
                status = '* Repo is properly configured\n'
                status += f'* Repo is in directory ({repo_dir})'
                status_msg = urwid.Text(status)
                listbox = urwid.ListBox(urwid.SimpleFocusListWalker([
                    header_msg, status_msg]))
                self.right_panel = urwid.LineBox(
                    urwid.Padding(listbox, left=2, right=2),
                    title='Info', title_align="right", title_attr="title"
                )
                self.main_loop.widget = self.build_main_frame()
                return

        else:
            depl_type = deployment.split(':')[0]
            instance = deployment.split(':')[1]
            if depl_type == 'monerod':
                depl = self.model.get_monerod_deployment(instance)
                return
                # TBD - Handle reconfiguration of an existing deployment

            else:
                self.right_panel = urwid.LineBox(
                    urwid.Padding(urwid.Text(f'No info available for {deployment}.'), left=2, right=2),
                    title='INFO', title_align='right', title_attr='title'
                )
                self.main_loop.widget = self.build_main_frame()

    def show_db4e_setup(self, button):
        self.main_loop.widget = self.db4e_setup_ui.widget()

    def show_monerod_setup(self, button):
        pass

    def show_remote_monerod_setup(self, button):
        self.main_loop.widget = self.monerod_remote_setup_ui.widget()

    def show_p2pool_setup(self, button):
        pass

    def show_remote_p2pool_setup(self, button):
        self.main_loop.widget = self.p2pool_remote_setup_ui.widget()

    def show_repo_setup(self, button):
        self.main_loop.widget = self.repo_setup_ui.widget()

    def show_xmrig_setup(self, button):
        self.main_loop.widget = self.xmrig_setup_ui.widget()

    def run(self):
        try:
            self.main_loop.run()
        except KeyboardInterrupt:
            print('Exiting...')
            sys.exit(0)

