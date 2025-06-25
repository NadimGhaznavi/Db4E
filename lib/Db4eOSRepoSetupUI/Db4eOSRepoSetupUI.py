"""
lib/Db4eOSRepoSetupUI/Db4eOSRepoSetupUI.py

This urwid based TUI drops into the db4e-os.py TUI to help the
user configure their GitHub repository.


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
from Db4eOSStrings.Db4eOSStrings import MD

class Db4eOSRepoSetupUI:
    def __init__(self, parent_tui):
        self.parent_tui = parent_tui
        self.osdb = Db4eOSDb()
        self.model = Db4eOSModel()
        self.ini = Db4eConfig()
        self.reset()

    def back_to_main(self, button):
        self.reset()
        self.parent_tui.return_to_main()

    def on_submit(self, button):
        username = self.github_username_edit.edit_text.strip()
        repo_name = self.github_repo_name_edit.edit_text.strip()
        website_dir = self.osdb.get_dir('website')

        good = MD['good']
        warning = MD['warning']
        dancing_man = MD['dancing_man']
        dancing_woman = MD['dancing_woman']

        # The results
        results_text = 'Checklist:\n'

        # Validate input
        if not username or not repo_name:
            self.results_msg.set_text("Please provide your GitHub username and GitHub pages repository name.")
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
                self.results_msg.set_text(f'{warning}  SSH connection failed.\nSTDOUT: {stdout}\nSTDERR: {stderr}')
                return

        except Exception as e:
            self.results_msg.set_text(f'{warning}  SSH check failed: {str(e)}')
            return
        
        results_text += f'{good}  SSH authentication to GitHub successful\n'


        # Try to clone
        try:
            if os.path.exists(website_dir):
                # Delete the clone_path if it exists
                shutil.rmtree(website_dir)

            cmd_result = subprocess.run(
                ["git", "clone", f"git@github.com:{username}/{repo_name}.git", website_dir],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            stdout = cmd_result.stdout.decode().strip()
            stderr = cmd_result.stderr.decode().strip()

            if cmd_result.returncode != 0:
                self.results_msg.set_text(
                    f'{warning}  Failed to clone repository.\n\n{stderr}'
                )
                return
            
            # Build the deployment record
            depl = self.osdb.get_tmpl('repo')
            depl['enable'] = True
            depl['github_repo'] = repo_name
            depl['github_user'] = username
            depl['install_dir'] = website_dir
            self.osdb.add_deployment('repo', depl)
            
            results_text += f'{good}  Repository cloned successfully\n'
            results_text += f'{good}  Pre-populating static content:\n'

            # Pre-Populate the new repo with static content
            db4e_dir = self.osdb.get_dir('db4e')
            local_repo_dir = self.osdb.get_dir('website')
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
            # Run the update repo script
            if sync_result.returncode != 0:
                stderr = cmd_result.stderr.decode().strip()
                self.results_msg.set_text(
                    f'{warning}  Failed to pre-populate static content.\n\n{stderr}'
                )
                return
            # Add the script output to the results
            sync_output = sync_result.stdout.decode().strip()
            results_text += f'{sync_output}\n'
            results_text += f'{good}  Static content updated\n'

            # Remove the submit button after success and change the back to done
            self.back_button.set_label("Done")
            self.form_buttons.set_focus(0)
            self.form_buttons.contents = [
                (self.back_button, self.form_buttons.options('given', 8))
            ]
            results_text += f'{dancing_man} GitHub website repository setup successful {dancing_woman}'
            self.results_msg.set_text(results_text)

        except Exception as e:
            self.results_msg.set_text(f"Error: {str(e)}")

    def reset(self):
        # Form elements, edit widgets
        self.github_username_edit = urwid.Edit("GitHub account name (e.g. sallykolodny): ", edit_text='')
        self.github_repo_name_edit = urwid.Edit("GitHub repository name (e.g. xmr): ", edit_text='')

        # The buttons
        self.submit_button =  urwid.Button(('button', 'Submit'), on_press=self.on_submit)
        self.back_button = urwid.Button(('button', 'Back'), on_press=self.back_to_main)

        # The assembled buttons
        self.form_buttons = urwid.Columns([
            (10, self.submit_button),
            (8, self.back_button)
        ], dividechars=1)

        # The assembled form elements and buttons
        self.form_box = urwid.Pile([
            self.github_username_edit,
            self.github_repo_name_edit,
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
            urwid.Text('Enter your GitHub account name and the name of your GitHub ' + 
                       'repository\n\n' +
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
            title="GitHub Repo Setup", title_align='center', title_attr='title'
        )

    def widget(self):
        return self.frame
