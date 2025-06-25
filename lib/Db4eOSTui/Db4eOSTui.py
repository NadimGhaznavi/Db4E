"""
lib/Db4eOSTui/Db4eOSTui.py

This is the db4e-os view, which is part of db4e-os MVC pattern.


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
lib_dir = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(lib_dir)

### Import DB4E modules
from Db4eOSModel.Db4eOSModel import Db4eOSModel
from Db4eClient.Db4eClient import Db4eClient
from Db4eOSStrings.Db4eOSStrings import MD
## Mini TUIs
# Setup new component
from Db4eOSInstallDb4eServiceUI.Db4eOSInstallDb4eServiceUI import Db4eOSInstallDb4eServiceUI
from Db4eOSInitialSetupUI.Db4eOSInitialSetupUI import Db4eOSInitialSetupUI
from Db4eOSRepoSetupUI.Db4eOSRepoSetupUI import Db4eOSRepoSetupUI
from Db4eOSMonerodRemoteSetupUI.Db4eOSMonerodRemoteSetupUI import Db4eOSMonerodRemoteSetupUI
from Db4eOSP2PoolSetupUI.Db4eOSP2PoolSetupUI import Db4eOSP2PoolSetupUI
from Db4eOSP2PoolRemoteSetupUI.Db4eOSP2PoolRemoteSetupUI import Db4eOSP2PoolRemoteSetupUI
from Db4eOSXMRigSetupUI.Db4eOSXMRigSetupUI import Db4eOSXMRigSetupUI
# Edit component
from Db4eOSDb4eEditUI.Db4eOSDb4eEditUI import Db4eOSDb4eEditUI
from Db4eOSRepoEditUI.Db4eOSRepoEditUI import Db4eOSRepoEditUI
from Db4eOSP2PoolSetupUI.Db4eOSP2PoolSetupUI import Db4eOSP2PoolSetupUI
from Db4eOSMonerodRemoteEditUI.Db4eOSMonerodRemoteEditUI import Db4eOSMonerodRemoteEditUI
from Db4eOSP2PoolEditUI.Db4eOSP2PoolEditUI import Db4eOSP2PoolEditUI
from Db4eOSP2PoolRemoteEditUI.Db4eOSP2PoolRemoteEditUI import Db4eOSP2PoolRemoteEditUI
from Db4eOSXMRigEditUI.Db4eOSXMRigEditUI import Db4eOSXMRigEditUI

# Urwid colors
PALETTE = [
    ('title', 'dark green, bold', ''),
    ('button', 'light cyan', '')
]

# Deployed component status
STATUS = {
    'running'       : '🟢',
    'stopped'       : '🟡',
    'not_installed' : '🔴',
}

bullet = MD['bullet']

WELCOME_MSG = "Welcome to the db4e OS console!\n\n"
WELCOME_MSG += "Use the arrow keys and the spacebar to select a component. "
WELCOME_MSG += "Or use your mouse to select components and to click the "
WELCOME_MSG += "\"More Info\", \"Exit\" or \"New Deployment\" buttons.\n\n"
WELCOME_MSG += "Please be patient: This application can take up to 30 seconds "
WELCOME_MSG += "to refresh. The Monero and P2Pool daemons can also take 30 to "
WELCOME_MSG += "60 seconds to start or stop cleanly."

DB4E_SETUP = "\nThis screen will take you to the initial setup screen. "
DB4E_SETUP += "There are three distinct elements that are configured: "
DB4E_SETUP += "1) Setting the 3rd party software directory and 2) "
DB4E_SETUP += "creating a \"db4e\" group and 3) installing the db4e service.\n\n"
DB4E_SETUP += "The 3rd party software directory is used to store "
DB4E_SETUP += "configuration files, log files, startup scripts and "
DB4E_SETUP += "other runtime artifacts.\n\n"
DB4E_SETUP += "Members of the db4e group will be allowed to interact with the "
DB4E_SETUP += "service using the db4e-os tool.\n\n"
DB4E_SETUP += "The db4e service will start at boot time and is "
DB4E_SETUP += "responsible for managing:\n"
DB4E_SETUP += f"{bullet} The Monero blockchain daemon(s).\n"
DB4E_SETUP += f"{bullet} The P2Pool daemon(s).\n"
DB4E_SETUP += f"{bullet} The XMRig miner(s).\n"
DB4E_SETUP += "You *MUST* have sudo access to the root account "
DB4E_SETUP += "before you can install the db4e service."

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

REPO_SETUP = "This screen will help you setup your GitHub repository. This "
REPO_SETUP += "repo is used by db4e to publish web reports. In order to "
REPO_SETUP += "proceed you must:\n\n"
REPO_SETUP += f"{bullet} Have a GitHub account\n"
REPO_SETUP += f"{bullet} Have created a db4e GitHub repository\n"
REPO_SETUP += f"{bullet} Have configured the GitHub repository\n"
REPO_SETUP += f"{bullet} Have SSH Authentication with GitHub configured"

VENDOR_DIR_SETUP = "3rd Party Software Setup\n\n"
VENDOR_DIR_SETUP += "This screen is used to set the directory where 3rd party "
VENDOR_DIR_SETUP += "configuration files, logs, startup scripts and "
VENDOR_DIR_SETUP += "other 3rd part software artifacts are deployed. "
VENDOR_DIR_SETUP += "You must set this directory before you deploy any local "
VENDOR_DIR_SETUP += "software i.e. a Monero daemon, P2Pool daemon or XMRig."

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
        self.client = Db4eClient()
        self.selected_deployment = 'db4e'
        self.selected_instance = None
        self.deployment_radios = []
        self.right_panel = urwid.LineBox(urwid.Padding(
            urwid.Text(WELCOME_MSG),
            right=2, left=2),
            title='Info', title_align="right", title_attr="title")
        self.results_contents = urwid.Text('')
        
        ## Mini TUIs
        # Setup
        self.install_db4e_service_ui = Db4eOSInstallDb4eServiceUI(self)
        self.initial_setup_ui = Db4eOSInitialSetupUI(self)
        self.repo_setup_ui = Db4eOSRepoSetupUI(self)
        self.monerod_remote_setup_ui = Db4eOSMonerodRemoteSetupUI(self)
        self.p2pool_setup_ui = Db4eOSP2PoolSetupUI(self)
        self.p2pool_remote_setup_ui = Db4eOSP2PoolRemoteSetupUI(self)
        self.xmrig_setup_ui = Db4eOSXMRigSetupUI(self)
        # Edit
        self.edit_db4e_ui = Db4eOSDb4eEditUI(self)
        self.edit_repo_ui = Db4eOSRepoEditUI(self)
        self.edit_monerod_remote_ui = Db4eOSMonerodRemoteEditUI(self)
        self.edit_p2pool_ui = Db4eOSP2PoolEditUI(self)
        self.edit_p2pool_remote_ui = Db4eOSP2PoolRemoteEditUI(self)
        self.edit_xmrig_ui = Db4eOSXMRigEditUI(self)

        self.main_loop = urwid.MainLoop(self.build_main_frame(), PALETTE, unhandled_input=self.exit_on_q)
        self.initialize()

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
        if not self.model.get_deployments_by_component('monerod'):
            # You need to have a Monero daemon deployment before setting up a P2Pool instance.
            text_msg = urwid.Text(P2POOL_PREREQ)
            self.right_panel = urwid.LineBox(text_msg)
            self.main_loop.widget = self.build_main_frame()
            return

        text_msg = urwid.Text(P2POOL_SETUP)
        buttons = urwid.Columns([
            (9, urwid.Button(('button', 'Local'), on_press=self.show_p2pool_setup)),
            (10, urwid.Button(('button', 'Remote'), on_press=self.show_remote_p2pool_setup))
        ], dividechars=2)
        widgets = [text_msg, urwid.Divider(), buttons]
        # Wrap in a ListBox to make scrollable
        listbox = urwid.ListBox(urwid.SimpleFocusListWalker(widgets))
        self.right_panel = urwid.LineBox(
            urwid.Padding(listbox, left=2, right=2),
            title='Info', title_align="right", title_attr="title"
        )
        self.main_loop.widget = self.build_main_frame()
        return
    
    def add_new_xmrig(self, button):
        if not self.model.get_deployments_by_component('p2pool'):
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
        db4e = self.model.get_deployment_by_component('db4e')
        db4e_radio = urwid.RadioButton(group, db4e['name'], on_state_change=self.select_deployment, user_data='db4e', state=('db4e' == self.selected_deployment))
        self.deployment_radios.append(db4e_radio)
        db4e_items.append(urwid.Columns([
            (20, db4e_radio), 
            (3, urwid.Text(('', STATUS[db4e['status']]), wrap='clip'))
        ], dividechars=1))
        
        # repo radiobutton
        repo = self.model.get_deployment_by_component('repo')
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
        all_items.append(self.build_instance_box("Monero Daemon(s)", self.model.get_deployments_by_component('monerod'), group, 'monerod'))
        all_items.append(self.build_instance_box("P2Pool Daemon(s)", self.model.get_deployments_by_component('p2pool'), group, 'p2pool'))
        all_items.append(self.build_instance_box("XMRig Miner(s)", self.model.get_deployments_by_component('xmrig'), group, 'xmrig'))

        return urwid.Pile(all_items)

    def build_instance_box(self, title, instances_list, group, depl_type):
        items = []
        for instance in instances_list:
            instance_name = instance['instance']
            is_selected = (instance_name == self.selected_deployment)
            radio = urwid.RadioButton(
                group,
                instance_name,
                on_state_change=self.select_deployment,
                user_data=depl_type + ':::' + instance_name,
                state=is_selected
            )
            self.deployment_radios.append(radio)
            items.append(urwid.Columns([
                (20, radio),
                (3, urwid.Text(('', STATUS[instance['status']]), wrap='clip'))
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

    def delete_instance(self, button):
        component = self.selected_instance['component']
        instance = self.selected_instance['instance']
        self.model.delete_instance(component, instance)
        self.return_to_main()

    def edit_db4e(self, button):
        self.edit_db4e_ui.reset()
        self.in_mini_tui = True
        self.main_loop.widget = self.edit_db4e_ui.widget()

    def edit_monerod(self, button):
        self.edit_monerod_remote_ui.reset()
        self.edit_monerod_remote_ui.set_instance(self.selected_instance['instance'])
        self.in_mini_tui = True
        self.main_loop.widget = self.edit_monerod_remote_ui.widget()

    def edit_p2pool(self, button):
        if self.model.is_remote('p2pool', self.selected_instance['instance']):
            self.edit_p2pool_remote()
        else:
            self.edit_p2pool_ui.reset()
            self.edit_p2pool_ui.set_instance(self.selected_instance['instance'])
            self.in_mini_tui = True
            self.main_loop.widget = self.edit_p2pool_ui.widget()

    def edit_p2pool_remote(self):
        self.edit_p2pool_remote_ui.reset()
        self.edit_p2pool_remote_ui.set_instance(self.selected_instance['instance'])
        self.in_mini_tui = True
        self.main_loop.widget = self.edit_p2pool_remote_ui.widget()

    def edit_repo(self, button):
        self.edit_repo_ui.reset()
        self.in_mini_tui = True
        self.main_loop.widget = self.edit_repo_ui.widget()

    def edit_xmrig(self, button):
        self.edit_xmrig_ui.reset()
        self.edit_xmrig_ui.set_instance(self.selected_instance['instance'])
        self.in_mini_tui = True
        self.main_loop.widget = self.edit_xmrig_ui.widget()

    def exit_app(self, button):
        raise urwid.ExitMainLoop()
    
    def exit_on_q(self, key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()

    def initialize(self):
        # Check if this is the first time the user ran db4e-os.
        if self.model.first_time():
            self.in_mini_tui = True
            self.main_loop.widget = self.initial_setup_ui.widget()
        else:
            self.in_mini_tui = False
            # Safe to start auto-refresh
            self.main_loop.set_alarm_in(30, self.refresh_tui)

    def install_db4e_service(self, button):
        self.in_mini_tui = True
        self.main_loop.widget = self.install_db4e_service_ui.widget()

    def refresh_tui(self, loop=None, user_data=None):
        # Refresh the TUI
        # Make sure we're not in a mini-TUI (they have a different layout)
        if self.in_mini_tui:
            self.main_loop.set_alarm_in(30, self.refresh_tui)
            return
        try:
            new_left_panel = urwid.Pile([
                self.build_deployments_list(),
                self.build_actions()
            ])
            self.main_loop.widget.base_widget.contents[0] = (new_left_panel, self.main_loop.widget.base_widget.options('given', 30))
        except (AttributeError, TypeError) as e:
            # Another urwid quirk :(
            pass
        self.main_loop.set_alarm_in(30, self.refresh_tui)

    def return_to_main(self):
        self.in_mini_tui = False
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
        div = urwid.Divider()
        self.results_msg = urwid.Text('')
        self.results_box = urwid.Pile([
            urwid.Divider(),
            urwid.LineBox(
                urwid.Padding(
                    self.results_msg,
                    left=2, right=2
                ),
                title='Results', title_align='left', title_attr='title'
            )
        ])
        if deployment == 'db4e':
            title_text = 'db4e Service Status'
            status_info = self.model.get_status('db4e')
            status_list = []
            self.edit_button = urwid.Button(('button', 'Edit'), on_press=self.edit_db4e)
            self.start_button = urwid.Button(('button', 'Start Service'), on_press=self.start_db4e_service)
            self.stop_button = urwid.Button(('button', 'Stop Service'), on_press=self.stop_db4e_service)
            self.install_button = urwid.Button(('button', 'Install Service'), on_press=self.install_db4e_service)
            button_list = [(8, self.edit_button)]
            for aStatus in status_info[1:]:
                status_state = MD[aStatus['state']]
                status_msg = aStatus['msg']
                if status_msg == 'The db4e service is not installed':
                    button_list.append((19, self.install_button))
                elif status_msg == 'The db4e service is stopped':
                    button_list.append((17, self.start_button))
                elif 'The db4e service is running PID' in status_msg:
                    button_list.append((16, self.stop_button))
                status_list.append(urwid.Text(f'{status_state}  {status_msg}'))
            status = urwid.Pile(status_list)
            self.form_buttons = urwid.Columns(button_list, dividechars=1)
            listbox = urwid.ListBox(urwid.SimpleFocusListWalker([
                div, status, div, self.form_buttons, div, self.results_box]))
            self.right_panel = urwid.LineBox(
                urwid.Padding(listbox, left=2, right=2),
                title=title_text, title_align='left', title_attr='title'
            )
            self.main_loop.widget = self.build_main_frame()
            return

        elif deployment == 'repo':
            title_text = 'Website Repository Status'
            repo = self.model.get_deployment_by_component('repo')
            if not repo:
                text_msg = urwid.Text(REPO_SETUP)
                continue_button = urwid.Columns([
                    (12, urwid.Button(('button', 'Continue'), on_press=self.show_repo_setup))
                ])
                widgets = [div, text_msg, div, continue_button]
                # Wrap in a ListBox to make scrollable
                listbox = urwid.ListBox(urwid.SimpleFocusListWalker(widgets))
                self.right_panel = urwid.LineBox(
                    urwid.Padding(listbox, left=2, right=2),
                    title=title_text, title_align='left', title_attr='title'
                )
                self.main_loop.widget = self.build_main_frame()
                return
            
            else:
                status_info = self.model.get_status('repo')
                status_list = []
                for aStatus in status_info[1:]:
                    status_state = MD[aStatus['state']]
                    status_msg = aStatus['msg']
                    status_list.append(urwid.Text(f'{status_state}  {status_msg}'))
                status = urwid.Pile(status_list)
                buttons = urwid.Columns([
                    (8, urwid.Button(('button', 'Edit'), on_press=self.edit_repo)), 
                ], dividechars=1)
                listbox = urwid.ListBox(urwid.SimpleFocusListWalker([
                    div, status, div, buttons]))
                self.right_panel = urwid.LineBox(
                    urwid.Padding(listbox, left=2, right=2),
                    title=title_text, title_align='left', title_attr='title'
                )
                self.main_loop.widget = self.build_main_frame()
                return

        else:
            # Unlike the 'db4e' and 'repo' records, the 'monerod', 'p2opool' and 'xmrig' 
            # deployment records can have multiple instances...
            depl_type = deployment.split(':::')[0]
            instance = deployment.split(':::')[1]
            self.selected_instance = { 'component': depl_type, 'instance': instance }

            if depl_type == 'monerod':
                title_text = f'Monero Daemon ({instance}) Status'
                status_info = self.model.get_status('monerod', instance)
                status_list = []
                for aStatus in status_info[1:]:
                    status_state = MD[aStatus['state']]
                    status_msg = aStatus['msg']
                    status_list.append(urwid.Text(f'{status_state}  {status_msg}'))
                status = urwid.Pile(status_list)
                buttons = urwid.Columns([
                    (10, urwid.Button(('button', 'Delete'), on_press=self.delete_instance)),
                    (8, urwid.Button(('button', 'Edit'), on_press=self.edit_monerod)), 
                ], dividechars=1)
                listbox = urwid.ListBox(urwid.SimpleFocusListWalker([
                    div, status, div, buttons]))
                self.right_panel = urwid.LineBox(
                    urwid.Padding(listbox, left=2, right=2),
                    title=title_text, title_align='left', title_attr='title'
                )
                self.main_loop.widget = self.build_main_frame()
                return

            elif depl_type == 'p2pool':
                title_text = f'P2Pool Daemon ({instance}) Status'
                status_info = self.model.get_status('p2pool', instance)
                status_list = []
                self.edit_button = urwid.Button(('button', 'Edit'), on_press=self.edit_p2pool)
                self.stop_button = urwid.Button(('button', 'Stop Service'), on_press=self.stop_instance)
                self.start_button = urwid.Button(('button', 'Start Service'), on_press=self.start_instance)
                self.delete_button = urwid.Button(('button', 'Delete'), on_press=self.delete_instance)
                button_list = [(8, self.edit_button)]
                for aStatus in status_info[1:]:
                    status_state = MD[aStatus['state']]
                    status_msg = aStatus['msg']
                    if status_msg == f'The p2pool@' + instance + ' service is stopped':
                        button_list.append((17, self.start_button))
                    if f'The p2pool@' + instance + ' service is running PID' in status_msg:
                        button_list.append((16, self.stop_button))
                    status_list.append(urwid.Text(f'{status_state}  {status_msg}'))
                status = urwid.Pile(status_list)
                if status_info[0]['state'] == 'good':
                    buttons = urwid.Columns([
                        (8, self.stop_button),
                    ], dividechars=1)
                else:
                    buttons = urwid.Columns([
                        (9, self.start_button),
                    ], dividechars=1)
                button_list.append((10, self.delete_button))
                self.form_buttons = urwid.Columns(button_list, dividechars=1)
                listbox = urwid.ListBox(urwid.SimpleFocusListWalker([
                    div, status, div, self.form_buttons, div, self.results_box]))
                self.right_panel = urwid.LineBox(
                    urwid.Padding(listbox, left=2, right=2),
                    title=title_text, title_align='left', title_attr='title'
                )
                self.main_loop.widget = self.build_main_frame()
                return

            elif depl_type == 'xmrig':
                title_text = f'XMRig Miner ({instance}) Status'
                status_info = self.model.get_status('xmrig', instance)
                status_list = []
                for aStatus in status_info[1:]:
                    status_state = MD[aStatus['state']]
                    status_msg = aStatus['msg']
                    status_list.append(urwid.Text(f'{status_state}  {status_msg}'))
                status = urwid.Pile(status_list)
                buttons = urwid.Columns([
                    (10, urwid.Button(('button', 'Delete'), on_press=self.delete_instance)),
                    (8, urwid.Button(('button', 'Edit'), on_press=self.edit_xmrig)), 
                ], dividechars=1)
                listbox = urwid.ListBox(urwid.SimpleFocusListWalker([
                    div, status, div, buttons]))
                self.right_panel = urwid.LineBox(
                    urwid.Padding(listbox, left=2, right=2),
                    title=title_text, title_align='left', title_attr='title'
                )
                self.main_loop.widget = self.build_main_frame()
                return
            
            else:
                self.right_panel = urwid.LineBox(
                    urwid.Padding(urwid.Text(f'No info available for {deployment}.'), left=2, right=2),
                    title='INFO', title_align='right', title_attr='title'
                )
                self.main_loop.widget = self.build_main_frame()

    def show_db4e_setup(self, button):
        self.in_mini_tui = True
        self.main_loop.widget = self.db4e_setup_ui.widget()

    def show_monerod_setup(self, button):
        # TODO
        pass

    def show_remote_monerod_setup(self, button):
        self.monerod_remote_setup_ui.reset()
        self.in_mini_tui = True
        self.main_loop.widget = self.monerod_remote_setup_ui.widget()

    def show_p2pool_setup(self, button):
        # Check db4e has been setup (we need the vendor_dir for P2pool deployments)
        if not self.model.get_dir('vendor'):
            self.in_mini_tui = True
            self.main_loop.widget = self.initial_setup_ui.widget()
        else:
            self.p2pool_setup_ui.reset()
            self.in_mini_tui = True
            self.main_loop.widget = self.p2pool_setup_ui.widget()

    def show_remote_p2pool_setup(self, button):
        self.p2pool_remote_setup_ui.reset()
        self.in_mini_tui = True
        self.main_loop.widget = self.p2pool_remote_setup_ui.widget()

    def show_repo_setup(self, button):
        self.in_mini_tui = True
        self.main_loop.widget = self.repo_setup_ui.widget()

    def show_xmrig_setup(self, button):
        # Check that db4e has been setup (we need the vendor_dir for XMRig deployments)
        if not self.model.get_dir('vendor'):
            self.in_mini_tui = True
            self.main_loop.widget = self.initial_setup_ui.widget()
        else:
            self.xmrig_setup_ui.reset()
            self.in_mini_tui = True
            self.main_loop.widget = self.xmrig_setup_ui.widget()

    def start_db4e_service(self, button):
        warning = MD['warning']
        good = MD['good']
        result = self.model.start_db4e_service()
        if 'error' in result:
            server_msg = result['msg']
            self.results_msg.set_text(f'{warning} {server_msg}')
        else:
            server_msg = result['msg']
            self.results_msg.set_text(f'{good} {server_msg}')
            self.form_buttons.contents = [
                (self.edit_button, self.form_buttons.options('given', 8)),
                (self.stop_button, self.form_buttons.options('given', 16))
            ]

    def start_instance(self, button):
        component = self.selected_instance['component']
        instance = self.selected_instance['instance']
        self.model.enable_instance(component, instance)
        self.results_msg.set_text(f'The {component} instance {instance} has been scheduled for immediate startup')

    def stop_db4e_service(self, button):
        warning = MD['warning']
        good = MD['good']
        result = self.model.stop_db4e_service()
        if 'error' in result:
            server_msg = result['msg']
            self.results_msg.set_text(f'{warning} {server_msg}')
        else:
            server_msg = result['msg']
            self.results_msg.set_text(f'{good} {server_msg}')
            self.form_buttons.contents = [
                (self.edit_button, self.form_buttons.options('given', 8)),
                (self.start_button, self.form_buttons.options('given', 17))
            ]

    def stop_instance(self, button):
        component = self.selected_instance['component']
        instance = self.selected_instance['instance']
        self.model.disable_instance(component, instance)
        self.results_msg.set_text(f'The {component} instance {instance} has been scheduled for immediate shutdown')

    def run(self):
        try:
            self.main_loop.run()
        except KeyboardInterrupt:
            print('Exiting...')
            sys.exit(0)

