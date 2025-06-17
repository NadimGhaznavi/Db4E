"""
lib/Infrastructure/Db4eOSMonerodRemoteEditUI/Db4eOSMonerodEditSetupUI.py

This urwid based TUI drops into the db4e-os.py TUI to help the
user re-configure access to a Monero blockchain daemon running on a
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

# TODO Put into a strings class
MD = {
    'bullet'  : '🔸',
    'warning' : '⚠️',
}

class Db4eOSMonerodRemoteEditUI:
    def __init__(self, parent_tui):
        self.parent_tui = parent_tui
        self._os = Db4eOS()
        self._db = Db4eOSDb()
        # Most of the initialization is done in set_instance()

    def back_to_main(self, button):
        self.parent_tui.return_to_main()

    def on_submit(self, button):
        instance = self.instance_edit.edit_text.strip()
        ip_addr = self.ip_addr_edit.edit_text.strip()
        zmq_port = self.zmq_port_edit.edit_text.strip()
        rpc_port = self.zmq_port_edit.edit_text.strip()
        # Unicode
        bullet = MD['bullet']
        warning = MD['warning']

        # Validate input
        if any(not val for val in (instance, ip_addr, zmq_port, rpc_port)):
            self.results_msg.set_text("You must fill in *all* of the fields.")
            return
        
        try:
            zmq_port = int(zmq_port)
            rpc_port = int(rpc_port)
        except:
            self.results_msg.set_text("The ZMQ and RPC ports must be integer values")
            return

        if self._db.get_deployment_by_instance('monerod', instance):
            self.results_msg.set_text(f"The instance name ({instance}) is already being used. " +
                                      "There can be only one Monero daemon deployment with that " +
                                      "instance name.")
            return

        # Check connectivity
        results = 'Checklist:\n'
        # Check that db4e can connect to the remote system
        if self._os.is_port_open(ip_addr, zmq_port):
            results += f'{bullet} Connected to ZMQ port ({zmq_port}) on remote machine ({ip_addr})\n'
        else:
            results += f"{warning} Unable to connect to ZMQ port ({zmq_port}) on remote machine ({ip_addr})\n"

        if self._os.is_port_open(ip_addr, rpc_port):
            results += f'{bullet} Connected to RPC port ({rpc_port}) on remote machine ({ip_addr})\n'
        else:
            results += f"{warning} Unable to connect to RPC port ({rpc_port}) on remote machine ({ip_addr})\n"

        
        # Update the deployment record
        self._db.update_deployment('monerod', { 
            'status': 'running',
            'instance': instance,
            'zmq_pub_port': zmq_port,
            'rpc_bind_port': rpc_port,
            'ip_addr': ip_addr,
            'remote': True
            })
        
        # Set the results
        results += f'\nRe-configured the Monero daemon ({instance}) deployment record. '
        self.results_msg.set_text(results)

        # Remove the submit button
        self.back_button.set_label("Done")
        self.form_buttons.set_focus(0)
        self.form_buttons.contents = [
            (self.back_button, self.form_buttons.options('given', 8))
        ]

    def set_instance(self, instance):
        self._instance = instance
        monerod_rec = self._db.get_deployment_by_instance('monerod', self._instance)
        zmq_port = monerod_rec['zmq_pub_port'] or ''
        rpc_port = monerod_rec['rpc_bind_port'] or ''
        ip_addr = monerod_rec['ip_addr'] or ''

        # Form elements; edit widgets
        self.instance_edit = urwid.Edit("Monero instance name (e.g. Primary): ", edit_text=instance)
        self.ip_addr_edit = urwid.Edit("Remote node hostname or IP address: ", edit_text=ip_addr)
        self.zmq_port_edit = urwid.Edit("ZMQ port: ", edit_text=str(zmq_port))
        self.rpc_port_edit = urwid.Edit("RPC port: ", edit_text=str(rpc_port))

        # The buttons
        self.update_button = urwid.Button(('button', 'Update'), on_press=self.on_submit)
        self.back_button = urwid.Button(('button', 'Back'), on_press=self.back_to_main)

        # The assembled buttons
        self.form_buttons = urwid.Columns([
            (10, self.update_button),
            (8, self.back_button)
        ], dividechars=1)

        # The assembled form elements and buttons
        self.form_box = urwid.Pile([
            self.instance_edit,
            self.ip_addr_edit,
            self.zmq_port_edit,
            self.rpc_port_edit,
            urwid.Divider(),
            self.form_buttons
        ])

        # Results
        self.results_msg = urwid.Text('')

        # Assembled results
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
                urwid.Padding(self.form_box, left=2, right=2),
                title='Setup Form', title_align='left', title_attr='title'),
            self.results_box
        ]

        # Wrap in a ListBox to make scrollable
        listbox = urwid.ListBox(urwid.SimpleFocusListWalker(form_widgets))
        self.frame = urwid.LineBox(
            urwid.Padding(listbox, left=2, right=2),
            title='Remote Monero Daemon Setup', title_align='center', title_attr='title'
        )


    def widget(self):
        return self.frame
