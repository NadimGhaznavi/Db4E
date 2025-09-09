"""
db4e/Panes/Db4EPane.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from textual import on
from textual.widgets import Label, Input, Button, RadioButton, RadioSet
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.reactive import reactive


from db4e.Modules.Db4E import Db4E
from db4e.Messages.Db4eMsg import Db4eMsg
from db4e.Modules.Helper import gen_results_table
from db4e.Constants.Fields import (
    RADIO_SET_FIELD, ELEMENT_FIELD, OP_FIELD, RADIO_BUTTON_TYPE_FIELD,
    TO_METHOD_FIELD, TO_MODULE_FIELD)
from db4e.Constants.Fields import DField, DMod, DElem
from db4e.Constants.Buttons import (
    BUTTON_ROW_FIELD, UPDATE_BUTTON_FIELD)
from db4e.Constants.Labels import DLabel
from db4e.Constants.Jobs import DJob
from db4e.Constants.Form import Form

color = "#9cae41"
hi = "cyan"


class Db4EPane(Container):

    user_name_label = Label("", classes=Form.STATIC)
    group_name_label = Label("", classes=Form.STATIC)
    install_dir_label = Label("", classes=Form.STATIC)
    vendor_dir_input = Input(id="vendor_dir_input",
        restrict=r"/[a-zA-Z0-9/_.\- ]*", compact=True, classes=Form.INPUT_30)
    user_wallet_input = Input(id="user_wallet_input",
        restrict=r"[a-zA-Z0-9]*", compact=True, classes=Form.INPUT_70)
    health_msgs = Label()
    instance_map = {}
    radio_button_list = reactive([], always_update=True)
    radio_set = RadioSet(id="radio_set", classes=RADIO_SET_FIELD)

    def compose(self):
        INTRO = f"Welcome to the [bold {hi}]Database 4 Everything Core[/] " \
            f"[{hi}]configuration screen[/]. On this screen you can update your " \
            f"[{hi}]Monero Wallet[/], [{hi}]Primary Server[/] and relocate the " \
            f"[{hi}]Deployment Directory[/]. The [{hi}]Primary Server[/] is the " \
            f"[{hi}]Monero server[/] that is used by the internal " \
            f"[{hi}]P2Pool servers[/] for chain data collection."
        yield Vertical(
            ScrollableContainer(
                Label(INTRO, classes=Form.INTRO),

                Vertical(
                    Horizontal(
                        Label(DLabel.DB4E_USER, classes=Form.FORM_LABEL),
                        self.user_name_label),
                    Horizontal(
                        Label(DLabel.DB4E_GROUP, classes=Form.FORM_LABEL),
                        self.group_name_label),
                    Horizontal(
                        Label(DLabel.INSTALL_DIR, classes=Form.FORM_LABEL),
                        self.install_dir_label),
                    Horizontal(
                        Label(DLabel.VENDOR_DIR, classes=Form.FORM_LABEL),
                        self.vendor_dir_input),
                    Horizontal(
                        Label(DLabel.USER_WALLET, classes=Form.FORM_LABEL),
                        self.user_wallet_input),
                    classes=Form.FORM_5, id="form_field"),

                Vertical(
                    self.radio_set),

                Vertical(
                    self.health_msgs,
                    classes=Form.HEALTH_BOX,
                ),

                Horizontal(
                    Button(label=DLabel.UPDATE, id=UPDATE_BUTTON_FIELD),
                    classes=BUTTON_ROW_FIELD
                ),
            classes=Form.PANE_BOX))


    def on_mount(self):
        self.radio_set.border_subtitle = DLabel.PRIMARY_SERVER
        form_box = self.query_one("#form_field", Vertical)
        form_box.border_subtitle = DLabel.CONFIG




    def set_data(self, db4e: Db4E):
        self.db4e = db4e
        self.user_name_label.update(db4e.user.value)
        self.group_name_label.update(db4e.group.value)
        self.install_dir_label.update(db4e.install_dir.value)
        self.vendor_dir_input.value = db4e.vendor_dir.value
        self.user_wallet_input.value = db4e.user_wallet.value
        self.health_msgs.update(gen_results_table(db4e.pop_msgs()))

        # Create the Monerod radio buttons
        self.instance_map = db4e.instance_map()
        instance_list = []
        for instance in db4e.instance_map().keys():
            instance_list.append(instance)
        self.radio_button_list = instance_list


    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.db4e.user_wallet.value = self.query_one("#user_wallet_input", Input).value
        self.db4e.vendor_dir.value = self.query_one("#vendor_dir_input", Input).value

        form_data = {
            TO_MODULE_FIELD: DMod.DEPLOYMENT_MGR,
            TO_METHOD_FIELD: DJob.POST_JOB,
            OP_FIELD: DJob.UPDATE,
            DField.ELEMENT_TYPE: DElem.DB4E,
            ELEMENT_FIELD: self.db4e,
        }
        self.app.post_message(Db4eMsg(self, form_data=form_data))


    def watch_radio_button_list(self, old, new):
        for child in list(self.radio_set.children):
            child.remove()
        for instance in self.radio_button_list:
            radio_button = RadioButton(instance, classes=RADIO_BUTTON_TYPE_FIELD)
            if self.p2pool.parent() == self.instance_map[instance]:
                radio_button.value = True
            self.radio_set.mount(radio_button)