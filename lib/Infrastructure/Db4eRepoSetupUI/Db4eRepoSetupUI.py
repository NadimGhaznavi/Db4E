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

class Db4eRepoSetupUI:
    def __init__(self, parent_tui):
        self.parent_tui = parent_tui
        self.github_username_edit = urwid.Edit("GitHub user name (e.g. NadimGhaznavi): ")
        self.github_repo_name_edit = urwid.Edit("GitHub repo name (e.g. xmr): ")
        self.local_repo_path_edit = urwid.Edit("Local path for the repo: (e.g. /home/nadim/xmr): ")
        self.info_text = urwid.Text("")
        self.form = urwid.Pile([
            urwid.Text('Enter the following information to setup your db4d GitHub Pages website:'),
            urwid.Divider(),
            self.github_username_edit,
            self.github_repo_name_edit,
            self.local_repo_path_edit,
            urwid.Divider(),
            urwid.Button(('button', 'Submit'), on_press=self.on_submit),
            urwid.Button(('button', 'Back'), on_press=self.back_to_main)
        ])
        self.frame = urwid.LineBox(
            urwid.Padding(urwid.Pile([self.form, self.info_text]), left=2, right=2),
            title="GitHub Repo Setup", title_align="center", title_attr="title"
        )

    def back_to_main(self, button):
        self.parent_tui.return_to_main()

    def on_submit(self, button):
        repo_name = self.repo_name_edit.edit_text.strip()
        clone_path = os.path.expanduser(self.repo_path_edit.edit_text.strip())

        # Validate input
        if not repo_name or not clone_path:
            self.info_text.set_text("Please provide your GitHub username, repository name and local path.")
            return

        # Check SSH access
        try:
            ssh_result = subprocess.run(
                ["ssh", "-T", "git@github.com"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                input=b"",
                timeout=10
            )
            if ssh_result.returncode not in (0, 1):  # 1 is acceptable for SSH auth check
                self.info_text.set_text("SSH connection failed. Ensure SSH is configured for GitHub.")
                return
        except Exception as e:
            self.info_text.set_text(f"SSH check failed: {str(e)}")
            return

        # Try to clone
        try:
            if os.path.exists(clone_path):
                shutil.rmtree(clone_path)
            subprocess.run([
                "git", "clone", f"git@github.com:{repo_name}.git", clone_path
            ], check=True)
            self.info_text.set_text("Repository cloned successfully.")
        except subprocess.CalledProcessError:
            self.info_text.set_text("Failed to clone the repository. Check SSH and repo name.")
        except Exception as e:
            self.info_text.set_text(f"Error: {str(e)}")

    def widget(self):
        return self.frame
