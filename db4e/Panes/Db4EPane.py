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


from db4e.Messages.Db4eMsg import Db4eMsg


from db4e.Modules.Db4E import Db4E
from db4e.Modules.Helper import gen_results_table

from db4e.Constants.DField import DField
from db4e.Constants.DModule import DModule
from db4e.Constants.DElem import DElem
from db4e.Constants.DMethod import DMethod
from db4e.Constants.DForm import DForm
from db4e.Constants.DButton import DButton
from db4e.Constants.DLabel import DLabel

color = "#9cae41"
hi = "cyan"


class Db4EPane(Container):

    user_name_label = Label("", classes=DForm.STATIC)
    group_name_label = Label("", classes=DForm.STATIC)
    install_dir_label = Label("", classes=DForm.STATIC)
    vendor_dir_input = Input(id=DForm.VENDOR_DIR_INPUT,
        restrict=r"/[a-zA-Z0-9/_.\- ]*", compact=True, classes=DForm.INPUT_30)
    user_wallet_input = Input(id=DForm.USER_WALLET_INPUT,
        restrict=r"[a-zA-Z0-9]*", compact=True, classes=DForm.INPUT_70)
    health_msgs = Label()
    instance_map = {}
    radio_button_list = reactive([], always_update=True)
    radio_set = RadioSet(id=DForm.RADIO_SET, classes=DForm.RADIO_SET)

    def compose(self):
        INTRO = f"Welcome to the [bold {hi}]Database 4 Everything Core " \
            f"configuration screen[/]. On this screen you can update your " \
            f"[{hi}]Monero Wallet[/], [{hi}]Primary Server[/] and relocate the " \
            f"[{hi}]Deployment Directory[/]. The [{hi}]Primary Server[/] is the " \
            f"[{hi}]Monero server[/] that is used by the internal [i]Main[/], " \
            f"[i]Mini[/] and [i]Nano[/i] [{hi}]P2Pool servers[/] that collect " \
            f"chain metrics data." 
        yield Vertical(
            ScrollableContainer(
                Label(INTRO, classes=DForm.INTRO),

                Vertical(
                    Horizontal(
                        Label(DLabel.DB4E_USER, classes=DForm.FORM_LABEL),
                        self.user_name_label),
                    Horizontal(
                        Label(DLabel.DB4E_GROUP, classes=DForm.FORM_LABEL),
                        self.group_name_label),
                    Horizontal(
                        Label(DLabel.INSTALL_DIR, classes=DForm.FORM_LABEL),
                        self.install_dir_label),
                    Horizontal(
                        Label(DLabel.VENDOR_DIR, classes=DForm.FORM_LABEL),
                        self.vendor_dir_input),
                    Horizontal(
                        Label(DLabel.USER_WALLET, classes=DForm.FORM_LABEL),
                        self.user_wallet_input),
                    classes=DForm.FORM_5, id=DForm.FORM_BOX),

                self.radio_set,

                Vertical(
                    self.health_msgs,
                    classes=DForm.HEALTH_BOX, id=DForm.HEALTH_BOX),

                Horizontal(
                    Button(label=DLabel.UPDATE, id=DButton.UPDATE),
                    Button(label=DLabel.UPTIME, id=DButton.UPTIME),
                    classes=DForm.BUTTON_ROW
                ),
            classes=DForm.PANE_BOX))


    def on_mount(self):
        self.radio_set.border_subtitle = DLabel.PRIMARY_SERVER
        form_box = self.query_one("#" + DForm.FORM_BOX, Vertical)
        form_box.border_subtitle = DLabel.CONFIG
        health_box = self.query_one("#" + DForm.HEALTH_BOX, Vertical)
        health_box.border_subtitle = DLabel.STATUS


    def set_data(self, db4e: Db4E):
        self.db4e = db4e
        self.user_name_label.update(db4e.user())
        self.group_name_label.update(db4e.group())
        self.install_dir_label.update(db4e.install_dir())
        self.vendor_dir_input.value = db4e.vendor_dir()
        self.user_wallet_input.value = db4e.user_wallet()
        self.health_msgs.update(gen_results_table(db4e.pop_msgs()))

        # Create the Monerod radio buttons
        self.instance_map = db4e.instance_map()
        self.instance_map[DLabel.DISABLE] = DField.DISABLE
        instance_list = []
        for instance in db4e.instance_map().keys():
            instance_list.append(instance)
        self.radio_button_list = instance_list


    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        self.db4e.user_wallet(self.query_one("#" + DForm.USER_WALLET_INPUT, Input).value)
        self.db4e.vendor_dir(self.query_one("#" + DForm.VENDOR_DIR_INPUT, Input).value)
        radio_set = self.query_one("#" + DForm.RADIO_SET, RadioSet)
        primary_instance = radio_set.pressed_button.label
        self.db4e.primary_server(self.instance_map[primary_instance])
        
        if button_id == DButton.UPDATE:
            form_data = {
                DField.TO_MODULE: DModule.DEPLOYMENT_CLIENT,
                DField.TO_METHOD: DMethod.UPDATE_DEPLOYMENT,
                DField.ELEMENT_TYPE: DElem.DB4E,
                DField.ELEMENT: self.db4e,
            }

        elif button_id == DButton.UPTIME:
            form_data = {
                DField.TO_MODULE: DModule.OPS_MGR,
                DField.TO_METHOD: DMethod.GET_UPTIME,
                DField.ELEMENT_TYPE: DElem.DB4E,
                DField.ELEMENT: self.db4e,
            }

        self.app.post_message(Db4eMsg(self, form_data=form_data))


    def watch_radio_button_list(self, old, new):
        for child in list(self.radio_set.children):
            child.remove()
        for instance in self.radio_button_list:
            radio_button = RadioButton(instance, classes=DForm.RADIO_BUTTON_TYPE)
            if self.db4e.primary_server() == self.instance_map[instance]:
                radio_button.value = True
            self.radio_set.mount(radio_button)