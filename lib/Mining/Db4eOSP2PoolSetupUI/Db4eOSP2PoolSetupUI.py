"""
lib/Infrastructure/Db4eOSP2PoolRemoteSetupUI/Db4eOSP2PoolSetupUI.py

This urwid based TUI drops into the db4e-os.py TUI to help the
user configure access to a local P2Pool daemon running on your 
machine. The db4e project includes a pre-compiled P2Pool binary.
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

# Where the DB4E modules live
lib_dir = os.path.dirname(__file__) + "/../../"
# Import DB4E modules
db4e_dirs = [
    lib_dir + 'Infrastructure',
    lib_dir + 'Mining'
]
for db4e_dir in db4e_dirs:
    sys.path.append(db4e_dir)

from Db4eConfig.Db4eConfig import Db4eConfig
from Db4eOS.Db4eOS import Db4eOS
from Db4eOSDb.Db4eOSDb import Db4eOSDb

# TODO Put into a strings class
MD = {
    'bullet'  : '🔸',
    'warning' : '⚠️',
}

class Db4eOSP2PoolSetupUI:
    def __init__(self, parent_tui):
        self.parent_tui = parent_tui
        self._os = Db4eOS()
        self._db = Db4eOSDb()
        self.ini = Db4eConfig()

        p2pool_rec = self._db.get_tmpl(component='p2pool', remote=False)

        instance = p2pool_rec['instance'] or ''
        wallet = p2pool_rec['wallet'] or ''
        any_ip = p2pool_rec['any_ip'] or ''
        stratum_port = p2pool_rec['stratum_port'] or ''
        p2p_port = p2pool_rec['p2p_port'] or ''
        log_level = p2pool_rec['log_level'] or ''
        in_peers = p2pool_rec['in_peers'] or ''
        out_peers = p2pool_rec['out_peers'] or ''

        # Form elements; edit widgets
        self.instance_edit = urwid.Edit("P2Pool instance name (e.g. Primary): ", edit_text=instance)
        self.wallet_edit = urwid.Edit("Your Monero wallet (e.g. 48aTDJfRH...QHwao4j): ", edit_text=wallet)
        self.any_ip_edit = urwid.Edit("Listen on IP address: ", edit_text=any_ip)
        self.stratum_port_edit = urwid.Edit("Stratum port: ", edit_text=str(stratum_port))
        self.p2p_port_edit = urwid.Edit("P2P port: ", edit_text=str(p2p_port))
        self.log_level_edit = urwid.Edit("P2Pool log level: ", edit_text=str(log_level))
        self.in_peers_edit = urwid.Edit("Number of allowed incoming connections: ", edit_text=str(in_peers))
        self.out_peers_edit = urwid.Edit("Number of allowed outbound connections: ", edit_text=str(out_peers))

        # The buttons
        self.submit_button = urwid.Button(('button', 'Submit'), on_press=self.on_submit)
        self.back_button = urwid.Button(('button', 'Back'), on_press=self.back_to_main)

        # The assembled buttons
        self.form_buttons = urwid.Columns([
            (10, self.submit_button),
            (8, self.back_button)
        ], dividechars=1)

        # Setup the reference to the P2Pool instance XMRig will use
        self.selected_monerod = None
        self.deployment_radios = []
        self.group = []
        monerod_deployments = {}
        for deployment in self._db.get_monerod_deployments():
            name = deployment['name']
            instance = deployment['instance']
            monerod_deployments[instance] = { 'name': name, 'instance': instance }
            self.selected_monerod = instance # Initialize to the last instance
        monerod_deployments_box = self.build_monerod_deployments(monerod_deployments)

        # The assembled form elements and buttons
        self.form_box = urwid.Pile([
            self.instance_edit,
            self.wallet_edit,
            self.any_ip_edit,
            self.stratum_port_edit,
            self.p2p_port_edit,
            self.log_level_edit,
            self.in_peers_edit,
            self.out_peers_edit,
            urwid.Divider(),
            monerod_deployments_box,
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
            urwid.Text('Remote P2Pool Demon Setup\n\n' +
                'The \"instance name\" must be unique within the ' +
                'db4e environment i.e. if you have more than one ' +
                'daemon deployed, then each must have their own ' +
                'instance name. Setting the listen on IP to \"0.0.0.0\" "'
                'will configure P2Pool to listen on all of your network ' +
                'interfaces (you likely want this).\n\nUse the arrow ' +
                'keys or mouse scrollwheel to scroll up and down and ' +
                'the spacebar to click.'),
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
            title="Remote P2Pool Daemon Setup", title_align="center", title_attr="title"
        )

    def back_to_main(self, button):
        self.parent_tui.return_to_main()

    def build_monerod_deployments(self, deployments):
        items = []
        for instance_name, data in sorted(deployments.items()):
            is_selected = (instance_name == self.selected_monerod)
            radio = urwid.RadioButton(
                self.group,
                data['instance'],
                on_state_change=self.select_monerod,
                user_data=instance_name,
                state=is_selected
            )
            self.deployment_radios.append(radio)
            items.append(urwid.Columns([
                (20, radio)
            ], dividechars=1))
        return urwid.LineBox(urwid.Padding(urwid.Pile(items), left=2, right=2), title='Select Monero daemon', title_align='left', title_attr='title')

    def on_submit(self, button):
        instance = self.instance_edit.edit_text.strip()
        wallet = self.wallet_edit.edit_text.strip()
        any_ip = self.any_ip_edit.edit_text.strip()
        stratum_port = self.stratum_port_edit.edit_text.strip()
        p2p_port = self.p2p_port_edit.edit_text.strip()
        log_level = self.log_level_edit.edit_text.strip()
        in_peers = self.in_peers_edit.edit_text.strip()
        out_peers = self.out_peers_edit.edit_text.strip()

        # Validate input
        if any(not val for val in (instance, wallet, any_ip, stratum_port, p2p_port,
                                   log_level, in_peers, out_peers)):
            self.results_msg.set_text("You must fill in *all* of the fields")
            return
        
        try:
            stratum_port = int(stratum_port)
            p2p_port = int(p2p_port)
            log_level = int(log_level)
            in_peers = int(in_peers)
            out_peers = int(out_peers)
        except:
            self.results_msg.set_text("The stratum port, p2p port, log level, incoming and " +
                                      "outgoing connections must have integer values")

        if self._db.get_deployment_by_instance('p2pool', instance):
            self.results_msg.set_text(f"The instance name ({instance}) is already being used. " +
                                      "There can be only one P2Pool daemon deployment with that " +
                                      "instance name.")
            return

        # Generate a P2Pool configuration file
        conf_dir        = self.ini.config['db4e']['conf_dir']
        tmpl_dir        = self.ini.config['db4e']['template_dir']
        third_party_dir = self.ini.config['db4e']['third_party_dir']
        version         = self.ini.config['p2pool']['version']
        config          = self.ini.config['p2pool']['config']
        p2pool_dir = 'p2pool-' + str(version)
        db4e_dir = self._db.get_db4e_dir()
        vendor_dir = self._db.get_vendor_dir()
        tmpl_config = os.path.join(db4e_dir, tmpl_dir, third_party_dir, p2pool_dir, conf_dir, config)
        fq_config = os.path.join(vendor_dir, p2pool_dir, conf_dir, instance + '.ini')
        # Make sure the directories exist
        if not os.path.exists(os.path.join(vendor_dir, p2pool_dir)):
            os.mkdir(os.path.join(vendor_dir, p2pool_dir))
        if not os.path.exists(os.path.join(vendor_dir, p2pool_dir, conf_dir)):
            os.mkdir(os.path.join(vendor_dir, p2pool_dir, conf_dir))
        with open(tmpl_config, 'r') as f:
            config_contents = f.read()

        # P2Pool deployments point at a Monero daemon deployment. We need the
        # Monero daemon hostname/IP, ZMQ and RPC ports for P2Pool.
        monerod_rec = self._db.get_deployment_by_instance('monerod', self.selected_monerod)
        monerod_ip_addr = monerod_rec['ip_addr']
        monerod_zmq_port = monerod_rec['zmq_pub_port']
        monerod_rpc_port = monerod_rec['rpc_bind_port']
        # Populate the config template placeholders
        config_contents = config_contents.replace('[[MONEROD_IP]]', monerod_ip_addr)
        config_contents = config_contents.replace('[[ZMQ_PORT]]', str(monerod_zmq_port))
        config_contents = config_contents.replace('[[RPC_PORT]]', str(monerod_rpc_port))
        config_contents = config_contents.replace('[[ANY_IP]]', any_ip)
        config_contents = config_contents.replace('[[STRATUM_PORT]]', str(stratum_port))
        config_contents = config_contents.replace('[[P2P_PORT]]', str(p2p_port))
        config_contents = config_contents.replace('[[LOG_LEVEL]]', str(log_level))
        config_contents = config_contents.replace('[[IN_PEERS]]', str(in_peers))
        config_contents = config_contents.replace('[[OUT_PEERS]]', str(out_peers))

        with open(fq_config, 'w') as f:
            f.write(config_contents)

        monerod_id = monerod_rec['_id']
        self._db.new_deployment('p2pool', { 
            'status': 'running',
            'instance': instance,
            'wallet': wallet,
            'config': fq_config,
            'any_ip': any_ip,
            'stratum_port': stratum_port,
            'p2p_port': p2p_port,
            'log_level': log_level,
            'in_peers': in_peers,
            'out_peers': out_peers,
            'monerod_id': monerod_id,
            'remote': False
            })

        # Set the results
        results = f'Created new P2Pool daemon ({instance}) deployment record. '
        self.results_msg.set_text(results)

        # Remove the submit button
        self.form_buttons.contents = [
            (self.back_button, self.form_buttons.options('given', 8))
        ]

    def select_monerod(self, radio, new_state, deployment):
        if new_state:
            self.selected_monerod = deployment

    def widget(self):
        return self.frame
