"""
lib/Infrastructure/Db4eRepoSetupUI/Db4eRepoSetupUI.py

This urwid based TUI drops into the db4e-os.py TUI to help the
user configure their GitHub repository.
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


NEW_REPO_MSG = "GitHub Pages Website Repository Setup\n\n"
NEW_REPO_MSG += "This screen will help you setup your GitHub repository. This "
NEW_REPO_MSG += "repo is used by db4e to publish web reports. In order to"
NEW_REPO_MSG += "proceed you *must*:\n\n"
NEW_REPO_MSG += "  * Have a GitHub account\n"
NEW_REPO_MSG += "  * Have created a db4e GitHub repository\n"
NEW_REPO_MSG += "  * Have configured the GitHub repository\n"
NEW_REPO_MSG += "  * Have SSH Authentication with GitHub configured\n\n"
NEW_REPO_MSG += "The command \"ssh -T git@github.com\" needs to work. "
NEW_REPO_MSG += "You *MUST* have this configured before you can proceeed. "
NEW_REPO_MSG += "Refer to the \"Getting Started\" page "
NEW_REPO_MSG += "(https://db4e.osoyalce.com/pages/Getting-Started.html) for "
NEW_REPO_MSG += "detailed information on setting this up."


class Db4eOSRepoSetupUI:
    def __init__(self, parent_tui):
        self.parent_tui = parent_tui
        self._db = Db4eOSDb()
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
            urwid.Text('Enter your GitHub account name, the name of your GitHub ' + 
                       'repository and a directory on your computer for the local ' +
                       'GitHub repository. Git will create the local directory and ' +
                       'clone your repository into it. Do *NOT* use a "local path" ' +
                       'that is within the directory where you have installed db4e.\n\n' +
                       'Use the arrow keys or mouse scrollwheel to scroll up and down.'),
            urwid.Divider(),
            urwid.LineBox(
                urwid.Padding(
                    urwid.Pile([
                        self.github_username_edit,
                        self.github_repo_name_edit,
                        self.local_repo_path_edit,
                        urwid.Divider(),
                        urwid.Columns([
                            ('pack', urwid.Button(('button', 'Submit'), on_press=self.on_submit)),
                            ('pack', urwid.Button(('button', 'Back'), on_press=self.back_to_main))
                        ])
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

    def new_repo_msg(self):
        return NEW_REPO_MSG

    def on_submit(self, button):
        username = self.github_username_edit.edit_text.strip()
        repo_name = self.github_repo_name_edit.edit_text.strip()
        clone_path = os.path.expanduser(self.local_repo_path_edit.edit_text.strip())

        # Validate input
        if not username or not repo_name or not clone_path:
            self.info_msg.set_text("Please provide your GitHub username, repository name and a local path.")
            return

        # Check SSH access
        try:
            cmd_result = subprocess.run(
                ["ssh", "-T", "git@github.com"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                input=b"",
                timeout=10)
            stdout = cmd_result.stdout.decode().strip()
            stderr = cmd_result.stderr.decode().strip()

            # 1 is acceptable for SSH auth check
            if cmd_result.returncode not in (0, 1):  
                self.info_msg.set_text(
                    f"SSH connection failed.\nSTDOUT: {stdout}\nSTDERR: {stderr}"
                )
                return

            self.info_msg.set_text(
                f"SSH check succeeded (return code {cmd_result.returncode}).\nSTDOUT: {stdout}\nSTDERR: {stderr}"
            )

        except Exception as e:
            self.info_msg.set_text(f"SSH check failed: {str(e)}")
            return

        # Try to clone
        try:
            if os.path.exists(clone_path):
                # Delete the clone_path if it exists
                shutil.rmtree(clone_path)

            cmd_result = subprocess.run(
                ["git", "clone", f"git@github.com:{username}/{repo_name}.git", clone_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            stdout = cmd_result.stdout.decode().strip()
            stderr = cmd_result.stderr.decode().strip()

            if cmd_result.returncode != 0:
                self.info_msg.set_text(
                    f'Failed to clone repository.\n\n{stderr}'
                )
                return

            self._db.update_repo({ 
                'status': 'running', 
                'install_dir': clone_path,
                'github_user': username,
                'github_repo': repo_name
                })
            self.info_msg.set_text("Repository cloned successfully.")

        except Exception as e:
            self.info_msg.set_text(f"Error: {str(e)}")

    def widget(self):
        return self.frame
