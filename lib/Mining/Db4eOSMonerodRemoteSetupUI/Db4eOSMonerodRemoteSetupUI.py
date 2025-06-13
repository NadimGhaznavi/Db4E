"""
lib/Infrastructure/Db4eOSMonerodRemoteSetupUI/Db4eOSMonerodRemoteSetupUI.py

This urwid based TUI drops into the db4e-os.py TUI to help the
user configure access to a Monero blockchain daemon running on a
remote node.
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

class Db4eOSMonerodRemoteSetupUI:
    def __init__(self, parent_tui):
        self.parent_tui = parent_tui
        self._os = Db4eOS()
        self._db = Db4eOSDb()
        monerod_rec = self._db.get_monerod_tmpl()
        instance = monerod_rec['instance'] or ''
        ip_addr = monerod_rec['ip_addr'] or ''
        zmq_port = monerod_rec['zmq_pub_port'] or ''
        rpc_port = monerod_rec['rpc_bind_port'] or ''
        self.instance_edit = urwid.Edit("Monero instance name: ", edit_text=instance)
        self.ip_addr_edit = urwid.Edit("Remote node IP addrss: ", edit_text=ip_addr)
        self.zmq_port_edit = urwid.Edit("ZMQ port: ", edit_text=str(zmq_port))
        self.rpc_port_edit = urwid.Edit("RPC port: ", edit_text=str(rpc_port))
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
            urwid.Text('Remote Monero Blockchain Daemon Setup\n\n' +
                'All of the fields below are mandatory. Furthermore ' +
                'the \"instance name\" must be unique within the ' +
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
                        self.zmq_port_edit,
                        self.rpc_port_edit,
                        urwid.Divider(),
                        urwid.Columns([
                            ('pack', urwid.Button(('button', 'Submit'), on_press=self.on_submit)),
                            ('pack', urwid.Button(('button', 'Back'), on_press=self.back_to_main))
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
            title="GitHub Repo Setup", title_align="center", title_attr="title"
        )

    def back_to_main(self, button):
        self.parent_tui.return_to_main()

    def on_submit(self, button):
        instance = self.instance_edit.edit_text.strip()
        ip_addr = self.ip_addr_edit.edit_text.strip()
        zmq_port = self.zmq_port_edit.edit_text.strip()
        rpc_port = self.zmq_port_edit.edit_text.strip()

        # Validate input
        if not instance or not ip_addr or not zmq_port or not rpc_port:
            self.info_msg.set_text("Please fill in *all* of the fields.")
            return
        # TODO Put this in a try/except block
        zmq_port = int(zmq_port)
        rpc_port = int(rpc_port)

        # Cannot connect warnings
        results = 'Checklist:\n\n'
        # Check that db4e can connect to the remote system
        if not self._os.is_port_open(ip_addr, zmq_port):
            results += f'* Connected to ZMQ port ({zmq_port}) on remote machine ({ip_addr})\n'
        else:
            results += f"* WARNING: Unable to connect to ZMQ port ({zmq_port}) on remote machine ({ip_addr})\n"

        if not self._os.is_port_open(ip_addr, rpc_port):
            results += f'* Connected to RPC port ({rpc_port}) on remote machine ({ip_addr})\n'
        else:
            results += f"* WARNING: Unable to connect to RPC port ({rpc_port}) on remote machine ({ip_addr})\n"

        self._db.update_deployment('monerod', { 
            'status': 'running',
            'component': 'monerod',
            'instance': instance,
            'doc_type': 'template'
            }, instance)
        results += f'\nCreated new Monero daemon ({instance}) deployment record. '
        self.info_msg.set_text(results)

    def widget(self):
        return self.frame
