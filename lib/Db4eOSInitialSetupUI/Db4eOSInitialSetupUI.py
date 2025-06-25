"""
lib/Db4eOSInitialSetupUI/Db4eOSInitialSetupUI.py

This urwid based TUI drops into the db4e-os.py TUI to help the
do the initial setup.


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
from Db4eOSStrings.Db4eOSStrings import MD

bullet = MD['bullet']
INTRO_TEXT = 'NOTE:\n'
INTRO_TEXT += f'{bullet}  The software deployment and GitHub pages website directories '
INTRO_TEXT += 'can *NOT* be within the base db4e directory.\n'
INTRO_TEXT += f'{bullet}  Do not use symbols or spaces in any of the fields.\n'
INTRO_TEXT += f'{bullet}  When you click on "Proceed" you will be prompted for your '
INTRO_TEXT += 'password. This is for "sudo" access which will allow db4e to '
INTRO_TEXT += 'do the initial setup.'

class Db4eOSInitialSetupUI:
    def __init__(self, parent_tui):
        self.parent_tui = parent_tui
        self.osdb = Db4eOSDb()
        self.ini = Db4eConfig()

        db4e_dir = self.osdb.get_dir('db4e')
        website_dir = os.path.abspath(os.path.join(db4e_dir, '..', 'website'))
        vendor_dir = os.path.abspath(os.path.join(db4e_dir, '..', 'vendor'))

        # Form widgets    
        self.db4e_group_edit = urwid.Edit("The Linux db4e group: ", edit_text='db4e')
        self.vendor_dir_edit = urwid.Edit("Software deployment directory: ", edit_text=vendor_dir)
        self.website_dir_edit = urwid.Edit("GitHub pages repository directory: ", edit_text=website_dir)
        self.wallet_edit = urwid.Edit("Enter your Monero wallet address: ", edit_text='')

        # The assembled form
        setup_form = urwid.LineBox(
            urwid.Padding(
                urwid.Pile([
                    self.db4e_group_edit,
                    self.vendor_dir_edit,
                    self.website_dir_edit,
                    self.wallet_edit,
                ]), left=2, right=2), title='Setup Form', title_align='left', title_attr='title')

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
            setup_form,
            urwid.Divider(),
            self.form_buttons,
            self.results_box
        ]

        # Wrap in a ListBox to make scrollable
        listbox = urwid.ListBox(urwid.SimpleFocusListWalker(all_widgets))
        self.frame = urwid.LineBox(
            urwid.Padding(listbox, left=2, right=2),
            title="Initial db4e Setup", title_align="center", title_attr="title"
        )

    def on_continue(self, button):
        self.parent_tui.return_to_main()

    def on_proceed(self, button):
        db4e_user = os.getlogin()
        db4e_group = self.db4e_group_edit.edit_text.strip()
        vendor_dir = self.vendor_dir_edit.edit_text.strip()
        website_dir = self.website_dir_edit.edit_text.strip()
        wallet = self.wallet_edit.edit_text.strip()

        # Validate user input
        if any(not val for val in (db4e_group, vendor_dir, website_dir, wallet)):
            self.results_msg.set_text("You must fill in *all* of the fields")
            return

        # Start assembling the results
        good = MD['good']
        warning = MD['warning']
        dancing_man = MD['dancing_man']
        dancing_woman = MD['dancing_woman']
        msg_text = 'Checklist:\n'

        # Create the vendor directory
        try:
            if os.path.exists(vendor_dir):
                os.rename(vendor_dir, vendor_dir + '.orig')
                msg_text += f'{warning}  Found existing vendor dir, backed it up as {vendor_dir}.orig\n'
            os.mkdir(vendor_dir)
        except (PermissionError, FileNotFoundError, FileExistsError) as e:
            error_msg = f'Failed to create directory ({vendor_dir}). Make sure you '
            error_msg += 'have permission to create the directory and that the parent '
            error_msg += f'exists\n\n'
            error_msg += f'{e}'
            self.results_msg.set_text(error_msg)
            return
        msg_text += f'{good}  Created software deployment directory: {vendor_dir}\n'

        # Create the website directory        
        try:
            if os.path.exists(website_dir):
                shutil.rmtree(website_dir)
            os.mkdir(website_dir)
        except (PermissionError, FileNotFoundError, FileExistsError) as e:
            error_msg = f'Failed to create directory ({website_dir}). Make sure you '
            error_msg += 'have permission to create the directory and that the parent '
            error_msg += f'exists\n\n'
            error_msg += f'{e}'
            self.results_msg.set_text(error_msg)
            return
        msg_text += f'{good}  Created GitHb pages website directory: {website_dir}\n'
        
        # Update the db4e deployment record
        self.osdb.update_deployment('db4e', {'status': 'stopped',
                                             'vendor_dir': vendor_dir,
                                             'user': db4e_user,
                                             'group': db4e_group,
                                             'user_wallet': wallet,
                                             'website_dir': website_dir})
        # Update the repo deployment record
        self.osdb.update_deployment('repo', {'status': 'stopped', 
                                             'install_dir': website_dir})

        # Additional config settings
        bin_dir              = self.ini.config['db4e']['bin_dir']
        conf_dir             = self.ini.config['db4e']['conf_dir']
        db4e_config          = self.ini.config['db4e']['config']
        db4e_version         = self.ini.config['db4e']['version']
        db4e_service_file    = self.ini.config['db4e']['service_file']
        initial_setup_script = self.ini.config['db4e']['setup_script']
        log_dir              = self.ini.config['db4e']['log_dir']
        run_dir              = self.ini.config['db4e']['run_dir']
        systemd_dir          = self.ini.config['db4e']['systemd_dir']
        tmpl_dir             = self.ini.config['db4e']['template_dir']
        tmpl_vendor_dir      = self.ini.config['db4e']['vendor_dir']
        p2pool_binary        = self.ini.config['p2pool']['process']
        p2pool_service_file  = self.ini.config['p2pool']['service_file']
        p2pool_start_script  = self.ini.config['p2pool']['start_script']
        p2pool_socket_file   = self.ini.config['p2pool']['socket_file']
        p2pool_version       = self.ini.config['p2pool']['version']
        blockchain_dir       = self.ini.config['monerod']['blockchain_dir']
        monerod_binary       = self.ini.config['monerod']['process']
        monerod_service_file = self.ini.config['monerod']['service_file']
        monerod_socket_file  = self.ini.config['monerod']['socket_file']
        monerod_start_script = self.ini.config['monerod']['start_script']
        monerod_version      = self.ini.config['monerod']['version']
        xmrig_binary         = self.ini.config['xmrig']['process']
        xmrig_service_file   = self.ini.config['xmrig']['service_file'] 
        xmrig_version        = self.ini.config['xmrig']['version']


        # db4e, P2Pool, Monero daemon and XMRig directories
        db4e_dir = self.osdb.get_dir('db4e')
        db4e_vendor_dir = 'db4e-' + str(db4e_version)
        p2pool_dir = 'p2pool-' + str(p2pool_version)
        monerod_dir = 'monerod-' + str(monerod_version)
        xmrig_dir = 'xmrig-' + str(xmrig_version)

        # Templates for the db4e, Monero daemon and P2pool services
        fq_db4e_service_file    = os.path.join(db4e_dir, tmpl_dir, systemd_dir, db4e_service_file)
        fq_p2pool_service_file  = os.path.join(db4e_dir, tmpl_dir, tmpl_vendor_dir, p2pool_dir, systemd_dir, p2pool_service_file)
        fq_p2pool_socket_file   = os.path.join(db4e_dir, tmpl_dir, tmpl_vendor_dir, p2pool_dir, systemd_dir, p2pool_socket_file)
        fq_monerod_service_file = os.path.join(db4e_dir, tmpl_dir, tmpl_vendor_dir, monerod_dir, systemd_dir, monerod_service_file)
        fq_monerod_socket_file  = os.path.join(db4e_dir, tmpl_dir, tmpl_vendor_dir, monerod_dir, systemd_dir, monerod_socket_file)
        fq_xmrig_service_file   = os.path.join(db4e_dir, tmpl_dir, tmpl_vendor_dir, xmrig_dir, systemd_dir, xmrig_service_file)

        # P2Pool, Monerod daemon, XMRig binaries and start-scripts
        fq_p2pool               = os.path.join(db4e_dir, tmpl_dir, tmpl_vendor_dir, p2pool_dir, bin_dir, p2pool_binary)
        fq_p2pool_start_script  = os.path.join(db4e_dir, tmpl_dir, tmpl_vendor_dir, p2pool_dir, bin_dir, p2pool_start_script)
        fq_monerod              = os.path.join(db4e_dir, tmpl_dir, tmpl_vendor_dir, monerod_dir, bin_dir, monerod_binary)
        fq_monerod_start_script = os.path.join(db4e_dir, tmpl_dir, tmpl_vendor_dir, monerod_dir, bin_dir, monerod_start_script)
        fq_xmrig                = os.path.join(db4e_dir, tmpl_dir, tmpl_vendor_dir, xmrig_dir, bin_dir, xmrig_binary)

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

        # Update the P2Pool service templates with deployment values
        placeholders = {
            'P2POOL_DIR': os.path.join(vendor_dir, p2pool_dir),
            'DB4E_USER': db4e_user,
            'DB4E_GROUP': db4e_group,
        }
        with open(fq_p2pool_service_file, 'r') as f:
            service_contents = f.read()
            for key, val in placeholders.items():
                service_contents = service_contents.replace(f'[[{key}]]', str(val))
        tmp_service_file = os.path.join(tmp_dir, p2pool_service_file)
        with open(tmp_service_file, 'w') as f:
            f.write(service_contents)
        with open(fq_p2pool_socket_file, 'r') as f:
            service_contents = f.read()
            for key, val in placeholders.items():
                service_contents = service_contents.replace(f'[[{key}]]', str(val))
        tmp_service_file = os.path.join(tmp_dir, p2pool_socket_file)
        with open(tmp_service_file, 'w') as f:
            f.write(service_contents)

        # Update the Monero daemon service templates with deployment values
        placeholders = {
            'MONEROD_DIR': os.path.join(vendor_dir, monerod_dir),
            'DB4E_USER': db4e_user,
            'DB4E_GROUP': db4e_group,
        }
        with open(fq_monerod_service_file, 'r') as f:
            service_contents = f.read()
            for key, val in placeholders.items():
                service_contents = service_contents.replace(f'[[{key}]]', str(val))
        tmp_service_file = os.path.join(tmp_dir, monerod_service_file)
        with open(tmp_service_file, 'w') as f:
            f.write(service_contents)
        with open(fq_monerod_socket_file, 'r') as f:
            service_contents = f.read()
            for key, val in placeholders.items():
                service_contents = service_contents.replace(f'[[{key}]]', str(val))
        tmp_service_file = os.path.join(tmp_dir, monerod_socket_file)
        with open(tmp_service_file, 'w') as f:
            f.write(service_contents)

        # Update the XMRig miner service template with deployment values
        placeholders = {
            'XMRIG_DIR': os.path.join(vendor_dir, xmrig_dir),
            'DB4E_USER': db4e_user,
            'DB4E_GROUP': db4e_group,
        }
        with open(fq_xmrig_service_file, 'r') as f:
            service_contents = f.read()
            for key, val in placeholders.items():
                service_contents = service_contents.replace(f'[[{key}]]', str(val))
        tmp_service_file = os.path.join(tmp_dir, xmrig_service_file)
        with open(tmp_service_file, 'w') as f:
            f.write(service_contents)

        # Create the vendor directories
        os.mkdir(os.path.join(vendor_dir, blockchain_dir))
        os.mkdir(os.path.join(vendor_dir, db4e_vendor_dir))
        os.mkdir(os.path.join(vendor_dir, db4e_vendor_dir, conf_dir))
        os.mkdir(os.path.join(vendor_dir, p2pool_dir))
        os.mkdir(os.path.join(vendor_dir, p2pool_dir, bin_dir))
        os.mkdir(os.path.join(vendor_dir, p2pool_dir, conf_dir))
        os.mkdir(os.path.join(vendor_dir, p2pool_dir, run_dir))
        os.mkdir(os.path.join(vendor_dir, monerod_dir))
        os.mkdir(os.path.join(vendor_dir, monerod_dir, bin_dir))
        os.mkdir(os.path.join(vendor_dir, monerod_dir, conf_dir))
        os.mkdir(os.path.join(vendor_dir, monerod_dir, run_dir))
        os.mkdir(os.path.join(vendor_dir, monerod_dir, log_dir))
        os.mkdir(os.path.join(vendor_dir, xmrig_dir))
        os.mkdir(os.path.join(vendor_dir, xmrig_dir, bin_dir))
        os.mkdir(os.path.join(vendor_dir, xmrig_dir, conf_dir))

        # db4e configuration file
        fq_db4e_config    = os.path.join(db4e_dir, conf_dir, db4e_config)
        shutil.copy(fq_db4e_config, os.path.join(vendor_dir, db4e_vendor_dir, conf_dir))
        
        # Copy in the Monero daemon, P2Pool and XMRig binaries
        shutil.copy(fq_p2pool, os.path.join(vendor_dir, p2pool_dir, bin_dir))
        shutil.copy(fq_p2pool_start_script, os.path.join(vendor_dir, p2pool_dir, bin_dir))
        shutil.copy(fq_monerod, os.path.join(vendor_dir, monerod_dir, bin_dir))
        shutil.copy(fq_monerod_start_script, os.path.join(vendor_dir, monerod_dir, bin_dir))
        shutil.copy(fq_xmrig, os.path.join(vendor_dir, xmrig_dir, bin_dir))

        # Run the bin/db4e-installer.sh
        try:
            fq_initial_setup = os.path.join(db4e_dir, bin_dir, initial_setup_script)
            cmd_result = subprocess.run(
                ['sudo', fq_initial_setup, db4e_dir, db4e_user, db4e_group, vendor_dir],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                input=b"",
                timeout=10)
            stdout = cmd_result.stdout.decode().strip()
            stderr = cmd_result.stderr.decode().strip()

            # Check the return code
            if cmd_result.returncode != 0:
                self.info_msg.set_text(f"Service install failed.\n\n{stderr}")
                return
            
            for aLine in stdout.split('\n'):
                msg_text += f"{good}  {aLine}\n"
            msg_text += f"{dancing_man} db4e setup was successful {dancing_woman}"
            self.results_msg.set_text(msg_text)
            shutil.rmtree(tmp_dir)

        except Exception as e:
            self.info_msg.set_text(f"Service install failed: {str(e)}")

        # Replace the "Quit" and "Proceed" buttons with a "Continue" button
        self.form_buttons.set_focus(0)
        self.form_buttons.contents = [
            (self.continue_button, self.form_buttons.options('given', 12))
        ]   

    def on_quit(self, button):
        raise urwid.ExitMainLoop()

    def widget(self):
        return self.frame
