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


import urwid
import subprocess
import os
import shutil


NEW_REPO_MSG = "GitHub Pages Website Repository Setup\n\n"
NEW_REPO_MSG += "This screen will help you setup your GitHub repository. This "
NEW_REPO_MSG += "repo is used by db4e to publish web reports. In order to"
NEW_REPO_MSG += "proceed you *must*:\n\n"
NEW_REPO_MSG += "  * Have a GitHub account\n"
NEW_REPO_MSG += "  * Have created a db4e GitHub repository\n"
NEW_REPO_MSG += "  * Have configured the GitHub repository\n"
NEW_REPO_MSG += "  * Have SSH Authentication with GitHub configured\n\n"
NEW_REPO_MSG += "You *MUST* have this configured before you can proceeed. "
NEW_REPO_MSG += "Refer to the \"Getting Started\" page "
NEW_REPO_MSG += "(https://db4e.osoyalce.com/pages/Getting-Started.html) for "
NEW_REPO_MSG += "detailed information on setting this up."

class Db4eRepoSetupUI:
    def __init__(self, parent_tui):
        self.parent_tui = parent_tui
        self.github_username_edit = urwid.Edit("GitHub user name (e.g. NadimGhaznavi): ")
        self.github_repo_name_edit = urwid.Edit("GitHub repo name (e.g. xmr): ")
        self.local_repo_path_edit = urwid.Edit("Local path for the repo: (e.g. /home/nadim/xmr): ")
        self.info_text = urwid.Text("")
        self.form = urwid.Pile([
            urwid.Text('Enter the following information to setup your db4e GitHub Pages website:'),
            urwid.Divider(),
            self.github_username_edit,
            self.github_repo_name_edit,
            self.local_repo_path_edit,
            urwid.Divider(),
            urwid.Text('Do *NOT* use a \"local path\" in the directory where you have installed db4e.'),
            urwid.Divider(),
            urwid.Columns([
                ('pack', urwid.Button(('button', 'Submit'), on_press=self.on_submit)),
                ('pack', urwid.Button(('button', 'Back'), on_press=self.back_to_main))
            ])
            
        ])
        self.frame = urwid.LineBox(
            urwid.Padding(urwid.Pile([self.form, self.info_text]), left=2, right=2),
            title="GitHub Repo Setup", title_align="center", title_attr="title"
        )

    def back_to_main(self, button):
        self.parent_tui.return_to_main()

    def on_submit(self, button):
        username = self.github_username_edit.edit_text.strip()
        repo_name = self.github_repo_name_edit.edit_text.strip()
        clone_path = os.path.expanduser(self.local_repo_path_edit.edit_text.strip())

        # Validate input
        if not username or not repo_name or not clone_path:
            self.info_text.set_text("Please provide your GitHub username, repository name and a local path.")
            return

        # Check SSH access
        try:
            cmd_result = subprocess.run(
                ["ssh", "-T", "git@github.com"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                input=b"",
                timeout=5)
            stdout = cmd_result.stdout.decode().strip()
            stderr = cmd_result.stderr.decode().strip()

            # 1 is acceptable for SSH auth check
            if cmd_result.returncode not in (0, 1):  
                self.info_text.set_text(
                    f"SSH connection failed.\nSTDOUT: {stdout}\nSTDERR: {stderr}"
                )
                return

            self.info_text.set_text(
                f"SSH check succeeded (return code {cmd_result.returncode}).\nSTDOUT: {stdout}\nSTDERR: {stderr}"
            )

        except Exception as e:
            self.info_text.set_text(f"SSH check failed: {str(e)}")
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
                #check=True)
            stdout = cmd_result.stdout.decode().strip()
            stderr = cmd_result.stderr.decode().strip()

            if cmd_result.returncode != 0:
                self.info_text.set_text(
                    f'Failed to clone repository.\nSTDOUT: {stdout}\nSTDERR: {stderr}'
                )
                return

            self.info_text.set_text("Repository cloned successfully.")

        #except subprocess.CalledProcessError:
        #    self.info_text.set_text("Failed to clone the repository. Check SSH and repo name.")
        except Exception as e:
            self.info_text.set_text(f"Error: {str(e)}")

    def widget(self):
        return self.frame
