"""
lib/Db4eOSMonerodRemoteSetupUI/Db4eOSMonerodRemoteSetupUI.py

This urwid based TUI drops into the db4e-os.py TUI to help the
user configure access to a Monero blockchain daemon running on a
remote node.


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
lib_dir = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(lib_dir)

# Import DB4E modules
from Db4eOSModel.Db4eOSModel import Db4eOSModel
from Db4eOSDb.Db4eOSDb import Db4eOSDb
from Db4eOSStrings.Db4eOSStrings import MD

class Db4eOSMonerodRemoteSetupUI:
    def __init__(self, parent_tui):
        self.parent_tui = parent_tui
        self.osdb = Db4eOSDb()
        self.model = Db4eOSModel()
        self.reset() # (Re)initialize the mini-TUI

    def back_to_main(self, button):
        self.parent_tui.return_to_main()

    def on_submit(self, button):
        instance = self.instance_edit.edit_text.strip()
        ip_addr = self.ip_addr_edit.edit_text.strip()
        zmq_port = self.zmq_port_edit.edit_text.strip()
        rpc_port = self.rpc_port_edit.edit_text.strip()

        # Unicode
        good = MD['good']
        warning = MD['warning']
        dancing_man = MD['dancing_man']
        dancing_woman = MD['dancing_woman']

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

        if self.osdb.get_deployment_by_instance('monerod', instance):
            self.results_msg.set_text(f"The instance name ({instance}) is already being used. " +
                                      "There can be only one Monero daemon deployment with that " +
                                      "instance name.")
            return

        # Check connectivity
        results = 'Checklist:\n'
        # Check that db4e can connect to the remote system
        if self.model.is_port_open(ip_addr, zmq_port):
            results += f'{good} Connected to ZMQ port ({zmq_port}) on remote machine ({ip_addr})\n'
        else:
            results += f"{warning} Unable to connect to ZMQ port ({zmq_port}) on remote machine ({ip_addr})\n"

        if self.model.is_port_open(ip_addr, rpc_port):
            results += f'{good} Connected to RPC port ({rpc_port}) on remote machine ({ip_addr})\n'
        else:
            results += f"{warning} Unable to connect to RPC port ({rpc_port}) on remote machine ({ip_addr})\n"

        # Create the deployment record
        depl = self.osdb.get_tmpl('monerod')
        depl['enable'] = True
        depl['instance'] = instance
        depl['ip_addr'] = ip_addr
        depl['remote'] = True
        depl['rpc_bind_port'] = rpc_port
        depl['zmq_pub_port'] = zmq_port
        self.osdb.new_deployment('monerod', depl)
        
        # Set the results
        results += f'{dancing_man} Created new Monero daemon ({instance}) deployment record {dancing_woman}'
        self.results_msg.set_text(results)

        # Remove the submit button
        self.back_button.set_label("Done")
        self.form_buttons.set_focus(0)
        self.form_buttons.contents = [
            (self.back_button, self.form_buttons.options('given', 8))
        ]

    def reset(self):
        monerod_rec = self.osdb.get_tmpl('monerod', 'remote')
        zmq_port = monerod_rec['zmq_pub_port'] or ''
        rpc_port = monerod_rec['rpc_bind_port'] or ''

        # Form elements; edit widgets
        self.instance_edit = urwid.Edit("Monero instance name (e.g. Primary): ", edit_text='')
        self.ip_addr_edit = urwid.Edit("Remote node hostname or IP address: ", edit_text='')
        self.zmq_port_edit = urwid.Edit("ZMQ port: ", edit_text=str(zmq_port))
        self.rpc_port_edit = urwid.Edit("RPC port: ", edit_text=str(rpc_port))

        # The buttons
        self.submit_button = urwid.Button(('button', 'Submit'), on_press=self.on_submit)
        self.back_button = urwid.Button(('button', 'Back'), on_press=self.back_to_main)

        # The assembled buttons
        self.form_buttons = urwid.Columns([
            (10, self.submit_button),
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
