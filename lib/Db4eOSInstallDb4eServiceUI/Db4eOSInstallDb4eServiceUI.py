"""
lib/Db4eOSInstallDb4eServiceUI/Db4eOSInstallDb4eServiceUI.py

This urwid based TUI drops into the db4e-os.py TUI to enable the
user to install the db4e service.


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
lib_dir = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(lib_dir)

# Import DB4E modules
from Db4eOSDb.Db4eOSDb import Db4eOSDb
from Db4eConfig.Db4eConfig import Db4eConfig
from Db4eOSModel.Db4eOSModel import Db4eOSModel
from Db4eOSStrings.Db4eOSStrings import MD

bullet = MD['bullet']
INTRO_TEXT = 'The db4e service is at the core of db4e. It must be installed and running. '
INTRO_TEXT += 'Clicking on the "Proceed" button will install the service, configure it '
INTRO_TEXT += 'to automatically start when the system boots and start it now.\n\n'
INTRO_TEXT += 'Installing a systemd service requires root access. You will be prompted '
INTRO_TEXT += 'for your password. This is for "sudo" access. The db4e application never '
INTRO_TEXT += 'stores your password.'

class Db4eOSInstallDb4eServiceUI:
    def __init__(self, parent_tui):
        self.parent_tui = parent_tui
        self.osdb = Db4eOSDb()
        self.ini = Db4eConfig()
        self.model = Db4eOSModel()

        # The buttons
        self.proceed_button = urwid.Button(('button', 'Proceed'), on_press=self.on_proceed)
        self.continue_button = urwid.Button(('button', 'Continue'), on_press=self.on_continue)
        self.quit_button = urwid.Button(('button', 'Quit'), on_press=self.on_quit)

        # The assembled buttons
        self.form_buttons = urwid.Columns([
            (11, self.proceed_button),
            (8, self.quit_button)
            ], dividechars=1)
        
        # Results
        self.results_msg = urwid.Text('')
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

        all_widgets = [
            urwid.Text(INTRO_TEXT),
            urwid.Divider(),
            self.form_buttons,
            self.results_box
        ]

        # Wrap in a ListBox to make scrollable
        listbox = urwid.ListBox(urwid.SimpleFocusListWalker(all_widgets))
        self.frame = urwid.LineBox(
            urwid.Padding(listbox, left=2, right=2),
            title="Reinstall the db4e Service", title_align="center", title_attr="title"
        )

    def on_continue(self, button):
        self.parent_tui.return_to_main()

    def on_proceed(self, button):
        db4e_user = os.getlogin()
        db4e_group = self.model.get_db4e_group()

        # Start assembling the results
        good = MD['good']
        dancing_man = MD['dancing_man']
        dancing_woman = MD['dancing_woman']
        msg_text = 'Checklist:\n'

        # Additional config settings
        bin_dir                = self.ini.config['db4e']['bin_dir']
        db4e_service_file      = self.ini.config['db4e']['service_file']
        service_install_script = self.ini.config['db4e']['service_install_script']
        systemd_dir            = self.ini.config['db4e']['systemd_dir']
        tmpl_dir               = self.ini.config['db4e']['template_dir']

        # db4e, P2Pool, Monero daemon and XMRig directories
        db4e_dir = self.osdb.get_dir('db4e')

        # Templates for the db4e, Monero daemon and P2pool services
        fq_db4e_service_file    = os.path.join(db4e_dir, tmpl_dir, systemd_dir, db4e_service_file)

        # Temp directory to house the systemd service files
        tmp_dir = os.path.join('/tmp', 'db4e')
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
        os.mkdir(tmp_dir)

        # Update the db4e service template with deployment values
        placeholders = {
            'DB4E_USER': db4e_user,
            'DB4E_GROUP': db4e_group,
            'DB4E_DIR': db4e_dir,
        }
        with open(fq_db4e_service_file, 'r') as f:
            service_contents = f.read()
            for key, val in placeholders.items():
                service_contents = service_contents.replace(f'[[{key}]]', str(val))
        tmp_service_file = os.path.join(tmp_dir, db4e_service_file)
        with open(tmp_service_file, 'w') as f:
            f.write(service_contents)

        # Run the bin/db4e-installer.sh
        try:
            fq_service_install = os.path.join(db4e_dir, bin_dir, service_install_script)
            cmd_result = subprocess.run(
                ['sudo', fq_service_install],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                input=b"",
                timeout=10)
            stdout = cmd_result.stdout.decode().strip()
            stderr = cmd_result.stderr.decode().strip()

            # 1 is acceptable for SSH auth check
            if cmd_result.returncode != 0:
                self.results_msg.set_text(f"Service install failed.\n\n{stderr}")
                return
            
            for aLine in stdout.split('\n'):
                msg_text += f"{good}  {aLine}\n"
            msg_text += f"{dancing_man} db4e service setup was successful {dancing_woman}"
            self.results_msg.set_text(msg_text)
            shutil.rmtree(tmp_dir)

        except Exception as e:
            self.results_msg.set_text(f"Service install failed: {str(e)}")

        # Replace the "Quit" and "Proceed" buttons with a "Continue" button
        self.form_buttons.set_focus(0)
        self.form_buttons.contents = [
            (self.continue_button, self.form_buttons.options('given', 12))
        ]   

    def on_quit(self, button):
        raise urwid.ExitMainLoop()

    def widget(self):
        return self.frame
