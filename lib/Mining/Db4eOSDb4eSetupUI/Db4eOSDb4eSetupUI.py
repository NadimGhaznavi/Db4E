"""
lib/Infrastructure/Db4eOSDb4eSetupUI/Db4eOSDb4eSetupUI.py

This urwid based TUI drops into the db4e-os.py TUI to help the
user setup the db4e service.
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

from Db4eOSDb.Db4eOSDb import Db4eOSDb
from Db4eConfig.Db4eConfig import Db4eConfig

# TODO Put into a strings class
MD = {
    'good'  : '✔️',
    'warning' : '⚠️',
}

class Db4eOSDb4eSetupUI:
    def __init__(self, parent_tui):
        self.parent_tui = parent_tui
        self._db = Db4eOSDb()
        self.ini = Db4eConfig()
        self.db4e_group_edit = urwid.Edit("The Linux db4e group: ", edit_text='db4e')
        self.vendor_dir_edit = urwid.Edit("3rd party software directory (e.g. /home/sally/vendor): ", edit_text='')
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

        # The buttons
        self.proceed_button = urwid.Button(('button', 'Proceed'), on_press=self.on_submit)
        self.back_button = urwid.Button(('button', 'Back'), on_press=self.back_to_main)

        # The assembled buttons
        self.form_buttons = urwid.Columns([
            (11, self.proceed_button),
            (8, self.back_button)
            ], dividechars=1)

        form_widgets = [
            urwid.Text('The 3rd party software directory must *NOT* be within ' +
                       'the db4e directory or in the directory containing the ' + 
                       'website repository.\n\n' +
                       'When you setup db4e as a service you will be prompted for your ' +
                       'password. This is for "sudo" access which will allow db4e to ' +
                       'install and configure the service.'),
            urwid.Divider(),
            self.db4e_group_edit,
            self.vendor_dir_edit,
            urwid.Divider(),
            self.form_buttons,
            self.info_text
        ]

        # Wrap in a ListBox to make scrollable
        listbox = urwid.ListBox(urwid.SimpleFocusListWalker(form_widgets))
        self.frame = urwid.LineBox(
            urwid.Padding(listbox, left=2, right=2),
            title="db4e Service Setup", title_align="center", title_attr="title"
        )

    def back_to_main(self, button):
        self.parent_tui.return_to_main()

    def on_submit(self, button):
        good = MD['good']
        # Create the 3rd party software directory
        vendor_dir = self.vendor_dir_edit.edit_text.strip()
        if not vendor_dir:
            self.info_msg.set_text("You must set the 3rd party software directory.")
            return
        
        try:
            if os.path.exists(vendor_dir):
                shutil.rmtree(vendor_dir)
            os.mkdir(vendor_dir)
        except (PermissionError, FileNotFoundError, FileExistsError) as e:
            error_msg = f'Failed to create directory ({vendor_dir}). Make sure you '
            error_msg += 'have permission to create the directory and that the parent '
            error_msg += f'exists\n\n'
            error_msg += f'{e}'
            self.results_msg.set_text(error_msg)
            return
        msg_text = 'Checklist\n'
        msg_text += f'{good}  Created 3rd party software directory: {vendor_dir}\n'

        # The db4e group
        db4e_group = self.db4e_group_edit.edit_text.strip()
        if not db4e_group:
            self.info_msg.set_text("You must choose a name for the db4e group")
            return
        
        # The db4e user
        db4e_user = os.getlogin()

        tmpl_dir         = self.ini.config['db4e']['template_dir']
        service_file     = self.ini.config['db4e']['service_file']
        systemd_dir      = self.ini.config['db4e']['systemd_dir']
        installer_script = self.ini.config['db4e']['service_installer']
        bin_dir          = self.ini.config['db4e']['bin_dir']
        third_party_dir  = self.ini.config['db4e']['third_party_dir']
        xmrig_version    = self.ini.config['xmrig']['version']
        xmrig_binary     = self.ini.config['xmrig']['process']

        db4e_dir = self._db.get_db4e_dir()

        # Template for the db4e.service
        fq_service_file = os.path.join(db4e_dir, tmpl_dir, systemd_dir, service_file)

        # Setup xmrig so the installer script can set the SUID bit for performance reasons
        xmrig_src = os.path.join(db4e_dir, third_party_dir, 'xmrig-' + xmrig_version, bin_dir,  xmrig_binary)
        xmrig_dest = os.path.join(vendor_dir, 'xmrig-' + xmrig_version, bin_dir,  xmrig_binary)
        os.mkdir(os.path.join(vendor_dir, 'xmrig-' + xmrig_version))
        os.mkdir(os.path.join(vendor_dir, 'xmrig-' + xmrig_version, bin_dir))

        # Update the template service definition with the actual deployment path
        with open(fq_service_file, 'r') as f:
            service_contents = f.read()
            service_contents = service_contents.replace('[[INSTALL_DIR]]', db4e_dir)
            service_contents = service_contents.replace('[[DB4E_USER]]', db4e_user)
        tmp_service_file = os.path.join('/tmp', service_file)
        with open(tmp_service_file, 'w') as f:
            f.write(service_contents)

        # Run the bin/db4e-installer.sh
        try:
            fq_installer = os.path.join(db4e_dir, bin_dir, installer_script)
            cmd_result = subprocess.run(
                ['sudo', fq_installer, tmp_service_file, db4e_group, db4e_user, xmrig_src, xmrig_dest],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                input=b"",
                timeout=10)
            stdout = cmd_result.stdout.decode().strip()
            stderr = cmd_result.stderr.decode().strip()

            # 1 is acceptable for SSH auth check
            if cmd_result.returncode != 0:
                self.info_msg.set_text(f"Service install failed.\n\n{stderr}")
                return
            
            self._db.update_deployment('db4e', {'status': 'running', 'vendor_dir': vendor_dir})
            for aLine in stdout.split('\n'):
                msg_text += f"{good}  {aLine}\n"
            msg_text += f"Service installed successfully:\n"
            self.info_msg.set_text(msg_text)
            os.remove(tmp_service_file)

        except Exception as e:
            self.info_msg.set_text(f"Service install failed: {str(e)}")

        # Remove the submit button
        self.back_button.set_label("Done")
        self.form_buttons.set_focus(0)
        self.form_buttons.contents = [
            (self.back_button, self.form_buttons.options('given', 8))
        ]

    def widget(self):
        return self.frame
