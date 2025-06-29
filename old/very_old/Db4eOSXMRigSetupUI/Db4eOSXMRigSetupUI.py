"""
lib/Db4eOSXMRigSetupUI/Db4eOSXMRigSetupUI.py

This urwid based TUI drops into the db4e-os.py TUI to help the
user setup a local XMRig miner.


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

# Where the DB4E modules live
lib_dir = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(lib_dir)

# Import DB4E modules
from Db4eOSDb.Db4eOSDb import Db4eOSDb
from Db4eConfig.Db4eConfig import Db4eConfig
from Db4eOSModel.Db4eOSModel import Db4eOSModel
from Db4eOSStrings.Db4eOSStrings import MD

class Db4eOSXMRigSetupUI:
    def __init__(self, parent_tui):
        self.parent_tui = parent_tui
        self.ini = Db4eConfig()
        self.osdb = Db4eOSDb()
        self.model = Db4eOSModel()
        self.reset()

    def back_to_main(self, button):
        self.parent_tui.return_to_main()

    def build_p2pool_deployments(self, deployments):
        items = []
        for instance_name, data in sorted(deployments.items()):
            is_selected = (instance_name == self.selected_p2pool)
            radio = urwid.RadioButton(
                self.group,
                data['instance'],
                on_state_change=self.select_p2pool,
                user_data=instance_name,
                state=is_selected
            )
            self.deployment_radios.append(radio)
            items.append(urwid.Columns([
                (20, radio)
            ], dividechars=1))
        return urwid.LineBox(urwid.Padding(urwid.Pile(items), left=2, right=2), title='Select P2Pool daemon', title_align='left', title_attr='title')

    def on_submit(self, button):
        instance = self.instance_edit.edit_text.strip()
        num_threads = self.num_threads_edit.edit_text.strip()

        # Validate input
        try:
            num_threads = int(num_threads)
        except:
            self.results_msg.set_text("The number of threads must be an integer value")
            return
        
        if self.osdb.get_deployment_by_instance('xmrig', instance):
            self.results_msg.set_text(f"The instance name ({instance}) is already being used. " +
                                      "There can be only one XMRig deployment with that " +
                                      "instance name.")
            return

        ### Generate a XMRig configuration file
        conf_dir        = self.ini.config['db4e']['conf_dir']
        tmpl_dir        = self.ini.config['db4e']['template_dir']
        tmpl_vendor_dir = self.ini.config['db4e']['vendor_dir']
        config          = self.ini.config['xmrig']['config']
        version         = self.ini.config['xmrig']['version']
        xmrig_dir = 'xmrig-' + str(version)
        db4e_dir = self.osdb.get_dir('db4e')
        vendor_dir = self.osdb.get_dir('vendor')
        tmpl_config = os.path.join(db4e_dir, tmpl_dir, tmpl_vendor_dir, xmrig_dir, conf_dir, config)
        fq_config = os.path.join(vendor_dir, xmrig_dir, conf_dir, instance + '.json')
        # The XMRig deploymet has references to the upstream P2Pool deployment
        p2pool_rec = self.osdb.get_deployment_by_instance('p2pool', self.selected_p2pool)
        p2pool_id = p2pool_rec['_id']
        url_entry = p2pool_rec['ip_addr'] + ':' + str(p2pool_rec['stratum_port'])
        # Populate the config templace placeholders
        placeholders = {
            'MINER_NAME': instance,
            'NUM_THREADS': ','.join(['-1'] * num_threads),
            'URL': url_entry
        }
        with open(tmpl_config, 'r') as f:
            config_contents = f.read()
            for key, val in placeholders.items():
                config_contents = config_contents.replace(f'[[{key}]]', str(val))
        with open(fq_config, 'w') as f:
            f.write(config_contents)

        # Create a new deployment record
        depl = self.osdb.get_tmpl('xmrig')
        depl['config'] = fq_config
        depl['enable'] = True
        depl['instance'] = instance
        depl['num_threads'] = int(num_threads)
        depl['p2pool_id'] = p2pool_id
        self.osdb.new_deployment('xmrig', depl)

        self.parent_tui.return_to_main()

    def reset(self):
        # Form elements; edit widgets
        self.instance_edit = urwid.Edit("XMRig miner name (e.g. sally): ", edit_text='')
        self.num_threads_edit = urwid.Edit("CPU threads: ", edit_text='')

        # The buttons
        self.submit_button = urwid.Button(('button', 'Submit'), on_press=self.on_submit)
        self.back_button = urwid.Button(('button', 'Back'), on_press=self.back_to_main)

        # The assembled buttons
        self.form_buttons = urwid.Columns([
            (10, self.submit_button),
            (8, self.back_button)
        ], dividechars=1)

        # Setup the reference to the P2Pool instance XMRig will use
        self.selected_p2pool = None
        self.deployment_radios = []
        self.group = []
        p2pool_deployments = {}
        for deployment in self.osdb.get_deployments_by_component('p2pool'):
            name = deployment['name']
            instance = deployment['instance']
            p2pool_deployments[instance] = { 'name': name, 'instance': instance }
            self.selected_p2pool = instance # Initialize to the last instance
        p2pool_deployments_box = self.build_p2pool_deployments(p2pool_deployments)

        # The assembled form elements and buttons
        self.form_box = urwid.Pile([
            self.instance_edit,
            self.num_threads_edit,
            urwid.Divider(),
            p2pool_deployments_box,
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
                'many CPU threads to allocate to the miner. It is recommended ' +
                'that you leave at least one thread free for the OS.\n\n ' +
                'Use the arrow keys or mouse scrollwheel to scroll up and ' +
                'down and the spacebar to click.'),
            urwid.Divider(),
            urwid.LineBox(
                urwid.Padding(self.form_box, left=2, right=2),
                title='Setup Form', title_align='left', title_attr='title'),
            self.results_box
        ]

        # Wrap in a ListBox to make scrollable
        listbox = urwid.ListBox(urwid.SimpleFocusListWalker(form_widgets))
        self.frame = urwid.LineBox(
            urwid.Padding(listbox, left=2, right=2),
            title='XMRig Miner Setup', title_align='center', title_attr='title'
        )

    def select_p2pool(self, radio, new_state, deployment):
        if new_state:
            self.selected_p2pool = deployment

    def widget(self):
        return self.frame
