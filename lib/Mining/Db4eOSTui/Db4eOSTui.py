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
## Mini TUIs
# Setup new component
from Db4eOSDb4eSetupUI.Db4eOSDb4eSetupUI import Db4eOSDb4eSetupUI
from Db4eOSRepoSetupUI.Db4eOSRepoSetupUI import Db4eOSRepoSetupUI
from Db4eOSMonerodRemoteSetupUI.Db4eOSMonerodRemoteSetupUI import Db4eOSMonerodRemoteSetupUI
from Db4eOSP2PoolSetupUI.Db4eOSP2PoolSetupUI import Db4eOSP2PoolSetupUI
from Db4eOSP2PoolRemoteSetupUI.Db4eOSP2PoolRemoteSetupUI import Db4eOSP2PoolRemoteSetupUI
from Db4eOSXMRigSetupUI.Db4eOSXMRigSetupUI import Db4eOSXMRigSetupUI
# Edit component
from Db4eOSRepoEditUI.Db4eOSRepoEditUI import Db4eOSRepoEditUI
from Db4eOSP2PoolSetupUI.Db4eOSP2PoolSetupUI import Db4eOSP2PoolSetupUI
from Db4eOSMonerodRemoteEditUI.Db4eOSMonerodRemoteEditUI import Db4eOSMonerodRemoteEditUI
from Db4eOSP2PoolEditUI.Db4eOSP2PoolEditUI import Db4eOSP2PoolEditUI
from Db4eOSP2PoolRemoteEditUI.Db4eOSP2PoolRemoteEditUI import Db4eOSP2PoolRemoteEditUI
from Db4eOSXMRigEditUI.Db4eOSXMRigEditUI import Db4eOSXMRigEditUI

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
    'warning'       : '⚠️',
    'unknown'       : '❔'
}

