"""
lib/Infrastructure/Db4eOSMonerodRemoteSetupUI/Db4eOSMonerodRemoteSetupUI.py

This urwid based TUI drops into the db4e-os.py TUI to help the
user configure access to a Monero blockchain daemon running on a
remote node.
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


class Db4eOSMonerodRemoteSetupUI:
    def __init__(self, parent_tui):
        self.parent_tui = parent_tui
        self._db = Db4eOSDb()
        monerod_rec = self._db.get_monerod_tmpl()
        # MONERO_NODE="192.168.0.176"
        # ZMQ_PORT=20083
        # RPC_PORT=20081
        instance = monerod_rec['instance'] or ''
        ip_addr = monerod_rec['ip_addr'] or ''
        zmq_port = monerod_rec['zmq_pub_port'] or ''
        rpc_port = monerod_rec['rpc_bind_port'] or ''
        self.instance_edit = urwid.Edit("Monero instance name: ", edit_text=instance)
        self.ip_addr_edit = urwid.Edit("Remote node IP addrss: ", edit_text=ip_addr)
        self.zmq_port_edit = urwid.Edit("ZMQ port: ", edit_text=zmq_port)
        self.rpc_port_edit = urwid.Edit("RPC port: ", edit_text=rpc_port)

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
            urwid.Text('Remote Monero Blockchain Daemon Setup\n\n' +
                'All of the fields below are mandatory. Furthermore ' +
                'the \"instance name\" must be unique within the ' +
                'db4e environment i.e. if you have more than one ' +
                'daemon deployed, then each must have their own ' +
                'instance name.\n\nUse the arrow keys or mouse scrollwheel ' +
                'to scroll up and down.'),
            urwid.Divider(),
            urwid.LineBox(
                urwid.Padding(
                    urwid.Pile([
                        self.instance_edit,
                        self.ip_addr_edit,
                        self.zmq_port_edit,
                        self.rpc_port_edit,
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
                self.info_msg.set_text(f"SSH connection failed.\nSTDOUT: {stdout}\nSTDERR: {stderr}")
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
