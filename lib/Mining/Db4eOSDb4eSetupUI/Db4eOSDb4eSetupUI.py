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

NEW_DB4E_SERVICE_MSG = "Database 4 Everything Service Setup\n\n"
NEW_DB4E_SERVICE_MSG += "This screen lets you install db4e as a service. "
NEW_DB4E_SERVICE_MSG += "The service will start at boot time and is "
NEW_DB4E_SERVICE_MSG += "responsible for the following:\n\n"
NEW_DB4E_SERVICE_MSG += "* The Monero blockchain daemon(s).\n"
NEW_DB4E_SERVICE_MSG += "* The P2Pool daemon(s).\n"
NEW_DB4E_SERVICE_MSG += "* The XMRig miner(s).\n\n"
NEW_DB4E_SERVICE_MSG += "You *MUST* have sudo access to the root account "
NEW_DB4E_SERVICE_MSG += "before you can proceed."


class Db4eOSDb4eSetupUI:
    def __init__(self, parent_tui):
        self.parent_tui = parent_tui
        self._db = Db4eOSDb()
        self._ini = Db4eConfig()
        repo_rec = self._db.get_repo_deployment()
        github_user = repo_rec['github_user'] or ''
        github_repo = repo_rec['github_repo'] or ''
        install_dir = repo_rec['install_dir'] or ''
        self.github_username_edit = urwid.Edit("GitHub user name (e.g. NadimGhaznavi): ", edit_text=github_user)
        self.github_repo_name_edit = urwid.Edit("GitHub repo name (e.g. xmr): ", edit_text=github_repo)
        self.local_repo_path_edit = urwid.Edit("Local path for the repo: (e.g. /home/nadim/xmr): ", edit_text=install_dir)

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
            urwid.Text('When you setup db4e as a service you will be prompted for your ' +
                       'password. This is for "sudo" access which will allow db4e to ' +
                       'install and configure the service.'),
            urwid.Divider(),
            urwid.Columns([
                ('pack', urwid.Button(('button', 'Install Service'), on_press=self.on_submit)),
                ('pack', urwid.Button(('button', 'Back'), on_press=self.back_to_main))
                ]),
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

    def setup_service_msg(self):
        return NEW_DB4E_SERVICE_MSG

    def on_submit(self, button):
        tmpl_dir         = self._ini.config['db4e']['template_dir']
        service_file     = self._ini.config['db4e']['service_file']
        systemd_dir      = self._ini.config['db4e']['systemd_dir']
        installer_script = self._ini.config['db4e']['service_installer']
        bin_dir          = self._ini.config['db4e']['bin_dir']
        db4e_rec = self._db.get_db4e_deployment()
        db4e_dir = db4e_rec['install_dir']
        fq_service_file = os.path.join(db4e_dir, tmpl_dir, systemd_dir, service_file)
        with open(fq_service_file, 'r') as f:
            service_contents = f.read()
        service_contents = service_contents.replace('[[INSTALL_DIR]]', db4e_dir)
        tmp_service_file = os.path.join('/tmp', service_file)
        with open(tmp_service_file, 'w') as f:
            f.write(service_contents)
        
        try:
            fq_installer = os.path.join(db4e_dir, bin_dir, installer_script)
            cmd_result = subprocess.run(
                ['sudo', fq_installer, tmp_service_file, ],
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
            
            self._db.update_db4e({'status': 'running'})
            self.info_msg.set_text(f"Service installed successfully:\n{stdout}")

        except Exception as e:
            self.info_msg.set_text(f"Service install failed: {str(e)}")

    def widget(self):
        return self.frame
