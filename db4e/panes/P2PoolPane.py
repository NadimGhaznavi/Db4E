# db4e/Panes/P2PoolPane.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0


from textual.containers import Container, ScrollableContainer, Vertical, Horizontal
from textual.widgets import Label, Input, Button, RadioButton, RadioSet
from textual.reactive import reactive

from db4e.messages.Db4EMsg import Db4EMsg
from db4e.recs.monero.BaseP2Pool import CHAIN_TO_CHAIN_LABEL_MAP
from db4e.recs.monero.P2Pool import P2Pool
from db4e.util.Helper import gen_results_table
from db4e.constants.DElem import DElem
from db4e.constants.DField import DField
from db4e.constants.DModule import DModule
from db4e.constants.DMethod import DMethod
from db4e.constants.DLabel import DLabel
from db4e.constants.DButton import DButtonF, DButtonL
from db4e.constants.DForm import DForm


class P2PoolPane(Container):
    """Textual pane for P2PoolPane."""

    radio_button_list = reactive([], always_update=True)
    instance_map = {}
    p2pool = None

    def compose(self):
        """Compose the pane layout.

        :return: Yielded child widgets for this pane.
        :rtype: ComposeResult
        """
        yield Vertical(
            ScrollableContainer(
                Label("", classes=DForm.INTRO, id=DForm.INTRO),
                Vertical(
                    Horizontal(
                        Label(DLabel.INSTANCE, classes=DForm.FORM_LABEL),
                        Input(
                            id=DForm.INSTANCE_INPUT,
                            restrict=f"[a-zA-Z0-9_\-]*",
                            compact=True,
                            classes=DForm.INPUT_30,
                        ),
                        Label("", classes=DForm.STATIC, id=DForm.INSTANCE_LABEL),
                    ),
                    Horizontal(
                        Label(DLabel.IN_PEERS, classes=DForm.FORM_LABEL),
                        Input(
                            id=DForm.IN_PEERS_INPUT,
                            restrict=f"[0-9]*",
                            compact=True,
                            classes=DForm.INPUT_30,
                        ),
                    ),
                    Horizontal(
                        Label(DLabel.OUT_PEERS, classes=DForm.FORM_LABEL),
                        Input(
                            id=DForm.OUT_PEERS_INPUT,
                            restrict=f"[0-9]*",
                            compact=True,
                            classes=DForm.INPUT_30,
                        ),
                    ),
                    Horizontal(
                        Label(DLabel.P2P_PORT, classes=DForm.FORM_LABEL),
                        Input(
                            id=DForm.P2P_PORT_INPUT,
                            restrict=f"[0-9]*",
                            compact=True,
                            classes=DForm.INPUT_30,
                        ),
                    ),
                    Horizontal(
                        Label(DLabel.STRATUM_PORT, classes=DForm.FORM_LABEL),
                        Input(
                            id=DForm.STRATUM_PORT_INPUT,
                            restrict=f"[0-9]*",
                            compact=True,
                            classes=DForm.INPUT_30,
                        ),
                    ),
                    Horizontal(
                        Label(DLabel.LOG_LEVEL, classes=DForm.FORM_LABEL),
                        Input(
                            id=DForm.LOG_LEVEL_INPUT,
                            restrict=f"[0-9]*",
                            compact=True,
                            classes=DForm.INPUT_30,
                        ),
                    ),
                    Horizontal(
                        Label(DLabel.CONFIG_FILE, classes=DForm.FORM_LABEL),
                        Label("", classes=DForm.STATIC, id=DForm.CONFIG_LABEL),
                    ),
                    id=DForm.FORM_BOX,
                    classes=DForm.FORM_7,
                ),
                RadioSet(id=DForm.CHAIN_RADIO_SET, classes=DForm.RADIO_SET),
                RadioSet(id=DForm.RADIO_SET, classes=DForm.RADIO_SET),
                Vertical(
                    Label("", id=DForm.HEALTH_LABEL),
                    id=DForm.HEALTH_BOX,
                    classes=DForm.HEALTH_BOX,
                ),
                Vertical(
                    Horizontal(
                        Button(DButtonL.HASHRATE, id=DButtonF.HASHRATE),
                        Button(DButtonL.SHARES_FOUND, id=DButtonF.SHARES_FOUND),
                        Button(DButtonL.NEW, id=DButtonF.NEW),
                        Button(DButtonL.TABLES, id=DButtonF.TABLES),
                        Button(DButtonL.UPDATE, id=DButtonF.UPDATE),
                        Button(DButtonL.START, id=DButtonF.ENABLE),
                        Button(DButtonL.VIEW_LOG, id=DButtonF.VIEW_LOG),
                        Button(DButtonL.STOP, id=DButtonF.DISABLE),
                        Button(DButtonL.DELETE, id=DButtonF.DELETE),
                        classes=DForm.BUTTON_ROW,
                    )
                ),
            ),
            classes=DForm.PANE_BOX,
        )

    def on_mount(self):
        """Handle the mount lifecycle event.

        :return: None
        :rtype: None
        """
        self.query_one(f"#{DForm.RADIO_SET}", RadioSet).border_subtitle = (
            DLabel.UPSTREAM_MONERO
        )
        self.query_one(f"#{DForm.CHAIN_RADIO_SET}", RadioSet).border_subtitle = (
            DLabel.CHAIN
        )
        self.query_one(f"#{DForm.FORM_BOX}", Vertical).border_subtitle = DLabel.CONFIG
        self.query_one(f"#{DForm.HEALTH_BOX}", Vertical).border_subtitle = DLabel.STATUS

    def set_data(self, p2pool: P2Pool):
        """Set the data for the pane.

        :param p2pool: P2Pool deployment object.
        :type p2pool: P2Pool
        :return: None
        :rtype: None
        """
        self.p2pool = p2pool

        # Populate inputs and labels
        self.query_one(f"#{DForm.INSTANCE_INPUT}", Input).value = p2pool.instance()
        self.query_one(f"#{DForm.INSTANCE_LABEL}", Label).update(p2pool.instance())
        self.query_one(f"#{DForm.CONFIG_LABEL}", Label).update(p2pool.config_file())
        self.query_one(f"#{DForm.IN_PEERS_INPUT}", Input).value = str(p2pool.in_peers())
        self.query_one(f"#{DForm.OUT_PEERS_INPUT}", Input).value = str(
            p2pool.out_peers()
        )
        self.query_one(f"#{DForm.P2P_PORT_INPUT}", Input).value = str(p2pool.p2p_port())
        self.query_one(f"#{DForm.STRATUM_PORT_INPUT}", Input).value = str(
            p2pool.stratum_port()
        )
        self.query_one(f"#{DForm.LOG_LEVEL_INPUT}", Input).value = str(
            p2pool.log_level()
        )

        # Monerod radio buttons
        self.instance_map = p2pool.instance_map()
        self.radio_button_list = list(self.instance_map.keys())

        chain_radio_set = self.query_one(f"#{DForm.CHAIN_RADIO_SET}", RadioSet)
        for child in list(chain_radio_set.children):
            child.remove()

        for chain in CHAIN_TO_CHAIN_LABEL_MAP.keys():
            rb = RadioButton(
                CHAIN_TO_CHAIN_LABEL_MAP[chain], classes=DForm.RADIO_BUTTON_TYPE
            )
            if p2pool.chain() == chain:
                rb.value = True
            chain_radio_set.mount(rb)

        # Configure buttons visibility
        intro_text = f"Configure settings for a new {DLabel.P2POOL} deployment."
        if p2pool.instance():
            intro_text = f"Configure settings for the [b]{p2pool.instance()} {DLabel.P2POOL}[/] deployment."
            self.remove_class(DField.NEW)
            self.add_class(DField.UPDATE)

            if p2pool.enabled():
                self.remove_class(DField.DISABLED)
                self.add_class(DField.ENABLED)
            else:
                self.remove_class(DField.ENABLED)
                self.add_class(DField.DISABLED)
        else:
            self.remove_class(DField.UPDATE)
            self.add_class(DField.NEW)

        self.query_one(f"#{DForm.INTRO}", Label).update(intro_text)
        self.query_one(f"#{DForm.HEALTH_LABEL}", Label).update(
            gen_results_table(p2pool.pop_msgs())
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button pressed events.

        :param event: Event payload.
        :type event: Button.Pressed
        :return: None
        :rtype: None
        """
        button_id = event.button.id

        radio_set = self.query_one(f"#{DForm.RADIO_SET}", RadioSet)
        monerod_instance = None
        monerod_id = None
        # if radio_set.pressed_button:
        monerod_instance = str(radio_set.pressed_button.label)
        monerod_id, remote_flag = self.instance_map[monerod_instance]
        print(
            f"P2PoolPane:on_button_pressed(): monerod_id: {monerod_id}, remote_flag: {remote_flag}"
        )
        self.p2pool.parent(monerod_id)
        self.p2pool.parent_remote(remote_flag)

        chain_radio_set = self.query_one(f"#{DForm.CHAIN_RADIO_SET}", RadioSet)
        chain_label = (
            chain_radio_set.pressed_button.label
            if chain_radio_set.pressed_button
            else None
        )

        selected_chain = ""
        for aChain in CHAIN_TO_CHAIN_LABEL_MAP.keys():
            if CHAIN_TO_CHAIN_LABEL_MAP[aChain] == chain_label:
                selected_chain = aChain

        # Update p2pool object
        self.p2pool.chain(selected_chain)
        self.p2pool.instance(self.query_one(f"#{DForm.INSTANCE_INPUT}", Input).value)
        self.p2pool.in_peers(self.query_one(f"#{DForm.IN_PEERS_INPUT}", Input).value)
        self.p2pool.out_peers(self.query_one(f"#{DForm.OUT_PEERS_INPUT}", Input).value)
        self.p2pool.p2p_port(self.query_one(f"#{DForm.P2P_PORT_INPUT}", Input).value)
        self.p2pool.stratum_port(
            self.query_one(f"#{DForm.STRATUM_PORT_INPUT}", Input).value
        )
        self.p2pool.log_level(self.query_one(f"#{DForm.LOG_LEVEL_INPUT}", Input).value)

        # Map button to action
        button_map = {
            DButtonF.DELETE: (DModule.SYNC_CLIENT, DMethod.DELETE_DEPLOYMENT),
            DButtonF.DISABLE: (DModule.DEPLOYMENT_CLIENT, DMethod.DISABLE_DEPLOYMENT),
            DButtonF.ENABLE: (DModule.DEPLOYMENT_CLIENT, DMethod.ENABLE_DEPLOYMENT),
            DButtonF.HASHRATE: (DModule.OPS_MGR, DMethod.HASHRATES),
            DButtonF.NEW: (DModule.SYNC_CLIENT, DMethod.ADD_DEPLOYMENT),
            DButtonF.SHARES_FOUND: (DModule.OPS_MGR, DMethod.SHARES_FOUND),
            DButtonF.TABLES: (DModule.OPS_MGR, DMethod.GET_TABLE_DATA),
            DButtonF.UPDATE: (DModule.SYNC_CLIENT, DMethod.UPDATE_DEPLOYMENT),
            DButtonF.VIEW_LOG: (DModule.OPS_MGR, DMethod.LOG_VIEWER),
        }

        if button_id not in button_map:
            raise ValueError(f"No handler for button {button_id}")

        module, method = button_map[button_id]
        form_data = {
            DField.TO_MODULE: module,
            DField.TO_METHOD: method,
            DField.ELEMENT_TYPE: DElem.P2POOL,
            DField.ELEMENT: self.p2pool,
        }

        if button_id == DButtonF.VIEW_LOG:
            form_data[DField.INSTANCE] = self.p2pool.instance()

        self.app.post_message(Db4eMsg(self, form_data=form_data))

    def watch_radio_button_list(self, old, new):
        """React to changes in radio button list.

        :param old: Previous value.
        :type old: list
        :param new: New value.
        :type new: list
        :return: None
        :rtype: None
        """
        radio_set = self.query_one(f"#{DForm.RADIO_SET}", RadioSet)
        for child in list(radio_set.children):
            child.remove()

        ## Get the current P2Pool values
        parent_id = None
        remote_flag = None
        if self.p2pool:
            # id value from the monerod or monerod_remote table (or -1 if currently disabled)
            parent_id = self.p2pool.parent()
            # if it's 1, then it's the monerod_remote table, 0 it's the monerod table, -1 disabled
            remote_flag = self.p2pool.parent_remote()

        for instance in self.radio_button_list:
            rb = RadioButton(instance, classes=DForm.RADIO_BUTTON_TYPE)
            cur_parent_id, cur_remote_flag = self.instance_map[instance]
            if parent_id == cur_parent_id and remote_flag == cur_remote_flag:
                rb.value = True
            radio_set.mount(rb)
