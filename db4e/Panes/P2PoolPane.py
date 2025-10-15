"""
db4e/Panes/P2PoolPane.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from textual.containers import Container, ScrollableContainer, Vertical, Horizontal
from textual.widgets import Label, Input, Button, RadioButton, RadioSet
from textual.reactive import reactive

from db4e.Messages.Db4eMsg import Db4eMsg
from db4e.Modules.P2Pool import P2Pool
from db4e.Modules.Helper import gen_results_table
from db4e.Constants.DElem import DElem
from db4e.Constants.DField import DField
from db4e.Constants.DModule import DModule
from db4e.Constants.DMethod import DMethod
from db4e.Constants.DLabel import DLabel
from db4e.Constants.DButton import DButton
from db4e.Constants.DForm import DForm


class P2PoolPane(Container):

    radio_button_list = reactive([], always_update=True)
    instance_map = {}
    p2pool = None

    def compose(self):
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
                        Button(DLabel.HASHRATE, id=DButton.HASHRATE),
                        Button(DLabel.SHARES_FOUND, id=DButton.SHARES_FOUND),
                        Button(DLabel.NEW, id=DButton.NEW),
                        Button(DLabel.TABLES, id=DButton.TABLES),
                        Button(DLabel.UPDATE, id=DButton.UPDATE),
                        Button(DLabel.START, id=DButton.ENABLE),
                        Button(DLabel.VIEW_LOG, id=DButton.VIEW_LOG),
                        Button(DLabel.STOP, id=DButton.DISABLE),
                        Button(DLabel.DELETE, id=DButton.DELETE),
                        classes=DForm.BUTTON_ROW,
                    )
                ),
            ),
            classes=DForm.PANE_BOX,
        )

    def on_mount(self):
        self.query_one(f"#{DForm.RADIO_SET}", RadioSet).border_subtitle = (
            DLabel.UPSTREAM_MONERO
        )
        self.query_one(f"#{DForm.CHAIN_RADIO_SET}", RadioSet).border_subtitle = (
            DLabel.CHAIN
        )
        self.query_one(f"#{DForm.FORM_BOX}", Vertical).border_subtitle = DLabel.CONFIG
        self.query_one(f"#{DForm.HEALTH_BOX}", Vertical).border_subtitle = DLabel.STATUS

    def set_data(self, p2pool: P2Pool):
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

        # Chain radio buttons
        chain_radio_set = self.query_one(f"#{DForm.CHAIN_RADIO_SET}", RadioSet)
        for child in list(chain_radio_set.children):
            child.remove()
        for chain in [DField.MAIN_CHAIN, DField.MINI_CHAIN, DField.NANO_CHAIN]:
            rb = RadioButton(chain, classes=DForm.RADIO_BUTTON_TYPE)
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
                self.remove_class(DField.DISABLE)
                self.add_class(DField.ENABLE)
            else:
                self.remove_class(DField.ENABLE)
                self.add_class(DField.DISABLE)
        else:
            self.remove_class(DField.UPDATE)
            self.add_class(DField.NEW)

        self.query_one(f"#{DForm.INTRO}", Label).update(intro_text)
        self.query_one(f"#{DForm.HEALTH_LABEL}", Label).update(
            gen_results_table(p2pool.pop_msgs())
        )

    def watch_radio_button_list(self, old, new):
        radio_set = self.query_one(f"#{DForm.RADIO_SET}", RadioSet)
        for child in list(radio_set.children):
            child.remove()
        for instance in self.radio_button_list:
            rb = RadioButton(instance, classes=DForm.RADIO_BUTTON_TYPE)
            if self.p2pool.parent() == self.instance_map[instance]:
                rb.value = True
            radio_set.mount(rb)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        radio_set = self.query_one(f"#{DForm.RADIO_SET}", RadioSet)
        monerod_instance = None
        monerod_id = None
        if radio_set.pressed_button:
            monerod_instance = str(radio_set.pressed_button.label)
            monerod_id = self.instance_map[monerod_instance]

        chain_radio_set = self.query_one(f"#{DForm.CHAIN_RADIO_SET}", RadioSet)
        chain = (
            chain_radio_set.pressed_button.label
            if chain_radio_set.pressed_button
            else None
        )

        # Update p2pool object
        self.p2pool.parent(monerod_id)
        self.p2pool.chain(str(chain))
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
            DButton.DELETE: (DModule.DEPLOYMENT_CLIENT, DMethod.DELETE_DEPLOYMENT),
            DButton.DISABLE: (DModule.DEPLOYMENT_CLIENT, DMethod.DISABLE_DEPLOYMENT),
            DButton.ENABLE: (DModule.DEPLOYMENT_CLIENT, DMethod.ENABLE_DEPLOYMENT),
            DButton.HASHRATE: (DModule.OPS_MGR, DMethod.HASHRATES),
            DButton.NEW: (DModule.OPS_MGR, DMethod.ADD_DEPLOYMENT),
            DButton.SHARES_FOUND: (DModule.OPS_MGR, DMethod.SHARES_FOUND),
            DButton.TABLES: (DModule.OPS_MGR, DMethod.GET_TABLE_DATA),
            DButton.UPDATE: (DModule.DEPLOYMENT_CLIENT, DMethod.UPDATE_DEPLOYMENT),
            DButton.VIEW_LOG: (DModule.OPS_MGR, DMethod.LOG_VIEWER),
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

        if button_id == DButton.VIEW_LOG:
            form_data[DField.INSTANCE] = self.p2pool.instance()

        self.app.post_message(Db4eMsg(self, form_data=form_data))
