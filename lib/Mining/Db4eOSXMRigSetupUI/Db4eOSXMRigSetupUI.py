"""
lib/Infrastructure/Db4eOSXMRigSetupUI/Db4eOSXMRigSetupUI.py

This urwid based TUI drops into the db4e-os.py TUI to help the
user setup a local XMRig miner.
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

from Db4eOS.Db4eOS import Db4eOS
from Db4eOSDb.Db4eOSDb import Db4eOSDb
from Db4eConfig.Db4eConfig import Db4eConfig

class Db4eOSXMRigSetupUI:
    def __init__(self, parent_tui):
        self.parent_tui = parent_tui
        self.ini = Db4eConfig()
        self._os = Db4eOS()
        self._db = Db4eOSDb()
        xmrig_rec = self._db.get_xmrig_tmpl()
        instance = xmrig_rec['instance'] or ''
        p2pool_host = xmrig_rec['p2pool_host'] or ''
        stratum_port = xmrig_rec['stratum_port'] or ''
        num_threads = xmrig_rec['num_threads'] or ''
        self.instance_edit = urwid.Edit("XMRig miner name (e.g. sally): ", edit_text=instance)
        self.p2pool_host_edit = urwid.Edit("P2Pool hostname or IP address: ", edit_text=p2pool_host)
        self.stratum_port_edit = urwid.Edit("Stratum port: ", edit_text=str(stratum_port))
        self.num_threads_edit = urwid.Edit("CPU threads: ", edit_text=str(num_threads))
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
            urwid.Text('XMRig Miner Setup\n\n' +
                'All of the fields below are mandatory. Furthermore ' +
                'the \"miner name\" must be unique within the ' +
                'db4e environment i.e. if you have more than one ' +
                'miner deployed, then each must have their own ' +
                'unique name. The \"CPU threads\" setting determines how ' +
                'many CPU threads to allocate to the miner. It iss recommended ' +
                'that you leave at least one thread free for the OS.\n\n ' +
                'Use the arrow keys or mouse scrollwheel to scroll up and down.'),
            urwid.Divider(),
            urwid.LineBox(
                urwid.Padding(
                    urwid.Pile([
                        self.instance_edit,
                        self.p2pool_host_edit,
                        self.stratum_port_edit,
                        self.num_threads_edit,
                        urwid.Divider(),
                        urwid.Columns([
                            ('pack', urwid.Button(('button', 'Submit'), on_press=self.on_submit)),
                            ('pack', urwid.Button(('button', 'Back'), on_press=self.back_to_main))
                        ], dividechars=1)
                    ]), left=2, right=2),
                title='Setup Form', title_align='left', title_attr='title'
            ),
            self.info_text
        ]

        # Wrap in a ListBox to make scrollable
        listbox = urwid.ListBox(urwid.SimpleFocusListWalker(form_widgets))
        self.frame = urwid.LineBox(
            urwid.Padding(listbox, left=2, right=2),
            title="XMRig Miner Setup", title_align="center", title_attr="title"
        )

    def back_to_main(self, button):
        self.parent_tui.return_to_main()

    def on_submit(self, button):
        instance = self.instance_edit.edit_text.strip()
        p2pool_host = self.p2pool_host_edit.edit_text.strip()
        stratum_port = self.stratum_port_edit.edit_text.strip()
        num_threads = self.num_threads_edit.edit_text.strip()

        # Validate input
        if not instance or not p2pool_host or not stratum_port and num_threads:
            self.info_msg.set_text("Please fill in *all* of the fields.")
            return
        # TODO Put this in a try/except block
        stratum_port = int(stratum_port)
        num_threads = int(num_threads)
        # TODO check that the miner name is unique
        # TODO check that a P2pool deployment exists. Have the P2Pool deployments
        # show as a drop down i.e. so XMRig "chooses" a P2Pool deployment.
        # TODO support multiple P2Pools (xmrig does that) for a xmrig deployment

        # Cannot connect warnings
        results = 'Checklist:\n\n'
        # Check that db4e can connect to the remote system
        if self._os.is_port_open(p2pool_host, stratum_port):
            results += f'* Connected to stratum port ({stratum_port}) on remote machine ({p2pool_host})\n'
        else:
            results += f"* WARNING: Unable to connect to stratum port ({stratum_port}) on remote machine ({p2pool_host})\n"

        # Generate a XMRig configuration file
        conf_dir        = self.ini.config['db4e']['conf_dir']
        tmpl_dir        = self.ini.config['db4e']['template_dir']
        third_party_dir = self.ini.config['db4e']['third_party_dir']
        config          = self.ini.config['xmrig']['config']
        version         = self.ini.config['xmrig']['version']
        xmrig_dir = 'xmrig-' + version
        db4e_dir = self._db.get_db4e_dir()
        tmpl_config = os.path.join(db4e_dir, tmpl_dir, third_party_dir, xmrig_dir, conf_dir, instance.replace(' ', '-') + '.ini')
        fq_config = os.path.join(db4e_dir, third_party_dir, xmrig_dir, conf_dir, instance
        with open(tmpl_config, 'r') as f:
            config_contents = f.read()
        # Populate the config template placeholders
        config_contents = config_contents.replace('[[MINER_NAME]]', instance)
        num_threads_entry = ','.join(['-1'] * num_threads)
        config_contents = config_contents.replace('[[NUM_THREADS]]', num_threads_entry)
        url_entry = p2pool_host + ':' + str(stratum_port)
        config_contents = config_contents.replace('[[URL]]', url_entry)
        with open(fq_config, 'w') as f:
            f.write(config_contents)

        self._db.update_deployment('xmrig', { 
            'status': 'stopped',
            'component': 'xmrig',
            'instance': instance,
            'doc_type': 'template'
            }, instance)
        results += f'\nCreated new XMRig daemon ({instance}) deployment record. '
        self.info_msg.set_text(results)

    def widget(self):
        return self.frame
