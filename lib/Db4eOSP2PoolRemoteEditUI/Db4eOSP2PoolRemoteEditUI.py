"""
lib/Db4eOSP2PoolRemoteEditUI/Db4eOSP2PoolRemoteEditUI.py

This urwid based TUI drops into the db4e-os.py TUI to help the
user re-configure access to a P2Pool daemon running on a remote node.


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

class Db4eOSP2PoolRemoteEditUI:
    def __init__(self, parent_tui):
        self.parent_tui = parent_tui
        self._model = Db4eOSModel()
        self._db = Db4eOSDb()
        # Most of the initialization is done in set_instance()

    def back_to_main(self, button):
        self.parent_tui.return_to_main()

    def on_submit(self, button):
        instance = self.instance_edit.edit_text.strip()
        ip_addr = self.ip_addr_edit.edit_text.strip()
        stratum_port = self.stratum_port_edit.edit_text.strip()

        good = MD['good']
        warning = MD['warning']

        # Validate input
        if any(not val for val in (instance, ip_addr, stratum_port)):
            self.results_msg.set_text("You must fill in *all* of the fields")
            return
        try:
            stratum_port = int(stratum_port)
        except:
            self.results_msg.set_text("The stratum port must be an integer value")

        if instance != self.old_instance:
            if self._db.get_deployment_by_instance('p2pool', instance):
                self.results_msg.set_text(f"The instance name ({instance}) is already being used. " +
                                        "There can be only one P2Pool daemon deployment with that " +
                                        "instance name.")
                return

        results = 'Checklist:\n'
        # Check that db4e can connect to the remote system
        if self._model.is_port_open(ip_addr, stratum_port):
            results += f'{good} Connected to stratum port ({stratum_port}) on remote machine ({ip_addr})\n'
        else:
            results += f'{warning} Unable to connect to stratum port ({stratum_port}) on remote machine ({ip_addr})\n'

        if instance != self.old_instance:
            self._db.update_deployment_instance('p2pool', self.old_instance, { 
                'status': 'running',
                'instance': instance,
                'ip_addr': ip_addr,
                'stratum_port': stratum_port,
                'remote': True
                })
        else:
            self._db.update_deployment_instance('p2pool', instance, { 
                'status': 'running',
                'instance': instance,
                'ip_addr': ip_addr,
                'stratum_port': stratum_port,
                'remote': True
                })

        # Set the results
        results += f'\nRe-configured the P2Pool daemon ({instance}) deployment record. '
        self.results_msg.set_text(results)

        # Remove the submit button
        self.back_button.set_label("Done")
        self.form_buttons.set_focus(0)
        self.form_buttons.contents = [
            (self.back_button, self.form_buttons.options('given', 8))
        ]

    def reset(self):
        self.old_instance = None
        self.instance_edit = urwid.Edit("P2Pool instance name (e.g. Primary): ", edit_text='')
        self.ip_addr_edit = urwid.Edit("Remote P2Pool hostname or IP address: ", edit_text='')
        self.stratum_port_edit = urwid.Edit("Stratum port: ", edit_text='')
        self.submit_button = urwid.Button(('button', 'Submit'), on_press=self.on_submit)
        self.back_button = urwid.Button(('button', 'Back'), on_press=self.back_to_main)
        self.form_buttons = urwid.Columns([
            (10, self.submit_button),
            (8, self.back_button)
        ], dividechars=1)
        self.results_msg = urwid.Text('')

    def set_instance(self, instance):
        p2pool_rec = self._db.get_deployment_by_instance('p2pool', instance)
        self.old_instance = instance
        ip_addr = p2pool_rec['ip_addr'] or ''
        stratum_port = p2pool_rec['stratum_port'] or ''

        # Form elements; edit widgets
        self.instance_edit = urwid.Edit("P2Pool instance name (e.g. Primary): ", edit_text=instance)
        self.ip_addr_edit = urwid.Edit("Remote P2Pool hostname or IP address: ", edit_text=ip_addr)
        self.stratum_port_edit = urwid.Edit("Stratum port: ", edit_text=str(stratum_port))

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
            self.stratum_port_edit,
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
            urwid.Text('Remote P2Pool Demon Setup\n\n' +
                'The \"instance name\" must be unique within the ' +
                'db4e environment i.e. if you have more than one ' +
                'daemon deployed, then each must have their own ' +
                'instance name.\n\nUse the arrow keys or mouse scrollwheel ' +
                'to scroll up and down and the spacebar to click.'),
            urwid.Divider(),
            urwid.LineBox(
                urwid.Padding(self.form_box, left=2, right=2),
                title='Setup Form', title_align='left', title_attr='title'
            ),
            self.results_box
        ]

        # Wrap in a ListBox to make scrollable
        listbox = urwid.ListBox(urwid.SimpleFocusListWalker(form_widgets))
        self.frame = urwid.LineBox(
            urwid.Padding(listbox, left=2, right=2),
            title="Remote P2Pool Daemon Setup", title_align="center", title_attr="title"
        )

    def widget(self):
        return self.frame
