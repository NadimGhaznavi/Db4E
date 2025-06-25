"""
lib/Db4eOSDb4eEditUI/Db4eOSDb4eEditUI.py

This urwid based TUI drops into the db4e-os.py TUI to help the
user re-configure the core db4e service.


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
from datetime import datetime

# Where the DB4E modules live
lib_dir = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(lib_dir)

# Import DB4E modules
from Db4eOSDb.Db4eOSDb import Db4eOSDb
from Db4eOSModel.Db4eOSModel import Db4eOSModel
from Db4eConfig.Db4eConfig import Db4eConfig
from Db4eOSStrings.Db4eOSStrings import MD

class Db4eOSDb4eEditUI:
    def __init__(self, parent_tui):
        self.parent_tui = parent_tui
        self._db = Db4eOSDb()
        self.model = Db4eOSModel()
        self.ini = Db4eConfig()
        self.reset() # (Re)initialize the mini-TUI

    def back_to_main(self, button):
        self.parent_tui.return_to_main()

    def on_submit(self, button):
        vendor_dir = self.vendor_dir_edit.edit_text.strip()
        good = MD['good']
        warning = MD['warning']

        # Validate input
        if not vendor_dir:
            self.results_msg.set_text(f'{warning}  You must set the 3rd party software directory.')
            return

        # Create the vendor directory
        results = ''
        if self.old_vendor_dir and self.old_vendor_dir != vendor_dir:
            if os.path.exists(vendor_dir):
                timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
                try:
                    os.rename(vendor_dir, vendor_dir + '.' + timestamp)
                    results += f'{warning}  Found existing directory ({vendor_dir}), backed it up as ({vendor_dir}.{timestamp})\n'
                except PermissionError as e:
                    results += f'{warning}  Unable to move directory ({vendor_dir}): {e}'
                    self.results_msg.set_text(results)
                    return
            # Move the directory
            try:
                shutil.move(self.old_vendor_dir, vendor_dir)
                results += f'{good}  Moved {self.old_vendor_dir} to {vendor_dir}'
            except (PermissionError, FileNotFoundError) as e:
                results_msg += f'{warning}  Failed to create directory ({vendor_dir}). Make sure you '
                results_msg += f'{warning}  have permission to create the directory and that the parent '
                results_msg += f'{warning}  exists\n\n'
                self.results_msg.set_text(results)
                return

        # Update the deployment record
        self._db.update_deployment('db4e', {'vendor_dir': vendor_dir})

        # Set the results
        self.results_msg.set_text(f'{good}  Updated the db4e deployment record')

        # Remove the submit button
        self.back_button.set_label("Done")
        self.form_buttons.set_focus(0)        
        self.form_buttons.contents = [
            (self.back_button, self.form_buttons.options('given', 8))
        ]        

    def reset(self):
        vendor_dir = self.model.get_dir('vendor') or ''
        self.old_vendor_dir = vendor_dir
        # Form elements, edit widgets
        self.vendor_dir_edit = urwid.Edit("3rd party software directory: ", edit_text=vendor_dir)

        # The buttons
        self.update_button =  urwid.Button(('button', 'Update'), on_press=self.on_submit)
        self.uninstall_button = urwid.Button(('button', 'Uninstall Service'), on_press=self.uninstall_service)
        self.back_button = urwid.Button(('button', 'Back'), on_press=self.back_to_main)

        # The assembled buttons
        self.form_buttons = urwid.Columns([
            (10, self.update_button),
            (21, self.uninstall_button),
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
                    title='Results', title_align='left', title_attr='title'
                )
        ])

        form_widgets = [
            urwid.Text('This screen allows (re)set the 3rd party software directory ' +
                       'and uninstall the db4e service. The unistall of the db4e ' +
                       'service requires root access using sudo. You will be prompted ' +
                       'for your password if you uninstall the service.\n\n' +
                       'Use the arrow keys or mouse scrollwheel to scroll up and down  ' +
                       'and the spacebar to click.'),
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
            title="Edit db4e Configuration", title_align='center', title_attr='title'
        )

    def uninstall_service(self, button):
        db4e_dir = self._db.get_db4e_dir()
        uninstall_script = self.ini.config['db4e']['service_uninstaller']
        bin_dir          = self.ini.config['db4e']['bin_dir']
        fq_uninstaller = os.path.join(db4e_dir, bin_dir, uninstall_script)

        try:
            cmd_result = subprocess.run(
                ['sudo', fq_uninstaller],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                input=b"",
                timeout=10)
            stdout = cmd_result.stdout.decode().strip()
            stderr = cmd_result.stderr.decode().strip()

            # 1 is acceptable for SSH auth check
            if cmd_result.returncode != 0:
                self.results_msg.set_text(f"Service uninstall failed.\n\n{stderr}")
                return
            
            self.results_msg.set_text(f"Service uninstalled successfully:\n{stdout}")

        except Exception as e:
            self.results_msg.set_text(f"Service uninstall failed: {str(e)}")

    def widget(self):
        return self.frame
