"""
db4e/Panes/Db4E.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from textual import on
from textual.widgets import Label, MarkdownViewer, Input, Button, Static
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer

from db4e.Modules.Helper import gen_results_table, get_component_value
from db4e.Messages.Db4eMsg import Db4eMsg
from db4e.Constants.Fields import (
    BUTTON_ROW_FIELD, DB4E_FIELD, ELEMENT_TYPE_FIELD,
    FORM_5_FIELD, FORM_DATA_FIELD, FORM_INPUT_30_FIELD, FORM_INPUT_70_FIELD,
    FORM_INTRO_FIELD, FORM_LABEL_FIELD, GREEN_BUTTON_FIELD, GROUP_FIELD,
    HEALTH_BOX_FIELD, HEALTH_MSGS_FIELD, INSTALL_DIR_FIELD, PANE_BOX_FIELD,
    STATIC_CONTENT_FIELD, TO_METHOD_FIELD, TO_MODULE_FIELD, UPDATE_BUTTON_FIELD,
    UPDATE_DEPLOYMENT_FIELD, USER_FIELD, USER_WALLET_FIELD, VENDOR_DIR_FIELD,
    OPS_MGR_FIELD
)
from db4e.Constants.Labels import (
    DB4E_GROUP_LABEL, DB4E_USER_LABEL, INSTALL_DIR_LABEL, UPDATE_LABEL,
    USER_WALLET_LABEL, VENDOR_DIR_LABEL
)

color = "#9cae41"
hi = "cyan"

class UIType:
    STATIC = STATIC_CONTENT_FIELD
    INPUT_30 = FORM_INPUT_30_FIELD
    INPUT_70 = FORM_INPUT_70_FIELD
    INTRO = FORM_INTRO_FIELD
    LABEL = FORM_LABEL_FIELD
    FORM_5 = FORM_5_FIELD


class Db4E(Container):

    user_name_label = Label("", classes=UIType.STATIC)
    group_name_label = Label("", classes=UIType.STATIC)
    install_dir_label = Label("", classes=UIType.STATIC)
    vendor_dir_input = Input(id="vendor_dir_input",
        restrict=r"/[a-zA-Z0-9/_.\- ]*", compact=True, classes=UIType.INPUT_30)
    user_wallet_input = Input(id="user_wallet_input",
        restrict=r"[a-zA-Z0-9]*", compact=True, classes=UIType.INPUT_70)
    health_msgs = Label()

    def compose(self):
        INTRO = f"Welcome to the [bold {hi}]Database 4 Everything Core[/] " \
            f"[{hi}]configuration screen[/]. On this screen you can update your " \
            f"[{hi}]Monero Wallet[/] and relocate the [{hi}]Deployment Directory[/]. "
        yield Vertical(
            ScrollableContainer(
                Label(INTRO, classes=UIType.INTRO),

                Vertical(
                    Horizontal(
                        Label(DB4E_USER_LABEL, classes=UIType.LABEL),
                        self.user_name_label),
                    Horizontal(
                        Label(DB4E_GROUP_LABEL, classes=UIType.LABEL),
                        self.group_name_label),
                    Horizontal(
                        Label(INSTALL_DIR_LABEL, classes=UIType.LABEL),
                        self.install_dir_label),
                    Horizontal(
                        Label(VENDOR_DIR_LABEL, classes=UIType.LABEL),
                        self.vendor_dir_input),
                    Horizontal(
                        Label(USER_WALLET_LABEL, classes=UIType.LABEL),
                        self.user_wallet_input),
                    classes=UIType.FORM_5),

                Vertical(
                    self.health_msgs,
                    classes=HEALTH_BOX_FIELD,
                ),

                Horizontal(
                    Button(label=UPDATE_LABEL, id=UPDATE_BUTTON_FIELD, 
                           classes=GREEN_BUTTON_FIELD),
                    classes=BUTTON_ROW_FIELD
                ),
            classes=PANE_BOX_FIELD))

    def set_data(self, rec):
        print(f"Db4E:set_data(): {rec}")
        self.user_name_label.update(get_component_value(rec, USER_FIELD))
        self.group_name_label.update(get_component_value(rec, GROUP_FIELD))
        self.install_dir_label.update(get_component_value(rec, INSTALL_DIR_FIELD))
        self.vendor_dir_input.value = get_component_value(rec, VENDOR_DIR_FIELD)
        self.user_wallet_input.value = get_component_value(rec, USER_WALLET_FIELD)
        self.health_msgs.update(gen_results_table(rec[HEALTH_MSGS_FIELD]))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        form_data = {
            TO_MODULE_FIELD: OPS_MGR_FIELD,
            TO_METHOD_FIELD: UPDATE_DEPLOYMENT_FIELD,
            ELEMENT_TYPE_FIELD: DB4E_FIELD,
            FORM_DATA_FIELD: True,
            USER_WALLET_FIELD: self.query_one("#user_wallet_input", Input).value,
            VENDOR_DIR_FIELD: self.query_one("#vendor_dir_input", Input).value,
        }
        self.app.post_message(Db4eMsg(self, form_data=form_data))

