"""
lib/Infrastructure/Db4eOSVendorSetupUI/Db4eOSVendorSetupUI.py

This urwid based TUI drops into the db4e-os.py TUI to let the
user set the directory where 3rd party software artifacts are
installed.


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

class Db4eOSVendorSetupUI:
    def __init__(self, parent_tui):
        self.parent_tui = parent_tui
        self._os = Db4eOS()
        self._db = Db4eOSDb()

        # Form elements; edit widgets
        self.vendor_dir_edit = urwid.Edit("3rd Party Software directory (e.g. /home/sally/3rdParty): ")

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
            self.vendor_dir_edit,
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
                title="Results", title_align='left', title_attr='title'
            )
        ])

        form_widgets = [
            urwid.Text('The "3rd Party Software Directory" is where 3rd party ' +
                'configuration files, logs, startup scripts and ' +
                'other 3rd party software artifacts are deployed. This directory ' +
                'must *NOT* use a \"local path\" within the directory where ' +
                'you have installed db4e or within the directory that you ' +
                'chose for the local GitHub repository.\n\n' +
                'Use the arrow keys or mouse scrollwheel to scroll up and ' +
                'down and the spacebar to click.'),
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
            title='3rd Party Software Directory Setup', title_align='center', title_attr='title'
        )

    def back_to_main(self, button):
        self.parent_tui.return_to_main()

    def on_submit(self, button):
        vendor_dir = self.vendor_dir_edit.edit_text.strip()

        # Validate input
        try:
            os.mkdir(vendor_dir)
        except (PermissionError, FileNotFoundError) as e:
            error_msg = f'Failed to create directory ({vendor_dir}). Make sure you '
            error_msg += 'have permission to create the directory and that the parent '
            error_msg += 'exists.\n\n'
            error_msg += f'{e}'
            self.results_msg.set_text(error_msg)
            return

        # Update the db4e deployment record
        self._db.update_deployment('db4e', {'vendor_dir': vendor_dir})

        # Set the results
        results = f'Set the local vendor software directory ({vendor_dir}).'
        self.results_msg.set_text(results)

        # Remove the submit button
        self.back_button.set_label("Done")
        self.form_buttons.set_focus(0)
        self.form_buttons.contents = [
            (self.back_button, self.form_buttons.options('given', 8))
        ]

    def select_p2pool(self, radio, new_state, deployment):
        if new_state:
            self.selected_p2pool = deployment

    def widget(self):
        return self.frame