MD = {
    'bullet': '🔸',
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

REPO_SETUP = "This screen will help you setup your GitHub repository. This "
REPO_SETUP += "repo is used by db4e to publish web reports. In order to "
REPO_SETUP += "proceed you *must*:\n\n"
REPO_SETUP += f"{MD['bullet']} Have a GitHub account\n"
REPO_SETUP += f"{MD['bullet']} Have created a db4e GitHub repository\n"
REPO_SETUP += f"{MD['bullet']} Have configured the GitHub repository\n"
REPO_SETUP += f"{MD['bullet']} Have SSH Authentication with GitHub configured\n\n"
REPO_SETUP += "The command \"ssh -T git@github.com\" needs to work. "
REPO_SETUP += "You *MUST* have this configured before you can proceeed. "
REPO_SETUP += "Refer to the \"Getting Started\" page "
REPO_SETUP += "(https://db4e.osoyalce.com/pages/Getting-Started.html) for "
REPO_SETUP += "detailed information on setting this up."


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
        self.selected_instance = None
        self.deployment_radios = []
        self.right_panel = urwid.LineBox(urwid.Padding(
            urwid.Text(WELCOME_MSG),
            right=2, left=2),
            title='Info', title_align="right", title_attr="title")
        self.results_contents = urwid.Text('')
        
        ## Mini TUIs
        # Setup
        self.repo_setup_ui = Db4eOSRepoSetupUI(self)
        self.db4e_setup_ui = Db4eOSDb4eSetupUI(self)
        self.monerod_remote_setup_ui = Db4eOSMonerodRemoteSetupUI(self)
        self.p2pool_setup_ui = Db4eOSP2PoolSetupUI(self)
        self.p2pool_remote_setup_ui = Db4eOSP2PoolRemoteSetupUI(self)
        self.xmrig_setup_ui = Db4eOSXMRigSetupUI(self)
        # Edit
        self.edit_repo_ui = Db4eOSRepoEditUI(self)
        self.edit_monerod_ui = Db4eOSMonerodRemoteEditUI(self)
        self.edit_p2pool_ui = Db4eOSP2PoolEditUI(self)
        self.edit_p2pool_remote_ui = Db4eOSP2PoolRemoteEditUI(self)
        self.edit_xmrig_ui = Db4eOSXMRigEditUI(self)

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
        all_items.append(self.build_instance_box("P2Pool Daemon(s)", self.model.get_p2pool_deployments(), group, 'p2pool'))
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

    def delete_instance(self, button):
        component = self.selected_instance['component']
        instance = self.selected_instance['instance']
        self.model.delete_instance(component, instance)
        self.return_to_main()

    def edit_monerod(self, button):
        self.edit_monerod_ui.set_instance(self.selected_instance['instance'])
        self.main_loop.widget = self.edit_monerod_ui.widget()

    def edit_p2pool(self, button):
        self.edit_p2pool_ui.set_instance(self.selected_instance['instance'])
        self.main_loop.widget = self.edit_p2pool_ui.widget()

    def edit_p2pool_remote(self, button):
        self.edit_p2pool_remote_ui.set_instance(self.selected_instance['instance'])
        self.main_loop.widget = self.edit_p2pool_remote_ui.widget()

    def edit_repo(self, button):
        self.main_loop.widget = self.edit_repo_ui.widget()

    def edit_xmrig(self, button):
        self.edit_xmrig_ui.set_instance(self.selected_instance['instance'])
        self.main_loop.widget = self.edit_xmrig_ui.widget()

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
        # Fancy unicode
        bullet = MD['bullet']
        warning = STATUS['warning']
        # uwid divider
        div = urwid.Divider()

        if deployment == 'db4e':
            title_text = 'db4e Service Status'
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
                    title=title_text, title_align='left', title_attr='title'
                )
                self.main_loop.widget = self.build_main_frame()
                return
            
            elif db4e['status'] == 'running':
                status = self.model.get_db4e_status()
                status_msg = urwid.Text(bullet + status['service_installed'] )
                enabled_msg = urwid.Text(bullet + status['service_enabled'] )
                running_msg = urwid.Text(bullet + status['service_running'] )
                listbox = urwid.ListBox(urwid.SimpleFocusListWalker([
                    div, status_msg, enabled_msg, running_msg]))
                self.right_panel = urwid.LineBox(
                    urwid.Padding(listbox, left=2, right=2),
                    title=title_text, title_align='left', title_attr='title'
                )
                self.main_loop.widget = self.build_main_frame()
                return


        elif deployment == 'repo':
            title_text = 'Website Repository Status'
            repo = self.model.get_repo_deployment()
            if repo['status'] == 'not_installed':
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
            
            elif repo['status'] == 'running':
                repo_dir = self.model.get_repo_dir()
                status1 = urwid.Text(f'{bullet} Repo is properly configured')
                status2 = urwid.Text(f'{bullet} Repo is in directory ({repo_dir})')
                status_msg = urwid.Pile([ status1, status2 ])
                edit_button = urwid.Columns([
                    (8, urwid.Button(('button', 'Edit'), on_press=self.edit_repo))
                ])
                listbox = urwid.ListBox(urwid.SimpleFocusListWalker([
                    div, status_msg, div, edit_button]))
                self.right_panel = urwid.LineBox(
                    urwid.Padding(listbox, left=2, right=2),
                    title=title_text, title_align='left', title_attr='title'
                )
                self.main_loop.widget = self.build_main_frame()
                return

        else:
            # Unlike 'db4e' and 'repo' the 'monerod', 'p2opool' and 'xmrig' 
            # deployments have multiple instances...
            depl_type = deployment.split(':')[0]
            instance = deployment.split(':')[1]
            self.selected_instance = { 'component': depl_type, 'instance': instance }

            if depl_type == 'monerod':
                depl = self.model.get_monerod_deployment(instance)
                ip_addr = depl['ip_addr']
                remote_flag = depl['remote']
                if remote_flag:
                    remote = 'Remote'
                else:
                    remote = 'Local'
                rpc_bind_port = depl['rpc_bind_port']
                zmq_pub_port = depl['zmq_pub_port']
                updated = depl['updated'].strftime("%Y-%m-%d %H:%M:%S")
                header_msg = urwid.Text(f'Monero Blockchain Daemon - {instance}\n')
                status = f'{bullet} Hostname or IP address: {ip_addr}\n'
                status += f'{bullet} Local or remote: {remote}\n'
                status += f'{bullet} RPC bind port: {rpc_bind_port}\n'
                status += f'{bullet} ZMQ pub port: {zmq_pub_port}\n'
                status += f'{bullet} Updated: {updated}\n'
                status_msg = urwid.Text(status)
                buttons = urwid.Columns([
                    (8, urwid.Button(('button', 'Edit'), on_press=self.edit_monerod)), 
                    (19, urwid.Button(('button', 'Delete Instance'), on_press=self.delete_instance))
                ], dividechars=1)
                listbox = urwid.ListBox(urwid.SimpleFocusListWalker([
                header_msg, status_msg, div, buttons]))
                self.right_panel = urwid.LineBox(
                    urwid.Padding(listbox, left=2, right=2),
                    title='Info', title_align="right", title_attr="title"
                )
                self.main_loop.widget = self.build_main_frame()
                return

            elif depl_type == 'p2pool':
                depl = self.model.get_p2pool_deployment(instance)
                remote_flag = depl['remote']
                if remote_flag:
                    remote = 'Remote'
                    ip_addr = depl['ip_addr']
                    stratum_port = depl['stratum_port']
                    updated = depl['updated'].strftime("%Y-%m-%d %H:%M:%S")
                    header_msg = urwid.Text(f'Remote P2Pool Daemon - {instance}\n')
                    status = f'{bullet} Hostname or IP address: {ip_addr}\n'
                    status += f'{bullet} Local or remote: {remote}\n'
                    status += f'{bullet} Stratum port: {stratum_port}\n'
                    status += f'{bullet} Updated: {updated}'
                    status_msg = urwid.Text(status)
                    problems_list = []
                    for problem in self.model.get_problems(depl_type, instance):
                        problems_list.append(urwid.Text(f'{warning}  {problem}\n'))
                    if problems_list:
                        problems_list.append(div)
                    problems = urwid.Pile(problems_list)
                    delete_button = urwid.Columns([
                        (8, urwid.Button(('button', 'Edit'), on_press=self.edit_p2pool_remote)),
                        (19, urwid.Button(('button', 'Delete Instance'), on_press=self.delete_instance))
                    ])
                    listbox = urwid.ListBox(urwid.SimpleFocusListWalker([
                    header_msg, status_msg, div, problems, delete_button]))
                    self.right_panel = urwid.LineBox(
                        urwid.Padding(listbox, left=2, right=2),
                        title='Info', title_align="right", title_attr="title"
                    )
                    self.main_loop.widget = self.build_main_frame()
                    return

                # Local P2Pool deployment
                remote = 'Local'
                wallet = depl['wallet']
                any_ip = depl['any_ip']
                stratum_port = depl['stratum_port']
                p2p_port = depl['p2p_port']
                log_level = depl['log_level']
                in_peers = depl['in_peers']
                out_peers = depl['out_peers']
                updated = depl['updated'].strftime("%Y-%m-%d %H:%M:%S")
                header_msg = urwid.Text(f'Local P2Pool Daemon - {instance}\n')
                status = f'{bullet} Your Monero wallet: {wallet}\n'
                status += f'{bullet} Local or remote: {remote}\n'
                status += f'{bullet} Listen on IP address: {any_ip}\n'
                status += f'{bullet} Stratum port: {stratum_port}\n'
                status += f'{bullet} P2P port: {p2p_port}\n'
                status += f'{bullet} Log level: {log_level}\n'
                status += f'{bullet} Number of allowed incoming connections: {in_peers}\n'
                status += f'{bullet} Number of allowed outbound connections: {out_peers}\n'
                status += f'{bullet} Updated: {updated}'
                status_msg = urwid.Text(status)
                problems_list = []
                for problem in self.model.get_problems(depl_type, instance):
                    problems_list.append(urwid.Text(f'{warning}  {problem}\n'))
                if problems_list:
                    problems_list.append(div)
                problems = urwid.Pile(problems_list)
                delete_button = urwid.Columns([
                    (8, urwid.Button(('button', 'Edit'), on_press=self.edit_p2pool)),
                    (19, urwid.Button(('button', 'Delete Instance'), on_press=self.delete_instance))
                ])
                listbox = urwid.ListBox(urwid.SimpleFocusListWalker([
                header_msg, status_msg, div, problems, delete_button]))
                self.right_panel = urwid.LineBox(
                    urwid.Padding(listbox, left=2, right=2),
                    title='Info', title_align="right", title_attr="title"
                )
                self.main_loop.widget = self.build_main_frame()
                return


            elif depl_type == 'xmrig':
                depl = self.model.get_xmrig_deployment(instance)
                config = depl['config']
                num_threads = depl['num_threads']
                updated = depl['updated'].strftime("%Y-%m-%d %H:%M:%S")
                p2pool_id = depl['p2pool_id']
                p2pool_rec = self.model.get_p2pool_deployment_by_id(p2pool_id)
                p2pool_name = p2pool_rec['instance']

                header_msg = urwid.Text(f'XMRig Miner - {instance}\n')
                status = f'{bullet} CPU threads: {num_threads}\n'
                status += f'{bullet} Configuration file: {config}\n'
                status += f'{bullet} P2Pool daemon: {p2pool_name}\n'
                status += f'{bullet} Updated: {updated}'
                status_msg = urwid.Text(status)
                problems_list = []
                for problem in self.model.get_problems(depl_type, instance):
                    problems_list.append(urwid.Text(f'{warning}  {problem}\n'))
                if problems_list:
                    problems_list.append(div)
                problems = urwid.Pile(problems_list)
                buttons = urwid.Columns([
                    (8, urwid.Button(('button', 'Edit'), on_press=self.edit_xmrig)),
                    (19, urwid.Button(('button', 'Delete Instance'), on_press=self.delete_instance))
                ])
                listbox = urwid.ListBox(urwid.SimpleFocusListWalker([
                header_msg, status_msg, div, problems, buttons]))
                self.right_panel = urwid.LineBox(
                    urwid.Padding(listbox, left=2, right=2),
                    title='Info', title_align="right", title_attr="title"
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
        self.main_loop.widget = self.db4e_setup_ui.widget()

    def show_monerod_setup(self, button):
        pass

    def show_remote_monerod_setup(self, button):
        self.main_loop.widget = self.monerod_remote_setup_ui.widget()

    def show_p2pool_setup(self, button):
        self.main_loop.widget = self.p2pool_setup_ui.widget()

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

