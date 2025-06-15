"""
lib/Infrastructure/Db4eOSP2PoolRemoteSetupUI/Db4eOSP2PoolRemoteSetupUI.py

This urwid based TUI drops into the db4e-os.py TUI to help the
user configure access to a P2Pool daemon running on a remote node.
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

# Supporting modules
import os, sys
import urwid
import subprocess
import shutil

# Where the DB4E modules live
lib_dir = os.path.dirname(__file__) + "/../../"
# Import DB4E modules
db4e_dirs = [
    lib_dir + 'Infrastructure',
    lib_dir + 'Mining'
]
for db4e_dir in db4e_dirs:
    sys.path.append(db4e_dir)

from Db4eOS.Db4eOS import Db4eOS
from Db4eOSDb.Db4eOSDb import Db4eOSDb

class Db4eOSP2PoolRemoteSetupUI:
    def __init__(self, parent_tui):
        self.parent_tui = parent_tui
        self._os = Db4eOS()
        self._db = Db4eOSDb()
        p2pool_rec = self._db.get_tmpl('p2pool', 'remote')
        self.selected_monerod = None
        self.deployment_radios = []
        self.group = []
        monerod_deployments = {}
        for deployment in self._db.get_monerod_deployments():
            name = deployment['name']
            instance = deployment['instance']
            monerod_deployments[instance] = { 'name': name, 'instance': instance }
            self.selected_monerod = instance # Initialize to the last instance
        instance = p2pool_rec['instance'] or ''
        ip_addr = p2pool_rec['ip_addr'] or ''
        stratum_port = p2pool_rec['stratum_port'] or ''
        self.instance_edit = urwid.Edit("P2Pool instance name (e.g. Primary): ", edit_text=instance)
        self.ip_addr_edit = urwid.Edit("Remote P2Pool hostname or IP address: ", edit_text=ip_addr)
        self.stratum_port_edit = urwid.Edit("Stratum port: ", edit_text=str(stratum_port))
        self.info_msg = urwid.Text('')
        self.info_text = urwid.Pile([
                urwid.Divider(),
                urwid.LineBox(
                    urwid.Padding(
                        self.info_msg,
                        left=2, right=2
                    ),
                    title="Results", title_align='left', title_attr='title'
                )
        ])

        form_widgets = [
            urwid.Text('Remote P2Pool Demon Setup\n\n' +
                'The \"instance name\" must be unique within the ' +
                'db4e environment i.e. if you have more than one ' +
                'daemon deployed, then each must have their own ' +
                'instance name.\n\nUse the arrow keys or mouse scrollwheel ' +
                'to scroll up and down.'),
            urwid.Divider(),
            urwid.LineBox(
                urwid.Padding(
                    urwid.Pile([
                        self.instance_edit,
                        self.ip_addr_edit,
                        self.stratum_port_edit,
                        # Not used for remote deployments
                        #self.build_monerod_deployments(monerod_deployments),
                        urwid.Divider(),
                        urwid.Columns([
                            (10, urwid.Button(('button', 'Submit'), on_press=self.on_submit)),
                            (8, urwid.Button(('button', 'Back'), on_press=self.back_to_main))
                        ], dividechars=1)
                    ]), left=2, right=2),
                title='Setup Form', title_align='left', title_attr='title'
            ),
            self.info_text
        ]

        # Wrap in a ListBox to make scrollable
        listbox = urwid.ListBox(urwid.SimpleFocusListWalker(form_widgets))
        self.frame = urwid.LineBox(
            urwid.Padding(listbox, left=2, right=2),
            title="Remote P2Pool Daemon Setup", title_align="center", title_attr="title"
        )

    def back_to_main(self, button):
        self.parent_tui.return_to_main()

    def build_monerod_deployments(self, deployments):
        items = []
        for instance_name, data in sorted(deployments.items()):
            is_selected = (instance_name == self.selected_monerod)
            radio = urwid.RadioButton(
                self.group,
                data['instance'],
                on_state_change=self.select_monerod,
                user_data=instance_name,
                state=is_selected
            )
            self.deployment_radios.append(radio)
            items.append(urwid.Columns([
                (20, radio)
            ], dividechars=1))
        return urwid.LineBox(urwid.Padding(urwid.Pile(items), left=2, right=2), title='Select Monero daemon', title_align='left', title_attr='title')

    def on_submit(self, button):
        instance = self.instance_edit.edit_text.strip()
        ip_addr = self.ip_addr_edit.edit_text.strip()
        stratum_port = self.stratum_port_edit.edit_text.strip()

        # Validate input
        results = ''
        if not instance:
            self.info_msg.set_text("Please fill enter a unique instance name.")
            return
        # Check that db4e can connect to the remote system
        if self._os.is_port_open(ip_addr, int(stratum_port)):
            results += f'* Connected to P2Pool\'s stratum port ({stratum_port}) on  ({ip_addr})\n'
        else:
            results += f'* WARNING: Unable to connected to P2Pool\'s stratum port ({stratum_port}) on  ({ip_addr})\n'

        # TODO check that the instance name is unique
        monerod_rec = self._db.get_deployment_by_instance('monerod', self.selected_monerod)
        self._db.new_deployment('p2pool', { 
            'status': 'running',
            'component': 'p2pool',
            'instance': instance,
            'ip_addr': ip_addr,
            'stratum_port': int(stratum_port),
            'monerod_id': monerod_rec['_id'],
            'doc_type': 'template',
            'remote': True
            })
        results += f'\nCreated new P2Pool daemon ({instance}) deployment record. '
        self.info_msg.set_text(results)

    def select_monerod(self, radio, new_state, deployment):
        if new_state:
            self.selected_monerod = deployment

    def widget(self):
        return self.frame
