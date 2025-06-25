"""
lib/Db4eOSRepoEditUI/Db4eOSRepoEditUI.py

This urwid based TUI drops into the db4e-os.py TUI to help the
user re-configure their GitHub repository.


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
from Db4eOSModel.Db4eOSModel import Db4eOSModel
from Db4eConfig.Db4eConfig import Db4eConfig

class Db4eOSRepoEditUI:
    def __init__(self, parent_tui):
        self.parent_tui = parent_tui
        self.osdb = Db4eOSDb()
        self.model = Db4eOSModel()
        self.ini = Db4eConfig()
        self.reset() # (Re)initialize the mini-TUI

    def back_to_main(self, button):
        self.parent_tui.return_to_main()

    def on_submit(self, button):
        username = self.github_username_edit.edit_text.strip()
        repo_name = self.github_repo_name_edit.edit_text.strip()
        clone_path = os.path.expanduser(self.local_repo_path_edit.edit_text.strip())

        # Validate input
        if not username or not repo_name or not clone_path:
            self.results_msg.set_text("Please provide your GitHub username, repository name and a local path.")
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
                self.results_msg.set_text(f"SSH connection failed.\nSTDOUT: {stdout}\nSTDERR: {stderr}")
                return

            self.results_msg.set_text(
                f"SSH check succeeded (return code {cmd_result.returncode}).\nSTDOUT: {stdout}\nSTDERR: {stderr}"
            )

        except Exception as e:
            self.results_msg.set_text(f"SSH check failed: {str(e)}")
            return

        # Delete the old repository
        if os.path.exists(self.old_install_dir):
            shutil.rmtree(self.old_install_dir)

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
                self.results_msg.set_text(
                    f'Failed to clone repository.\n\n{stderr}'
                )
                return
            
            self.osdb.update_deployment('repo', {
                'status': 'running',
                'component': 'repo',
                'install_dir': clone_path,
                'github_user': username,
                'github_repo': repo_name
                })
            results_text = 'Repository cloned successfully.\n\n'
            results_text += 'Pre-populating static content:\n'

            # Pre-Populate the new repo with static content
            db4e_dir = self.model.get_db4e_dir()
            local_repo_dir = self.model.get_repo_dir()
            tmpl_dir = self.ini.config['db4e']['template_dir']
            db4e_repo_dir = self.ini.config['db4e']['repo_dir']
            bin_dir = self.ini.config['db4e']['bin_dir']
            update_repo_script = self.ini.config['db4e']['update_repo_script']
            fq_script = os.path.join(db4e_dir, bin_dir, update_repo_script)
            fq_src_dir = os.path.join(db4e_dir, tmpl_dir, db4e_repo_dir)
            sync_result = subprocess.run(
                [fq_script, fq_src_dir, local_repo_dir],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            
            if sync_result.returncode != 0:
                stderr = cmd_result.stderr.decode().strip()
                self.results_msg.set_text(
                    f'Failed to pre-populate static content.\n\n{stderr}'
                )
                return
            
            # Set the results
            sync_output = sync_result.stdout.decode().strip()
            self.results_msg.set_text(f'{results_text}{sync_output}')

            # Remove the submit button after success
            self.back_button.set_label("Done")
            self.form_buttons.set_focus(0)
            self.form_buttons.contents = [
                (self.back_button, self.form_buttons.options('given', 8))
            ]

        except Exception as e:
            self.results_msg.set_text(f"Error: {str(e)}")

    def reset(self):
        repo_rec = self.osdb.get_deployment_by_component('repo')
        github_user = repo_rec['github_user'] or ''
        github_repo = repo_rec['github_repo'] or ''
        install_dir = repo_rec['install_dir'] or ''
        self.old_install_dir = install_dir

        # Form elements, edit widgets
        self.github_username_edit = urwid.Edit("GitHub user name (e.g. NadimGhaznavi): ", edit_text=github_user)
        self.github_repo_name_edit = urwid.Edit("GitHub repo name (e.g. xmr): ", edit_text=github_repo)
        self.local_repo_path_edit = urwid.Edit("Local path for the repo: (e.g. /home/nadim/xmr): ", edit_text=install_dir)

        # The buttons
        self.update_button =  urwid.Button(('button', 'Update'), on_press=self.on_submit)
        self.back_button = urwid.Button(('button', 'Back'), on_press=self.back_to_main)

        # The assembled buttons
        self.form_buttons = urwid.Columns([
            (10, self.update_button),
            (8, self.back_button)
        ], dividechars=1)

        # The assembled form elements and buttons
        self.form_box = urwid.Pile([
            self.github_username_edit,
            self.github_repo_name_edit,
            self.local_repo_path_edit,
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
            urwid.Text('This screen allows you to re-create your local website ' +
                       'GitHub repository. Do *NOT* use a "local path" ' +
                       'that is within the directory where you have installed db4e.\n\n' +
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
            title="GitHub Website Repository Setup", title_align='center', title_attr='title'
        )

    def widget(self):
        return self.frame
